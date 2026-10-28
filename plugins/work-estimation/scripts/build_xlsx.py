# -*- coding: utf-8 -*-
"""Fill a workbook template from a data module by the template's map, preserving its styling.

    build_xlsx.py <data module> <template .xlsx> <map .json> <output .xlsx>

The map, kept beside the template, says where the estimate goes: every place in it is a
label the template carries and an offset from that label ("The workbook map" in
reference/data-format.md). All places are found before anything is written, so a map
that does not fit the template stops the run instead of filling the wrong cells.

The empty workbook is the input and is never written to; the filled one is the output.
Running this twice must give the same result, so the template must not be the file produced.
"""

import json
import posixpath
import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape, unescape

from estimate_data import DEFAULT_COLUMNS, NUMERIC, Estimate

ROW_KEYS = [key for key, _ in DEFAULT_COLUMNS]
LISTS = ("RISKS", "EXCLUDES", "QUESTIONS")
MAP_HELP = 'see reference/data-format.md, "The workbook map"'


# --------------------------------------------------------------- ref helpers
def col_letters(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


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


# A reference as a formula reads it: not part of a name, not a function such as LOG10(.
REF_RE = re.compile(r"(?<![A-Za-z0-9_.$])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\w(])")


def translate(formula, drow, dcol):
    """A shared formula as a cell `drow` rows and `dcol` columns from its first cell reads
    it: relative references move, $-anchored ones and quoted text do not."""
    def move(m):
        col = m.group(2) if m.group(1) else col_letters(col_index(m.group(2)) + dcol)
        row = m.group(4) if m.group(3) else str(int(m.group(4)) + drow)
        return f"{m.group(1)}{col}{m.group(3)}{row}"

    parts, quoted = re.split(r'(&quot;|")', formula), False
    for i, part in enumerate(parts):
        if part in ('"', "&quot;"):
            quoted = not quoted
        elif not quoted:
            parts[i] = REF_RE.sub(move, part)
    return "".join(parts)


# -------------------------------------------------------------- cell writing
# A row, self-closing when it holds no cells.
ROW_RE = re.compile(r'<row\b[^>]*\br="(\d+)"[^>]*?(?:/>|(?<!/)>.*?</row>)', re.S)


def add_cell(rowxml, col, style=None):
    """The row with an empty cell added in column order: a template stores no cell it
    has nothing in."""
    n = re.search(r'<row\b[^>]*\br="(\d+)"', rowxml).group(1)
    st = f' s="{style}"' if style else ""
    new = f'<c r="{col}{n}"{st}/>'
    if re.fullmatch(r"<row\b[^>]*/>", rowxml):
        return rowxml[:-2] + ">" + new + "</row>"
    for m in re.finditer(r'<c r="([A-Z]{1,3})\d+"', rowxml):
        if col_index(m.group(1)) > col_index(col):
            return rowxml[: m.start()] + new + rowxml[m.start():]
    end = rowxml.rindex("</row>")
    return rowxml[:end] + new + rowxml[end:]


def cell_style(rowxml, col):
    m = re.search(r'<c r="%s\d+"([^>]*?)/?>' % col, rowxml)
    style = m and re.search(r'\bs="(\d+)"', m.group(1))
    return style.group(1) if style else None


def set_cell(rowxml, col, value, numeric=False):
    n = re.search(r'<row\b[^>]*\br="(\d+)"', rowxml).group(1)
    ref = col + n
    pat = re.compile(r'<c r="' + ref + r'"([^>]*?)(?:/>|>.*?</c>)', re.S)
    m = pat.search(rowxml)
    if not m:
        rowxml = add_cell(rowxml, col)
        m = pat.search(rowxml)
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


def put_item(rowxml, col, text, number=None, k=0):
    """A list item: its text, and its number when the list has a number column. A number
    cell the template does not store takes the style of the text cell beside it."""
    if number:
        if not re.search(r'<c r="%s\d+"' % number, rowxml):
            rowxml = add_cell(rowxml, number, cell_style(rowxml, col))
        rowxml = set_cell(rowxml, number, k, numeric=True)
    return set_cell(rowxml, col, text)


def edit_rows(body, edits):
    """<sheetData> with {row number: edit(row xml)} applied, on a sheet whose rows stay
    where they are; a row the template does not store is created."""
    edits, out, pos = dict(edits), [], 0
    for m in ROW_RE.finditer(body):
        n = int(m.group(1))
        out.append(body[pos: m.start()])
        out += [edits.pop(k)(f'<row r="{k}"></row>') for k in sorted(k for k in edits if k < n)]
        out.append(edits.pop(n)(m.group(0)) if n in edits else m.group(0))
        pos = m.end()
    out += [edits[k](f'<row r="{k}"></row>') for k in sorted(edits)]
    return "".join(out) + body[pos:]


# ------------------------------------------------------- the template's text
def shared_strings(zin):
    """The workbook's shared strings as plain text: a label cell holds an index into them."""
    if "xl/sharedStrings.xml" not in zin.namelist():
        return []
    xml = zin.read("xl/sharedStrings.xml").decode("utf-8")
    return [unescape("".join(re.findall(r"<t(?:\s[^>]*)?>(.*?)</t>", si, re.S)))
            for si in re.findall(r"<si>(.*?)</si>", xml, re.S)]


CELL_XML = re.compile(r'<c r="([A-Z]{1,3})(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', re.S)


def cells(xml, strings):
    """(column, row, text, formula) for every cell a sheet stores. The text is what the
    cell shows — a shared string, an inline string or a value, "" when empty; the
    formula is "" for a constant and "=" for a shared formula's other cells."""
    for m in CELL_XML.finditer(xml):
        attrs, inner = m.group(3), m.group(4) or ""
        f = re.search(r"<f\b[^>]*?(?:/>|>(.*?)</f>)", inner, re.S)
        formula = ("=" + unescape(f.group(1) or "")) if f else ""
        if re.search(r'\bt="s"', attrs):
            text = strings[int(re.search(r"<v>(\d+)</v>", inner).group(1))]
        else:
            texts = re.findall(r"<t(?:\s[^>]*)?>(.*?)</t>", inner, re.S)
            value = re.search(r"<v>(.*?)</v>", inner)
            text = unescape("".join(texts)) if texts else unescape(value.group(1)) if value else ""
        yield m.group(1), int(m.group(2)), text, formula


def sheet_parts(zin):
    """{sheet name: its part in the zip}, in the workbook's order."""
    targets = {}
    for rel in re.findall(r"<Relationship\b[^>]*>", zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")):
        rid, target = (re.search(r'\b%s="([^"]*)"' % a, rel).group(1) for a in ("Id", "Target"))
        targets[rid] = target[1:] if target.startswith("/") else posixpath.normpath("xl/" + target)
    parts = {}
    for sheet in re.findall(r"<sheet\b[^>]*>", zin.read("xl/workbook.xml").decode("utf-8")):
        name = unescape(re.search(r'\bname="([^"]*)"', sheet).group(1), {"&quot;": '"', "&apos;": "'"})
        parts[name] = targets[re.search(r'\s[\w.-]+:id="([^"]*)"', sheet).group(1)]
    return parts


# -------------------------------------------------------------------- the map
PLACE = ("label", "down", "right")


def place_problems(where, place, extra):
    if not isinstance(place, dict):
        return [f"{where}: a place is an object with a label"]
    out = [f"{where}: unknown key {key!r}" for key in place if key not in PLACE + extra]
    if not isinstance(place.get("label"), str) or not place["label"].strip():
        out.append(f"{where}: label must be the text of a cell")
    for key in ("down", "right"):
        v = place.get(key, 0)
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            out.append(f"{where}: {key} must be a whole number, 0 or more")
    return out


def is_column(v):
    return isinstance(v, str) and re.fullmatch(r"[A-Z]{1,3}", v) is not None


def load_map(path):
    """The map as a dict; ValueError naming every key it does not know."""
    with open(path, encoding="utf-8") as f:
        try:
            wmap = json.load(f)
        except ValueError as e:
            raise ValueError(f"{path}: not JSON - {e}")
    if not isinstance(wmap, dict):
        raise ValueError(f"{path}: the map is an object")
    out = [f"unknown key {key!r}" for key in wmap if key not in ("sheet", "tasks", "lists", "fields")]
    if "sheet" in wmap and not isinstance(wmap["sheet"], str):
        out.append("sheet must be a sheet's name")
    tasks = wmap.get("tasks")
    if tasks is None:
        out.append("tasks: the map has no place for the task rows")
    else:
        out += place_problems("tasks", tasks, ("rows", "columns"))
        rows = tasks.get("rows") if isinstance(tasks, dict) else None
        if not isinstance(rows, int) or isinstance(rows, bool) or rows < 1:
            out.append("tasks: rows must be the number of task rows in the template, 1 or more")
        columns = tasks.get("columns") if isinstance(tasks, dict) else None
        if not isinstance(columns, dict) or not columns:
            out.append("tasks: columns must name at least one column")
        else:
            out += [f"tasks.columns: {col!r} is not a column" for col in columns if not is_column(col)]
            out += [f"tasks.columns.{col}: unknown key {key!r}; known: {', '.join(ROW_KEYS)}"
                    for col, key in columns.items() if key not in ROW_KEYS]
    lists, fields = wmap.get("lists", {}), wmap.get("fields", {})
    out += [f"{key} must be an object" for key, v in (("lists", lists), ("fields", fields))
            if not isinstance(v, dict)]
    for name, place in (lists.items() if isinstance(lists, dict) else []):
        if name not in LISTS:
            out.append(f"lists: unknown list {name!r}; known: {', '.join(LISTS)}")
            continue
        out += place_problems(f"lists.{name}", place, ("sheet", "rows", "number"))
        if not isinstance(place, dict):
            continue
        rows = place.get("rows", 1)
        if not isinstance(rows, int) or isinstance(rows, bool) or rows < 1:
            out.append(f"lists.{name}: rows must be the number of blank rows, 1 or more")
        if "number" in place and not is_column(place["number"]):
            out.append(f"lists.{name}: number must be a column")
        if not isinstance(place.get("sheet", ""), str):
            out.append(f"lists.{name}: sheet must be a sheet's name")
    for key, place in (fields.items() if isinstance(fields, dict) else []):
        out += place_problems(f"fields.{key}", place, ("sheet",))
    if out:
        raise ValueError("\n".join(f"{path}: {line}" for line in out))
    return wmap


def resolve(zin, wmap):
    """Every place of the map, found in the template, and the problems met on the way.

    A place is (sheet, column, row) in the template's own rows, before any row is moved.
    Returns ({"sheet": the task sheet, "parts": {sheet: part}, "tasks": place,
    "lists": {name: place}, "fields": {key: place}}, problems); every problem is
    collected, so one run names all of them."""
    parts, strings = sheet_parts(zin), shared_strings(zin)
    task_sheet = wmap.get("sheet", next(iter(parts)))
    labels, problems = {}, []

    def find(where, place, sheet):
        if sheet not in parts:
            problems.append(f'{where}: sheet "{sheet}" is not in the workbook; it has {", ".join(parts)}')
            return None
        if sheet not in labels:
            labels[sheet] = {}
            for col, n, text, formula in cells(zin.read(parts[sheet]).decode("utf-8"), strings):
                if text.strip() and not formula:
                    labels[sheet].setdefault(text.strip(), []).append(f"{col}{n}")
        label = place["label"].strip()
        refs = labels[sheet].get(label, [])
        if len(refs) != 1:
            found = "not found" if not refs else f"found {len(refs)} times: {' '.join(refs)}"
            problems.append(f'{where}: label "{label}" {found} on sheet "{sheet}"')
            return None
        col, row = re.fullmatch(r"([A-Z]+)(\d+)", refs[0]).groups()
        return sheet, col_letters(col_index(col) + place.get("right", 0)), int(row) + place.get("down", 0)

    found = {"sheet": task_sheet, "parts": parts, "lists": {}, "fields": {}}
    found["tasks"] = find("tasks", wmap["tasks"], task_sheet)
    for name, place in wmap.get("lists", {}).items():
        sheet = place.get("sheet", task_sheet)
        if "rows" in place and sheet != task_sheet:
            problems.append(f'lists.{name}: rows are inserted only on the task sheet "{task_sheet}"')
        found["lists"][name] = find(f"lists.{name}", place, sheet)
    for key, place in wmap.get("fields", {}).items():
        found["fields"][key] = find(f"fields.{key}", place, place.get("sheet", task_sheet))

    # A place inside the task rows would be rebuilt away with them.
    if found["tasks"]:
        first = found["tasks"][2]
        last = first + wmap["tasks"]["rows"] - 1
        spans = [(f"lists.{name}", spot, wmap["lists"][name].get("rows", 1))
                 for name, spot in found["lists"].items()]
        spans += [(f"fields.{key}", spot, 1) for key, spot in found["fields"].items()]
        for where, spot, rows in spans:
            if spot and spot[0] == task_sheet and spot[2] <= last and spot[2] + rows - 1 >= first:
                problems.append(f"{where}: {spot[1]}{spot[2]} is inside the task rows {first}-{last}")
    return found, problems


def item_problems(zin, wmap, found, E):
    """A list without rows of its own writes into the cells under its place: one that
    holds text, or a task row, would be lost."""
    strings, problems, filled = shared_strings(zin), [], {}
    first = found["tasks"][2]
    last = first + wmap["tasks"]["rows"] - 1
    for name, (sheet, col, row) in found["lists"].items():
        place = wmap["lists"][name]
        if "rows" in place:
            continue
        if sheet not in filled:
            xml = zin.read(found["parts"][sheet]).decode("utf-8")
            filled[sheet] = {(c, n): text or formula for c, n, text, formula in cells(xml, strings)
                             if text or formula}
        for n in range(row, row + len(E.get(name, []))):
            if sheet == found["sheet"] and first <= n <= last:
                problems.append(f"lists.{name}: {col}{n} is inside the task rows {first}-{last}")
                break
            for c in filter(None, (col, place.get("number"))):
                if (c, n) in filled[sheet]:
                    problems.append(f'lists.{name}: {sheet}!{c}{n} holds "{filled[sheet][(c, n)][:40]}" '
                                    f"- the list would overwrite it")
    return problems


def workbook_cells(E, fields):
    """{key: text} for the single cells WORKBOOK fills, and the keys left empty.

    The keys are the map's fields. The timeline defaults to the report's weeks; any other
    key has no default — it is the project's, in the workbook's language, and an empty
    cell is named instead of being filled with another project's text."""
    given = dict(E.get("WORKBOOK", {}))
    unknown = sorted(set(given) - set(fields))
    if unknown:
        raise ValueError(f"WORKBOOK has keys the map does not place: {', '.join(unknown)}; "
                         f"it places: {', '.join(fields) or 'none'}")
    if "timeline" in fields and "timeline" not in given:
        wo, wp = E.weeks()
        given["timeline"] = f"{wo}–{wp} weeks" if wo != wp else f"{wo} weeks"
    values = {key: given.get(key, "") for key in fields}
    return values, [key for key in fields if not values[key]]


# ------------------------------------------------------------------ sheet body
class Sheet:
    """The task sheet while it is rebuilt: its rows as (number, xml), the XML after
    <sheetData>, where each template row went, and the merges added for inserted rows."""

    def __init__(self, rows, tail, mapping):
        self.rows, self.tail, self.mapping = rows, tail, mapping
        self.extra_merges = []


def shift_tail(tail, thr, delta):
    """Shift the merged ranges, selections and conditional-format formulas after <sheetData>."""
    tail = re.sub(r'(<mergeCell ref=")([^"]+)(")',
                  lambda m: m.group(1) + shift_ref(m.group(2), thr, delta) + m.group(3), tail)
    tail = re.sub(r'(sqref=")([^"]+)(")',
                  lambda m: m.group(1) + " ".join(shift_ref(p, thr, delta) for p in m.group(2).split()) + m.group(3), tail)
    return re.sub(r"<formula>(.*?)</formula>",
                  lambda m: f"<formula>{shift_formula(m.group(1), thr, delta)}</formula>", tail)


def row_merges(tail, n):
    """The merged ranges that lie on row n alone, as (left, right) columns."""
    return [(a, b) for a, r1, b, r2 in re.findall(r'<mergeCell ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"', tail)
            if int(r1) == int(r2) == n]


def insert_rows(sheet, at, count, clone, merges):
    """Insert `count` clones of a template row at position `at`, each merged as that row
    is; shift everything below. `clone` is (the row's number in the template, its xml)."""
    new, new_merges, old_merges = [], [], list(sheet.extra_merges)
    for n, x in sheet.rows:
        if n >= at:
            new.append((n + count, shift_row_xml(x, n + count, at, count)))
        else:
            new.append((n, shift_row_xml(x, n, at, count)))
    text, text_xml = clone
    for i in range(count):
        rn = at + i
        new.append((rn, shift_row_xml(text_xml, rn, text, rn - text)))
        new_merges += [f"{left}{rn}:{right}{rn}" for left, right in merges]
    sheet.rows = sorted(new, key=lambda t: t[0])
    sheet.mapping = {k: (v + count if v >= at else v) for k, v in sheet.mapping.items()}
    sheet.extra_merges = [shift_ref(r, at, count) for r in old_merges] + new_merges
    sheet.tail = shift_tail(sheet.tail, at, count)


SHARED_RE = re.compile(r'<c r="([A-Z]{1,3})(\d+)"([^>]*)><f([^>]*\bt="shared"[^>]*?)(?:/>|>(.*?)</f>)', re.S)


def unshare(rows, first, last):
    """Write out in full every shared formula with a cell in the task rows.

    A shared formula is stored once, in its first cell, and the others refer to it. The
    task rows are rebuilt from the last one: that first cell may be gone, and every
    clone of it would be a first cell again."""
    masters = {}
    for x in rows.values():
        for m in SHARED_RE.finditer(x):
            ref = re.search(r'\bref="[A-Z]+(\d+):[A-Z]+(\d+)"', m.group(4))
            if ref and m.group(5) is not None:
                si = re.search(r'\bsi="(\d+)"', m.group(4)).group(1)
                masters[si] = (m.group(1), int(m.group(2)), m.group(5), int(ref.group(1)), int(ref.group(2)))
    touched = {si for si, (_, _, _, top, bottom) in masters.items() if top <= last and bottom >= first}

    def write_out(m):
        si = re.search(r'\bsi="(\d+)"', m.group(4)).group(1)
        if si not in touched:
            return m.group(0)
        col, row, text, _, _ = masters[si]
        f = translate(text, int(m.group(2)) - row, col_index(m.group(1)) - col_index(col))
        return f'<c r="{m.group(1)}{m.group(2)}"{m.group(3)}><f>{f}</f>'

    return {n: SHARED_RE.sub(write_out, x) for n, x in rows.items()} if touched else rows


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


# ------------------------------------------------------------------ the sheets
def fill_task_sheet(xml, wmap, found, E, values):
    """The task sheet with the estimate's rows, its lists and its fields written in."""
    task_sheet = found["sheet"]
    _, _, first = found["tasks"]
    last = first + wmap["tasks"]["rows"] - 1
    lists = {name: spot for name, spot in found["lists"].items() if spot[0] == task_sheet}
    fields = {key: spot for key, spot in found["fields"].items() if spot[0] == task_sheet}

    head, rest = xml.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)
    rows, order = {}, []
    for m in ROW_RE.finditer(body):
        n = int(m.group(1))
        rows[n] = m.group(0)
        order.append(n)
    # The rows the map writes to that the template does not store.
    needed = {last} | {row for _, _, row in fields.values()}
    for name, (_, _, row) in lists.items():
        needed |= set(range(row, row + wmap["lists"][name].get("rows", len(E.get(name, [])))))
    for n in sorted(needed - set(rows)):
        rows[n] = f'<row r="{n}"></row>'
        order.append(n)
    order.sort()
    rows = unshare(rows, first, last)
    tpl_data_row = rows[last]

    # ---- task rows -----------------------------------------------------
    # Rows carry their own PART OF; the workbook's summary formulas pick them up by name.
    entries = E.all_rows()
    delta = len(entries) - (last - first + 1)
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
                    for col, key in wmap["tasks"]["columns"].items():
                        x = set_cell(x, col, r[key], numeric=key in NUMERIC)
                    out.append((rn, x))
        else:
            nn = n + delta
            out.append((nn, shift_row_xml(rows[n], nn, last, delta)))
            mapping[n] = nn
    sheet = Sheet(out, shift_tail(tail, last, delta), mapping)

    # ---- lists with blank rows: more items insert clones of the first one ----
    for name, (_, _, top) in lists.items():
        size = wmap["lists"][name].get("rows")
        extra = len(E.get(name, [])) - (size or 0)
        if size and extra > 0:
            insert_rows(sheet, sheet.mapping[top + size - 1], extra, (top, rows[top]), row_merges(tail, top))

    rowmap = dict(sheet.rows)
    for name, (_, col, top) in lists.items():
        place, items = wmap["lists"][name], E.get(name, [])
        if "rows" in place:
            # inserted before the last blank row, so the list runs on from its first one
            size = place["rows"]
            start = sheet.mapping[top + size - 1] - max(0, len(items) - size) - (size - 1)
            targets = [start + i for i in range(len(items))]
        else:
            targets = [sheet.mapping[top + i] for i in range(len(items))]
        for i, (n, text) in enumerate(zip(targets, items)):
            rowmap[n] = put_item(rowmap[n], col, text, place.get("number"), i + 1)
    for key, (_, col, row) in fields.items():
        n = sheet.mapping[row]
        rowmap[n] = set_cell(rowmap[n], col, values[key])

    new_body = "".join(x for _, x in sorted(rowmap.items()))
    tail = sheet.tail
    if sheet.extra_merges:  # cloned from the template's merges, so it has <mergeCells>
        cnt = int(re.search(r'<mergeCells count="(\d+)"', tail).group(1)) + len(sheet.extra_merges)
        tail = re.sub(r'<mergeCells count="\d+">', f'<mergeCells count="{cnt}">', tail)
        tail = tail.replace("</mergeCells>",
                            "".join(f'<mergeCell ref="{r}"/>' for r in sheet.extra_merges) + "</mergeCells>")
    return fix_shared_refs(head + "<sheetData>" + new_body + "</sheetData>" + tail)


def fill_other_sheet(xml, sheet, wmap, found, E, values):
    """Another sheet: its rows stay put, lists run down from their place."""
    edits = {}

    def edit(n, fn):
        prev = edits.get(n, lambda x: x)
        edits[n] = lambda x: fn(prev(x))

    for name, (s, col, row) in found["lists"].items():
        if s != sheet:
            continue
        number = wmap["lists"][name].get("number")
        for i, text in enumerate(E.get(name, [])):
            edit(row + i, lambda x, text=text, k=i + 1: put_item(x, col, text, number, k))
    for key, (s, col, row) in found["fields"].items():
        if s == sheet:
            edit(row, lambda x, col=col, value=values[key]: set_cell(x, col, value))
    if not edits:
        return None
    head, rest = xml.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)
    return head + "<sheetData>" + edit_rows(body, edits) + "</sheetData>" + tail


# ------------------------------------------------------------------ workbook
def main(argv):
    if len(argv) != 4:
        print("usage: build_xlsx.py <data module> <template .xlsx> <map .json> <output .xlsx>", file=sys.stderr)
        if len(argv) == 3:
            print(f"a map is required - {MAP_HELP}", file=sys.stderr)
        return 2
    module, src, map_path, dst = argv
    E = Estimate(module)

    with zipfile.ZipFile(src) as zin:
        try:
            wmap = load_map(map_path)
        except ValueError as e:
            print(f"{e}\nnothing written - {MAP_HELP}", file=sys.stderr)
            return 1
        found, problems = resolve(zin, wmap)
        if not problems:
            problems = item_problems(zin, wmap, found, E)
        try:
            values, empty = workbook_cells(E, wmap.get("fields", {}))
        except ValueError as e:
            problems.append(str(e))
        for line in problems:
            print(line, file=sys.stderr)
        if problems:
            print(f"the map does not fit the template, nothing written - {MAP_HELP}", file=sys.stderr)
            return 1

        core_o, core_p = E.core()
        total_o, total_p = E.total()
        print(f"rows={len(E.all_rows())} parts={E.parts} core={core_o}/{core_p} total={total_o}/{total_p}")
        for name in LISTS:
            if name not in found["lists"] and E.get(name):
                print(f"skipped: {name} ({len(E.get(name))}) - no place in the map")
        for key in empty:
            sheet, col, row = found["fields"][key]
            where = f"{col}{row}" if sheet == found["sheet"] else f"{sheet}!{col}{row}"
            print(f'empty: WORKBOOK["{key}"] -> {where}')

        parts = found["parts"]
        new = {parts[found["sheet"]]: fill_task_sheet(zin.read(parts[found["sheet"]]).decode("utf-8"),
                                                      wmap, found, E, values)}
        for sheet, part in parts.items():
            if sheet != found["sheet"]:
                xml = fill_other_sheet(zin.read(part).decode("utf-8"), sheet, wmap, found, E, values)
                if xml is not None:
                    new[part] = xml
        workbook = zin.read("xl/workbook.xml").decode("utf-8")
        new["xl/workbook.xml"] = re.sub(r"<calcPr[^>]*/>", '<calcPr calcId="191029" fullCalcOnLoad="1"/>', workbook)

        # ---- write -----------------------------------------------------
        with zipfile.ZipFile(dst + ".tmp", "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                d = new[item.filename].encode("utf-8") if item.filename in new else zin.read(item.filename)
                zout.writestr(item, d)
    shutil.move(dst + ".tmp", dst)
    print("written:", dst)
    print("source :", src)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
