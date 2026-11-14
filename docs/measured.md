# Measured

Figures from live projects, which stay unnamed, taken from session
transcripts or measured on a clone. Each section names its date and
conditions; a new measurement is added as its own section, or a dated line,
rather than by rewriting an old one.

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
- **Delta pass, before 2026-11-08.** Ours reads the fix round's delta and
  checks that each fix closed its finding; the built-in re-reads the whole
  branch each time, older code included, at the same price or more. Over 6
  repeat passes on fix deltas, ours found nothing of its own and the
  built-in found 37, two of them `major` consequences of fixes that ours had
  called ready. 2026-11-09: the rubric has since read every diff by three
  angles, one of them what a removed line held, and the passes changed on
  2026-11-08; the delta pass has not been measured again.
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

## Heavy local runs on one machine

2026-11-13–14, one machine: 6 logical cores, 16 GB, WSL2, an editor and five
idle agent sessions open; one project's Vitest suite, 64 of its files, in a
clone. The figures hold for this machine and suite; what the checklist takes
from them is the mechanism, not the numbers.

- **Workers.** Alone, 3 workers (half the cores) took 122 s against 93 s at
  Vitest's default of 5, and kept the machine about as responsive: a 12 ms
  task at normal priority ran at most 2.2 against 2.8 times slower at the
  95th percentile.
- **Sessions at once.** Two sessions at 5 workers each finished in 195 s,
  green, and left 2.8 GB of memory free. Three at once took 246–318 s each
  and all went red, at 1.4–1.8 GB free; three runs alone take about 280 s
  together. A limit read from free memory at start chose 5, 5 and 3 for
  three sessions 15 s apart, and 5 each for three started together.
- **Another process on every core.** With six busy processes at normal
  priority, every run went red whatever its worker count: at `nice` 10,
  1 worker ran 62–69 minutes with 117–193 failures, 3 workers 20–25 minutes
  with 116–285, 5 workers 16 minutes with 249–303. At normal priority, 3 workers
  took 6.5 minutes with 10–16 failures, and the 12 ms task ran 10 times
  slower instead of 5–7.
- **A live implementation, 2026-11-14.** The lock around the whole suite, a
  busy check after it and the runner's default: the holder ran 5 workers at
  `nice` 10; a second run waited 244 s and then passed green in 222 s,
  without a false stop; six busy processes stopped it at 92 % of the cores
  busy, naming them; the whole suite took 228 s at the default against about
  330 s at 3 workers.
