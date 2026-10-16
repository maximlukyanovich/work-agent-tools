---
description: Carry an estimate into the workbook template, preserving its styles and formulas.
argument-hint: '[<data module>] [<template.xlsx>] [<output.xlsx>]'
---

# /work-estimation:export

Write the estimate into the workbook template.

## Steps

1. **Check the inputs.** The data module, an untouched copy of the template, and
   an output path that is **not** the template. Running twice must give the same
   result, so the input is never the file being produced.

2. **Run** `${CLAUDE_PLUGIN_ROOT}/scripts/build_xlsx.py <module> <template> <output>`. It inserts the
   rows, shifts the template's formulas and merged ranges to match, sets the
   sheet to recalculate on open, and fills the questions sheet.

3. **Verify before handing it over**: the archive opens, every sheet parses, the
   summary formulas cover the new row range, and the hours in the rows sum to the
   totals in the report.

4. **Report** the totals, the file path, and anything the template still expects
   from a human — company name, date, rates.

## Scripts are run, not read

The data module format is documented in `${CLAUDE_PLUGIN_ROOT}/reference/data-format.md`.
Do not open the scripts to learn it — `render_md.py` alone is five thousand
tokens, and everything it needs from the module is in that reference.

## Hard rules

- **The template is read-only.** It is never the output, and it is never
  overwritten "just this once".
- **Formulas are shifted, not replaced.** The workbook's own arithmetic is what
  the reader checks; a hand-computed total in a formula cell is a defect.
- **Report the mismatch, do not fix it silently** if the rows and the totals
  disagree.
