---
description: Carry an estimate into the workbook template, preserving its styles and formulas.
argument-hint: '[<data module>] [<template.xlsx>] [<output.xlsx>]'
---

# /work-estimation:export

Write the estimate into the workbook template.

## Steps

1. **Check the inputs.** The data module, an untouched copy of the template —
   from the argument, else the profile's `Workbook template` in
   `## Estimation`; with neither, ask for its path and offer to record it there —
   its map — the profile's `Workbook map`, else `<template stem>.map.json` beside
   the template; with neither, step 2 proposes one — and an output path that is
   **not** the template. Running twice must give the same result, so the input
   is never the file being produced.

2. **Propose a map** when the template has none. Run
   `${CLAUDE_PLUGIN_ROOT}/scripts/xlsx_outline.py <template>` — its labels,
   headers, formulas and merged ranges; do not open the template otherwise. A
   label marked `(xN)` occurs N times and cannot be a place. Draft the map ("The
   workbook map" in `${CLAUDE_PLUGIN_ROOT}/reference/data-format.md`): match the
   template's column headers to the report's `COLUMNS`, the label above the task
   rows, the lists and the single cells. Write the draft to a scratch file, run
   `xlsx_outline.py <template> <draft>`, and show the user the result as a
   table — template column, header, data key — with the lists and cells under
   it, and name the report's columns the template has no place for. Save the
   map beside the template only on the user's word, and offer to record
   `Workbook map` in the profile's `## Estimation`.

3. **Run** `${CLAUDE_PLUGIN_ROOT}/scripts/build_xlsx.py <module> <template> <map> <output>`. It finds
   the map's labels, inserts the rows, shifts the template's formulas and
   merged ranges to match, sets the workbook to recalculate on open, and
   writes the lists and the map's fields from `WORKBOOK`. On a label it cannot
   find, a `WORKBOOK` key the map does not place, or a list that would
   overwrite the template's text, it exits 1, names it, and writes nothing:
   correct the map, never the template, and show the user the corrected map,
   as in step 2, before running it again.

4. **Verify before handing it over**: the archive opens, every sheet parses, the
   summary formulas cover the new row range, and the hours in the rows sum to the
   totals in the report.

5. **Report** the totals, the file path, the lists the map has no place for —
   the script's `skipped:` lines — the cells left empty — its `empty:` lines,
   with the `WORKBOOK` key that fills each — the task hours rounded up — its
   `rounded up:` lines — and anything the template still
   expects from a human — company name, date, rates.

## Scripts are run, not read

The data module format is documented in `${CLAUDE_PLUGIN_ROOT}/reference/data-format.md`.
Do not open the scripts to learn it — `render_md.py` alone is five thousand
tokens, and everything it needs from the module is in that reference.

## Hard rules

- **The template is read-only.** It is never the output, and it is never
  overwritten "just this once".
- **The map is the user's.** The agent proposes it and the user confirms it; a
  template column without a key is never written.
- **Formulas are shifted, not replaced.** The workbook's own arithmetic is what
  the reader checks; a hand-computed total in a formula cell is a defect.
- **Report the mismatch, do not fix it silently** if the rows and the totals
  disagree.
