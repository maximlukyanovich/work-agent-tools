---
description: Propose how a scope decomposes into a tree of Jira issues, and the shape of their descriptions, then wait for approval.
argument-hint: '[<scope name or estimate file>]'
---

# /jira-plan

Turn a scope into a proposed tree of issues. **Nothing is created here** —
`/jira-create` does that, and only after this plan is approved.

`$1` names the scope: an epic to plan, or the estimate file to read it from. Bare
call — ask which part of the estimate to plan, listing what is available.

## Steps

1. **Load the conventions.** The `issues` skill, then
   `.claude/project-profile.md`. If the profile lacks `## Tracker` or
   `## Issues`, run the batch from `reference/first-run.md` first and write the
   answers — do not plan on guesses.

2. **Read the scope.** From the estimate if there is one: task names, hours for
   both scenarios, risks, the provenance of each line. From the spec and design
   if there is not — and say so, because an estimate-less plan carries no hours.

3. **Derive the tree** by the hierarchy rules. For each node: type, summary,
   parent, label, estimate, and which technologies it needs. Where a story needs
   both frontend and backend but only one is estimated, create the story and the
   estimated sub-task, and say the other is pending — do not invent its hours.

4. **Check the sizes.** Anything past three working days gets split by
   deliverable, and the split is shown with its arithmetic: the parts must sum to
   the original.

5. **Propose the description shape.** The four required sections, plus which
   optional ones this scope needs and why. Show **one worked example** in full —
   a real issue from this tree, not a template with placeholders. That is what
   the developer is actually approving.

6. **Report and stop.**

   ```
   Epic     <summary>                                    <hours opt/pess>
     Task   [<prefix>] <summary>                         <hours>  <label>
     Story  <summary>
       Sub  [<prefix>] <summary>                         <hours>  <label>
   ```

   Follow it with: the total, how many issues, which are pending a backend
   estimate, and anything the estimate flagged as a risk on these lines.

7. **Ask three questions**, each with a recommended answer: is the tree right,
   is the description shape right, and which optional sections to include.

## Hard rules

- **Creates nothing.** No issue, no field, no comment. Read-only against Jira.
- **Never invent hours.** A line with no estimate is shown without one.
- **The developer approves the shape**, even the recommended one. Silence is not
  approval.
- **A deviation from the standard is stated as such**, with its reason, not
  slipped in.
