"""The wait blocks of `reference/templates/merge.md`, run against stubs.

A project copies these blocks into its merge command, and a wrong one reports
a pipeline green that is not. So the test takes them from the template itself
and runs them, with `glab` and `gh` replaced by scripted answers.
"""

import json
import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

TEMPLATE = Path(
    os.environ.get(
        "CI_WAIT_TEMPLATE",
        Path(__file__).resolve().parent.parent
        / "plugins/work-bootstrap/reference/templates/merge.md",
    )
)

SHA = "a" * 40
OLD_SHA = "b" * 40

STUB = """#!/bin/bash
n=$(cat "$STUB_DIR/reads")
echo $((n + 1)) > "$STUB_DIR/reads"
last=$(cat "$STUB_DIR/last")
[ "$n" -gt "$last" ] && n=$last
cat "$STUB_DIR/$n.out"
cat "$STUB_DIR/$n.err" >&2
exit "$(cat "$STUB_DIR/$n.code")"
"""


def blocks():
    section = TEMPLATE.read_text().split("### Waiting for CI", 1)[1].split("\n### ", 1)[0]
    return re.findall(r"```bash\n(.*?)```", section, re.S)


def run(block, tool, answers, limit=5):
    """Runs a block; `answers` are (stdout, stderr, exit code), the last repeating."""
    with tempfile.TemporaryDirectory() as folder:
        stub_dir = Path(folder)
        stub = stub_dir / tool
        stub.write_text(STUB)
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        (stub_dir / "reads").write_text("0")
        (stub_dir / "last").write_text(str(len(answers) - 1))
        for index, (out, err, code) in enumerate(answers):
            (stub_dir / f"{index}.out").write_text(out)
            (stub_dir / f"{index}.err").write_text(err)
            (stub_dir / f"{index}.code").write_text(str(code))
        env = {
            **os.environ,
            "PATH": f"{stub_dir}:{os.environ['PATH']}",
            "STUB_DIR": str(stub_dir),
            "MR": "7",
            "PR": "7",
            "SHA": SHA,
            "LIMIT": str(limit),
            "POLL": "0.01",
        }
        result = subprocess.run(
            ["bash", "-c", block], env=env, capture_output=True, text=True, timeout=30
        )
        return result, int((stub_dir / "reads").read_text())


def mr(status=None, source="merge_request_event", sha=SHA):
    pipeline = None if status is None else {"status": status, "source": source, "sha": sha}
    return json.dumps({"head_pipeline": pipeline}), "", 0


def checks(*buckets):
    return json.dumps([{"name": f"c{i}", "bucket": b} for i, b in enumerate(buckets)]), "", 0


NO_CHECKS = ("", "no checks reported on the 'x' branch\n", 1)


class GitLab(unittest.TestCase):
    def setUp(self):
        self.block = blocks()[0]
        self.assertIn("glab mr view", self.block)

    def wait(self, *answers, limit=5):
        return run(self.block, "glab", list(answers), limit)

    def assert_waits_then_green(self, first):
        result, reads = self.wait(first, mr("success"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 2)

    def test_success_of_the_pushed_head_is_green(self):
        result, reads = self.wait(mr("success"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 1)

    def test_no_pipeline_yet_keeps_waiting(self):
        self.assert_waits_then_green(mr())

    def test_a_green_branch_pipeline_keeps_waiting(self):
        self.assert_waits_then_green(mr("success", source="push"))

    def test_the_last_heads_pipeline_keeps_waiting(self):
        self.assert_waits_then_green(mr("success", sha=OLD_SHA))

    def test_a_red_pipeline_of_another_head_keeps_waiting(self):
        self.assert_waits_then_green(mr("failed", sha=OLD_SHA))

    def test_unfinished_statuses_keep_waiting(self):
        for status in (
            "created",
            "waiting_for_resource",
            "preparing",
            "waiting_for_callback",
            "pending",
            "running",
            "canceling",
            "scheduled",
        ):
            with self.subTest(status):
                self.assert_waits_then_green(mr(status))

    def test_a_status_that_is_not_green_stops_and_is_named(self):
        for status in ("failed", "canceled", "manual", "skipped"):
            with self.subTest(status):
                result, reads = self.wait(mr(status), mr("success"))
                self.assertEqual((result.stdout.strip(), result.returncode), (status, 1))
                self.assertEqual(reads, 1)

    def test_an_error_ends_the_wait_and_stays_visible(self):
        result, reads = self.wait(("", "glab: 502\n", 1), mr("success"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("status not read", 1))
        self.assertIn("glab: 502", result.stderr)
        self.assertEqual(reads, 1)

    def test_an_answer_that_is_not_json_is_not_read(self):
        result, _ = self.wait(("<html>", "", 0))
        self.assertEqual((result.stdout.strip(), result.returncode), ("status not read", 1))

    def test_a_limit_that_runs_out_is_no_result(self):
        result, _ = self.wait(mr("success", source="push"), limit=1)
        self.assertEqual((result.stdout.strip(), result.returncode), ("no result", 1))


class GitHub(unittest.TestCase):
    def setUp(self):
        self.block = blocks()[1]
        self.assertIn("gh pr checks", self.block)

    def wait(self, *answers, limit=5):
        return run(self.block, "gh", list(answers), limit)

    def test_passed_and_skipped_checks_are_green(self):
        result, reads = self.wait(checks("pass", "skipping"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 1)

    def test_no_checks_yet_keeps_waiting(self):
        result, reads = self.wait(NO_CHECKS, checks("pass"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 2)

    def test_an_empty_list_is_not_green(self):
        result, reads = self.wait(checks(), checks("pass"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 2)

    def test_a_pending_check_keeps_waiting(self):
        result, reads = self.wait(checks("pass", "pending"), checks("pass", "pass"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("success", 0))
        self.assertEqual(reads, 2)

    def test_a_failed_check_stops_at_once(self):
        result, reads = self.wait(checks("fail", "pending"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("failed", 1))
        self.assertEqual(reads, 1)

    def test_a_canceled_check_is_not_green(self):
        result, _ = self.wait(checks("pass", "cancel"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("canceled", 1))

    def test_an_error_ends_the_wait_and_stays_visible(self):
        result, reads = self.wait(("", "HTTP 502\n", 1), checks("pass"))
        self.assertEqual((result.stdout.strip(), result.returncode), ("status not read", 1))
        self.assertIn("HTTP 502", result.stderr)
        self.assertEqual(reads, 1)

    def test_a_limit_that_runs_out_is_no_result(self):
        result, _ = self.wait(checks("pending"), limit=1)
        self.assertEqual((result.stdout.strip(), result.returncode), ("no result", 1))


if __name__ == "__main__":
    unittest.main()
