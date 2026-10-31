# -*- coding: utf-8 -*-
"""Load an estimate data module into one normalised shape shared by the renderers.

A task row is a tuple of 7 or 8 elements:

    (epic, task, description, optimistic, pessimistic, negative_risk, positive_risk)
    (part, epic, task, description, optimistic, pessimistic, negative_risk, positive_risk)

With 7 elements the part comes from `PART` in the module (default "Frontend"), or from
`PARTS = {task_name: part}` when tasks belong to different parts. Hours are whole: a
fraction is rounded up, and each row rounded is named in `rounded` for the scripts to print.

Coefficient rows (`DERIVED`) are tuples of 6:

    (epic, task, description, key, negative_risk, positive_risk)

where key is one of "responsive", "i18n", "tests". Their hours are computed from
`RESPONSIVE_RATE`, `I18N_RATE`, `TESTS_RATE`: whole hours, rounded up, tests last and
computed on the sum. They belong to one part — `DERIVED_PART`, default the first — and
with several parts in the module they are computed from that part's development sum
only: a backend has no responsive layout to pay for.
"""

import importlib
from math import ceil

DEFAULT_COLUMNS = [
    ("part", "PART OF"),
    ("epic", "EPIC / FEATURE"),
    ("task", "TASK / USER STORY"),
    ("description", "DESCRIPTION"),
    ("optimistic", "OPT"),
    ("pessimistic", "PESS"),
    ("negative", "RISKS: NEGATIVE"),
    ("positive", "RISKS: POSITIVE"),
]

NUMERIC = {"optimistic", "pessimistic"}


class Estimate:
    def __init__(self, module_name):
        self.m = importlib.import_module(module_name)
        self.rounded = []
        self.rows = [self._row(t) for t in self.m.TASKS]
        self.columns = list(getattr(self.m, "COLUMNS", DEFAULT_COLUMNS))
        self.parts = list(dict.fromkeys(r["part"] for r in self.rows))
        self.rates = {
            "responsive": getattr(self.m, "RESPONSIVE_RATE", 0),
            "i18n": getattr(self.m, "I18N_RATE", 0),
            "tests": getattr(self.m, "TESTS_RATE", 0),
        }
        self.derived = self._derived()

    # ----------------------------------------------------------- normalise
    def _row(self, t):
        if len(t) == 8:
            part, epic, task, desc, o, p, neg, pos = t
        elif len(t) == 7:
            epic, task, desc, o, p, neg, pos = t
            parts = getattr(self.m, "PARTS", {})
            part = parts.get(task, getattr(self.m, "PART", "Frontend"))
        else:
            raise ValueError(f"task row must have 7 or 8 elements: {t[:2]}")
        hours = (ceil(o), ceil(p))
        if hours != (o, p):
            self.rounded.append(f"rounded up: {task} {o:g}/{p:g} -> {hours[0]}/{hours[1]}")
        return {"part": part, "epic": epic, "task": task, "description": desc,
                "optimistic": hours[0], "pessimistic": hours[1], "negative": neg or "",
                "positive": pos or ""}

    def _derived(self):
        # Overheads apply to one part (usually the frontend): the base is that part's
        # development sum, not the whole estimate — a backend has no responsive layout.
        part = getattr(self.m, "DERIVED_PART", self.parts[0] if self.parts else "Frontend")
        co, cp = self.core(part) if len(self.parts) > 1 else self.core()
        resp = (ceil(co * self.rates["responsive"]), ceil(cp * self.rates["responsive"]))
        i18n = (ceil(co * self.rates["i18n"]), ceil(cp * self.rates["i18n"]))
        tests = (ceil((co + resp[0] + i18n[0]) * self.rates["tests"]),
                 ceil((cp + resp[1] + i18n[1]) * self.rates["tests"]))
        hours = {"responsive": resp, "i18n": i18n, "tests": tests}
        out = []
        for epic, task, desc, key, neg, pos in getattr(self.m, "DERIVED", []):
            o, p = hours[key]
            out.append({"part": part, "epic": epic, "task": task, "description": desc,
                        "optimistic": o, "pessimistic": p, "negative": neg or "",
                        "positive": pos or "", "key": key})
        return out

    # -------------------------------------------------------------- totals
    def core(self, part=None):
        rows = [r for r in self.rows if part is None or r["part"] == part]
        return sum(r["optimistic"] for r in rows), sum(r["pessimistic"] for r in rows)

    def overhead(self):
        return (sum(r["optimistic"] for r in self.derived),
                sum(r["pessimistic"] for r in self.derived))

    def total(self):
        co, cp = self.core()
        oo, op = self.overhead()
        return co + oo, cp + op

    def weeks(self):
        """The timeline in whole weeks, (optimistic, pessimistic): the total over
        HOURS_PER_WEEK (default 40), rounded — one rule for the report and the workbook."""
        hpw = self.get("HOURS_PER_WEEK", 40)
        to, tp = self.total()
        return round(to / hpw), round(tp / hpw)

    def all_rows(self):
        return self.rows + self.derived

    def by_epic(self):
        out = {}
        for r in self.rows:
            out.setdefault(r["epic"], []).append(r)
        return out

    def by_part(self):
        out = {}
        for r in self.rows:
            out.setdefault(r["part"], []).append(r)
        return out

    # ------------------------------------------------------------ optional
    def get(self, name, default=None):
        return getattr(self.m, name, default)
