# -*- coding: utf-8 -*-
"""The hours report: hours logged in the tracker against the estimate, as one local HTML page.

    actuals.py <report.json> [<out.html>]

The page goes beside the report as <report stem>_<YYYYMMDD>.html — the build's date, so an
earlier page stays as it was. The report file holds the selection and every decision taken for it; the issues come from
the file it names, written by the tracker adapter. Both formats are in
reference/actuals.md. The page is actuals.html with the data and the strings of the
report's language put in; it is rebuilt from the same two files any number of times.

Statistics cover closed issues with an estimate; the table shows the whole selection.
Prints one line per thing a person should look at — an issue without an estimate, an
estimate that disagrees with the tracker's field, a closed issue over the optimistic with
no reason recorded — then the page's file URL and the figures of its tiles.
"""

import datetime
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPS = 1e-9


def key_order(key):
    prefix, _, number = key.rpartition("-")
    return (prefix, int(number)) if number.isdigit() else (key, 0)


def hours(text):
    return float(text.replace(",", "."))


def from_text(text, patterns):
    """The last (opt, pess) pair any pattern finds: after a split the paragraph ends with
    the new pair. A pattern without a `pess` group gives a single estimate."""
    best = None
    for pattern in patterns:
        for m in re.finditer(pattern, text or ""):
            opt = hours(m.group("opt"))
            pess = m.groupdict().get("pess")
            pair = (opt, hours(pess) if pess else opt)
            if best is None or m.start() > best[0]:
                best = (m.start(), pair)
    return best[1] if best else (None, None)


CHECK = re.compile(r"^\[([ x])\] ", re.M)
# Resolutions that close an issue without doing it, as Jira and Linear name them.
DROPPED = {"won't do", "won't fix", "cancelled", "canceled", "duplicate", "declined", "obsolete", "invalid"}
# A summary opening with a bracketed marker — "[Cancelled] …", "[Отменено] …" — is how a team
# drops an issue without a resolution; asked about, never left out unasked.
MARKER = re.compile(r"^\s*\[[^\]]+\]")


def checklist(text):
    """Percent of ticked task items in a description. None without a tick: many teams tick
    nothing until the review, so an untouched list says nothing about progress."""
    marks = CHECK.findall(text or "")
    return round(100 * marks.count("x") / len(marks)) if "x" in marks else None


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def manual(key, value):
    """An estimate the user gave: [opt, pess], [opt] or a number — a single estimate."""
    if value is None:
        return None, None
    if number(value):
        value = [value]
    if not (isinstance(value, list) and len(value) in (1, 2) and all(map(number, value))):
        sys.exit(f"estimates: {key} {value!r} — a number, [opt] or [opt, pess]")
    return float(value[0]), float(value[-1])


def setting(report, key, default):
    """A report's field; a null counts as left out."""
    value = report.get(key)
    return default if value is None else value


def build(report, issues, warn=print):
    source = setting(report, "source", "tracker")
    given = setting(report, "estimates", {})
    groups = setting(report, "groups", {})
    dev_done = set(setting(report, "dev_done", []))
    readiness = setting(report, "readiness", {})
    exclude = set(setting(report, "exclude", []))
    keep = set(setting(report, "keep", []))
    rows = []
    for i in sorted(issues, key=lambda i: key_order(i["key"])):
        key, field = i["key"], i.get("estimate") or None
        if key in exclude:
            continue
        if key not in keep and (i.get("resolution") or "").lower() in DROPPED:
            warn(f"looks dropped: {key} resolved as {i['resolution']!r} — `exclude` or `keep`")
        elif key not in keep and MARKER.match(i["summary"]):
            warn(f"looks dropped: {key} {i['summary']!r} — `exclude` or `keep`")
        opt = pess = None
        group = (i.get("parent") or {}).get("summary")
        if source == "description":
            opt, pess = from_text(i.get("text"), setting(report, "patterns", []))
            if opt is None and field is not None:
                opt = pess = field
                warn(f"no estimate in the description: {key} — the field's {field:g} is taken")
            elif opt is not None and field is not None and abs(opt - field) > 0.01:
                warn(f"estimate differs: {key} description {opt:g} / field {field:g} — the description is taken")
        elif source == "manual":
            opt, pess = manual(key, given.get(key))
        else:
            opt = pess = field
        if not opt:
            opt = pess = None
            warn(f"no estimate: {key} {i['summary']!r}")
        elif pess < opt:
            warn(f"pess below opt: {key} {opt:g} / {pess:g} — taken as a single {opt:g}")
            pess = opt
        done = i["category"] == "done"
        if done and opt and not i.get("spent"):
            warn(f"no hours: {key} closed with nothing logged — is the time on its sub-tasks?")
        ready = 100 if done or i["status"] in dev_done else 0
        if not done and i["status"] not in dev_done and i["category"] == "progress":
            ready = readiness.get(key, checklist(i.get("text")))
            if ready is None and key not in readiness:
                warn(f"no readiness: {key} in progress, no ticked list and no value — ask the user")
        rows.append({
            "key": key, "url": i.get("url"), "name": i["summary"], "status": i["status"],
            "group": groups.get(key, group), "assignee": i.get("assignee"),
            "opt": opt, "pess": pess, "fact": i.get("spent") or 0,
            "done": done, "started": i["category"] == "progress",
            "readiness": ready, "closed": i.get("resolved"),
        })
    # A group sits where its first key does and keeps its rows together, so the table
    # shows each group once.
    first = {}
    for r in rows:
        first.setdefault(r["group"], len(first))
    rows.sort(key=lambda r: (first[r["group"]], key_order(r["key"])))
    reasons = setting(report, "reasons", {})
    wrong = [k for k, v in reasons.items() if v is not None and not isinstance(v, dict)]
    if wrong:
        sys.exit(f"reasons: {', '.join(wrong)} — each is {{\"text\": …, \"url\": …}}")
    for r in rows:
        if r["done"] and r["opt"] is not None and r["fact"] > r["opt"] + EPS:
            if r["key"] not in reasons:
                warn(f"no reason: {r['key']} {r['fact']:g} h against {r['opt']:g} — read its comments and worklogs")
            reason = reasons.get(r["key"]) or {}
            r["reason"], r["reasonUrl"] = reason.get("text") or "", reason.get("url")
    return rows


def stats(rows):
    done = [r for r in rows if r["done"] and r["opt"]]
    so, sp, sf = (sum(r[k] for r in done) for k in ("opt", "pess", "fact"))
    over = [r["fact"] / r["opt"] - 1 for r in done]
    over_pess = [r["fact"] / r["pess"] - 1 for r in done]
    closed = sorted(r["closed"] for r in done if r["closed"])
    return {
        "count": len(done), "opt": so, "pess": sp, "fact": sf,
        "mean_over": sum(over) / len(over) if over else 0,
        "sum_over": sf / so - 1 if so else 0,
        "mean_over_pess": sum(over_pess) / len(over_pess) if over_pess else 0,
        "sum_over_pess": sf / sp - 1 if sp else 0,
        "corridor": (sf - so) / (sp - so) if sp > so else None,
        "within_opt": sum(1 for r in done if r["fact"] <= r["opt"] + EPS),
        "within_pess": sum(1 for r in done if r["fact"] <= r["pess"] + EPS),
        "over_pess": sum(1 for r in done if r["fact"] > r["pess"] + EPS),
        "closed_from": closed[0] if closed else None, "closed_to": closed[-1] if closed else None,
        "unestimated": sum(1 for r in rows if r["opt"] is None),
    }


def cumulative(rows, warn=print):
    undated = [r["key"] for r in rows if r["done"] and r["opt"] and not r["closed"]]
    if undated:
        warn(f"no closing date: {', '.join(undated)} — left out of the overrun over time")
    out, over_opt, over_pess = [], 0, 0
    for r in sorted((r for r in rows if r["done"] and r["opt"] and r["closed"]),
                    key=lambda r: (r["closed"], key_order(r["key"]))):
        over_opt += r["fact"] - r["opt"]
        over_pess += r["fact"] - r["pess"]
        out.append({"date": r["closed"], "key": r["key"], "opt": round(over_opt, 2), "pess": round(over_pess, 2)})
    return out


def breakdown(rows, by):
    out = {}
    for r in rows:
        if r["done"] and r["opt"]:
            name = r["assignee"] if by == "people" else r["group"]
            b = out.setdefault(name, {"name": name, "count": 0, "opt": 0, "pess": 0, "fact": 0})
            b["count"] += 1
            for k in ("opt", "pess", "fact"):
                b[k] += r[k]
    return sorted(out.values(), key=lambda b: -b["fact"])


def period_start(date, period):
    d = datetime.date.fromisoformat(date)
    return (d - datetime.timedelta(days=d.weekday()) if period == "week" else d.replace(day=1)).isoformat()


def periods(issues, period, warn=print):
    logs = [w for i in issues for w in i.get("worklogs") or []]
    if not any("worklogs" in i for i in issues):
        warn("periods: the issues file has no worklogs — dump it with them")
        return period, []
    if not period:
        dates = sorted(w["date"] for w in logs)
        span = (datetime.date.fromisoformat(dates[-1]) - datetime.date.fromisoformat(dates[0])).days if dates else 0
        period = "month" if span > 84 else "week"
    out = {}
    for w in logs:
        start = period_start(w["date"], period)
        out[start] = round(out.get(start, 0) + w["hours"], 2)
    return period, [{"start": k, "hours": v} for k, v in sorted(out.items())]


def strings(report, base, warn=print):
    """The page's texts: the plugin's file for the language, or the project's translation.
    A key the translation lacks falls back to English and is named, so the page never
    shows a bare key."""
    english = json.loads((HERE / "actuals" / "en.json").read_text(encoding="utf-8"))
    lang = setting(report, "language", "en")
    path = base / report["strings"] if report.get("strings") else HERE / "actuals" / f"{lang}.json"
    if not path.exists():
        sys.exit(f"no strings for {lang!r}: translate {HERE / 'actuals' / 'en.json'} into the project "
                 f"and name the copy in the report's \"strings\"")
    text = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in english if k not in text]
    if missing:
        warn(f"strings: {path.name} lacks {', '.join(missing)} — English is used for them")
    return {**english, **text}


def main(report_path, out_path=None):
    report_path = Path(report_path)
    base = report_path.parent
    report = json.loads(report_path.read_text(encoding="utf-8"))
    issues = json.loads((base / report["issues"]).read_text(encoding="utf-8"))
    rows = build(report, issues)
    st = stats(rows)
    source = setting(report, "source", "tracker")
    single = source == "tracker" or all(r["opt"] == r["pess"] for r in rows if r["opt"] is not None)
    sections = setting(report, "sections", [])
    custom = setting(report, "custom", [])
    for c in custom:
        width = len(c.get("columns") or [])
        if any(len(row) != width for row in c.get("rows") or []):
            sys.exit(f"custom: {c.get('title')!r} — every row has as many cells as `columns`, {width}")
    payload = {
        "rows": rows, "stats": st, "single": single, "sections": sections, "source": source,
        "date": datetime.date.today().isoformat(),
        "sourceNote": setting(report, "source_note", ""), "devDone": setting(report, "dev_done", []),
        "notes": setting(report, "notes", []), "custom": custom,
        "openOver": [r for r in rows if not r["done"] and r["opt"] is not None and r["fact"] > r["opt"] + EPS],
    }
    if "cumulative" in sections:
        payload["cumulative"] = cumulative(rows)
    if "breakdown" in sections:
        payload["breakdownBy"] = setting(report, "breakdown", "epics")
        payload["breakdown"] = breakdown(rows, payload["breakdownBy"])
    if "periods" in sections:
        shown = {r["key"] for r in rows}
        payload["period"], payload["periods"] = periods([i for i in issues if i["key"] in shown], report.get("period"))
    text = strings(report, base)
    page = (HERE / "actuals.html").read_text(encoding="utf-8")
    # One pass, so a placeholder inside the tracker's text stays text.
    parts = {
        "/*DATA*/null": json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"),
        "/*STRINGS*/null": json.dumps(text, ensure_ascii=False).replace("</", "<\\/"),
        "{{LANG}}": html.escape(text["locale"]),
        "{{TITLE}}": html.escape(setting(report, "title", text["title"])),
    }
    page = re.sub("|".join(map(re.escape, parts)), lambda m: parts[m.group()], page)
    stamp = datetime.date.today().strftime("%Y%m%d")
    out = Path(out_path) if out_path else report_path.with_name(f"{report_path.stem}_{stamp}.html")
    out.write_text(page, encoding="utf-8")
    print(out.resolve().as_uri())
    span = f" between {st['closed_from']} and {st['closed_to']}" if st["closed_from"] else ""
    print(f"closed {st['count']}{span}; within the optimistic {st['within_opt']}"
          + ("" if single else f", within the pessimistic {st['within_pess']}"))
    print(f"fact {st['fact']:g} h against " + (f"{st['opt']:g}" if single else f"opt. {st['opt']:g} / pess. {st['pess']:g}"))
    print(f"to the optimistic: mean {st['mean_over']:+.1%}, by sum {st['sum_over']:+.1%}")
    if not single:
        print(f"to the pessimistic: mean {st['mean_over_pess']:+.1%}, by sum {st['sum_over_pess']:+.1%}"
              + (f"; place in the range {st['corridor']:.0%}" if st["corridor"] is not None else ""))


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__.split("\n\n")[1])
    main(*sys.argv[1:])
