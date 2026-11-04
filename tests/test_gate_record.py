"""gate_record.py: when a branch skips the full gate and when it must run it."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-bootstrap" / "templates" / "gate-record"))

import gate_record  # noqa: E402


def run(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


class GateRecordTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.origin = root / "origin.git"
        self.repo = root / "repo"
        run(root, "git", "init", "-q", "--bare", "-b", "main", str(self.origin))
        run(root, "git", "init", "-q", "-b", "main", str(self.repo))
        for key, value in (("user.name", "T"), ("user.email", "t@example.com"), ("commit.gpgsign", "false")):
            run(self.repo, "git", "config", key, value)
        self.commit("base")
        run(self.repo, "git", "remote", "add", "origin", str(self.origin))
        run(self.repo, "git", "push", "-q", "-u", "origin", "main")
        run(self.repo, "git", "remote", "set-head", "origin", "main")
        run(self.repo, "git", "switch", "-q", "-c", "feat/x")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, name, cwd=None):
        cwd = cwd or self.repo
        (Path(cwd) / f"{name}.ts").write_text(f"{name}\n")
        run(cwd, "git", "add", "-A")
        run(cwd, "git", "commit", "-q", "-m", name)
        return run(cwd, "git", "rev-parse", "--short=7", "HEAD").strip()

    def gate(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = gate_record.main([*args])
        return code, out.getvalue().strip(), err.getvalue().strip()

    def here(self, *args):
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            return self.gate(*args)
        finally:
            os.chdir(cwd)

    def test_full_on_this_tree_skips(self):
        first = self.commit("a")
        self.assertEqual(self.here("check")[1], f"gate: run — {first} has no green record")
        self.assertTrue(self.here("record", "full")[1].startswith("gate: recorded full "))
        self.assertEqual(self.here("check")[1], "gate: skip · full green on this tree")

    def test_targeted_deltas_after_a_full_run_skip(self):
        anchor = self.commit("a")
        self.here("record", "full")
        self.commit("fix1")
        self.here("record", "targeted")
        self.commit("fix2")
        self.here("record", "targeted")
        self.assertEqual(self.here("check")[1], f"gate: skip · full green at {anchor} · targeted since: 2")

    def test_a_delta_without_a_record_runs(self):
        self.commit("a")
        self.here("record", "full")
        hub = self.commit("routes")
        self.commit("fix")
        self.here("record", "targeted")
        self.assertEqual(self.here("check")[1], f"gate: run — {hub} has no green record")

    def test_an_amend_keeps_a_record_of_the_same_tree(self):
        self.commit("a")
        self.here("record", "full")
        run(self.repo, "git", "commit", "-q", "--amend", "-m", "reworded")
        self.assertEqual(self.here("check")[1], "gate: skip · full green on this tree")

    def test_groups_of_one_run_are_recorded_after_the_last(self):
        anchor = self.commit("a")
        self.here("record", "full")
        self.commit("group1")
        self.commit("group2")
        self.assertTrue(self.here("record", "targeted", "--commits", "2")[1].endswith(" · 2 commits"))
        self.assertEqual(self.here("check")[1], f"gate: skip · full green at {anchor} · targeted since: 2")

    def test_commits_goes_with_targeted_only(self):
        self.commit("a")
        self.commit("b")
        self.assertEqual(self.here("record", "full", "--commits", "2")[0], 2)
        self.assertEqual(self.here("record", "targeted", "--commits", "0")[0], 2)

    def test_a_targeted_record_never_stands_for_full(self):
        self.commit("a")
        self.here("record", "targeted")
        self.assertEqual(self.here("check")[1], "gate: run — no full green run since origin/main")
        self.here("record", "full")
        self.here("record", "targeted")
        self.assertEqual(self.here("check")[1], "gate: skip · full green on this tree")

    def test_small_needs_every_commit_recorded_not_a_full_run(self):
        self.commit("a")
        self.here("record", "targeted")
        self.commit("b")
        self.here("record", "targeted")
        self.assertEqual(self.here("check", "--small")[1], "gate: skip · small · targeted on all 2")
        hub = self.commit("routes")
        self.assertEqual(self.here("check", "--small")[1], f"gate: run — {hub} has no green record")

    def test_a_dirty_tree_neither_records_nor_skips(self):
        self.commit("a")
        self.here("record", "full")
        (self.repo / "loose.ts").write_text("x\n")
        self.assertEqual(self.here("record", "full")[1], "gate: not recorded — the tree has uncommitted changes")
        self.assertEqual(self.here("check")[1], "gate: run — the tree has uncommitted changes")

    def test_no_commits_ahead_runs(self):
        self.assertEqual(self.here("check")[1], "gate: run — no commits ahead of origin/main")

    def test_target_is_a_worktree_folder_or_its_branch(self):
        tree = Path(self.tmp.name) / "repo-y"
        run(self.repo, "git", "worktree", "add", "-q", "-b", "feat/y", str(tree), "main")
        self.commit("y", tree)
        self.assertTrue(self.here("record", "full", "feat/y")[1].startswith("gate: recorded full "))
        self.assertEqual(self.gate("check", str(tree))[1], "gate: skip · full green on this tree")
        mine = self.commit("x")
        self.assertEqual(self.here("check")[1], f"gate: run — {mine} has no green record")

    def test_errors(self):
        self.commit("a")
        run(self.repo, "git", "branch", "-q", "feat/z")
        code, out, err = self.here("check", "feat/z")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("checked out nowhere", err)
        self.assertIn("not a directory or a branch", self.here("check", "nope")[2])
        self.assertIn("base not found", self.here("check", "--base", "nope")[2])


if __name__ == "__main__":
    unittest.main()
