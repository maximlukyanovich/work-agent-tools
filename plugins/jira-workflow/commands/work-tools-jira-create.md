---
description: Create the epics, stories, tasks and sub-tasks from an approved plan, with descriptions written as ADF.
argument-hint: '[<epic or plan file>] [dry-run]'
---

# /work-tools-jira-create

Create what `/work-tools-jira-plan` proposed and the developer approved.

**Writes to Jira.** Every creation is confirmed before it happens; `dry-run`
prints what would be created and exits.

## Steps

1. **Refuse without an approved plan.** If this session has no approved tree from
   `/work-tools-jira-plan`, run that first. A plan approved in another session is re-shown
   for confirmation, not trusted silently.

2. **Load conventions and coordinates.** The `issues` skill, the profile's
   `## Tracker` and `## Issues`. Credentials from `.mcp.json`. Missing
   credentials stop the command with the fix, not with a stack trace.

3. **Read the instance, do not assume it.** Issue type ids from `createmeta`,
   labels from `GET /rest/api/3/label`. Pick labels from what exists; creating
   one is a question for the developer, never a side effect.

4. **Build each description** with `scripts/jira.py`: `h` for section headings,
   `ul` for scope, `checklist` for acceptance criteria, `p` for prose. Sections
   in the order the skill fixes, `Estimate` last.

5. **Create top-down**, so parents exist before children: epics, then stories,
   then tasks and sub-tasks. After each issue, set `Original Estimate` with the
   second request — the field is not on the create screen.

6. **Be idempotent.** Before creating, list the project's existing summaries and
   skip exact matches, saying which were skipped. A re-run after a partial
   failure must not double anything.

7. **Report** one line per issue: key, type, estimate, summary. Then the totals
   and the links.

## Hard rules

- **Confirm before the first write**, showing the count and the total hours.
- **Never create a label**, a version, or a component without being asked.
- **Never invent an estimate.** An issue whose hours are unknown is created
  without them, and that is reported.
- **On a failure, stop.** Report what was created and what was not; do not
  continue past an error to "finish the batch".
