"""Fractional task hours: rounded up in estimate_data.py and named by both scripts.

A truncated half hour moves the total without a trace, in the report and in the workbook
alike; rounding up keeps the method's "whole hours, round up", and the named line lets
the estimator see which number moved.
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins" / "work-estimation" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_xlsx as bx  # noqa: E402
import xlsx_fixture  # noqa: E402
from estimate_data import Estimate  # noqa: E402

MODULE = (
    'TASKS = [\n'
    '    ("Catalogue", "Product list", "Filters.", 1.5, 2.5, "", ""),\n'
    '    ("Catalogue", "Product page", "Gallery.", 12, 18.0, "", ""),\n'
    '    ("Checkout", "Payment", "Card payment.", 0.5, 6, "", ""),\n'
    ']\n'
    'RESPONSIVE_RATE = 0.25\n'
    'DERIVED = [("Cross-cutting", "Responsive layout", "Phones.", "responsive", "", "")]\n')
LINES = ["rounded up: Product list 1.5/2.5 -> 2/3", "rounded up: Payment 0.5/6 -> 1/6"]


class RoundUpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.path = Path(cls.dir.name)
        sys.path.insert(0, cls.dir.name)
        (cls.path / "fractional_estimate.py").write_text(MODULE)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.dir.name)
        cls.dir.cleanup()

    def test_hours_are_rounded_up_and_named(self):
        estimate = Estimate("fractional_estimate")
        self.assertEqual([(r["optimistic"], r["pessimistic"]) for r in estimate.rows], [(2, 3), (12, 18), (1, 6)])
        self.assertEqual(estimate.core(), (15, 27))
        self.assertEqual(estimate.overhead(), (4, 7))
        self.assertEqual(estimate.rounded, LINES)

    def test_whole_hours_name_nothing(self):
        (self.path / "whole_estimate.py").write_text('TASKS = [("Epic", "Task", "Description.", 6, 9, "", "")]\n')
        self.assertEqual(Estimate("whole_estimate").rounded, [])

    def test_report_names_the_rounded_rows(self):
        out = subprocess.run([sys.executable, str(SCRIPTS / "render_md.py"), "fractional_estimate",
                              str(self.path / "report.md")], env={**os.environ, "PYTHONPATH": self.dir.name},
                             capture_output=True, text=True, check=True).stdout
        self.assertIn("core=15/27", out)
        self.assertEqual([line for line in out.splitlines() if line.startswith("rounded up:")], LINES)

    def test_workbook_names_the_rounded_rows(self):
        xlsx_fixture.write("corporate", self.path / "template.xlsx")
        (self.path / "template.map.json").write_text(json.dumps(xlsx_fixture.MAPS["corporate"]))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = bx.main(["fractional_estimate", str(self.path / "template.xlsx"),
                            str(self.path / "template.map.json"), str(self.path / "out.xlsx")])
        self.assertEqual(code, 0)
        self.assertIn("core=15/27", out.getvalue())
        self.assertEqual([line for line in out.getvalue().splitlines() if line.startswith("rounded up:")], LINES)
        with zipfile.ZipFile(self.path / "out.xlsx") as z:
            sheet = z.read("xl/worksheets/sheet1.xml").decode()
        self.assertIn('<c r="F32" s="3"><v>2</v></c><c r="G32" s="3"><v>3</v></c>', sheet)


if __name__ == "__main__":
    unittest.main()
