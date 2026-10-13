---
description: Set up a repository's agent harness — inventory, questions, plan, then create AGENTS.md, skills, commands, hooks, MCP and docs.
argument-hint: '[<language>]'
---

# /work-bootstrap:setup

Create the agent harness for this repository. Stack-agnostic.

**Writes files.** Nothing is created before the plan is approved, and nothing is
committed — apart from rewording the first commit, on a yes (step 4).

## Steps

The order is fixed. Steps are not reordered or skipped.

1. **Inventory the repository.** Everything visible from code, config and git
   history is **not** a question. What exists already: `AGENTS.md`, `.claude/`,
   other agents' config. The stack and its quality commands, from the manifest
   files. Branches, remotes, commit style, git hooks. Documentation and local
   notes. Integrations: MCP examples, environment templates.

   Decide the mode from what you found: no manifest and nothing but tool
   configuration → offer `/work-bootstrap:new`, which creates the project
   first; nothing or fragments → set up — an `AGENTS.md` or `CLAUDE.md` that
   holds only a generator's block is a fragment; a harness already there →
   say so and offer `/work-bootstrap:audit` instead. A stack with a recipe in
   `${CLAUDE_PLUGIN_ROOT}/reference/scaffold/` — read its "For the harness"
   section.

2. **Ask what the code cannot answer.** One or two batches, never one question
   per turn, every question with an explicit default. The list is in
   `${CLAUDE_PLUGIN_ROOT}/reference/questions.md` — eleven of them, and the
   most valuable is "what has already gone wrong here", because without it the
   hook set comes out speculative. Wait for the answers.

3. **Show the plan**: which files will be created, which changed, which left
   alone — in the chat's language, as the `kickoff` skill says. Wait for
   confirmation.

4. **Create.** Layout and the two traps that cost a rewrite:
   `${CLAUDE_PLUGIN_ROOT}/reference/layout.md`. Skeletons:
   `${CLAUDE_PLUGIN_ROOT}/reference/templates.md`. Which layer each rule
   belongs on: the `layers` skill.

   Order: `AGENTS.md` first — everything else references it — then `CLAUDE.md`,
   the profile, skills, commands, agents, hooks, MCP, docs.

   The profile gets a `## Harness` section whose `Baseline:` is the id of the
   last entry in `${CLAUDE_PLUGIN_ROOT}/CHANGES.md`: the harness was built
   to the method as it stands, and `/work-bootstrap:audit` later checks only
   what changed after it.

   The plugin set goes where Q10 put it:
   `claude plugin install <plugin>@mluk-work-agent-tools --scope project` — or
   `local` — for each, from the repository root. When Q7 settled a format
   the repository's only commit does not follow, and that commit is not
   pushed, offer to reword it: `git commit --amend --only -m "<message>"`, on
   a yes.

5. **Run the final check** from `${CLAUDE_PLUGIN_ROOT}/reference/checklist.md`
   and report what is green and what is not.

6. **Report**: created, changed, deliberately left out and why, still open.

## Hard rules

- **Never invent a missing requirement.** No tracker, stack, branch scheme or
  documentation language — ask. A placeholder is tolerable only while a question
  is open and only if it is listed in the report.
- **Never carry another project's domain over.** Examples in skills and commands
  are written for this project.
- **No empty placeholder directories and no stub READMEs.** A directory appears
  with its first real file.
- **Nothing is committed, pushed or opened as a PR.** Not without an explicit
  instruction on the current turn.
- **One fact, one place.** Before writing a rule, check it does not already live
  in another file. If it does, link to it.
- **A missing layer is a decision, not an oversight** — recorded in `AGENTS.md`
  with its reason and the conditions that would add it later.
