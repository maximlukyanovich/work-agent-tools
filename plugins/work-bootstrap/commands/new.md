---
description: Start a project in an empty folder — the stack's official generator, pinned versions, git and a remote — before setup builds its harness.
argument-hint: '[<stack>]'
disable-model-invocation: true
---

# /work-bootstrap:new

Create a project in an empty folder, so that `/work-bootstrap:setup` has a
repository to inventory. The procedure knows no stack: each stack is a recipe
in `${CLAUDE_PLUGIN_ROOT}/reference/scaffold/`, one file per stack, read one at
a time. Use that path verbatim — never search the filesystem for the plugin.

**Writes files.** Nothing is committed, created on a server or pushed without a
yes on the current turn.

## Steps

1. **Check that the folder is empty.** List everything, hidden files
   included. Only tool and editor configuration and repository metadata may
   be there — `.claude/`, `.git/`, `.idea/`, `.vscode/` and the like.
   Anything else — a manifest, sources, `AGENTS.md`, `README.md` — means the
   project exists: stop, and offer `/work-bootstrap:setup`, or
   `/work-bootstrap:audit` when a harness is there, as a code block.

2. **Ask the stack** — `$1`, or one option per recipe in the scaffold
   directory and "another" last.

3. **Read its recipe.** With none, ask the owner for the generator command
   and its options; never assemble one from memory.

4. **Ask the recipe's questions in one batch**, by the `kickoff` skill's
   rules: the recommendation first and marked, every option with its
   trade-off.

5. **Run the generator** as the recipe says: in this folder, every option
   passed explicitly, its own git initialisation off. When the installed
   generator's version differs from the one the recipe was checked with,
   compare the recipe's flags with `--help` first.

6. **Pin the environment** as the recipe says — the runtime version, the
   package manager, a lockfile from a first install — and write nothing the
   generator already wrote.

7. **Initialise git** unless `.git/` is there: `git init -b main`. The branch
   chain is `setup`'s question.

8. **Offer the first commit.** `.claude/settings.local.json`, if present, goes
   into `.gitignore` first: it predates the repository, so nothing ignores it
   yet. An empty `git config user.email` → ask the owner which identity
   commits here and set it in this repository; one borrowed from another
   repository is a guess. Stage explicit paths. Propose the message in the
   default format of `${CLAUDE_PLUGIN_ROOT}/reference/questions.md` (Q7),
   without a task key, and ask whether the format suits — its rules are set by
   `setup`, which can still reword this commit until it is pushed. Commit on a
   yes.

9. **Offer the remote** on GitLab, either way on a yes:
   - the URL of an existing empty project → `git remote add origin <url>`;
   - or a new one: `glab repo create <host>/<group>/<name> --private
     --defaultBranch main`, which also adds `origin`. `glab` defaults to an
     internal project, a `master` branch and the first host in its config,
     so all three are passed.

   A project created with a README rejects the first push. Pushing is a
   separate yes, and after it the first commit's message is final.

10. **End with the next step** — a block for a fresh session:
    `/work-bootstrap:setup`.

## Hard rules

- **Only in an empty folder.** Never a generator mode that clears a non-empty
  folder: it deletes `.claude/`.
- **Never the generator's git.** Its initial commit follows no convention.
- **No option the recipe or the owner did not give.** A generator's saved
  preferences are not a source.
- **No commit, no project on a server, no push** without a yes on the current
  turn.
- **No stack knowledge here.** A stack's decisions and traps live in its
  recipe.
