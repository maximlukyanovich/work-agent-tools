# Templates — A command that merges

### A command that merges must offer the closing steps

Merging is the moment a task stops being visible. Whatever is not done in the
minute after it is done weeks later, from memory, against a branch nobody
recognises — or never. So a command that merges ends with **one question,
asked every time**, covering:

- **the result comment** on the issues the branch touched;
- **the worklog**;
- **deleting the branch** — locally, and on the remote when the profile's
  `delete branch` is `ask` or missing; with `merge` the merge command has
  deleted the remote branch without asking, with `platform` the platform
  has. For a branch checked out in a worktree, `git worktree remove` first;
- **anything the work raised for someone else** — a defect belonging to
  another team, a question for the designer. A question that gets posted
  goes on the waiting list, and one the merge answers is closed there.

All of these are optional and none is done unasked. The obligation is to
**ask**, not to do. Two rules make the question worth answering:

- **Carry the state into it.** «Log some time?» invites a shrug; «logged 0 of
  an estimated 8h, nothing logged today» gets an answer. Same for whether the
  issue already has a comment and where the branch still exists.
- **Never infer the hours.** Elapsed session time is not worked time. The
  developer names the number.

Deletion on the remote is the user's decision — per merge, or once, by
the profile's `delete branch` (Q6): `ask` merges without deleting, `merge`
deletes with the merge, `platform` leaves it to the platform's setting. The
library recommends none of them. An unanswered step is reported as still open, never dropped
silently. After the closing steps, `/work-bootstrap:handoff` prints the start
of the next task for a fresh session.
