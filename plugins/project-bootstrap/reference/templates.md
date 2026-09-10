# Templates

Skeletons only. Every example inside a skill or command is written for **this**
project's domain — carrying someone else's examples over is an anti-pattern.

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

## .mcp.json.example

Servers with `${VAR}` placeholders, committed. A generator script substitutes
values from `.env` and fails loudly on a missing one — a partially substituted
config is worse than none: the server starts and authentication fails somewhere
far from the cause.

## Hook contract

A `PostToolUse` hook receives the tool call, exits **0 and silent** when the file
is outside its area, and prints an actionable message otherwise. Every hook has a
test. A hook that fires on ordinary edits gets ignored and then removed.

## docs/local/README.md

The only committed file in the personal space. It states what lives there — local
specs, correspondence, estimates, task notes — and one rule for the agent: this
material is context, never a source of truth, and is never quoted into committed
content.
