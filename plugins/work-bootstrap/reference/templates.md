# Templates

Skeletons only. Every example inside a skill or command is written for **this**
project's domain — carrying someone else's examples over is an anti-pattern.

## AGENTS.md

Seven sections, in this order. Anything a linter already enforces is marked
`[lint]` and not explained twice.

```markdown
# Agent instructions

## 1. Project        what it is, which surfaces, current phase
## 2. Commands       install, dev, the one gate command, tests, build
## 3. Architecture   layers table: path, responsibility, what it may import
## 4. Conventions    language, branches, commits, styling, copy
## 5. Sources of truth   priority order, and what to do on conflict
## 6. Working agreements  the rules that are not machine-checkable
## 7. Agent tooling   commands, skills, deterministic checks, hooks
```

Rules that keep it cheap: no rule appears twice; anything expressible as lint
configuration is a one-line reference, not a paragraph; the absence of a layer is
recorded deliberately, with its reason.

§6 carries one line for the efficiency journal: a remark from the developer
about the agent's speed, cost or quality of work goes as a row into
`docs/local/efficiency-remarks.md` in the same session — date, task, the
quote, context, a link, no judgement; `/work-bootstrap:audit` reads it.

A generator may have written some of these files first — `create-next-app`
writes `AGENTS.md`, most generators a `.gitignore`. They are
extended, never rewritten, and a block the generator marks as its own stays
where it is: the framework may write it back, and from then on the tree is
dirty. The stack's recipe in `reference/scaffold/` names the block.

With pnpm 11, §2 says next to how a dependency is added that one with a build
script — direct or transitive — needs an `allowBuilds` entry in
`pnpm-workspace.yaml`. A missing entry fails the install with
`ERR_PNPM_IGNORED_BUILDS`, but only a clean one: a warm `node_modules` hides
it, and the first to see it is the server. The file's header gives each entry
its reason and says to prove a new dependency with
`pnpm install --frozen-lockfile` on a fresh checkout.

## README.md — Deployment

Once the project runs anywhere but a developer machine, the root README has a
Deployment section. Whoever sets up the server reads README, not `AGENTS.md`,
and a deployment guessed from `dev` ships the dev server.

```markdown
## Deployment

`<dev command>` is for local development only. A server runs:

    <install from the lockfile, frozen>
    <build>
    <start, with the port>

- Versions are pinned: <runtime> (<file>) and <package manager> (<field>);
  how a stock image gets them.
- <VARIABLE>: which steps need it — build, start or both — and whether it is
  baked into the bundle or read at start. What it means → <env example>.
```

Every line is proven on a fresh checkout without a local env file before it
is written: a variable the build validates at import is invisible on the
machine that has one.

## CLAUDE.md

```markdown
@AGENTS.md

# CLAUDE.md

Project rules live in AGENTS.md, imported above. This file holds only what is
specific to Claude Code and written nowhere else — deleting it must not lose a
single project rule.
```

## SKILL.md

```markdown
---
name: <name>
description: <what it covers, and when it applies — the sentence that decides loading>
---

# <name>

## When it applies
## How to do it
## How not to do it
## How it is verified
```

The `description` is the whole loading mechanism. Vague means either never loaded
or always loaded.

## A command

```markdown
---
description: <one line, shown in slash-command completion>
argument-hint: '[<arg>]'
---

# /<name>

## Steps
## Hard rules      what this command must never do
```

Read-only unless stated otherwise. No implicit push, merge or issue creation;
permission applies to the current turn only.

### A command acts on a target, wherever it is checked out

Work in a worktree should not need a second editor window. So the commands
that commit, review and merge take an optional target — a branch or a
worktree path — and run there from the main workspace:

- **Recognise it by shape.** An existing directory is a worktree; a name that
  `git rev-parse --verify` resolves is a branch, and
  `git worktree list --porcelain` says where it is checked out.
- **Run there.** Every git call as `git -C <tree>`, the gate as
  `cd <tree> && <gate>`; a record the commands share, such as a validated
  tree, goes in that tree's own git directory
  (`git -C <tree> rev-parse --git-dir`).
- **A branch checked out nowhere** has no tree for the gate: the review reads
  it by refs and reports the gate as not run; commit and merge stop and say
  which worktree to create.

### A command ends with its next step

A report that ends on "done" leaves the next step to memory, and it is
skipped exactly when the work went well. So every command ends with what
comes next as a code block ready to paste, one block per option. So does a
step that stops early and sends the developer to another command — a dirty
tree to the commit command: that command is also given as a block, with the
target the work needs. Naming it inside a sentence is fine; what the stop
must not lack is the block. A next step that is an answer in this session —
a choice of closing steps — stays a question; a commit still to make is the
commit command as a block, with its target. The text and the first block
name the same step, the nearest one: while a commit or another step of the
task is ahead, the block is for it, and the review command comes only after
the task's last commit, with its head known.

At a phase boundary — a task's last commit, a review, before and after a
merge — the block is for a fresh session and comes from
`/work-bootstrap:handoff`: the session that did the work is the most
expensive place for the next phase, and a review must not run there at all.

### The gate runs once per tree

The full gate costs minutes. Run after every edit and again by every command,
it makes a fix wait longer than the fix. Observed on a live project: the
commit command and then the review ran a six-minute gate on the same tree,
and an amend of six files took half an hour. So the commands that commit,
review, sync and merge share one rule:

- **Between edits, in a commit, after a sync — the targeted checks.** The
  profile names a row per path class with a command that really narrows:
  the linter on the changed files, the type-check, the tests related to them
  (`vitest related <files> --run`, one app's tests with `--keepdb`). A step
  runs the rows of the paths it changed; a path no row covers — shared
  configuration among them: the lockfile, the linter's, type-checker's or
  test runner's config — runs the full gate. A filter that silently runs the
  whole suite is not a targeted check; it is tried once before it is written
  down.
- **The full gate — once per tree.** The review runs it on the head it reads,
  in the background while the rubric runs; the merge command runs it before
  the push. Every green full run on a clean tree records the tree —
  `git rev-parse HEAD^{tree}` into `validated-tree` in that tree's git
  directory — and every command skips a recorded tree, saying so.
- **Red under load is not red by code.** When only timeouts fail while the
  machine is busy, the failing files are rerun alone, and both runs and the
  load are reported.
- **A gate of several parts picks them by content.** A part whose content is
  unchanged since its last green run is skipped — a fingerprint of the part's
  tree, kept in the git common directory so every worktree shares it, taken
  before and after the part's checks and recorded only when the two match,
  since a file edited during the run was checked in its new state — and
  `--all` runs everything. Tests run in parallel only where they share no
  outside state: tests that write a Redis-backed config the dev stack also
  reads race each other's restore and leave the stack's value changed. The
  linter keeps a cache when no rule needs type information, the type-check
  is incremental; CI runs without these caches.

**`model:` in a command's frontmatter** switches only the turn the command
runs in: the session's model is back with the next prompt, and that turn
re-reads the whole context uncached — each model has its own cache. So it
pays only on a command that runs in one turn without a question, in a fresh
session; never on commit, review or merge, whose first question ends it.

### The onboarding command

The project's start command is the first a newcomer runs, often in a clone
where nothing is installed yet. Committed `enabledPlugins` turns a plugin on
in every clone but downloads nothing, and trusting the folder only registers
the marketplaces the settings declare — so the settings declare every
marketplace `enabledPlugins` names: `mluk-work-agent-tools` from GitHub with
`autoUpdate`, so a library change reaches every clone on its own, and
`claude-plugins-official` when its plugins are on (an interactive first start
adds that one on its own, a profile used only from the CLI lacks it):

```json
"extraKnownMarketplaces": {
  "mluk-work-agent-tools": {
    "source": { "source": "github", "repo": "maximlukyanovich/work-agent-tools" },
    "autoUpdate": true
  }
}
```

The command then:

- **Installs what this checkout lacks.** It reads `enabledPlugins` and one
  `claude plugin list --json`, cut to `id`, `scope`, `enabled`,
  `projectPath`, `installPath` before it is read. An install counts when its
  scope is `user` or `managed`, or its `projectPath` is this checkout or
  another checkout of the same repository — the same
  `git rev-parse --path-format=absolute --git-common-dir`. A declared plugin
  with no install that counts is missing; one whose installs all have
  `enabled: false` is turned off here — a personal switch, left alone. The
  missing ones are installed on a yes with `--scope local` — the settings
  already turn them on, and a project-scope install writes into the
  committed `settings.json` — then `/reload-plugins` and the start command
  again, each as a code block. A plugin whose marketplace this machine does
  not know (`claude plugin marketplace list --json`) is not installed: a
  declared marketplace is registered by starting Claude Code at the
  repository root and trusting the folder, an undeclared one goes under
  `extraKnownMarketplaces` first. Neither needs
  `claude plugin marketplace add`, and at two scopes it does harm:
  `--scope local` replaces the committed entry and drops its `autoUpdate`,
  `--scope project` rewrites the committed `settings.json`.
- **Prints how to run the project** — the commands of `AGENTS.md` §2,
  verbatim, as code blocks ready to paste, from the repository root.
- **Lists the commands from their files** — the project's from
  `.claude/COMMANDS.md`, each enabled plugin's from the `description` line
  of `<installPath>/commands/*.md`: a command with
  `disable-model-invocation`, such as `help`, is missing from the session's
  own list.

### A command that starts a task must offer the opening steps

The status of an issue is the only thing the rest of the team sees of work
that has not shipped. A task started without moving it reads as untouched
for days — and the move, left to memory, is the step that gets skipped. So
when the profile names a tracker the agent can reach (an MCP server or the
plugin's script), the command that starts a task (`/task` or its equivalent)
asks **one question**, once the issue is read and before the branch is cut:

- **the transition to the workflow's in-progress status**, chosen from the
  transitions the tracker offers for that issue, never a guessed id;
- **the assignee**, when the issue has none;
- **the parent story or epic**, when it still sits in a to-do status.

Carry the state into the question — «Backlog, assigned to you, story still in
Backlog» — and do only what is answered. When the project keeps a waiting
list of posted questions (`work-jira`), name this issue's open
ones in the same message: an unanswered question is often why the issue is
still open. Hour buckets and issues already in
progress are left alone. With no reachable tracker the step is skipped and
said so in one line, not silently.

The same command loads the `kickoff` skill before its first question to the
developer: the questionnaire rules live there, and a command that asks
without them drops the closing "anything to add?". And once the plan is approved,
before the first production edit, it names the project's skills for
placement, components and tests to load: skills match on context
unreliably, and the rules they carry are the ones a review finds broken. Its
plan carries the sections `kickoff` names — the state table, the framework
behaviour with file:line, the line on the structural option.

### A command that starts a task can open it in a worktree

A task may start while the main working tree holds other work, and switching
that tree away from it risks the work. So the command that starts a task
takes an optional `worktree` argument, and offers one itself when its branch
check finds the tree busy — dirty, or a feature branch with work in flight.
On a free tree a worktree only adds setup, and is not offered.

- **Read the state live.** A `git status` captured when the session started
  can be hours old; the check runs it again before deciding.
- **Beside the repository**, `../<repo>-<key>`, never inside it: the main
  tree's linters, tests and type-check would pick up a nested copy. The
  folder is confirmed with the branch name.
- **Link what git ignores but the work reads** — local notes, env files (one
  that takes the tree's own port or Compose project name is copied instead,
  see below), tool configs — listed from the main tree's ignored files and
  confirmed. A folder tracked for one file (a README) is linked entry by
  entry, not whole. Then install dependencies in the new tree, and run the
  framework's type generation when its generated types are ignored —
  without them a fresh tree fails its type-check on the route types.
- **Its own port, for the dev server and for end-to-end tests.** A second
  dev server needs a free port, and so does an end-to-end run: a runner that
  reuses an already running server would otherwise test the main tree's code
  on the default port, and pass. A Compose stack also gets its own
  `COMPOSE_PROJECT_NAME`: under the main tree's name, `up` in the worktree
  recreates the running containers with the worktree's code. The port goes
  into the env file the dev server reads, the name into the `.env` beside the
  compose file (or the file `--env-file` names) — Compose takes its own
  variables from there, never from a service's `env_file:`. Either file is
  copied from the main tree, not linked, since a value written through a link
  lands in the main tree's file. What the compose file names outright is the
  same for both stacks even then, and collides or is shared: a host port, a
  `container_name`, a network or volume with its own `name:` or marked
  `external`.
- **A worktree is temporary.** The command that merges removes it with its
  branch (closing steps below); a folder deleted by hand leaves a stale entry
  that `git worktree prune` clears.

### A project with a design source holds to it

When the project implements a design, its component skill (or equivalent)
carries these rules; they are where a review finds drift.

- **A value off the design's scale extends the scale.** A size, radius or
  spacing the design draws between two steps becomes a new token rather than
  a silent snap to the nearer one — even a 1 px difference is visible across a
  product. The deviation goes into the project's register and to the
  designer, in the result comment's "for the designer to confirm" block.
- **Nothing the design does not draw is invented** — a control, a state, a
  piece of copy. It becomes a question; a placeholder is tolerated only while
  the question is open and only if the task report names it.
- **Know which copy is the source.** A design export can carry the same
  component twice — the files the screens import and an older bundled copy.
  Before reading, establish which one the rendered screens actually use, and
  write it into the project's design-source document; a whole pass was once
  briefed from the stale copy.
- **The sources take precedence over a screen.** The design's guide, its
  component sources and its tokens are what the code follows. A screen that
  disagrees with them is escalated to the developer, not settled by the
  agent — and the escalation names the likely reading: a designer who
  updated the screen and not the sources usually means the screen as the
  final decision. Whatever the developer decides goes into the project's
  register, and the designer gets the gaps together, in one comment asking
  for the sources to be brought up to date — not a question in every task.
- **Every state from the source, read each time.** Hover, focus, pressed,
  selected, disabled, invalid, open, loading — and the design's global
  stylesheet (link and title hovers, the focus ring, scrollbars) — are part
  of the component as much as its size. Before implementing or changing a
  component, open its source in the design and the global CSS and carry
  every state over as written; never fill a state in from memory, from the
  library the component is built on (a stock focus ring, a hover wash), or
  from a similar component. A state the design does not draw is a
  question, not a default.
- **Every load shows something.** Wherever something loads — a page, a
  history, a list, a search, an image, an upload, a retry, a reconnect —
  decide what is on screen until it arrives and while it is slow. Designs
  draw few of these; when the design is silent, it is a question for the
  designer, with a placeholder built from existing primitives (a skeleton,
  an inline spinner) named in the task report — never a blank area.
- **Real content, not the mock's.** A design's data is short and tidy; real
  names run six lines, prices carry two currencies, lists come empty or long,
  and the layout gets a narrower width than the mock. Lay out for that within
  the design's rules — clamp what can grow, keeping the full text reachable;
  wrap what must wrap; check the narrow widths. This is the team's to solve,
  not a question for every case, and it is work the design did not contain:
  the result comment names it, so it counts toward time over the optimistic
  estimate.
- **The task report lists deviations from the screen**, one row each: the
  design's value, the code's, why, and whether the designer has seen it.
- **A measurement, not an eyeball.** A project script compares the computed
  styles of the design's screen with the app's at the target viewport and
  prints the elements that differ with their values. It runs during the
  task's browser check, before review, and the review command accepts a
  `layout` mode that runs it on the branch. The script is the project's; its
  contract — inputs are the two URLs and a list of selectors, output is one
  line per differing property — is what the commands rely on.

### A command that merges must offer the closing steps

Merging is the moment a task stops being visible. Whatever is not done in the
minute after it is done weeks later, from memory, against a branch nobody
recognises — or never. So a command that merges ends with **one question,
asked every time**, covering:

- **the result comment** on the issues the branch touched;
- **the worklog**;
- **deleting the branch**, locally and on the remote — and, for a branch
  checked out in a worktree, `git worktree remove` first;
- **anything the work raised for someone else** — a defect belonging to
  another team, a question for the designer. A question that gets posted
  goes on the waiting list, and one the merge answers is closed there.

All of these are optional and none is done unasked. The obligation is to
**ask**, not to do. Two rules make the question worth answering:

- **Carry the state into it.** «Log some time?» invites a shrug; «logged 0 of
  an estimated 8h, nothing logged today» gets an answer. Same for whether the
  issue already has a comment and where the branch still exists.
- **Never infer the hours.** Elapsed session time is not worked time. The
  developer names the number.

Merge without deleting the source branch, so deletion stays a decision and
not a flag. An unanswered step is reported as still open, never dropped
silently. After the closing steps, `/work-bootstrap:handoff` prints the start
of the next task for a fresh session.

### A command that reviews keeps a pass ledger

A review that starts cold every time drifts. Each pass re-derives severity,
raises what the last pass deferred, critiques the fixes the last pass asked
for, and cannot say whether its verdict agrees with the previous one. Over
repeated passes the finding count grows while the code barely changes. A pass
counter does not fix this; a ledger does.

**The ledger.** One file per reviewed target in the gitignored personal space,
by default `docs/local/reviews/<key>.md`. The key is the first of: the task key
in the branch name, the MR number (`mr-<n>`), the branch slug. An MR that
appears later is added to `Aliases:`; the file is not renamed.

```
# Review ledger — PROJ-12
Aliases: MR !34, feat/PROJ-12-orders-list
Trajectory: P1 a1b2c3d 0/2/5/5 changes · P2 e4f5a6b 0/0/1/2 ready
## Open
- R3 minor bug fix-now src/api/client.ts:114 — error body lost when it is not JSON
## Pass 2 — <date> — head e4f5a6b · base a1b2c3d · delta — ready to merge
- R9 minor fix-critique src/api/client.ts:83 — helper duplicated — open
```

Ids `R<n>` never change. A `minor` or `nit` worth fixing before the merge
carries `fix-now` after its class. Status: `open`, `fixed`, `deferred (<reason>)`,
`false-positive (<mechanism>)`, `disputed`. By default only `Trajectory` and
`Open` are read; pass sections are appended, never rewritten. The command
writes the ledger itself, without asking — a ledger that waits for a human to
update it stays empty.

**The procedure the command carries:**

1. **Target from the ledger.** The last reviewed head equals `HEAD` → no new
   pass; print the recorded verdict. The last head is an ancestor of `HEAD` →
   review the delta `<last head>..HEAD`. The last head is not an ancestor
   because the fixes went into the commits it reviewed (below) → review
   `git diff <last head> HEAD`, which the reflog keeps resolvable, and name
   the rewritten commits in the pass header; a last head the repository no
   longer has → the whole target. No ledger or `full` → the whole
   target. An explicit `<sha>..<sha>` argument overrides both — the way to
   review follow-up fixes on a branch after the original MR was merged — and
   a base that is no longer an ancestor reads the same way.
2. **Blind first.** The rubric runs without the ledger's findings — reading a
   previous verdict first anchors the new one. Above the delegation threshold
   the subagents never receive the ledger.
3. **Refute before keeping.** Every `blocker` / `major` is checked against the
   code for a guard or a caller that makes it impossible.
4. **Reconcile.** Each finding is tagged `new` (code after the last head),
   `missed` (older code, never raised — honest severity, marked as missed),
   `escalated` (a deferred finding raised higher — only with a named new cause),
   or `fix-critique` (aimed at a fix a previous pass requested). A recorded
   false positive is not raised again without a new mechanism. A finding whose
   mechanism a ledger already holds — this target's or another's — ends the
   report with one line proposing to move it upstream (the `layers` skill,
   "A finding that comes back"). On a delta pass, a `missed` finding in lines
   the delta does not change is written out only at `major` and above; the
   rest are counted in the opening block and the pass, not listed. They
   survived the passes that read them, and listing them is what kept a large
   range from converging. The first pass and `full` list everything.
5. **The report opens with the same block, every pass, zeros included** —
   the developer compares passes by it, and counts named in a sentence came
   and went between passes:

   ```
   **Review `<target>`, pass <N>.** <range>, <commits>, <files / lines>; uncommitted: <yes / no>
   Trajectory: P1 <head> <b/m/m/n> <verdict> → P2 <head> <b/m/m/n> <verdict>
   Outside the delta, not listed: <n> minor · <n> nit      ← delta passes only

   | blocker | major | minor | nit |
   |---|---|---|---|
   | <n> | <n> | <n> | <n> |

   **Verdict: <blocked / changes requested / ready to merge>.**
   ```

   The verdict follows from the table; the findings come after it, most
   severe first. A `minor` or `nit` that is cheap and real — a defect a user
   can meet or a statement that is wrong, fixed in a line or two — is marked
   `fix-now`; the other minors and nits stay open and do not hold the merge.
   Observed on a live project: eight passes over one branch, each full one
   finding ten to twenty-two old minors and nits, while the only delta pass
   found three. Stop and ask what a further pass should add when it is
   pass 3+ with no new commits, when findings grew while the delta is small,
   or when `escalated` plus `fix-critique` exceed half the findings. When the
   verdict reads ready and the growth is `missed` findings in code older than
   the delta, the first option offered is to close the range: the merge; the
   second, when there are `fix-now` ids, one fix round on them and a pass
   over that round's delta alone — not another full pass, which on a large
   range finds a fresh batch of old nits every time.
6. **Append the pass.**
7. **Hand the next step over** through `/work-bootstrap:handoff`. An open
   `blocker` or `major` → a prompt for the fix round naming the pass, the ids, the
   ledger's path, the plan and the target — never the report: the fix
   session reads the ledger. Ready closes the range, not the task: first read
   the plan and the task's notes — work the branch has not done yet makes the
   block "continue the task" (`Read <NEXT.md> and continue`, or the plan's
   next step), and the merge waits. The task done → the merge command with
   the target first, and the fix prompt for the `fix-now` ids as a second
   block when there are any.
   Observed on a live project: a clean repeat pass in the middle of a task
   would have printed the merge command with two slices and the live check
   still ahead.

**The rubric additions that repeated passes showed were missing:**

- Run the gate once on the target, in the background while the rubric runs,
  and skip a tree already recorded green ("The gate runs once per tree"). A
  red gate is one finding; what the linter and the git hooks catch is not
  repeated as judgement.
- Async code and stateful hooks: walk the lifecycle transitions (A→B mid-event,
  A→none→A) and a misbehaving peer (a 200 that closes at once). Check a type's
  documentation against the code instead of trusting it.
- The `test` lens grades by the testing skill (below, "The testing skill
  proves a change by its risk"). No test for a risk-class break — the last
  class under its condition — is `major`, unless the diff says why it cannot
  be tested, and so are a deleted or weakened test that guarded one and a
  document or a comment that calls a behaviour tested when its test does not
  assert the decision. The same gap in code the branch did not change or
  delete and made no claim about is `minor` at most, and its place is
  techdebt. Any other behaviour change whose live check the commit or the
  report records needs no test — a missing one is a `nit` at most — and with
  neither it is a `minor`. A test that asserts the look is a `nit`,
  "remove". Observed on a live project: a deleted guard of a break that had
  already happened once, and a document calling a fallback tested while its
  test skipped the readiness report the text relied on, were graded `minor`
  and `nit`, and would have gone to techdebt.
- A finding names every place with the same mechanism. The fix closes all of
  them, each with its proof — a fix for one site of a race routinely leaves
  its twin.
- UI: an element that holds the focus and leaves the page outside a modal's
  focus scope with nowhere named for the focus to go — the plan's state table
  names it (`kickoff`); the browser drops it to `<body>`. A `nit`; `minor`
  only when a keyboard user loses their place in a flow under way, such as a
  dialog or a form.

**Review groups run on the session's model.** Above the delegation threshold
the groups are where the diff is actually read, and the session's refutation
removes false findings but never recovers a missed one — so a group on a
weaker model costs exactly the defects a large diff is reviewed for. The
groups go to a project agent, `.claude/agents/review-group.md`, which
inherits the model the developer chose for the review session:

```markdown
---
name: review-group
description: Reviews one file group of a diff against the rubric in its prompt and returns anchored findings. Used by the review command; not for a whole review.
model: inherit
tools: Read, Grep, Glob, Bash
---

You review one group of files from a diff; the prompt gives the range, the
files and the rubric. Read-only: diffs, logs and files are read, nothing is
written. No ledger, no verdict — findings only, one line each: severity ·
class · file:line · the mechanism, or input → bad output. A `blocker` or
`major` without that anchor is written as a `nit`.
```

The review command takes `model=<name>` and passes it as the Agent call's
`model`, which outranks the definition — a one-off choice for a single run.
`inherit` is written out rather than left implicit: an omitted `model` falls
back to a default subagent model when one is configured. The synthesis, the
refutation of every `blocker` and `major`, and the ledger stay with the
session.

**Run it in a fresh session.** The session that wrote the code remembers its
own reasons and tends to confirm them. Everything a review needs from the past
is in the ledger. When the command runs in a session that edited files in the
diff, the report says so and recommends a rerun; it does not refuse. And on a
frozen range: while the branch's findings have a fix round open, no new work
lands on it — the fixes, the repeat review, then the plan goes on. One tree,
one writer.

**The commit command hands the review over.** After the last commit of a task,
or of a round of review fixes, its report ends — through
`/work-bootstrap:handoff` — with the review command ready to paste into a
fresh session. The command carries:

- the range — from where the branch left its base branch for the first pass,
  from the head the last pass reviewed after it. Never `<base>..<head>` once
  a pass exists: an explicit range outranks the ledger's delta, and a fix
  round of six files then gets a review of the whole branch — observed on a
  live project, a pass over 120 files that found nine old minors, which read
  as bugs of the fixes;
- what to skip — merge commits, other people's commits;
- one code block per branch;
- no prompt for what follows the review: the fix round or the merge is the
  review's to print at its end. A `NEXT.md` written now is for the step after
  the review and its fixes, and says so.

Left to the agent's memory, this step is skipped precisely when a task ends
well. Observed on a live project: a finished task was reported done with
commits, questions and a library merge request all proposed, and the review
was not. The rule was already a saved preference.

**A commit the hook refuses leaves its paths staged.** A `commit-msg` hook
that turns the message down — a header over the length limit, a missing task
key — stops the commit and keeps the index. The next `git add` adds to it,
and the next commit takes both groups. So the commit command, right before
`git commit`, compares `git diff --cached --name-only` with the list it
proposed and stops on a difference; after a refusal it fixes the message and
commits the same index again — it never stages the next group on top.
Observed on a live project: a header three characters too long left one
task's six files staged, the following commit for another task swept them in,
and the pair had to be split with `git reset --soft` before the push.

**A fix to a commit not yet pushed goes into that commit; review fixes go
into one fix commit.** A bug found while the work goes on, whose cause is a
commit no remote holds yet (`git branch -r --contains <sha>` prints
nothing), is fixed inside it:
`git commit --amend` when it is `HEAD`, otherwise `git commit --fixup=<sha>`
and `git rebase --autosquash <sha>~` — before git 2.44 a rebase without
`-i` ignores `--autosquash` and says nothing, so there it is
`GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <sha>~`. The message is
reworded when the fix changes what it says. A rebase that stops on a
conflict — a later commit changed the same lines — is aborted
(`git rebase --abort`) and the fix becomes a new commit: a conflict resolved
inside history the gate never sees again is how a fold breaks a commit. A
pushed commit takes a new commit, never a force push. A round of review
fixes is placed differently: the first round after a review is one new
commit on top of the series, and every later round goes into that fix commit
while it is unpushed — amended, or folded with `--fixup` when it is not
`HEAD`. The series' own commits are not rewritten for a review fix. A branch
merges with its history, and "fix", then "fix the fix" tells a later reader
nothing the corrected commit does not; the review's story is in the ledger,
which reads a rewritten head (step 1 above). So the push waits for the
review and its fixes, not the other way round. Observed on a live project: a
fourteen-commit branch carried five commits that only fixed its other
commits, after six review passes; and later, spreading one round of fixes
over four unpushed slices took blame by hunk, four reworded messages, a
partial staging the formatter hook mangled and a rebase that stopped on a
file every slice had touched.

**Fixing the findings has its own discipline**, and the review command cannot
enforce it: the fixes are made in a fresh session from the handoff's fix
prompt, where no command runs. So the rule lives where every session reads
it — one line in `AGENTS.md` — and points to the project's testing skill,
which carries the round:

- **a budget in proportion to the findings** — minutes for a document or a
  one-line fix, about twenty to thirty for a round on a small task; a round
  that will plainly take longer says why before it starts. The budget limits
  the measures added on top, never the fixes: every finding taken is closed,
  or named with what it waits on, and a measure that costs more than the
  fix — agents critiquing the plan or the delta, a batch of reverts, a
  repeated gate or build — is asked about with its price, never added by
  default;
- **the narrow fix** — a structural one (moving logic out, moving tests, a
  new convention) is a question first, with the narrow fix and a techdebt
  entry as the default; a fix that would need its own parser, protocol or
  format where the code already uses a library for the job takes the
  library; a mechanism the fix introduces covers every site of its class,
  not only the sites the finding named;
- **proof by risk**, by the skill's rule (below, "The testing skill proves
  a change by its risk") — a test in the same commit for a change in a risk
  class; a live check, recorded, for the rest. A test that may pass by
  coincidence — the focus, timing, a fake or a mock, an async step — is run
  once against the code it replaces and goes red there; an existing test
  that "covers the area" usually passes either way, and a plain input →
  output test needs no such run;
- **every state the fix touches**, not the one the finding named: a query's
  pending, error, and error **with stale data**; success that may be out of
  date — while a refetch is in flight, and while the cache still counts as
  fresh, so nothing is read again on mount; every mutation in flight, not
  the last; a stream before its history has replayed. A fix round that
  closes one state ships the next round's `major` in the state beside it;
- **a transition table before any edit to state**, a fix or not: state ×
  event → expected → proof, by the same risk rule. The
  states an edit touches are listed before the code, not found by the next
  review. The frame around the state has events too — closed, opened again,
  asked to open while open, remounted — and each gets a row while a call is
  still in flight, saying where that call's outcome lands. A reset by
  remount (a new `key`) throws away whatever the call would still deliver;
- **one read of the round's own diff** before the commit: what else does
  each change do — in which states, for which users of the element (mouse,
  keyboard, screen reader, another order of events)? A precedent is copied
  whole. A doubt in the reasoning — "if…", "probably…", "fine anyway" —
  becomes a row, a check or a report line; a changed sentence is reread
  whole, and a changed rule is searched for across the docs, the harness and
  the tests;
- **the proof handed back** before the commit is asked for, and shown by the
  commit command: one row per finding, or per transition of a state edit —
  the test (red on the old code where the rule asks for it) or the live
  check.

Observed on a live project: pass 2 found two new `major`s, both in states
the pass-1 fixes had touched and not enumerated, and both untested — the
testing skill held the rule already, and nothing loaded it. Later, a fix that
reworked a hand-over between two screens dropped a guard one transition
away from the one it fixed; a transition table lists that row. And a dialog
reset by remount on every opening lost a sign-in finishing behind a close:
the outcome reached an unmounted component, and the reopened card showed its
first step to a user the service had just signed in. Later still, 83 reverts
in a row went red and found nothing, while the defects the rounds brought —
five to seven each — were side effects of fixes that worked, which a revert
cannot see; that time now goes to the read of the diff.

**A merging command reads the ledger** before the merge: no pass on the
current head, or `major`+ still open → it says so and merges only on an
explicit yes.

**Cost.** The same head costs nothing; a delta costs a delta. The ledger is one
line per finding, not a copy of the reports. The rules live in the command
text, which loads only when invoked — not in `AGENTS.md` or a skill
description, which every session pays for.

### The testing skill proves a change by its risk

The project's testing skill holds the rule that the plan, the fix round and
the review's `test` lens all read, so it is written once:

- **The risk classes.** A change in one ships with its test in the same
  commit, and the test fails without the change: money; data written or
  deleted, and what decides which rows; access; a merge of records or
  accounts; what lets a confirmation through, or blocks it; logic that
  branches on its input; and what breaks where nobody looks — the request a
  page assembles (a field's name, a hidden fingerprint, the form a checkbox
  or a button belongs to, a `formaction`), what lets a key, a tap or a
  submit reach an action (above all one that deletes or charges), a
  contract of shared code other screens lean on (a lock taken and released,
  a queue that moves, a global flag reset, a fallback that never leaves the
  user stuck), a path the local check cannot reach (the exchange with a
  provider, a slow or failing network, a first visit, reduced motion,
  touch). The last class holds on one condition, on any screen: the break
  costs data, access, a merge or a payment, or leaves the user stuck; a
  break of the look alone is outside it. Any other behaviour is checked
  live, and the check is recorded.
- **What a test asserts** — the decision: the request sent, the handler
  called, the code or the status returned, a guarding attribute (`inert`,
  `form=`); not a class, the layout or a text, and not what a mock was told
  to return. Markup that assembles the next request is a decision, not the
  look.
- **An existing test** — an audit removes one that proves nothing, and one
  whose break the live check of the change itself would show, a break of
  the look alone among them. A test of a break that happens silently, or
  somewhere else, stays, even where a new change would not have required it.
- **A test of a code convention** — the module graph, the language of
  messages, the number of queries as the data grows — is a deterministic
  check, like a lint rule: the risk rule neither asks for it nor removes it,
  and it lives as long as the convention does.

Observed on a live project: a test audit that removed everything outside the
first six classes would have dropped about a dozen groups of frontend tests
and several backend ones that guarded silent breaks — an empty choice read
as the whole history, drafts overwritten without their fingerprints, a page
hold that leaked, a key reaching a delete button, a scroll lock in every
dialog — and a rule against checking HTML had pushed its first pass that way.

## .mcp.json.example

Servers with `${VAR}` placeholders, committed. A generator script substitutes
values from `.env` and fails loudly on a missing one — a partially substituted
config is worse than none: the server starts and authentication fails somewhere
far from the cause.

## Hook contract

A `PostToolUse` hook receives the tool call, exits **0 and silent** when the file
is outside its area, and prints an actionable message otherwise. Every hook has a
test. A hook that fires on ordinary edits gets ignored and then removed.

## Git hooks

- **Git hooks stay fast; the full gate does not go into one.** A gate that
  takes minutes in `pre-push` is bypassed within a week, and a bypassed check
  is worse than none. The full gate runs in CI, and before that in the commands
  that commit and push: the commit command runs it and records the tree it
  passed on (a file under `.git/`), and the push or merge command runs it again
  only when `HEAD`'s tree is not the recorded one — so the usual push costs
  nothing extra. The commit command does not run it a second time either:
  when the session ran it green after its last edit and the commit takes the
  whole diff, it names that run and commits. A gate of a few minutes, run
  twice on the same tree, makes every small fix cost minutes of waiting.
- **lint-staged: the linter's fixes first, the formatter last** —
  `['eslint --fix', 'prettier --write']`. The reverse order leaves the linter's
  edits unformatted while the hook reports success, and the gate fails a commit
  later.
- **An optional task-key check in `commit-msg`**, offered at setup. The key
  comes from the branch name (`<prefix>/PROJ-12-slug` → the subject must carry
  `PROJ-12`); a branch without a key, a detached `HEAD` and a merge commit are
  exempt, which is the way to work without a task. **commitlint keeps only one
  inline plugin**, and a second replaces the first — including the one a
  preset brings: `commitlint-config-gitmoji` ships its rule as an inline
  plugin, so even the first local plugin disables it and the config fails with
  "Found rules without implementation: start-with-gitmoji". Spread the preset's
  plugin rules into the one local plugin object together with your own.

## docs/local/README.md

The only committed file in the personal space. It states what lives there — local
specs, correspondence, estimates, task notes, the efficiency journal — and one
rule for the agent: this material is context, never a source of truth, and is
never quoted into committed content.

## docs/local/efficiency-remarks.md

The developer's remarks about how the agent spends time, tokens and care —
raw material for `/work-bootstrap:audit`, not decisions. Ignored with the
rest of `docs/local/`, written in the conversation's language:

```markdown
# Efficiency remarks

One row per remark about the agent's speed, cost or quality of work, in the
session it was made: the words as said and what happened. No judgement — the
audit draws the conclusions and fills the last column.

| Date | Task / phase | Quote | Context | Details | Analysed |
| --- | --- | --- | --- | --- | --- |
```

A row may name the project's issues and quote people: the file stays local.
What leaves it — an issue for the library — is depersonalised by the audit.
