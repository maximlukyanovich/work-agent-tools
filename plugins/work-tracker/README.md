# work-tracker

Run tracker work to one standard. Jira is the recommended tracker, and its
adapter ships here.

Replaces `work-jira`: the same commands under a new prefix, the same
`scripts/jira.py`, the method kept apart from the tracker's transport. A
project moves over with `/work-bootstrap:audit`.

## Install

```bash
claude plugin install work-tracker --marketplace maximlukyanovich/work-agent-tools --scope project
```

Other scopes and updating: [Quick start](../../README.md#quick-start).

## Commands

| Command | What it does |
| --- | --- |
| `/work-tracker:plan` | Proposes a hierarchy and a description shape for the scope at hand, then waits for approval. |
| `/work-tracker:create` | Creates epics and issues from an approved plan. |
| `/work-tracker:next` | Recommends the next issue to take: unblocked first, ordered by what it unblocks, the roadmap and size. Read-only in the tracker. |
| `/work-tracker:questions` | Open questions on an issue — from the tracker, the design and the branch state. |
| `/work-tracker:status` | Checks whether an issue is actually done. Read-only. |
| `/work-tracker:comment` | Drafts and posts a result comment on the issues a branch touched, asks for their status; offers a worklog afterwards. |
| `/work-tracker:check-actuals` | Hours logged on a selection of issues against their estimate, as a dated local HTML report in `docs/local/actuals/`, rebuilt by one command. Read-only in the tracker. |
| `/work-tracker:help` | What this plugin can do: commands, the order they are applied in, the conventions it carries. Optional language argument. |

Starting work on an issue — branch, plan, quality gate — stays a **project**
command, usually `/task`. That procedure is tied to branch naming and the local
gate, and those differ between repositories; only the tracker half is shared.

## Where the rules live

`skills/issues/SKILL.md` is the single source of the method: hierarchy from
the standard, the four required description sections and the optional ones,
the estimate basis and the overhead rule, labels taken from the instance, and
what gets written down where. The agent loads it by itself whenever the
conversation touches an issue. This README does not repeat it.

`skills/question-drafts/SKILL.md` — how a question or notice for someone
outside the team is checked against its sources as soon as it is drafted,
before anyone sees it, wherever it was drafted.

`reference/first-run.md` — the six questions asked once on a fresh project and
written to `.claude/project-profile.md`. The plugin does not require
`work-bootstrap`; it derives what it can, carries the standard itself, and asks
only what nothing can answer.

## Adapters

What a tracker does — its calls, its text format, the quirks of its editor —
lives in its adapter, `reference/adapters/<system>.md`, picked by the `System`
line of the profile's `## Tracker`.

| Adapter | State |
| --- | --- |
| `jira.md`, `jira-batch.md` | Ready and recommended; the default when the profile names no system |

Another tracker gets an adapter written to `reference/adapters/contract.md` —
the operations the method calls, the capabilities it reads, what it skips when
an operation is missing — and lands here as a pull request, not in a project.

## Scripts

| File | What it does |
| --- | --- |
| `scripts/jira.py` | Jira REST v3 wrapper: descriptions assembled directly in ADF (`h`, `p`, `ul`, `checklist`, `doc`, issue cards), `batch` creating a tree in three passes — create, resolve references, link — plus estimates, assignment, issue links, transitions and worklogs. Coordinates come from the project profile, credentials from `.mcp.json`. |

Why the script writes and MCP reads: [the Jira adapter](reference/adapters/jira.md),
"Writing the text".

## The one hard prerequisite

Access to the tracker, as its adapter names it — for Jira, a working
`.mcp.json`. Without it the commands stop and say what to do rather than
failing with "no tools found".
