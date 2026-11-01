# Jira adapter

The operations the method asks of the tracker, on Jira Cloud. Writing goes
through `${CLAUDE_PLUGIN_ROOT}/scripts/jira.py`, REST v3 with descriptions in
ADF; reading goes through the Atlassian MCP server. A script that imports the
module runs with `PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/scripts`. The form is
`${CLAUDE_PLUGIN_ROOT}/reference/adapters/contract.md`.

## Access

`.mcp.json` in the project, generated from `.env` and gitignored:
`mcpServers.jira.env` holds `JIRA_URL`, `JIRA_USERNAME` and `JIRA_API_TOKEN`.
The script finds it from the working directory upwards, or through
`JIRA_PROJECT_ROOT`. Without a working `.mcp.json` the command stops and says
how to get one — copy `.env.example`, fill it in, run the project's mcp sync —
rather than failing with "no tools found".

## Capabilities

| Capability | Jira |
| --- | --- |
| Sub-tasks | yes |
| Estimate unit | time — `Original Estimate`, `Remaining Estimate` |
| Time tracking | yes — worklogs |
| Text format | ADF; Markdown through MCP loses formatting |
| Mention | by account id |
| Reply in a thread | yes |
| Reaction | read only with an API token |
| Flag | yes |

## Operations

| Operation | On Jira |
| --- | --- |
| `read` | MCP: the issue — description, acceptance criteria, comments, attachments, parent, links |
| `query` | One JQL through MCP: every open issue in scope with status, assignee, estimate, remaining time, links and parent, and every issue they link to |
| `vocabulary` | Issue type ids from `createmeta` for the project, labels from `GET /rest/api/3/label`, link types from `GET /rest/api/3/issueLinkType`, statuses from the workflow API |
| `create tree` | `jira.batch`, dry run included — `${CLAUDE_PLUGIN_ROOT}/reference/adapters/jira-batch.md` |
| `describe` | `describe(key, doc)` replaces a description; `resolve(key)` patches its unresolved references in place |
| `comment` | `comment(key, doc)`, `edit_comment(key, id, doc)`, `comment(..., reply_to=<root id>)` — the editor's Reply; `thread(key, root_id)` reads a thread; `comment_url(key, id)` is the link handed back |
| `mention` | An ADF `mention` node with the account id; `mention(name)` and `header(title, *names)` read the id from the team file |
| `transition` | `transition(key, status)` matches the name against the transitions the issue offers |
| `estimate` | `set_estimate(key, estimate, remaining=None)` |
| `worklog` | `worklog(key, started, spent, text, leave_remaining=False)` |
| `assign`, `release` | `assign(key, account_id)`, `myself()`; `set_release(key, fix_version, priority)` |
| `flag` | `flag(key)`; `flag(key, on=False)` clears it |
| `react` | None with an API token — see "Reactions" |

## Writing the text

Descriptions go to the API as ADF through
`${CLAUDE_PLUGIN_ROOT}/scripts/jira.py`, not as Markdown through the MCP layer.
The MCP converter rewrites Markdown into wiki markup and loses formatting on the
way: a link under bold loses its target, bold inside a list item becomes literal
asterisks, and task lists do not survive at all.

A tree is created with `jira.batch`, in three passes — create, resolve the
references, link — so a description may point at a sibling that does not exist
yet when it is written. The node format and the inline notation are in
`${CLAUDE_PLUGIN_ROOT}/reference/adapters/jira-batch.md`.

Consequences worth knowing:

- **Acceptance criteria are a real task list** (`checklist(...)`), tickable in
  the UI. Dashes are a fallback, not the format.
- **A section heading is a wholly bold paragraph.** Bold that starts a list item
  renders as asterisks in the new editor.
- **Inline code goes in backticks**, including when it contains braces —
  `/clients/{id}` renders fine. Literal `{{...}}` does not.
- **Issue keys are inline cards** — `[[PROJ-7]]`, or `[[@<summary>]]` for an
  issue created in the same batch. A plain link shows only the key; bold around
  a link loses the target.

MCP remains the right tool for reading issues, moving statuses and logging
work. Comments go the same way as descriptions — `comment()` / `edit_comment()`
in the script — as soon as they carry a link or code: posted as Markdown, a URL
is stored as plain text and Jira does not auto-link it.

## Fields

- **The epic sums its children.** Jira shows the children's estimates on the
  epic itself.
- **`Original Estimate` is set by a second request**: the field is absent from
  the create screen.
- **Jira fills `Remaining Estimate` from `Original Estimate` only while
  Remaining is empty**; once set, an edit to the original leaves it alone, so a
  re-estimate sets both in the same request (`set_estimate(key, new,
  remaining=…)`).
- **Labels: Jira does not normalise case**, so `frontend` and `Frontend` live
  side by side forever.
- **The flag** is the "Impediment" the board draws in red.

## Reactions and notifications

An API token cannot set a Jira reaction — the reactions gateway answers 401 and
the GraphQL `addReaction` covers Confluence only — so a reaction is the
developer's click: hand over the list, issue · comment id · link
`…/browse/KEY?focusedCommentId=ID`. Leave out the ones already reacted to: the
token can read them — GraphQL
`graphStore_userReactedToIssueComment(id: "ari:cloud:identity::user/<accountId>",
queryContext: "ari:cloud:platform::site/<cloudId>")` with
`@optIn(to: "GraphStoreUserReactedToIssueComment")` returns the comments the
developer reacted to, any emoji, as `…:issue-comment/<issueId>/<commentId>`.

The notification feed is no shortcut to replies: read with an API token, it
comes back empty.
