---
description: At a phase boundary — after a commit, after a review, before or after a merge — print the next step as a prompt for a fresh session, and /compact where staying is cheaper.
argument-hint: '[<branch | worktree path>] [<next step>]'
---

# /work-bootstrap:handoff

Ends a phase of work so the next one starts small. A session re-reads its
whole context on every tool call, so a review, a fix round, a merge or the
next task costs a fraction in a fresh session that gets a short prompt.
**Read-only**, apart from `NEXT.md` below.

The agent runs it itself at a phase boundary: after a commit, after a review,
before promoting, after a merge. Before a commit it prints only the project's
commit command, to run in this session — the message needs the context this
session holds.

## Steps

1. **Read the target live.** A branch or a worktree path; none means the
   current tree. An existing directory is a worktree; a name that
   `git rev-parse --verify` resolves is a branch, and its worktree comes from
   `git worktree list --porcelain`. With `git -C <tree>`: the branch, its
   base, the commits since the base, a clean or dirty tree.

2. **Collect pointers, not content.** The files the next phase reads, those
   that exist: the plan (the session's plan file, `~/.claude/plans/` unless
   the settings move it), the review ledger with its last pass and open ids
   (`docs/local/reviews/<key>.md` unless the project's review command puts it
   elsewhere), the task's notes and decisions in the personal space. A report
   is never pasted into a prompt — the next session reads the file it lives
   in.

3. **Pick the next step** — named by the caller, or read from the state:

   | Boundary | Fresh session | `/compact` here |
   |---|---|---|
   | uncommitted changes | none — the project's commit command with the target, as a block to run here; it hands off after | — |
   | a task's last commit, or a fix round's | the review command with its range, flags and what to skip — and no prompt for what follows it | no — a review runs fresh |
   | a review with an open `blocker` or `major` | "Fix the open findings of pass N from `<ledger>` (R…) by the testing skill's fix round. Plan — `<path>`. Target — `<branch or worktree>`." | no |
   | a review that reads ready | the task done: with `fix-now` ids open or techdebt rows to write, the fix prompt for them — the round's commit hands over the review of its delta, and that review the merge; without them, the merge command with the target. The merge command first only on the developer's word to ship now. Work left in the plan: "continue the task" | no |
   | before promoting | the merge command with the target | no |
   | after a merge | the start of the next task — `/work-jira:next` or the project's start command. Findings are not listed: by now each has its place; only a gap is named — an id still `open`, or a techdebt place whose row the file lacks | no |
   | the next slice of a long phase | the goal, what is done, where the decisions are, the next step; findings the ledger holds open come before the slice | `/compact <focus>`, then go on |

   **Ready closes the range, not the task.** A verdict speaks for the commits
   the review read. Before the merge command, read the plan and the task's
   notes: work the branch has not done yet — a slice, a live check — makes
   the block "continue the task" (`Read <path>/NEXT.md and continue`, or the
   plan's next step), and the merge waits for the task's end. A review after
   the task's last commit, the usual case, goes to the merge as before.

   **The review prints what follows it.** When the next step is a review,
   the block is the review command. It may name what comes after, but the
   fix-round prompt or the merge command is the review's to print at its
   end, and the task's notes do not argue with it: a `NEXT.md` written now
   is for the step after the chain of review and fixes, and says so.

4. **Print one code block per option**, ready to paste, in the chat's
   language; identifiers, paths and commands verbatim. The text above the
   blocks and the first block name the same step, the nearest one: while a
   commit or another step of the task is ahead, the block is for it, and a
   review command follows only the task's last commit. A prompt longer than
   about eight lines goes into `NEXT.md` in the task's folder in the personal
   space, and its block becomes "Read `<path>/NEXT.md` and continue."

5. **Say how to choose the model** when the next phase is routine — a merge,
   tracker tails: the `/model` picker with `s` switches that session only;
   `/model <name>` typed saves the model as the default for every later
   session.

## Hard rules

- **Read-only**, except `NEXT.md` in the personal space.
- **Before a commit, only the commit command.**
- **A review always gets a fresh session.** The session that wrote the code
  confirms its own reasons; `/compact` does not make it forget them.
- **A review freezes its range.** While the branch's findings have a fix
  round open, no new work lands on it — the fixes, the repeat review, then
  the plan goes on. One tree, one writer.
- **Pointers, never a summary** of a report, a plan or a ledger.
