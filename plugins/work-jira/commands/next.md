---
description: Recommend the next issue to take — unblocked work first, ordered by what it unblocks, the repository's roadmap and size. Read-only.
argument-hint: '[<KEY-N epic> | mine | all]'
---

# /work-jira:next

Answer one question: **what should I pick up next?** The answer is one
recommended issue with the reason, then the ranked alternatives, then what is
blocked and on what. **Read-only** — nothing is moved, assigned or commented.

The tracker knows statuses and links; the repository knows the roadmap and the
blockers nobody has put into Jira. The recommendation needs both, so a run that
can reach only one of them says so and ranks on what it has.

## Steps

1. **Scope.** `$1` narrows the candidates: an epic key limits to its children,
   `mine` to issues assigned to the developer running the command, `all` to the
   whole project. Default: `mine`, falling back to `all` when nothing is
   assigned.

2. **Read the tracker.** Every open issue in scope — status, assignee, estimate,
   remaining time, issue links, parent — and every issue it links to, since a
   dependency may sit outside the scope. One JQL, not one call per issue.
   Then drop what is not a unit of work: epics and stories (they wait on
   their children and are never «taken»), and hour buckets — issues with no
   estimate that stay `In Progress` to collect time for meetings or analysis.
   A story appears in the report only as the parent of a candidate.

3. **Read the repository, when the command runs inside one.** The profile's
   roadmap and open-stubs documents (`docs/planning/roadmap.md`,
   `docs/planning/todo.md` or what the profile names), the current branch and
   whether its work is already merged. These carry the blockers Jira does not:
   "adaptive design does not exist", "backend contract not published".

4. **Work out, per open issue:**
   - **Blocked or not**, and by what — an unresolved `is blocked by` link to
     open work, a dependency the issue's own description names («components
     from KEY-7», «through the API layer, KEY-10»), a roadmap order that puts
     it after open work, or a repository stub its scope depends on. A
     dependency that is `Done` or already merged does not block. **`Relates`
     is not a dependency:** it is symmetric, so reading it as one blocks
     every issue by every other — the direction comes from `Blocks`, the
     description or the roadmap, never from a `relates to` link alone.
   - **What it unblocks** — how many open issues link to it as a dependency.
   - **Roadmap position** — where the repository's roadmap lists it, if at all.
   - **Signals from the board** — `Selected for Development` outranks
     `Backlog`; an issue already `In Progress` with nothing left is
     housekeeping, not work.

5. **Rank the unblocked candidates**: first the roadmap order, then the number
   of issues each one unblocks, then the smaller estimate. When two are equal,
   the one whose design is marked ready. Say the tie-break used.

6. **Report**, in the conversation's language:
   - **Recommended:** `KEY — summary`, estimate, one paragraph of reasoning
     that names what it unblocks and why it goes before the runner-up.
   - **Also ready:** the rest of the unblocked list, one line each with the
     reason it ranks lower.
   - **Blocked:** one line each — `KEY — summary — waits on X`.
   - **Housekeeping:** issues finished but not moved, delivered work without a
     result comment or without a merge request, open questions that block the
     next step and should go to the designer or the product owner *before*
     the work starts. Hour buckets are not housekeeping — they are meant to
     stay open.
   - **The next fork**, when nothing is ready but the recommended issue: what
     becomes ready once it lands, and any decision that must be taken before
     that — pulling the mock half of a blocked task forward, say. A decision
     is named as one, not ranked as work.

## Hard rules

- **Read-only.** No transition, no assignment, no comment, no worklog. The
  developer starts the issue with the project's own command (`/task` or its
  equivalent).
- **A dependency is what the tracker or the repository says, not a guess.** An
  issue with no `Blocks` link, no named dependency in its text and no roadmap
  mention is "unranked on dependencies", not "unblocked".
- **Estimates are the tracker's.** Never re-estimate here; `work-estimation` is
  for that.
- **One recommendation, stated as one.** A list of five "you could" is the
  question handed back.
