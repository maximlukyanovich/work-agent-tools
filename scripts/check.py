#!/usr/bin/env python3
"""The merge-request gate for this repository — the mechanical half of AGENTS.md §4.

Checks what a reviewer should never have to read for:
  - every command has frontmatter with `description`;
  - every skill has frontmatter with `name` and `description`;
  - every `${CLAUDE_PLUGIN_ROOT}/…` path and every relative Markdown link resolves;
  - marketplace.json lists every plugin under plugins/, sources exist, names match plugin.json;
  - every Python script compiles.

Standard library only, so CI needs nothing but a Python image. Exit code 1 on any finding.
Run: python3 scripts/check.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
problems = []


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

# ---------------------------------------------------------------- scripts
for script in list(ROOT.rglob("*.py")):
    if "__pycache__" in script.parts:
        continue
    try:
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
    except SyntaxError as e:
        fail(script, f"does not compile: line {e.lineno}: {e.msg}")

if problems:
    print("\n".join(problems))
    print(f"\n{len(problems)} problem(s)")
    sys.exit(1)
print("all checks passed")
