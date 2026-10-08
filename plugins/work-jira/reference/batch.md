# Batch format for `scripts/jira.py`

`jira.batch(project, nodes, ...)` creates a tree of issues from a list of nodes.
The command writes the list in a short Python script inside the project's local
notes and runs it; the script is the record of what was created and how.

## A node

| Field | Meaning |
| --- | --- |
| `type` | `Epic`, `Story`, `Task`, `Sub-task`, `Bug` — a name from the project's `createmeta` |
| `summary` | Unique in the project. It is the idempotency key: an existing summary is never created twice |
| `parent` | The summary of a node earlier in the list, or the key of an existing issue. Absent on an epic |
| `labels` | From the instance, never invented |
| `estimate` | `15h`, `6h 30m` — what `Original Estimate` holds. Absent when the hours are unknown, and **absent on an epic**: Jira sums the children |
| `fix_version` | The version name; defaults to the batch's `fix_version`. Set right after creation |
| `priority` | The priority name, by the profile's rule. Set right after creation |
| `blocked_by` | Keys, or summaries from this batch, of the issues this one waits on. Each becomes a `Blocks` link with the provider first |
| `split_from` | Key of the issue this one was carved out of. Becomes an `Issue split` link, the original first: `PROJ-12 split to PROJ-40` |
| `blocks` | A **function** returning the description blocks, in the section order the `issues` skill fixes |

`blocks` is a function and not a value because the description is rendered twice:
once to create the issue and once more after the whole batch exists, when every
reference can be resolved.

```python
import jira
from jira import h, p, ul, checklist

nodes = [
    dict(type="Epic", summary="Checkout", labels=["Frontend"],
         blocks=lambda: [h("Context"), p("…"), h("Scope"), ul(["…"]),
                         h("Sources of truth"), ul(["…"])]),
    dict(type="Task", summary="[FE] Cart & payment", parent="Checkout",
         labels=["Frontend"], estimate=jira.jira_hours(6 + jira.half_up(6 * 0.05)),
         blocks=lambda: [
             h("Context"), p("…"),
             h("Out of scope"),
             ul(["Rendering the sent message — [[@[FE] Chat stream & message rendering]]",
                 "Stream transport — [[PROJ-10]]"]),
             h("Acceptance criteria"), checklist(["…"]),
             h("Sources of truth"), ul(["Related: [[PROJ-7]], [[PROJ-10]]"]),
             h("Estimate"), p("…"),
         ]),
]
jira.batch("PROJ", nodes, dry_run="--dry-run" in sys.argv, assignee=jira.myself())
```

## Inline notation

Understood inside every string handed to `p`, `ul` and `checklist`:

| Written | Rendered |
| --- | --- |
| `` `code` `` | inline code |
| `[text](url)` | a link |
| `[[PROJ-7]]` | an inline card — Jira shows key, summary and status and keeps them current |
| `[[@<summary>]]` | the card of an issue in this batch, by its summary; resolved in pass two |

A `[[@summary]]` whose issue does not exist yet renders as the summary in code
and is replaced by the card as soon as the key is known. A summary that never
resolves — a typo, or an issue outside the batch — stays as code, which is
visible in the result and is the signal to fix it.

## The three passes

1. **Create**, parents before children. `Original Estimate`, the fix version and
   the priority are set with follow-up requests; tasks, sub-tasks and bugs are
   assigned when `assignee` is given. Every line prints `[version · priority]`,
   and `NO VERSION` / `NO PRIORITY` where one is missing.
   Epics and stories are never assigned by the batch — the standard gives them to
   the manager or the analyst.
2. **Resolve.** Every new description is rendered again and updated where it
   changed. An existing issue is patched in place: the code-rendered summaries
   that now have a key are swapped for cards inside the document Jira holds, so
   task items keep their ids and their ticks — this is how a reference to a
   sibling created in a later run gets its card. `rewrite=True` re-renders
   existing issues instead; that gives every task item a fresh id and unticks
   acceptance criteria, so it is for repairing a run that failed between the
   passes, not for routine re-runs.
3. **Link.** First the dependencies: every `blocked_by` entry becomes a `Blocks`
   link, provider first, printed as a sentence — `PROJ-57 Search API blocks
   PROJ-14 Results grid`. Then every issue is linked, type `link_type` (`Relates`
   by default), to every issue its description references as a card. A pair
   already linked in any way is skipped, and so is the issue's own parent or
   child — the hierarchy already shows that relation. The order matters: a
   dependency that is also referenced in the text would otherwise stay a plain
   `relates to`. A dry run prints the dependency sentences too.

## Options

| Option | Default | Effect |
| --- | --- | --- |
| `dry_run` | `False` | Prints the plan and the dependency sentences, writes nothing, stops after pass one |
| `fix_version` | `None` | Default version for every node that does not name its own |
| `assignee` | `None` | Account id for tasks, sub-tasks and bugs; `jira.myself()` is the developer |
| `link_type` | `"Relates"` | Name from `GET /rest/api/3/issueLinkType`; `None` skips the links derived from references, for a project that links dependencies only |
| `rewrite` | `False` | Pass two re-renders existing issues instead of patching them in place |

Returns `summary → key` for the batch. Raises before writing anything when an
epic carries an estimate or an `Estimate` section.

## Other helpers

`jira.index(project)` — every summary → key of the project, also feeding the
reference registry. `jira.describe(key, doc)` — replace one description;
`jira.resolve(key)` — patch its unresolved references in place.
`jira.block(provider, consumer, dry_run=False)` — one `Blocks` link between
existing issues, printed as a sentence; the way to add or repair a dependency
outside a batch. `jira.set_release(key, fix_version, priority)`.
`jira.link(a, b, type)` — reads left to right, `a blocks b`, `a split to b`; the API's own body names the sides the other way round, and the helper hides that, `jira.linked(key)`, `jira.assign(key, account_id)`,
`jira.myself()`, `jira.set_estimate(key, "6h 30m")`, `jira.half_up(hours)`,
`jira.jira_hours(hours)`, `jira.refs(doc)`, `jira.has_section(doc, title)`.
