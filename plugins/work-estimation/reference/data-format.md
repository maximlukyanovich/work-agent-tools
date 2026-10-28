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
COLUMNS = [                 # default is the workbook's eight columns
    ("part", "PART OF"), ("epic", "EPIC / FEATURE"), ("task", "TASK / USER STORY"),
    ("description", "DESCRIPTION"), ("optimistic", "OPT"), ("pessimistic", "PESS"),
    ("negative", "RISKS: NEGATIVE"), ("positive", "RISKS: POSITIVE"),
]
```

Drop, reorder or rename freely; keys are fixed, headers are yours. The
workbook export always writes the eight workbook columns regardless — that
sheet is the template's, not the report's.

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
WORKBOOK = {
    "timeline": "13–19 weeks (frontend only)",  # K9; default: the report's weeks, "12–18 weeks"
    "timeline_note": "…",                        # I10, under the timeline; default: empty
    "stack": "FRONT-END: …",                     # B56, under TECH STACK; default: empty
}
```

A key left out leaves its cell empty, and the script names it —
`empty: WORKBOOK["stack"] -> B56` — so no cell carries another project's text.
A key it does not know stops the run before anything is written.

One template layout is supported — the corporate estimate workbook, known by
its labels: `I9` "Overall Expected Timeline:", `B30` "Development", `B47` "Risks
which may cause estimation changes:", `B50` "Excludes:", `B55` "TECH STACK".
The script checks them first; on any other template it names the cell, the
label expected and the one found, and writes nothing. Under those labels the
rows go to rows 32 onwards, the eight `COLUMNS` keys to B–I, `RISKS` and
`EXCLUDES` to the blank rows under their headers — more rows are inserted when
needed — and `QUESTIONS` to the second sheet.

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
