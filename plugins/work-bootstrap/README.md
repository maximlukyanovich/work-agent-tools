# work-bootstrap

Initialise and audit a repository's agent harness. Stack-agnostic: frontend,
backend, monorepo, library, CLI.

## Commands

| Command | What it does |
| --- | --- |
| `/work-bootstrap:setup` | Inventories the repository, asks only what the code cannot answer, shows a plan, then creates the harness. |
| `/work-bootstrap:audit` | Checks an existing harness against the model and reports what drifted. Read-only. |
| `/work-bootstrap:help` | What this plugin can do: commands, the layer model it applies, what it creates. Optional language argument. |

## What it creates

`AGENTS.md` as the canonical document, `CLAUDE.md` as a thin vendor layer,
skills, commands, hooks, `.mcp.json.example`, the `docs/**` skeleton, and the
project profile that every other plugin reads first.

## The five-layer model

A rule lives on the cheapest layer that can catch it: deterministic checks →
agent hooks → documents → skills → commands. Duplication across layers is
sometimes deliberate; duplication within a layer is always a bug.

## Skill

`skills/layers` — the five layers, what each costs, and the anti-patterns that
make a harness expensive. Loaded by the agent whenever a rule needs a home.

## Reference

Read one at a time, not as a whole: `questions.md` (the eleven asked in phase 1),
`layout.md` (target file tree, gitignore, and the two traps that cost a rewrite),
`templates.md` (skeletons), `project-profile.md` (the file shared plugins read),
`checklist.md` (the final check).
