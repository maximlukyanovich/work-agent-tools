# Templates — A command: skeleton, target, next step

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

**`model:` in a command's frontmatter** switches only the turn the command
runs in: the session's model is back with the next prompt, and that turn
re-reads the whole context uncached — each model has its own cache. So it
pays only on a command that runs in one turn without a question, in a fresh
session; never on commit, review or merge, whose first question ends it.

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
the task's last commit, with its head known. A command that only reports
into a task under way may end without a block; an audit does not count that.

**A block for work in a worktree** runs in a session opened in the main
repository, from an IDE or a terminal, so it is never `cd <tree> && claude`,
which only a terminal can run. A command takes the tree as its target, as
above. A prompt for a session that works in the tree opens, in the chat's
language, by entering `<absolute path>` with `EnterWorktree` and says to leave
with `ExitWorktree`, `keep`, before writing what lives in the main tree, then
enter again. Any other path it names is absolute too: after entering, a
relative one resolves in the tree. The tool refuses the tree a session has
already entered, which only means it is there, so the prompt leaves that out. A
`cd` to a tree outside the session's working directories does not outlive its
Bash call, and a command that forgets it runs in the main tree unnoticed; a dev
server there takes the tree's port. Entered, in auto mode, the session reads
the main tree's files, and commits and records the gate in its own tree; Write
to the main tree, through a link too, and `git -C` at it are refused, so local
notes, `NEXT.md`, the efficiency journal and the review ledger wait for the
leaving. Where the tool is missing, the prompt names the tree's absolute path
as the place of work.

At a phase boundary — a task's last commit, a review, before and after a
merge — the block is for a fresh session and comes from
`/work-bootstrap:handoff`: the session that did the work is the most
expensive place for the next phase, and a review must not run there at all.
A small change is the exception (`task.md`, "The change sets the process"): its
phases stay in the session that started it while the handoff leaves it small.
