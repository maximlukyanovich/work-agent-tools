# -*- coding: utf-8 -*-
"""Render an estimate into a markdown report.

    render_md.py <data module> <output.md>

Every default text below is English and every one of them can be overridden by
the data module, so the report's language is the project's. Sections come in a
fixed order; the module can add its own through `SECTIONS`.

Module-level overrides, all optional:

    TITLE, INTRO (list of lines), SCOPE (list of lines), RATES_NOTE (list of lines),
    TIMELINE_NOTE (list of lines), SECTIONS (list of (title, [lines])),
    ORIGIN ({task: "both"|"spec"|"design"|"ours"}), ORIGIN_NOTE ({task: line}),
    SPEC_NOT_BROKEN_OUT ([(item, where)]), RISKS, EXCLUDES, QUESTIONS,
    HOURS_PER_MONTH (default 170), HOURS_PER_WEEK (default 40), LABELS (dict).
"""

import sys

from estimate_data import NUMERIC, Estimate

if len(sys.argv) < 3:
    sys.exit("usage: render_md.py <data module> <output.md>")

E = Estimate(sys.argv[1])
OUT = sys.argv[2]

# ------------------------------------------------------------------ labels
L = {
    "title": "Estimate",
    "summary": "Summary",
    "row": "Row",
    "optimistic": "Optimistic",
    "pessimistic": "Pessimistic",
    "development": "Development",
    "tasks_in_epics": "{n} tasks in {e} epics",
    "part_total": "{part}, total",
    "grand_total": "Total",
    "timeline": "One developer at {hpm} hours a month — **{weeks} weeks**.",
    "roles_note": "Project roles (QA, management, analysis, communication) are not in "
                  "these numbers.",
    "method": "How the hours were counted",
    "rates_default": [
        "- **Routine** — porting components and screens that already exist as working "
        "code in the design handoff, forms, CRUD sections, static blocks. The work is "
        "posing the task to an agent and checking the result in a browser.",
        "- **Decisions and sensitive logic** — money, realtime, schemas produced at "
        "runtime, caching policy. Here you pay for a developer who makes the calls "
        "and walks the edge cases; whole large screens land here too.",
    ],
    "avg_task": "Average task: about {o} / {p} hours. Browser verification and the "
                "fixes it produces are inside the task's hours.",
    "coefficients": "Overheads are their own rows so each can be discussed on its "
                    "own: responsive layout {r}%, localisation {i}%, automated tests "
                    "{t}%. Tests are computed last, on the sum.",
    "breakdown": "Breakdown",
    "breakdown_note": "",  # a line under the heading, for a module that needs one
    "scope": "Scope",
    "scope_default": "Everything the sources describe, within the parts named above.",
    "provenance": "Where each line came from",
    "provenance_intro": "An audit of every task by source. It shows where the estimate "
                        "stands on firm ground and where it was built up by us.",
    "group": "Group",
    "tasks": "Tasks",
    "share": "Share of development",
    "dev_total": "Development, total",
    "overhead_row": "Overheads: responsive layout, localisation, tests",
    "provenance_groups": {
        "both": ("Confirmed by both the spec and the design",
                 "The firmest part: named in the spec, drawn in the design."),
        "spec": ("In the spec, but one or two sentences and no mockup",
                 "The decomposition is ours. Both size and composition can move."),
        "design": ("Taken from the design; the spec does not mention it",
                   "The client never asked for it in words. Each line is a question."),
        "ours": ("In neither — foundation and engineering",
                 "Cannot be skipped, but has to be justified separately."),
    },
    "not_broken_out": "Spec items without a row of their own",
    "not_broken_out_note": "Folded into other tasks — so a reader looking for them "
                           "finds out where they went.",
    "risks": "Risks",
    "exclusions": "Exclusions",
    "questions": "Open questions",
    "none": "—",
}
L.update(E.get("LABELS", {}))

HPM = E.get("HOURS_PER_MONTH", 170)


def n(x):
    return str(int(x))


def cell(x):
    return x if x else L["none"]


def plural_tasks(k, e):
    return L["tasks_in_epics"].format(n=k, e=e)


out = []
w = out.append

# ------------------------------------------------------------------- title
w(f"# {E.get('TITLE', L['title'])}")
w("")
for line in E.get("INTRO", []):
    w(line)
if E.get("INTRO"):
    w("")

# ----------------------------------------------------------------- summary
co, cp = E.core()
oo, op = E.overhead()
to, tp = E.total()
w(f"## {L['summary']}")
w("")
w(f"| {L['row']} | {L['optimistic']} | {L['pessimistic']} |")
w("| --- | ---: | ---: |")
if len(E.parts) > 1:
    for part in E.parts:
        po, pp = E.core(part)
        w(f"| {L['development']} — {part} | {n(po)} | {n(pp)} |")
    w(f"| {L['development']} — {plural_tasks(len(E.rows), len(E.by_epic()))} | {n(co)} | {n(cp)} |")
else:
    w(f"| {L['development']} — {plural_tasks(len(E.rows), len(E.by_epic()))} | {n(co)} | {n(cp)} |")
for d in E.derived:
    pct = int(E.rates[d["key"]] * 100)
    w(f"| {d['task']}, {pct}% | {n(d['optimistic'])} | {n(d['pessimistic'])} |")
label = L["part_total"].format(part=E.parts[0]) if len(E.parts) == 1 else L["grand_total"]
w(f"| **{label}** | **{n(to)}** | **{n(tp)}** |")
w("")
wo, wp = E.weeks()
weeks = f"{wo}–{wp}" if wo != wp else str(wo)
w(L["timeline"].format(hpm=HPM, weeks=weeks))
for line in E.get("TIMELINE_NOTE", []):
    w(line)
w("")
w(L["roles_note"])
w("")

# ------------------------------------------------------------------ method
w(f"## {L['method']}")
w("")
for line in E.get("RATES_NOTE", L["rates_default"]):
    w(line)
w("")
w(L["avg_task"].format(o=round(co / max(len(E.rows), 1)), p=round(cp / max(len(E.rows), 1))))
w("")
w(L["coefficients"].format(r=int(E.rates["responsive"] * 100), i=int(E.rates["i18n"] * 100),
                           t=int(E.rates["tests"] * 100)))
w("")

# --------------------------------------------------------------- breakdown
w(f"## {L['breakdown']}")
w("")
if L["breakdown_note"]:
    w(L["breakdown_note"])
    w("")
w("| " + " | ".join(h for _, h in E.columns) + " |")
w("| " + " | ".join("---:" if k in NUMERIC else "---" for k, _ in E.columns) + " |")
for r in E.all_rows():
    w("| " + " | ".join(n(r[k]) if k in NUMERIC else cell(r.get(k, "")) for k, _ in E.columns) + " |")
tot_cells = []
for k, _ in E.columns:
    if k == "optimistic":
        tot_cells.append(f"**{n(to)}**")
    elif k == "pessimistic":
        tot_cells.append(f"**{n(tp)}**")
    elif k == E.columns[0][0]:
        tot_cells.append(f"**{L['grand_total']}**")
    else:
        tot_cells.append("")
w("| " + " | ".join(tot_cells) + " |")
w("")

# ------------------------------------------------------------------- scope
w(f"## {L['scope']}")
w("")
for line in E.get("SCOPE", [L["scope_default"]]):
    w(line)
w("")

# ---------------------------------------------------- project's own sections
for title, lines in E.get("SECTIONS", []):
    w(f"## {title}")
    w("")
    for line in lines:
        w(line)
    w("")

# -------------------------------------------------------------- provenance
origin = E.get("ORIGIN")
if origin:
    note = E.get("ORIGIN_NOTE", {})
    groups = {k: [] for k in ("both", "spec", "design", "ours")}
    for r in E.rows:
        groups.setdefault(origin.get(r["task"], "ours"), []).append(r)
    w(f"## {L['provenance']}")
    w("")
    w(L["provenance_intro"])
    w("")
    w(f"| {L['group']} | {L['tasks']} | {L['optimistic']} | {L['pessimistic']} | {L['share']} |")
    w("| --- | ---: | ---: | ---: | ---: |")
    for key in ("both", "spec", "design", "ours"):
        rows = groups[key]
        a, b = sum(r["optimistic"] for r in rows), sum(r["pessimistic"] for r in rows)
        title, _ = L["provenance_groups"][key]
        w(f"| {title} | {len(rows)} | {n(a)} | {n(b)} | {round(a / co * 100) if co else 0}% |")
    w(f"| **{L['dev_total']}** | **{len(E.rows)}** | **{n(co)}** | **{n(cp)}** | **100%** |")
    w(f"| {L['overhead_row']} | — | {n(oo)} | {n(op)} | — |")
    w(f"| **{L['grand_total']}** | — | **{n(to)}** | **{n(tp)}** | — |")
    w("")
    for key in ("both", "spec", "design", "ours"):
        rows = groups[key]
        if not rows:
            continue
        title, explain = L["provenance_groups"][key]
        a, b = sum(r["optimistic"] for r in rows), sum(r["pessimistic"] for r in rows)
        w(f"### {title} — {n(a)} / {n(b)}")
        w("")
        w(explain)
        w("")
        for r in rows:
            extra = f" — {note[r['task']]}" if r["task"] in note else ""
            w(f"- **{r['task']}** ({n(r['optimistic'])} / {n(r['pessimistic'])}){extra}")
        w("")
    folded = E.get("SPEC_NOT_BROKEN_OUT", [])
    if folded:
        w(f"### {L['not_broken_out']}")
        w("")
        w(L["not_broken_out_note"])
        w("")
        for item, where in folded:
            w(f"- {item} — {where}")
        w("")

# ---------------------------------------------- risks, exclusions, questions
for title_key, attr, numbered in (("risks", "RISKS", False), ("exclusions", "EXCLUDES", False),
                                  ("questions", "QUESTIONS", True)):
    items = E.get(attr, [])
    if not items:
        continue
    w(f"## {L[title_key]}")
    w("")
    for i, item in enumerate(items, 1):
        w(f"{i}. {item}" if numbered else f"- {item}")
    w("")

open(OUT, "w").write("\n".join(out))
print(f"written: {OUT}")
print(f"parts={E.parts} core={co}/{cp} overhead={oo}/{op} total={to}/{tp}")
for line in E.rounded:
    print(line)
