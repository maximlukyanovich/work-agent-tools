# estimation

Estimate a project from a spec and a design handoff.

## Commands

| Command | What it does |
| --- | --- |
| `/est-project` | Gathers the scope, decomposes it, counts bottom-up, audits where every line came from, and emits the report. |
| `/est-update` | Re-runs the numbers after the scope changed: recomputes coefficients, keeps per-task hours untouched. |
| `/est-export` | Carries an existing estimate into the company workbook. |
| `/est-help` | What this plugin can do: commands, the estimation method it applies, the data format it expects. Optional language argument. |

## Method

- **Two rates of work, not one coefficient.** Routine with design code already
  written is one rate; decisions and sensitive logic — money, realtime, price
  caching — are another.
- **Count bottom-up.** Comparing the total against a named deadline before the
  count is finished is forbidden: the estimate gets nudged silently and large
  lines end up understated by a factor of three.
- **Provenance audit.** Four groups: confirmed by both spec and mockup; one
  sentence in the spec with no mockup; taken from the design, absent from the
  spec; present in neither. The size of groups two and three is the strongest
  argument in a scope conversation.
- **Coefficients as their own rows**, whole hours, rounded up.

## Scripts

| File | What it does |
| --- | --- |
| `scripts/render_md.py <data module> <out.md>` | The markdown report: totals, breakdown, provenance audit, risks, exclusions, questions. |
| `scripts/build_xlsx.py <data module> <template.xlsx> <out.xlsx>` | Carries the same data into the estimate workbook, preserving its styles and formulas. |

Data lives in a single python module: tasks, coefficients, risks, exclusions,
questions and the provenance map. Narrowing the scope is a filter module on top
of the full set, never a hand-edited copy.

The wording of the report comes from the data module, so its language is the
project's. The built-in fallbacks are still Russian — they are on the list to be
replaced with neutral English defaults.

**Status:** scripts carried over from a live project; the command and the skill
are being written.
