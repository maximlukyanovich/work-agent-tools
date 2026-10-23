---
description: Audit an existing agent harness against the layer model and report what drifted, in priority order; read the project's efficiency journal.
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

**The efficiency journal is read in either mode** — section 14 below.

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
   Does a finding whose mechanism a ledger already holds end the report with
   a proposal to move it upstream?
   Does the commit command, after a task's last commit, hand over the review
   command with its range — from the last reviewed head after the first pass
   — or is the review left to someone's memory? Does a delta pass count, not
   list, the missed minors and nits in lines it does not change, and mark a
   cheap and real one `fix-now`?
   And the other half: when findings are fixed — usually in the working
   session, from a pasted report — does a rule in `AGENTS.md` load the testing
   skill first, and does that skill carry the round — a budget that limits
   added measures, not fixes; the narrow fix; proof by risk; every state the
   fix touches, with a transition table before any edit to state — rows for
   the frame closed, reopened or remounted while a call is in flight among
   them; one read of the round's diff — and a proof table the commit command
   shows? Without it, each pass's fixes become the next pass's `major`s, or
   a round on a small task takes hours. Does the review end with the next
   step — the fix-round prompt that names the ledger, or the merge command
   first and the `fix-now` round second — through `/work-bootstrap:handoff`,
   rather than a report to paste back?
   Does a ready verdict read the plan and the task's notes before the merge
   command, and print "continue the task" while work is left? Does the
   review command say that no new work lands on a branch while its fix round
   is open, and does the commit command hand over the review alone, leaving
   what follows to the review?
   Do review groups go to `.claude/agents/review-group.md` with
   `model: inherit` — not pinned to a cheaper model — with `model=` to
   override it and refutation left to the session?

6. **Where the gate runs.** Does the commit command run the targeted checks
   of the changed paths, with the full gate only for a path no row covers —
   and do the review and the push run the full gate once per tree, skipping
   a tree already recorded green? Does every code path have a targeted row
   whose command narrows, and does a gate of several parts skip a part whose
   content is unchanged? Does a fix to a commit not yet pushed go into that
   commit, do review fixes go into one fix commit that later rounds amend,
   and does the review command read a head rewritten that way as
   `git diff <last head> HEAD`? Is a git hook running the whole gate —
   minutes per push, soon bypassed? Does lint-staged run the formatter after
   the linter's fixes? The wrong order leaves linter edits unformatted while
   the hook passes. Does the commit command compare the index with its
   proposed list right before committing? A commit the `commit-msg` hook
   refused keeps its paths staged, and without the check the next commit
   carries them in. Do commit, review and merge take a target — a branch or
   a worktree path — and run their git calls and the gate in that tree?
   Does every command end with its next step as a block ready to paste, and
   does a stop that sends to another command print that command as one?

7. **Gaps.** Layers from the model that are absent. Absence is allowed — but it
   must be deliberate and written down, with the conditions that would fill it.

8. **A merge that ends in silence.** Does every command that merges offer the
   closing steps afterwards — result comment, worklog, branch deletion,
   anything raised for another team? A command that merges and stops is how
   issues end up delivered but undocumented and untracked, and the gap is
   invisible precisely because the code shipped.
   The mirror check: does the command that starts a task offer the opening
   steps — the in-progress transition, the assignee, the parent's status —
   when a tracker is reachable, and load `kickoff` before it asks — and does
   its plan carry the state table, the framework pointers and the structural
   line? Does it
   take a `worktree` argument and offer one when a live `git status` finds
   the tree busy — does its setup generate the ignored framework types, give
   the dev server and the end-to-end run their own port and a Compose stack
   its own `COMPOSE_PROJECT_NAME` in the `.env` Compose reads, not a
   service's `env_file:` — each in a file copied into the tree rather than
   linked — and does the merge's closing step remove the worktree?

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
    `node_modules` hides a build script missing from `allowBuilds` — and does
    the type-check pass there, where no generated types exist yet? Once the
    project is deployed, does the root README's Deployment section name the
    production commands, the pinned versions and every variable the build and
    the start need — and does a fresh checkout without an env file agree?

13. **A fresh clone gets its plugins.** Does the settings file declare every
    marketplace `enabledPlugins` names, the library's with `autoUpdate`?
    Does the onboarding command install the declared plugins the checkout
    lacks — at local scope, on a yes, leaving one turned off here alone and
    never adding a marketplace by hand — print `AGENTS.md` §2's commands as
    blocks, and list the plugins' commands from their files rather than
    from the session's list?

14. **The efficiency journal.** Do `docs/local/efficiency-remarks.md` and its
    line in `AGENTS.md` §6 exist? Then read the rows not yet marked analysed
    and group them by cause:
    - a cause in this project — a rule, a skill, a command, a hook, a profile
      key, a check that does not narrow — is a finding of this audit, with
      its edit;
    - a cause in a library plugin goes into **one** issue draft for that
      library's repository (its `plugin.json` `repository`), the whole
      audit's worth: the mechanism and the proposed change, with no project
      or company name, issue key, path or quote — the library's issues are
      public. The draft is shown verbatim and filed with `gh issue create`
      only on an explicit yes; without `gh`, the draft and the repository's
      new-issue link are printed. When the session's instructions name
      another route for library proposals, the draft goes there instead.

    The analysed rows get the audit's date in their last column.

## Report

A table: finding → layer → severity → proposed action. Apply changes after
confirmation, one group at a time, never all at once.

End with the next step as a block: changes applied — `/reload-skills` when a
command or skill changed, the project's commit command in this same session,
then `/work-bootstrap:handoff`; the report alone — the instruction that
applies the proposed changes.

## Hard rules

- **Read-only by default.** Findings first, edits after approval.
- **Do not rewrite a working harness to match a template.** A deliberate
  deviation is a finding only if it is undocumented.
- **Deleting an artefact is proposed, never done silently** — a command that
  looks unused may be someone's weekly ritual.
