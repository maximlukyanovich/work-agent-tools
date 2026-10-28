"""build_xlsx.py on XML fragments and on a whole synthetic workbook.

A workbook is a zip of sheet XML, and every inserted row moves the rows, formulas and
merged ranges below it. The fragments pin that arithmetic; the synthetic template from
xlsx_fixture.py runs the script end to end. A real template is still compared byte for
byte before and after a change to the script.
"""

import contextlib
import hashlib
import io
import json
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

    def test_self_closing_formula_leaves_the_next_cells_alone(self):
        row = ('<row r="42"><c r="G42"><f t="shared" si="2"/></c><c r="H42" s="1"/>'
               '<c r="J42"><f>SUM(J31:J41)</f></c></row>')
        self.assertEqual(bx.shift_row_xml(row, 102, 35, 60),
                         '<row r="102"><c r="G102"><f t="shared" si="2"/></c><c r="H102" s="1"/>'
                         '<c r="J102"><f>SUM(J31:J101)</f></c></row>')

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

    def test_missing_cell_is_created_in_column_order(self):
        self.assertEqual(bx.set_cell(self.ROW, "C", "x"),
                         '<row r="32" spans="1:9"><c r="B32" s="5"/>'
                         '<c r="C32" t="inlineStr"><is><t xml:space="preserve">x</t></is></c>'
                         '<c r="E32" s="7" t="s"><v>3</v></c><c r="F32" s="6"><v>0</v></c></row>')
        self.assertTrue(bx.set_cell(self.ROW, "H", 5, numeric=True).endswith('<c r="H32"><v>5</v></c></row>'))

    def test_cell_in_a_self_closing_row(self):
        self.assertEqual(bx.set_cell('<row r="3" ht="6"/>', "C", 2, numeric=True),
                         '<row r="3" ht="6"><c r="C3"><v>2</v></c></row>')

    def test_list_number_takes_the_text_style(self):
        self.assertEqual(bx.put_item('<row r="2"><c r="B2" s="4"/></row>', "B", "Why?", "A", 1),
                         '<row r="2"><c r="A2" s="4"><v>1</v></c>'
                         '<c r="B2" s="4" t="inlineStr"><is><t xml:space="preserve">Why?</t></is></c></row>')


class InsertRowsTest(unittest.TestCase):
    def test_rows_formulas_and_merges_move_down(self):
        def row(n, inner):
            return f'<row r="{n}">{inner}</row>'

        text_row = row(48, '<c r="B48" s="2"/>')
        sheet = bx.Sheet(
            [(47, row(47, '<c r="B47" s="1"/>')), (48, text_row), (49, row(49, '<c r="B49" s="2"/>')),
             (50, row(50, '<c r="B50" s="1"><f>COUNTA(B48:B49)</f></c>'))],
            '<mergeCells count="1"><mergeCell ref="B50:G50"/></mergeCells>',
            {47: 47, 48: 48, 49: 49, 50: 50})
        bx.insert_rows(sheet, 49, 2, (48, text_row), [("B", "G")])
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

    def test_merges_of_a_row(self):
        tail = '<mergeCells count="3"><mergeCell ref="B47:G48"/><mergeCell ref="B48:D48"/><mergeCell ref="E48:G48"/>'
        self.assertEqual(bx.row_merges(tail, 48), [("B", "D"), ("E", "G")])


class SharedFormulaTest(unittest.TestCase):
    def test_translate(self):
        self.assertEqual(bx.translate('IF(B32=&quot;B32&quot;,LOG10(F32)*$C$4+Rates!B$1,0)', 2, 1),
                         'IF(C34=&quot;B32&quot;,LOG10(G34)*$C$4+Rates!C$1,0)')

    def test_written_out_when_it_touches_the_task_rows(self):
        rows = {7: '<row r="7"><c r="F7"><f t="shared" ref="F7:G7" si="0">SUM(F1:F6)</f></c>'
                   '<c r="G7"><f t="shared" si="0"/></c></row>',
                8: '<row r="8"><c r="F8" s="3"><f t="shared" ref="F8:F9" si="1">E8*$C$4</f><v>0</v></c></row>',
                9: '<row r="9"><c r="F9" s="3"><f t="shared" si="1"/><v>0</v></c></row>'}
        out = bx.unshare(rows, 8, 9)
        self.assertEqual(out[7], rows[7])
        self.assertEqual(out[8], '<row r="8"><c r="F8" s="3"><f>E8*$C$4</f><v>0</v></c></row>')
        self.assertEqual(out[9], '<row r="9"><c r="F9" s="3"><f>E9*$C$4</f><v>0</v></c></row>')


CORPORATE_MAP = {
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
}

FOREIGN_MAP = {
    "sheet": "Estimate",
    "tasks": {"label": "Tasks", "down": 2, "rows": 2,
              "columns": {"B": "epic", "C": "task", "D": "optimistic", "E": "pessimistic"}},
    "lists": {"RISKS": {"label": "Risks:", "down": 1, "rows": 1},
              "QUESTIONS": {"label": "Open questions", "down": 1, "rows": 1, "number": "A"}},
    "fields": {"timeline": {"label": "Timeline:", "right": 1}},
}


def with_map(base, **changes):
    """A copy of a map with some of its keys replaced; None removes one. A dotted key
    reaches inside: "lists.RISKS"."""
    wmap = json.loads(json.dumps(base))
    for key, value in changes.items():
        *path, last = key.split(".")
        node = wmap
        for part in path:
            node = node[part]
        if value is None:
            del node[last]
        else:
            node[last] = value
    return wmap


class ResolveTest(unittest.TestCase):
    def setUp(self):
        self.zin = zipfile.ZipFile(io.BytesIO(xlsx_fixture.build("corporate")))

    def tearDown(self):
        self.zin.close()

    def test_found(self):
        found, problems = bx.resolve(self.zin, CORPORATE_MAP)
        self.assertEqual(problems, [])
        self.assertEqual(found["tasks"], ("General Estimate", "B", 32))
        self.assertEqual(found["lists"], {"RISKS": ("General Estimate", "B", 48),
                                          "EXCLUDES": ("General Estimate", "B", 51),
                                          "QUESTIONS": ("Q&A", "B", 2)})
        self.assertEqual(found["fields"], {"timeline": ("General Estimate", "K", 9),
                                           "timeline_note": ("General Estimate", "I", 10),
                                           "stack": ("General Estimate", "B", 56)})
        self.assertEqual(found["parts"]["Q&A"], "xl/worksheets/sheet2.xml")

    def test_first_sheet_by_default(self):
        found, _ = bx.resolve(self.zin, with_map(CORPORATE_MAP, sheet=None))
        self.assertEqual(found["sheet"], "General Estimate")

    def test_every_problem_is_named(self):
        wmap = with_map(CORPORATE_MAP, **{
            "fields.stack": {"label": "Stack", "down": 1},
            "fields.note": {"label": "Frontend"},
            "fields.inside": {"label": "Development", "down": 3},
            "lists.QUESTIONS": {"sheet": "Questions", "label": "QUESTIONS", "rows": 2}})
        _, problems = bx.resolve(self.zin, wmap)
        self.assertEqual(problems, [
            'lists.QUESTIONS: rows are inserted only on the task sheet "General Estimate"',
            'lists.QUESTIONS: sheet "Questions" is not in the workbook; it has General Estimate, Q&A, Rates',
            'fields.stack: label "Stack" not found on sheet "General Estimate"',
            'fields.note: label "Frontend" found 3 times: B11 B32 B35 on sheet "General Estimate"',
            "fields.inside: B33 is inside the task rows 32-35",
        ])

    def test_cells(self):
        xml = ('<row r="9"><c r="I9" s="1" t="s"><v>0</v></c></row>'
               '<row r="30"><c r="B30" t="inlineStr"><is><t>R&amp;D</t></is></c><c r="C30"><f>B30</f><v>R&amp;D</v></c></row>'
               '<row r="55"><c r="B55" s="2" t="s"><v>1</v></c><c r="B56" s="3"/><c r="C56"><v>4</v></c></row>')
        self.assertEqual(list(bx.cells(xml, ["Overall Expected Timeline:", "TECH STACK "])), [
            ("I", 9, "Overall Expected Timeline:", ""), ("B", 30, "R&D", ""), ("C", 30, "R&D", "=B30"),
            ("B", 55, "TECH STACK ", ""), ("B", 56, "", ""), ("C", 56, "4", "")])

    def test_shared_strings(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("xl/sharedStrings.xml",
                       '<sst><si><t>A &amp; B</t></si>'
                       '<si><r><t>Rich </t></r><r><rPr/><t xml:space="preserve">text</t></r></si></sst>')
        with zipfile.ZipFile(buf) as z:
            self.assertEqual(bx.shared_strings(z), ["A & B", "Rich text"])


class WorkbookCellsTest(unittest.TestCase):
    FIELDS = CORPORATE_MAP["fields"]

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
        self.assertEqual(bx.workbook_cells(self.estimate("wb_none"), self.FIELDS),
                         ({"timeline": "10–15 weeks", "timeline_note": "", "stack": ""},
                          ["timeline_note", "stack"]))

    def test_one_week_figure(self):
        self.assertEqual(bx.workbook_cells(self.estimate("wb_flat", (120, 120)), self.FIELDS)[0]["timeline"],
                         "3 weeks")

    def test_everything_given(self):
        estimate = self.estimate("wb_all", extra='WORKBOOK = {"timeline": "13-19 weeks", '
                                                 '"timeline_note": "One developer.", "stack": "React"}\n')
        self.assertEqual(bx.workbook_cells(estimate, self.FIELDS),
                         ({"timeline": "13-19 weeks", "timeline_note": "One developer.", "stack": "React"}, []))

    def test_no_timeline_in_the_map(self):
        self.assertEqual(bx.workbook_cells(self.estimate("wb_stack"), {"stack": {}}), ({"stack": ""}, ["stack"]))

    def test_key_the_map_does_not_place(self):
        estimate = self.estimate("wb_typo", extra='WORKBOOK = {"timline": "13-19 weeks"}\n')
        with self.assertRaisesRegex(ValueError, "keys the map does not place: timline; "
                                                "it places: timeline, timeline_note, stack"):
            bx.workbook_cells(estimate, self.FIELDS)


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
        (d / "template.map.json").write_text(json.dumps(CORPORATE_MAP))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            cls.code = bx.main(["corporate_estimate", str(d / "template.xlsx"), str(d / "template.map.json"),
                                str(d / "out.xlsx")])
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


class MainRun:
    """main() on a fixture template and a map, each run in its own files."""

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        sys.path.insert(0, cls.dir.name)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.dir.name)
        cls.dir.cleanup()

    @classmethod
    def run_main(cls, name, shape, wmap, module=CorporateWorkbookTest.MODULE):
        """(exit code, stdout, stderr, the output's path)."""
        d = Path(cls.dir.name)
        (d / f"{name}.py").write_text(module)
        xlsx_fixture.write(shape, d / f"{name}.xlsx")
        (d / f"{name}.map.json").write_text(json.dumps(wmap))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = bx.main([name, str(d / f"{name}.xlsx"), str(d / f"{name}.map.json"),
                            str(d / f"{name}.out.xlsx")])
        return code, out.getvalue(), err.getvalue(), d / f"{name}.out.xlsx"


class ForeignWorkbookTest(MainRun, unittest.TestCase):
    """Another user's template, filled by its own map."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.code, cls.out, cls.err, path = cls.run_main("foreign_estimate", "foreign", FOREIGN_MAP)
        with zipfile.ZipFile(path) as z:
            cls.sheet = z.read("xl/worksheets/sheet2.xml").decode()
            cls.cover = z.read("xl/worksheets/sheet1.xml")
        with zipfile.ZipFile(io.BytesIO(xlsx_fixture.build("foreign"))) as z:
            cls.template_cover = z.read("xl/worksheets/sheet1.xml")

    def test_exit_and_output(self):
        self.assertEqual((self.code, self.err), (0, ""))
        self.assertIn("skipped: EXCLUDES (1) - no place in the map", self.out)
        self.assertNotIn("empty:", self.out)

    def test_task_columns_by_the_map(self):
        self.assertIn('<row r="8"><c r="B8" s="2" t="inlineStr"><is><t xml:space="preserve">Catalogue</t></is></c>'
                      '<c r="C8" s="2" t="inlineStr"><is><t xml:space="preserve">Product list</t></is></c>'
                      '<c r="D8" s="3"><v>16</v></c><c r="E8" s="3"><v>24</v></c>'
                      '<c r="F8" s="3"><f>E8*$C$4</f><v>0</v></c></row>', self.sheet)
        self.assertIn('<c r="E13" s="3"><v>10</v></c><c r="F13" s="3"><f>E13*$C$4</f><v>0</v></c>', self.sheet)
        self.assertNotIn("Filters and sorting.", self.sheet)
        self.assertNotIn('t="shared"', self.sheet)

    def test_totals_follow_the_block(self):
        self.assertIn('<c r="D14" s="3"><f>SUM(D8:D13)</f>', self.sheet)
        self.assertIn('<c r="F14" s="3"><f>SUM(F8:F13)</f>', self.sheet)

    def test_empty_row_and_created_cell(self):
        self.assertIn('<row r="2" ht="6" customHeight="1"/><row r="3"><c r="B3" s="1" t="s"><v>2</v></c>'
                      '<c r="C3" t="inlineStr"><is><t xml:space="preserve">2–3 weeks</t></is></c></row>', self.sheet)

    def test_lists_with_one_blank_row(self):
        for n, text in ((17, "The payment provider is not chosen."), (19, "Design is a draft.")):
            self.assertIn(f'<c r="B{n}" s="2" t="inlineStr"><is><t xml:space="preserve">{text}</t>', self.sheet)
        self.assertIn('<row r="22"><c r="A22" s="2"><v>1</v></c><c r="B22" s="2" t="inlineStr"><is>'
                      '<t xml:space="preserve">Which payment provider?</t>', self.sheet)
        self.assertIn('<c r="A23" s="2"><v>2</v></c>', self.sheet)
        self.assertIn('<mergeCells count="5"><mergeCell ref="B19:F19"/><mergeCell ref="B23:F23"/>'
                      '<mergeCell ref="B17:F17"/><mergeCell ref="B18:F18"/><mergeCell ref="B22:F22"/></mergeCells>',
                      self.sheet)

    def test_other_sheet_untouched(self):
        self.assertEqual(self.cover, self.template_cover)


class MapProblemTest(MainRun, unittest.TestCase):
    """A map that does not fit stops the run: exit 1, every problem named, no workbook."""

    def check(self, name, wmap, message, module=CorporateWorkbookTest.MODULE):
        code, out, err, path = self.run_main(name, "corporate", wmap, module)
        self.assertEqual(code, 1)
        self.assertIn(message, err)
        self.assertIn("nothing written", err)
        self.assertFalse(path.exists())
        self.assertFalse(Path(f"{path}.tmp").exists())

    def test_unknown_key(self):
        self.check("map_key", with_map(CORPORATE_MAP, colums={}), "unknown key 'colums'")

    def test_unknown_row_key(self):
        self.check("map_column", with_map(CORPORATE_MAP, **{"tasks.columns.B": "parts"}),
                   "tasks.columns.B: unknown key 'parts'; known: part, epic, task")

    def test_unknown_list(self):
        self.check("map_list", with_map(CORPORATE_MAP, **{"lists.RISK": {"label": "Excludes:"}}),
                   "lists: unknown list 'RISK'; known: RISKS, EXCLUDES, QUESTIONS")

    def test_workbook_key_without_a_place(self):
        self.check("map_field", with_map(CORPORATE_MAP, **{"fields.stack": None}),
                   "WORKBOOK has keys the map does not place: stack",
                   CorporateWorkbookTest.MODULE + 'WORKBOOK = {"stack": "React"}\n')

    def test_label_not_found(self):
        self.check("map_label", with_map(CORPORATE_MAP, **{"fields.stack.label": "Stack"}),
                   'fields.stack: label "Stack" not found on sheet "General Estimate"')

    def test_list_would_overwrite_text(self):
        self.check("map_overwrite", with_map(CORPORATE_MAP, **{"lists.RISKS": {"label": "TECH STACK", "down": 1}}),
                   'lists.RISKS: General Estimate!B56 holds "Sample stack." - the list would overwrite it')

    def test_three_arguments(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(bx.main(["data", "template.xlsx", "out.xlsx"]), 2)
        self.assertIn('a map is required - see reference/data-format.md, "The workbook map"', err.getvalue())


if __name__ == "__main__":
    unittest.main()
