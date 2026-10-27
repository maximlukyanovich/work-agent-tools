#!/usr/bin/env python3
"""Release notes between two refs — the part `gh release create --generate-notes` cannot write.

Output, Markdown on stdout, prepended to the generated list of pull requests:
  ## Plugins — `Plugin | Version | Was | Change`, one row per plugin in either catalogue; Change is
     major, minor, patch, new (no version before), removed, lowered or — (unchanged);
  ## Action needed — every plugin raised by a major, every plugin removed from the catalogue, and
     every CHANGES.md entry added since <previous-tag> with the first sentence of its `What:`, under
     the audit command that applies it; "Nothing." when there is none.

Standard library and git only. Exit code 2 when a ref does not resolve.
Run: python3 scripts/release_notes.py <previous-tag> [<ref>]   (default HEAD)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")
ENTRY = re.compile(r"^## \S+ · (\S+)[ \t]*\n(.*?)(?=^## |\Z)", re.M | re.S)
WHAT = re.compile(r"^What:\s*(.*?)(?=^(?:Supersedes|Check|Applies to):|\Z)", re.M | re.S)
SENTENCE_END = re.compile(r"(?<=\.)\s+(?=[A-Z`])")


def git(*argv):
    return subprocess.run(["git", "-C", str(ROOT), *argv], capture_output=True, text=True)


def show(ref, path):
    out = git("show", f"{ref}:{path}")
    return out.stdout if out.returncode == 0 else None


def catalogue(ref):
    """{plugin: (version or None, source directory)} as the catalogue at ref lists them."""
    found = {}
    for entry in json.loads(show(ref, ".claude-plugin/marketplace.json") or "{}").get("plugins", []):
        source = entry["source"].removeprefix("./").rstrip("/")
        manifest = show(ref, f"{source}/.claude-plugin/plugin.json")
        found[entry["name"]] = (json.loads(manifest).get("version") if manifest else None, source)
    return found


def parse(version):
    m = SEMVER.fullmatch(version or "")
    return tuple(int(n) for n in m.groups()) if m else None


def change(now, was):
    n, w = parse(now), parse(was)
    if n is None or n == w:
        return "—"
    if w is None:
        return "new"
    if n < w:
        return "lowered"
    return ("major", "minor", "patch")[next(i for i in range(3) if n[i] != w[i])]


def first_sentence(body):
    what = WHAT.search(body)
    return SENTENCE_END.split(" ".join(what.group(1).split()), maxsplit=1)[0] if what else "(no What:)"


def entries(ref, source):
    return {m.group(1): m.group(2) for m in ENTRY.finditer(show(ref, f"{source}/CHANGES.md") or "")}


if len(sys.argv) not in (2, 3):
    sys.exit("usage: release_notes.py <previous-tag> [<ref>]")
previous, ref = sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else "HEAD"
for r in (previous, ref):
    if git("rev-parse", "--verify", "--quiet", f"{r}^{{commit}}").returncode != 0:
        print(f"{r} does not resolve — git fetch --tags", file=sys.stderr)
        sys.exit(2)

before, after = catalogue(previous), catalogue(ref)
rows, actions = [], []
for name, (now, source) in after.items():
    was = before.get(name, (None, None))[0]
    level = change(now, was)
    rows.append(f"| `{name}` | {now or '—'} | {was or '—'} | {level} |")
    if level == "major":
        actions.append(f"- `{name}` {was} → {now}: a major — a project must act; the pull requests below say how.")
for name, (was, _) in before.items():
    if name not in after:
        rows.append(f"| `{name}` | — | {was or '—'} | removed |")
        actions.append(f"- `{name}` is removed from the catalogue: a project that enables it drops it from its settings.")
for name, (_, source) in after.items():
    old = entries(previous, source)
    added = [(i, body) for i, body in entries(ref, source).items() if i not in old]
    if added:
        actions.append(f"- `/{name}:audit` applies these `CHANGES.md` entries in a set-up project:")
        for entry_id, body in added:
            actions.append(f"  - `{entry_id}` — {first_sentence(body)}")

print(f"## Plugins\n\nAgainst `{previous}`.\n")
print("| Plugin | Version | Was | Change |\n| --- | --- | --- | --- |")
print("\n".join(rows))
print("\n## Action needed\n")
print("\n".join(actions) if actions else "Nothing.")
