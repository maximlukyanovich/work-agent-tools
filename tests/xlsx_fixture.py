"""Small workbooks for the tests of build_xlsx.py, built with the standard library.

    python3 tests/xlsx_fixture.py <shape> <out.xlsx>

writes one for a live run. A workbook is a zip of XML parts; this writes the few a
spreadsheet application needs and nothing else. The shapes are synthetic: `corporate`
puts the labels of the corporate estimate template in its cells and repeats its
mechanics — a summary over the task rows, formulas on another sheet, totals under the
block, merged list rows, a questions sheet — with none of its content.
"""

import io
import sys
import zipfile
from xml.sax.saxutils import escape

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
NS_R = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "application/vnd.openxmlformats-officedocument.spreadsheetml"

# Cell styles: 0 plain, 1 label, 2 text, 3 hours.
STYLES = (
    f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet {NS}>'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">'
    '<alignment wrapText="1"/></xf>'
    '<xf numFmtId="1" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '<dxfs count="1"><dxf><font><b/></font></dxf></dxfs></styleSheet>')


class F:
    """A formula cell: its text, and the attributes of <f> for a shared formula."""

    def __init__(self, text, attrs=""):
        self.text, self.attrs = text, attrs


def blank(n, cols, s):
    return [(f"{c}{n}", None, s) for c in cols]


def cell_xml(ref, value, s, strings):
    st = f' s="{s}"' if s else ""
    if value is None:
        return f'<c r="{ref}"{st}/>'
    if isinstance(value, F):
        attrs = f" {value.attrs}" if value.attrs else ""
        f = (f"<f{attrs}>{escape(value.text, {chr(34): '&quot;'})}</f>" if value.text
             else f"<f{attrs}/>")
        return f'<c r="{ref}"{st}>{f}<v>0</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{ref}"{st}><v>{value}</v></c>'
    if value not in strings:
        strings.append(value)
    return f'<c r="{ref}"{st} t="s"><v>{strings.index(value)}</v></c>'


def sheet_xml(rows, merges, tail, strings):
    """A row with no cells is self-closing, as a spreadsheet application writes an empty
    row that keeps its height."""
    body = "".join((f'<row r="{n}">' + "".join(cell_xml(*c, strings) for c in rows[n]) + "</row>")
                   if rows[n] else f'<row r="{n}" ht="6" customHeight="1"/>' for n in sorted(rows))
    mc = (f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in merges)
          + "</mergeCells>") if merges else ""
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet {NS} {NS_R}>'
            f"<sheetData>{body}</sheetData>{mc}{tail}</worksheet>")


# ------------------------------------------------------------------- shapes
def corporate():
    """The corporate template's layout: labels at I9, B30, B47, B50, B55, task rows
    32-35, blank list rows 48-49 and 51-52 merged B:G, questions on the second sheet."""
    def task_row(n, part="", epic="", task="", desc=""):
        return [(f"B{n}", part or None, 2), (f"C{n}", epic or None, 2), (f"D{n}", task or None, 2),
                (f"E{n}", desc or None, 2), (f"F{n}", None, 3), (f"G{n}", None, 3),
                (f"H{n}", None, 2), (f"I{n}", None, 2),
                (f"J{n}", F(f'IF(B{n}="Backend",F{n}*Rates!$B$2,F{n}*Rates!$B$1)'), 3),
                (f"K{n}", F(f'IF(B{n}="Backend",G{n}*Rates!$B$2,G{n}*Rates!$B$1)'), 3)]

    def summary_row(n, part):
        return [(f"B{n}", part, 2),
                (f"C{n}", F(f'SUM(SUMIF(B32:H35,"{part}",F32:F35))'), 3),
                (f"D{n}", F(f'SUM(SUMIF(B32:H35,"{part}",G32:G35))'), 3)]

    estimate = {
        1: [("H1", "COMPANY NAME:", 1)],
        9: [("I9", "Overall Expected Timeline:", 1), ("J9", None, 1), ("K9", "9-12 weeks", 2)],
        10: [("I10", "The timeline assumes one developer.", 2)],
        11: summary_row(11, "Frontend") + [("E11", F("C11*Rates!B1", 't="shared" ref="E11:E12" si="0"'), 3)],
        12: summary_row(12, "Backend") + [("E12", F("", 't="shared" si="0"'), 3)],
        13: [("B13", "Total hours:", 1), ("C13", F("SUM(C11:C12)"), 3), ("D13", F("SUM(D11:D12)"), 3)],
        30: [("B30", "Development", 1), ("F30", F("F37", 't="shared" ref="F30:G30" si="1"'), 3),
             ("G30", F("", 't="shared" si="1"'), 3)],
        31: blank(31, "BCDEFGHIJK", 2),
        32: task_row(32, "Frontend"),
        33: task_row(33, "Backend"),
        34: task_row(34),
        35: task_row(35, "Frontend", "Sample epic", "Sample task", "Sample description."),
        36: blank(36, "BCDEFGHIJK", 2),
        # A shared formula's second cell is self-closing, and plain cells follow it.
        37: [("B37", "Total", 1), ("F37", F("SUM(F31:F36)", 't="shared" ref="F37:G37" si="2"'), 3),
             ("G37", F("", 't="shared" si="2"'), 3), ("H37", None, 2), ("I37", None, 2),
             ("J37", F("SUM(J31:J36)"), 3), ("K37", F("SUM(K31:K36)"), 3)],
        45: [("B45", "RISKS & EXCLUDES", 1)],
        47: [("B47", "Risks which may cause estimation changes:", 1)] + blank(47, "CDEFG", 1),
        48: blank(48, "BCDEFG", 2),
        49: blank(49, "BCDEFG", 2),
        50: [("B50", "Excludes:", 1)] + blank(50, "CDEFG", 1),
        51: blank(51, "BCDEFG", 2),
        52: blank(52, "BCDEFG", 2),
        55: [("B55", "TECH STACK", 1)],
        56: [("B56", "Sample stack.", 2)],
        58: [("B58", "Lines:", 1), ("C58", F("COUNTA(B48:B52)"), 3)],
    }
    merges = ["I9:J9", "I10:M10", "B30:E30", "B37:E37", "B45:E45",
              "B47:G47", "B48:G48", "B49:G49", "B50:G50", "B51:G51", "B52:G52"]
    tail = ('<conditionalFormatting sqref="F31:G35"><cfRule type="containsBlanks" dxfId="0" priority="1">'
            "<formula>LEN(TRIM(F31))=0</formula></cfRule></conditionalFormatting>"
            '<dataValidations count="1"><dataValidation type="list" allowBlank="1" sqref="B31 B36:B37">'
            "<formula1>Rates!$A$1:$A$2</formula1></dataValidation></dataValidations>")
    questions = {1: [("A1", "#", 1), ("B1", "QUESTIONS", 1)]}
    questions.update({n: [(f"B{n}", None, 2)] for n in range(2, 13)})
    rates = {1: [("A1", "Frontend", 2), ("B1", 50, 3)], 2: [("A2", "Backend", 2), ("B2", 60, 3)]}
    return [("General Estimate", estimate, merges, tail), ("Q&A", questions, [], ""),
            ("Rates", rates, [], "")]


def foreign():
    """Another user's template: the tasks on the second sheet, other columns in another
    order, a cost column filled down as one shared formula, an empty row stored
    self-closing, the questions under the risks on the same sheet, no exclusions and a
    timeline cell the template does not store."""
    def task_row(n, cost):
        return [(f"B{n}", None, 2), (f"C{n}", None, 2), (f"D{n}", None, 3), (f"E{n}", None, 3),
                (f"F{n}", cost, 3)]

    estimate = {
        1: [("A1", "Project estimate", 1)],
        2: [],
        3: [("B3", "Timeline:", 1)],
        4: [("B4", "Rate", 1), ("C4", 40, 3)],
        6: [("B6", "Tasks", 1)],
        7: [("B7", "Feature", 1), ("C7", "Work", 1), ("D7", "Min h", 1), ("E7", "Max h", 1), ("F7", "Cost", 1)],
        8: task_row(8, F("E8*$C$4", 't="shared" ref="F8:F9" si="0"')),
        9: task_row(9, F("", 't="shared" si="0"')),
        10: [("B10", "Total", 1), ("D10", F("SUM(D8:D9)"), 3), ("E10", F("SUM(E8:E9)"), 3),
             ("F10", F("SUM(F8:F9)"), 3)],
        12: [("B12", "Risks:", 1)],
        13: blank(13, "BCDEF", 2),
        15: [("B15", "Open questions", 1)],
        16: blank(16, "BCDEF", 2),
    }
    return [("Cover", {1: [("A1", "Estimate for the client", 1)]}, [], ""),
            ("Estimate", estimate, ["B13:F13", "B16:F16"], "")]


SHAPES = {"corporate": corporate, "foreign": foreign}

# The maps the tests fill each shape by; a live run drafts its own.
MAPS = {
    "corporate": {
        "sheet": "General Estimate",
        "tasks": {"label": "Development", "down": 2, "rows": 4,
                  "columns": {"B": "part", "C": "epic", "D": "task", "E": "description",
                              "F": "optimistic", "G": "pessimistic", "H": "negative", "I": "positive"}},
        "lists": {"RISKS": {"label": "Risks which may cause estimation changes:", "down": 1, "rows": 2},
                  "EXCLUDES": {"label": "Excludes:", "down": 1, "rows": 2},
                  "QUESTIONS": {"sheet": "Q&A", "label": "QUESTIONS", "down": 1, "number": "A"}},
        "fields": {"timeline": {"label": "Overall Expected Timeline:", "right": 2},
                   "timeline_note": {"label": "Overall Expected Timeline:", "down": 1},
                   "stack": {"label": "TECH STACK", "down": 1}},
    },
    "foreign": {
        "sheet": "Estimate",
        "tasks": {"label": "Tasks", "down": 2, "rows": 2,
                  "columns": {"B": "epic", "C": "task", "D": "optimistic", "E": "pessimistic"}},
        "lists": {"RISKS": {"label": "Risks:", "down": 1, "rows": 1},
                  "QUESTIONS": {"label": "Open questions", "down": 1, "rows": 1, "number": "A"}},
        "fields": {"timeline": {"label": "Timeline:", "right": 1}},
    },
}


def build(shape):
    """The workbook of a shape, as bytes of a zip."""
    sheets, strings = SHAPES[shape](), []
    parts = {f"xl/worksheets/sheet{i}.xml": sheet_xml(rows, merges, tail, strings)
             for i, (_, rows, merges, tail) in enumerate(sheets, 1)}
    names = "".join(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
                    for i, (name, *_) in enumerate(sheets, 1))
    rels = "".join(f'<Relationship Id="rId{i}" Type="{DOC_REL}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                   for i in range(1, len(sheets) + 1))
    n = len(sheets)
    rels += (f'<Relationship Id="rId{n + 1}" Type="{DOC_REL}/styles" Target="styles.xml"/>'
             f'<Relationship Id="rId{n + 2}" Type="{DOC_REL}/sharedStrings" Target="sharedStrings.xml"/>')
    overrides = "".join(f'<Override PartName="/{p}" ContentType="{CT}.worksheet+xml"/>' for p in parts)
    head = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    pkg = "http://schemas.openxmlformats.org/package/2006"
    parts.update({
        "[Content_Types].xml":
            f'{head}<Types xmlns="{pkg}/content-types">'
            f'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            f'<Default Extension="xml" ContentType="application/xml"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{CT}.sheet.main+xml"/>'
            f'<Override PartName="/xl/styles.xml" ContentType="{CT}.styles+xml"/>'
            f'<Override PartName="/xl/sharedStrings.xml" ContentType="{CT}.sharedStrings+xml"/>'
            f"{overrides}</Types>",
        "_rels/.rels":
            f'{head}<Relationships xmlns="{pkg}/relationships">'
            f'<Relationship Id="rId1" Type="{DOC_REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f"{head}<workbook {NS} {NS_R}><sheets>{names}</sheets><calcPr/></workbook>",
        "xl/_rels/workbook.xml.rels": f'{head}<Relationships xmlns="{pkg}/relationships">{rels}</Relationships>',
        "xl/styles.xml": STYLES,
        "xl/sharedStrings.xml":
            f'{head}<sst {NS} count="{len(strings)}" uniqueCount="{len(strings)}">'
            + "".join(f"<si><t>{escape(s)}</t></si>" for s in strings) + "</sst>",
    })
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(parts, key=lambda p: (p != "[Content_Types].xml", p)):
            z.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)), parts[name], zipfile.ZIP_DEFLATED)
    return out.getvalue()


def write(shape, path):
    with open(path, "wb") as f:
        f.write(build(shape))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in SHAPES:
        sys.exit(f"usage: xlsx_fixture.py {{{','.join(SHAPES)}}} <out.xlsx>")
    write(sys.argv[1], sys.argv[2])
