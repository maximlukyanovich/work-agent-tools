# Templates — A project with a design source

### A project with a design source holds to it

When the project implements a design, its component skill (or equivalent)
carries these rules; they are where a review finds drift.

- **A value off the design's scale extends the scale.** A size, radius or
  spacing the design draws between two steps becomes a new token rather than
  a silent snap to the nearer one — even a 1 px difference is visible across a
  product. The deviation goes into the project's register and to the
  designer, in the result comment's "for the designer to confirm" block.
- **Nothing the design does not draw is invented** — a control, a state, a
  piece of copy. It becomes a question; a placeholder is tolerated only while
  the question is open and only if the task report names it.
- **Know which copy is the source.** A design export can carry the same
  component twice — the files the screens import and an older bundled copy.
  Before reading, establish which one the rendered screens actually use, and
  write it into the project's design-source document; a whole pass was once
  briefed from the stale copy.
- **The sources take precedence over a screen.** The design's guide, its
  component sources and its tokens are what the code follows. A screen that
  disagrees with them is escalated to the developer, not settled by the
  agent — and the escalation names the likely reading: a designer who
  updated the screen and not the sources usually means the screen as the
  final decision. Whatever the developer decides goes into the project's
  register, and the designer gets the gaps together, in one comment asking
  for the sources to be brought up to date — not a question in every task.
- **Every state from the source, read each time.** Hover, focus, pressed,
  selected, disabled, invalid, open, loading — and the design's global
  stylesheet (link and title hovers, the focus ring, scrollbars) — are part
  of the component as much as its size. Before implementing or changing a
  component, open its source in the design and the global CSS and carry
  every state over as written; never fill a state in from memory, from the
  library the component is built on (a stock focus ring, a hover wash), or
  from a similar component. A state the design does not draw is a
  question, not a default.
- **Every load shows something.** Wherever something loads — a page, a
  history, a list, a search, an image, an upload, a retry, a reconnect —
  decide what is on screen until it arrives and while it is slow. Designs
  draw few of these; when the design is silent, it is a question for the
  designer, with a placeholder built from existing primitives (a skeleton,
  an inline spinner) named in the task report — never a blank area.
- **Real content, not the mock's.** A design's data is short and tidy; real
  names run six lines, prices carry two currencies, lists come empty or long,
  and the layout gets a narrower width than the mock. Lay out for that within
  the design's rules — clamp what can grow, keeping the full text reachable;
  wrap what must wrap; check the narrow widths. This is the team's to solve,
  not a question for every case, and it is work the design did not contain:
  the result comment names it, so it counts toward time over the optimistic
  estimate.
- **The task report lists deviations from the screen**, one row each: the
  design's value, the code's, why, and whether the designer has seen it.
- **A measurement, not an eyeball.** A project script compares the computed
  styles of the design's screen with the app's at the target viewport and
  prints the elements that differ with their values. It runs during the
  task's browser check, before review, and the review command accepts a
  `layout` mode that runs it on the branch. The script is the project's; its
  contract — inputs are the two URLs and a list of selectors, output is one
  line per differing property — is what the commands rely on. A measurement
  through the agent's browser first checks that `window.devicePixelRatio`
  is 1 and stops when it is not: the browser keeps a zoom level per host,
  and every size read at another scale is off by its factor. Observed on a
  live project: `localhost` opened at 80%, borders measured 1.25 px and
  sizes came out fractional; device-metrics emulation did not reset the
  zoom, and the same server opened as `127.0.0.1` did.
