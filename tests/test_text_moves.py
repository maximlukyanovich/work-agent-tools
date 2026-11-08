"""text_moves.py: what a branch removed from plugin texts and its tree lost, on a scratch repository."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "text_moves.py"

KEPT = "A plugin text holds only the rules that outlive the project."
MOVED = "Every finding names its file and line, so the fix starts where the problem is."
TO_AGENTS = "Nothing is pushed without an explicit instruction on the current turn."
DROPPED = "The ledger is read before the pass and written after it, never in between."
REWORDED = "The review stops at the first blocker and prints the block for a fresh session."
IN_DELETED = "A deleted reference file takes its last sentence with it into the void."


def run(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class TextMovesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run(self.repo, "git", "init", "-q", "-b", "main")
        for key, value in (("user.name", "T"), ("user.email", "t@example.com"), ("commit.gpgsign", "false"),
                           ("core.quotePath", "true")):
            run(self.repo, "git", "config", key, value)
        self.write("plugins/p/commands/review.md",
                   f"---\ndescription: Review the branch\n---\n\n# Review\n\n{KEPT} {MOVED}\n"
                   f"{TO_AGENTS}\n\n- {DROPPED}\n- {REWORDED}\n")
        self.write("plugins/p/reference/old.md", f"> {IN_DELETED}\n")
        self.commit("base")
        run(self.repo, "git", "switch", "-q", "-c", "feat/move")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self, message):
        run(self.repo, "git", "add", "-A")
        run(self.repo, "git", "commit", "-q", "-m", message)

    def check(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--base", "main", *args],
                              cwd=self.repo, capture_output=True, text=True)

    def test_reports_only_what_the_tree_lost(self):
        # KEPT stays, rewrapped and in bold; MOVED goes to another plugin text with a link around a
        # word; TO_AGENTS leaves the plugins for AGENTS.md; DROPPED goes; REWORDED is rewritten;
        # old.md is deleted.
        self.write("plugins/p/commands/review.md",
                   "---\ndescription: Review the branch\n---\n\n# Review\n\n"
                   "A plugin text holds **only the rules**\nthat outlive the project.\n\n"
                   "- The review stops at the first blocker and hands a fresh session its block.\n")
        self.write("plugins/p/reference/findings.md",
                   "Every finding names its [file](x.md) and line, so the fix starts where the problem is.\n")
        self.write("AGENTS.md", f"## Rules\n\n- {TO_AGENTS}\n")
        (self.repo / "plugins/p/reference/old.md").unlink()
        self.commit("move")

        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertIn("5 sentence(s) left their plugin text, 2 found elsewhere, 3 not found.", lines[0])
        reported = "\n".join(lines[1:])
        self.assertIn("plugins/p/commands/review.md:10  " + DROPPED.lower().rstrip("."), reported)
        self.assertIn("plugins/p/reference/old.md:1  " + IN_DELETED.lower().rstrip("."), reported)
        self.assertIn("plugins/p/commands/review.md:11  " + REWORDED.lower().rstrip("."), reported)
        self.assertRegex(reported, r"≈ 0\.\d\d plugins/p/commands/review.md  the review stops at the first blocker")
        for found in (KEPT, MOVED, TO_AGENTS):
            self.assertNotIn(found.lower()[:30], reported)

    def test_a_line_in_a_fence_is_its_own_unit(self):
        run(self.repo, "git", "switch", "-q", "main")
        self.write("plugins/p/commands/tag.md",
                   "```bash\ngit tag -a <tag> -m <tag> <merge>\ngit push origin <tag> --follow-tags\n```\n")
        self.commit("fence")
        run(self.repo, "git", "switch", "-q", "-c", "feat/drop-fence")
        self.write("plugins/p/commands/tag.md", "```bash\ngit tag -a <tag> -m <tag> <merge>\n```\n")
        self.commit("drop a line")

        result = self.check()
        self.assertIn("1 sentence(s) left their plugin text, 0 found elsewhere, 1 not found.", result.stdout)
        self.assertIn("plugins/p/commands/tag.md:3  git push origin <tag> --follow-tags", result.stdout)

    def test_nothing_changed_reports_nothing(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 sentence(s) left their plugin text, 0 found elsewhere, 0 not found.", result.stdout)
        self.assertEqual(len(result.stdout.splitlines()), 1)

    def test_a_sentence_a_longer_one_holds_is_not_found(self):
        # The rule survives as a substring, weakened by the clause after it.
        self.write("plugins/p/commands/review.md",
                   f"{KEPT} {MOVED}\n"
                   "Nothing is pushed without an explicit instruction on the current turn, "
                   "unless the owner said so earlier.\n\n"
                   f"- {DROPPED}\n- {REWORDED}\n")
        self.commit("weaken")

        result = self.check()
        self.assertIn("1 sentence(s) left their plugin text, 0 found elsewhere, 1 not found.", result.stdout)
        self.assertIn("review.md:8  " + TO_AGENTS.lower().rstrip("."), result.stdout)
        self.assertRegex(result.stdout, r"≈ 0\.\d\d plugins/p/commands/review.md  nothing is pushed .* unless")

    def test_a_path_git_would_quote_is_read(self):
        run(self.repo, "git", "switch", "-q", "main")
        self.write("plugins/p/reference/größe.md", "A file with an umlaut in its name is read like any other.\n")
        self.commit("non-ASCII name")
        run(self.repo, "git", "switch", "-q", "-c", "feat/drop-umlaut")
        (self.repo / "plugins/p/reference/größe.md").unlink()
        self.commit("drop it")

        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("plugins/p/reference/größe.md:1  a file with an umlaut in its name is read like any other",
                      result.stdout)

    def test_a_missing_ref_stops(self):
        result = self.check("--head", "no-such-branch")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no such ref: no-such-branch", result.stderr)


if __name__ == "__main__":
    unittest.main()
