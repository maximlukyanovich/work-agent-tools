# Templates — A command that reviews: hand-over, fixes, merge

**The commit command hands the phase over.** Every report ends through
`/work-bootstrap:handoff`. In the middle of a task that is the next slice —
a fresh session or `/compact`, by the handoff's criterion; after the last
commit of a task, or of a round of review fixes, the review command ready to
paste into a fresh session, or to run here for a small change. The review
command carries:

- the range — from where the branch left its base branch for the first pass,
  from the head the last pass reviewed after it. Never `<base>..<head>` once
  a pass exists: an explicit range outranks the ledger's delta, and a fix
  round of six files then gets a review of the whole branch — observed on a
  live project, a pass over 120 files that found nine old minors, which read
  as bugs of the fixes;
- what to skip — merge commits, other people's commits;
- one code block per branch;
- no prompt for what follows the review: the fix round or the merge is the
  review's to print at its end. A `NEXT.md` written now is for the step after
  the review and its fixes, and says so.

Left to the agent's memory, this step is skipped precisely when a task ends
well. Observed on a live project: a finished task was reported done with
commits, questions and a library merge request all proposed, and the review
was not. The rule was already a saved preference.

**A commit the hook refuses leaves its paths staged.** A `commit-msg` hook
that turns the message down — a header over the length limit, a missing task
key — stops the commit and keeps the index. The next `git add` adds to it,
and the next commit takes both groups. So the commit command, right before
`git commit`, compares `git diff --cached --name-only` with the list it
proposed and stops on a difference; after a refusal it fixes the message and
commits the same index again — it never stages the next group on top.
Observed on a live project: a header three characters too long left one
task's six files staged, the following commit for another task swept them in,
and the pair had to be split with `git reset --soft` before the push.

**A fix to a commit not yet pushed goes into that commit; review fixes go
into one fix commit.** A bug found while the work goes on, whose cause is a
commit no remote holds yet (`git branch -r --contains <sha>` prints
nothing), is fixed inside it:
`git commit --amend` when it is `HEAD`, otherwise `git commit --fixup=<sha>`
and `git rebase --autosquash <sha>~` — before git 2.44 a rebase without
`-i` ignores `--autosquash` and says nothing, so there it is
`GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <sha>~`. The message is
reworded when the fix changes what it says. A rebase that stops on a
conflict — a later commit changed the same lines — is aborted
(`git rebase --abort`) and the fix becomes a new commit: a conflict resolved
inside history the gate never sees again is how a fold breaks a commit. A
pushed commit takes a new commit, never a force push. A round of review
fixes is placed differently: the first round after a review is one new
commit on top of the series, and every later round goes into that fix commit
while it is unpushed — amended, or folded with `--fixup` when it is not
`HEAD`. The series' own commits are not rewritten for a review fix. A branch
merges with its history, and "fix", then "fix the fix" tells a later reader
nothing the corrected commit does not; the review's story is in the ledger,
which reads a rewritten head (step 1 above). So the push waits for the
review and its fixes, not the other way round. Observed on a live project: a
fourteen-commit branch carried five commits that only fixed its other
commits, after six review passes; and later, spreading one round of fixes
over four unpushed slices took blame by hunk, four reworded messages, a
partial staging the formatter hook mangled and a rebase that stopped on a
file every slice had touched.

**Fixing the findings has its own discipline**, and the review command cannot
enforce it: the fixes are made in a fresh session from the handoff's fix
prompt, where no command runs. So the rule lives where every session reads
it — one line in `AGENTS.md` — and points to the project's testing skill,
which carries the round:

- **a budget in proportion to the findings** — minutes for a document or a
  one-line fix, about twenty to thirty for a round on a small task; a round
  that will plainly take longer says why before it starts. The budget limits
  the measures added on top, never the fixes: every finding taken is closed,
  or named with what it waits on, and a measure that costs more than the
  fix — agents critiquing the plan or the delta, a batch of reverts, a
  repeated gate or build — is asked about with its price, never added by
  default;
- **the narrow fix** — a structural one (moving logic out, moving tests, a
  new convention) is a question first, with the narrow fix and a techdebt
  entry as the default; a fix that would need its own parser, protocol or
  format where the code already uses a library for the job takes the
  library; a mechanism the fix introduces covers every site of its class,
  not only the sites the finding named;
- **proof by risk**, by the skill's rule (`testing-skill.md`, "The testing skill proves
  a change by its risk") — a test in the same commit for a change in a risk
  class; a live check, recorded, for the rest. A test that may pass by
  coincidence — the focus, timing, a fake or a mock, an async step — is run
  once against the code it replaces and goes red there; an existing test
  that "covers the area" usually passes either way, and a plain input →
  output test needs no such run;
- **every state the fix touches**, not the one the finding named: a query's
  pending, error, and error **with stale data**; success that may be out of
  date — while a refetch is in flight, and while the cache still counts as
  fresh, so nothing is read again on mount; every mutation in flight, not
  the last; a stream before its history has replayed. A fix round that
  closes one state ships the next round's `major` in the state beside it;
- **a transition table before any edit to state**, a fix or not: state ×
  event → expected → proof, by the same risk rule. The
  states an edit touches are listed before the code, not found by the next
  review. The frame around the state has events too — closed, opened again,
  asked to open while open, remounted — and each gets a row while a call is
  still in flight, saying where that call's outcome lands. A reset by
  remount (a new `key`) throws away whatever the call would still deliver;
- **one read of the round's own diff** before the commit: what else does
  each change do — in which states, for which users of the element (mouse,
  keyboard, screen reader, another order of events)? A precedent is copied
  whole. A doubt in the reasoning — "if…", "probably…", "fine anyway" —
  becomes a row, a check or a report line; a changed sentence is reread
  whole, and a changed rule is searched for across the docs, the harness and
  the tests;
- **the proof handed back** before the commit is asked for, and shown by the
  commit command: one row per finding, or per transition of a state edit —
  the test (red on the old code where the rule asks for it) or the live
  check;
- **the techdebt places written** with the fixes — each finding the review
  placed in techdebt becomes its row (what breaks, who sees it, the
  priority, the id), in the round's commit when the file is in git.

Observed on a live project: pass 2 found two new `major`s, both in states
the pass-1 fixes had touched and not enumerated, and both untested — the
testing skill held the rule already, and nothing loaded it. Later, a fix that
reworked a hand-over between two screens dropped a guard one transition
away from the one it fixed; a transition table lists that row. And a dialog
reset by remount on every opening lost a sign-in finishing behind a close:
the outcome reached an unmounted component, and the reopened card showed its
first step to a user the service had just signed in. Later still, 83 reverts
in a row went red and found nothing, while the defects the rounds brought —
five to seven each — were side effects of fixes that worked, which a revert
cannot see; that time now goes to the read of the diff.

**A merging command reads the ledger** before the merge: no pass on the
current head, or `major`+ still open → it says so and merges only on an
explicit yes.

**Cost.** The same head costs nothing; a delta costs a delta. The ledger is one
line per finding, not a copy of the reports. The rules live in the command
text, which loads only when invoked — not in `AGENTS.md` or a skill
description, which every session pays for.
