# Templates — A command that merges

### A merge request is shown before it is opened

Its title and description go into the chat as a code block, the way the
commit command shows a message, before the confirmation of the push. A file
path or a pointer alone is not showing it; the question that follows names
only the title. Observed on a live project: a push was confirmed against a
text the chat neither held nor located.

### Waiting for CI

With `full gate: ci` the merge waits for the pipeline, and the status comes
from the merge request itself, never from a list of pipelines by branch. The
wait is bounded, an error ends it where it can be seen — no `2>/dev/null` —
and every outcome is reported. Observed on a live project: a loop on a flag
that does not exist, its errors silenced, read nothing for ten minutes after
the pipeline had gone green.

The project's merge command carries the block of its platform, run in the
background, with `MR` or `PR` the number, `LIMIT` the longest run's time with a
margin, in seconds, and `POLL` the seconds between reads. The block prints `success` and exits 0, or prints
what stopped it and exits 1: a status that is not green, `no result` when the
limit ran out, `status not read` after an error. Only `success` is green.

**GitLab.** The status counts only when `head_pipeline.source` is
`merge_request_event` and `head_pipeline.sha` is the pushed head (`SHA`). One
sha carries two pipelines, and a branch pipeline without the gate job is green
in seconds; after a repeat push `head_pipeline` can still be the last head's.
A gate that runs in branch pipelines compares with `push` instead. `manual`
and `skipped` are not green: a skipped pipeline blocks a merge under
"Pipelines must succeed". The block is written for merge request pipelines:
merged results pipelines test a temporary merged commit and were not tried
with it.

```bash
deadline=$((SECONDS + LIMIT))
while [ "$SECONDS" -lt "$deadline" ]; do
  json=$(glab mr view "$MR" -F json) || { echo "status not read"; exit 1; }
  status=$(printf '%s' "$json" | python3 -c '
import json, sys
p = json.load(sys.stdin).get("head_pipeline") or {}
ours = p.get("source") == "merge_request_event" and p.get("sha") == sys.argv[1]
print(p["status"] if ours else "waiting")
' "$SHA") || { echo "status not read"; exit 1; }
  case "$status" in
    success) echo success; exit 0 ;;
    failed|canceled|manual|skipped) echo "$status"; exit 1 ;;
  esac
  sleep "$POLL"
done
echo "no result"; exit 1
```

**GitHub.** `gh pr checks --watch` does not decide: it exits 0 on a canceled
check, and 1 both on a failed one and while no check has been reported yet. So
the block reads each check's `bucket`. Skipped checks beside a passed one are
green; all skipped is `skipped`, not green, since the gate may not have run.

```bash
deadline=$((SECONDS + LIMIT))
while [ "$SECONDS" -lt "$deadline" ]; do
  if out=$(gh pr checks "$PR" --json name,bucket 2>&1); then
    status=$(printf '%s' "$out" | python3 -c '
import json, sys
b = [check["bucket"] for check in json.load(sys.stdin)]
print("failed" if "fail" in b else "waiting" if "pending" in b or not b
      else "canceled" if "cancel" in b else "success" if "pass" in b else "skipped")
') || { echo "status not read"; exit 1; }
  else
    case "$out" in
      *"no checks reported"*) status=waiting ;;
      *) printf '%s\n' "$out" >&2; echo "status not read"; exit 1 ;;
    esac
  fi
  case "$status" in
    success) echo success; exit 0 ;;
    failed|canceled|skipped) echo "$status"; exit 1 ;;
  esac
  sleep "$POLL"
done
echo "no result"; exit 1
```

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
