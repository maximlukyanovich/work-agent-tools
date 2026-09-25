# Agent instructions

Canonical, agent-agnostic guidance for this repository. It ships tooling that
teaches other repositories to have a harness, so it has one of its own.

## 1. What this is

A Claude Code marketplace and the plugins it lists. Everything in `plugins/` is
installed into other repositories and runs there; nothing here is an
application. README.md explains the model — generator versus library plugins,
the project profile, precedence, command naming. This file holds only the rules
for working on the repository itself.

## 2. Working agreements

- **Nothing is pushed, merged, or opened as a merge request without an explicit
  instruction on the current turn.** Permission does not carry over to the next
  turn. This rule was broken here once; it exists because of that.
- **`main` is protected.** Work goes through a branch and a merge request. Force
  push is not a tool in normal use; the one time it happened was a deliberate
  rewrite of authorship, agreed in advance, with the protection restored after.
- **One trunk, no `develop`.** Every branch — `<type>/<slug>`, types as in the
  commit convention — targets `main`. Contributors hold the Developer role and
  open merge requests; the maintainer reviews and merges. Testing happens on
  the merge request's branch, not on a second long-lived branch: check it out
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

## 3. Conventions

- **Language.** Everything committed here is English — plugin texts, README,
  commit messages, this file.
- **No client project is named.** Not in plugin texts, examples, commit
  messages or merge requests — neither its name nor its issue keys; projects
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

## 4. Checks before a merge request

`scripts/check.py` is the gate, run by CI on every merge request and on
`main`; run it locally before pushing — `python3 scripts/check.py`. It checks:

- every `commands/*.md` has frontmatter with `description`;
- every `skills/*/SKILL.md` has `name` and `description`;
- every file reference inside a plugin resolves — relative links to files that
  exist, or `${CLAUDE_PLUGIN_ROOT}` paths;
- `marketplace.json` lists every plugin under `plugins/`, and each `plugin.json`
  name matches its catalogue entry;
- every Python script compiles.

One check stays with people: **the changed command or skill was run once, in a
real repository, and did what its text says.** The merge request says where
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
  README.md                       for people, links to the skill
scripts/check.py                  the merge-request gate, run by CI
.gitlab-ci.yml                    runs the gate
```
