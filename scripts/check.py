#!/usr/bin/env python3
"""The merge-request gate for this repository — the mechanical half of AGENTS.md §4.

Checks what a reviewer should never have to read for:
  - every command has frontmatter with `description`;
  - every skill has frontmatter with `name` and `description`;
  - every `${CLAUDE_PLUGIN_ROOT}/…` path and every relative Markdown link resolves;
  - marketplace.json lists every plugin under plugins/, sources exist, names match plugin.json;
  - every CHANGES.md entry is `## YYYY-MM-DD · <id>` with a unique id and What / Check / Applies to;
  - every plugin hook points at a script that exists, in its `command` or its `args`;
  - every Python script compiles;
  - every plugin text — a `*.md` under plugins/ but a README — is at most 10 KB, or a warning says
    so: splitting it is a decision, not drift;
  - every plugin.json has a MAJOR.MINOR.PATCH `version` and the catalogue has none; a plugin whose
    files differ from the merge base with --base, its README aside, has a version above the one at
    --base's tip, and one whose CHANGES.md gains an entry is raised by a minor at least;
  - no commit since the merge base with --base, and under GitHub Actions no pull-request body,
    carries agent attribution — a co-author trailer naming Claude or a "Generated with Claude Code" line.

The sections are the agent-tools gate's, kept in pairs; that one differs in three: no plugin there
keeps a CHANGES.md, so it has no section for one; it requires `argument-hint` on commands; it checks
agents, which no plugin here ships.

Standard library and git only, so CI needs nothing but a Python image. Exit code 1 on any finding;
a size warning alone leaves it 0, and under GitHub Actions it also becomes an annotation on the file.
Run: git fetch origin main && python3 scripts/check.py [--base <ref>]   (default origin/main)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
problems = []
warnings = []

parser = argparse.ArgumentParser(description="The merge-request gate; see the module docstring.")
parser.add_argument("--base", default="origin/main", help="the ref versions are raised against (default origin/main)")
args = parser.parse_args()


def fail(path, message):
    problems.append(f"{path.relative_to(ROOT)}: {message}")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    return {k.strip(): v.strip() for k, v in
            (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line and not line.startswith(" "))}


def prose(text):
    """Markdown with code removed: a path inside backticks or a fence is an example, not a link."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


# ---------------------------------------------------------------- frontmatter
for cmd in PLUGINS.glob("*/commands/*.md"):
    fm = frontmatter(cmd)
    if fm is None or not fm.get("description"):
        fail(cmd, "command without a `description` in frontmatter")

for skill in PLUGINS.glob("*/skills/*/SKILL.md"):
    fm = frontmatter(skill)
    for key in ("name", "description"):
        if fm is None or not fm.get(key):
            fail(skill, f"skill without `{key}` in frontmatter")

# ---------------------------------------------------------------- references
for md in list(PLUGINS.rglob("*.md")) + [ROOT / "README.md", ROOT / "AGENTS.md"]:
    raw = md.read_text(encoding="utf-8")
    plugin = next((p for p in md.parents if p.parent == PLUGINS), None)
    # Plugin-root paths are checked even inside code: that is where commands write them.
    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", raw):
        if plugin is None:
            continue
        if not (plugin / ref.rstrip(".")).exists():
            fail(md, f"${{CLAUDE_PLUGIN_ROOT}}/{ref} does not exist in {plugin.name}")
    for target in re.findall(r"\]\(([^)\s]+)\)", prose(raw)):
        # A URL, an anchor or a placeholder in an example — `[MR !1](…)` — is not a file link.
        if re.match(r"[a-z]+:|#", target) or not re.search(r"[A-Za-z0-9]", target):
            continue
        if not (md.parent / target.split("#")[0]).exists():
            fail(md, f"link to {target} does not resolve")

# ---------------------------------------------------------------- catalogue
catalogue = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
listed = {}
for entry in catalogue.get("plugins", []):
    source = (ROOT / entry["source"]).resolve()
    listed[source] = entry["name"]
    manifest = source / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        fail(ROOT / ".claude-plugin" / "marketplace.json", f"{entry['name']}: no plugin.json at {entry['source']}")
        continue
    name = json.loads(manifest.read_text(encoding="utf-8")).get("name")
    if name != entry["name"]:
        fail(manifest, f"name {name!r} differs from the catalogue entry {entry['name']!r}")
for plugin_dir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
    if plugin_dir.resolve() not in listed:
        fail(plugin_dir, "plugin not listed in marketplace.json")

# ---------------------------------------------------------------- harness changes
# A project's baseline names an entry; the audit and the SessionStart hook read
# them by id. A malformed or duplicated entry breaks both silently.
for changes in PLUGINS.glob("*/CHANGES.md"):
    text = changes.read_text(encoding="utf-8")
    seen = set()
    for match in re.finditer(r"^## (.*)$", text, re.M):
        head = re.fullmatch(r"(\d{4}-\d{2}-\d{2}) · ([a-z0-9][a-z0-9-]*)", match.group(1).strip())
        if head is None:
            fail(changes, f"entry heading {match.group(1)!r} is not `YYYY-MM-DD · <id>`")
            continue
        entry_id = head.group(2)
        if entry_id in seen:
            fail(changes, f"entry id {entry_id!r} is used twice")
        seen.add(entry_id)
        body = text[match.end():].split("\n## ", 1)[0]
        for field in ("What:", "Check:", "Applies to:"):
            if not re.search(rf"^{field}\s*\S", body, re.M):
                fail(changes, f"entry {entry_id!r} has no `{field}`")

# ---------------------------------------------------------------- plugin hooks
for hooks in PLUGINS.glob("*/hooks/hooks.json"):
    plugin = hooks.parent.parent
    try:
        config = json.loads(hooks.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(hooks, f"does not parse: {e}")
        continue
    for groups in config.get("hooks", {}).values():
        for group in groups:
            for hook in group.get("hooks", []):
                for part in [hook.get("command", ""), *hook.get("args", [])]:
                    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", part):
                        if not (plugin / ref).exists():
                            fail(hooks, f"${{CLAUDE_PLUGIN_ROOT}}/{ref} does not exist in {plugin.name}")

# ---------------------------------------------------------------- scripts
for script in list(ROOT.rglob("*.py")):
    if "__pycache__" in script.parts:
        continue
    try:
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
    except SyntaxError as e:
        fail(script, f"does not compile: line {e.lineno}: {e.msg}")

# ---------------------------------------------------------------- size
# Every byte of a command, skill or reference is paid for on each turn after the
# agent reads it; growth past the limit should be a decision, so it is named.
SIZE_LIMIT = 10 * 1024
for md in sorted(PLUGINS.rglob("*.md")):
    size = md.stat().st_size
    if md.name != "README.md" and size > SIZE_LIMIT:
        warnings.append((md.relative_to(ROOT), f"{size / 1024:.1f} KB, above {SIZE_LIMIT // 1024} KB"))

# ---------------------------------------------------------------- versions
# Claude Code replaces an installed plugin only when its version changes: a
# change without a raise reaches nobody, and nothing else would say so.
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")
ENTRY_ID = re.compile(r"^## \S+ · (\S+)", re.M)


def git(*argv):
    return subprocess.run(["git", "-C", str(ROOT), *argv], capture_output=True, text=True)


def semver(value):
    m = SEMVER.fullmatch(value) if isinstance(value, str) else None
    return tuple(int(n) for n in m.groups()) if m else None


def shown(version):
    return ".".join(map(str, version))


for entry in catalogue.get("plugins", []):
    if "version" in entry:
        fail(ROOT / ".claude-plugin" / "marketplace.json",
             f"{entry['name']}: a `version` in the catalogue — it belongs in plugin.json alone")

versions = {}
for manifest in sorted(PLUGINS.glob("*/.claude-plugin/plugin.json")):
    version = semver(json.loads(manifest.read_text(encoding="utf-8")).get("version"))
    if version is None:
        fail(manifest, "no `version` of the form MAJOR.MINOR.PATCH")
    else:
        versions[manifest.parent.parent.name] = version

if git("rev-parse", "--verify", "--quiet", f"{args.base}^{{commit}}").returncode != 0:
    # A skipped comparison would pass the very change this section exists to stop.
    problems.append(f"versions: base {args.base} not found — git fetch origin main, or pass --base")
else:
    fork = git("merge-base", args.base, "HEAD").stdout.strip()
    changed = git("diff", "--name-only", fork, "--", "plugins/").stdout.splitlines()
    touched = {Path(p).parts[1] for p in changed
               if not (len(Path(p).parts) == 3 and Path(p).name == "README.md")}
    for plugin in sorted(touched & versions.keys()):
        before = git("show", f"{args.base}:plugins/{plugin}/.claude-plugin/plugin.json")
        if before.returncode != 0:
            continue  # new in this change: any version will do
        try:
            base_version = semver(json.loads(before.stdout).get("version")) or (0, 0, 0)
        except json.JSONDecodeError:
            base_version = (0, 0, 0)
        manifest = PLUGINS / plugin / ".claude-plugin" / "plugin.json"
        if versions[plugin] <= base_version:
            fail(manifest, f"{plugin} changed since {args.base}, but its version {shown(versions[plugin])} "
                           f"is not above {shown(base_version)} there")
            continue
        changes = PLUGINS / plugin / "CHANGES.md"
        if not changes.exists():
            continue
        old_ids = set(ENTRY_ID.findall(git("show", f"{args.base}:plugins/{plugin}/CHANGES.md").stdout))
        new_ids = [i for i in ENTRY_ID.findall(changes.read_text(encoding="utf-8")) if i not in old_ids]
        if new_ids and versions[plugin][:2] <= base_version[:2]:
            fail(manifest, f"CHANGES.md gains {', '.join(new_ids)}: raise {plugin} by a minor at least, "
                           f"not {shown(base_version)} → {shown(versions[plugin])}")

# AGENTS.md §3: no agent attribution. Claude Code adds a co-author trailer and a
# "Generated with" line unless its `attribution` setting says otherwise, and a
# commit that reaches main with the trailer lists the agent among the
# repository's contributors for good — a released tag keeps it reachable.
ATTRIBUTION = re.compile(r"^co-authored-by:.*\b(claude|anthropic)\b|generated with \[?claude code", re.I | re.M)

if git("rev-parse", "--verify", "--quiet", f"{args.base}^{{commit}}").returncode == 0:
    fork = git("merge-base", args.base, "HEAD").stdout.strip()
    for record in git("log", "--format=%h%x00%B%x01", f"{fork}..HEAD").stdout.split("\x01"):
        sha, _, message = record.strip().partition("\x00")
        if sha and ATTRIBUTION.search(message):
            problems.append(f"commit {sha}: agent attribution in the message — drop the line, AGENTS.md §3")
event = os.environ.get("GITHUB_EVENT_PATH")
if event and Path(event).is_file():
    pull = json.loads(Path(event).read_text(encoding="utf-8")).get("pull_request") or {}
    if ATTRIBUTION.search(pull.get("body") or ""):
        problems.append("pull request body: agent attribution — drop the line, AGENTS.md §3")

for path, message in warnings:
    print(f"warning: {path}: {message}")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning file={path}::{message}")
tail = f", {len(warnings)} warning(s)" if warnings else ""
if problems:
    print("\n".join(problems))
    print(f"\n{len(problems)} problem(s){tail}")
    sys.exit(1)
print(f"all checks passed{tail}")
