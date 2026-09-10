---
description: Recompute an estimate after the scope changed — coefficients from the new sum, per-task hours untouched.
argument-hint: '[<data module>]'
---

# /est-update

Re-run the numbers when the composition changes: a module dropped, a line
returned, a task added.

## Steps

1. **Read the current module** and the profile's rates.

2. **Apply the change as a filter, not a rewrite.** A narrowed scope is a module
   that imports the full one and keeps a named subset. The full estimate stays
   as the upper bound in its own file.

3. **Keep per-task hours.** A line that survives the cut keeps its number; a line
   that returns brings its original number back. Only the composition changed.

4. **Recompute the coefficients** from the new development sum. Whole hours,
   rounded up, tests on the sum.

5. **Re-run the audit.** The provenance mix shifts when lines leave — the share
   of thin and design-only work is rarely the same afterwards.

6. **Regenerate the report** and state the delta plainly: what was, what is,
   which lines moved and why.

## Hard rules

- **Never re-derive hours that were not questioned.** Changing them while
  changing the scope hides one change behind the other.
- **Both files stay.** The full estimate is the upper bound; deleting it loses
  the ceiling.
- **A dropped line is recorded**, with what it would cost to bring back.
