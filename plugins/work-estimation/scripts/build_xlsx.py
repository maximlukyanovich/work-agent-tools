# -*- coding: utf-8 -*-
"""Fill the estimate workbook template from a data module, preserving the template's styling.

    build_xlsx.py <data module> <template .xlsx> <output .xlsx>

The empty workbook is the input and is never written to; the filled one is the output.
Running this twice must give the same result, so the template must not be the file produced.
"""

import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape, unescape

from estimate_data import NUMERIC, Estimate

# The one layout this script fills: the corporate estimate template. Row numbers are the
# template's own, before any row is inserted. The labels are checked before anything is
# written, so another template stops the run instead of being filled in the wrong cells.
# The questions sheet is the second one: numbers in A and questions in B from row 2.
LAYOUT = {
    "labels": {
        "I9": "Overall Expected Timeline:",
        "B30": "Development",
        "B47": "Risks which may cause estimation changes:",
        "B50": "Excludes:",
        "B55": "TECH STACK",
    },
    # The template's data rows; the last one is cloned for every row of the estimate.
    "data_rows": (32, 35),
    "columns": {"B": "part", "C": "epic", "D": "task", "E": "description",
                "F": "optimistic", "G": "pessimistic", "H": "negative", "I": "positive"},
    # A blank text row, cloned and merged across for every item past a list's blank rows.
    "text_row": 48,
    "text_merge": ("B", "G"),
    "lists": {"RISKS": (48, 49), "EXCLUDES": (51, 52)},
    # The cell each WORKBOOK key fills.
    "fields": {"timeline": "K9", "timeline_note": "I10", "stack": "B56"},
}


# --------------------------------------------------------------- ref helpers
def col_letters(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


CELL_RE = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)")


def shift_ref(ref, thr, delta):
    def rep(m):
        row = int(m.group(4))
        if row >= thr:
            row += delta
        return f"{m.group(1)}{m.group(2)}{m.group(3)}{row}"

    return CELL_RE.sub(rep, ref)


SHEETREF_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?")


def shift_formula(f, thr, delta):
    """Shift row references, leaving cross-sheet references (Rates!$B$3) untouched."""
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return f"\x00{len(keep) - 1}\x00"

    f = SHEETREF_RE.sub(stash, f)
    f = shift_ref(f, thr, delta)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], f)


def shift_row_xml(xml, new_n, thr, delta):
    """Renumber a <row> and shift the row references inside its formulas."""
    xml = re.sub(r'(<row\b[^>]*\br=")\d+(")', lambda m: m.group(1) + str(new_n) + m.group(2), xml, count=1)
    xml = re.sub(r'(<c r="([A-Z]{1,3}))\d+(")', lambda m: m.group(1) + str(new_n) + m.group(3), xml)
    # A shared formula's other cells hold a self-closing <f .../>: it has no text to shift,
    # and matching it would run on to the next </f> and shift the cells in between.
    xml = re.sub(r"<f([^>]*)(?<!/)>(.*?)</f>",
                 lambda m: f"<f{m.group(1)}>{shift_formula(m.group(2), thr, delta)}</f>", xml, flags=re.S)
    return xml


# -------------------------------------------------------------- cell writing
def set_cell(rowxml, col, value, numeric=False):
    n = re.search(r'<row\b[^>]*\br="(\d+)"', rowxml).group(1)
    ref = col + n
    pat = re.compile(r'<c r="' + ref + r'"([^>]*?)(?:/>|>.*?</c>)', re.S)
    m = pat.search(rowxml)
    if not m:
        raise KeyError(f"cell {ref} not found")
    attrs = m.group(1)
    style = re.search(r'\bs="(\d+)"', attrs)
    s = f' s="{style.group(1)}"' if style else ""
    if numeric:
        body = f'<c r="{ref}"{s}><v>{value}</v></c>'
    elif value == "":
        body = f'<c r="{ref}"{s}/>'
    else:
        txt = escape(str(value))
        body = f'<c r="{ref}"{s} t="inlineStr"><is><t xml:space="preserve">{txt}</t></is></c>'
    return rowxml[: m.start()] + body + rowxml[m.end():]


# ------------------------------------------------------------------- labels
def shared_strings(zin):
    """The workbook's shared strings as plain text: a label cell holds an index into them."""
    if "xl/sharedStrings.xml" not in zin.namelist():
        return []
    xml = zin.read("xl/sharedStrings.xml").decode("utf-8")
    return [unescape("".join(re.findall(r"<t(?:\s[^>]*)?>(.*?)</t>", si, re.S)))
            for si in re.findall(r"<si>(.*?)</si>", xml, re.S)]


def cell_text(xml, ref, strings):
    """The text a cell shows — a shared string, an inline string or a value; "" when empty."""
    m = re.search(r'<c r="%s"([^>]*?)(?:/>|>(.*?)</c>)' % ref, xml, re.S)
    if not m:
        return ""
    attrs, inner = m.group(1), m.group(2) or ""
    if re.search(r'\bt="s"', attrs):
        return strings[int(re.search(r"<v>(\d+)</v>", inner).group(1))]
    texts = re.findall(r"<t(?:\s[^>]*)?>(.*?)</t>", inner, re.S)
    if texts:
        return unescape("".join(texts))
    value = re.search(r"<v>(.*?)</v>", inner)
    return unescape(value.group(1)) if value else ""


def check_labels(xml, strings, labels):
    """(cell, expected, found) for every anchor label the template does not carry."""
    found = {ref: cell_text(xml, ref, strings).strip() for ref in labels}
    return [(ref, want, found[ref]) for ref, want in labels.items() if found[ref] != want]


def workbook_cells(E):
    """{cell: text} for the single cells WORKBOOK fills, and the keys left empty.

    The timeline defaults to the report's weeks; the note and the stack have no default —
    they are the project's, in the workbook's language, and an empty cell is named instead
    of being filled with another project's text."""
    given = dict(E.get("WORKBOOK", {}))
    unknown = sorted(set(given) - set(LAYOUT["fields"]))
    if unknown:
        raise ValueError(f"WORKBOOK has unknown keys {', '.join(unknown)}; "
                         f"known: {', '.join(LAYOUT['fields'])}")
    if "timeline" not in given:
        wo, wp = E.weeks()
        given["timeline"] = f"{wo}–{wp} weeks" if wo != wp else f"{wo} weeks"
    cells = {ref: given.get(key, "") for key, ref in LAYOUT["fields"].items()}
    empty = [key for key, ref in LAYOUT["fields"].items() if not cells[ref]]
    return cells, empty


# ------------------------------------------------------------------ sheet body
class Sheet:
    """The first sheet while it is rebuilt: its rows as (number, xml), the XML after
    <sheetData>, where each template row went, and the merges added for inserted rows."""

    def __init__(self, rows, tail, mapping, text_row):
        self.rows, self.tail, self.mapping, self.text_row = rows, tail, mapping, text_row
        self.extra_merges = []


def shift_tail(tail, thr, delta):
    """Shift the merged ranges, selections and conditional-format formulas after <sheetData>."""
    tail = re.sub(r'(<mergeCell ref=")([^"]+)(")',
                  lambda m: m.group(1) + shift_ref(m.group(2), thr, delta) + m.group(3), tail)
    tail = re.sub(r'(sqref=")([^"]+)(")',
                  lambda m: m.group(1) + " ".join(shift_ref(p, thr, delta) for p in m.group(2).split()) + m.group(3), tail)
    return re.sub(r"<formula>(.*?)</formula>",
                  lambda m: f"<formula>{shift_formula(m.group(1), thr, delta)}</formula>", tail)


def insert_rows(sheet, at, count):
    """Insert `count` clones of the text row at position `at`; shift everything below."""
    new, new_merges, old_merges = [], [], list(sheet.extra_merges)
    for n, x in sheet.rows:
        if n >= at:
            new.append((n + count, shift_row_xml(x, n + count, at, count)))
        else:
            new.append((n, shift_row_xml(x, n, at, count)))
    text, (left, right) = LAYOUT["text_row"], LAYOUT["text_merge"]
    for i in range(count):
        rn = at + i
        new.append((rn, shift_row_xml(sheet.text_row, rn, text, rn - text)))
        new_merges.append(f"{left}{rn}:{right}{rn}")
    sheet.rows = sorted(new, key=lambda t: t[0])
    sheet.mapping = {k: (v + count if v >= at else v) for k, v in sheet.mapping.items()}
    sheet.extra_merges = [shift_ref(r, at, count) for r in old_merges] + new_merges
    sheet.tail = shift_tail(sheet.tail, at, count)


# ------------------------------------------------------------- other sheets
def fill_qa(xml, questions):
    for i, q in enumerate(questions):
        n = i + 2
        m = re.search(r'<row\b[^>]*\br="%d"[^>]*(?:/>|>.*?</row>)' % n, xml, re.S)
        row = m.group(0)
        if f'<c r="A{n}"' not in row:
            st = re.search(r'<c r="B%d"([^>]*?)/?>' % n, row).group(1)
            st = (re.search(r'\bs="\d+"', st) or [""])
            st = " " + st.group(0) if hasattr(st, "group") else ""
            row = re.sub(r'(<row\b[^>]*?[^/]>)', r'\1<c r="A%d"%s/>' % (n, st), row, count=1)
        row = set_cell(row, "A", i + 1, numeric=True)
        row = set_cell(row, "B", q)
        xml = xml[: m.start()] + row + xml[m.end():]
    return xml


# ---- post-fixes: shared-formula refs on moved rows, recalc on load -----
def fix_shared_refs(xml):
    def one(m):
        col, row, attrs, fattrs = m.group(1), m.group(2), m.group(3), m.group(4)
        fattrs = re.sub(
            r'ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"',
            lambda r: f'ref="{r.group(1)}{row}:{r.group(3)}{row}"'
            if r.group(2) == r.group(4) and r.group(2) != row else r.group(0),
            fattrs)
        return f'<c r="{col}{row}"{attrs}><f{fattrs}>'
    return re.sub(r'<c r="([A-Z]{1,3})(\d+)"([^>]*)><f([^>]*)>', one, xml)


# ------------------------------------------------------------------ workbook
def main(argv):
    module = argv[0] if argv else "data"
    src, dst = argv[1], argv[2]
    E = Estimate(module)
    data = E.m

    zin = zipfile.ZipFile(src)
    sheet1 = zin.read("xl/worksheets/sheet1.xml").decode("utf-8")
    sheet2 = zin.read("xl/worksheets/sheet2.xml").decode("utf-8")

    mismatches = check_labels(sheet1, shared_strings(zin), LAYOUT["labels"])
    for ref, want, found in mismatches:
        print(f"{ref}: expected {want!r}, found {found!r}", file=sys.stderr)
    if mismatches:
        print("not the supported workbook layout, nothing written - see reference/data-format.md",
              file=sys.stderr)
        return 1
    try:
        cells, empty = workbook_cells(E)
    except ValueError as e:
        print(f"{e}, nothing written", file=sys.stderr)
        return 1

    head, rest = sheet1.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)

    rows = {}
    order = []
    for m in re.finditer(r'<row\b[^>]*\br="(\d+)"[^>]*(?:/>|>.*?</row>)', body, re.S):
        n = int(m.group(1))
        rows[n] = m.group(0)
        order.append(n)

    first, last = LAYOUT["data_rows"]
    tpl_data_row = rows[last]

    # ---- numbers -------------------------------------------------------
    # Rows carry their own PART OF; the workbook's summary formulas pick them up by name.
    entries = E.all_rows()
    delta = len(entries) - (last - first + 1)
    core_o, core_p = E.core()
    total_o, total_p = E.total()
    print(f"rows={len(entries)} parts={E.parts} core={core_o}/{core_p} total={total_o}/{total_p}")

    # ---- rebuild sheetData ---------------------------------------------
    out, mapping = [], {}
    for n in order:
        if n < first:
            out.append((n, shift_row_xml(rows[n], n, last, delta)))
            mapping[n] = n
        elif n <= last:
            if n == first:  # emit all data rows here
                for i, r in enumerate(entries):
                    rn = first + i
                    x = shift_row_xml(tpl_data_row, rn, last, rn - last)
                    for col, key in LAYOUT["columns"].items():
                        x = set_cell(x, col, r[key], numeric=key in NUMERIC)
                    out.append((rn, x))
        else:
            nn = n + delta
            out.append((nn, shift_row_xml(rows[n], nn, last, delta)))
            mapping[n] = nn
    sheet = Sheet(out, shift_tail(tail, last, delta), mapping, rows[LAYOUT["text_row"]])

    # each list has its blank rows under the header; more items insert more rows
    for name, (top, bottom) in LAYOUT["lists"].items():
        extra = len(getattr(data, name)) - (bottom - top + 1)
        if extra > 0:
            insert_rows(sheet, sheet.mapping[bottom], extra)

    rowmap = dict(sheet.rows)

    def write(ref, value):
        col, orig_row = re.fullmatch(r"([A-Z]+)(\d+)", ref).groups()
        n = sheet.mapping[int(orig_row)]
        rowmap[n] = set_cell(rowmap[n], col, value)

    for name, (top, _) in LAYOUT["lists"].items():
        for i, txt in enumerate(getattr(data, name)):
            n = sheet.mapping[top] + i
            rowmap[n] = set_cell(rowmap[n], LAYOUT["text_merge"][0], txt)

    # timeline, its note, tech stack
    for ref, value in cells.items():
        write(ref, value)
    for key in empty:
        print(f'empty: WORKBOOK["{key}"] -> {LAYOUT["fields"][key]}')

    new_body = "".join(x for _, x in sorted(rowmap.items()))
    tail = sheet.tail
    if sheet.extra_merges:
        cnt = int(re.search(r'<mergeCells count="(\d+)"', tail).group(1)) + len(sheet.extra_merges)
        tail = re.sub(r'<mergeCells count="\d+">', f'<mergeCells count="{cnt}">', tail)
        tail = tail.replace("</mergeCells>",
                            "".join(f'<mergeCell ref="{r}"/>' for r in sheet.extra_merges) + "</mergeCells>")
    sheet1_new = fix_shared_refs(head + "<sheetData>" + new_body + "</sheetData>" + tail)
    sheet2_new = fill_qa(sheet2, data.QUESTIONS)
    workbook = zin.read("xl/workbook.xml").decode("utf-8")
    workbook = re.sub(r"<calcPr[^>]*/>", '<calcPr calcId="191029" fullCalcOnLoad="1"/>', workbook)

    # ---- write ---------------------------------------------------------
    with zipfile.ZipFile(dst + ".tmp", "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            d = zin.read(item.filename)
            if item.filename == "xl/worksheets/sheet1.xml":
                d = sheet1_new.encode("utf-8")
            elif item.filename == "xl/worksheets/sheet2.xml":
                d = sheet2_new.encode("utf-8")
            elif item.filename == "xl/workbook.xml":
                d = workbook.encode("utf-8")
            zout.writestr(item, d)
    shutil.move(dst + ".tmp", dst)
    print("written:", dst)
    print("source :", src)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
