#!/usr/bin/env python3
"""The target of a review pass, from the pass ledger, HEAD and the arguments.

Template: work-bootstrap review-target v1 — copied by /work-bootstrap:setup into
the project's scripts folder; /work-bootstrap:audit compares the copy with the
template. Python 3.8+, standard library only.

    python3 scripts/review_target.py --ledger <file> [--tree <dir>] [--head <rev>]
                                     [--full] [--range <a>..<b>]

One line on stdout, exit 0:

    target: none · head 9f8e7d6 — the ledger's last head is HEAD
    target: delta · git diff e4f5a6b..9f8e7d6 — the last head is an ancestor of HEAD
    target: rewritten · git diff e4f5a6b 9f8e7d6 · replaced a1b2c3d e4f5a6b — the last head is not an ancestor of HEAD
    target: whole — no ledger

`whole` is the target the review command computes itself — the branch against
its base; its reasons: no ledger, the ledger has no pass, full, the last head
is not in the repository. An explicit range outranks the ledger and `full`:
`range` when its base is an ancestor of its head, `rewritten` otherwise.
Exit 2, with the reason on stderr, when the head or the range does not resolve, or the ledger
is a directory.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

PASS = re.compile(r"^## Pass \d+\b.*?\bhead ([0-9a-f]{7,40})\b", re.M)
TRAJECTORY = re.compile(r"^Trajectory:(.*)$", re.M)
TRAJECTORY_HEAD = re.compile(r"\bP\d+ ([0-9a-f]{7,40})\b")


class Unresolved(Exception):
    pass


def git(tree, *args):
    return subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True)


def commit(tree, rev):
    """The full sha of a commit, or None when the repository does not have it."""
    out = git(tree, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    return out.stdout.strip() if out.returncode == 0 else None


def short(tree, sha):
    return git(tree, "rev-parse", "--short=7", sha).stdout.strip()


def is_ancestor(tree, older, newer):
    return git(tree, "merge-base", "--is-ancestor", older, newer).returncode == 0


def last_head(ledger: Path):
    """The head of the ledger's last pass: its last pass header, else its trajectory."""
    text = ledger.read_text(encoding="utf-8")
    heads = PASS.findall(text)
    if heads:
        return heads[-1]
    trajectory = TRAJECTORY.findall(text)
    heads = TRAJECTORY_HEAD.findall(trajectory[-1]) if trajectory else []
    return heads[-1] if heads else None


def between(tree, base, head, reason_ancestor, reason_rewritten, mode="delta"):
    if is_ancestor(tree, base, head):
        return f"target: {mode} · git diff {short(tree, base)}..{short(tree, head)} — {reason_ancestor}"
    replaced = git(tree, "rev-list", "--abbrev-commit", "--abbrev=7", "--reverse",
                   f"{head}..{base}").stdout.split()
    named = f" · replaced {' '.join(replaced)}" if replaced else ""
    return f"target: rewritten · git diff {short(tree, base)} {short(tree, head)}{named} — {reason_rewritten}"


def target(ledger: Path, tree: Path, head_rev="HEAD", full=False, explicit=None) -> str:
    if explicit:
        if ".." not in explicit or "..." in explicit:
            raise Unresolved(f"a range is <a>..<b>, not {explicit}")
        start, end = explicit.split("..", 1)
        base, head = commit(tree, start), commit(tree, end or "HEAD")
        if not base or not head:
            raise Unresolved(f"{explicit} does not resolve in {tree}")
        return between(tree, base, head, "explicit range",
                       "the range's base is not an ancestor of its head", mode="range")
    head = commit(tree, head_rev)
    if not head:
        raise Unresolved(f"{head_rev} does not resolve in {tree}")
    if ledger.is_dir():
        raise Unresolved(f"{ledger} is a directory; --ledger takes the ledger file")
    if full:
        return "target: whole — full"
    if not ledger.is_file():
        return "target: whole — no ledger"
    last = last_head(ledger)
    if last is None:
        return "target: whole — the ledger has no pass"
    reviewed = commit(tree, last)
    if not reviewed:
        return f"target: whole — the last head {last} is not in the repository"
    if reviewed == head:
        return f"target: none · head {short(tree, head)} — the ledger's last head is HEAD"
    return between(tree, reviewed, head, "the last head is an ancestor of HEAD",
                   "the last head is not an ancestor of HEAD")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print the target of a review pass.")
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--tree", type=Path, default=Path("."))
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--range", dest="explicit")
    args = parser.parse_args(argv)
    try:
        print(target(args.ledger, args.tree, args.head, args.full, args.explicit))
    except Unresolved as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
