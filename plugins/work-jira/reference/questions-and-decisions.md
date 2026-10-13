# Questions and decisions

Read on demand, from the `issues` skill and the commands that post, close or
draft a question. Both files below are the project's, personal and gitignored.

## Questions waiting for an answer

A posted question is work the developer is waiting on, and its reply lands in
a thread nobody watches. So each one goes on the waiting list —
`docs/local/questions.md` in the project, personal and gitignored like the
team file: one line per question — issue · to whom · comment id · date · what
it blocks.

- **Remember and remind; do not poll.** Name an issue's open lines when work on
  it starts, before it is closed, and whenever a status report or a closing
  step touches it — the ones that block delivery first. Asked what is still
  pending, answer from the file. A reminder costs a file read; a forgotten
  question costs a task that cannot be closed.
- **Check one thread, not the tracker.** The file is a reminder, not the
  truth — a reply can land unrecorded. When a decision rests on a question —
  closing the issue, starting work it blocks — read that open line's thread,
  one call each; closed lines are skipped. A sweep across every issue with an
  open question is long and costly: offer it, and run it only on a yes. The
  tracker's notification feed is no shortcut: read with an API token, it comes
  back empty.
- **A question closes on an answer or a decision** — a reply in its thread, an
  answer the developer relays, or the question dropped. Mark the line with the
  date and where the answer is, and copy the decision into the decisions file
  ("Decisions already made"). A dropped question is said so in its thread,
  so the person asked stops working on it.
- **A processed answer is acknowledged where it was given.** Once a reply has
  been acted on — in the code, the plan or a new question — its author sees
  that it landed: a reaction under it, or a reply in its thread when there is
  something to say (a clarification, a follow-up, a disagreement). Which one is
  the developer's choice, asked once and recorded in the profile's
  `## Tracker`: a fixed reaction (offer ✅, "check mark button"), or asking each
  time whether to react or to reply. An API token cannot set a Jira reaction —
  the reactions gateway answers 401 and the GraphQL `addReaction` covers
  Confluence only — so a reaction is the developer's click: hand over the list,
  issue · comment id · link `…/browse/KEY?focusedCommentId=ID`. Leave out the
  ones already reacted to: the token can read them — GraphQL
  `graphStore_userReactedToIssueComment(id: "ari:cloud:identity::user/<accountId>",
  queryContext: "ari:cloud:platform::site/<cloudId>")` with
  `@optIn(to: "GraphStoreUserReactedToIssueComment")` returns the comments the
  developer reacted to, any emoji, as `…:issue-comment/<issueId>/<commentId>`.
  A reply goes through `comment(..., reply_to=<root id>)`.

## Decisions already made

An answer settles more than the question it was asked under: the next
question, on a neighbouring screen or another issue, often has it already.
So the decisions are kept too — `docs/local/decisions.md`, personal and
gitignored like the waiting list — **grouped by topic, not by issue**: one
line per decision · who decided · a link to the comment
(`…/browse/KEY?focusedCommentId=ID`) · the date.

- **Written whenever a decision lands**: a question closing on the waiting
  list, an answer under some other issue, a call the developer relays. A
  later answer that overrides an earlier one marks it "(replaced by ID)";
  both stay, so the history still reads.
- **What the sources settled goes in too.** A drafted question that the spec,
  the design or the backend's contract turned out to answer is written down
  with its pointer — file and line — so the same question is not drafted a
  second time.
- **Read before any question is drafted** — the topic and its neighbours
  (`/work-jira:questions`, step 6). Built once from the tracker: export every
  comment by the people who answer — design, product, backend — and group it
  by topic; afterwards it is kept by hand. A one-off export of a busy
  backend's comments is long; delegate the grouping and record the comments
  the export cut short, to be read in full before anything rests on them.
