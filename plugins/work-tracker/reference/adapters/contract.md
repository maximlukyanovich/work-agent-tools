# Adapter contract

What the method asks of a tracker, and the form of an adapter that answers it.
Read when an adapter is written, and by a command whose step needs an
operation its adapter does not list. A command in a normal run reads only its
adapter — which one, and what happens without an operation: the `issues`
skill, "The adapter".

## Operations

| Operation | What the method gets | Called by |
| --- | --- | --- |
| `read` | One issue: description, acceptance criteria, comments, attachments, parent, links | `next`, `questions`, `status`, `comment` |
| `worked` | Issues by a filter, written to a file in the form of `reference/actuals.md`: status category, estimate, time logged, resolution date; the description and the worklogs on request | `check-actuals` |
| `query` | Issues by a filter in one query — the open issues of a scope with status, assignee, estimate, remaining time, links and parent, and the issues they link to; issues by a name | `next`, `plan` |
| `vocabulary` | Issue types, labels, link types and statuses, as the instance has them | `create`, the first run |
| `create tree` | A tree from nodes, parents first, references between them resolved and linked, and a dry run that writes nothing | `create` |
| `describe` | Replace a description; resolve its references | `comment`, `issues` "Description" |
| `comment` | New, edit, reply in a thread, read a thread, a link to a comment | `comment`, the waiting list |
| `mention` | Notify a person by what the team file holds for them | `comment`, questions |
| `transition` | Move to a status by its name | `comment` |
| `estimate` | Set the estimate, and the remaining time with it | `create`, `issues` "Estimates" |
| `worklog` | Log time with a sentence | `comment` |
| `assign`, `release` | The assignee; the version and the priority | `create` |
| `flag` | Mark a blocker from outside the team | `issues` "Links" |
| `react` | Acknowledge an answer under it | the waiting list |

## Capabilities

An adapter states each one; the method reads them before it offers a step.

| Capability | Values |
| --- | --- |
| Sub-tasks | yes, no |
| Estimate unit | time, points, none |
| Time tracking | yes, no |
| Text format | what the tracker stores — ADF, Markdown, … |
| Mention | by id, by profile link, none |
| Reply in a thread | yes, no |
| Reaction | yes, read only, no |
| Flag | yes, no |

## Writing an adapter

A file `reference/adapters/<system>.md` in the form of `jira.md`: a first
line naming the deployments it covers, the operations with the call for each,
the capabilities, "Writing the text" — what a format converter loses and how
the editor renders headings, task lists and code — then what else the tracker
does that a writer would not expect — each fact checked against the tracker's
documentation or a probe. A script in `scripts/` when the tracker needs one.
It lands in this plugin as a pull request, never in a project: an adapter is
true for every project on that tracker.
