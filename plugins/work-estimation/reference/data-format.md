# The data module

**Internal format.** The `project` command writes it; a person never does. It
exists so that `update` and `export` work from the same numbers as the report.
One python module holds an estimate; the scripts read it through
`estimate_data.py`, which is the only place the shape is interpreted.

## Required

```python
TASKS = [
    # one part, the common case — 7 elements, part comes from PART below
    (
        "Epic name",                    # product surface
        "Task name",                    # goes to the report and to Jira
        "Description for the client.",  # what exists when this is done
        6, 9,                           # optimistic, pessimistic — whole hours
        "Negative risk, or empty",      # only where it changes the number
        "Positive risk, or empty",      # only where it changes the number
    ),
    # several parts — 8 elements, part first
    ("Backend", "Epic", "Task", "Description.", 16, 24, "", ""),
]
PART = "Frontend"           # default part for 7-element rows

RESPONSIVE_RATE = 0.25      # project settings; 0 switches a coefficient off
I18N_RATE = 0.05
TESTS_RATE = 0.05

DERIVED = [                 # the coefficient rows, in report order
    ("Cross-cutting", "Responsive & mobile layout", "…", "responsive", "", ""),
    ("Cross-cutting", "Localization",               "…", "i18n",       "", ""),
    ("Cross-cutting", "Automated tests",            "…", "tests",      "", ""),
]
DERIVED_PART = "Frontend"   # which part the coefficients belong to and are computed from
```

Coefficients are whole hours, rounded up; tests are computed last, on the sum.
With several parts they are computed from `DERIVED_PART`'s development sum only.

## Shape of the report

```python
COLUMNS = [                 # default: these eight
    ("part", "PART OF"), ("epic", "EPIC / FEATURE"), ("task", "TASK / USER STORY"),
    ("description", "DESCRIPTION"), ("optimistic", "OPT"), ("pessimistic", "PESS"),
    ("negative", "RISKS: NEGATIVE"), ("positive", "RISKS: POSITIVE"),
]
```

Drop, reorder or rename freely; keys are fixed, headers are yours. The
workbook export writes the columns its map names — that sheet is the
template's, not the report's.

## Audit and lists

```python
ORIGIN = {"Task name": "both"}      # both | spec | design | ours — per task
ORIGIN_NOTE = {"Task name": "…"}    # optional one-liner shown in the audit
SPEC_NOT_BROKEN_OUT = [("Spec item", "where it went")]
RISKS = ["…"]        # risks that apply to the estimate as a whole
EXCLUDES = ["…"]     # what the price does not include
QUESTIONS = ["…"]    # what has to be answered before this firms up
```

## Wording

Every default text in the renderer is English. The module overrides any of
them, so the report's language is the project's:

```python
TITLE = "…"
INTRO = ["line", "line"]            # after the title
SCOPE = ["line", …]                 # the Scope section body
RATES_NOTE = ["- **…** …", …]        # the two rates, in the project's words
TIMELINE_NOTE = ["line", …]         # after the weeks line
SECTIONS = [("Title", ["line", …])]  # the project's own sections, after Scope
LABELS = {"summary": "Итог", …}     # any label key from render_md.py
HOURS_PER_MONTH = 170
HOURS_PER_WEEK = 40
```

## The workbook

Read by `export` only. The texts are in the workbook's language, which is not
always the report's: the report's `TIMELINE_NOTE` is not reused.

```python
WORKBOOK = {                                     # the keys are the map's fields
    "timeline": "13–19 weeks (frontend only)",   # default: the report's weeks, "12–18 weeks"
    "stack": "Frontend: …",                      # no default
}
```

A field of the map left out of `WORKBOOK` leaves its cell empty, and the script
names it — `empty: WORKBOOK["stack"] -> B56` — so no cell carries another
project's text. Only `timeline` has a default. A key the map does not place
stops the run before anything is written.

## The workbook map

Where the estimate goes in one template: a JSON file beside it,
`<template stem>.map.json`, or the profile's `Workbook map`. The template is
never adapted to the script; the map is. `export` proposes it the first time,
from `xlsx_outline.py`, and the user confirms it.

```json
{
  "sheet": "Estimate",
  "tasks": {
    "label": "Tasks", "down": 2, "rows": 2,
    "columns": {"B": "epic", "C": "task", "D": "optimistic", "E": "pessimistic"}
  },
  "lists": {
    "RISKS": {"label": "Risks:", "down": 1, "rows": 1},
    "QUESTIONS": {"sheet": "Questions", "label": "Open questions", "down": 1, "number": "A"}
  },
  "fields": {
    "timeline": {"label": "Timeline:", "right": 1}
  }
}
```

- **A place** is `{"label": "<text>", "down": n, "right": n}`: the cell that
  holds the text, moved by the offsets — 0 by default, counted from the
  top-left cell of a merged label. The text is matched exactly, without
  surrounding spaces, and must occur once on its sheet; missing or repeated,
  the run stops before writing and names the label, the sheet and the cells.
- **`sheet`** — the sheet of the task rows, by name; the first by default.
- **`tasks`** — the place of the first task row. `rows` — how many task rows
  the template has; the last is cloned for every row of the estimate, and a
  formula that reaches it grows with the block. `columns` — letter to row
  key: `part`, `epic`, `task`, `description`, `optimistic`, `pessimistic`,
  `negative`, `positive`; the hours are written as numbers. A column without
  a key — a cost, a formula — is never written.
- **`lists`** — `RISKS`, `EXCLUDES`, `QUESTIONS`. The place is the list's first
  row, and the text goes in its column.
  - With `rows`, on the task sheet only: that many blank rows; more items
    insert clones of the first, each merged as it is.
  - Without `rows`: the items go into the rows under the place, on any sheet.
    A cell on the way that holds anything stops the run: the list would
    overwrite the template's text.
  - `number` — a column for 1, 2, 3…; optional.
  - A list with no place is skipped and named:
    `skipped: EXCLUDES (13) - no place in the map`.
- **`fields`** — a `WORKBOOK` key to its place; `sheet` as for a list.
- A row or a cell the template does not store is created, without a style; a
  list's number takes the style of its text.
- A key the script does not know, at any level, stops the run with its name.

## Narrowing the scope

A filter module imports the full one and keeps a named subset:

```python
import data

KEEP = ["Project bootstrap", "Design system foundation", ...]
TASKS = [t for t in data.TASKS if t[1] in KEEP]
PART, DERIVED, RESPONSIVE_RATE, I18N_RATE, TESTS_RATE = (
    data.PART, data.DERIVED, data.RESPONSIVE_RATE, data.I18N_RATE, data.TESTS_RATE)

OVERRIDES = {...}   # a task whose scope shrank with the cut
EXTRA = [...]       # something the cut made necessary
```

Coefficients recompute from the new sum; per-task hours are untouched. The full
estimate stays as the upper bound, in its own file.
