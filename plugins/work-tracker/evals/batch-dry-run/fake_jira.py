"""A read-only Jira for the eval: answers the GETs a dry run of a batch makes and
records every request in the journal the graders read. A write is answered 405.
Writes its port to argv[2] and exits on its own after ten minutes."""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

JOURNAL = sys.argv[1]
EXISTING = {"PROJ-7": ("Design tokens", "Task", ["Frontend"]),
            "PROJ-9": ("Payments API", "Task", ["Backend"])}
TYPES = [{"id": str(10000 + i), "name": n} for i, n in enumerate(["Epic", "Story", "Task", "Sub-task", "Bug"])]
LINKS = [{"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
         {"name": "Relates", "inward": "relates to", "outward": "relates to"},
         {"name": "Issue split", "inward": "split from", "outward": "split to"}]


def answer(path):
    route = urlparse(path).path
    if route == "/rest/api/3/myself":
        return {"accountId": "acc-dev", "displayName": "Dev"}
    if route == "/rest/api/3/label":
        return {"values": ["Frontend", "Backend"], "isLast": True}
    if route == "/rest/api/3/issueLinkType":
        return {"issueLinkTypes": LINKS}
    if route.startswith("/rest/api/3/issue/createmeta/"):
        return {"issueTypes": TYPES}
    if route == "/rest/api/3/priority":
        return [{"name": n} for n in ("Highest", "High", "Medium", "Low")]
    if route.endswith("/versions"):
        return [{"name": "1.0"}]
    if route == "/rest/api/3/search/jql":
        if "parent" in path:
            return {"issues": [], "isLast": True}
        return {"issues": [{"key": k, "fields": {"summary": s}} for k, (s, _, _) in EXISTING.items()],
                "isLast": True}
    if route.startswith("/rest/api/3/issue/"):
        key = route.rsplit("/", 1)[1]
        if key in EXISTING:
            s, t, labels = EXISTING[key]
            return {"key": key, "fields": {"summary": s, "issuetype": {"name": t}, "labels": labels,
                                           "issuelinks": [], "subtasks": [], "description": None}}
    return None


class Handler(BaseHTTPRequestHandler):
    def record(self, code):
        with open(JOURNAL, "a") as f:
            f.write(f"{self.command} {self.path} {code}\n")

    def send(self, code, body):
        data = json.dumps(body).encode()
        self.record(code)
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        body = answer(self.path)
        self.send(200, body) if body is not None else self.send(404, {"errorMessages": ["not in the stub"]})

    def refuse(self):
        self.send(405, {"errorMessages": ["read-only stub"]})

    do_POST = do_PUT = do_DELETE = do_PATCH = refuse

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Handler)
with open(sys.argv[2], "w") as f:
    f.write(str(server.server_address[1]))
threading.Timer(600, lambda: os._exit(0)).start()
server.serve_forever()
