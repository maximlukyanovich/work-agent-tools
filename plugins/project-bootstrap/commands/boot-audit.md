---
description: Audit an existing agent harness against the layer model and report what drifted, in priority order.
argument-hint: ''
---

# /boot-audit

The harness exists; the job is to find the gaps, not to rewrite it.
**Read-only** until a change is approved, and then one group at a time.

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

5. **Gaps.** Layers from the model that are absent. Absence is allowed — but it
   must be deliberate and written down, with the conditions that would fill it.

6. **Secret hygiene.** Are the generated MCP config and the environment file
   ignored? Did a token leak into a committed file, or into history?

7. **Cross-agent availability.** Do the rules live in `AGENTS.md` rather than only
   in a vendor file? Are the skill symlinks present and unbroken, and pointing the
   right way?

## Report

A table: finding → layer → severity → proposed action. Apply changes after
confirmation, one group at a time, never all at once.

## Hard rules

- **Read-only by default.** Findings first, edits after approval.
- **Do not rewrite a working harness to match a template.** A deliberate
  deviation is a finding only if it is undocumented.
- **Deleting an artefact is proposed, never done silently** — a command that
  looks unused may be someone's weekly ritual.
