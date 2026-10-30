---
name: kickoff
description: How a piece of work is planned before code — plan mode, exploring before asking, the questionnaire rules (marked recommendation first, at most four questions a round, a closing "anything to add" in the first round), a decisions table, a plan in the chat's language, approval before code. Use when starting a task that needs a plan or before asking the developer questions. Not for trivial edits.
license: MIT
metadata:
  author: Maxim Lukyanovich
  source: https://github.com/maximlukyanovich/work-agent-tools
---

# kickoff

A task starts with a plan the developer has approved, not with code. The plan is
built from what the code says, from questions the code cannot answer, and from
the developer's decisions — recorded, not remembered.

## When it applies

Any task whose answer is not obvious from one file: a feature, an integration,
a refactor across modules, a workflow change. A typo, a one-line fix or a
rename does not need this. When the project has a `/task` command, it collects
the issue, offers its status transition and prepares the branch (see
`reference/templates.md`, "opening steps"); this skill governs the planning
around it. The task command names the change's level first — small, normal
or critical ("The change sets the process" there): a small change takes a
short plan in chat and the developer's yes instead of steps 1, 3 and 6, and
its yes is the approval this skill asks for.

## How to do it

1. **Enter plan mode** before reading widely. In plan mode the only file that
   changes is the plan file.

2. **Explore before asking.** Everything visible from the code, config, git
   history, the issue and its links, and the design source is not a question.
   Use exploration subagents for broad sweeps (one per area, at most three in
   parallel); read the critical files yourself afterwards. A subagent's
   report locates; it does not stand in for the source. Any contract wording
   the plan's logic rests on — an API field, an event's semantics, a rule in
   the spec — is read in the source and quoted in the plan with its path.
   Check library APIs against their docs, not memory. When the task has a
   design source, read the whole screen it touches, not only the component,
   and put a table in the plan: each element of the screen → the code that
   draws it, or why it is left out. Read each element's states (hover, focus,
   pressed, selected, disabled, invalid) and the design's global stylesheet
   from the source as well — they are requirements, and memory of "how such
   a component usually looks" is not a source. Check each screen's design
   status too — by the per-screen statuses the profile's `## Sources of
   truth` names, or a designer's word quoted with its date in the decisions
   file. A screen not ready goes into the last slice and a risk line of
   the plan.

3. **Ask what the code cannot answer** — with the questionnaire tool, not as
   prose in chat:
   - **The recommendation goes first and is marked** `(Recommended)`. Every
     other option carries a one-line trade-off, so the developer can choose
     without asking back.
   - **A requirement that names a reference behaviour sets the
     recommendation.** "As in ChatGPT", "like the old app": the recommended
     option is the one that behaves as the reference does. A technical
     blocker narrows that option — say where it cannot follow the reference
     and why — rather than replacing it; a cheaper option that departs from
     the reference is offered with what it gives up, never marked
     recommended. Observed on a live project: a "spinner on each photo until
     it is uploaded, as in ChatGPT" got "upload on send" as the
     recommendation, and the developer had to point out that the reference
     uploads on attach.
   - **A screen with no design status found is a question** of the first
     round — where the statuses are kept, or the designer's word — and the
     answer is recorded; "no status found" is not a finding.
   - **At most four questions a round.** More than one round is fine; a wall of
     questions is not.
   - **Multi-select where choices are not exclusive.**
   - **A closing "anything to add?" ends the first round, always.** The
     developer often holds a requirement the code cannot show. Its options:
     "no, all covered" and "yes, I will describe it in chat". It counts toward
     the four. In later rounds ask it only when new input is plausible.
   - **Read the answers literally.** An answer may change direction, add a
     constraint or decline; follow what it says, not what was expected.

4. **Record decisions as a table** in the plan — question → decision — so the
   plan can be re-read without the chat.

5. **Write the plan**: context (why this change, what prompted it), the
   decisions table, one recommended approach, slices in execution order with
   the files each touches, assumptions, open questions, and verification —
   how the result is proven. Three more where they apply, and nothing beyond
   them: **a state table** for work that changes state — state × event →
   expected → its proof, a test or a recorded live check; its rows include
   the state lists of the project's testing skill, loaded before the table
   is written, and the frame's events (closed, opened again, remounted
   while a call is in flight) and, in UI, every element that leaves while
   it may hold the focus — a button its own press replaces, a row a re-read
   removes — with where the focus goes; **the framework behaviour the plan
   rests on**, with file:line, read before the plan rather than recalled;
   **one line on the structural option** and why the plan does not take it.
   When the plan describes access — who sees what, and where — the state
   table serves better as a who × where table with the states before and
   after a reset (a link reissued, rights revoked), and under it the events
   that move a person between columns mid-flow: a missed combination is an
   empty cell.
   **The plan is written in the language of the chat**: the developer reads
   it in the approval dialog. Identifiers and paths stay as they are;
   committed text — commits, MR bodies, code comments — keeps the
   repository's language.

   **Assumptions are for minor gaps** — a default nobody would notice. Each is
   one line: what is assumed, on what basis, the alternative — so the
   developer reviews it rather than accepts it unread. Anything the user or
   the designer would see differently, and any gap in the spec or the
   design, is a question in the questionnaire, not an assumption. Such a gap
   is also an open question for whoever owns the spec or the design, never
   settled with the developer as final: the plan says where it was looked
   for, and until the answer the developer picks only placeholder behaviour,
   marked as a placeholder in the task report. A part with no backend
   behind it, or a screen not drawn, is asked with the options of
   `work-jira`'s `issues` skill, "Status at hand-over", when the project
   uses it.

6. **Ask for approval** through the plan-approval mechanism, not with a
   question in chat. A plan returned with comments is revised and submitted
   again.

7. **After approval**: code in slices, the targeted checks of what changed
   after each edit — the full gate runs once per tree, in the review and
   before the push — verify in the real environment, commit each slice
   through the project's commit procedure — only on an explicit go-ahead,
   and never pushed without its own. Each change carries its proof by risk,
   as the project's testing skill says — a test for a change in a risk class
   (money, data written or deleted, access, merges, what lets a confirmation
   through, branching logic, a costly break where nobody looks), a recorded
   live check for the rest, a run on
   the old code only for a test that may pass by coincidence — and one read
   of the slice's diff for what else it changes. Before an edit to state,
   the transition table again, each row with its proof. A slice ends with
   its next step as code blocks: the commit command while it is
   uncommitted; once committed and the plan goes on, continuing here after
   `/compact <focus>` or in a fresh session. A phase ends at its boundary —
   after a commit, one made outside the project's commit command included,
   after a review, before and after a merge — with `/work-bootstrap:handoff`,
   and the next one starts in a fresh session — a small change's stays here
   while its measured diff stays small, a critical change's review is never
   here; inside a long phase, `/compact` with a focus.

8. **After a decision worth keeping** — a convention, a rule for how to ask, a
   preset — propose the matching change in `mluk-work-agent-tools` in one line:
   what changes, in which plugin. The developer decides; the change is made as
   a merge request to that repository, never from the project. The same
   for a mechanism a check finds twice: `layers`, "A finding that comes back".

## How not to do it

- Asking one question per turn, or asking what `git log` or the issue already
  answers.
- Presenting three approaches without a recommendation.
- Recommending the cheaper option over the reference behaviour the
  requirement names.
- Writing the plan in the commit language when the chat is in another one.
- Writing code "to show the idea" before the plan is approved.
- Filing a design decision under assumptions, where it gets approved unread.
- Treating one approval as permission for the whole chain of commits, pushes
  and merge requests.
- Recording decisions only in chat, so the next session asks them again.

## How it is verified

The plan file has the decisions table, slices and a verification section —
and the state table, the framework pointers and the structural line where
they apply — before approval is requested. Each slice ends with its targeted
checks green and the real check the plan named. Every commit was made on an
explicit go-ahead.
