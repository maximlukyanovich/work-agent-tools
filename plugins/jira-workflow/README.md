# jira-workflow

Run Jira work the way the company standard requires.

## Commands

| Command | What it does |
| --- | --- |
| `/jira-plan` | Proposes a hierarchy and a description shape for the scope at hand, then waits for approval. |
| `/jira-create` | Creates epics and issues from an approved estimate. |
| `/jira-questions` | Open questions on an issue — from Jira, the design and the branch state. |
| `/jira-status` | Checks whether an issue is actually done. Read-only. |
| `/jira-comment` | Drafts and posts a result comment on the issues a branch touched; offers a worklog afterwards. |
| `/jira-help` | What this plugin can do: commands, the order they are applied in, the conventions it carries. Optional language argument. |

Starting work on an issue — branch, plan, quality gate — stays a **project**
command, usually `/task`. That procedure is tied to branch naming and the local
gate, and those differ between repositories; only the Jira half is shared.

## Rules

- **Hierarchy from the standard.** Work spanning frontend and backend is
  `Epic → Story → Sub-tasks`; a single technology is `Epic → Task` with no Story;
  a defect is always a separate `Bug`, linked to what it came from.
- **The human approves the description shape.** The agent proposes the
  recommended set of sections and asks about the optional ones.
- **The estimate basis is the user's choice**: pessimistic, optimistic
  (recommended), or optimistic plus overheads. An overhead percentage goes into
  *both* scenarios — otherwise they are computed by different formulas and cannot
  be compared.
- **Definition of Done is never copied** into issues; it lives in the standard.

## Where the coordinates come from

Three sources, read in this order. Nothing is guessed and nothing is asked twice.

| What | Source | Committed |
| --- | --- | --- |
| API token, account | `.env` → `.mcp.json` | never |
| Instance URL, project key | the project profile | yes |
| Labels, issue types, statuses, fields | the Jira API, every run | no — a copy would drift |
| Decisions: which labels we use, hierarchy, sections, estimate basis | the project profile | yes |

The profile answers *where and what to write*, `.mcp.json` answers *what to
authenticate with*, the API answers *what exists there right now*.

The URL and the project key are **not secrets** and must not live only in an
ignored file: a developer who clones the repository should be able to see which
Jira the project uses before anyone hands them a token.

The distinction between the last two rows matters. The list of labels is fetched
every time, because a copy in the profile would drift from the instance. The
*decision* — "we use `Frontend`, we do not invent our own" — belongs in the
profile, or the agent creates a lowercase duplicate on the next run.

## What must be written down

A command that learns something durable records it before it finishes. Not in the
conversation — in a file.

**Into the project profile:** anything the developer decided and anything that
would otherwise be asked again. Language, prefixes, hierarchy, description
sections, estimate basis, the instance URL and project key, deliberate deviations
from the company standard with the reason for them.

**Into this repository, as a merge:** anything true for every project. A quirk of
the Jira editor, a field missing from the create screen, an API that behaves
unlike its documentation. This is how the method grows; a rule that stays in one
project's notes is lost to the next one.

**Nowhere:** anything the API answers in one call. Labels, issue type ids,
statuses, field schemas. Copying them creates a second truth that goes stale
silently.

A deviation from the company standard is never applied silently. It is written
into the profile together with its reason, so the next reader sees a decision
rather than a mistake.

## Standing on its own

This plugin does **not** require `project-bootstrap`. It works in a repository
that has nothing but code.

**Derived, never asked:** Jira URL and project key from `.mcp.json` or `.env`;
allowed labels from `GET /rest/api/3/label`; issue type ids from the project's
`createmeta`; workflow statuses from the API; platform and branches from git;
stack and quality commands from the manifest files.

**Carried by the plugin:** the company standard — hierarchy, required issue
fields, the status model, Definition of Done. A project that has documented
nothing about Jira still gets all of it.

**Asked once, in a single batch,** because nothing can derive them:

1. Language of summaries and descriptions (default: English)
2. `[FE]` / `[BE]` prefixes in summaries — yes or no (the standard says no)
3. Epic granularity: product surface or functional layer
4. Which description sections apply: the required four plus which optional ones
5. Estimate basis: pessimistic, optimistic, or optimistic plus overheads

The answers are written to `.claude/project-profile.md`, section `## Issues`, not
left in the conversation. A second run asks nothing.

### The profile is sectioned

That is what keeps the plugins independent. One file, but each plugin owns its
sections and can create them alone: `project-bootstrap` writes the whole profile,
`jira-workflow` writes `## Tracker` and `## Issues`, `estimation` writes
`## Estimation`. Install order does not matter.

### The one hard prerequisite

Access to Jira. Without a working `.mcp.json` the command stops and says what to
do — copy `.env.example`, fill it in, run the project's mcp sync — rather than
failing with "no tools found".

## Scripts

| File | What it does |
| --- | --- |
| `scripts/jira.py` | A wrapper over REST v3: descriptions assembled directly in ADF (`h`, `p`, `ul`, `checklist`, `doc`), issue creation, estimate setting. |

Why not through MCP: the `mcp-atlassian` layer rewrites Markdown into wiki markup
and loses part of the formatting — links under bold, bold inside list items; task
lists do not survive at all. MCP stays for reading, comments, statuses and
worklog.

## Skill

`skills/issues` — the full conventions: hierarchy, description sections,
estimates, labels, and the ADF quirks. The agent loads it by itself when the
conversation touches a Jira issue.

`reference/first-run.md` — the five questions asked once on a fresh project.
