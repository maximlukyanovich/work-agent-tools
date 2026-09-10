---
name: issues
description: Conventions for creating and running Jira issues — hierarchy, description shape, estimates, labels, and the formatting quirks of the Atlassian editor. Use when creating, editing or reviewing a Jira issue, or when planning how a scope decomposes into a tree of issues.
---

# Jira issues

The company standard is the default. The project profile overrides it. What the
developer says in the current session overrides both.

Read `.claude/project-profile.md` before anything else. If its `## Tracker` or
`## Issues` sections are missing, ask the five questions in
`${CLAUDE_PLUGIN_ROOT}/reference/first-run.md` and write the answers
there — the second run must not ask again.

## Hierarchy

| Situation | Shape |
| --- | --- |
| Work spans frontend and backend | `Epic → Story → Sub-tasks`, one sub-task per technology |
| Work is one technology | `Epic → Task`, no Story |
| A defect | a separate `Bug`, linked to the issue it came from — never a sub-task |

Epic and Story are assigned to the project manager or the analyst; tasks and
sub-tasks to the developers who do the work.

**Epic granularity is a project decision.** By product surface (one epic per
screen or area) or by functional layer — whichever the profile says. Surfaces
usually win: the question "where is the results page in this plan?" then has one
answer instead of a scan across three epics.

**No separate QA issue.** QA tests the Story or Task and logs time against it.

**Size.** One task, or a slice of one, is one to three working days. A task that
does not fit gets split — but split by deliverable, not by "part 1 / part 2".

## Description

Four sections are required:

- **Context** — one to three sentences: why this exists and where it came from.
  Not a retelling of the design.
- **Scope** — what is included, as a list.
- **Acceptance criteria** — a checklist of concrete, testable statements.
- **Sources of truth** — the spec with its section, the design by screen name,
  related issues.

Four are offered before creation and used when they earn their place:

- **Out of scope** — what is excluded and where it went instead.
- **Technical notes** — the approach, when it is not obvious.
- **Open questions** — forks that must be resolved before work starts.
- **Estimate** — always last when present; see below.

Foundation and cross-cutting issues legitimately carry a reduced set. That is not
an omission.

**Definition of Done is never copied into an issue.** It lives in the company
standard, and a copy drifts from it. The same goes for anything else that has one
canonical home.

**No meta-blocks about the issue itself.** "We split this task", "renamed from
…" — that is Jira's history, not the scope of the work. A companion issue belongs
in `Out of scope`, not in a preamble about the issue's own life.

## Naming things

- **Summary** — imperative, one line, in the profile's summary language.
- **Prefixes** — the standard drops `[FE]` / `[BE]` and leaves direction to the
  label. A project may keep them; if it does, the profile records the deviation
  *and its reason*.
- **The spec** is referenced by document name and section, never by a local file
  path or a date-stamped copy. Paths rot on the first move.
- **The design** is referenced by bundle date and screen name. Check the date
  against the source before writing it down — a local copy lags behind.

## Estimates

The basis is the user's choice, asked once and recorded in the profile:
pessimistic, optimistic (recommended), or optimistic plus overheads such as
automated tests, responsive layout or localisation.

When an overhead percentage is used it goes into **both** scenarios. Otherwise
the two are computed by different formulas and cannot be compared. Rounding is
upwards, to the half hour.

The `Estimate` section states both scenarios, the size and the percentage of the
addition, and which of the two numbers went into the field:

> Optimistic: 6 h of development plus 0.5 h of automated tests (5%) — 6.5 h.
> Pessimistic: 9 h plus 0.5 h — 9.5 h. Original Estimate holds the optimistic one.

Infrastructure issues with no product code get no test percentage — say so in the
section rather than leaving the reader to wonder.

`Original Estimate` is set by a **second request**: the field is absent from the
create screen.

## Labels

Pick from the labels the instance already has — `GET /rest/api/3/label`. Never
invent one. Jira does not normalise case, so `frontend` and `Frontend` live side
by side forever, and the wrong one is invisible in a filter.

## Writing the text

Descriptions go to the API as ADF through
`${CLAUDE_PLUGIN_ROOT}/scripts/jira.py`, not as Markdown through the MCP layer.
The MCP converter rewrites Markdown into wiki markup and loses formatting on the
way: a link under bold loses its target, bold inside a list item becomes literal
asterisks, and task lists do not survive at all.

Consequences worth knowing:

- **Acceptance criteria are a real task list** (`checklist(...)`), tickable in
  the UI. Dashes are a fallback, not the format.
- **A section heading is a wholly bold paragraph.** Bold that starts a list item
  renders as asterisks in the new editor.
- **Inline code goes in backticks**, including when it contains braces —
  `/clients/{id}` renders fine. Literal `{{...}}` does not.
- **Issue keys are plain links.** Bold around a link loses the target.

MCP remains the right tool for reading issues, posting comments, moving statuses
and logging work.

## What gets written down

- **Into the project profile** — anything the developer decided, and anything
  that would otherwise be asked twice.
- **Into this plugin, as a merge** — anything true for every project: a quirk of
  the editor, a field missing from a screen, an API that contradicts its
  documentation.
- **Nowhere** — anything the API answers in one call. Labels, type ids, statuses.
  A copy becomes a second truth that goes stale in silence.

A deviation from the standard is never applied silently: it goes into the profile
with its reason, so the next reader sees a decision rather than a mistake.
