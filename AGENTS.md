# Agent instructions

Canonical, agent-agnostic guidance for this repository. It ships tooling that
teaches other repositories to have a harness, so it has one of its own.

## 1. What this is

A Claude Code marketplace and the plugins it lists. Everything in `plugins/` is
installed into other repositories and runs there; nothing here is an
application. `docs/design.md` explains the model — generator versus library
plugins, the project profile, precedence, command naming. This file holds only the rules
for working on the repository itself.

## 2. Working agreements

- **Nothing is pushed, merged, or opened as a pull request without an explicit
  instruction on the current turn.** Permission does not carry over to the next
  turn. This rule was broken here once; it exists because of that.
- **`main` is protected.** Work goes through a branch and a pull request. Force
  push is not a tool in normal use; the one time it happened was a deliberate
  rewrite of authorship, agreed in advance, with the protection restored after.
- **One trunk, no `develop`.** Every branch — `<type>/<slug>`, types as in the
  commit convention — targets `main`. Contributors are collaborators and open
  pull requests; the maintainer reviews and merges. Testing happens on the
  pull request's branch, not on a second long-lived branch: check it out
  here and run the changed command in a real repository before approving.
  A project that needs to stay on a known state pins a release tag, by the
  release rule below — still no second branch.
- **A pull request raises the `version` of every plugin it changes**, in its
  `plugin.json`; a change to the plugin's README alone needs none. Major when
  a project must act or it breaks — a profile or data format, a new required
  plugin, a removed command; minor for a new rule, command or template
  section, every `CHANGES.md` entry included; patch for wording or a fix that
  keeps the behaviour. Claude Code replaces an installed plugin only when its
  version differs from the installed one, so a change without a raise reaches
  nobody, the maintainer included. The catalogue carries no `version`:
  `plugin.json` wins over it, and a second copy drifts.
- **A merged batch is released** on the maintainer's word, like a push: an
  annotated tag `vYYYY.MM.DD` on the batch's merge commit into `main` — that
  commit's date, `git log -1 --format=%cs <merge>`; `.2`, `.3` for a second
  and third batch that day — and a GitHub release whose notes put
  `scripts/release_notes.py` — the plugin versions and what a project must
  do — above the merged pull requests:

  ```bash
  git tag -a <tag> -m <tag> <merge> && git push origin <tag>
  gh release create <tag> --verify-tag --title <tag> \
    --notes "$(python3 scripts/release_notes.py <previous tag> <tag>)" \
    --generate-notes --notes-start-tag <previous tag>
  ```

  Release immutability is on: a released tag cannot be moved or deleted, so a
  wrong release is corrected by the next tag. The date says which release a
  project runs; a plugin's version says whether the project must act.
- **Plugin files are addressed through `${CLAUDE_PLUGIN_ROOT}`**, never found by
  searching the filesystem. An installed plugin lives under
  `~/.claude/plugins/cache/`, not where this repository is checked out.
- **Scripts are run, not read.** Their formats are documented under
  `reference/`; opening a script to learn its input costs thousands of tokens
  and teaches nothing the reference does not.
- **A plugin command never takes over a job the project owns** — `/task`,
  `/commit`, `/promote`, `/sync`, `/start` stay in the projects. Only the
  shareable half of a procedure moves here.
- **The method lives here; project specifics live in the project profile.** A
  rule that names a concrete path, key or design system does not belong in a
  plugin. A rule that survives a change of project does not belong in a
  project.
- **One fact, one place.** The skill is the source; README links to it and
  does not restate it. When a rule changes, it changes in one file.
- **A change corrects every text it makes untrue, in the same commit** —
  README, `AGENTS.md`, `CONTRIBUTING.md`, `docs/design.md`, a plugin's README
  and `help`. Before committing, search the repository for the statements the
  change touches. "One fact, one place" keeps the copies few; this keeps the
  ones left true.
- **A tool's behaviour is stated only after a check.** What a plugin text or
  a template says Claude Code, git, Compose or any other tool does — which
  file a value comes from, what a flag or a scope changes, which entry wins a
  merge — is checked first: a probe in a scratch directory, the tool's
  documentation (Context7) or its source, never memory or inference. A claim
  that holds for some options names them; a reason that names no property
  ("that copy lacks what the declaration carries") was not checked.
- **A rule earned on a live project lands here as a merge**, not in that
  project's notes. That is the whole reason this repository exists.
- **A change a set-up project must carry over gets a `CHANGES.md` entry** in
  `plugins/work-bootstrap/`, in the same pull request. That is any change to
  what the checklist or `audit` verifies — the templates, the checklist,
  `audit` itself. Without the entry no project hears of it: the audit checks
  the delta after its baseline, and the `SessionStart` hook counts entries.

## 3. Conventions

- **Language.** Everything committed here is English — plugin texts, README,
  commit messages, this file.
- **No real project is named** — a client's or the maintainer's own. Not in
  plugin texts, examples, commit messages, pull requests or issues: not its
  name, issue keys, paths, recognisable domain terms or quotes from it.
  Projects may be under NDA, and every installer reads these files. Examples
  use `PROJ-N`; a lesson from a live project is described as "observed on a
  live project", without saying which.
- **Commits.** `:gitmoji: type(scope): Subject`, body as one bullet per point
  explaining why. Scope is the plugin name (`jira`, `estimation`, `bootstrap`)
  or `readme` / `catalog` for the repository level. No agent attribution.
- **Command names** are short verbs; the plugin name is the prefix, added by
  the harness with a colon. Never a colon in a filename, never the plugin name
  repeated inside a command name.
- **Plugin names are fixed once.** Renaming one breaks every command it ships
  and every document quoting them.
- **Descriptions are the loading mechanism.** A skill's `description` decides
  when the agent loads it; a command's decides what completion shows. Both are
  written for that purpose, narrowly, and both are paid for in every session.
  A plugin's entry in `marketplace.json` is its shop window in `/plugin`;
  README files are for people on the web, and no tool renders them.
- **A plugin command ends the way a project's does** — with its next step as
  a block ready to paste, a stop that sends to another command included, by
  "A command ends with its next step" in
  `plugins/work-bootstrap/reference/templates.md`.

## 4. Checks before a pull request

`scripts/check.py` is the gate, run by CI on every pull request and on
`main`; run it locally before pushing, after `git fetch` —
`python3 scripts/check.py`. It compares versions against `origin/main`, or the
`--base` you pass, and stops when that ref is missing. It checks:

- every `commands/*.md` has frontmatter with `description`;
- every `skills/*/SKILL.md` has `name` and `description`;
- every file reference inside a plugin resolves — relative links to files that
  exist, or `${CLAUDE_PLUGIN_ROOT}` paths;
- `marketplace.json` lists every plugin under `plugins/`, and each `plugin.json`
  name matches its catalogue entry;
- every `CHANGES.md` entry is `## YYYY-MM-DD · <id>`, with a unique id and
  `What:`, `Check:` and `Applies to:`;
- every plugin hook points at a script that exists, in its `command` or its
  `args`;
- every Python script compiles;
- every `plugin.json` has a `version` of the form `MAJOR.MINOR.PATCH`, the
  catalogue has none, and a plugin whose files changed, its README aside, has
  a version above the base's;
- a new `CHANGES.md` entry comes with a minor raise of its plugin at least;
- no commit of the range, and in CI no pull-request body, carries agent
  attribution — a co-author trailer naming Claude, a "Generated with Claude
  Code" line.

It also warns, without failing, about a plugin text above 10 KB — any `*.md`
under `plugins/` but a README: splitting it is a decision, not drift.

The tests under `tests/` pin what the plugins' scripts do, and CI runs them
after the gate: every test passes — `python3 -m unittest discover -s tests`.
They live outside the plugins, so a change to a test raises no plugin's
version.

One check stays with people: **the changed command or skill was run once, in a
real repository, and did what its text says.** The pull request says where
and how it was run. This item is not optional. A command that has never been
executed is a draft.

## 5. Layout

```
.claude-plugin/marketplace.json   the catalogue
plugins/<name>/
  .claude-plugin/plugin.json      manifest
  commands/*.md                   procedures a human invokes
  skills/<name>/SKILL.md          knowledge the agent loads by itself
  reference/*.md                  read one file at a time, on instruction
  scripts/                        executed, never read into context
  hooks/hooks.json                plugin hooks — run wherever the plugin is on
  README.md                       for people, links to the skill
plugins/work-bootstrap/CHANGES.md method changes a set-up project carries over
docs/design.md                    the model behind the plugins
CONTRIBUTING.md                   for outside contributors; points here
LICENSE                           MIT
scripts/check.py                  the pull-request gate, run by CI
scripts/release_notes.py          a release's notes: plugin versions, action needed
tests/                            the scripts' tests, stdlib unittest, run by CI
.github/workflows/check.yml       runs the gate and the tests
```
