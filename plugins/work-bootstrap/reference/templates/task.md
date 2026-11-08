# Templates — A command that starts a task

### A command that starts a task must offer the opening steps

The status of an issue is the only thing the rest of the team sees of work
that has not shipped. A task started without moving it reads as untouched
for days — and the move, left to memory, is the step that gets skipped. So
when the profile names a tracker the agent can reach (an MCP server or the
plugin's script), the command that starts a task (`/my-task` or its equivalent)
asks **one question**, once the issue is read and before the branch is cut:

- **the transition to the workflow's in-progress status**, chosen from the
  transitions the tracker offers for that issue, never a guessed id;
- **the assignee**, when the issue has none;
- **the parent story or epic**, when it still sits in a to-do status.

Carry the state into the question — «Backlog, assigned to you, story still in
Backlog» — and do only what is answered. When the project keeps a waiting
list of posted questions (`work-tracker`), name this issue's open
ones in the same message: an unanswered question is often why the issue is
still open. Hour buckets and issues already in
progress are left alone. With no reachable tracker the step is skipped and
said so in one line, not silently.

Once the issue is read, the command also holds its description against the
sources — the design, the backend, the answers and decisions recorded. A
description that has drifted gets a draft as a section of the plan, posted on
the developer's yes right after the plan is approved and before the first
code, not in the last slice; a developer without the right to edit the issue
posts the change as a comment for whoever keeps it. With `work-tracker`, the
rules are its `issues` skill's "Description".

The same command loads the `kickoff` skill before its first question to the
developer: the questionnaire rules live there, and a command that asks
without them drops the closing "anything to add?". It loads the project's
testing skill before it writes the plan: the skill's proof by risk sets the
plan's verification, and its lists of states — a write while another is in
flight, data out of date while a re-read runs — become rows of the state
table. Observed on a live project: a 22-row state table held neither kind,
and three of the first review's seven `major`s were rows of them. And once
the plan is approved, before the first production edit, it names the
project's skills for placement, components and tests to load — the testing
skill again when the plan was approved in another session: skills match on
context unreliably, and the rules they carry are the ones a review finds
broken. Its plan carries the sections `kickoff` names — the state table, the
framework behaviour with file:line, the line on the structural option.

**The change sets the process.** Every fresh session starts by re-reading
the harness and the task, and a handoff is worth that only when the phase
it closes was large. So the first line of the command's answer names the
change's level, predicted from the issue and the exploration — there is no
diff yet:

- **small** — prose, or a change that keeps behaviour, within the
  thresholds `/work-bootstrap:handoff` measures (at most 100 lines and 5
  files, prose alone up to 300; `${CLAUDE_PLUGIN_ROOT}/reference/change-size.md`),
  and in no risk class of the testing skill. A new isolated page or module
  is small too, whatever the thresholds say, when the rest of its diff is
  wiring — the route registry, navigation links, catalogue rows, tests
  updated to the new link, documentation lines: the level follows the
  surface of behaviour, not the count of files. A file of a risk class
  touched only to register the new path takes a test of that registration,
  not the critical level. A short plan in chat — what changes, which files,
  how it is proven — and the developer's yes before code take the place of
  the questionnaire and plan mode; the targeted checks stand for the full
  gate, unless a commit touched a hub file or a path no row covers
  (`gate.md`, "The full gate runs once per branch"); the review and the
  merge run in the same session;
- **critical** — money, access, a migration, deleted data. Its review runs
  only in a fresh session;
- **normal** — everything else, as this section describes.

The developer may raise the level at any time; the agent never lowers a
critical one. The handoff measures the diff and raises a small change that
outgrew the thresholds, in one line, unless the overage is that wiring.
Observed on a live project: a 31-line documentation change took nine
sessions, nearly nine tenths of its cost spent on their starts; a new static
page — half an hour of work, sixteen files, most of them wiring — went
through the whole normal cycle: a plan, a review in its own session, a round
of fixes, the full gate twice.

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
- **What it hands over goes to a session in the main repository.** The
  command's closing block and every next step after it follow `command.md`,
  "A block for work in a worktree".
- **A worktree is temporary.** The command that merges removes it with its
  branch (closing steps below); a folder deleted by hand leaves a stale entry
  that `git worktree prune` clears.
