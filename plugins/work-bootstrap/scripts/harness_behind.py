#!/usr/bin/env python3
"""SessionStart: tell the developer when the project's harness is behind this plugin.

Reads the baseline from `.claude/project-profile.md` (section `## Harness`, line
`Baseline: <id>`) and the entries of this plugin's CHANGES.md. Behind → one
`systemMessage`, shown to the developer and never added to the model's context.
Anything else — no profile, no section, up to date, a file it cannot read — is
silence and exit 0: this hook must never get in a session's way.
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
    if current is None:
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
