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
  When consumers need to stay on a known state, `main` gets release tags and
  the catalogue can pin one — still no second branch.
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
- **No client project is named.** Not in plugin texts, examples, commit
  messages or pull requests — neither its name nor its issue keys; projects
  may be under NDA, and every installer reads these files. Examples use
  `PROJ-N`; a lesson from a live project is described as one, without saying
  which.
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
`main`; run it locally before pushing — `python3 scripts/check.py`. It checks:

- every `commands/*.md` has frontmatter with `description`;
- every `skills/*/SKILL.md` has `name` and `description`;
- every file reference inside a plugin resolves — relative links to files that
  exist, or `${CLAUDE_PLUGIN_ROOT}` paths;
- `marketplace.json` lists every plugin under `plugins/`, and each `plugin.json`
  name matches its catalogue entry;
- every `CHANGES.md` entry is `## YYYY-MM-DD · <id>`, with a unique id and
  `What:`, `Check:` and `Applies to:`;
- every plugin hook's command points at a script that exists;
- every Python script compiles.

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
.github/workflows/check.yml       runs the gate
```
