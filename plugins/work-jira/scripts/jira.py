# -*- coding: utf-8 -*-
"""A thin wrapper over Jira Cloud REST v3 that writes descriptions in native ADF.

Why not through MCP: the mcp-atlassian layer rewrites Markdown into wiki markup and loses
part of the formatting on the way — links under bold lose their target, bold inside a list
item turns into literal asterisks, and task lists do not survive at all. Here the
description is assembled directly in Atlassian Document Format, so it renders as intended.

Issue type ids come from the project's createmeta: they differ between instances.

Inline notation understood by every text helper (`p`, `ul`, `checklist`):
  `code`                 inline code
  [text](url)            a link
  [[PROJ-7]]             an inline card of an existing issue — Jira shows key, summary and status
  [[@<summary>]]         a card of an issue in the same batch, resolved once its key is known;
                         until then it renders as `<summary>` in code

`batch()` creates a tree in three passes — create, resolve references, link — so a
description may point at a sibling that does not exist yet when it is written.
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
_INLINE = re.compile(r"`([^`]+)`|\[\[(.+?)\]\]|\[([^\]]+)\]\(([^)]+)\)")

# summary -> key. Filled by index() and by every create(); read by [[@summary]] references.
_KEYS = {}


def register(summary, key):
    _KEYS[summary] = key


def _card(target):
    """[[PROJ-7]] or [[@summary]] -> an inline card; an unresolved summary -> code text.

    Inline cards are how Jira renders a pasted issue URL: key, summary and status, kept
    current by Jira itself. A plain link would show only the key.
    """
    if target.startswith("@"):
        key = _KEYS.get(target[1:])
        if not key:
            return {"type": "text", "text": target[1:], "marks": [{"type": "code"}]}
    else:
        key = target
    return {"type": "inlineCard", "attrs": {"url": key if key.startswith("http") else url(key)}}


def _text(s):
    """Parses `code`, [[cards]] and [links](url); everything else is plain text."""
    out, pos = [], 0
    for m in _INLINE.finditer(s):
        if m.start() > pos:
            out.append({"type": "text", "text": s[pos:m.start()]})
        if m.group(1):
            out.append({"type": "text", "text": m.group(1), "marks": [{"type": "code"}]})
        elif m.group(2):
            out.append(_card(m.group(2)))
        else:
            out.append({"type": "text", "text": m.group(3),
                        "marks": [{"type": "link", "attrs": {"href": m.group(4)}}]})
        pos = m.end()
    if pos < len(s):
        out.append({"type": "text", "text": s[pos:]})
    return out or [{"type": "text", "text": s}]


def refs(document):
    """Keys of every issue the document references as an inline card, in order of appearance."""
    found = []

    def walk(node):
        if node.get("type") == "inlineCard":
            m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)$", node["attrs"]["url"])
            if m and m.group(1) not in found:
                found.append(m.group(1))
        for child in node.get("content", []):
            walk(child)

    walk(document)
    return found


def has_section(document, title):
    """True when the document carries a section heading of that title."""
    return any(b.get("type") == "paragraph" and len(b.get("content", [])) == 1
               and b["content"][0].get("text") == title
               and b["content"][0].get("marks") == [{"type": "strong"}]
               for b in document.get("content", []))


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


def describe(key, document):
    """Replaces the description. Every task item gets a fresh id, so ticked acceptance
    criteria come back unticked — fine minutes after creation, not on a live issue."""
    call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"description": document}})


def comment(key, document):
    """Posts a comment as ADF and returns its id.

    Why not through MCP: a comment posted as Markdown stores a bare URL as plain text, and
    Jira does not auto-link plain text — a merge-request link in the header arrives dead.
    Built with the same helpers as a description: `doc(p(...), ul([...]))`, with [text](url)
    for the link and [[PROJ-7]] for a card.
    """
    return call("POST", f"/rest/api/3/issue/{key}/comment", {"body": document})["id"]


def edit_comment(key, comment_id, document):
    """Replaces a comment's body. Read it first with

        call("GET", f"/rest/api/3/issue/{key}/comment/{comment_id}")["body"]

    when only one block changes — the rest of the ADF can be kept as Jira holds it."""
    call("PUT", f"/rest/api/3/issue/{key}/comment/{comment_id}", {"body": document})


def resolve(key):
    """Turns unresolved references in a live description into cards, in place.

    An unresolved [[@summary]] was rendered as the summary in code. Once that summary has
    a key, the text node is swapped for the card inside the document Jira holds — task
    items keep their ids and their ticks. Returns the keys resolved.
    """
    document = call("GET", f"/rest/api/3/issue/{key}?fields=description")["fields"]["description"]
    if not document:
        return []
    done = []

    def walk(node):
        for i, child in enumerate(node.get("content", [])):
            if (child.get("type") == "text" and child.get("marks") == [{"type": "code"}]
                    and child["text"] in _KEYS):
                node["content"][i] = {"type": "inlineCard", "attrs": {"url": url(_KEYS[child["text"]])}}
                done.append(_KEYS[child["text"]])
            else:
                walk(child)

    walk(document)
    if done:
        call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"description": document}})
    return done


def index(project):
    """summary -> key for the whole project; also feeds the reference registry.

    One call serves both idempotency (an existing summary is never created twice) and
    [[@summary]] references to issues created by an earlier run.
    """
    found, token = {}, None
    while True:
        path = f"/rest/api/3/search/jql?jql=project%3D{project}&fields=summary&maxResults=100"
        if token:
            path += f"&nextPageToken={token}"
        r = call("GET", path)
        for i in r.get("issues", []):
            found[i["fields"]["summary"]] = i["key"]
        token = r.get("nextPageToken")
        if not token or r.get("isLast", True):
            break
    _KEYS.update(found)
    return found


def relatives(key):
    """Parent and children of an issue — relations the hierarchy already carries."""
    f = call("GET", f"/rest/api/3/issue/{key}?fields=parent,subtasks")["fields"]
    out = {s["key"] for s in f.get("subtasks") or []}
    if f.get("parent"):
        out.add(f["parent"]["key"])
    # `subtasks` lists only sub-tasks; an epic's stories and tasks hang off `parent`.
    children = call("GET", f"/rest/api/3/search/jql?jql=parent%3D{key}&fields=key&maxResults=100")
    out.update(i["key"] for i in children.get("issues", []))
    return out


def linked(key):
    """Keys already linked to the issue, whatever the type or direction."""
    out = []
    for l in call("GET", f"/rest/api/3/issue/{key}?fields=issuelinks")["fields"]["issuelinks"]:
        other = l.get("outwardIssue") or l.get("inwardIssue")
        out.append(other["key"])
    return out


def link(key, other, link_type="Relates"):
    """One issue link, skipped when the pair is already linked in any way.

    Type names come from GET /rest/api/3/issueLinkType. `Relates` is symmetric. For a
    directed type the first key is the outward side: link(a, b, "Blocks") means a blocks b.
    Returns True when a link was created.
    """
    if other == key or other in linked(key):
        return False
    call("POST", "/rest/api/3/issueLink", {
        "type": {"name": link_type},
        "outwardIssue": {"key": key},
        "inwardIssue": {"key": other},
    })
    return True


def myself():
    """Account id of the credentials in use — the developer running the command."""
    return call("GET", "/rest/api/3/myself")["accountId"]


def assign(key, account_id):
    call("PUT", f"/rest/api/3/issue/{key}/assignee", {"accountId": account_id})


def url(key):
    return f"{BASE}/browse/{key}"


# ------------------------------------------------------------------- hours
def half_up(hours):
    """Rounds upwards to the half hour, the company rule for estimates."""
    from math import ceil
    return ceil(hours * 2) / 2


def jira_hours(hours):
    """A duration as the timetracking field expects it: 15h, 6h 30m."""
    whole = int(hours)
    return f"{whole}h" if float(hours).is_integer() else f"{whole}h 30m"


# ------------------------------------------------------------------- batch
_ASSIGNABLE = {"Task", "Sub-task", "Bug"}


def batch(project, nodes, dry_run=False, assignee=None, link_type="Relates", rewrite=False, log=print):
    """Creates a tree of issues in three passes; returns summary -> key for the batch.

    The node format is documented in reference/batch.md. In short: parents come before
    children; `blocks` is a function returning the description blocks, so pass two can
    render it again once every key is known; `parent` is a summary from this batch or an
    existing key.

    Pass 1 creates top-down and sets estimates; a [[@summary]] whose issue does not exist
    yet renders as code. Pass 2 renders every new description again and updates the ones
    that changed; an existing issue is patched in place (see resolve) unless `rewrite`,
    which re-renders it and resets ticked acceptance criteria — for repairing a partial
    run only. Pass 3 links every issue to the issues its description references.
    Epics and stories are never assigned here: the standard gives them to the manager.
    """
    existing = index(project)
    created, first_render = {}, {}

    for n in nodes:
        if n["type"] == "Epic" and n.get("estimate"):
            raise ValueError(f"epic carries an estimate: {n['summary']} — Jira sums the children")
        if n["summary"] in existing:
            log(f"{existing[n['summary']]:8} {n['type']:8} exists, skipped: {n['summary']}")
            continue
        parent = n.get("parent")
        parent_key = created.get(parent) or existing.get(parent) or parent
        document = doc(*n["blocks"]())
        if n["type"] == "Epic" and has_section(document, "Estimate"):
            raise ValueError(f"epic carries an Estimate section: {n['summary']}")
        first_render[n["summary"]] = json.dumps(document, sort_keys=True)
        estimate = n.get("estimate") or ""
        if dry_run:
            log(f"{'(new)':8} {n['type']:8} {estimate:8} {n['summary']}" + (f"  -> {parent_key}" if parent else ""))
            created[n["summary"]] = f"(new) {n['summary']}"
            continue
        key = create(project, n["type"], n["summary"], document, labels=n.get("labels"),
                     parent=parent_key if parent else None)
        register(n["summary"], key)
        created[n["summary"]] = key
        if estimate:
            set_estimate(key, estimate)
        if assignee and n["type"] in _ASSIGNABLE:
            assign(key, assignee)
        log(f"{key:8} {n['type']:8} {estimate:8} {n['summary']}  {url(key)}")

    if dry_run:
        return created

    # Pass 2: every key is known now — resolve the references written as summaries.
    # A new issue is rendered again; an existing one is patched in place so its ticks
    # survive, unless a rewrite was asked for.
    for n in nodes:
        key = created.get(n["summary"]) or existing.get(n["summary"])
        if n["summary"] in existing and not rewrite:
            found = resolve(key)
            if found:
                log(f"{key:8} description patched: {', '.join(found)}")
            continue
        document = doc(*n["blocks"]())
        if n["summary"] in created and json.dumps(document, sort_keys=True) == first_render[n["summary"]]:
            continue
        describe(key, document)
        log(f"{key:8} description {'rewritten' if n['summary'] in existing else 'updated'}: references resolved")

    # Pass 3: the links, derived from the references — one relation, visible in the panel.
    # A card pointing at the issue's own child or parent adds nothing: the hierarchy already
    # shows that relation, and a duplicate `relates to` only clutters the panel.
    for n in nodes:
        key = created.get(n["summary"]) or existing.get(n["summary"])
        family = relatives(key)
        for other in refs(doc(*n["blocks"]())):
            if other in family:
                continue
            if link(key, other, link_type):
                log(f"{key:8} {link_type.lower()} {other}")

    return created
