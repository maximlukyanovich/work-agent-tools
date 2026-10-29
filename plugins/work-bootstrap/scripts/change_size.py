#!/usr/bin/env python3
"""Measure a branch's change against the thresholds of a small change.

Usage: change_size.py [<target>] [--base <branch>] [--max-lines 100]
                      [--max-files 5] [--max-prose-lines 300]

The target is a worktree directory or a branch name; none means the current
directory. The diff runs from the merge-base with `origin/<base>` (or the
local `<base>` when the remote has none) to the target's head. One line out:

    size: small · files 1 · +29 −2 · prose-only yes · uncommitted no

followed by ` — <reason>` when the size is normal. Exit 2 when the target or
the base cannot be resolved. The format is documented in
`reference/change-size.md`; the risk class is the agent's to judge, not this
script's.
"""

import argparse
import os
import subprocess
import sys

PROSE_DIRS = ("docs/",)
PROSE_SUFFIXES = (".md",)


class Failure(Exception):
    pass


def git(cwd, *args):
    done = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise Failure(done.stderr.strip() or f"git {' '.join(args)} failed")
    return done.stdout


def resolve_target(target):
    """Return (directory to run git in, ref of the head, whether it has a tree)."""
    if target is None:
        return ".", "HEAD", True
    if os.path.isdir(target):
        return target, "HEAD", True
    try:
        git(".", "rev-parse", "--verify", "--quiet", f"{target}^{{commit}}")
    except Failure:
        raise Failure(f"not a directory or a branch: {target}")
    branch_ref = f"refs/heads/{target}"
    for block in git(".", "worktree", "list", "--porcelain").split("\n\n"):
        lines = block.splitlines()
        if f"branch {branch_ref}" in lines:
            return lines[0].removeprefix("worktree "), "HEAD", True
    return ".", target, False


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


def numstat(cwd, start, head):
    """Yield (added, deleted, path) per file; a binary file counts 0 lines."""
    out = git(cwd, "diff", "--numstat", "-z", "-M", start, head)
    fields = out.split("\0")
    i = 0
    while i < len(fields) and fields[i]:
        added, deleted, path = fields[i].split("\t", 2)
        if path == "":  # a rename: the old and the new path follow
            path = fields[i + 2]
            i += 3
        else:
            i += 1
        lines = (0, 0) if added == "-" else (int(added), int(deleted))
        yield lines[0], lines[1], path


def is_prose(path):
    return path.endswith(PROSE_SUFFIXES) or path.startswith(PROSE_DIRS)


def measure(cwd, head, has_tree, base, max_lines, max_files, max_prose_lines):
    start = git(cwd, "merge-base", base_ref(cwd, base), head).strip()
    files = list(numstat(cwd, start, head))
    added = sum(f[0] for f in files)
    deleted = sum(f[1] for f in files)
    prose_only = bool(files) and all(is_prose(f[2]) for f in files)
    uncommitted = has_tree and git(cwd, "status", "--porcelain").strip() != ""
    line_limit, line_label = (max_prose_lines, "prose lines") if prose_only else (max_lines, "lines")
    reasons = []
    if len(files) > max_files:
        reasons.append(f"files {len(files)} > {max_files}")
    if added + deleted > line_limit:
        reasons.append(f"{line_label} {added + deleted} > {line_limit}")
    line = (
        f"size: {'normal' if reasons else 'small'} · files {len(files)} · +{added} −{deleted}"
        f" · prose-only {'yes' if prose_only else 'no'} · uncommitted {'yes' if uncommitted else 'no'}"
    )
    return line + (f" — {', '.join(reasons)}" if reasons else "")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure a change against the small-change thresholds.")
    parser.add_argument("target", nargs="?")
    parser.add_argument("--base")
    parser.add_argument("--max-lines", type=int, default=100)
    parser.add_argument("--max-files", type=int, default=5)
    parser.add_argument("--max-prose-lines", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        cwd, head, has_tree = resolve_target(args.target)
        base = args.base or default_base(cwd)
        print(measure(cwd, head, has_tree, base, args.max_lines, args.max_files, args.max_prose_lines))
    except Failure as error:
        print(f"change_size: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
