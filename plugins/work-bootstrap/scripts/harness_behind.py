#!/usr/bin/env python3
"""SessionStart: tell the developer when the project's harness is behind this plugin.

Reads the baseline from `.claude/project-profile.md` (section `## Harness`, line
`Baseline: <id>`) and the entries of this plugin's CHANGES.md. One `systemMessage`
— shown to the developer, never added to the model's context — when:

- the profile exists but has no baseline: a project set up before this
  mechanism, which needs one full audit to get on it;
- the baseline is older than the last entry, or unknown to the installed plugin.

Silence and exit 0 otherwise — no profile (not a project these tools set up),
`Baseline: off` (the project opted out), up to date, or a file it cannot read:
this hook must never get in a session's way.
"""

import json
import os
import re
import sys
from pathlib import Path

ENTRY = re.compile(r"^## \d{4}-\d{2}-\d{2} · (\S+)\s*$", re.M)
BASELINE = re.compile(r"^Baseline:\s*`?([^\s`]+)", re.M)


def baseline(profile: Path):
    text = profile.read_text(encoding="utf-8")
    section = re.search(r"^## Harness\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if section is None:
        return None
    match = BASELINE.search(section.group(1))
    return match.group(1) if match else None


def main() -> None:
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    plugin = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
    profile = project / ".claude" / "project-profile.md"
    if not profile.is_file():
        return
    current = baseline(profile)
    if current == "off":
        return
    if current is None:
        print(json.dumps({"systemMessage": (
            "This project's harness has no work-bootstrap baseline — run "
            "/work-bootstrap:audit full once to get method updates.")}))
        return
    ids = ENTRY.findall((plugin / "CHANGES.md").read_text(encoding="utf-8"))
    if not ids or current == ids[-1]:
        return
    if current not in ids:
        message = (f"Harness baseline '{current}' is not in the installed work-bootstrap — "
                   "update the plugin (claude plugin update).")
    else:
        newer = len(ids) - ids.index(current) - 1
        message = (f"Harness baseline '{current}': {newer} newer work-bootstrap "
                   f"change{'s' if newer != 1 else ''} — run /work-bootstrap:audit.")
    print(json.dumps({"systemMessage": message}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 — a reminder is never worth a broken session
        pass
    sys.exit(0)
