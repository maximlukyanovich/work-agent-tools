# Templates — A command that reviews: ledger, procedure, rubric, groups

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
carries `fix-now` after its class. Status: `open`, `fixed`,
`deferred (<techdebt file, section>)`, `deferred (accepted: <reason>)`,
`false-positive (<mechanism>)`, `disputed`. Every other `minor` and `nit`
gets one of the two `deferred` places in the pass that raises it, and none
is `open` at the merge (step 5). By default only `Trajectory` and
`Open` are read; pass sections are appended, never rewritten. The command
writes the ledger itself, without asking — a ledger that waits for a human to
update it stays empty.

**The procedure the command carries:**

1. **Target from the ledger, by a script.**
   `python3 scripts/review_target.py --ledger <ledger file> --tree <tree>`, plus
   `--full` or `--range <a>..<b>` from the arguments, prints the mode, the
   diff and the reason — a copy of
   `${CLAUDE_PLUGIN_ROOT}/templates/review-target/review_target.py`, its
   header the contract. `none` → no new pass; print the recorded verdict.
   `whole` → the whole target; any other mode → the diff it prints, and for
   `rewritten` — the fixes went into the reviewed commits
   (`review-fixes.md`) — the pass header names the `replaced` ones. An
   explicit range, the way to review follow-up fixes after the original MR
   was merged, outranks the ledger and `full`.
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
   `fix-now`. Every other `minor` and `nit` gets its place in the same
   report: a row for the project's techdebt file — what breaks, who sees it,
   the priority — or `deferred (accepted: <reason>)`; a `security` finding
   goes only to techdebt, or where the developer's word puts it. The ledger
   records the place as the status, the developer's word overturns it, and
   the fix round writes the techdebt rows. These do not hold the merge, and
   none stays `open` past it: the ledger lives outside git, by branch, so an
   `open` is lost after the merge, and the next task's planning sees only
   techdebt with a priority.
   Observed on a live project: eight passes over one branch, each full one
   finding ten to twenty-two old minors and nits, while the only delta pass
   found three. Stop and ask what a further pass should add when it is
   pass 3+ with no new commits, when findings grew while the delta is small,
   or when `escalated` plus `fix-critique` exceed half the findings. A ready
   verdict with `fix-now` ids open, or techdebt rows still to write, offers
   one fix round on them first, a pass over that round's delta alone next,
   and the merge last; without them, the merge. The merge goes first only on
   the developer's word to ship now: a fix in the same unmerged branch is one
   commit, one delta and one MR, and after the merge it is a new branch, an
   MR, CI and a review. When the verdict reads ready and the growth is
   `missed` findings in code older than the delta, the range closes that way
   — not with another full pass, which on a large range finds a fresh batch
   of old nits every time.
6. **Append the pass.**
7. **Hand the next step over** through `/work-bootstrap:handoff`. An open
   `blocker` or `major` → a prompt for the fix round naming the pass, the ids, the
   ledger's path, the plan and the target — never the report: the fix
   session reads the ledger. Ready closes the range, not the task: first read
   the plan and the task's notes — work the branch has not done yet makes the
   block "continue the task" (`Read <NEXT.md> and continue`, or the plan's
   next step), and the merge waits. The task done → with `fix-now` ids open
   or techdebt rows to write, the fix prompt for them: the round's commit
   hands over the review of its delta, and that review the merge. Without
   them, the merge command with the target. The merge command comes first
   only on the developer's word to ship now.
   Observed on a live project: a clean repeat pass in the middle of a task
   would have printed the merge command with two slices and the live check
   still ahead.

**The rubric additions that repeated passes showed were missing:**

- Run the gate once on the target, in the background while the rubric runs,
  unless `python3 scripts/gate_record.py check <tree> --base <base>`
  (`--small` for a small change) says skip — with `full gate: ci`, the
  pipeline's status on the head instead, the commits' targeted checks not
  rerun ("The full gate runs once per branch"). A
  red gate is one finding; what the linter and the git hooks catch is not
  repeated as judgement.
- Async code and stateful hooks: walk the lifecycle transitions (A→B mid-event,
  A→none→A) and a misbehaving peer (a 200 that closes at once). Check a type's
  documentation against the code instead of trusting it.
- The `test` lens grades by the testing skill (`testing-skill.md`, "The testing skill
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
- Four questions for the classes human reviewers find most and a rubric
  rarely names. Pairs that must agree — read and write, display and submit,
  list and detail, create, edit and copy, every entry point to one action:
  a changed rule is checked in each. A new path beside an old one does
  everything the old did besides its main effect — signals and hooks, a
  cache or derived state reset, implicit validation, hints and required
  marks in the UI; a write past the model (`update`, a bulk operation) is
  the usual case. Empty is not unset — `0`, `""`, `[]`, a missing key — and
  a repeat — a double click, a retried job or webhook — does not repeat a
  side effect. New text — a log line, an error, UI copy — is true in every
  outcome: success, partial failure, timeout, the flag off.
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
diff, the report says so and recommends a rerun; it does not refuse. A small
change is reviewed in the same session and the report recommends no rerun;
a critical one stops there and prints the review command for a fresh
session ("The change sets the process"). And on a
frozen range: while the branch's findings have a fix round open, no new work
lands on it — the fixes, the repeat review, then the plan goes on. One tree,
one writer.
