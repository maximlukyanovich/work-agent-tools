# -*- coding: utf-8 -*-
"""Print a workbook template's outline, or where a map puts the estimate in it.

    xlsx_outline.py <template .xlsx>              labels, formulas, merged ranges, by sheet
    xlsx_outline.py <template .xlsx> <map .json>  where each place of the map lands

A map is drafted from the outline instead of the template's XML, and the second form
checks the draft before it is saved. Places are resolved by build_xlsx.py's own code,
so both scripts read a map the same way.
"""

import re
import sys
import zipfile

import build_xlsx as bx


def short(text, n):
    return text if len(text) <= n else text[: n - 3] + "..."


def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def sheet_rows(zin, part):
    """{row number: row xml} with every shared formula written out, and the XML after <sheetData>."""
    xml = zin.read(part).decode("utf-8")
    if "<sheetData>" not in xml:
        return {}, ""
    body, tail = xml.split("<sheetData>", 1)[1].split("</sheetData>", 1)
    rows = {int(m.group(1)): m.group(0) for m in bx.ROW_RE.finditer(body)}
    return bx.unshare(rows, 1, 1 << 20), tail


def relative(formula, n):
    """A formula with its relative rows counted from row n: equal for a filled-down column."""
    return bx.REF_RE.sub(lambda m: m.group(1) + m.group(2) + m.group(3)
                         + (m.group(4) if m.group(3) else f"[{int(m.group(4)) - n}]"), formula)


def outline(zin):
    strings, lines = bx.shared_strings(zin), []
    for i, (name, part) in enumerate(bx.sheet_parts(zin).items(), 1):
        rows, tail = sheet_rows(zin, part)
        cells = list(bx.cells("".join(rows[n] for n in sorted(rows)), strings))
        lines.append(f"== sheet {i}: {name}")

        texts = [(c, n, t.strip()) for c, n, t, f in cells if t.strip() and not f]
        where, by_row = {}, {}
        for c, n, t in texts:
            where.setdefault(t, []).append(f"{c}{n}")
        for c, n, t in texts:
            refs, mark = where[t], ""
            if len(refs) > 1 and not is_number(t):  # a number is no label: its repeats are noise
                some = " ".join(refs[:6]) + (" ..." if len(refs) > 6 else "")
                mark = f" (x{len(refs)}: {some})" if refs[0] == f"{c}{n}" else f" (x{len(refs)})"
            by_row.setdefault(n, []).append(f"{c}{n} {short(t, 60)}{mark}")
        lines += ["  " + " | ".join(by_row[n]) for n in sorted(by_row)]

        groups = []
        for c, n, f in sorted(((c, n, f[1:]) for c, n, _, f in cells if f), key=lambda x: (bx.col_index(x[0]), x[1])):
            key, last = relative(f, n), groups[-1] if groups else None
            if last and last[0] == c and last[2] == n - 1 and last[4] == key:
                last[2] = n
            else:
                groups.append([c, n, n, f, key])
        if groups:
            lines.append("  formulas:")
            lines += [f"    {c}{a}{f'-{c}{b}' if b > a else ''} ={short(f, 50)}" for c, a, b, f, _ in groups]

        merges = re.findall(r'<mergeCell ref="([^"]+)"', tail)
        if merges:
            lines.append("  merged: " + " ".join(merges))
    return lines


def placement(zin, wmap):
    """Where each place of the map lands, in the template's rows; or the problems."""
    found, problems = bx.resolve(zin, wmap)
    if problems:
        return [], problems
    strings, task_sheet, sheets = bx.shared_strings(zin), found["sheet"], {}

    def sheet(name):
        if name not in sheets:
            rows, tail = sheet_rows(zin, found["parts"][name])
            content = {(c, n): t or f for c, n, t, f in bx.cells("".join(rows.values()), strings)}
            sheets[name] = content, tail
        return sheets[name]

    def ref(name, col, row):
        return f"{col}{row}" if name == task_sheet else f"{name}!{col}{row}"

    _, _, first = found["tasks"]
    last = first + wmap["tasks"]["rows"] - 1
    columns = wmap["tasks"]["columns"]
    kept = sorted({c for (c, n), v in sheet(task_sheet)[0].items() if n == last and v and c not in columns},
                  key=bx.col_index)
    lines = [f"tasks: {task_sheet} rows {first}-{last}, clone {last}; "
             + ", ".join(f"{c} {k}" for c, k in columns.items())
             + (f"; kept from row {last}: {' '.join(kept)}" if kept else "")]
    for name in bx.LISTS:
        place = wmap.get("lists", {}).get(name)
        if place is None:
            lines.append(f"{name}: no place - skipped")
            continue
        s, col, row = found["lists"][name]
        if "rows" in place:
            end = row + place["rows"] - 1
            line = f"{name}: {col}{row}{f'-{col}{end}' if end > row else ''}, more rows inserted"
            merges = bx.row_merges(sheet(s)[1], row)
            line += (", merge " + " ".join(f"{a}:{b}" for a, b in merges)) if merges else ""
        else:
            line = f"{name}: {ref(s, col, row)} down"
        lines.append(line + (f", numbers in {place['number']}" if "number" in place else ""))
    for key, (s, col, row) in found["fields"].items():
        now = sheet(s)[0].get((col, row), "")
        now = '"%s"' % short(now, 40) if now else "empty"
        lines.append(f"{key}: {ref(s, col, row)} (now {now})")
    return lines, []


def main(argv):
    if len(argv) not in (1, 2):
        print("usage: xlsx_outline.py <template .xlsx> [<map .json>]", file=sys.stderr)
        return 2
    with zipfile.ZipFile(argv[0]) as zin:
        if len(argv) == 1:
            print("\n".join(outline(zin)))
            return 0
        try:
            lines, problems = placement(zin, bx.load_map(argv[1]))
        except ValueError as e:
            lines, problems = [], [str(e)]
    if problems:
        print("\n".join(problems), file=sys.stderr)
        print(f"the map does not fit the template - {bx.MAP_HELP}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
