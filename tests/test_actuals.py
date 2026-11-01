"""actuals.py — the hours report: estimates from each source, the statistics, the sections,
the strings of a language, and the page they are put into."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins" / "work-tracker" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import actuals  # noqa: E402

PAIR = r"opt (?P<opt>\d+(?:[.,]\d+)?) h, pess (?P<pess>\d+(?:[.,]\d+)?) h"
ONE = r"both (?P<opt>\d+(?:[.,]\d+)?) h"


def issue(key, category="done", spent=0, estimate=None, text="", **extra):
    out = {"key": key, "url": f"https://example/{key}", "summary": f"Task {key}", "type": "Task",
           "status": {"done": "Done", "progress": "In Progress", "todo": "To Do"}[category],
           "category": category, "labels": [], "parent": {"key": "P-1", "summary": "Epic"},
           "assignee": "Dev", "estimate": estimate, "spent": spent,
           "resolved": "2026-10-01" if category == "done" else None, "text": text}
    out.update(extra)
    return out


def build(report, issues, **extra):
    report = {**report, **extra}
    lines = []
    rows = actuals.build(report, issues, warn=lines.append)
    return {r["key"]: r for r in rows}, lines


class FromTextTest(unittest.TestCase):
    def test_the_last_pair_wins_and_a_comma_is_a_decimal(self):
        text = "opt 6 h, pess 9 h. After the split: opt 4,5 h, pess 6 h."
        self.assertEqual(actuals.from_text(text, [PAIR]), (4.5, 6.0))

    def test_without_pess_the_estimate_is_single(self):
        self.assertEqual(actuals.from_text("both 3 h", [PAIR, ONE]), (3.0, 3.0))

    def test_no_match(self):
        self.assertEqual(actuals.from_text("nothing", [PAIR]), (None, None))
        self.assertEqual(actuals.from_text(None, [PAIR]), (None, None))


class BuildTest(unittest.TestCase):
    def test_description_falls_back_to_the_field_and_names_disagreement(self):
        rows, lines = build({"source": "description", "patterns": [PAIR]}, [
            issue("P-2", text="opt 6 h, pess 9 h", estimate=5, spent=7),
            issue("P-3", text="no paragraph", estimate=2, spent=1),
        ])
        self.assertEqual((rows["P-2"]["opt"], rows["P-2"]["pess"]), (6.0, 9.0))
        self.assertEqual((rows["P-3"]["opt"], rows["P-3"]["pess"]), (2, 2))
        self.assertTrue(any(l.startswith("estimate differs: P-2") for l in lines))
        self.assertTrue(any(l.startswith("no estimate in the description: P-3") for l in lines))

    def test_tracker_source_and_warnings(self):
        rows, lines = build({"source": "tracker", "reasons": {"P-3": {"text": "Scope grew.", "url": "u"}}}, [
            issue("P-2", estimate=4, spent=0),
            issue("P-3", estimate=4, spent=6),
            issue("P-4", estimate=4, spent=5),
            issue("P-5", category="todo"),
        ])
        self.assertEqual(rows["P-3"]["reason"], "Scope grew.")
        self.assertEqual(rows["P-4"]["reason"], "")
        self.assertIn("P-2", next(l for l in lines if l.startswith("no hours")))
        self.assertIn("P-4", next(l for l in lines if l.startswith("no reason")))
        self.assertIn("P-5", next(l for l in lines if l.startswith("no estimate")))

    def test_readiness(self):
        rows, _ = build({"source": "tracker", "dev_done": ["Testing"], "readiness": {"P-3": 40}}, [
            issue("P-2", estimate=1),
            issue("P-3", category="progress", estimate=1),
            issue("P-4", category="progress", estimate=1),
            issue("P-5", category="progress", estimate=1, status="Testing"),
            issue("P-6", category="todo", estimate=1),
        ])
        self.assertEqual([rows[k]["readiness"] for k in ("P-2", "P-3", "P-4", "P-5", "P-6")],
                         [100, 40, None, 100, 0])

    def test_groups_keep_their_first_place_and_keys_sort_by_number(self):
        other = {"key": "P-50", "summary": "Other"}
        rows = actuals.build({"source": "tracker", "groups": {"P-11": "Moved"}}, [
            issue("P-10", estimate=1), issue("P-9", estimate=1, parent=other),
            issue("P-2", estimate=1), issue("P-11", estimate=1),
        ], warn=lambda _: None)
        self.assertEqual([(r["key"], r["group"]) for r in rows],
                         [("P-2", "Epic"), ("P-10", "Epic"), ("P-9", "Other"), ("P-11", "Moved")])

class ReviewFixesTest(unittest.TestCase):
    def test_manual_estimates(self):
        rows, lines = build({"source": "manual", "estimates": {"P-2": [4, 6], "P-3": [5], "P-4": 2}}, [
            issue("P-2"), issue("P-3"), issue("P-4"), issue("P-5")])
        self.assertEqual([(rows[k]["opt"], rows[k]["pess"]) for k in ("P-2", "P-3", "P-4", "P-5")],
                         [(4, 6), (5, 5), (2, 2), (None, None)])
        self.assertTrue(any(l.startswith("no estimate: P-5") for l in lines))

    def test_a_group_keeps_its_rows_together(self):
        other = {"key": "E", "summary": "Other"}
        rows = actuals.build({"source": "tracker", "groups": {"P-3": "Other"}}, [
            issue("P-2", estimate=1), issue("P-3", estimate=1), issue("P-4", estimate=1, parent=other),
            issue("P-5", estimate=1),
        ], warn=lambda _: None)
        self.assertEqual([r["key"] for r in rows], ["P-2", "P-5", "P-3", "P-4"])

    def test_readiness_from_a_ticked_list_unless_given(self):
        text = "[x] one\n[x] two\n[ ] three\n[ ] four"
        rows, lines = build({"source": "tracker", "readiness": {"P-3": 70}}, [
            issue("P-2", category="progress", estimate=1, text=text),
            issue("P-3", category="progress", estimate=1, text=text),
            issue("P-4", category="progress", estimate=1, text="no list"),
            issue("P-5", category="progress", estimate=1, text="[ ] one\n[ ] two")])
        self.assertEqual([rows[k]["readiness"] for k in ("P-2", "P-3", "P-4", "P-5")], [50, 70, None, None])
        self.assertEqual([l.split()[2] for l in lines if l.startswith("no readiness")], ["P-4", "P-5"])

    def test_dropped_issues_are_named_and_excluded(self):
        rows, lines = build({"source": "tracker", "exclude": ["P-3"]}, [
            issue("P-2", category="todo", estimate=1, resolution="Won't Do"),
            issue("P-3", category="todo", estimate=1, resolution="Duplicate"),
            issue("P-4", estimate=1, spent=1, resolution="Done"),
            issue("P-5", category="todo", estimate=1, summary="[Cancelled] Localization"),
            issue("P-6", category="todo", estimate=1, summary="[UI] Kept on purpose")], keep=["P-6"])
        self.assertEqual(sorted(rows), ["P-2", "P-4", "P-5", "P-6"])
        self.assertEqual([l.split(":")[1].split()[0] for l in lines if l.startswith("looks dropped")], ["P-2", "P-5"])

    def test_an_answered_readiness_is_not_asked_again(self):
        rows, lines = build({"source": "tracker", "readiness": {"P-2": None}},
                            [issue("P-2", category="progress", estimate=1)])
        self.assertIsNone(rows["P-2"]["readiness"])
        self.assertFalse([l for l in lines if l.startswith("no readiness")])

    def test_null_fields_count_as_left_out(self):
        rows, _ = build({"source": None, "estimates": None, "groups": None, "reasons": None, "dev_done": None,
                         "readiness": None, "patterns": None}, [issue("P-2", estimate=2, spent=3)])
        self.assertEqual(rows["P-2"]["opt"], 2)

    def test_a_zero_estimate_is_none(self):
        rows, lines = build({"source": "tracker"}, [issue("P-2", category="progress", estimate=0, spent=5)])
        self.assertIsNone(rows["P-2"]["opt"])
        self.assertTrue(any(l.startswith("no estimate: P-2") for l in lines))

    def test_a_malformed_manual_estimate_stops(self):
        for value in ("12", [], [4, None], [1, 2, 3], True):
            with self.assertRaises(SystemExit) as stop:
                build({"source": "manual", "estimates": {"P-2": value}}, [issue("P-2")])
            self.assertIn("estimates: P-2", str(stop.exception))

    def test_a_pess_below_opt_is_taken_as_single(self):
        rows, lines = build({"source": "manual", "estimates": {"P-2": [4, 0]}}, [issue("P-2", spent=5)])
        self.assertEqual((rows["P-2"]["opt"], rows["P-2"]["pess"]), (4, 4))
        self.assertTrue(any(l.startswith("pess below opt: P-2") for l in lines))
        self.assertEqual(actuals.stats(list(rows.values()))["over_pess"], 1)

    def test_a_reason_that_is_not_an_object_stops(self):
        with self.assertRaises(SystemExit) as stop:
            build({"source": "tracker", "reasons": {"P-2": "Scope grew."}}, [issue("P-2", estimate=1, spent=2)])
        self.assertIn("reasons: P-2", str(stop.exception))

    def test_an_undated_close_is_named(self):
        rows, _ = build({"source": "tracker"}, [issue("P-2", estimate=2, spent=3, resolved=None)])
        lines = []
        self.assertEqual(actuals.cumulative(list(rows.values()), warn=lines.append), [])
        self.assertTrue(lines[0].startswith("no closing date: P-2"))


class FiguresTest(unittest.TestCase):
    def setUp(self):
        self.rows = actuals.build({"source": "description", "patterns": [PAIR]}, [
            issue("P-2", text="opt 10 h, pess 20 h", spent=15, resolved="2026-10-02", assignee="A"),
            issue("P-3", text="opt 10 h, pess 20 h", spent=8, resolved="2026-10-01", assignee="B"),
            issue("P-4", text="opt 4 h, pess 6 h", spent=7, resolved="2026-10-03", assignee="A"),
            issue("P-5", category="progress", text="opt 2 h, pess 3 h", spent=3),
        ], warn=lambda _: None)

    def test_stats_cover_closed_issues_only(self):
        st = actuals.stats(self.rows)
        self.assertEqual((st["count"], st["opt"], st["pess"], st["fact"]), (3, 24.0, 46.0, 30))
        self.assertAlmostEqual(st["mean_over"], (0.5 - 0.2 + 0.75) / 3)
        self.assertAlmostEqual(st["sum_over"], 30 / 24 - 1)
        self.assertAlmostEqual(st["corridor"], 6 / 22)
        self.assertAlmostEqual(st["mean_over_pess"], (-0.25 - 0.6 + 7 / 6 - 1) / 3)
        self.assertAlmostEqual(st["sum_over_pess"], 30 / 46 - 1)
        self.assertEqual((st["within_opt"], st["within_pess"], st["over_pess"]), (1, 2, 1))
        self.assertEqual((st["closed_from"], st["closed_to"]), ("2026-10-01", "2026-10-03"))

    def test_cumulative_follows_closing_dates(self):
        self.assertEqual([(p["key"], p["opt"], p["pess"]) for p in actuals.cumulative(self.rows)],
                         [("P-3", -2.0, -12.0), ("P-2", 3.0, -17.0), ("P-4", 6.0, -16.0)])

    def test_breakdown(self):
        people = actuals.breakdown(self.rows, "people")
        self.assertEqual([(b["name"], b["count"], b["fact"]) for b in people], [("A", 2, 22), ("B", 1, 8)])
        self.assertEqual([b["name"] for b in actuals.breakdown(self.rows, "epics")], ["Epic"])


class PeriodsTest(unittest.TestCase):
    def logs(self, *dates):
        return [{"id": str(i), "date": d, "hours": 1.5} for i, d in enumerate(dates)]

    def test_weeks_start_on_monday(self):
        issues = [issue("P-2", worklogs=self.logs("2026-10-27", "2026-11-01", "2026-11-02"))]
        self.assertEqual(actuals.periods(issues, None, warn=print),
                         ("week", [{"start": "2026-10-26", "hours": 3.0}, {"start": "2026-11-02", "hours": 1.5}]))

    def test_a_long_span_is_counted_by_month(self):
        period, out = actuals.periods([issue("P-2", worklogs=self.logs("2026-06-03", "2026-10-20"))], None)
        self.assertEqual((period, [p["start"] for p in out]), ("month", ["2026-06-01", "2026-10-01"]))

    def test_without_worklogs(self):
        lines = []
        self.assertEqual(actuals.periods([issue("P-2")], "week", warn=lines.append), ("week", []))
        self.assertTrue(lines[0].startswith("periods:"))


class PageTest(unittest.TestCase):
    def tmp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)

    def run_report(self, report, issues):
        d = self.tmp()
        (d / "r.issues.json").write_text(json.dumps(issues))
        (d / "r.json").write_text(json.dumps({"issues": "r.issues.json", **report}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            actuals.main(d / "r.json")
        [page] = d.glob("r_*.html")
        self.assertRegex(page.name, r"^r_\d{8}\.html$")
        return page.read_text(encoding="utf-8"), out.getvalue(), d

    def test_data_and_strings_are_put_in(self):
        page, printed, _ = self.run_report(
            {"title": "Hours </script>", "language": "ru", "source": "tracker", "sections": ["open"]},
            [issue("P-2", estimate=4, spent=5, summary="</script><b>")])
        self.assertIn('<html lang="ru">', page)
        self.assertIn("<title>Hours &lt;/script&gt;</title>", page)
        self.assertNotIn("/*DATA*/null", page)
        self.assertNotIn("/*STRINGS*/null", page)
        self.assertNotIn("</script><b>", page)
        self.assertIn('"single": true', page)
        self.assertIn('"tile_closed": "Закрыто задач"', page)
        self.assertIn("closed 1 between 2026-10-01 and 2026-10-01; within the optimistic 0", printed)
        self.assertIn("fact 5 h against 4\n", printed)
        self.assertTrue(any(l.startswith("file://") for l in printed.splitlines()))

    def test_excluded_issues_leave_the_periods_too(self):
        log = lambda h: [{"id": "1", "date": "2026-10-27", "hours": h}]
        page, _, _ = self.run_report({"source": "tracker", "sections": ["periods"], "exclude": ["P-3"]},
                                     [issue("P-2", estimate=2, spent=2, worklogs=log(2)),
                                      issue("P-3", estimate=1, spent=12, worklogs=log(12))])
        self.assertIn('"periods": [{"start": "2026-10-26", "hours": 2}]', page)

    def test_a_placeholder_in_the_tracker_text_stays_text(self):
        page, _, _ = self.run_report({"title": "Hours", "source": "tracker"},
                                     [issue("P-2", estimate=1, spent=1, summary="{{TITLE}} /*STRINGS*/null")])
        self.assertIn('"name": "{{TITLE}} /*STRINGS*/null"', page)

    def test_a_custom_row_wider_than_its_columns_stops(self):
        with self.assertRaises(SystemExit) as stop:
            self.run_report({"source": "tracker", "custom": [{"title": "T", "columns": ["Key"], "rows": [["P-2", 1]]}]},
                            [issue("P-2", estimate=1, spent=1)])
        self.assertIn("custom: 'T'", str(stop.exception))

    def test_a_translation_falls_back_to_english_per_key(self):
        d = self.tmp()
        (d / "de.json").write_text(json.dumps({"locale": "de", "total": "Summe"}))
        lines = []
        text = actuals.strings({"language": "de", "strings": "de.json"}, d, warn=lines.append)
        self.assertEqual((text["total"], text["tile_closed"]), ("Summe", "Issues closed"))
        self.assertIn("tile_closed", lines[0])

    def test_a_language_without_strings_stops(self):
        with self.assertRaises(SystemExit) as stop:
            actuals.strings({"language": "de"}, Path("."))
        self.assertIn("translate", str(stop.exception))

    def test_shipped_languages_have_the_same_keys(self):
        en = json.loads((SCRIPTS / "actuals" / "en.json").read_text())
        for f in (SCRIPTS / "actuals").glob("*.json"):
            self.assertEqual(set(json.loads(f.read_text())), set(en), f.name)


if __name__ == "__main__":
    unittest.main()
