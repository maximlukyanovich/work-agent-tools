# The data module

One python module holds an estimate. The scripts read it; nothing else is a
source of truth. Keeping it as code rather than a spreadsheet is what makes a
re-count a one-line change instead of an afternoon.

## Required

```python
TASKS = [
    (
        "Epic name",                    # product surface
        "Task name",                    # goes to the report and to Jira
        "Description for the client.",  # what exists when this is done
        6, 9,                           # optimistic, pessimistic — whole hours
        "Negative risk, or empty",      # only where it changes the number
        "Positive risk, or empty",      # only where it changes the number
    ),
    ...
]

RESPONSIVE_RATE = 0.25      # project settings
I18N_RATE = 0.05
TESTS_RATE = 0.05

DERIVED = [                 # the coefficient rows, in report order
    ("Cross-cutting", "Responsive & mobile layout", "…", "responsive", "", ""),
    ("Cross-cutting", "Localization",               "…", "i18n",       "", ""),
    ("Cross-cutting", "Automated tests",            "…", "tests",      "", ""),
]

ORIGIN = {"Task name": "both"}   # both | spec | design | ours — the audit

RISKS = ["…"]        # risks that apply to the estimate as a whole
EXCLUDES = ["…"]     # what the price does not include
QUESTIONS = ["…"]    # what has to be answered before this firms up


def totals():
    """Whole hours. Coefficients rounded up; tests computed on the sum."""
```

## Optional

`ORIGIN_NOTE` — one line per task on where exactly it came from, shown in the
audit. `SPEC_NOT_BROKEN_OUT` — spec items folded into other tasks, so a reader
looking for them in the breakdown finds out where they went. `SCREEN_MAP` —
which tasks make up one approved screen, for the inevitable question "where is
that page in this plan?". `TITLE`, `INTRO`, `SCOPE`, `TIMELINE_NOTE`,
`RATES_NOTE`, `EXPENSIVE_NOTE` — texts that depend on the scope, overriding the
defaults in the renderer.

## Narrowing the scope

A filter module imports the full one and keeps a named subset:

```python
import data

KEEP = ["Project bootstrap", "Design system foundation", ...]
TASKS = [t for t in data.TASKS if t[1] in KEEP]

OVERRIDES = {...}   # a task whose scope shrank with the cut
EXTRA = [...]       # something the cut made necessary
```

Coefficients recompute from the new sum; per-task hours are untouched. The full
estimate stays as the upper bound, in its own file.

## Language

The report's wording comes from this module, so its language is the project's.
The renderer's built-in fallbacks are English.
