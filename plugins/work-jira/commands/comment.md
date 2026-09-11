---
description: Draft and post a result comment on the issues a branch touched, then offer a worklog.
argument-hint: '[<target branch>]'
---

# /work-jira:comment

Close the loop on the issues a branch delivered: what shipped, in their language,
on their issues.

**Posts to Jira**, but never without showing the text and being told to.

## Steps

1. **Collect the issue keys** from the commits in `<target>..HEAD`, target being
   `$1` or the profile's integration branch.

2. **List them** — one line per issue, `KEY — summary` — and ask which to comment
   on: all, a subset, or none.

3. **Draft each comment** and show it in the chat for review. Shape: a header
   naming the merge request when one exists, otherwise a plain result line; then
   a bullet list of what shipped, each starting with the area and focused on the
   outcome rather than the process. An `Out of scope / follow-ups` block when
   there is something to flag.

4. **Post only on an explicit go-ahead**, applying the formatting rules from the
   `issues` skill: backticks for inline code, an issue as a link whose text
   carries key and summary (a comment through MCP cannot carry a card), no bold
   inside list items.

5. **Then, separately, offer a worklog.** Propose one short sentence per issue.
   The default answer is "text only" — the developer may want the wording but log
   the time elsewhere. On a yes, **ask for the duration**; never invent one.

## Hard rules

- **Two decisions, not one.** Comments and worklog are asked separately.
- **Nothing is posted silently**, and nothing is posted that the developer has
  not read.
- **Never invent time spent.**
- **Not triggered by conversation.** "готово", "мержим", "done" mark a
  checkpoint, not the end of the work — this command runs when it is called.
