"""build_xlsx.py's row arithmetic on XML fragments: renumbering, formula shifts, cell writes.

A workbook is a zip of sheet XML, and every inserted row moves the rows, formulas and
merged ranges below it. These fragments pin that arithmetic; the whole workbook is
compared byte for byte on a real template before and after a change to the script.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-estimation" / "scripts"))

import build_xlsx as bx  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
