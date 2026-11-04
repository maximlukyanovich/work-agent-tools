#!/usr/bin/env python3
"""Record green gate runs and say whether a branch still needs the full gate.

Template: work-bootstrap gate-record v1 — copied by /work-bootstrap:setup into
the project's scripts folder; /work-bootstrap:audit compares the copy with the
template. Python 3.9+, standard library only.

    python3 scripts/gate_record.py record full|targeted [<target>] [--commits <n>]
    python3 scripts/gate_record.py check [<target>] [--base <branch>] [--small]

The target is a worktree directory or a branch checked out in one; none means
the current directory. `record` appends the head's tree to `gate-record` in
that tree's git directory, only when the tree is clean; `--commits`, with
`targeted`, appends the last n first-parent commits. `check` prints one line:
    gate: skip · full green at 1a2b3c4 · targeted since: 2
    gate: run — 5d6e7f8 has no green record
The format is documented in the plugin's `reference/gate-record.md`; which run counts as
`targeted` is the agent's to judge, not this script's.
"""

import argparse
import os
import subprocess
import sys

RECORD = "gate-record"
KINDS = ("full", "targeted")


class Failure(Exception):
    pass


def git(cwd, *args):
    done = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Failure(done.stderr.strip() or f"git {' '.join(args)} failed")
    return done.stdout


def resolve_tree(target):
    """Return the directory of the worktree the target names."""
    if target is None:
        return "."
    if os.path.isdir(target):
        return target
    try:
        git(".", "rev-parse", "--verify", "--quiet", f"{target}^{{commit}}")
    except Failure:
        raise Failure(f"not a directory or a branch: {target}")
    branch_ref = f"refs/heads/{target}"
    for block in git(".", "worktree", "list", "--porcelain").split("\n\n"):
        lines = block.splitlines()
        if f"branch {branch_ref}" in lines:
            return lines[0].removeprefix("worktree ")
    raise Failure(f"branch checked out nowhere, no tree for the gate: {target}")


def record_path(cwd):
    return os.path.join(git(cwd, "rev-parse", "--absolute-git-dir").strip(), RECORD)


def read_record(cwd):
    """Map each recorded tree to the strongest kind recorded for it."""
    trees = {}
    try:
        with open(record_path(cwd)) as f:
            for line in f:
                kind, _, tree = line.strip().partition(" ")
                if kind in KINDS and tree and trees.get(tree) != "full":
                    trees[tree] = kind
    except FileNotFoundError:
        pass
    return trees


def is_clean(cwd):
    return git(cwd, "status", "--porcelain").strip() == ""


def tree_of(cwd, rev):
    return git(cwd, "rev-parse", f"{rev}^{{tree}}").strip()


def record(cwd, kind, commits):
    if commits < 1 or (kind == "full" and commits > 1):
        raise Failure("--commits takes a number from 1, above 1 with targeted only")
    if not is_clean(cwd):
        return "gate: not recorded — the tree has uncommitted changes"
    revs = git(cwd, "rev-list", "--first-parent", "-n", str(commits), "HEAD").split()
    trees = [tree_of(cwd, rev) for rev in revs]
    with open(record_path(cwd), "a") as f:
        f.writelines(f"{kind} {tree}\n" for tree in trees)
    return f"gate: recorded {kind} {trees[0][:7]}" + (f" · {len(trees)} commits" if len(trees) > 1 else "")


def default_base(cwd):
    try:
        ref = git(cwd, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD").strip()
    except Failure:
        raise Failure("no origin/HEAD to take the base from; pass --base")
    return ref.removeprefix("refs/remotes/origin/")


def base_ref(cwd, base):
    for ref in (f"origin/{base}", base):
        try:
            git(cwd, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            return ref
        except Failure:
            continue
    raise Failure(f"base not found: origin/{base} or {base}")


def check(cwd, base, small):
    if not is_clean(cwd):
        return "gate: run — the tree has uncommitted changes"
    trees = read_record(cwd)
    if trees.get(tree_of(cwd, "HEAD")) == "full":
        return "gate: skip · full green on this tree"
    ref = base_ref(cwd, base)
    start = git(cwd, "merge-base", ref, "HEAD").strip()
    commits = git(cwd, "rev-list", "--first-parent", f"{start}..HEAD").split()
    if not commits:
        return f"gate: run — no commits ahead of {ref}"
    for since, commit in enumerate(commits):
        kind = trees.get(tree_of(cwd, commit))
        if kind is None:
            return f"gate: run — {commit[:7]} has no green record"
        if kind == "full":
            return f"gate: skip · full green at {commit[:7]} · targeted since: {since}"
    if small:
        return f"gate: skip · small · targeted on all {len(commits)}"
    return f"gate: run — no full green run since {ref}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Record green gate runs; say whether the full gate is due.")
    sub = parser.add_subparsers(dest="action", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("kind", choices=KINDS)
    rec.add_argument("target", nargs="?")
    rec.add_argument("--commits", type=int, default=1)
    chk = sub.add_parser("check")
    chk.add_argument("target", nargs="?")
    chk.add_argument("--base")
    chk.add_argument("--small", action="store_true")
    args = parser.parse_args(argv)
    try:
        cwd = resolve_tree(args.target)
        if args.action == "record":
            print(record(cwd, args.kind, args.commits))
        else:
            print(check(cwd, args.base or default_base(cwd), args.small))
    except Failure as error:
        print(f"gate_record: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
