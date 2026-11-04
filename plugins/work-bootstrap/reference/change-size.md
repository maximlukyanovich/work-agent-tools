# change_size.py

Measures a branch's diff against the thresholds of a small change
(`reference/templates/task.md`, "The change sets the process"). Run it; this file
is its contract.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/change_size.py" [<target>] [--base <branch>] \
  [--max-lines 100] [--max-files 5] [--max-prose-lines 300]
```

- **Target** — a worktree directory or a branch name; none means the current
  directory. A branch checked out in a worktree is measured there; a branch
  checked out nowhere is measured by refs, and `uncommitted` reads `no`.
- **Base** — the branch the work left. The diff runs from the merge-base
  with `origin/<base>`, or the local `<base>` when the remote has none, to
  the target's head. Without `--base`, the remote's default branch
  (`origin/HEAD`).
- **Thresholds** — small when the diff touches at most `--max-files` files
  and at most `--max-lines` lines, insertions plus deletions; a diff of
  prose alone — `*.md` files and anything under `docs/` — may reach
  `--max-prose-lines`. A rename counts its edits, not the file twice; a
  binary file counts as a file without lines.

## Output

One line on stdout, exit 0:

```
size: small · files 1 · +29 −2 · prose-only yes · uncommitted no
size: normal · files 9 · +77 −21 · prose-only no · uncommitted no — files 9 > 5
size: normal · files 16 · +287 −47 · prose-only no · uncommitted no · new 3 +210 · changed 13 +77 −47, largest 18 — files 16 > 5, lines 334 > 100
size: normal · files 3 · +180 −0 · prose-only no · uncommitted no · new 3 +180 — lines 180 > 100
```

A diff that adds files shows them as `new`; when it changes others too,
`changed` follows — the rest, renames included, with the largest edit of one
file in lines. A new isolated module whose `changed` part is
small edits spread over many files is the module and its wiring; the
thresholds are a hint, and the level is the agent's to name. A normal size
ends with ` — ` and every threshold it crossed. `uncommitted`
says the tree has changes the measure does not count: commit them first and
measure again.

Exit 2, with the reason on stderr, when the target or the base does not
resolve.

The script does not judge risk: a change in a risk class of the project's
testing skill is critical whatever its size, and that is the agent's call.
