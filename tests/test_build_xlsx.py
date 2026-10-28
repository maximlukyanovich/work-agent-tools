"""build_xlsx.py on XML fragments and on a whole synthetic workbook.

A workbook is a zip of sheet XML, and every inserted row moves the rows, formulas and
merged ranges below it. The fragments pin that arithmetic; the synthetic template from
xlsx_fixture.py runs the script end to end. A real template is still compared byte for
byte before and after a change to the script.
"""

import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-estimation" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_xlsx as bx  # noqa: E402
import xlsx_fixture  # noqa: E402
from estimate_data import Estimate  # noqa: E402


class ShiftTest(unittest.TestCase):
    def test_row_renumbered_and_formulas_shifted(self):
        row = ('<row r="40" spans="1:9"><c r="B40" s="3"><f>SUM(F32:F35)+Rates!$B$3*$F$40</f></c>'
               '<c r="C40" s="4"/></row>')
        self.assertEqual(bx.shift_row_xml(row, 43, 35, 3),
                         '<row r="43" spans="1:9"><c r="B43" s="3"><f>SUM(F32:F38)+Rates!$B$3*$F$43</f></c>'
                         '<c r="C43" s="4"/></row>')

    def test_shared_formula_follows_its_row(self):
        row = '<row r="48"><c r="J48" s="2"><f t="shared" ref="J48:K48" si="1">F48*2</f></c></row>'
        moved = bx.shift_row_xml(row, 51, 48, 3)
        self.assertEqual(bx.fix_shared_refs(moved),
                         '<row r="51"><c r="J51" s="2"><f t="shared" ref="J51:K51" si="1">F51*2</f></c></row>')

    def test_shared_formula_over_rows_is_kept(self):
        cell = '<c r="J40" s="2"><f t="shared" ref="J32:J40" si="0">F32</f></c>'
        self.assertEqual(bx.fix_shared_refs(cell), cell)


class SetCellTest(unittest.TestCase):
    ROW = ('<row r="32" spans="1:9"><c r="B32" s="5"/><c r="E32" s="7" t="s"><v>3</v></c>'
           '<c r="F32" s="6"><v>0</v></c></row>')

    def test_number(self):
        self.assertIn('<c r="F32" s="6"><v>12</v></c>', bx.set_cell(self.ROW, "F", 12, numeric=True))

    def test_text_is_escaped_and_keeps_the_style(self):
        self.assertIn('<c r="B32" s="5" t="inlineStr"><is><t xml:space="preserve">A &amp; B</t></is></c>',
                      bx.set_cell(self.ROW, "B", "A & B"))

    def test_empty_keeps_only_the_style(self):
        self.assertEqual(bx.set_cell(self.ROW, "E", ""),
                         '<row r="32" spans="1:9"><c r="B32" s="5"/><c r="E32" s="7"/>'
                         '<c r="F32" s="6"><v>0</v></c></row>')

    def test_missing_cell(self):
        with self.assertRaisesRegex(KeyError, "cell H32 not found"):
            bx.set_cell(self.ROW, "H", "x")


class InsertRowsTest(unittest.TestCase):
    def test_rows_formulas_and_merges_move_down(self):
        def row(n, inner):
            return f'<row r="{n}">{inner}</row>'

        text_row = row(48, '<c r="B48" s="2"/>')
        sheet = bx.Sheet(
            [(47, row(47, '<c r="B47" s="1"/>')), (48, text_row), (49, row(49, '<c r="B49" s="2"/>')),
             (50, row(50, '<c r="B50" s="1"><f>COUNTA(B48:B49)</f></c>'))],
            '<mergeCells count="1"><mergeCell ref="B50:G50"/></mergeCells>',
            {47: 47, 48: 48, 49: 49, 50: 50}, text_row)
        bx.insert_rows(sheet, 49, 2)
        self.assertEqual(sheet.rows, [
            (47, row(47, '<c r="B47" s="1"/>')),
            (48, text_row),
            (49, row(49, '<c r="B49" s="2"/>')),
            (50, row(50, '<c r="B50" s="2"/>')),
            (51, row(51, '<c r="B51" s="2"/>')),
            (52, row(52, '<c r="B52" s="1"><f>COUNTA(B48:B51)</f></c>')),
        ])
        self.assertEqual(sheet.mapping, {47: 47, 48: 48, 49: 51, 50: 52})
        self.assertEqual(sheet.extra_merges, ["B49:G49", "B50:G50"])
        self.assertEqual(sheet.tail, '<mergeCells count="1"><mergeCell ref="B52:G52"/></mergeCells>')


class LabelsTest(unittest.TestCase):
    XML = ('<row r="9"><c r="I9" s="1" t="s"><v>0</v></c></row>'
           '<row r="30"><c r="B30" t="inlineStr"><is><t>R&amp;D</t></is></c></row>'
           '<row r="55"><c r="B55" s="2" t="s"><v>1</v></c><c r="B56" s="3"/></row>')
    STRINGS = ["Overall Expected Timeline:", "TECH STACK "]

    def test_cell_text(self):
        self.assertEqual([bx.cell_text(self.XML, ref, self.STRINGS) for ref in ("I9", "B30", "B56", "Z1")],
                         ["Overall Expected Timeline:", "R&D", "", ""])

    def test_labels_match(self):
        self.assertEqual(bx.check_labels(self.XML, self.STRINGS, {
            "I9": "Overall Expected Timeline:", "B30": "R&D", "B55": "TECH STACK"}), [])

    def test_labels_differ(self):
        self.assertEqual(bx.check_labels(self.XML, self.STRINGS, {
            "I9": "Overall Expected Timeline:", "B47": "Excludes:", "B55": "Stack"}),
            [("B47", "Excludes:", ""), ("B55", "Stack", "TECH STACK")])

    def test_shared_strings(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("xl/sharedStrings.xml",
                       '<sst><si><t>A &amp; B</t></si>'
                       '<si><r><t>Rich </t></r><r><rPr/><t xml:space="preserve">text</t></r></si></sst>')
        with zipfile.ZipFile(buf) as z:
            self.assertEqual(bx.shared_strings(z), ["A & B", "Rich text"])


class WorkbookCellsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        sys.path.insert(0, cls.dir.name)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.dir.name)
        cls.dir.cleanup()

    def estimate(self, name, hours=(410, 610), extra=""):
        Path(self.dir.name, f"{name}.py").write_text(
            f'TASKS = [("Epic", "Task", "Description.", {hours[0]}, {hours[1]}, "", "")]\n{extra}')
        return Estimate(name)

    def test_weeks(self):
        self.assertEqual(self.estimate("weeks_default").weeks(), (10, 15))
        self.assertEqual(self.estimate("weeks_30", extra="HOURS_PER_WEEK = 30\n").weeks(), (14, 20))

    def test_nothing_given(self):
        self.assertEqual(bx.workbook_cells(self.estimate("wb_none")),
                         ({"K9": "10–15 weeks", "I10": "", "B56": ""}, ["timeline_note", "stack"]))

    def test_one_week_figure(self):
        self.assertEqual(bx.workbook_cells(self.estimate("wb_flat", (120, 120)))[0]["K9"], "3 weeks")

    def test_everything_given(self):
        estimate = self.estimate("wb_all", extra='WORKBOOK = {"timeline": "13-19 weeks", '
                                                 '"timeline_note": "One developer.", "stack": "React"}\n')
        self.assertEqual(bx.workbook_cells(estimate),
                         ({"K9": "13-19 weeks", "I10": "One developer.", "B56": "React"}, []))

    def test_unknown_key(self):
        estimate = self.estimate("wb_typo", extra='WORKBOOK = {"timline": "13-19 weeks"}\n')
        with self.assertRaisesRegex(ValueError, "unknown keys timline; known: timeline, timeline_note, stack"):
            bx.workbook_cells(estimate)


class CorporateWorkbookTest(unittest.TestCase):
    """main() end to end on the synthetic corporate template.

    The hashes were taken before the layout moved out of the script: the same parts,
    byte for byte, are the proof that the move changed nothing. The fragments say
    what broke when a hash does not match."""

    MODULE = (
        'TASKS = [\n'
        '    ("Catalogue", "Product list", "Filters and sorting.", 16, 24, "No filter API yet.", ""),\n'
        '    ("Catalogue", "Product page", "Gallery & price.", 12, 18, "", ""),\n'
        '    ("Checkout", "Payment", "Card payment.", 20, 32, "", "The provider\'s widget fits."),\n'
        ']\n'
        'RESPONSIVE_RATE, I18N_RATE, TESTS_RATE = 0.25, 0.05, 0.1\n'
        'DERIVED = [("Cross-cutting", "Responsive layout", "Phones.", "responsive", "", ""),\n'
        '           ("Cross-cutting", "Localization", "Two languages.", "i18n", "", ""),\n'
        '           ("Cross-cutting", "Automated tests", "Unit and e2e.", "tests", "", "")]\n'
        'RISKS = ["The payment provider is not chosen.", "No staging API.", "Design is a draft."]\n'
        'EXCLUDES = ["Hosting."]\n'
        'QUESTIONS = ["Which payment provider?", "Is there a mobile app?"]\n')
    SHA256 = {
        "xl/worksheets/sheet1.xml": "72f4e8ece4b6a2e192810a52325a7ce5f2f46788c89d46010e5dfc8a0920cf49",
        "xl/worksheets/sheet2.xml": "b989c8ead8a21ce2e3c6de2b06045bdf44fd30d60004bd14d1d8d21d000e60b6",
        "xl/workbook.xml": "35b8bfe04c5ca5f0d29207a860237c4440d8f91003ef9aa6d297fe506189c80f",
    }

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        d = Path(cls.dir.name)
        sys.path.insert(0, cls.dir.name)
        (d / "corporate_estimate.py").write_text(cls.MODULE)
        xlsx_fixture.write("corporate", d / "template.xlsx")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            cls.code = bx.main(["corporate_estimate", str(d / "template.xlsx"), str(d / "out.xlsx")])
        cls.out = out.getvalue()
        with zipfile.ZipFile(d / "out.xlsx") as z:
            cls.parts = {name: z.read(name) for name in cls.SHA256}
        cls.sheet = cls.parts["xl/worksheets/sheet1.xml"].decode()

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.dir.name)
        cls.dir.cleanup()

    def test_exit_and_output(self):
        self.assertEqual(self.code, 0)
        self.assertIn("rows=6 parts=['Frontend'] core=48/74 total=70/107", self.out)
        self.assertIn('empty: WORKBOOK["timeline_note"] -> I10', self.out)

    def test_rows_renumbered_and_the_summary_grows(self):
        self.assertIn('<c r="D37" s="2" t="inlineStr"><is><t xml:space="preserve">Automated tests</t>', self.sheet)
        self.assertIn('<c r="F37" s="3"><v>7</v></c><c r="G37" s="3"><v>10</v></c>', self.sheet)
        self.assertIn("<f>SUM(SUMIF(B32:H37,&quot;Frontend&quot;,F32:F37))</f>", self.sheet)
        self.assertIn('<f t="shared" ref="F30:G30" si="1">F39</f>', self.sheet)

    def test_formulas_below_shift_and_rates_stay(self):
        self.assertIn('<f t="shared" ref="F39:G39" si="2">SUM(F31:F38)</f>', self.sheet)
        self.assertIn('<c r="H39" s="2"/><c r="I39" s="2"/><c r="J39" s="3"><f>SUM(J31:J38)</f>', self.sheet)
        self.assertIn("<f>IF(B37=&quot;Backend&quot;,F37*Rates!$B$2,F37*Rates!$B$1)</f>", self.sheet)
        self.assertIn("<f>COUNTA(B50:B55)</f>", self.sheet)
        self.assertIn('<conditionalFormatting sqref="F31:G37">', self.sheet)

    def test_lists_fill_their_rows_and_an_inserted_row_is_merged(self):
        for ref, text in (("B50", "The payment provider is not chosen."), ("B52", "Design is a draft."),
                          ("B54", "Hosting.")):
            self.assertIn(f'<c r="{ref}" s="2" t="inlineStr"><is><t xml:space="preserve">{text}</t>', self.sheet)
        self.assertIn('<c r="B55" s="2"/>', self.sheet)
        self.assertIn('<mergeCells count="12">', self.sheet)
        self.assertIn('<mergeCell ref="B55:G55"/><mergeCell ref="B51:G51"/></mergeCells>', self.sheet)

    def test_single_cells(self):
        self.assertIn('<c r="K9" s="2" t="inlineStr"><is><t xml:space="preserve">2–3 weeks</t>', self.sheet)
        self.assertIn('<c r="I10" s="2"/>', self.sheet)
        self.assertIn('<c r="B59" s="2"/>', self.sheet)

    def test_questions_sheet(self):
        qa = self.parts["xl/worksheets/sheet2.xml"].decode()
        self.assertIn('<row r="2"><c r="A2" s="2"><v>1</v></c><c r="B2" s="2" t="inlineStr"><is>'
                      '<t xml:space="preserve">Which payment provider?</t></is></c></row>', qa)
        self.assertIn('<row r="4"><c r="B4" s="2"/></row>', qa)

    def test_recalculated_on_open(self):
        self.assertIn(b'<calcPr calcId="191029" fullCalcOnLoad="1"/>', self.parts["xl/workbook.xml"])

    def test_parts_unchanged(self):
        self.assertEqual({name: hashlib.sha256(data).hexdigest() for name, data in self.parts.items()},
                         self.SHA256)


if __name__ == "__main__":
    unittest.main()
