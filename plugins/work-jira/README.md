# work-jira

Run Jira work to one standard.

## Install

```bash
claude plugin install work-jira --marketplace maximlukyanovich/work-agent-tools --scope project
```

Other scopes and updating: [Quick start](../../README.md#quick-start).

## Commands

| Command | What it does |
| --- | --- |
| `/work-jira:plan` | Proposes a hierarchy and a description shape for the scope at hand, then waits for approval. |
| `/work-jira:create` | Creates epics and issues from an approved plan. |
| `/work-jira:next` | Recommends the next issue to take: unblocked first, ordered by what it unblocks, the roadmap and size. Read-only. |
| `/work-jira:questions` | Open questions on an issue — from Jira, the design and the branch state. |
| `/work-jira:status` | Checks whether an issue is actually done. Read-only. |
| `/work-jira:comment` | Drafts and posts a result comment on the issues a branch touched; offers a worklog afterwards. |
| `/work-jira:help` | What this plugin can do: commands, the order they are applied in, the conventions it carries. Optional language argument. |

Starting work on an issue — branch, plan, quality gate — stays a **project**
command, usually `/task`. That procedure is tied to branch naming and the local
gate, and those differ between repositories; only the Jira half is shared.

## Where the rules live

`skills/issues/SKILL.md` is the single source: hierarchy from the
standard, the four required description sections and the optional ones, the
estimate basis and the overhead rule, labels taken from the instance, the ADF
quirks, and what gets written down where. The agent loads it by itself whenever
the conversation touches a Jira issue. This README does not repeat it.

`reference/first-run.md` — the six questions asked once on a fresh project and
written to `.claude/project-profile.md`. `reference/batch.md` — the node format
`jira.batch` takes and the inline notation for references. The plugin does not require
`work-bootstrap`; it derives what it can, carries the standard itself, and asks
only what nothing can answer.

## Scripts

| File | What it does |
| --- | --- |
| `scripts/jira.py` | REST v3 wrapper: descriptions assembled directly in ADF (`h`, `p`, `ul`, `checklist`, `doc`, issue cards), `batch` creating a tree in three passes — create, resolve references, link — plus estimates, assignment and issue links. Coordinates come from the project profile, credentials from `.mcp.json`. |

Why REST for writing: the `mcp-atlassian` layer rewrites Markdown into wiki
markup and loses part of the formatting; task lists do not survive at all, and
a comment's URL is stored as dead plain text. Descriptions and comments go
through the script; MCP stays for reading, statuses and worklog.

## The one hard prerequisite

Access to Jira. Without a working `.mcp.json` the commands stop and say what to
do rather than failing with "no tools found".
