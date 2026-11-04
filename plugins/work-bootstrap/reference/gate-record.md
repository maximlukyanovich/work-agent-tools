# gate_record.py

Keeps the record that lets a branch run its full gate once
(`reference/templates/command.md`, "The full gate runs once per branch").
A project runs its copy of
`${CLAUDE_PLUGIN_ROOT}/templates/gate-record/gate_record.py`; this file is its
contract.

```bash
python3 scripts/gate_record.py record full|targeted [<target>] [--commits <n>]
python3 scripts/gate_record.py check [<target>] [--base <branch>] [--small]
```

- **Target** — a worktree directory or a branch checked out in one; none
  means the current directory. A branch checked out nowhere has no tree for
  the gate: exit 2.
- **The record** — `gate-record` in the tree's git directory
  (`git rev-parse --absolute-git-dir`), one line per green run: `full <tree>`
  or `targeted <tree>`, the tree being `HEAD^{tree}`. Trees, not commits, so
  an amend or a rebase that keeps the content keeps its record. A tree
  recorded `full` once stays full.
- **`record`** appends the head's tree only when the tree is clean, untracked
  files included. `full` — after a green full gate, or a run red by timeouts
  alone that "Red under load" calls green, nothing left unrun; `targeted` —
  after a commit whose every changed path had a targeted row and the rows
  passed. The
  paths are the whole commit's (`git show --name-only HEAD`): an amend counts
  what the commit already held, not only the round's. A commit that touched
  a hub file ran only its areas' tests and is not recorded: the full gate is
  still due. A step that changed a path no row covers ran the full gate and
  records `full`, a hub file among its paths or not; under `full gate: ci` it
  ran none and is not recorded. An amend whose own paths all had rows, while
  the commit already held such a path, ran only those rows: it is not
  recorded, the full gate still due. `--commits <n>`, with `targeted`, appends
  the last `n` first-parent commits: a run of several groups commits the
  earlier ones on a dirty tree, so it records once, after the last, when
  every group's paths passed.
- **`check`** walks the first-parent commits from `HEAD` back to the
  merge-base with `origin/<base>` (or the local `<base>`; without `--base`,
  the remote's default branch). It skips when `HEAD`'s tree is recorded
  `full`, or when it meets a commit recorded `full` and every commit before
  it on the walk is recorded. `--small` skips also when every commit of the
  walk is recorded and none is `full`.

## Output

One line on stdout, exit 0:

```
gate: recorded full 1a2b3c4
gate: recorded targeted 1a2b3c4 · 2 commits
gate: not recorded — the tree has uncommitted changes
gate: skip · full green on this tree
gate: skip · full green at 1a2b3c4 · targeted since: 2
gate: skip · small · targeted on all 3
gate: run — 5d6e7f8 has no green record
gate: run — no full green run since origin/main
gate: run — no commits ahead of origin/main
gate: run — the tree has uncommitted changes
```

Exit 2, with the reason on stderr, when the target does not resolve,
`--commits` is out of range, no base can be named, or the walk needs a base
that does not resolve: a dirty tree or a head recorded `full` answers before
a `--base` is looked up. A `skip` is said in one line and the gate is not run;
a `run` names its reason.
