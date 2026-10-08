# Harness changes

What `work-bootstrap` changed in the method that an already set-up project
should carry over. Read by `/work-bootstrap:audit` — which checks only the
entries after the project's baseline — and by the `SessionStart` hook, which
says when a project is behind.

**Only changes a project acts on.** A skill or command that runs from this
plugin reaches every project when the plugin updates and has no entry here;
neither does a rewording. An entry exists when a project's own files — its
`AGENTS.md`, commands, skills, hooks — need an edit to match.

**Append-only.** New entries go at the end; an entry is never rewritten or
removed, because a project's baseline names it. The id after the date is
unique and is what a baseline records.

Each entry:

- `What:` the change, in one or two sentences, as a project would apply it;
- `Check:` the checklist item or audit section that verifies it;
- `Applies to:` which projects — an entry that does not apply is skipped, and
  the baseline still moves past it.

## 2026-09-30 · closing-steps

What: every command that merges ends with one question offering the result
comment, the worklog, branch deletion and anything raised for another team,
carrying the current state; it merges without deleting the branch.
Check: checklist — "Any command that merges ends by offering the closing
steps"; audit §8.
Applies to: projects with a merging command.

## 2026-09-30 · review-ledger

What: the review command keeps a pass ledger in the personal space, reviews
the delta since the last reviewed head, runs blind before reconciling, tags
findings, recommends a fresh session; the merging command reads the ledger.
Check: checklist — "A review command, if there is one, keeps a pass ledger";
audit §5.
Applies to: projects with a review command.

## 2026-10-01 · gate-out-of-hooks

What: no git hook runs the whole gate; the commit and push commands run it,
the push skipping a tree already validated; lint-staged runs the formatter
after the linter's fixes.
Check: checklist — "Deterministic layer"; audit §6.
Applies to: every project.

## 2026-10-01 · opening-steps

What: the task-start command (`/task` or its equivalent) asks once, carrying
the current state, about the in-progress transition, the assignee and the
parent's status when a tracker is reachable; it loads `kickoff` before its
first question and, once the plan is approved, the project's placement,
component and testing skills before the first production edit.
Check: checklist — "The command that starts a task, when a tracker is
reachable, offers the opening steps"; audit §8, the mirror check.
Applies to: projects with a task-start command.

## 2026-10-01 · review-fix-proof

What: `AGENTS.md` says to load the testing skill before fixing review
findings, and that skill asks for a reverted-fix test per finding, every state
the fix touches, and a finding → test table before the commit.
Check: checklist — "Fixing review findings is a rule in `AGENTS.md`"; audit §5.
Applies to: every project; the testing skill's name is the project's own.

## 2026-10-03 · question-waiting-list

What: the task-start command names the issue's open questions from the
waiting list (`docs/local/questions.md`, `work-jira` `issues` skill) in its
opening-steps message; the merge command's closing step puts a newly posted
question on that list and closes one the merge answers.
Check: checklist — the opening-steps and closing-steps items; audit §8.
Applies to: projects that use `work-jira`.

## 2026-10-03 · design-fidelity

What: projects that implement a design add to their component skill — an
off-scale value becomes a new token (no silent snap) and goes to the designer;
nothing undrawn is invented; the task report lists deviations from the screen.
A layout-measuring script runs in the task's browser check, and the review
command gains a `layout` mode that runs it.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source.

## 2026-10-06 · stale-cache-state

What: the testing skill's list of a query's states gains success that may be
out of date — while a refetch is in flight, and while the cache still counts
as fresh by its stale time, so nothing is read again on mount. A fix that
closed only the first was followed by the second in the next review.
Check: checklist — "Fixing review findings is a rule in `AGENTS.md`", the
testing skill it points to; audit §5.
Applies to: projects whose data layer caches query results.

## 2026-10-06 · processed-answer-ack

What: the profile's `## Tracker` records how an answer the agent has acted on
is acknowledged — a fixed reaction (✅ offered) or asking each time whether to
react or to reply. The developer sets the reaction by hand: an API token cannot.
Check: checklist — "With Jira, the profile's `## Tracker` says how a processed
answer is acknowledged"; audit §7.
Applies to: projects that use `work-jira` with Jira.

## 2026-10-07 · clean-install-deploy

What: with pnpm 11, `AGENTS.md` §2 says a new dependency with a build script
needs an `allowBuilds` entry, and the `pnpm-workspace.yaml` header says to
prove it with a frozen install on a fresh checkout — a warm `node_modules`
hid a missing entry until the server's install failed. Once the project is
deployed, the root README gains a Deployment section: production commands,
pinned versions, and every variable the build and the start need.
Check: checklist — "A fresh checkout installs", "Once deployed anywhere";
audit §12.
Applies to: projects on pnpm 11; the README part, deployed projects.

## 2026-10-07 · review-handover

What: the commit command, after a task's last commit or a round of review
fixes, ends its report with the review command ready to paste into a fresh
session — the range `<base>..<head>`, what to skip, one code block per branch.
Check: checklist — "The commit command … ends its report with the review
command"; audit §5.
Applies to: projects with a commit command and a review command.

## 2026-10-08 · real-content-layout

What: a project with a design source adds to its component skill — lay out for
real content rather than the mock's (clamp what can grow with the full text
reachable, wrap what must wrap, check narrow widths), and name that work in
the result comment as work the design did not contain. Remove any leftover
"snap to the nearest token" wording.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source.

## 2026-10-09 · states-from-source

What: a project with a design source adds to its component skill — every
interactive state (hover, focus, pressed, selected, disabled, invalid, open,
loading) and every rule of the design's global stylesheet is read from the
source each time a component is built or changed and carried over as written;
nothing is filled in from memory, from the underlying library's defaults or
from a similar component.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source.
