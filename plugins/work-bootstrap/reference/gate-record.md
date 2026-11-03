# gate_record.py

Keeps the record that lets a branch run its full gate once
(`reference/templates/command.md`, "The full gate runs once per branch").
Run it; this file is its contract.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate_record.py" record full|targeted [<target>]
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate_record.py" check [<target>] [--base <branch>] [--small]
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
  files included. `full` — after a green full gate; `targeted` — after a
  commit whose every changed path had a targeted row and the rows passed. A
  commit that touched a hub file or a path no row covers is not recorded:
  the full gate is still due.
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
gate: not recorded — the tree has uncommitted changes
gate: skip · full green on this tree
gate: skip · full green at 1a2b3c4 · targeted since: 2
gate: skip · small · targeted on all 3
gate: run — 5d6e7f8 has no green record
gate: run — no full green run since origin/main
gate: run — no commits ahead of origin/main
gate: run — the tree has uncommitted changes
```

Exit 2, with the reason on stderr, when the target or the base does not
resolve. A `skip` is said in one line and the gate is not run; a `run` names
its reason.
