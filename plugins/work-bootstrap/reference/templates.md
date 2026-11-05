# Templates

Skeletons only. Every example inside a skill or command is written for **this**
project's domain — carrying someone else's examples over is an anti-pattern.

This file is the index: the skeletons live in `templates/`, one file per
reader, and each is read alone — the one the file being written or checked
needs. A text that quotes "`templates.md`, «X»" means the file that holds X.

| File | Sections | Read for |
| --- | --- | --- |
| [`files.md`](templates/files.md) | `AGENTS.md`, `README.md` — Deployment, `CLAUDE.md`, `SKILL.md`, `.mcp.json.example`, Hook contract, Git hooks, `docs/local/README.md`, `docs/local/efficiency-remarks.md` | the harness's files other than commands |
| [`command.md`](templates/command.md) | A command; A command acts on a target, wherever it is checked out; A command ends with its next step; The full gate runs once per branch — with "A hub file takes the tests of its areas", "A gate of several parts picks them by content" and "`model:` in a command's frontmatter" | any command, the gate |
| [`onboarding.md`](templates/onboarding.md) | The onboarding command | the onboarding command, the plugin set |
| [`task.md`](templates/task.md) | A command that starts a task must offer the opening steps — with "The change sets the process"; A command that starts a task can open it in a worktree | the task command, a change's level |
| [`design-source.md`](templates/design-source.md) | A project with a design source holds to it — with "A measurement, not an eyeball" | design rules |
| [`merge.md`](templates/merge.md) | A merge request is shown before it is opened; Waiting for CI; A command that merges must offer the closing steps | the merge command |
| [`review.md`](templates/review.md) | A command that reviews keeps a pass ledger — the ledger, the procedure with "Stop and ask", the rubric additions, "Review groups run on the session's model", "Run it in a fresh session" | the review command, the review agent |
| [`review-fixes.md`](templates/review-fixes.md) | The same section, its second half — "The commit command hands the phase over" (once "…hands the review over"), "A commit the hook refuses leaves its paths staged", "A fix to a commit not yet pushed goes into that commit", "Fixing the findings has its own discipline", "A merging command reads the ledger", "Cost" | the commit command, the fix round, the merge's reading of the ledger |
| [`testing-skill.md`](templates/testing-skill.md) | The testing skill proves a change by its risk | the testing skill, the `test` lens |

A quoted name the table does not list is a paragraph inside a file:
`grep -ln '<name>' "${CLAUDE_PLUGIN_ROOT}/reference/templates/"*.md`.
