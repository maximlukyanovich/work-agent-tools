#!/usr/bin/env bash
# A project on Jira with an approved tree in its local notes, and a read-only Jira
# stub on the host. The stub is reached through the sandbox's proxy: JIRA_URL names
# `localhost.`, which no_proxy does not match, so the request leaves the sandbox
# and the proxy resolves it to the host. The stub journals every request in
# .stub/requests.log and exits on its own after thirty minutes.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git init -q -b main .
git config commit.gpgsign false
printf 'docs/local/\n.mcp.json\n.stub/\n' > .gitignore
mkdir -p .claude docs/local/plans .stub
nohup python3 "$HERE/fake_jira.py" "$PWD/.stub/requests.log" "$PWD/.stub/port" \
  >/dev/null 2>&1 < /dev/null &
for _ in $(seq 50); do [ -s .stub/port ] && break; python3 -c 'import time; time.sleep(0.1)'; done
PORT="$(cat .stub/port)"
printf '{"mcpServers":{"jira":{"env":{"JIRA_URL":"http://localhost.:%s/","JIRA_USERNAME":"dev@example.com","JIRA_API_TOKEN":"token"}}}}\n' "$PORT" > .mcp.json
cat > .claude/project-profile.md <<'PROFILE'
# Project profile

## Tracker

- System: Jira Cloud, example.atlassian.net
- Project key: PROJ
- Labels: Frontend, Backend
- Access: `.mcp.json`, generated from `.env`

## Issues

- Summaries and descriptions: English
- Prefixes: dropped, the label carries the direction
- Epics: one per product surface
- Optional sections: Out of scope, Technical notes, Open questions
- Estimate basis: optimistic; Original Estimate holds it
- Assignee: tasks, sub-tasks and bugs go to the developer who creates them
- Fix version: 1.0 for the checkout scope
- Priority: High for work that blocks another issue, Medium otherwise
PROFILE
cat > docs/local/plans/checkout.md <<'PLAN'
# Checkout — approved tree

Approved by the developer. Fix version 1.0.

```
Epic     Checkout
  Story  Checkout flow
    Sub  Order endpoint            6h    Backend   blocks "Cart & payment form"
    Sub  Cart & payment form       8h    Frontend  uses the tokens of PROJ-7, waits on PROJ-9 Payments API
```

Descriptions: Context, Scope, Acceptance criteria, Sources of truth on every issue;
Estimate last on the two sub-tasks, none on the epic. The epic's Scope lists the
flow; the sub-tasks reference each other and PROJ-7 as cards.

Dependencies, as sentences:

- Order endpoint blocks Cart & payment form
- PROJ-9 Payments API blocks Order endpoint
PLAN
git add -A
GIT_AUTHOR_NAME=T GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=T GIT_COMMITTER_EMAIL=t@example.com \
  git commit -qm "Project profile"
