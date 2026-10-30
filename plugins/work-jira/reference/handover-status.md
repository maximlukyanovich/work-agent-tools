# Status at hand-over

Read on demand: from `/work-jira:comment` before it recommends a status, from
the `issues` skill's "Carving a piece out", and from planning when part of a
task's scope turns out not ready. The status is the developer's answer, never
the agent's move.

## The default

The issue goes to the testing status. An issue that delivers only components
with no screen or route QA can open — a design system, shared blocks — goes to
Done as the recommended option, and its comment names the issues whose screens
show them to QA. An open question about a detail of a drawn screen — an error
text, a consent line — does not hold the hand-over: it goes into `Known
limitations`.

## Before recommending

Hold the issue's summary, `Scope` and acceptance criteria against its `Known
limitations` and its open lines on the waiting list. A part the summary or the
scope promises that was not built, or not built to the design, is a row of the
table below — never a `Known limitations` line under the testing status.

## Part of the scope not ready

The option is always asked, the recommended one first. The hours are a
separate question, with the numbers before any change — original estimate,
time logged, new estimate, new remaining, the budget moved.

| Cause | Options, recommended first | Hours |
| --- | --- | --- |
| A state of a drawn screen is not drawn; a placeholder meets the criteria; the item was in the issue and in the estimate's row, if only as an unknown | The issue waits for the answer in the in-progress status, the blocking question goes to the team's chat. Not a change request | No re-estimate. A change request only if the answer departs from what was built, estimated by what is then drawn |
| A whole screen or a function the summary or the scope names is not drawn — the code holds a stub | Carve it into its own issue with its questions, `is blocked by` the cause and flagged; the rest goes to testing. The question is a blocker, not a `Known limitations` line | The estimate contained it → cut from the original, the total stays (recommended); it did not → new hours, with why the scope grew |
| The backend has no data or endpoint for it | Carve it out, blocked by the backend issue, the rest to testing (recommended) / keep it, the issue waits for the backend / ship the layout without data, dashes in its place | As above |

## The move

The transition is one the tracker offers for the issue —
`jira.transition(key, status)` matches the name against them — never a guessed
id or a status name copied into a file.
