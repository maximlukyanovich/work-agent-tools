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

## Hard rules

- **A vague requirement is a question, not a gap to fill.** Never resolve it with
  a plausible default and move on.
- **Nothing is posted to Jira** by this command. Posting the questions as a
  comment is a separate, explicit step.
- **Questions with an obvious answer are not asked.** If the code or the design
  answers it, that is a finding, not a question.
