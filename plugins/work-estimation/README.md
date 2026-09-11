# work-estimation

Estimate a project from a spec and a design handoff.

## Commands

| Command | What it does |
| --- | --- |
| `/work-estimation:project` | Gathers the scope, decomposes it, counts bottom-up, audits where every line came from, and emits the report. |
| `/work-estimation:update` | Re-runs the numbers after the scope changed: recomputes coefficients, keeps per-task hours untouched. |
| `/work-estimation:export` | Carries an existing estimate into the company workbook. |
| `/work-estimation:help` | What this plugin can do: commands, the estimation method it applies, the data format it expects. Optional language argument. |

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

**Inputs** are whatever the client sent, in any form — documents, spreadsheets,
links, a design bundle. **The deliverable is a markdown report**; the workbook is
optional and produced by `export`. The user chooses which parts are estimated
(frontend, backend, analysis, design, DevOps, QA) and may reshape the table's
columns; the default shape is the company workbook's.

Internally the estimate lives in a python module — tasks, coefficients, risks,
exclusions, questions, provenance — produced by `project`, never written by
hand. It exists so that `update` can narrow the scope as a filter over the full
set and `export` can fill the workbook from the same numbers.

The wording of the report comes from the data module, so its language is the
project's. The built-in fallbacks are still Russian — they are on the list to be
replaced with neutral English defaults.

## Skill

`skills/method` — the full method, including why the deadline must not be looked
at while counting. The agent loads it by itself when an estimate is in play.

`reference/data-format.md` — the module the scripts consume.
