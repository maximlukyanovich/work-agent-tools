---
description: Estimate a project from its spec and design handoff — decomposition, bottom-up count, provenance audit, and the markdown report.
argument-hint: '[<scope hint>]'
---

# /work-estimation:project

Produce an estimate. The result is a data module plus a markdown report.

## Steps

1. **Load the method** — the `method` skill — and the profile's `## Estimation`
   section for rates and coefficients. Missing section: ask for the bands and the
   coefficient rates, then write them there.

2. **Inventory the sources.** The spec: every feature, numbered as it numbers
   them. The design handoff: every screen and component, by group. The
   repository: what already exists. Check the bundle version against its source
   before quoting anything from it.

   This step reads a lot and produces a short list. Delegate it to a sub-agent
   when the sources are large — the conclusion is what matters, not the file
   dumps.

3. **Decompose into tasks** by product surface. One task is one to three days of
   work; anything larger is split by deliverable. Every task gets a description
   written for the client.

4. **Count each task bottom-up.** Which of the two rates applies, and why.
   Verification in a browser is inside the hours. **Do not look at any named
   deadline while counting.**

5. **Classify every line** — confirmed, thin, design-only, ours — as you go, not
   afterwards. Doing it afterwards produces flattering answers.

6. **Add the coefficient rows** from the profile's rates. Whole hours, rounded
   up, tests last and computed on the sum.

7. **Write the risks** only where they change the number, and the exclusions
   where the price ends. Collect the open questions.

8. **Emit** the data module and run `${CLAUDE_PLUGIN_ROOT}/scripts/render_md.py <module> <out.md>`.

9. **Only now compare with the deadline**, if one was named, and report the gap
   as a scope question with concrete lines that could move.

## Hard rules

- **The deadline is not an input to the count.** It is a comparison made after.
- **Never invent a requirement** to make a line countable. An undefined area is
  estimated coarsely and the reason is written into its risk.
- **Every line carries a provenance.** No exceptions; "ours" is a valid answer.
- **Nothing is filed anywhere.** Creating issues from this is `/work-jira:plan`.
