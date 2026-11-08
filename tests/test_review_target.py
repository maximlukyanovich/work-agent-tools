"""templates/review-target/review_target.py: the pass target, for every ledger state."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-bootstrap" / "templates" / "review-target"))

import review_target  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class ReviewTargetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        git(self.tmp.name, "init", "-q", "-b", "main", str(self.repo))
        for key, value in (("user.name", "T"), ("user.email", "t@example.com"), ("commit.gpgsign", "false")):
            git(self.repo, "config", key, value)
        self.ledger = Path(self.tmp.name) / "PROJ-1.md"
        self.base = self.commit("base")
        self.first = self.commit("first")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, name):
        (self.repo / f"{name}.txt").write_text(name + "\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", name)
        return git(self.repo, "rev-parse", "--short=7", "HEAD")

    def passes(self, *heads, marked=()):
        lines = ["# Review ledger — PROJ-1", "Trajectory: " + " · ".join(f"P{n} {h} 0/0/0/0 ready" for n, h in enumerate(heads, 1)),
                 "## Open"]
        lines += [f"## Pass {n} — 2026-10-31 — head {h} · base {self.base} · delta — changes requested"
                  + (" · next: full" if n in marked else "") for n, h in enumerate(heads, 1)]
        self.ledger.write_text("\n".join(lines) + "\n")

    def target(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = review_target.main(["--ledger", str(self.ledger), "--tree", str(self.repo), *args])
        return code, out.getvalue().strip(), err.getvalue().strip()

    def test_no_ledger(self):
        self.assertEqual(self.target()[1], "target: whole — no ledger")

    def test_a_ledger_without_a_pass(self):
        self.ledger.write_text("# Review ledger — PROJ-1\n## Open\n")
        self.assertEqual(self.target()[1], "target: whole — the ledger has no pass")

    def test_same_head(self):
        self.passes(self.first)
        self.assertEqual(self.target()[1], f"target: none · head {self.first} — the ledger's last head is HEAD")

    def test_delta_from_the_last_pass(self):
        self.passes(self.base, self.first)
        second = self.commit("second")
        self.assertEqual(self.target()[1],
                         f"target: delta · git diff {self.first}..{second} — the last head is an ancestor of HEAD")

    def test_a_fix_round_line_is_not_a_pass(self):
        self.passes(self.first)
        second = self.commit("second")
        with self.ledger.open("a", encoding="utf-8") as ledger:
            ledger.write(f"## Fix round — 2026-10-31 — head {second} · closes R1\n")
        self.assertEqual(self.target()[1],
                         f"target: delta · git diff {self.first}..{second} — the last head is an ancestor of HEAD")

    def test_trajectory_when_no_pass_header_parses(self):
        self.ledger.write_text(f"# Review ledger — PROJ-1\nTrajectory: P1 {self.base} 0/1/0/0 changes\n")
        self.assertEqual(self.target()[1],
                         f"target: delta · git diff {self.base}..{self.first} — the last head is an ancestor of HEAD")

    def test_fixes_amended_into_the_reviewed_commit(self):
        self.passes(self.first)
        (self.repo / "first.txt").write_text("fixed\n")
        git(self.repo, "commit", "-q", "-a", "--amend", "--no-edit")
        head = git(self.repo, "rev-parse", "--short=7", "HEAD")
        self.assertEqual(self.target()[1], f"target: rewritten · git diff {self.first} {head} · replaced {self.first}"
                                           " — the last head is not an ancestor of HEAD")

    def test_a_last_head_the_repository_lost(self):
        self.passes("0123abc")
        self.assertEqual(self.target()[1], "target: whole — the last head 0123abc is not in the repository")

    def test_the_last_pass_asked_for_full(self):
        self.passes(self.base, self.first, marked=(2,))
        self.commit("second")
        self.assertEqual(self.target()[1], "target: whole — the last pass asked for full")

    def test_asked_for_full_with_no_new_commits(self):
        self.passes(self.first, marked=(1,))
        self.assertEqual(self.target()[1], f"target: none · head {self.first} — the ledger's last head is HEAD")

    def test_asked_for_full_outranks_a_rewritten_head(self):
        self.passes(self.first, marked=(1,))
        git(self.repo, "commit", "-q", "--amend", "-m", "first again")
        self.assertEqual(self.target()[1], "target: whole — the last pass asked for full")

    def test_explicit_range_outranks_asked_for_full(self):
        self.passes(self.first, marked=(1,))
        second = self.commit("second")
        self.assertEqual(self.target("--range", f"{self.first}..{second}")[1],
                         f"target: range · git diff {self.first}..{second} — explicit range")

    def test_a_pass_after_the_full_one_is_a_delta_again(self):
        self.passes(self.base, self.first, marked=(1,))
        second = self.commit("second")
        self.assertEqual(self.target()[1],
                         f"target: delta · git diff {self.first}..{second} — the last head is an ancestor of HEAD")

    def test_full_ignores_the_ledger(self):
        self.passes(self.first)
        self.assertEqual(self.target("--full")[1], "target: whole — full")

    def test_explicit_range_outranks_the_ledger_and_full(self):
        self.passes(self.first)
        self.assertEqual(self.target("--full", "--range", f"{self.base}..{self.first}")[1],
                         f"target: range · git diff {self.base}..{self.first} — explicit range")

    def test_explicit_range_with_a_rewritten_base(self):
        git(self.repo, "commit", "-q", "--amend", "-m", "first again")
        head = git(self.repo, "rev-parse", "--short=7", "HEAD")
        self.assertEqual(self.target("--range", f"{self.first}..")[1],
                         f"target: rewritten · git diff {self.first} {head} · replaced {self.first}"
                         " — the range's base is not an ancestor of its head")

    def test_a_ledger_directory_is_refused_not_read_as_no_ledger(self):
        self.ledger.mkdir()
        code, out, err = self.target()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("is a directory", err)

    def test_unresolved_head_or_range(self):
        self.assertEqual(self.target("--head", "nope")[0], 2)
        code, _, err = self.target("--range", "nope..HEAD")
        self.assertEqual(code, 2)
        self.assertIn("does not resolve", err)
        self.assertEqual(self.target("--range", f"{self.base}...{self.first}")[0], 2)


if __name__ == "__main__":
    unittest.main()
