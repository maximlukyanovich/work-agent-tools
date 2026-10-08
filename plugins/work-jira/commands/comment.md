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

3. **Check each issue's description first.** QA tests against it: what shipped,
   what moved to other issues (cards) and the known limits must be there. A
   description that has gone stale is offered for an update before the
   comment — the `issues` skill, "Description".

4. **Draft each comment** and show it in the chat for review. A comment that
   addresses or mentions someone takes the person and the account id from the
   project's team file (`${CLAUDE_PLUGIN_ROOT}/reference/team.md`). Shape:

   - A header of one readable sentence with the merge request as a link whose
     text is the whole `MR !N` — «Доставлено в [MR !1](…) (`feat/x` →
     `develop`)» — never a bare URL. Without a merge request, the header says
     where the work landed instead («Доставлено в `develop` напрямую
     (`sha`…`sha`)»).
   - A bullet list of what shipped, each starting with the area and focused on
     the outcome rather than the process.
   - **Deviations are deviations from the spec or the design** — a size off
     the scale, a colour, a timing, a missing default text: what a designer or
     QA would notice. Implementation choices (a prop's type, a component API,
     a library) are the team's own business and belong in the merge request,
     not here. A deviation the developer decided alone is never labelled
     "agreed"; the section is "for the designer / product owner to confirm",
     states what was done and the alternative, and the point stays open.
   - An `Out of scope / follow-ups` block when there is something to flag.

5. **Post only on an explicit go-ahead**, through `scripts/jira.py` as ADF —
   `comment(key, doc(p(header), ul([...])))`, `edit_comment` to amend,
   `comment(..., reply_to=<id>)` to answer in an earlier comment's thread. Not
   through MCP: a Markdown comment stores a URL as plain text, which Jira does
   not auto-link, so the merge-request link arrives dead. Formatting rules from
   the `issues` skill apply: backticks for inline code, `[[KEY-1]]` for an
   issue card, no bold inside list items. A comment that asks someone
   something goes on the waiting list when it is posted; a reply that answers
   or drops a listed question closes its line (`issues` skill). Hand each
   posted comment back as a link, `comment_url(key, id)`.

6. **Then, separately, offer a worklog.** Propose one short sentence per issue.
   The default answer is "text only" — the developer may want the wording but log
   the time elsewhere. On a yes, **ask for the duration**; never invent one.

## Hard rules

- **Two decisions, not one.** Comments and worklog are asked separately.
- **Nothing is posted silently**, and nothing is posted that the developer has
  not read.
- **Never invent time spent.**
- **Not triggered by conversation.** "готово", "мержим", "done" mark a
  checkpoint, not the end of the work — this command runs when it is called.
