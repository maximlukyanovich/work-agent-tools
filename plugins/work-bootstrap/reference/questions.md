# Phase 1: the questions

Rules: ask in batches, never one per turn; every question carries an explicit
default; never ask what the inventory already answered. **If an answer changes no
file, the question is redundant.**

**Q1. The repository's role and current phase.** What the product is, in a
paragraph; who the repository's clients are; whether there are sibling
repositories (backend, legacy, design bundle); whether there is a phase in which
production code must not be written yet. *Never derivable — always ask.*

**Q2. Boundaries and architecture.** How the code is laid out, what may import
what, what is forbidden. Default for a new project: two layers — domain modules
plus a shared layer, each module's public API through a single entry file. If
boundaries are already visible in the tree, state them and ask for confirmation
rather than asking from scratch.

**Q3. What "verified" means.** Which command is the full gate, and which
narrow commands check a change between edits and in a commit — the linter on
the changed files, the type-check, the tests related to them, each tried once
to see that it narrows. Whether a manual step is required — a browser, a real
request, a migration. Separately: which changes need a test — the default
risk classes are money, data written or deleted, access, merges, what lets a
confirmation through, branching logic and a costly break where nobody looks
(`reference/templates.md`, "The testing skill proves a change by its risk"),
with a recorded live check for the rest.

**Q4. Task tracker and key prefix.** Jira (needs the project key), Linear, GitHub
Issues, none. Affects the commit subject, branch names, the PR body, whether a
tracker-conventions skill exists, and which MCP is configured. With Jira, also:
how an answer the agent has acted on is acknowledged — a fixed reaction (offer
✅, "check mark button") or ask each time whether to react or to reply
(`work-jira`, its waiting list of questions).

**Q5. Source of design** — only if the repository has UI. A handoff bundle,
Figma, screenshots plus prose, or none. Affects design-reading skills, the
sources of truth, and the MCP set.

**Q6. Git platform, CLI and branch chain.** GitHub with `gh`, GitLab (including
self-hosted) with `glab`, other. Chain default `feature/* → develop → main`; a
`staging` stage by answer. Where a PR goes by default, and what is protected from
direct pushes.

Then **who deletes a merged branch on the remote** — the user's decision,
asked with the facts and without a recommendation, written to the profile as
`delete branch`:

- `ask` — the merge command's closing steps ask every time, and the merge
  itself deletes nothing. The default without the key;
- `merge` — the merge command deletes it without asking:
  `--remove-source-branch` on `glab mr merge`, `--delete-branch` on
  `gh pr merge`, or `git push origin --delete` in the closing steps;
- `platform` — the platform's setting deletes it: GitHub's "Automatically
  delete head branches", GitLab's "Enable 'Delete source branch' option by
  default". GitLab applies its setting to a merge request created through
  the API — `glab mr create` without `--remove-source-branch` — from 18.10
  on; an older instance applies it only to one created in the web UI.

The facts come before the question, read by `setup` (step 2):

- the setting's value — `gh api repos/{owner}/{repo} --jq .delete_branch_on_merge`,
  `glab api projects/:id --jq .remove_source_branch_after_merge` (`null` reads
  as off) and, on GitLab, `glab api version`;
- the default branch and which branches of the chain are protected;
- the branch the setting would delete: any branch of the chain but the last
  that is neither protected nor the default — an unprotected `staging`
  after a `staging → main` merge. Neither platform deletes a protected or a
  default branch;
- who may change the setting: an admin on GitHub, a Maintainer on GitLab.

On `platform` with a branch exposed, `setup` names it again and offers to
protect it. It changes the setting only on a separate yes, by a command it
shows; without the rights it prints the step for someone who has them.

**Q7. Commit convention.** Default `:gitmoji: type(scope): Subject (KEY-123)`,
body one bullet per point, agent attribution banned. Alternative: `Topic:
description`. Ask whether there is machine enforcement or only agreement, and
offer the task-key check in `commit-msg` — the key taken from the branch name,
a branch without one exempt (`templates.md` → Git hooks).

**Q8. Languages.** Three independent answers: the language of code, identifiers,
commits and PRs — almost always English; the language of committed
documentation; the language the agent speaks in chat. And separately, the
language of strings the end user sees — the single most common place a fresh
session gets it wrong.

**Q9. What has already gone wrong.** Which mistakes the agent or the developer
made repeatedly here. Each answer is a candidate for a hook (if machine-checkable)
or a skill (if it needs understanding). Without this question the hook set comes
out speculative.

**Q10. External access.** Which MCP servers and CLIs exist or are needed: library
docs, tracker, design, browser. Whether there are tokens and where they live.
Which `mluk-work-agent-tools` plugins the project uses, and where the set is
recorded: `.claude/settings.json` by default — every clone gets the same
tooling — or `settings.local.json` when the project's rules keep AI settings
out of git. Which release of the library: follow `main` — every raised
version arrives through `autoUpdate`, the default for one developer — or pin
the latest release tag, so a team moves between releases by a reviewed
settings change.

**Q11. Local notes.** Does the developer keep local material — specs, excerpts,
estimates, plans — and where should it live. Default `docs/local/`, fully
gitignored except its own README.
