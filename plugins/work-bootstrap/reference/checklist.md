# Final check

Run it and show the result. Anything unchecked is reported, not quietly skipped.

- [ ] `AGENTS.md` exists, covers the seven sections, and does not contradict the
      code.
- [ ] `CLAUDE.md` imports it and duplicates not a single line of it.
- [ ] A block a generator owns in `AGENTS.md` or `CLAUDE.md` is intact,
      between its markers.
- [ ] Skills: real directories under `.claude/skills/`, working symlinks in
      `.agents/skills/`, each with a precise `description`.
- [ ] Commands: only the ones actually needed, each with frontmatter and a hard-
      rules section; shared rules live in the index, not in every file.
- [ ] The command that starts a task, when a tracker is reachable, offers the
      opening steps — in-progress transition, assignee, parent status — as one
      question carrying the current state, and loads `kickoff` before asking
      and the testing skill before writing its plan; with `work-jira`, it
      also names the issue's open questions from the waiting list. Its plan
      carries `kickoff`'s state table — the testing skill's state lists among
      its rows — framework pointers and structural line. Its answer names
      the change's level on its first line — small, normal or critical — and
      a small change gets a short plan in chat and a yes, not plan mode.
- [ ] The command that starts a task takes an optional `worktree` argument
      and offers one when a live `git status` finds the tree busy: beside the
      repository, with the ignored files the work reads linked in, generated
      types produced, its own port for the dev server and the end-to-end
      run, and its own `COMPOSE_PROJECT_NAME` for a Compose stack in the
      `.env` Compose reads, not a service's `env_file:` — each in a file
      copied into the tree, not linked; the merge command's closing steps
      remove it with its branch.
- [ ] Any command that merges ends by offering the closing steps — result
      comment, worklog, branch deletion, anything raised for another team —
      as one question carrying the current state, and merges without deleting
      the branch; with `work-jira`, a posted question goes on the waiting list
      and an answered one is closed there.
- [ ] With a design source: the component skill extends the scale for an
      off-scale value, invents nothing the design does not draw, carries
      every interactive state and the design's global CSS over from the
      source, shows something wherever anything loads, lays out for real content rather than the mock's, and asks for a deviation table
      in the task report; a layout-measuring script runs in
      the task's browser check and in the review command's `layout` mode,
      and a browser measurement stops unless `window.devicePixelRatio` is 1.
- [ ] Hooks: each silent outside its area, each with a test, all wired into
      `settings.json`.
- [ ] Deterministic layer: linter, formatter, types, tests, git hooks, and one
      `validate` command that runs them; the commit runs the targeted checks
      of the changed paths — a profile row per path class whose command
      narrows, tried once — and the full gate only for a path no row covers;
      the review and the push run the full gate once per tree and skip a tree
      already recorded green; no git hook runs the whole gate, and lint-staged
      runs the formatter after the linter's fixes.
- [ ] The gate is fast: one of several parts skips a part whose content is
      unchanged since its last green run — fingerprinted before and after its
      checks, recorded only when the two match — and `--all` runs everything;
      a part's content is everything its tool reads, and every path a part
      excludes names its probe, a command or a way to look; tests run in
      parallel only where they share no outside state, the linter keeps a
      cache when no rule needs type information, the type-check is
      incremental. CI runs without these caches.
- [ ] A review command, if there is one, keeps a pass ledger in the personal
      space: reviews the delta since the last reviewed head, runs blind before
      reconciling, tags findings `new` / `missed` / `escalated` /
      `fix-critique`, opens every report with the same block — trajectory,
      a blocker / major / minor / nit table with zeros, the verdict — and
      recommends a fresh session, except for a small change, and for a
      critical one stops and prints the block for it; while its findings have a fix round open,
      no new work lands on the branch. A finding whose mechanism a ledger
      already holds ends the report with a proposal to move it upstream. A
      delta pass counts, not lists, the missed minors and nits in lines the
      delta does not change; a cheap and real minor or nit is marked
      `fix-now`, and every other one gets its place in the report — a
      techdebt row or `deferred (accepted: <reason>)`, a security finding
      only techdebt — so none is `open` at the merge. A ready verdict with
      `fix-now` ids or techdebt rows to write offers the fix round first, the
      review of its delta next and the merge last; the merge first only on
      the developer's word.
- [ ] Review groups above the delegation threshold go to
      `.claude/agents/review-group.md` (`model: inherit`, read-only tools,
      findings only), un-ignored in `.gitignore`; the review command passes
      `model=<name>` as the Agent call's model; synthesis and refutation
      stay with the session.
- [ ] The commit command, after a task's last commit or a round of review
      fixes, ends its report with the review command ready to paste: the
      range — from the base for the first pass, from the last reviewed head
      after it — what to skip, one code block per branch, and no prompt for
      what follows the review, which the review prints itself.
- [ ] The commands that commit, review and merge take a target — a branch or
      a worktree path — and run there: `git -C <tree>`, the gate in that
      tree.
- [ ] Every command ends with its next step as a block ready to paste, one
      per option, and so does a stop that sends to another command — a
      commit still to make included; at a phase boundary through
      `/work-bootstrap:handoff`. The text and the first block name the same,
      nearest step. The review's is the fix-round prompt naming the ledger —
      when it reads ready too, while `fix-now` ids or techdebt rows are left
      — and otherwise the merge command, once the plan and the task's notes
      show no work left, and "continue the task" while they do; the merge's
      is the next task.
- [ ] A fix to a commit not yet pushed goes into that commit — `--amend`, or
      `--fixup` and `--autosquash`; review fixes go into one fix commit on
      top, made by the first round and amended by the later ones; a pushed
      commit takes a new commit. The review command reads a head rewritten
      that way as `git diff <last head> HEAD`.
- [ ] The commit command compares the staged paths with its proposed list
      right before `git commit`, and after a commit the hook refused commits
      the same index again instead of staging the next group on top.
- [ ] Fixing review findings is a rule in `AGENTS.md` that loads the testing
      skill, and that skill carries the round: a budget in proportion to the
      findings that limits added measures, never fixes; the narrow fix, a
      structural one asked first; proof by risk — a test for a change in a
      risk class, a recorded live check for the rest, a run on the old code
      only for a test that may pass by coincidence; every state the fix
      touches; a transition table before any edit to state — with rows for
      the frame closed, reopened or remounted while a call is in flight; one
      read of the round's diff for side effects; the techdebt rows the
      review placed, written with the fixes; and a finding or transition
      → proof table that the commit command shows before it asks.
- [ ] The testing skill proves by risk: the risk classes, a costly break
      where nobody looks among them with its condition; a test asserts the
      decision, not the look or a mock's answer; an audit removes a test that
      proves nothing or whose break the change's live check shows, and keeps
      one for a silent break; a test of a code convention is left to the
      convention. The review's `test` lens grades by it — a missing test, a
      removed guard and a false claim of coverage `major`, the same gap in
      untouched code `minor` for techdebt, a test of the look a `nit` to
      remove.
- [ ] A fresh checkout installs: with pnpm 11, `allowBuilds` lists every
      dependency build script with its reason, `AGENTS.md` §2 says a new one
      needs an entry, and `pnpm install --frozen-lockfile` passes — and so
      does the type-check, there, with no generated types left over.
- [ ] Once deployed anywhere: the root README has a Deployment section —
      production commands from a frozen install, pinned versions, every
      variable the build and the start need — proven on a fresh checkout.
- [ ] MCP: the example in git, the generated file and `.env` ignored, generation
      works.
- [ ] `docs/README.md` and `docs/local/README.md` exist; `docs/local/` is fully
      ignored except its README. `docs/local/efficiency-remarks.md` exists,
      and `AGENTS.md` §6 has the line that fills it.
- [ ] `.claude/README.md` is a map with links; the command index is in
      `.claude/COMMANDS.md`; nothing inside `commands/` is not a command.
- [ ] `.claude/project-profile.md` exists if any shared plugin is installed.
- [ ] The plugin set is recorded where Q10 put it — `enabledPlugins` in
      `.claude/settings.json` or `settings.local.json` — and the same file
      declares every marketplace it names in `extraKnownMarketplaces` —
      `mluk-work-agent-tools` with `autoUpdate` (and `ref` when Q10 pinned a
      release), `claude-plugins-official` when its plugins are on.
- [ ] With Jira, the profile's `## Tracker` says how a processed answer is
      acknowledged — a reaction, or ask each time.
- [ ] No harness file contains a secret, an absolute path, or a person's name.
- [ ] The onboarding command installs, on a yes and at local scope, the
      declared plugins this checkout lacks, prints `AGENTS.md` §2's commands
      as blocks, lists the plugins' commands from their files, and runs:
      a green table — or rows with concrete actions.

Then report: what was created, what was changed, what was left out and why, and
which questions are still open.
