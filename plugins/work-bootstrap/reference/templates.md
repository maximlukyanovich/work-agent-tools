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
Backlog» — and do only what is answered. Hour buckets and issues already in
progress are left alone. With no reachable tracker the step is skipped and
said so in one line, not silently.

The same command loads the `kickoff` skill before its first question to the
developer: the questionnaire rules live there, and a command that asks
without them drops the closing "anything to add?". And once the plan is approved,
before the first production edit, it names the project's skills for
placement, components and tests to load: skills match on context
unreliably, and the rules they carry are the ones a review finds broken.

### A command that merges must offer the closing steps

Merging is the moment a task stops being visible. Whatever is not done in the
minute after it is done weeks later, from memory, against a branch nobody
recognises — or never. So a command that merges ends with **one question,
asked every time**, covering:

- **the result comment** on the issues the branch touched;
- **the worklog**;
- **deleting the branch**, locally and on the remote;
- **anything the work raised for someone else** — a defect belonging to
  another team, a question for the designer.

All of these are optional and none is done unasked. The obligation is to
**ask**, not to do. Two rules make the question worth answering:

- **Carry the state into it.** «Log some time?» invites a shrug; «logged 0 of
  an estimated 8h, nothing logged today» gets an answer. Same for whether the
  issue already has a comment and where the branch still exists.
- **Never infer the hours.** Elapsed session time is not worked time. The
  developer names the number.

Merge without deleting the source branch, so deletion stays a decision and
not a flag. An unanswered step is reported as still open, never dropped
silently.

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
- R3 minor bug src/api/client.ts:114 — error body lost when it is not JSON
## Pass 2 — <date> — head e4f5a6b · base a1b2c3d · delta — ready to merge
- R9 minor fix-critique src/api/client.ts:83 — helper duplicated — open
```

Ids `R<n>` never change. Status: `open`, `fixed`, `deferred (<reason>)`,
`false-positive (<mechanism>)`, `disputed`. By default only `Trajectory` and
`Open` are read; pass sections are appended, never rewritten. The command
writes the ledger itself, without asking — a ledger that waits for a human to
update it stays empty.

**The procedure the command carries:**

1. **Target from the ledger.** The last reviewed head equals `HEAD` → no new
   pass; print the recorded verdict. The last head is an ancestor of `HEAD` →
   review the delta `<last head>..HEAD`. No ledger or `full` → the whole
   target. An explicit `<sha>..<sha>` argument overrides both — the way to
   review follow-up fixes on a branch after the original MR was merged.
2. **Blind first.** The rubric runs without the ledger's findings — reading a
   previous verdict first anchors the new one. Above the delegation threshold
   the subagents never receive the ledger.
3. **Refute before keeping.** Every `blocker` / `major` is checked against the
   code for a guard or a caller that makes it impossible.
4. **Reconcile.** Each finding is tagged `new` (code after the last head),
   `missed` (older code, never raised — honest severity, marked as missed),
   `escalated` (a deferred finding raised higher — only with a named new cause),
   or `fix-critique` (aimed at a fix a previous pass requested). A recorded
   false positive is not raised again without a new mechanism.
5. **Trajectory in the report.** Stop and ask what a further pass should add
   when it is pass 3+ with no new commits, when findings grew while the delta
   is small, or when `escalated` plus `fix-critique` exceed half the findings.
6. **Append the pass.**

**The rubric additions that repeated passes showed were missing:**

- Run the gate once on the target. A red gate is one finding; what the linter
  and the git hooks catch is not repeated as judgement.
- Async code and stateful hooks: walk the lifecycle transitions (A→B mid-event,
  A→none→A) and a misbehaving peer (a 200 that closes at once). Check a type's
  documentation against the code instead of trusting it.
- A behaviour change without a test is its own `major`, unless the diff says
  why it cannot be tested.
- A finding names every place with the same mechanism. The fix closes all of
  them, each with a test that fails when the fix is reverted — a fix for one
  site of a race routinely leaves its twin.

**Run it in a fresh session.** The session that wrote the code remembers its
own reasons and tends to confirm them. Everything a review needs from the past
is in the ledger. When the command runs in a session that edited files in the
diff, the report says so and recommends a rerun; it does not refuse.

**A merging command reads the ledger** before the merge: no pass on the
current head, or `major`+ still open → it says so and merges only on an
explicit yes.

**Cost.** The same head costs nothing; a delta costs a delta. The ledger is one
line per finding, not a copy of the reports. The rules live in the command
text, which loads only when invoked — not in `AGENTS.md` or a skill
description, which every session pays for.

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
  nothing extra.
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
specs, correspondence, estimates, task notes — and one rule for the agent: this
material is context, never a source of truth, and is never quoted into committed
content.
