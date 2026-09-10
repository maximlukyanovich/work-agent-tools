---
description: What work-bootstrap can do — commands, the layer model it applies, and what it creates.
argument-hint: '[<language code>]'
---

# /work-bootstrap:help

Introduce this plugin. **Read-only.**

Language: the conversation's, unless `$1` gives a code.

## Steps

1. **List the commands from their frontmatter** — never typed by hand.

2. **Show the order:** `/work-bootstrap:setup` on a repository without a harness,
   `/work-bootstrap:audit` on one that has it.

3. **State the layer model in a few lines** — deterministic checks, hooks,
   documents, skills, commands, cheapest layer that can catch the rule — and
   point at `skills/layers/SKILL.md` for the rest.

4. **Say what `/work-bootstrap:setup` creates**: `AGENTS.md`, `CLAUDE.md`, the project
   profile, skills, commands, hooks, MCP scaffolding, docs skeleton.

5. **Say what is present here** — is there an `AGENTS.md`, a `.claude/`, a
   profile. One line each.
