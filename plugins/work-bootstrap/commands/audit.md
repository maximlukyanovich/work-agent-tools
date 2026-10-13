---
description: Audit an existing agent harness against the layer model and report what drifted, in priority order.
argument-hint: '[full]'
---

# /work-bootstrap:audit

The harness exists; the job is to find the gaps, not to rewrite it.
**Read-only** until a change is approved, and then one group at a time.

## Delta or full

**By default, only what changed in the method.** Read the baseline from
`.claude/project-profile.md`, section `## Harness`, line `Baseline: <id>`.
Take the entries of `${CLAUDE_PLUGIN_ROOT}/CHANGES.md` after that id and
check each one's `Check:` against the project — nothing else. The report is
one row per entry: the entry, its state in this project, the proposed action;
an entry whose `Applies to:` does not fit is reported as not applicable.

- **No baseline**: the project predates the mechanism — say so and run the
  full audit, which ends by setting one. `Baseline: off` means the project
  opted out of the reminder; the audit still runs when asked, and offers to
  set a real baseline at the end.
- **Baseline not in `CHANGES.md`**: the installed plugin is older than the
  one that set it — say so; run nothing until the plugin is updated.
- **`full`**: every check below, then the baseline.

**Moving the baseline is the last step, and it is asked.** Once each entry is
applied, declined with a recorded reason, or not applicable, offer to set
`Baseline:` to the last entry. A declined entry stays declined: its reason
goes into the project's own docs, not into the baseline, so the next delta
does not raise it again.

## What to check

1. **Document against code.** Do the commands named in `AGENTS.md` exist in the
   manifest? Does the described architecture match the tree? Are the enforcement
   mechanisms it names actually wired up? **Prose that contradicts the code is
   stale prose, and it is worse than no prose** — it looks like a source of truth
   without being one.

2. **Duplication.** The same rule in `AGENTS.md`, `CLAUDE.md` and a skill —
   collapse to one place plus links.

3. **A rule on the wrong layer.** A paragraph of prose about something a linter
   rule expresses — move it down. A hook that needs contextual judgement — move
   it up into a skill.

4. **Dead artefacts.** Commands and skills nobody uses, hooks with steady false
   positives, links to files that no longer exist.

5. **A review without memory.** Does the review command keep a pass ledger,
   compare against the last reviewed head, and tag what it finds against the
   previous passes? Without one, every pass starts cold, re-ranks deferred
   items and critiques the previous pass's fixes, and the finding count grows
   while the code does not change. Does a merging command read that ledger?
   Does the commit command, after a task's last commit, hand over the review
   command with its range — or is the review left to someone's memory?
   And the other half: when findings are fixed — usually in the working
   session, from a pasted report — does a rule in `AGENTS.md` load the testing
   skill first, and does that skill ask for a reverted-fix test per finding
   and for every state the fix touches? Without it, each pass's fixes become
   the next pass's `major`s. Does the review end with the next step — the
   fix-round prompt that names the ledger, or the merge command — through
   `/work-bootstrap:handoff`, rather than a report to paste back? Do review
   groups go to `.claude/agents/review-group.md` on a cheaper model, with
   `model=` to override it and refutation left to the session?

6. **Where the gate runs.** Does the push command run the gate for a tree the
   commit command did not validate? Is a git hook running the whole gate —
   minutes per push, soon bypassed? Does lint-staged run the formatter after
   the linter's fixes? The wrong order leaves linter edits unformatted while
   the hook passes. Does the commit command compare the index with its
   proposed list right before committing? A commit the `commit-msg` hook
   refused keeps its paths staged, and without the check the next commit
   carries them in. Do commit, review and merge take a target — a branch or
   a worktree path — and run their git calls and the gate in that tree?
   Does every command end with its next step as a block ready to paste?

7. **Gaps.** Layers from the model that are absent. Absence is allowed — but it
   must be deliberate and written down, with the conditions that would fill it.

8. **A merge that ends in silence.** Does every command that merges offer the
   closing steps afterwards — result comment, worklog, branch deletion,
   anything raised for another team? A command that merges and stops is how
   issues end up delivered but undocumented and untracked, and the gap is
   invisible precisely because the code shipped.
   The mirror check: does the command that starts a task offer the opening
   steps — the in-progress transition, the assignee, the parent's status —
   when a tracker is reachable, and load `kickoff` before it asks? Does it
   take a `worktree` argument and offer one when a live `git status` finds
   the tree busy — and does the merge's closing step remove the worktree?

9. **Secret hygiene.** Are the generated MCP config and the environment file
   ignored? Did a token leak into a committed file, or into history?

10. **Cross-agent availability.** Do the rules live in `AGENTS.md` rather than only
   in a vendor file? Are the skill symlinks present and unbroken, and pointing the
   right way?

11. **Design fidelity.** With a design source: does the component skill extend
    the scale for an off-scale value instead of snapping, forbid inventing
    what the design does not draw, require every interactive state and the
    design's global CSS to be carried over from the source, require a visible
    state wherever something loads, require a layout for real content (long
    names, empty and long lists, narrow widths), and ask for a deviation
    table in the task report? Does the project's own component skill still
    say to snap — a rule an older template left behind? Is there a layout-measuring script, run in the task's browser
    check and in the review command's `layout` mode?

12. **A server's first install.** Does `pnpm install --frozen-lockfile` pass
    on a fresh checkout — not in the developer's tree, where a warm
    `node_modules` hides a build script missing from `allowBuilds`? Once the
    project is deployed, does the root README's Deployment section name the
    production commands, the pinned versions and every variable the build and
    the start need — and does a fresh checkout without an env file agree?

## Report

A table: finding → layer → severity → proposed action. Apply changes after
confirmation, one group at a time, never all at once.

## Hard rules

- **Read-only by default.** Findings first, edits after approval.
- **Do not rewrite a working harness to match a template.** A deliberate
  deviation is a finding only if it is undocumented.
- **Deleting an artefact is proposed, never done silently** — a command that
  looks unused may be someone's weekly ritual.
