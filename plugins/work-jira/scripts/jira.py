# -*- coding: utf-8 -*-
"""A thin wrapper over Jira Cloud REST v3 that writes descriptions in native ADF.

Why not through MCP: the mcp-atlassian layer rewrites Markdown into wiki markup and loses
part of the formatting on the way — links under bold lose their target, bold inside a list
item turns into literal asterisks, and task lists do not survive at all. Here the
description is assembled directly in Atlassian Document Format, so it renders as intended.

Issue type ids come from the project's createmeta: they differ between instances.
"""

import base64
import json
import re
import urllib.error
import urllib.request
import uuid
from pathlib import Path

def _env():
    """Credentials come from the project's .mcp.json — generated from .env, gitignored.

    The root is searched upwards from the working directory, or set via JIRA_PROJECT_ROOT.
    """
    import os

    root = Path(os.environ.get("JIRA_PROJECT_ROOT", Path.cwd()))
    for candidate in [root, *root.parents]:
        cfg_path = candidate / ".mcp.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())["mcpServers"]["jira"]["env"]
            return cfg["JIRA_URL"].rstrip("/"), cfg["JIRA_USERNAME"], cfg["JIRA_API_TOKEN"]
    raise RuntimeError("no .mcp.json found - run the project's mcp:sync first")


def coordinates():
    """Instance URL and project key from the profile — they are not secrets.

    Falls back to .mcp.json when the profile has no Tracker section yet, so the very
    first run still works; the command is expected to write the section afterwards.
    """
    import os
    import re

    root = Path(os.environ.get("JIRA_PROJECT_ROOT", Path.cwd()))
    for candidate in [root, *root.parents]:
        profile = candidate / ".claude" / "project-profile.md"
        if profile.exists():
            text = profile.read_text()
            url = re.search(r"https://[\w.-]+\.atlassian\.net", text)
            key = re.search(r"[Pp]roject key\s*\|?\s*`?([A-Z][A-Z0-9]+)`?", text)
            if url and key:
                return url.group(0), key.group(1)
    return None, None


BASE, USER, TOKEN = _env()
_AUTH = base64.b64encode(f"{USER}:{TOKEN}".encode()).decode()


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Basic {_AUTH}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {method} {path}\n{e.read().decode('utf-8', 'replace')}") from None


# --------------------------------------------------------------------- ADF
_INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)")


def _text(s):
    """Parses `code` and [links](url); everything else is plain text."""
    out, pos = [], 0
    for m in _INLINE.finditer(s):
        if m.start() > pos:
            out.append({"type": "text", "text": s[pos:m.start()]})
        if m.group(1):
            out.append({"type": "text", "text": m.group(1), "marks": [{"type": "code"}]})
        else:
            out.append({"type": "text", "text": m.group(2),
                        "marks": [{"type": "link", "attrs": {"href": m.group(3)}}]})
        pos = m.end()
    if pos < len(s):
        out.append({"type": "text", "text": s[pos:]})
    return out or [{"type": "text", "text": s}]


def h(s):
    """A section heading: a wholly bold paragraph, the only form that survives every
    Jira editor."""
    return {"type": "paragraph", "content": [{"type": "text", "text": s, "marks": [{"type": "strong"}]}]}


def p(s):
    return {"type": "paragraph", "content": _text(s)}


def ul(items):
    return {"type": "bulletList", "content": [
        {"type": "listItem", "content": [{"type": "paragraph", "content": _text(i)}]} for i in items
    ]}


def checklist(items):
    return {"type": "taskList", "attrs": {"localId": str(uuid.uuid4())}, "content": [
        {"type": "taskItem", "attrs": {"localId": str(uuid.uuid4()), "state": "TODO"},
         "content": _text(i)} for i in items
    ]}


def doc(*blocks):
    return {"type": "doc", "version": 1, "content": list(blocks)}


# ------------------------------------------------------------------ issues
_TYPE_CACHE = {}


def types(project):
    """Issue type ids for one project — never hard-code them."""
    if project not in _TYPE_CACHE:
        meta = call("GET", f"/rest/api/3/issue/createmeta/{project}/issuetypes")
        _TYPE_CACHE[project] = {t["name"]: t["id"] for t in meta["issueTypes"]}
    return _TYPE_CACHE[project]


def create(project, issue_type, summary, description=None, labels=None, parent=None, **extra):
    fields = {
        "project": {"key": project},
        "issuetype": {"id": types(project)[issue_type]},
        "summary": summary,
    }
    if description:
        fields["description"] = description
    if labels:
        fields["labels"] = labels
    if parent:
        fields["parent"] = {"key": parent}
    fields.update(extra)
    r = call("POST", "/rest/api/3/issue", {"fields": fields})
    return r["key"]


def set_estimate(key, estimate):
    """Original Estimate needs its own request: the field is absent from the create screen."""
    call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"timetracking": {"originalEstimate": estimate}}})


def url(key):
    return f"{BASE}/browse/{key}"
