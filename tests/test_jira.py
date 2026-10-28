"""jira.py's behaviour, pinned before it changes: ADF, hours, worklog and batch.

jira.py writes to a live Jira, so nothing here reaches one. The credentials are a fake
.mcp.json found through JIRA_PROJECT_ROOT, and `jira.call` is replaced by FakeJira: a GET
is answered from a dictionary of paths, a POST or a PUT is only recorded.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins" / "work-jira" / "scripts"
BASE = "https://example.atlassian.net"

_ROOT = tempfile.TemporaryDirectory()
(Path(_ROOT.name) / ".mcp.json").write_text(json.dumps({"mcpServers": {"jira": {"env": {
    "JIRA_URL": BASE + "/", "JIRA_USERNAME": "dev@example.com", "JIRA_API_TOKEN": "token"}}}}))
os.environ["JIRA_PROJECT_ROOT"] = _ROOT.name
sys.path.insert(0, str(SCRIPTS))

import jira  # noqa: E402


def text(s, *marks):
    node = {"type": "text", "text": s}
    if marks:
        node["marks"] = list(marks)
    return node


CODE = {"type": "code"}


def card(key):
    return {"type": "inlineCard", "attrs": {"url": f"{BASE}/browse/{key}"}}


class FakeJira:
    """Stands in for `jira.call`: a GET is answered from `routes`, a POST or a PUT recorded."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})
        self.calls = []

    def __call__(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET":
            if path not in self.routes:
                raise AssertionError(f"unexpected GET {path}")
            return self.routes[path]
        return {"id": "10001", "key": "PROJ-100"}

    def writes(self):
        return [c for c in self.calls if c[0] != "GET"]


class JiraTest(unittest.TestCase):
    def setUp(self):
        jira._KEYS.clear()
        jira._TYPE_CACHE.clear()

    def fake(self, routes=None):
        fake = FakeJira(routes)
        patcher = mock.patch.object(jira, "call", fake)
        patcher.start()
        self.addCleanup(patcher.stop)
        return fake


class InlineTest(JiraTest):
    def test_plain_and_empty_text(self):
        self.assertEqual(jira._text("plain"), [text("plain")])
        self.assertEqual(jira._text(""), [text("")])

    def test_code_link_and_card(self):
        self.assertEqual(jira._text("Run `make` per [the guide](https://x.test/g), see [[PROJ-7]]."), [
            text("Run "),
            text("make", CODE),
            text(" per "),
            text("the guide", {"type": "link", "attrs": {"href": "https://x.test/g"}}),
            text(", see "),
            card("PROJ-7"),
            text("."),
        ])

    def test_card_keeps_a_full_url(self):
        self.assertEqual(jira._text("[[https://other.test/browse/X-1]]"),
                         [{"type": "inlineCard", "attrs": {"url": "https://other.test/browse/X-1"}}])

    def test_summary_reference_is_code_until_registered(self):
        self.assertEqual(jira._text("[[@Search API]]"), [text("Search API", CODE)])
        jira.register("Search API", "PROJ-3")
        self.assertEqual(jira._text("[[@Search API]]"), [card("PROJ-3")])


class BlocksTest(JiraTest):
    def test_blocks(self):
        self.assertEqual(jira.h("Scope"),
                         {"type": "paragraph", "content": [text("Scope", {"type": "strong"})]})
        self.assertEqual(jira.p("a `b`"), {"type": "paragraph", "content": [text("a "), text("b", CODE)]})
        self.assertEqual(jira.ul(["one", "[[PROJ-2]]"]), {"type": "bulletList", "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [text("one")]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [card("PROJ-2")]}]},
        ]})
        self.assertEqual(jira.expand("Details", [jira.p("x")]),
                         {"type": "expand", "attrs": {"title": "Details"}, "content": [jira.p("x")]})
        self.assertEqual(jira.doc(jira.p("x"), jira.h("y")),
                         {"type": "doc", "version": 1, "content": [jira.p("x"), jira.h("y")]})

    def test_checklist_structure_and_fresh_ids(self):
        block = jira.checklist(["done when `ok`", "second"])
        ids = [block["attrs"].pop("localId")] + [i["attrs"].pop("localId") for i in block["content"]]
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(block, {"type": "taskList", "attrs": {}, "content": [
            {"type": "taskItem", "attrs": {"state": "TODO"}, "content": [text("done when "), text("ok", CODE)]},
            {"type": "taskItem", "attrs": {"state": "TODO"}, "content": [text("second")]},
        ]})


class ReadingTest(JiraTest):
    def test_refs_in_order_without_repeats(self):
        document = jira.doc(jira.p("[[PROJ-2]] and [[PROJ-1]]"),
                            jira.ul(["[[PROJ-2]]", "[a link](https://x.test)"]))
        self.assertEqual(jira.refs(document), ["PROJ-2", "PROJ-1"])

    def test_has_section(self):
        document = jira.doc(jira.h("Estimate"), jira.p("6h"))
        self.assertTrue(jira.has_section(document, "Estimate"))
        self.assertFalse(jira.has_section(document, "6h"))
        self.assertFalse(jira.has_section(document, "Scope"))


class HoursTest(JiraTest):
    def test_half_up(self):
        for hours, want in [(0, 0), (0.1, 0.5), (0.5, 0.5), (1.2, 1.5), (1.5, 1.5), (2, 2), (2.01, 2.5)]:
            self.assertEqual(jira.half_up(hours), want, hours)

    def test_jira_hours(self):
        for hours, want in [(15, "15h"), (2.0, "2h"), (6.5, "6h 30m"), (0.5, "0h 30m")]:
            self.assertEqual(jira.jira_hours(hours), want, hours)


class WorklogTest(JiraTest):
    STARTED = "2026-10-08T09:00:00.000+0300"

    def test_body(self):
        fake = self.fake()
        self.assertEqual(jira.worklog("PROJ-3", self.STARTED, "3h 30m", "Search API"), "10001")
        self.assertEqual(fake.calls, [("POST", "/rest/api/3/issue/PROJ-3/worklog", {
            "started": self.STARTED, "timeSpent": "3h 30m", "comment": jira.doc(jira.p("Search API")),
        })])

    def test_leave_remaining(self):
        fake = self.fake()
        jira.worklog("PROJ-3", self.STARTED, "45m", "Review", leave_remaining=True)
        self.assertEqual(fake.calls[0][1], "/rest/api/3/issue/PROJ-3/worklog?adjustEstimate=leave")


def fields(issue_type, parent=None, labels=()):
    out = {"issuetype": {"name": issue_type}, "labels": list(labels)}
    if parent:
        out["parent"] = {"key": parent}
    return {"fields": out}


class ClashesTest(JiraTest):
    NODE = {"type": "Story", "summary": "Search page", "parent": "Search", "labels": ["frontend"]}
    EXISTING = {"Search": "PROJ-1", "Search page": "PROJ-2"}
    PATH = "/rest/api/3/issue/PROJ-2?fields=issuetype,parent,labels"

    def clashes(self, held):
        self.fake({self.PATH: held})
        return jira._clashes([self.NODE], self.EXISTING)

    def test_same_issue_is_no_clash(self):
        self.assertEqual(self.clashes(fields("Story", "PROJ-1", ["frontend", "web"])), [])

    def test_other_type_parent_and_labels(self):
        self.assertEqual(self.clashes(fields("Task", "PROJ-9", ["web"])),
                         ["'Search page' is PROJ-2 (type Task; parent PROJ-9; labels web)"])

    def test_no_parent_and_no_labels(self):
        self.assertEqual(self.clashes(fields("Story")),
                         ["'Search page' is PROJ-2 (parent none; labels none)"])

    def test_new_summary_is_not_read(self):
        fake = self.fake()
        self.assertEqual(jira._clashes([dict(self.NODE, summary="Filters")], self.EXISTING), [])
        self.assertEqual(fake.calls, [])


def tree():
    return [
        {"type": "Epic", "summary": "Search",
         "blocks": lambda: [jira.h("Goal"), jira.p("Find a product.")]},
        {"type": "Story", "summary": "Search page", "parent": "Search", "labels": ["frontend"],
         "priority": "High", "split_from": "PROJ-5",
         "blocks": lambda: [jira.p("Uses [[@Search API]].")]},
        {"type": "Task", "summary": "Search API", "parent": "Search page", "labels": ["backend"],
         "estimate": "6h 30m", "fix_version": "1.1", "blocked_by": ["PROJ-9"],
         "blocks": lambda: [jira.p("Serves [[@Search page]], see [[PROJ-9]]."),
                            jira.h("Estimate"), jira.p("6h 30m")]},
    ]


INDEX = "/rest/api/3/search/jql?jql=project%3DPROJ&fields=summary&maxResults=100"


def issue(key, query):
    return f"/rest/api/3/issue/{key}?fields={query}"


class BatchTest(JiraTest):
    def run_batch(self, routes, dry_run):
        fake = self.fake(routes)
        log = []
        created = jira.batch("PROJ", tree(), dry_run=dry_run, fix_version="1.0", log=log.append)
        return fake, log, created

    def test_dry_run_log(self):
        fake, log, created = self.run_batch({
            INDEX: {"issues": [], "isLast": True},
            issue("PROJ-9", "summary"): {"fields": {"summary": "Catalogue API"}},
        }, dry_run=True)
        self.assertEqual(log, [
            "(new)    Epic              Search  [1.0 · NO PRIORITY]",
            "(new)    Story             Search page  -> (new) Search  [1.0 · High]",
            "(new)    Task     6h 30m   Search API  -> (new) Search page  [1.1 · NO PRIORITY]",
            "would link: PROJ-5  split to  (new) Search page",
            "would link: PROJ-9 Catalogue API  blocks  (new) Search API",
        ])
        self.assertEqual(created, {s: f"(new) {s}" for s in ("Search", "Search page", "Search API")})
        self.assertEqual(fake.writes(), [])

    def test_second_run_only_reads(self):
        fake, log, created = self.run_batch({
            INDEX: {"issues": [{"key": "PROJ-1", "fields": {"summary": "Search"}},
                               {"key": "PROJ-2", "fields": {"summary": "Search page"}},
                               {"key": "PROJ-3", "fields": {"summary": "Search API"}}], "isLast": True},
            issue("PROJ-1", "issuetype,parent,labels"): fields("Epic"),
            issue("PROJ-2", "issuetype,parent,labels"): fields("Story", "PROJ-1", ["frontend"]),
            issue("PROJ-3", "issuetype,parent,labels"): fields("Task", "PROJ-2", ["backend"]),
            issue("PROJ-1", "description"): {"fields": {"description": None}},
            issue("PROJ-2", "description"): {"fields": {"description": jira.doc(
                {"type": "paragraph", "content": [text("Uses "), card("PROJ-3"), text(".")]})}},
            issue("PROJ-3", "description"): {"fields": {"description": jira.doc(
                {"type": "paragraph", "content": [text("Serves "), card("PROJ-2"), text(", see "),
                                                  card("PROJ-9"), text(".")]})}},
            issue("PROJ-1", "parent,subtasks"): {"fields": {"subtasks": []}},
            issue("PROJ-2", "parent,subtasks"): {"fields": {"parent": {"key": "PROJ-1"}, "subtasks": []}},
            issue("PROJ-3", "parent,subtasks"): {"fields": {"parent": {"key": "PROJ-2"}, "subtasks": []}},
            "/rest/api/3/search/jql?jql=parent%3DPROJ-1&fields=key&maxResults=100": {"issues": [{"key": "PROJ-2"}]},
            "/rest/api/3/search/jql?jql=parent%3DPROJ-2&fields=key&maxResults=100": {"issues": [{"key": "PROJ-3"}]},
            "/rest/api/3/search/jql?jql=parent%3DPROJ-3&fields=key&maxResults=100": {"issues": []},
            issue("PROJ-3", "summary"): {"fields": {"summary": "Search API"}},
            issue("PROJ-9", "summary"): {"fields": {"summary": "Catalogue API"}},
            issue("PROJ-5", "issuelinks"): {"fields": {"issuelinks": [{"outwardIssue": {"key": "PROJ-2"}}]}},
            issue("PROJ-9", "issuelinks"): {"fields": {"issuelinks": [{"outwardIssue": {"key": "PROJ-3"}}]}},
            issue("PROJ-3", "issuelinks"): {"fields": {"issuelinks": [{"inwardIssue": {"key": "PROJ-9"}}]}},
        }, dry_run=False)
        self.assertEqual(log, [
            "PROJ-1   Epic     exists, skipped: Search",
            "PROJ-2   Story    exists, skipped: Search page",
            "PROJ-3   Task     exists, skipped: Search API",
            "already linked, skipped: PROJ-9 Catalogue API  blocks  PROJ-3 Search API",
        ])
        self.assertEqual(created, {})
        self.assertEqual(fake.writes(), [])


if __name__ == "__main__":
    unittest.main()
