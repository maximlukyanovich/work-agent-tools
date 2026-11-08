#!/usr/bin/env python3
"""Text-move check: the sentences a branch removed from plugins/**/*.md that its tree no longer holds.

A pull request that moves text — a rule split out to a reference file, a section folded into a
template — can lose a paragraph on the way, and neither the gate, the tests, the evals nor a review
of the diff compares what was removed with where it went. This script does: every sentence of a
plugin text the merge base had and the head's version of that file lacks is looked up in every
tracked *.md of the head's tree, and only those found nowhere are printed — each with the closest
sentence of a changed file when one is similar enough, so "rewritten" reads apart from "lost".

Text is compared normalised: whitespace and hard wraps collapsed, Markdown emphasis, code ticks,
link targets, list, heading and quote markers dropped, case folded. A line inside a fenced block is
a unit of its own; a unit of fewer than four words is skipped.

A warning, never a failure — removing a rule can be the point of the change — so the exit code is
0 whatever is found, and 2 only when a ref is missing. The pull request attaches the output.
Kept identical in work-agent-tools and agent-tools.

Run: git fetch origin main && python3 scripts/text_moves.py [--base <ref>] [--head <ref>]
     (default origin/main and HEAD; the old side is their merge base)
"""

import argparse
import difflib
import re
import subprocess
import sys

MIN_WORDS = 4
NEAR = 0.6

FENCE = re.compile(r"^\s*(```|~~~)")
BLOCK_START = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|\|)")
SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
MARKS = re.compile(r"\*\*|__|[*`]|(?<!\w)_|_(?!\w)")
QUOTE = re.compile(r"^\s*(>\s?)+")
LEAD = re.compile(r"^(\s*(>|#{1,6}|[-*+]|\d+[.)])\s+)+")


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True)
    if result.returncode:
        print(f"text_moves: git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}",
              file=sys.stderr)
        sys.exit(2)
    return result.stdout.decode("utf-8", errors="replace")


def normalise(text):
    text = LINK.sub(r"\1", text)
    text = LEAD.sub("", text)
    text = MARKS.sub("", text)
    return " ".join(text.lower().split())


def blocks(text):
    """(starts, raw text) per paragraph, list item, heading, table cell or fenced line; starts maps
    each joined line's offset in the raw text to its line number."""
    lines = text.splitlines()
    out, current, fenced = [], [], False
    front = len(lines) > 1 and lines[0].strip() == "---"

    def flush():
        if current:
            starts, offset = [], 0
            for number, part in current:
                starts.append((offset, number))
                offset += len(part) + 1
            out.append((starts, " ".join(part for _, part in current)))
        current.clear()

    for number, line in enumerate(lines, 1):
        if front:
            if number > 1 and line.strip() == "---":
                front = False
            elif number > 1 and line.strip():
                out.append(([(0, number)], re.sub(r"^[\w-]+:\s*", "", line)))
            continue
        if FENCE.match(line):
            flush()
            fenced = not fenced
            continue
        if fenced:
            if line.strip():
                out.append(([(0, number)], line))
            continue
        line = QUOTE.sub("", line)
        if not line.strip():
            flush()
            continue
        if BLOCK_START.match(line):
            flush()
            if line.lstrip().startswith("|"):
                out.extend(([(0, number)], cell) for cell in line.split("|") if cell.strip(" -:"))
                continue
        current.append((number, line.strip()))
    flush()
    return out


def sentences(text):
    """(line number, normalised sentence) for every unit of at least MIN_WORDS words."""
    out = []
    for starts, raw in blocks(text):
        position = 0
        for part in SENTENCE_END.split(raw):
            position = raw.find(part, position)
            number = max(n for offset, n in starts if offset <= position)
            position += len(part)
            unit = normalise(part).rstrip(".!?;:,")
            if len(unit.split()) >= MIN_WORDS:
                out.append((number, unit))
    return out


def searchable(text):
    return "\n".join(normalise(raw) for _, raw in blocks(text))


def main():
    parser = argparse.ArgumentParser(description="Text-move check; see the module docstring.")
    parser.add_argument("--base", default="origin/main", help="the ref the branch forks from (default origin/main)")
    parser.add_argument("--head", default="HEAD", help="the ref whose tree is searched (default HEAD)")
    args = parser.parse_args()

    for ref in (args.base, args.head):
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                          capture_output=True).returncode:
            print(f"text_moves: no such ref: {ref}", file=sys.stderr)
            sys.exit(2)
    old = git("merge-base", args.base, args.head).strip()

    def show(ref, path):
        return git("show", f"{ref}:{path}")

    tree = [p for p in git("ls-tree", "-r", "--name-only", args.head).splitlines() if p.endswith(".md")]
    new_text = {p: show(args.head, p) for p in tree}
    haystack = "\n".join(searchable(t) for t in new_text.values())

    changed = git("diff", "--name-status", "--no-renames", old, args.head).splitlines()
    touched = [line.split("\t", 1)[1] for line in changed]
    removed_from = [path for status, path in (line.split("\t", 1) for line in changed)
                    if status in ("M", "D") and path.startswith("plugins/") and path.endswith(".md")]
    candidates = sorted({(p, s) for p in touched if p in new_text for _, s in sentences(new_text[p])})

    removed = lost = 0
    report = []
    for path in removed_from:
        same_file = searchable(new_text.get(path, ""))
        for number, unit in sentences(show(old, path)):
            if unit in same_file:
                continue
            removed += 1
            if unit in haystack:
                continue
            lost += 1
            report.append(f"{path}:{number}  {unit}")
            best = (NEAR, None, None)
            for where, text in candidates:
                matcher = difflib.SequenceMatcher(None, unit, text, autojunk=False)
                if matcher.real_quick_ratio() >= best[0] and matcher.quick_ratio() >= best[0]:
                    ratio = matcher.ratio()
                    if ratio >= best[0]:
                        best = (ratio, where, text)
            if best[1]:
                report.append(f"    ≈ {best[0]:.2f} {best[1]}  {best[2]}")

    print(f"Text moves {old[:7]}..{args.head}: {removed} sentence(s) left their plugin text, "
          f"{removed - lost} found elsewhere, {lost} not found.")
    if report:
        print("\n".join(report))


if __name__ == "__main__":
    main()
