---
name: kickoff
description: How a piece of work is planned before code — plan mode, exploring before asking, the questionnaire rules (marked recommendation first, at most four questions a round, a closing "anything to add" in the first round), a decisions table, a plan in the chat's language, approval before code. Use when starting a task that needs a plan or before asking the developer questions. Not for trivial edits.
---

# kickoff

A task starts with a plan the developer has approved, not with code. The plan is
built from what the code says, from questions the code cannot answer, and from
the developer's decisions — recorded, not remembered.

## When it applies

Any task whose answer is not obvious from one file: a feature, an integration,
a refactor across modules, a workflow change. A typo, a one-line fix or a
rename does not need this. When the project has a `/task` command, it collects
the issue and prepares the branch; this skill governs the planning around it.

## How to do it

1. **Enter plan mode** before reading widely. In plan mode the only file that
   changes is the plan file.

2. **Explore before asking.** Everything visible from the code, config, git
   history, the issue and its links, and the design source is not a question.
   Use exploration subagents for broad sweeps (one per area, at most three in
   parallel); read the critical files yourself afterwards. Check library APIs
   against their docs, not memory.

3. **Ask what the code cannot answer** — with the questionnaire tool, not as
   prose in chat:
   - **The recommendation goes first and is marked** `(Recommended)`. Every
     other option carries a one-line trade-off, so the developer can choose
     without asking back.
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
   the files each touches, assumptions the developer can overturn, open
   questions, and verification — how the result is proven. **The plan is
   written in the language of the chat**: the developer reads it in the
   approval dialog. Identifiers and paths stay as they are; committed text —
   commits, MR bodies, code comments — keeps the repository's language.

6. **Ask for approval** through the plan-approval mechanism, not with a
   question in chat. A plan returned with comments is revised and submitted
   again.

7. **After approval**: code in slices, run the gate after each, verify in the
   real environment, commit each slice through the project's commit procedure
   — only on an explicit go-ahead, and never pushed without its own.

8. **After a decision worth keeping** — a convention, a rule for how to ask, a
   preset — propose the matching change in `mluk-work-agent-tools` in one line:
   what changes, in which plugin. The developer decides; the change is made as
   a merge request to that repository, never from the project.

## How not to do it

- Asking one question per turn, or asking what `git log` or the issue already
  answers.
- Presenting three approaches without a recommendation.
- Writing the plan in the commit language when the chat is in another one.
- Writing code "to show the idea" before the plan is approved.
- Treating one approval as permission for the whole chain of commits, pushes
  and merge requests.
- Recording decisions only in chat, so the next session asks them again.

## How it is verified

The plan file has the decisions table, slices and a verification section before
approval is requested. Each slice ends with the gate green and the real check
the plan named. Every commit was made on an explicit go-ahead.
