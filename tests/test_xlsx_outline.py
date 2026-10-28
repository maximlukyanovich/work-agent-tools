"""xlsx_outline.py: the outline a map is drafted from, and where a map's places land."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-estimation" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import xlsx_fixture  # noqa: E402
import xlsx_outline as xo  # noqa: E402


def open_shape(shape):
    return zipfile.ZipFile(io.BytesIO(xlsx_fixture.build(shape)))


class OutlineTest(unittest.TestCase):
    def test_foreign(self):
        with open_shape("foreign") as z:
            self.assertEqual(xo.outline(z), [
                "== sheet 1: Cover",
                "  A1 Estimate for the client",
                "== sheet 2: Estimate",
                "  A1 Project estimate",
                "  B3 Timeline:",
                "  B4 Rate | C4 40",
                "  B6 Tasks",
                "  B7 Feature | C7 Work | D7 Min h | E7 Max h | F7 Cost",
                "  B10 Total",
                "  B12 Risks:",
                "  B15 Open questions",
                "  formulas:",
                "    D10 =SUM(D8:D9)",
                "    E10 =SUM(E8:E9)",
                "    F8-F9 =E8*$C$4",
                "    F10 =SUM(F8:F9)",
                "  merged: B13:F13 B16:F16",
            ])

    def test_repeats_are_marked(self):
        with open_shape("corporate") as z:
            lines = xo.outline(z)
        self.assertIn("  B11 Frontend (x3: B11 B32 B35)", lines)
        self.assertIn("  B32 Frontend (x3)", lines)
        self.assertIn("    J32-J35 =IF(B32=\"Backend\",F32*Rates!$B$2,F32*Rates!$B$1)", lines)

    def test_numbers_are_not_marked(self):
        self.assertEqual([xo.is_number(t) for t in ("4.0", "12", "Rate", "")], [True, True, False, False])

    def test_long_text_is_cut(self):
        self.assertEqual(xo.short("x" * 70, 60), "x" * 57 + "...")


class PlacementTest(unittest.TestCase):
    def test_foreign(self):
        with open_shape("foreign") as z:
            self.assertEqual(xo.placement(z, xlsx_fixture.MAPS["foreign"]), ([
                "tasks: Estimate rows 8-9, clone 9; B epic, C task, D optimistic, E pessimistic; kept from row 9: F",
                "RISKS: B13, more rows inserted, merge B:F",
                "EXCLUDES: no place - skipped",
                "QUESTIONS: B16, more rows inserted, merge B:F, numbers in A",
                "timeline: C3 (now empty)",
            ], []))

    def test_corporate(self):
        with open_shape("corporate") as z:
            lines, problems = xo.placement(z, xlsx_fixture.MAPS["corporate"])
        self.assertEqual(problems, [])
        self.assertEqual(lines[1:4], ["RISKS: B48-B49, more rows inserted, merge B:G",
                                      "EXCLUDES: B51-B52, more rows inserted, merge B:G",
                                      "QUESTIONS: Q&A!B2 down, numbers in A"])
        self.assertEqual(lines[4], 'timeline: K9 (now "9-12 weeks")')

    def test_label_not_found(self):
        wmap = json.loads(json.dumps(xlsx_fixture.MAPS["foreign"]))
        wmap["fields"]["timeline"]["label"] = "Deadline:"
        with tempfile.TemporaryDirectory() as d:
            Path(d, "t.xlsx").write_bytes(xlsx_fixture.build("foreign"))
            Path(d, "t.map.json").write_text(json.dumps(wmap))
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                code = xo.main([str(Path(d, "t.xlsx")), str(Path(d, "t.map.json"))])
        self.assertEqual(code, 1)
        self.assertIn('fields.timeline: label "Deadline:" not found on sheet "Estimate"', err.getvalue())


if __name__ == "__main__":
    unittest.main()
