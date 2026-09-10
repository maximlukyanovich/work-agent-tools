# project-bootstrap

Initialise and audit a repository's agent harness. Stack-agnostic: frontend,
backend, monorepo, library, CLI.

## Commands

| Command | What it does |
| --- | --- |
| `/boot-setup` | Inventories the repository, asks only what the code cannot answer, shows a plan, then creates the harness. |
| `/boot-audit` | Checks an existing harness against the model and reports what drifted. Read-only. |
| `/boot-help` | What this plugin can do: commands, the layer model it applies, what it creates. Optional language argument. |

## What it creates

`AGENTS.md` as the canonical document, `CLAUDE.md` as a thin vendor layer,
skills, commands, hooks, `.mcp.json.example`, the `docs/**` skeleton, and the
project profile that every other plugin reads first.

## The five-layer model

A rule lives on the cheapest layer that can catch it: deterministic checks →
agent hooks → documents → skills → commands. Duplication across layers is
sometimes deliberate; duplication within a layer is always a bug.

**Status:** skeleton. Content is being carried over from `agent-setup-playbook.md`.
