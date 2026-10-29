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
  the baseline still moves past it;
- `Supersedes:` optional — the id of an earlier entry and the part this one
  replaces. The earlier entry stays as it is; the audit checks that part
  against the later one.

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

## 2026-10-09 · loading-states

What: a project with a design source adds to its component skill — wherever
something loads, decide what is on screen until it arrives; when the design
is silent, ask the designer and use a placeholder from existing primitives,
named in the task report, never a blank area.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source.

## 2026-10-09 · task-worktree

What: the command that starts a task takes an optional `worktree` argument
and, from a live `git status`, offers one when the tree is busy — a folder
beside the repository, with the ignored files the work reads linked in; the
command that merges offers `git worktree remove` with the branch deletion.
Check: checklist — "The command that starts a task takes an optional
`worktree` argument"; audit §8.
Applies to: every project with a command that starts a task.

## 2026-10-12 · sources-first

What: a project with a design source replaces "the screen wins over a
component source" in its design-source document: the design's guide,
component sources and tokens take precedence; a screen that disagrees is
escalated to the developer with the likely reading (a screen updated without
its sources usually means the screen is final); decisions go to the register
and the designer gets the gaps in one comment asking to update the sources.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source.

## 2026-10-12 · review-report-block

What: the review command's report opens with the same block on every pass,
zeros included — target and range, the trajectory, a blocker / major / minor
/ nit table, and the verdict that follows from it — then the findings.
Check: checklist — the review command item; audit §5.
Applies to: projects with a review command that keeps a pass ledger.

## 2026-10-12 · commit-index-check

What: the commit command, right before `git commit`, compares
`git diff --cached --name-only` with the paths it proposed and stops on a
difference; after a commit the `commit-msg` hook refused, it commits the same
index again with the message fixed instead of staging the next group on top.
Check: checklist — "The commit command compares the staged paths"; audit §6.
Applies to: every project with a commit command.

## 2026-10-13 · command-target

What: the commands that commit, review and merge take an optional target — a
branch or a worktree path, recognised by shape — and run there from the main
workspace: git calls as `git -C <tree>`, the gate in that tree, shared
records such as the validated tree in its git directory. A branch checked out
nowhere is reviewed by its refs, with the gate reported as not run.
Check: checklist — "The commands that commit, review and merge take a
target"; audit §6.
Applies to: projects with a commit, review or merge command.

## 2026-10-13 · next-step-handoff

What: every command ends with its next step as a block ready to paste, one
per option; at a phase boundary — a task's last commit, a review, before and
after a merge — through `/work-bootstrap:handoff`, for a fresh session. The
review ends with the fix-round prompt naming the pass, the ids, the ledger,
the plan and the target, or with the merge command when it reads ready; the
merge ends with the start of the next task.
Check: checklist — "Every command ends with its next step"; audit §5, §6.
Applies to: every project with commands.

## 2026-10-13 · review-group-agent

What: review groups above the delegation threshold go to a project agent,
`.claude/agents/review-group.md` (`model: sonnet`, read-only tools, findings
only, no ledger and no verdict), and `.gitignore` un-ignores
`.claude/agents/`. The review command takes `model=<name>` and passes it as
the Agent call's model; the synthesis, the refutation of every blocker and
major, and the ledger stay with the session's model.
Check: checklist — "Review groups above the delegation threshold"; audit §5.
Applies to: projects with a review command that delegates file groups.

## 2026-10-13 · plan-state-table

What: the task command's plan carries the three sections the `kickoff` skill
names — a state table (state × event → expected → test) for work that
changes state, the framework behaviour it rests on with file:line, one line
on the structural option. The testing skill asks for a transition table
before any edit to state, a fix or not, each row's test red with the edit
reverted; the commit command shows those rows before it asks.
Check: checklist — the task command item and "Fixing review findings";
audit §5, §8.
Applies to: every project with a task command or a testing skill.

## 2026-10-13 · worktree-typegen-port

What: the worktree setup in the command that starts a task runs the
framework's type generation when its generated types are ignored, and gives
the second dev server and the end-to-end run their own port — a runner that
reuses a running server otherwise tests the main tree's code.
Check: checklist — "The command that starts a task takes an optional
`worktree` argument"; audit §8.
Applies to: projects whose task command offers a worktree.

## 2026-10-13 · recurring-findings-upstream

What: the review command ends its report with one line proposing to move a
finding upstream — to the cheapest layer that would have caught it during the
work — when its mechanism is already in a ledger, this target's or another's;
the owner decides, the review applies nothing.
Check: checklist — "A review command, if there is one, keeps a pass ledger";
audit §5.
Applies to: projects with a review command.

## 2026-10-13 · generator-block

What: a block a generator owns in `AGENTS.md` or `CLAUDE.md` stays intact
between its markers, and the harness is written around it. Next.js writes
`nextjs-agent-rules`; removed, it is appended again by `next dev` run by an
agent, and the tree is dirty from then on.
Check: checklist — "A block a generator owns in `AGENTS.md` or `CLAUDE.md` is
intact"; audit §1.
Applies to: projects whose framework manages such a block — Next.js where
`node_modules/next/dist/server/lib/generate-agent-files.js` exists.

## 2026-10-13 · plugin-set

What: the `mluk-work-agent-tools` plugins a project uses are recorded in the
project — `enabledPlugins` in `.claude/settings.json`, or in
`settings.local.json` when the project's rules keep AI settings out of git —
through `claude plugin install <plugin>@mluk-work-agent-tools --scope project`
(or `local`). A plugin installed for one user only is missing for everyone
else; one installed at user scope loads into every project on that machine.
Check: checklist — "The plugin set is recorded where Q10 put it".
Applies to: projects that use any `mluk-work-agent-tools` plugin.

## 2026-10-13 · typegen-type-check

What: in a Next.js project whose code uses the generated route types —
`LayoutProps`, `PageProps`, `RouteContext` — the type-check script runs
`next typegen` before `tsc --noEmit`. Those types exist only after type
generation and `next-env.d.ts` is ignored, so `tsc` alone fails on a clean
checkout and in a fresh worktree.
Check: checklist — "A fresh checkout installs"; audit §12.
Applies to: Next.js projects that use the generated route types.

## 2026-10-14 · review-group-inherit-model

What: `.claude/agents/review-group.md` carries `model: inherit` instead of
`model: sonnet`, so review groups run on the model the developer chose for
the review session. The session's refutation removes false findings but
never recovers a missed one, and above the delegation threshold the groups
are where the diff is read. `model=<name>` still overrides it for one run.
Check: checklist — "Review groups above the delegation threshold"; audit §5.
Applies to: projects that carry `review-group-agent`.

## 2026-10-15 · ready-closes-range

What: a review that reads ready closes the range it read, not the task.
Before the merge command, the review command reads the plan and the task's
notes in the personal space; work the branch has not done yet makes the next
step "continue the task" — `Read <NEXT.md> and continue`, or the plan's next
step — and the merge waits. A review after the task's last commit goes to the
merge as before.
Check: checklist — "Every command ends with its next step"; audit §5.
Applies to: projects with a review command.

## 2026-10-15 · review-frozen-range

What: the review command says, next to "run it in a fresh session", that
while the branch's findings have a fix round open no new work lands on it —
the fixes, the repeat review, then the plan goes on. One tree, one writer.
Check: checklist — "A review command, if there is one, keeps a pass ledger";
audit §5.
Applies to: projects with a review command.

## 2026-10-15 · review-prints-what-follows

What: the commit command hands over the review command alone. The fix-round
prompt or the merge command is the review's to print at its end; a `NEXT.md`
written at the commit is for the step after the review and its fixes, and
says so.
Check: checklist — "The commit command, after a task's last commit"; audit §5.
Applies to: projects whose commit command hands the review over.

## 2026-10-15 · state-table-frame-events

What: the testing skill's transition table gives the frame around the state
its own rows — closed, opened again, asked to open while open, remounted —
each while a call is still in flight, saying where that call's outcome lands;
a reset by remount (a new `key`) discards it.
Check: checklist — "Fixing review findings"; audit §5.
Applies to: every project with a testing skill.

## 2026-10-15 · fold-unpushed-fixes

What: a fix to a commit no remote holds yet — a review finding, or a bug a
fix round brought in — goes into that commit (`--amend`, or `--fixup` and
`--autosquash`; a conflicting rebase is aborted and the fix is a new commit),
a pushed one takes a new commit; the commit command and the
commit conventions allow it, and the review command reads a head rewritten
that way as `git diff <last head> HEAD`.
Check: checklist — "A fix to a commit not yet pushed"; audit §6.
Applies to: projects with a commit command or commit conventions.

## 2026-10-15 · commit-skips-validated-gate

What: the commit command does not run the gate again when the session ran it
green after its last edit and the commit takes the whole diff; it names that
run and commits.
Check: checklist — "Deterministic layer"; audit §6.
Applies to: projects whose commit command runs the gate.

## 2026-10-17 · work-prefix

What: the plugins are `work-bootstrap`, `work-jira` and `work-estimation`,
from the `mluk-work-agent-tools` catalogue at
github.com/maximlukyanovich/work-agent-tools; a project names them and their
commands by these names.
Check: `.claude/settings.json` enables each plugin as
`<plugin>@mluk-work-agent-tools`; every plugin command the project's own files
name — `AGENTS.md`, commands, skills — starts with `/work-`.
Applies to: every project set up before 2026-10-17.

## 2026-10-18 · next-step-at-a-stop

What: a command that stops early and sends the developer to another command —
a dirty tree to the commit command, a missing docs update — also prints that
command as a code block ready to paste, with the target the work needs;
naming it inside a sentence is fine, the block is what the stop must not lack.
Check: checklist — "Every command ends with its next step"; audit §6.
Applies to: every project with its own commands.

## 2026-10-18 · onboarding-installs-plugins

What: the settings declare every marketplace `enabledPlugins` names, the
library's with `autoUpdate`, and the onboarding command installs the declared
plugins a checkout lacks — at local scope, on a yes, leaving one turned off
here alone and without adding a marketplace by hand — prints `AGENTS.md`
§2's commands as code blocks, and lists the plugins' commands from their
files, `help` included.
Check: checklist — "The plugin set is recorded" and "The onboarding command";
audit §13.
Applies to: every project with an onboarding command or enabled plugins.

## 2026-10-18 · worktree-compose-project

What: the command that starts a task in a worktree gives a Compose stack
there its own `COMPOSE_PROJECT_NAME` beside its port, so `up` in the
worktree does not recreate the main tree's containers. The name goes into
the `.env` beside the compose file (or the file `--env-file` names), which
Compose reads for its own variables — a service's `env_file:` does not set
it — and a file carrying the port or the name is copied into the tree, not
linked, since a value written through a link lands in the main tree's file.
Check: checklist — "The command that starts a task takes an optional
`worktree` argument"; audit §8.
Applies to: projects that run a Compose stack and start tasks in worktrees.

## 2026-10-21 · review-focus-leaves

What: the review command's rubric checks UI for an element that holds the
focus and leaves the page outside a modal's focus scope with nowhere named
for the focus to go, since the browser drops it to `<body>` — a `nit`,
`minor` only when a keyboard user loses their place in a flow under way. The
rule itself is written at planning time, as a row of `kickoff`'s state table.
Check: templates — the review command's rubric additions; audit §5.
Applies to: projects with a review command and a UI.

## 2026-10-21 · review-close-ready-range

What: when a review reads ready and stops because findings grew on a small
delta, and the growth is `missed` findings in code older than the delta, the
first option it offers is to close the range — one fix round on the open ids,
then a pass over that round's delta alone, listing minor and above — instead
of another full pass.
Check: templates — the review command's "Stop and ask"; audit §5.
Applies to: projects with a review command and a pass ledger.

## 2026-10-24 · gate-once-per-tree

What: between edits, in a commit and after a sync, the project's commands
run the targeted checks of the changed paths — a profile row per path class
whose command really narrows, tried once — and the full gate only for a path
no row covers; the review runs the full gate in the background on its head,
the merge command before the push, and every command skips a tree already
recorded green. A gate of several parts skips a part whose content is
unchanged since its last green run; timeouts under load are rerun alone
before the gate is called red.
Check: checklist — "Deterministic layer" and "The gate is fast"; audit §6.
Applies to: projects with a commit or review command.

## 2026-10-24 · review-delta-ready-ships

What: a delta pass of the review command writes out a `missed` finding in
lines the delta does not change only at `major` and above, and counts the
rest in its opening block and the ledger; a cheap and real minor or nit is
marked `fix-now`, and the other minors and nits do not hold the merge. A
ready verdict hands over the merge command first and, when there are
`fix-now` ids, the fix prompt for them second; closing a ready range offers
the same. After the first pass, the commit command hands over the review
from the last reviewed head, never `<base>..<head>`.
Check: checklist — the review command, the commit command handing the
review over, "Every command ends with its next step"; audit §5.
Applies to: projects with a review command and a pass ledger.

## 2026-10-24 · fix-commit-layout

What: the first round of review fixes is one new commit on top of the
series, and every later round goes into that fix commit while it is unpushed
— amended, or folded with `--fixup`; the series' own commits are not
rewritten for a review fix. Any other fix to an unpushed commit still goes
into the commit it corrects.
Check: checklist — "A fix to a commit not yet pushed"; audit §6.
Applies to: projects with a commit command or a commit-conventions skill.

## 2026-10-24 · fix-round-by-risk

What: the testing skill carries the fix round — a budget in proportion to
the findings that limits the measures added on top, never the fixes; the
narrow fix, a structural one asked first; proof by risk, a test for money,
data written or deleted, access, merges, what lets a confirmation through
and branching logic, a recorded live check for the rest, and a run on the
old code only for a test that may pass by coincidence; one read of the
round's diff for side effects. The review rubric follows: a missing test is
`major` only in a risk class. The fix prompt names the skill's fix round.
Check: checklist — "Fixing review findings is a rule in `AGENTS.md`"; audit
§5.
Applies to: projects with a testing skill or a review command.

## 2026-10-24 · next-step-nearest

What: a command's report and its first block name the same, nearest step: a
commit still to make is the commit command as a block, and the review
command comes only after the task's last commit. A finished slice ends with
blocks to commit, to continue after `/compact <focus>`, or to continue in a
fresh session.
Check: checklist — "Every command ends with its next step"; audit §6.
Applies to: every project with its own commands.

## 2026-10-24 · efficiency-journal

What: the project keeps `docs/local/efficiency-remarks.md`, and one line in
`AGENTS.md` §6 says that a remark from the developer about the agent's
speed, cost or quality of work goes there as a row in the same session. The
audit reads the rows in either mode: a project cause becomes a finding, a
library cause one depersonalised issue draft, filed only on an explicit yes.
Check: checklist — "`docs/README.md` and `docs/local/README.md` exist";
audit §14.
Applies to: every project.

## 2026-10-25 · proof-silent-break

What: the testing skill's proof by risk adds the class of breaks where
nobody looks — the request a page assembles, what lets a key, a tap or a
submit reach an action, a contract of shared code, a path the local check
cannot reach — under one condition: the break costs data, access, a merge or
a payment, or leaves the user stuck. It says what a test asserts (the
decision, not the look or a mock's answer), which existing tests an audit
removes and which stay, and that a test of a code convention is left to the
convention. The review's `test` lens grades by it: a missing test, a removed
or weakened guard and a document claiming coverage its test does not assert
are `major`; the same gap in untouched code is `minor` at most, for
techdebt; a test of the look is a `nit` to remove.
Check: checklist — "The testing skill proves by risk"; audit §5.
Applies to: projects with a testing skill or a review command.

## 2026-10-25 · test-audit-by-risk

What: the audit sorts the project's tests by what they prove, with a second
reviewer that never sees the first pass's sorting; reads each test file's
history; measures what the suite costs to run; puts untested risk-class code
first; and turns a defect it finds into a task of its own. It is asked, with
its price, before it runs.
Check: audit §15.
Applies to: projects with tests.

## 2026-10-25 · review-findings-placed

What: the review report gives every `minor` and `nit` that is not `fix-now`
its place at once — a techdebt row (what breaks, who sees it, the priority)
or `deferred (accepted: <reason>)`; a security finding goes only to
techdebt, or where the developer's word puts it. The ledger records the
place as the status, the fix round writes the techdebt rows with its fixes,
and after a merge the handoff names only a finding without a place instead
of the open ones.
Check: checklist — the review command, "Fixing review findings is a rule in
`AGENTS.md`"; audit §5.
Applies to: projects with a review command and a pass ledger.

## 2026-10-25 · ready-fixes-first

What: a ready verdict with `fix-now` ids open, or techdebt rows to write,
hands over the fix round first; the round's commit hands over the review of
its delta, and that review the merge. The merge command comes first only on
the developer's word to ship now; without such ids, the merge as before.
Supersedes: review-delta-ready-ships — the order of a ready verdict and of
closing a ready range (the merge first, the `fix-now` round second).
Check: checklist — the review command, "Every command ends with its next
step"; audit §5.
Applies to: projects with a review command and a pass ledger.

## 2026-10-27 · library-pin

What: the settings that declare `mluk-work-agent-tools` either follow `main` —
every raised plugin version arrives through `autoUpdate` — or pin a release
tag with `ref` inside `source`, beside `autoUpdate`; a team pins, and moving
to the next tag is a reviewed settings change that the next session start
applies. The marketplace is never added by hand: an add replaces the
declared source, its `ref` included. A pin holds only on a machine whose
user settings do not declare the marketplace, and a pinned project updates
through `autoUpdate` in its own session.
Check: checklist — "The plugin set is recorded where Q10 put it"; audit §13.
Applies to: every project; the audit asks once, and a project that follows
`main` changes nothing.

## 2026-10-29 · plan-loads-testing-skill

What: the command that starts a task loads the project's testing skill before
it writes the plan, not only before the first edit: the skill's proof by risk
sets the plan's verification, and its state lists — a write while another is
in flight, data out of date while a re-read runs — become rows of the state
table. It loads the skill again before the first edit when the plan was
approved in another session.
Check: checklist — "The command that starts a task, when a tracker is
reachable, offers the opening steps"; audit §8.
Applies to: projects with a task command and a testing skill.

## 2026-10-29 · gate-part-reads

What: a gate part's content is everything its tool reads — its own globs, the
files they import and the files they read from disk. A path leaves a part only
by a probe named in a comment beside the rule — a command such as
`tsc --listFilesOnly`, or a search for imports and disk reads in the part's
files — never by the tool's configuration; in doubt the path stays.
Check: checklist — "The gate is fast"; audit §6.
Applies to: projects whose gate has several parts that skip by content.

## 2026-10-29 · measure-at-scale-one

What: a browser measurement first checks that `window.devicePixelRatio` is 1
and stops when it is not: the browser keeps a zoom level per host, which
device-metrics emulation does not reset; the same server under another host
(`127.0.0.1` for `localhost`) opens at 1.
Check: checklist — "With a design source"; audit §11.
Applies to: projects with a design source whose task measures in a browser.

## 2026-10-29 · change-size-tier

What: the task command names the change's level on its first line — small
(prose, or a change that keeps behaviour, within the thresholds
`change_size.py` checks, in no risk class of the testing skill), normal, or
critical (money, access, a migration, deleted data). A small change gets a
short plan in chat and the developer's yes instead of the questionnaire and
plan mode, and its review and merge run in the same session; a critical
change's review runs only in a fresh session. The developer may raise the
level, the agent never lowers a critical one, and the handoff measures the
diff and raises a small change that outgrew its thresholds.
Check: checklist — the task command and the review command items; audit §8.
Applies to: every project with a task command.
