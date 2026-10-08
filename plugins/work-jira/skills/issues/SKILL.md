---
name: issues
description: Conventions for creating and running Jira issues — hierarchy, description shape, estimates, labels, and the formatting quirks of the Atlassian editor. Use when creating, editing or reviewing a Jira issue, or when planning how a scope decomposes into a tree of issues.
---

# Jira issues

The company standard is the default. The project profile overrides it. What the
developer says in the current session overrides both.

Read `.claude/project-profile.md` before anything else. If its `## Tracker` or
`## Issues` sections are missing, ask the six questions in
`${CLAUDE_PLUGIN_ROOT}/reference/first-run.md` and write the answers
there — the second run must not ask again.

## Hierarchy

| Situation | Shape |
| --- | --- |
| Work spans frontend and backend | `Epic → Story → Sub-tasks`, one sub-task per technology |
| Work is one technology | `Epic → Task`, no Story |
| A defect | a separate `Bug`, linked to the issue it came from — never a sub-task |

Epic and Story are assigned to the project manager or the analyst; tasks and
sub-tasks to the developers who do the work. Whether the developer running the
command takes the tasks they create is asked, once, and the answer goes into the
profile — the batch never assigns an epic or a story.

**Epic granularity is a project decision.** By product surface (one epic per
screen or area) or by functional layer — whichever the profile says. Surfaces
usually win: the question "where is the results page in this plan?" then has one
answer instead of a scan across three epics.

**No separate QA issue.** QA tests the Story or Task and logs time against it.

**Size.** One task, or a slice of one, is one to three working days. A task that
does not fit gets split — but split by deliverable, not by "part 1 / part 2".

**A story is a user flow, not a pair.** The standard asks for separate
sub-tasks per technology; it does not ask them to mirror each other. One story
— what QA tests and the product owner accepts — may hold three frontend slices
and one backend slice, or a frontend slice alone with the backend pending.
Stories grouped by technology ("frontend foundation") are containers with no
user outcome: their sub-tasks can never be planned into a sprint on their own,
because a sub-task always follows its parent's sprint. Foundation work stays
`Epic → Task`.

**Fix Version and Priority are mandatory** before an issue enters a sprint.
A version mirrors an agreed scope (an estimate document, a release); a
priority follows a rule the profile states, so a new issue gets the right
one without a hand-sorted list. Both are asked at creation, never left at the
default silently.

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

**An epic carries no `Estimate` section and no task count.** Jira sums the
children on the epic itself; a copy in the text goes stale the first time a
child changes — it did, within a day. The epic's `Scope` lists the areas, and
the numbers live on the tasks.

**Another issue is referenced as an inline card**, never as a bare key or a
plain link: `[[PROJ-7]]` for an existing issue, `[[@<summary>]]` for one in the
same batch that may not exist yet. Jira renders the card with key, summary and
status and keeps them current. Where a card cannot be produced — a comment
posted through MCP — the link text carries key and summary, `PROJ-7 Domain
components`, so the reader does not have to open it.

**The description is current when the issue goes to testing.** QA tests against
it, and a description that still promises what moved elsewhere — or omits what
the answers to its questions added — sends them testing stale requirements.
Check it at the transition to testing and again when a result comment is
posted: what is in, what moved out and where (cards), known limits. A record of
what changed since the issue was written — a collapsed `Changes` section (ADF
`expand`) — is welcome but optional; the requirement is that the text is true.

**Every issue a description references is also linked to it**, type `relates
to`, so the relation is visible in the linked-items panel and survives a rewrite
of the text. A dependency is a `Blocks` link, set only when the plan says so —
see `Links`.

## Links

`relates to` is the default — the batch derives it from the references in a
description. `Blocks` states an order: one issue uses the result of another and
cannot be finished before it.

- **The provider blocks the consumer.** The issue whose result is used — an
  API, a component, a contract — `blocks` the issue that uses it; the consumer
  `is blocked by` it. A frontend sub-task that needs an endpoint to be finished
  is blocked by the backend sub-task that delivers it. Written the other way
  round, every tool that reads dependencies shows the work in reverse.
- **At the level where the dependency is true.** Epic → epic when it holds for
  the whole epic: one link from the foundation epic to a product epic instead of
  a link from every task to "project setup". Story → story when one flow needs
  another as a whole. Sub-task → sub-task when a concrete issue needs a
  concrete result — the usual level for a frontend–backend pair, since a sprint
  plans sub-tasks.
- **Not where it adds nothing.** Not to the issue's own parent or child — the
  hierarchy already carries that. Not transitively: A blocks B and B blocks C
  needs no A → C. Not from every task to the foundation — the epic link covers
  it.
- **Starting early is not unblocking.** A consumer may start on mocks while
  its provider is open; the link is about finishing. Say so in the consumer's
  `Technical notes` when that is the plan.
- **Blocked by something outside the team** — a backend issue in the backlog,
  a design not delivered, a decision not taken: Jira's flag (`flag(key)`, the
  "Impediment" the board draws in red) plus an `is blocked by` link to the
  cause. Agree this convention with the developer once per project and record
  it in the profile's `## Tracker` — a project may prefer a status of its own.
  Clear the flag when the cause is gone.
- **Other types, when they earn it.** `Issue split` (`split to` / `split
  from`) when an oversized issue is cut into parts; `Duplicate` to close a
  duplicate. The instance's other types — clones, incident, Gantt — are not
  used for planning: the boards and `next` do not read them.

Every `Blocks` link is shown as a sentence before it is written —
`PROJ-57 Search API blocks PROJ-14 Results grid` — so a reversed pair is
visible at a glance.

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
- **Another issue** is referenced by card, `[[PROJ-7]]` — see above.

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

**The pessimistic estimate is the ceiling.** Time over the optimistic estimate
needs concrete functionality the estimate did not contain, named in the result
comment; work bounced back from testing is the extreme case, not a budget line.
What the design left out and the code had to solve counts as such
functionality — real content the mock did not show (long names, empty or long
lists, a second currency), states it did not draw, narrow widths: name each.
Going over the pessimistic estimate is asked of the developer, never decided
alone — it can be right when the requirements change radically or the risks
the estimate priced in come true.

**Carving a piece out of an issue is the exception**, agreed with the developer
each time. When a part is blocked from outside and the rest can ship, the part
becomes its own issue with a small budget taken from the original: the
original's estimate (both scenarios) goes down by it, so the parent's total does
not grow. Show the numbers — original estimate, time logged, new estimate,
carved budget — before changing anything.

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

A tree is created with `jira.batch`, in three passes — create, resolve the
references, link — so a description may point at a sibling that does not exist
yet when it is written. The node format and the inline notation are in
`${CLAUDE_PLUGIN_ROOT}/reference/batch.md`.

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

## People

Whom to ask and how to mention them lives in the project's team file,
personal and gitignored — names and account ids stay out of committed files.
Its shape and why it exists: `${CLAUDE_PLUGIN_ROOT}/reference/team.md`. A
mention in a comment is an ADF `mention` node with the account id from that
file; a typed "@Name" notifies no one — `mention(name)` and `header(title, *names)` in
the script read the id from the file. A comment handed to the developer is a
link, `comment_url(key, id)`, never a bare id: they open it and forward it. A
thread is read with `thread(key, root_id)`. A follow-up to an existing comment — a
question it left open, an UPD — is a reply in its thread (`comment(...,
reply_to=<id>)`, the editor's Reply), not a new top-level comment.

## Questions waiting for an answer

A posted question is work the developer is waiting on, and its reply lands in
a thread nobody watches. So each one goes on the waiting list —
`docs/local/questions.md` in the project, personal and gitignored like the
team file: one line per question — issue · to whom · comment id · date · what
it blocks.

- **Remember and remind; do not poll.** Name an issue's open lines when work on
  it starts, before it is closed, and whenever a status report or a closing
  step touches it — the ones that block delivery first. Asked what is still
  pending, answer from the file. A reminder costs a file read; a forgotten
  question costs a task that cannot be closed.
- **Check one thread, not the tracker.** The file is a reminder, not the
  truth — a reply can land unrecorded. When a decision rests on a question —
  closing the issue, starting work it blocks — read that open line's thread,
  one call each; closed lines are skipped. A sweep across every issue with an
  open question is long and costly: offer it, and run it only on a yes. The
  tracker's notification feed is no shortcut: read with an API token, it comes
  back empty.
- **A question closes on an answer or a decision** — a reply in its thread, an
  answer the developer relays, or the question dropped. Mark the line with the
  date and where the answer is. A dropped question is said so in its thread,
  so the person asked stops working on it.
- **A processed answer is acknowledged where it was given.** Once a reply has
  been acted on — in the code, the plan or a new question — its author sees
  that it landed: a reaction under it, or a reply in its thread when there is
  something to say (a clarification, a follow-up, a disagreement). Which one is
  the developer's choice, asked once and recorded in the profile's
  `## Tracker`: a fixed reaction (offer ✅, "check mark button"), or asking each
  time whether to react or to reply. An API token cannot set a Jira reaction —
  the reactions gateway answers 401 and the GraphQL `addReaction` covers
  Confluence only — so a reaction is the developer's click: hand over the list,
  issue · comment id · link `…/browse/KEY?focusedCommentId=ID`. Leave out the
  ones already reacted to: the token can read them — GraphQL
  `graphStore_userReactedToIssueComment(id: "ari:cloud:identity::user/<accountId>",
  queryContext: "ari:cloud:platform::site/<cloudId>")` with
  `@optIn(to: "GraphStoreUserReactedToIssueComment")` returns the comments the
  developer reacted to, any emoji, as `…:issue-comment/<issueId>/<commentId>`.
  A reply goes through `comment(..., reply_to=<root id>)`.

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
