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
from xml.sax.saxutils import escape

from estimate_data import Estimate


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
    xml = re.sub(r"<f([^>]*)>(.*?)</f>",
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
    for i in range(count):
        rn = at + i
        new.append((rn, shift_row_xml(sheet.text_row, rn, 48, rn - 48)))
        new_merges.append(f"B{rn}:G{rn}")
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

    head, rest = sheet1.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)

    rows = {}
    order = []
    for m in re.finditer(r'<row\b[^>]*\br="(\d+)"[^>]*(?:/>|>.*?</row>)', body, re.S):
        n = int(m.group(1))
        rows[n] = m.group(0)
        order.append(n)

    tpl_data_row = rows[35]

    # ---- numbers -------------------------------------------------------
    # Rows carry their own PART OF; the workbook's summary formulas pick them up by name.
    entries = [(r["part"], r["epic"], r["task"], r["description"], r["optimistic"],
                r["pessimistic"], r["negative"], r["positive"]) for r in E.all_rows()]
    delta = len(entries) - 4  # template holds 4 data rows (32..35)
    core_o, core_p = E.core()
    total_o, total_p = E.total()
    print(f"rows={len(entries)} parts={E.parts} core={core_o}/{core_p} total={total_o}/{total_p}")

    # ---- rebuild sheetData ---------------------------------------------
    out, mapping = [], {}
    for n in order:
        if n < 32:
            out.append((n, shift_row_xml(rows[n], n, 35, delta)))
            mapping[n] = n
        elif n <= 35:
            if n == 32:  # emit all data rows here
                for i, r in enumerate(entries):
                    rn = 32 + i
                    x = shift_row_xml(tpl_data_row, rn, 35, rn - 35)
                    x = set_cell(x, "B", r[0])
                    x = set_cell(x, "C", r[1])
                    x = set_cell(x, "D", r[2])
                    x = set_cell(x, "E", r[3])
                    x = set_cell(x, "F", r[4], numeric=True)
                    x = set_cell(x, "G", r[5], numeric=True)
                    x = set_cell(x, "H", r[6])
                    x = set_cell(x, "I", r[7])
                    out.append((rn, x))
        else:
            nn = n + delta
            out.append((nn, shift_row_xml(rows[n], nn, 35, delta)))
            mapping[n] = nn
    sheet = Sheet(out, shift_tail(tail, 35, delta), mapping, rows[48])

    # risks: template gives 2 blank rows (orig 48, 49) after the header at orig 47
    need_risks = len(data.RISKS)
    if need_risks > 2:
        insert_rows(sheet, sheet.mapping[49], need_risks - 2)
    need_ex = len(data.EXCLUDES)
    if need_ex > 2:
        insert_rows(sheet, sheet.mapping[52], need_ex - 2)

    rowmap = dict(sheet.rows)

    def write(orig_row, col, value, numeric=False):
        n = sheet.mapping[orig_row]
        rowmap[n] = set_cell(rowmap[n], col, value, numeric)

    for i, txt in enumerate(data.RISKS):
        n = sheet.mapping[48] + i
        rowmap[n] = set_cell(rowmap[n], "B", txt)
    for i, txt in enumerate(data.EXCLUDES):
        n = sheet.mapping[51] + i
        rowmap[n] = set_cell(rowmap[n], "B", txt)

    # timeline + tech stack
    write(10, "I", "The timeline covers the frontend scope only and assumes 1 frontend developer, "
                  "with the backend contract available on time.")
    write(9, "K", "13-19 weeks (frontend only)")
    write(56, "B", "FRONT-END: React 19.2, Next.js 16.3 (App Router, Cache Components), TypeScript 5.9, "
                   "Tailwind CSS 4, shadcn/ui + Radix UI, TanStack Query 5, Zod 4, next-intl 4, "
                   "Storybook, Vitest + Testing Library, Playwright, MSW, ESLint 9 + Prettier, "
                   "Node 24, pnpm 11")

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


if __name__ == "__main__":
    main(sys.argv[1:])
