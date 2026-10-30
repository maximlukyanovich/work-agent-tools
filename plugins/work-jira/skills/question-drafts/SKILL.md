---
name: question-drafts
description: How a question or notice for someone outside the team is checked before it is shown or posted — the sources it is held against, the table for the developer, where it is posted, the chat digest. Use for any such draft, from /work-jira:questions, a plan, a review or a register.
license: MIT
metadata:
  author: Maxim Lukyanovich
  source: https://github.com/maximlukyanovich/work-agent-tools
---

# question-drafts

## When it applies

Any draft of a question or a notice for someone outside the team — a
designer, an analyst, the product owner, the backend — before it is shown for
posting, wherever it was written: `/work-jira:questions`, a plan, a review, a
register of discrepancies. A draft ages — the plan moves on, a decision
lands — so one from an earlier session is checked again.

## How to do it

1. **Hold each question against:**
   - the spec;
   - the design source — the whole bundle, not the one screen: another
     screen, a component card, a `.d.ts` or the design's own guide often
     draws or states the missing piece;
   - the backend's code and contract;
   - the tracker — the issue, its neighbours, their recent comments;
   - earlier answers — the decisions file, "Decisions already made" in
     `${CLAUDE_PLUGIN_ROOT}/reference/questions-and-decisions.md`: the
     question's topic and its neighbours, since an answer given for a
     different screen often settles this one;
   - the project's own written rules — a component or copy rule the team
     keeps decides a case without the designer.

   A question a source answers is dropped and reported as a finding with its
   pointer, and written into the decisions file; a question the plan no
   longer needs — the feature it served was cut or decided another way — is
   dropped too. On a long draft, split the check by area across a few
   read-only agents, each returning a verdict per question with the quote
   that decides it, and verify the decisive quotes yourself before acting on
   them.

2. **Show the developer a table** before the text: item → answered, partly or
   open, with the quote and where it is → whether it blocks delivery. What
   survives is shown for posting.

3. **Split notices from questions.** A notice tells the person about a
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

4. **After posting**, a digest goes to the team's chat only when a posted
   question blocks delivery; without one, the report says that none blocks.
   The digest's format is the project's. A follow-up to an earlier question
   is posted as the `issues` skill's "People" says.

## How not to do it

- Asking what a screen elsewhere in the bundle, the backend or an earlier
  answer already settles.

## How it is verified

The developer saw the table before the text, and every dropped question has
its pointer in the decisions file.
