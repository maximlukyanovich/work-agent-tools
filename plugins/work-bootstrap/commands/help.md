---
description: What work-bootstrap can do — commands, the layer model it applies, and what it creates.
argument-hint: '[<language code>]'
---

# /work-bootstrap:help

Introduce this plugin. **Read-only.**

Language: the conversation's, unless `$1` gives a code.

## Steps

1. **List the commands from their frontmatter.** Read `description` and
   `argument-hint` out of every file in `${CLAUDE_PLUGIN_ROOT}/commands/`.
   Use that path verbatim — never search the filesystem for the plugin.

2. **Show the order:** `/work-bootstrap:setup` on a repository without a harness,
   `/work-bootstrap:audit` on one that has it.

3. **State the layer model in a few lines** — deterministic checks, hooks,
   documents, skills, commands, cheapest layer that can catch the rule — and
   point at `${CLAUDE_PLUGIN_ROOT}/skills/layers/SKILL.md` for the rest.

4. **Say what `/work-bootstrap:setup` creates**: `AGENTS.md`, `CLAUDE.md`, the project
   profile, skills, commands, hooks, MCP scaffolding, docs skeleton.

5. **Say what is present here** — is there an `AGENTS.md`, a `.claude/`, a
   profile. One line each.

## Hard rules

- **Never search the filesystem for the plugin.** Its files are at
  `${CLAUDE_PLUGIN_ROOT}` — use that path verbatim. A `find` over the disk is the
  failure this rule exists to prevent.
- Read-only. No file is written, no API call changes anything.
- The command list comes from frontmatter, not from memory.
- Keep it short: this is an introduction, not the manual.
