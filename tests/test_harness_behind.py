"""harness_behind.py --entries: the delta an audit reads, at each baseline state."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-bootstrap" / "scripts"))

import harness_behind  # noqa: E402

CHANGES = """# Harness changes

Header prose, with a line that looks like `## heading` inline.

## 2026-10-01 · first

What: one.
Check: audit §1.
Applies to: every project.

## 2026-10-02 · second

What: two.
Supersedes: first — the whole of it.
Check: audit §2.
Applies to: every project.

## 2026-10-03 · third

What: three.
Check: audit §3.
Applies to: every project.
"""


class EntriesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.plugin = root / "plugin"
        self.plugin.mkdir()
        (self.plugin / "CHANGES.md").write_text(CHANGES, encoding="utf-8")
        self.project = root / "project"
        (self.project / ".claude").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def profile(self, harness):
        (self.project / ".claude" / "project-profile.md").write_text(
            f"# Profile\n\n## Repository\n\nBaseline: decoy\n\n## Harness\n\n{harness}\n\n## Other\n", encoding="utf-8")

    def entries(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = harness_behind.print_entries(self.project, self.plugin)
        return code, out.getvalue(), err.getvalue()

    def test_prints_every_entry_after_the_baseline_whole(self):
        self.profile("Baseline: `first`")
        code, out, _ = self.entries()
        self.assertEqual(code, 0)
        self.assertEqual(out, "baseline: first — 2 newer entries\n\n"
                              "## 2026-10-02 · second\n\nWhat: two.\nSupersedes: first — the whole of it.\n"
                              "Check: audit §2.\nApplies to: every project.\n\n"
                              "## 2026-10-03 · third\n\nWhat: three.\nCheck: audit §3.\nApplies to: every project.\n")

    def test_one_newer_entry(self):
        self.profile("Baseline: second")
        self.assertTrue(self.entries()[1].startswith("baseline: second — 1 newer entry\n\n## 2026-10-03 · third\n"))

    def test_up_to_date(self):
        self.profile("Baseline: third")
        self.assertEqual(self.entries()[1], "baseline: third — 0 newer entries\n")

    def test_no_baseline_reads_only_the_harness_section(self):
        self.profile("Nothing here.")
        self.assertEqual(self.entries()[1], "baseline: none — run the full audit, which sets one\n")

    def test_off(self):
        self.profile("Baseline: off")
        self.assertEqual(self.entries()[1], "baseline: off\n")

    def test_unknown_baseline(self):
        self.profile("Baseline: later")
        self.assertEqual(self.entries()[1], "baseline: later — not in the installed plugin, "
                                            "whose last entry is third; update it first\n")

    def test_no_profile(self):
        code, out, err = self.entries()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("does not exist", err)


if __name__ == "__main__":
    unittest.main()
