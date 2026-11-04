# Templates — A command: skeleton, target, next step, the gate

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
  `cd <tree> && <gate>`; a record the commands share, such as the gate
  record, goes in that tree's own git directory
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
A small change is the exception (`task.md`, "The change sets the process"): its
phases stay in the session that started it while the handoff leaves it small.

### The full gate runs once per branch

The full gate costs minutes. Run after every edit and again by every command,
it makes a fix wait longer than the fix. Observed on a live project: the
commit command and then the review ran a six-minute gate on the same tree,
and an amend of six files took half an hour; on another, a half-hour task's
merge ran the full gate again after a review fix that had passed its
targeted checks. So the commands that commit, review, sync and merge share
one rule, and the record behind it is kept by the project's
`scripts/gate_record.py` — a copy of
`${CLAUDE_PLUGIN_ROOT}/templates/gate-record/gate_record.py`, its contract
`${CLAUDE_PLUGIN_ROOT}/reference/gate-record.md`:

- **Between edits, in a commit, after a sync — the targeted checks.** The
  profile names a row per path class with a command that really narrows:
  the linter on the changed files, the type-check, the tests related to them
  (`vitest related <files> --run`, one app's tests with `--keepdb`). A step
  runs the rows of the paths it changed; a path no row covers — shared
  configuration among them: the lockfile, the linter's, type-checker's or
  test runner's config — runs the full gate. With `full gate: ci` it goes to
  the pipeline instead: the step runs no full gate, and such a commit is not
  recorded. A filter that silently runs the whole suite is not a targeted
  check; it is tried once before it is written down. A commit whose every
  path had its row, green, on a clean tree after
  the commit, is recorded `targeted`. The paths are the whole commit's
  (`git show --name-only HEAD`): an amend counts what the commit already
  held, not only the round's. Several groups of one run are recorded after
  the last, with `--commits <n>`.
- **A hub file takes the tests of its areas.** The tests related to a file
  most of the code imports — the route registry, a shared config, shared
  types — are the whole suite. The profile's `hub files` lists such files; a
  change to one runs the tests of the areas whose behaviour the diff changes,
  by a path filter (`vitest run <dir>` keeps the test files whose path
  contains it), and leaves the whole suite to the branch's full gate: such a
  commit is not recorded `targeted`. Observed on a live project: `related`
  on a route registry ran 1749 tests beside a running dev server — timeouts
  and two reruns.
- **The full gate — once per branch.** The review runs it on the head it
  reads, in the background while the rubric runs; the merge command runs it
  before the push. Each first runs
  `python3 scripts/gate_record.py check <tree> --base <base>` and skips on
  `skip`, saying so: the head's tree passed it, or a run earlier on the
  branch did and every commit since is recorded. Every green full run on a
  clean tree is recorded `full`. A small change (`task.md`, "The change sets
  the process") checks with `--small`: its commits' targeted checks stand
  for the gate, and the review runs the full gate once only when a commit
  is not recorded: it touched a hub file, or an amend ran only its own rows
  over a path no row covers. Such a path otherwise ran it in its commit,
  recorded `full`.
- **Where the full gate runs is the project's call** — the profile's
  `full gate`. `local`, and no key: as above. `ci`: the pipeline runs it on
  every merge request, and its status decides — no command runs it on its
  own, a commit whose paths all have rows still records `targeted`, and a
  local run `full`; the review reports the
  pipeline's status on its head and does not rerun the targeted checks —
  its commits ran them, and over a whole range "related" nears the whole
  suite; a head not yet pushed, or pushed with no merge request, rests on
  its commits' checks. The merge
  command waits for the pipeline — `gh pr checks
  --watch`, or `glab ci status --live` and then its status from
  `--output json` — and never merges on red or pending. A red pipeline is
  fixed by a new commit: the commit is already on the remote. Before the
  push the command offers the full gate locally as the second option, only
  with a reason — the diff touches what the targeted checks do not narrow
  (configuration, dependencies, hub files, the gate itself); the commits
  will still change (a review or a round of fixes ahead, an amend); the
  merge does not squash — with CI recommended, the local run's price (the
  gate's measured time) and its gain (an amend instead of a fix commit, a
  pipeline that stays green). No reason, no question.
- **Red under load is not red by code.** When only timeouts fail while the
  machine is busy, the failing files are rerun alone, and both runs and the
  load are reported. A dev server or stack the session started is stopped
  before a test run wider than a few files; one the developer runs is named
  in the report.
- **A gate of several parts picks them by content.** A part whose content is
  unchanged since its last green run is skipped — a fingerprint of the part's
  tree, kept in the git common directory so every worktree shares it, taken
  before and after the part's checks and recorded only when the two match,
  since a file edited during the run was checked in its new state — and
  `--all` runs everything. A part's content is everything its tool reads:
  its own globs, the files they import and the files they read from disk —
  tests read the stylesheets and the static assets. A path leaves a part
  only by a probe named in a comment beside the rule — a command
  (`tsc --listFilesOnly`) or a way to look (a search for imports and disk
  reads in the part's files) — never by the tool's `include` or ignore
  configuration. In doubt the path stays: an extra path costs a rerun of
  the part, a missing one a false green. Observed on a live project: three
  findings of one audit were a part narrowed by its tool's `include` while
  its files imported or read the excluded paths. Tests run in parallel only
  where they share no outside state: tests that write a Redis-backed config
  the dev stack also reads race each other's restore and leave the stack's
  value changed. The linter keeps a cache when no rule needs type
  information, the type-check is incremental; CI runs without these caches.

**`model:` in a command's frontmatter** switches only the turn the command
runs in: the session's model is back with the next prompt, and that turn
re-reads the whole context uncached — each model has its own cache. So it
pays only on a command that runs in one turn without a question, in a fresh
session; never on commit, review or merge, whose first question ends it.
