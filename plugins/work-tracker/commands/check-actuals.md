---
description: Hours logged on a selection of issues against their estimate — a local HTML report, rebuilt by one command.
argument-hint: '[<selection> | <report.json>]'
---

# /work-tracker:check-actuals

How the estimate held up: the hours logged on a selection of issues against
their optimistic and pessimistic estimates, as one page in
`docs/local/actuals/<name>_<YYYYMMDD>.html`. The files and every field:
`${CLAUDE_PLUGIN_ROOT}/reference/actuals.md`. Read-only on the tracker.

## Steps

1. **The adapter**, by "The adapter" in the `issues` skill. One without the
   `worked` operation stops the command, by the contract.

2. **A rebuild** — `$1` is a report file: keep everything it holds, fetch
   again (step 4) and build (step 7). Every `looks dropped` and `no readiness`
   line the build prints is a question still open, however old the issue:
   ask them in one questionnaire, record the answers (step 6) and build again.

3. **The selection** from the argument and the conversation — assignee, label,
   epic, version, period, status, or the user's own query — turned into the
   tracker's query; `<name>` is a short slug of it. Name what it leaves out;
   when it holds stories with sub-tasks, say where the time is logged —
   `spent` does not add up sub-tasks.

4. **Fetch** into `docs/local/actuals/<name>.issues.json` with the description
   and the worklogs — `worked` with both; the answer goes to the file, never
   through the conversation.

5. **One questionnaire**, with what the file shows (read it with `jq`):
   - **dropped-looking issues** — resolved as Won't Do, Duplicate or the
     like, a bracketed marker opening the summary, a label saying so: leave
     them out? Out goes into the query, or `exclude` where it cannot say it;
     kept goes into `keep`, so it is not asked again;
   - **readiness of the issues in progress** with no ticked item in the
     description — the script takes the share of ticked items — and none in
     the project's plan of the issue, where the profile keeps one: a field per
     issue, percent of its scope; left empty it is recorded as `null` — "—",
     not asked again;
   - **the estimates** — the issues' descriptions (read two or three with
     `jq`; offered when they state hours), the estimate field (offered with
     how many issues have it), or the user's own — a table, a file they point
     at, story points at their rate of hours: the `manual` source. With no
     estimate in the tracker the user's own is the only option, and the
     command asks for it rather than looking for files;
   - **the additional sections**, several at once — overrun over time by
     closing date, a breakdown by people or by epics, open issues already over
     the estimate, hours by period — with a field for the user's own.

6. **Write the report** — `docs/local/actuals/<name>.json`, by the reference:
   - `description`: `patterns` that match the descriptions read; each `no
     estimate in the description` line of step 7 is a pattern to widen before
     it is a fact.
   - `dev_done` — the statuses that count as development done, from the
     profile's tracker statuses, asked once if it names none; `readiness` —
     the plan's or the user's percent for an issue in progress; a ticked list
     needs none.
   - `notes` and `source_note` — facts of this project only: what its
     estimates include as the estimate, the description or the profile states
     it, and, when the profile or the project's rules cap logged time at the
     estimate, that the fact is a lower bound. Nothing stated — no line; never
     a sentence carried over from another report.
   - `reasons` — for each closed issue over the optimistic and not yet there:
     read its comments through `read` and its worklogs in the issues file;
     one line in the report's language, in your own words, the role (designer,
     backend, client) and never a name, linked to the comment or worklog it
     comes from; above the pessimistic it explains both. None stated — an
     empty `text`.
   - **Language** — the conversation's. Without a strings file for it,
     translate `${CLAUDE_PLUGIN_ROOT}/scripts/actuals/en.json` into
     `docs/local/actuals/strings.<lang>.json` once — keys unchanged, `locale`
     set — and name it in `strings`.

7. **Build**: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/actuals.py docs/local/actuals/<name>.json`.
   Act on each line it prints before the page's URL, by the reference, and
   build again until only what cannot be fixed remains.

8. **Report in five lines at most** — every detail is on the page:
   - the page as a link whose text is its path from the project root, and the
     `file://` URL the script printed, to open in a browser;
   - what was analysed — the selection in words and the closing dates the
     script printed;
   - the sections the page holds;
   - the tiles' figures in one line: closed, within each estimate, the fact
     against them, the deviation;
   - what was left out and why, only when something was.

   Then ask whether anything needs a pinpoint fix — a reason's wording, a
   readiness, a note, an issue to leave out: each goes into the report file
   and the page is built again (step 7), without fetching. End with the
   rebuild as a block ready to paste:
   `/work-tracker:check-actuals docs/local/actuals/<name>.json`.

## Scripts are run, not read

The formats are in `${CLAUDE_PLUGIN_ROOT}/reference/actuals.md`. Do not open
`actuals.py` or `actuals.html` to learn them.

## Hard rules

- **Nothing is written to the tracker** — no log, status or comment.
- **The fact is what was logged.** Never corrected by what "really" happened.
- **No names in the reasons.** A breakdown by people is the user's choice and
  shows the assignee; a reason never does.
- **The template is not edited for one report.** What the page lacks is a
  section in `custom`, or a change to this plugin.
