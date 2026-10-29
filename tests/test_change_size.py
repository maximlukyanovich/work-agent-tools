"""change_size.py: the size line a handoff reads, at the thresholds' edges."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "work-bootstrap" / "scripts"))

import change_size  # noqa: E402


def run(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class ChangeSizeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.origin = root / "origin.git"
        self.repo = root / "repo"
        run(root, "git", "init", "-q", "--bare", "-b", "main", str(self.origin))
        run(root, "git", "init", "-q", "-b", "main", str(self.repo))
        for key, value in (("user.name", "T"), ("user.email", "t@example.com"), ("commit.gpgsign", "false")):
            run(self.repo, "git", "config", key, value)
        self.write("README.md", "base\n")
        self.commit("base")
        run(self.repo, "git", "remote", "add", "origin", str(self.origin))
        run(self.repo, "git", "push", "-q", "-u", "origin", "main")
        run(self.repo, "git", "remote", "set-head", "origin", "main")
        run(self.repo, "git", "switch", "-q", "-c", "feat/x")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text, mode="w"):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, mode) as f:
            f.write(text)

    def commit(self, message):
        run(self.repo, "git", "add", "-A")
        run(self.repo, "git", "commit", "-q", "-m", message)

    def lines_in(self, files, total, suffix=".ts"):
        per, extra = divmod(total, files)
        for n in range(files):
            self.write(f"src/f{n}{suffix}", "x\n" * (per + (1 if n < extra else 0)))
        self.commit("change")

    def size(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = change_size.main([*args])
        return code, out.getvalue().strip(), err.getvalue().strip()

    def in_repo(self, *args):
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            return self.size(*args)
        finally:
            os.chdir(cwd)

    def test_lines_at_the_edge(self):
        self.lines_in(1, 100)
        self.assertEqual(self.in_repo()[1],
                         "size: small · files 1 · +100 −0 · prose-only no · uncommitted no")
        self.write("src/f0.ts", "x\n", "a")
        self.commit("one more")
        self.assertEqual(self.in_repo()[1],
                         "size: normal · files 1 · +101 −0 · prose-only no · uncommitted no — lines 101 > 100")

    def test_files_at_the_edge(self):
        self.lines_in(5, 10)
        self.assertTrue(self.in_repo()[1].startswith("size: small · files 5 "))
        self.lines_in(6, 12)
        self.assertTrue(self.in_repo()[1].endswith("— files 6 > 5"))

    def test_prose_only_up_to_its_own_limit(self):
        self.write("docs/guide.txt", "x\n" * 150)
        self.write("NOTES.md", "x\n" * 150)
        self.commit("prose")
        self.assertEqual(self.in_repo()[1],
                         "size: small · files 2 · +300 −0 · prose-only yes · uncommitted no")
        self.write("NOTES.md", "x\n", "a")
        self.commit("one more")
        self.assertTrue(self.in_repo()[1].endswith("— prose lines 301 > 300"))

    def test_prose_mixed_with_code_takes_the_code_limit(self):
        self.write("NOTES.md", "x\n" * 150)
        self.write("src/a.ts", "x\n")
        self.commit("mixed")
        self.assertIn("prose-only no", self.in_repo()[1])
        self.assertTrue(self.in_repo()[1].endswith("— lines 151 > 100"))

    def test_binary_file_counts_as_a_file_without_lines(self):
        self.write("img.png", "\0\1\2binary", "w")
        self.commit("binary")
        self.assertEqual(self.in_repo()[1],
                         "size: small · files 1 · +0 −0 · prose-only no · uncommitted no")

    def test_rename_counts_once(self):
        self.write("src/old.ts", "x\n" * 80)
        self.commit("add")
        run(self.repo, "git", "push", "-q", "origin", "feat/x:main")
        run(self.repo, "git", "mv", "src/old.ts", "src/new.ts")
        self.commit("rename")
        self.assertEqual(self.in_repo()[1],
                         "size: small · files 1 · +0 −0 · prose-only no · uncommitted no")

    def test_uncommitted_is_noticed_not_counted(self):
        self.lines_in(1, 10)
        self.write("src/f0.ts", "y\n" * 500, "a")
        self.assertEqual(self.in_repo()[1],
                         "size: small · files 1 · +10 −0 · prose-only no · uncommitted yes")

    def test_target_directory_and_branch(self):
        self.lines_in(1, 20)
        expected = "size: small · files 1 · +20 −0 · prose-only no · uncommitted no"
        self.assertEqual(self.size(str(self.repo))[1], expected)
        tree = Path(self.tmp.name) / "repo-y"
        run(self.repo, "git", "worktree", "add", "-q", "-b", "feat/y", str(tree), "main")
        (tree / "y.ts").write_text("y\n" * 3)
        run(tree, "git", "add", "-A")
        run(tree, "git", "commit", "-q", "-m", "y")
        self.assertEqual(self.in_repo("feat/y")[1],
                         "size: small · files 1 · +3 −0 · prose-only no · uncommitted no")
        run(self.repo, "git", "branch", "-q", "feat/z", "feat/x")
        self.assertEqual(self.in_repo("feat/z")[1], expected)

    def test_base_from_the_flag_and_errors(self):
        self.lines_in(1, 5)
        self.assertEqual(self.in_repo("--base", "main")[0], 0)
        code, out, err = self.in_repo("--base", "nope")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("base not found", err)
        code, _, err = self.in_repo("no-such-branch")
        self.assertEqual(code, 2)
        self.assertIn("not a directory or a branch", err)

    def test_thresholds_are_arguments(self):
        self.lines_in(2, 40)
        self.assertTrue(self.in_repo("--max-lines", "30", "--max-files", "1")[1]
                        .endswith("— files 2 > 1, lines 40 > 30"))


if __name__ == "__main__":
    unittest.main()
