---
description: Check whether an issue is actually done — acceptance criteria against the code, not against the status field.
argument-hint: '<KEY-123>'
---

# /work-jira:status

Answer one question: is this issue really done? **Read-only** — no status is
moved, no comment posted.

## Steps

1. **Read the issue** and its acceptance criteria.

2. **Check each criterion against the code**, not against the status field. Cite
   the file and line that satisfies it, or say plainly that nothing does.

3. **Run the project's quality gate** if the profile names one, and report the
   result rather than summarising it.

4. **Check the Definition of Done** from the company standard: is the change
   reviewed, deployed to the test environment, verified by QA, are blocking
   defects retested. Say which of these the agent cannot know.

5. **Check the waiting list** (`issues` skill, "Questions waiting for an
   answer"): read the thread of each open line for this issue — one call
   each, closed lines skipped. A question still unanswered that a criterion depends on makes that
   criterion unverifiable, whatever the code says.

6. **Report a verdict per criterion** — met, not met, unverifiable — then the
   single line that matters: done, or what remains.

## Hard rules

- **Ready for QA is not Done.** The standard is explicit; do not conflate them.
- **Never move the status.** That is the developer's action, and it follows this
  report rather than replacing it.
- **Unverifiable is a valid verdict.** Say so instead of guessing.
- **Remaining time on a Done issue is not a defect.** Report it, never
  propose zeroing it: the developer may keep a reserve on finished work
  deliberately.
