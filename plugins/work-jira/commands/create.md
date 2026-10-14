---
description: Create the epics, stories, tasks and sub-tasks from an approved plan, with descriptions written as ADF, references resolved and issues linked.
argument-hint: '[<epic or plan file>] [dry-run]'
---

# /work-jira:create

Create what `/work-jira:plan` proposed and the developer approved.

**Writes to Jira.** Every creation is confirmed before it happens; `dry-run`
prints what would be created and exits.

## Steps

1. **Refuse without an approved plan.** If this session has no approved tree from
   `/work-jira:plan`, run that first. A plan approved in another session is re-shown
   for confirmation, not trusted silently.

2. **Load conventions and coordinates.** The `issues` skill, the profile's
   `## Tracker` and `## Issues`. Credentials from `.mcp.json`. Missing
   credentials stop the command with the fix, not with a stack trace.

3. **Read the instance, do not assume it.** Issue type ids from `createmeta`,
   labels from `GET /rest/api/3/label`, link types from
   `GET /rest/api/3/issueLinkType`. Pick from what exists; creating a label is a
   question for the developer, never a side effect.

4. **Write the batch script** — the node format is
   `${CLAUDE_PLUGIN_ROOT}/reference/batch.md`. One node per issue, parents
   first; `blocks` a function of `h`, `p`, `ul`, `checklist` in the section order
   the skill fixes, `Estimate` last on tasks and absent on epics. Another issue is
   referenced as a card — `[[PROJ-7]]` when it exists, `[[@<summary>]]` when it is
   in this batch — and every reference becomes a `relates to` link. A dependency
   the plan approved goes into the node's `blocked_by`, never into a hand-made
   `link()` call: the batch writes it provider first and prints it. The script
   lives in the project's local notes, next to the earlier ones, and takes
   `--dry-run`.

5. **Decide the assignee, the fix version and the priority.** The profile's
   `## Issues` says whether tasks go to the developer running the command; if
   it is silent, ask — tasks, sub-tasks and bugs to the developer, or nobody —
   and write the answer into the profile so it is not asked again. Epics and
   stories are never assigned here. The standard makes `Fix Version` and
   `Priority` mandatory before an issue can enter a sprint, so ask for both
   now rather than leaving the defaults: which version the scope belongs to
   (one that mirrors the agreed scope, created if missing), and the rule the
   priorities follow — a rule, written into the profile, survives the next
   batch; a hand-sorted list does not. Both go into the batch — `fix_version`
   for the whole run, `priority` on each node — so they are written with the
   issue, not in a later pass that can be forgotten.

6. **Run dry, then confirm.** `--dry-run` shows what would be created, which
   summaries already exist and are skipped, and the totals. Each line carries
   the version and the priority — `NO VERSION` or `NO PRIORITY` on a line is a
   gap to close before the yes, and so is a `CLASH` line: the summary belongs to
   another issue, and the node needs a name of its own. Check every printed `Blocks` sentence against
   the skill's `Links` rule. Show the count, the total hours, the assignee and
   the dependency sentences, and wait for a yes.

7. **Run.** `jira.batch` does the three passes: create top-down with estimates
   and assignee; render every new description again and update the ones whose
   references resolved; link each issue to the issues it references. A re-run
   after a partial failure skips existing summaries — `rewrite=True` only when
   the failure was between the passes, since a rewrite unticks acceptance
   criteria.

8. **Report** one line per issue: key, type, estimate, summary, version,
   priority. Then the descriptions updated in pass two, the `Blocks` links as
   sentences, the other links created, the totals and the URLs. A summary
   that stayed unresolved — still rendered as code — is named as
   something to fix.

## Hard rules

- **Confirm before the first write**, showing the count, the total hours and the
  assignee.
- **Never create a label**, a version, a component or a link type without being
  asked.
- **Never invent an estimate.** An issue whose hours are unknown is created
  without them, and that is reported. **An epic never carries one** — the
  batch refuses it.
- **Never assign an epic or a story** to the developer; the standard gives them
  to the manager or the analyst.
- **On a failure, stop.** Report what was created and what was not; do not
  continue past an error to "finish the batch".
- **A Task does not become a Sub-task through the API.** Restructuring
  existing issues under new stories is done by the developer in the UI
  (Bulk change → Move, or Convert to Sub-task), after the stories exist;
  the command then verifies type, parent, label and estimate of every moved
  issue instead of assuming. Renaming summaries afterwards breaks every
  `[[@summary]]` in the batch scripts — update the scripts in the same step,
  or the next run creates duplicates.
