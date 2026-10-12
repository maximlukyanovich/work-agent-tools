---
description: Collect what is still unclear about an issue — from its own text, the design, the spec and the branch state.
argument-hint: '<KEY-123>'
---

# /work-jira:questions

Surface the open questions on an issue **before** work starts, when answering
them is cheap. **Read-only.**

## Steps

1. **Read the issue**: description, acceptance criteria, comments, attachments,
   parent, linked issues.

2. **Read what it points at**: the spec section, the design screen, related
   issues. A reference that leads nowhere — a renamed screen, a missing section —
   is itself a question.

3. **Look for the usual gaps.** Acceptance criteria that no one could test.
   A data source named but not specified. An edge case the design shows in one
   state only. A number with no source. A dependency on work that does not exist
   yet.

4. **Check the code** for what the issue assumes to exist: a component, an
   endpoint, a token. An assumption that does not hold is a question, not a task
   for later discovery.

5. **Report grouped by addressee** — analyst, designer, backend, product — each
   question one line, with what it blocks and a proposed default where one exists.
   Who holds each role, and how to mention them, comes from the project's
   team file (`${CLAUDE_PLUGIN_ROOT}/reference/team.md`); missing → offer to
   create it and ask for every row. A role is never inferred from context.
   Each group is written in its reader's language: the spec's and the
   design's terms for a designer or analyst, the backend's own field and
   endpoint names for the backend — never frontend component names.

6. **Re-check every draft right before it is posted.** A draft ages: the plan
   moves on, a decision lands, a source is read more closely. Hold each
   question against:
   - the spec;
   - the design source — the whole bundle, not the one screen: another
     screen, a component card, a `.d.ts` or the design's own guide often
     draws or states the missing piece;
   - the backend's code and contract;
   - earlier answers — the decisions file (`issues` skill, "Decisions already
     made"), the question's topic and its neighbours: an answer given for a
     different screen often settles this one;
   - the project's own written rules — a component or copy rule the team
     keeps decides a case without the designer.

   A question a source answers is dropped and reported as a finding with its
   pointer, and written into the decisions file; a question the plan no
   longer needs — the feature it served was cut or decided another way — is
   dropped too. On a long draft, split the check by area across a few
   read-only agents, each returning a verdict per question (answered, partly,
   open) with the quote that decides it, and verify the decisive quotes
   yourself before acting on them. What survives is posted.

7. **Split notices from questions.** A notice tells the person about a
   decision already made by someone entitled to make it, or settled by a
   source — an answer applied with a change a standing rule requires, a tone
   taken from the design's own precedent: what was done, why, and an offer to
   revert. A conflict between two of the person's own sources — the design's
   guide and one of its screens, two screens drawing the same thing two ways
   — is not the team's to settle: it is a question, or a decision the
   developer takes explicitly before it can become a notice. A notice states
   done work, so it is posted after that work has landed, together with the
   questions. In a comment that carries both, they are **two lists, each
   numbered from 1** — the questions that need an answer, then the notices
   that need one only if the reader disagrees — so the reader sees at once
   what waits on them; one running number across both hides it.

## Hard rules

- **A vague requirement is a question, not a gap to fill.** Never resolve it with
  a plausible default and move on.
- **Nothing is posted to Jira** by this command. Posting the questions as a
  comment is a separate, explicit step — and once posted, each goes on the
  waiting list (`issues` skill, "Questions waiting for an answer"). That step
  starts with steps 6 and 7, even for drafts written in an earlier session.
- **Questions with an obvious answer are not asked.** If the code, the design,
  an earlier answer or the team's own rule answers it, that is a finding, not
  a question.
