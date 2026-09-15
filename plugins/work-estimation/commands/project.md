---
description: Estimate a project from its spec and design handoff — decomposition, bottom-up count, provenance audit, and the markdown report.
argument-hint: '[<scope hint>]'
---

# /work-estimation:project

Produce an estimate. **The deliverable is a markdown report** — totals,
breakdown table, provenance audit, risks, exclusions, open questions. The
workbook is a separate, optional step: `/work-estimation:export`.

## Inputs

Whatever the client sent, in whatever form: `.docx`, `.xlsx`, `.pdf`, markdown,
a Google Docs or Drive link, a slide deck, a design bundle, Figma, screenshots
with prose. Read all of it; do not ask for a conversion. If a format cannot be
read, say which one and why, and continue with the rest.

## Steps

1. **Load the method** — the `method` skill — and the profile's `## Estimation`
   section for rates and coefficients. Missing section: ask for the bands and the
   coefficient rates, then write them there.

2. **Agree the frame before counting.** Two questions, each with a default:

   - **Which parts are estimated?** Frontend, backend, business analysis, design,
     DevOps, QA — any subset. Each becomes a `PART OF` value in the table with its
     own rates. Default: ask; never assume frontend-only.
   - **Which columns?** Default is the company workbook's shape: part of, epic,
     task, description, optimistic, pessimistic, negative risk, positive risk. The
     user may add, drop or rename columns; record the chosen shape in the report
     header so `export` knows what it is looking at.

3. **Inventory the sources.** The spec: every feature, numbered as it numbers
   them. The design handoff: every screen and component, by group. The
   repository: what already exists. Check the bundle version against its source
   before quoting anything from it.

   This step reads a lot and produces a short list. Delegate it to a sub-agent
   when the sources are large — the conclusion is what matters, not the file
   dumps.

4. **Decompose into tasks** by product surface, within each estimated part. One
   task is one to three days of work; anything larger is split by deliverable.
   Every task gets a description written for the client.


5. **Count each task bottom-up.** Which of the two rates applies, and why.
   Verification in a browser is inside the hours. **Do not look at any named
   deadline while counting.**

6. **Classify every line** — confirmed, thin, design-only, ours — as you go, not
   afterwards. Doing it afterwards produces flattering answers.

7. **Add the coefficient rows** from the profile's rates. Whole hours, rounded
   up, tests last and computed on the sum.

8. **Write the risks** only where they change the number, and the exclusions
   where the price ends. Collect the open questions.

9. **Emit the report.** Write the data module — the internal form the scripts
   consume, so that `update` and `export` work later — and render the markdown
   with `${CLAUDE_PLUGIN_ROOT}/scripts/render_md.py <module> <out.md>`. Hand the
   user the markdown; the module is mentioned, not presented.

10. **Only now compare with the deadline**, if one was named, and report the gap
   as a scope question with concrete lines that could move.

## Scripts are run, not read

The data module format is documented in `${CLAUDE_PLUGIN_ROOT}/reference/data-format.md`.
Do not open the scripts to learn it — `render_md.py` alone is five thousand
tokens, and everything it needs from the module is in that reference.

## Hard rules

- **The deadline is not an input to the count.** It is a comparison made after.
- **Never invent a requirement** to make a line countable. An undefined area is
  estimated coarsely and the reason is written into its risk.
- **Every line carries a provenance.** No exceptions; "ours" is a valid answer.
- **Nothing is filed anywhere.** Creating issues from this is `/work-jira:plan`.
