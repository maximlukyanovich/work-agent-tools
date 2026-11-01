# The hours report files

What `scripts/actuals.py` reads. A report is three files side by side in
`docs/local/actuals/`, named after the selection: `<name>.json` — the report,
`<name>.issues.json` — the issues, `<name>_<YYYYMMDD>.html` — the page, dated
by its build, so a rebuild on another day leaves the earlier page as it was.
The report holds every decision taken for it, so a rebuild asks nothing again.

## The issues

A list, written by the adapter's `worked` operation — never by hand. Hours are
decimal.

```json
[{
  "key": "PROJ-7", "url": "https://…/browse/PROJ-7", "summary": "Results grid",
  "type": "Task", "status": "In Progress", "category": "progress",
  "labels": ["Frontend"], "parent": {"key": "PROJ-2", "summary": "Results"},
  "assignee": "Name", "estimate": 6.0, "spent": 7.5,
  "resolution": "Done", "resolved": "2026-10-30",
  "text": "the description as plain text, task items as [x] / [ ] — on request",
  "worklogs": [{"id": "…", "author": "Name", "date": "2026-10-29", "hours": 2.5,
                "text": "…", "url": "…"}]
}]
```

`category` is `todo`, `progress` or `done` — the tracker's status category,
not its status name. `estimate` is the tracker's estimate field in hours;
`spent` is the time logged on the issue itself, sub-tasks not included.
`parent`, `assignee`, `estimate`, `resolution` and `resolved` may be `null`; `text` and
`worklogs` are present only when asked for.

## The report

```json
{
  "title": "Frontend hours: actual against the estimate",
  "language": "en",
  "strings": null,
  "selection": "label Frontend, the MVP scope",
  "query": "project = PROJ AND labels = Frontend AND issuetype != Epic",
  "issues": "frontend.issues.json",
  "source": "description",
  "patterns": ["Optimistic:\\s*(?P<opt>\\d+(?:[.,]\\d+)?)\\s*h,\\s*pessimistic:\\s*(?P<pess>\\d+(?:[.,]\\d+)?)"],
  "estimates": {"PROJ-9": [4, 6]},
  "source_note": "Estimates come from the Estimate paragraph of each issue.",
  "dev_done": ["Ready for QA"],
  "readiness": {"PROJ-12": 40},
  "exclude": ["PROJ-31"],
  "keep": ["PROJ-40"],
  "groups": {"PROJ-30": "Mobile layout"},
  "reasons": {"PROJ-7": {"text": "Two states the mockup lacked, agreed with the designer.", "url": "…"}},
  "sections": ["cumulative", "breakdown", "open", "periods"],
  "breakdown": "epics",
  "period": null,
  "custom": [{"request": "…", "title": "…", "caption": "…", "columns": ["Key", ["Hours", 1]], "rows": [["PROJ-7", 7.5]]}],
  "notes": ["Estimates include automated tests, 5% of development."]
}
```

A field set to `null` counts as left out.

- **`language`** — the user's, as the conversation shows it. The plugin ships
  `en` and `ru`; another language is a translation of `scripts/actuals/en.json`
  kept in the project and named in **`strings`**, relative to the report — keys
  unchanged, `locale` set to the language's tag, which also sets the number and
  date format. A key the translation lacks falls back to English and is named.
  `title`, `source_note`, `reasons`, `notes` and `custom` are written in that
  language.
- **`selection`** and **`query`** — what the user asked for, in words, and the
  tracker query that answers it. A rebuild runs the same query.
- **`source`** — where the estimates come from:
  - `description` — the issue's text; `patterns` are regular expressions with
    a group `opt` and an optional `pess` — without it the estimate is single.
    The match furthest into the text wins: after a split the paragraph ends
    with the new pair. An issue with no match takes the tracker's field, named.
  - `tracker` — the tracker's estimate field: always a single estimate.
  - `manual` — `estimates` the user gave, by key: `[opt, pess]`, `[opt]` or a
    number — from a table, a file they point at, or story points at their
    rate of hours.

  An estimate of 0 counts as none.
- **`dev_done`** — statuses before `done` that count as 100% done: development
  handed over to testing. **`readiness`** — percent done of an issue in
  progress, from the project's plan of it or the user; without one the share
  of ticked items in its description — a list with no tick says nothing;
  neither — "—". `null` records "asked, unknown".
- **`exclude`** — keys left out of the page: a dropped issue the query cannot
  leave out itself. **`keep`** — dropped-looking keys the user kept.
- **`groups`** — an issue's table group when its epic is not where it belongs.
- **`reasons`** — why a closed issue went over the optimistic — and, above the
  pessimistic, over both: one line, the role and not the name, `url` to the
  comment or the worklog it comes from. An entry with an empty `text` means
  "read, nothing stated".
- **`sections`** — the additional sections: `cumulative` — overrun by closing
  date; `breakdown` — by `"people"` (assignee) or `"epics"`; `open` — open
  issues above the optimistic; `periods` — hours logged by `"week"` or
  `"month"`; `period: null` picks month for a span over twelve weeks.
  **`custom`** — a section the user asked for in their own words: a table the
  agent computes from the issues; `request` is recomputed on a rebuild. A
  column is a header, or `[header, 1]` for a number; a row has a cell per
  column.
- **`notes`** — lines under the table, each a fact of this project: what its
  estimates include, that the fact is a lower bound when the project caps logs
  at the estimate. What "—" means is the page's own line, by the source.

## What the script prints

First one line per thing to look at: `looks dropped` (resolved as Won't Do,
Duplicate or the like, or a bracketed marker opening the summary — not in
`keep`), `no readiness` (in progress with neither a value, `null` included,
nor a ticked list), `no estimate`, `pess below opt` (taken as a single
estimate), `no estimate in the description` (the field taken), `estimate
differs` (description against the field), `no hours` (closed with nothing
logged — the time may be on sub-tasks), `no reason` (closed over the
optimistic with no entry in `reasons`), `no closing date` (closed without a resolution date — left out of
the overrun over time), `periods` (no worklogs in the issues file), `strings`
(keys a translation lacks). Then the page's `file://` URL and the figures of
its tiles: issues closed and between which dates, how many within each
estimate, the fact against the estimates, the mean and by-sum deviation, the
place in the range.

An entry of `estimates`, `reasons` or `custom` in the wrong form stops the
build, naming the field and the key or the section.
