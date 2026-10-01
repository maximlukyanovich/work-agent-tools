# work-bootstrap

Initialise and audit a repository's agent harness. Stack-agnostic: frontend,
backend, monorepo, library, CLI.

## Commands

| Command | What it does |
| --- | --- |
| `/work-bootstrap:setup` | Inventories the repository, asks only what the code cannot answer, shows a plan, then creates the harness. |
| `/work-bootstrap:audit` | Checks only the method changes after the project's baseline ([CHANGES.md](CHANGES.md)); `full` checks the whole harness against the model. Read-only until a change is approved. |
| `/work-bootstrap:help` | What this plugin can do: commands, the layer model it applies, what it creates. Optional language argument. |

## What it creates

`AGENTS.md` as the canonical document, `CLAUDE.md` as a thin vendor layer,
skills, commands, hooks, `.mcp.json.example`, the `docs/**` skeleton, and the
project profile that every other plugin reads first.

## Keeping a set-up project current

The method changes after a project is set up. A change the project should
carry over is an entry in [CHANGES.md](CHANGES.md); `setup` records the last
entry as the project's `Baseline:` (profile, section `## Harness`).

A `SessionStart` hook ([hooks/hooks.json](hooks/hooks.json)) runs on every new
session wherever this plugin is enabled. It is silent unless the project has a
baseline older than the installed plugin's last entry; then it shows the
developer one line — never added to the model's context — pointing at
`/work-bootstrap:audit`, which checks only the newer entries.

A project set up before the mechanism has a profile but no `## Harness`
section: the hook asks once for `/work-bootstrap:audit full`, which sets the
baseline. A project without a profile never hears from it, and
`Baseline: off` in the profile silences it on purpose.

## The five-layer model

A rule lives on the cheapest layer that can catch it: deterministic checks →
agent hooks → documents → skills → commands. Duplication across layers is
sometimes deliberate; duplication within a layer is always a bug.

## Skills

`skills/layers` — the five layers, what each costs, and the anti-patterns that
make a harness expensive. Loaded by the agent whenever a rule needs a home.

`skills/kickoff` — how a task is planned before code: exploring before asking,
the questionnaire rules, a decisions table, a plan in the chat's language,
approval before code. Loaded when a task needs a plan.

## Reference

Read one at a time, not as a whole: `questions.md` (the eleven asked in phase 1),
`layout.md` (target file tree, gitignore, and the two traps that cost a rewrite),
`templates.md` (skeletons), `project-profile.md` (the file shared plugins read),
`checklist.md` (the final check).
