# Templates — The harness's files: AGENTS.md, README, CLAUDE.md, SKILL.md, MCP, hooks, docs/local

## AGENTS.md

Seven sections, in this order. Anything a linter already enforces is marked
`[lint]` and not explained twice.

```markdown
# Agent instructions

## 1. Project        what it is, which surfaces, current phase
## 2. Commands       install, dev, the one gate command, tests, build
## 3. Architecture   layers table: path, responsibility, what it may import
## 4. Conventions    language, branches, commits, styling, copy
## 5. Sources of truth   priority order, and what to do on conflict
## 6. Working agreements  the rules that are not machine-checkable
## 7. Agent tooling   commands, skills, deterministic checks, hooks
```

Rules that keep it cheap: no rule appears twice; anything expressible as lint
configuration is a one-line reference, not a paragraph; the absence of a layer is
recorded deliberately, with its reason.

§6 carries one line for the efficiency journal: a remark from the developer
about the agent's speed, cost or quality of work goes as a row into
`docs/local/efficiency-remarks.md` in the same session — date, task, the
quote, context, a link, no judgement; `/work-bootstrap:audit` reads it.

§6 also carries a habit: a prompt or command the agent recommends to continue
the work, in any message, goes in a code block of its own, ready to copy; there
may be several. A block names a step that can run now: a step that waits on an
earlier one shows the earlier step's block first. The line above it says where
it runs, the words for a fresh session in bold. A block for a worktree runs in
a session opened in the main repository, so it is never `cd <tree> && claude`:
a prompt enters the tree by its absolute path with `EnterWorktree`, leaves with
`ExitWorktree`, `keep`, before writing to the main tree, and enters again. The
habit is a format of output, not a duty to end on a block (`command.md`, "A
command ends with its next step"), and it stays here rather than in a skill: it
applies to any message, and a skill loads only for its own topic.

A generator may have written some of these files first — `create-next-app`
writes `AGENTS.md`, most generators a `.gitignore`. They are
extended, never rewritten, and a block the generator marks as its own stays
where it is: the framework may write it back, and from then on the tree is
dirty. The stack's recipe in `reference/scaffold/` names the block.

With pnpm 11, §2 says next to how a dependency is added that one with a build
script — direct or transitive — needs an `allowBuilds` entry in
`pnpm-workspace.yaml`. A missing entry fails the install with
`ERR_PNPM_IGNORED_BUILDS`, but only a clean one: a warm `node_modules` hides
it, and the first to see it is the server. The file's header gives each entry
its reason and says to prove a new dependency with
`pnpm install --frozen-lockfile` on a fresh checkout.

## README.md — Deployment

Once the project runs anywhere but a developer machine, the root README has a
Deployment section. Whoever sets up the server reads README, not `AGENTS.md`,
and a deployment guessed from `dev` ships the dev server.

```markdown
## Deployment

`<dev command>` is for local development only. A server runs:

    <install from the lockfile, frozen>
    <build>
    <start, with the port>

- Versions are pinned: <runtime> (<file>) and <package manager> (<field>);
  how a stock image gets them.
- <VARIABLE>: which steps need it — build, start or both — and whether it is
  baked into the bundle or read at start. What it means → <env example>.
```

Every line is proven on a fresh checkout without a local env file before it
is written: a variable the build validates at import is invisible on the
machine that has one.

## CLAUDE.md

```markdown
@AGENTS.md

# CLAUDE.md

Project rules live in AGENTS.md, imported above. This file holds only what is
specific to Claude Code and written nowhere else — deleting it must not lose a
single project rule.
```

## SKILL.md

```markdown
---
name: <name>
description: <what it covers, and when it applies — the sentence that decides loading>
---

# <name>

## When it applies
## How to do it
## How not to do it
## How it is verified
```

The `description` is the whole loading mechanism. Vague means either never loaded
or always loaded.

## .mcp.json.example

Servers with `${VAR}` placeholders, committed. A generator script substitutes
values from `.env` and fails loudly on a missing one — a partially substituted
config is worse than none: the server starts and authentication fails somewhere
far from the cause.

## Hook contract

A `PostToolUse` hook receives the tool call, exits **0 and silent** when the file
is outside its area, and prints an actionable message otherwise. Every hook has a
test. A hook that fires on ordinary edits gets ignored and then removed.

## Git hooks

- **Git hooks stay fast; the full gate does not go into one.** A gate that
  takes minutes in `pre-push` is bypassed within a week, and a bypassed check
  is worse than none. The full gate runs in CI or in the review and merge
  commands, once per branch, by the profile's `full gate`
  (`gate.md`, "The full gate runs once per branch").
- **lint-staged: the linter's fixes first, the formatter last** —
  `['eslint --fix', 'prettier --write']`. The reverse order leaves the linter's
  edits unformatted while the hook reports success, and the gate fails a commit
  later.
- **An optional task-key check in `commit-msg`**, offered at setup. The key
  comes from the branch name (`<prefix>/PROJ-12-slug` → the subject must carry
  `PROJ-12`); a branch without a key, a detached `HEAD` and a merge commit are
  exempt, which is the way to work without a task. **commitlint keeps only one
  inline plugin**, and a second replaces the first — including the one a
  preset brings: `commitlint-config-gitmoji` ships its rule as an inline
  plugin, so even the first local plugin disables it and the config fails with
  "Found rules without implementation: start-with-gitmoji". Spread the preset's
  plugin rules into the one local plugin object together with your own.

## docs/local/README.md

The only committed file in the personal space. It states what lives there — local
specs, correspondence, estimates, task notes, the efficiency journal — and one
rule for the agent: this material is context, never a source of truth, and is
never quoted into committed content.

## docs/local/efficiency-remarks.md

The developer's remarks about how the agent spends time, tokens and care —
raw material for `/work-bootstrap:audit`, not decisions. Ignored with the
rest of `docs/local/`, written in the conversation's language:

```markdown
# Efficiency remarks

One row per remark about the agent's speed, cost or quality of work, in the
session it was made: the words as said and what happened. No judgement — the
audit draws the conclusions and fills the last column.

| Date | Task / phase | Quote | Context | Details | Analysed |
| --- | --- | --- | --- | --- | --- |
```

A row may name the project's issues and quote people: the file stays local.
What leaves it — an issue for the library — is depersonalised by the audit.
