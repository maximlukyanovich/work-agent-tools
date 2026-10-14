---
description: Propose how a scope decomposes into a tree of Jira issues, and the shape of their descriptions, then wait for approval.
argument-hint: '[<scope name or estimate file>]'
---

# /work-jira:plan

Turn a scope into a proposed tree of issues. **Nothing is created here** —
`/work-jira:create` does that, and only after this plan is approved.

`$1` names the scope: an epic to plan, or the estimate file to read it from. Bare
call — ask which part of the estimate to plan, listing what is available.

## Steps

1. **Load the conventions.** The `issues` skill, then
   `.claude/project-profile.md`. If the profile lacks `## Tracker` or
   `## Issues`, run the batch from `${CLAUDE_PLUGIN_ROOT}/reference/first-run.md` first and write the
   answers — do not plan on guesses.

2. **Read the scope.** From the estimate if there is one: task names, hours for
   both scenarios, risks, the provenance of each line. From the spec and design
   if there is not — and say so, because an estimate-less plan carries no hours.

   **Recommended: match the lines against the tracker first.** Search the
   existing issues by each line's name, and the other technology's descriptions
   for the line's name — a backend issue often names "the frontend line X" in
   its scope or out of scope, which is how a pair is found that the summary
   does not reveal. An issue that already does a line's work under another name
   — an earlier, narrower estimate cut the same work differently — is edited to
   carry the line instead of being duplicated; a part carved out of a line
   (`Issue split`) already holds some of its budget. Skip this when the scope
   has no issues yet.

3. **Derive the tree** by the hierarchy rules. For each node: type, summary,
   parent, label, estimate, which technologies it needs, and which issues it
   references — existing keys, or summaries from this tree — since every
   reference becomes a `relates to` link; and which issues it waits on, by the
   `Links` rules of the `issues` skill. Where a story needs both frontend and
   backend but only one is estimated, create the story and the estimated
   sub-task, and say the other is pending — do not invent its hours.

4. **Check the sizes.** Anything past three working days gets split by
   deliverable, and the split is shown with its arithmetic: the parts must sum to
   the original.

5. **Propose the description shape.** The four required sections, plus which
   optional ones this scope needs and why. Show **one worked example** in full —
   a real issue from this tree, not a template with placeholders, with other
   issues written as cards (`[[PROJ-7]]`, `[[@<summary>]]`) and no `Estimate` on
   the epic. That is what the developer is actually approving.

6. **Report and stop.**

   ```
   Epic     <summary>                                    <hours opt/pess>
     Task   [<prefix>] <summary>                         <hours>  <label>
     Story  <summary>
       Sub  [<prefix>] <summary>                         <hours>  <label>
   ```

   Follow it with: the total, how many issues, which are pending a backend
   estimate, which existing issues the plan edits and how, the links each issue will get — the `Blocks` ones as sentences —
   and anything the estimate flagged as a risk on these lines.

7. **Ask three questions**, each with a recommended answer: is the tree right,
   is the description shape right, and which optional sections to include.

8. **End with the next step** once the answers are in:
   `/work-jira:create <epic or plan file>` as a block ready to paste.

## Hard rules

- **Creates nothing.** No issue, no field, no comment. Read-only against Jira.
- **Never invent hours.** A line with no estimate is shown without one.
- **The developer approves the shape**, even the recommended one. Silence is not
  approval.
- **A deviation from the standard is stated as such**, with its reason, not
  slipped in.
