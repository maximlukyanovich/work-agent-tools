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
before promoting, after a merge. Never before a commit — the message needs
the context this session holds.

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
   | a task's last commit, or a fix round's | the review command with its range, flags and what to skip | no — a review runs fresh |
   | a review with open findings | "Fix the open findings of pass N from `<ledger>` (R…). Plan — `<path>`. Target — `<branch or worktree>`." | no |
   | a review that reads ready | the merge command with the target; with minors still open, the fix prompt as a second block | no |
   | before promoting | the merge command with the target | no |
   | after a merge | the start of the next task — `/work-jira:next` or the project's start command; findings the ledger still holds open are named, to fix or to defer | no |
   | the next slice of a long phase | the goal, what is done, where the decisions are, the next step | `/compact <focus>`, then go on |

4. **Print one code block per option**, ready to paste, in the chat's
   language; identifiers, paths and commands verbatim. A prompt longer than
   about eight lines goes into `NEXT.md` in the task's folder in the personal
   space, and its block becomes "Read `<path>/NEXT.md` and continue."

5. **Say how to choose the model** when the next phase is routine — a merge,
   tracker tails: the `/model` picker with `s` switches that session only;
   `/model <name>` typed saves the model as the default for every later
   session.

## Hard rules

- **Read-only**, except `NEXT.md` in the personal space.
- **Never before a commit.**
- **A review always gets a fresh session.** The session that wrote the code
  confirms its own reasons; `/compact` does not make it forget them.
- **Pointers, never a summary** of a report, a plan or a ledger.
