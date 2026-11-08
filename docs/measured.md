# Measured

Figures from live projects, which stay unnamed, taken from session
transcripts. Each section names its date and conditions; a new measurement is
added as its own section, or a dated line, rather than by rewriting an old one.

## Review against the built-in `/code-review`

The review command this method writes against the built-in `/code-review` at
`high` (Claude Code 2.1.319): 14 branches of two projects, about 40 passes,
recounted on 2026-11-08.

- **Full pass.** On one project's 8 branches, the built-in review found no
  `major` that ours missed, and ours found 7 that it missed. On the other's
  6 branches it was 3 to 3; two of the built-in's three were failing
  end-to-end tests that a truncated gate output hid — the gate now reads red
  output whole.
- **False findings.** Ours raised one in about 40 passes, dropped before the
  report; the built-in, 9 on one project and one or two per pass in half of
  the other's.
- **Delta pass — the weak side.** Over 6 repeat passes on fix deltas, ours
  found nothing of its own and the built-in found 37, two of them `major`
  consequences of fixes that ours had called ready. The rubric now reads
  every diff by three angles, one of them what a removed line held.
- **Cost.** A full pass of ours costs about three built-in runs — its price
  includes the gate, the refutation and the ledger; per confirmed finding
  the two are about even.

## The workflow

Who it is for: a team on a tracker and a forge, where each developer's work
with the agent comes down to choosing and approving the next prompt. The
commands written into the project carry the rest, and each one ends by
printing the next.

- **Sessions.** On a team project, 84 % of 320 sessions over 40 merged tasks
  started with a command or a block the agent had printed (since
  2026-10-01).
- **Fixes in a fresh session.** A fix round run in the session of two reviews
  spent about three quarters of its price re-reading their context; a fresh
  session started by the handoff does not carry it.
