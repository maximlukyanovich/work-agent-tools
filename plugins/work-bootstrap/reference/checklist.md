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
      question carrying the current state, and loads `kickoff` before asking;
      with `work-jira`, it also names the issue's open questions from the
      waiting list. Its plan carries `kickoff`'s state table, framework
      pointers and structural line.
- [ ] The command that starts a task takes an optional `worktree` argument
      and offers one when a live `git status` finds the tree busy: beside the
      repository, with the ignored files the work reads linked in, generated
      types produced, and its own port for the dev server and the end-to-end
      run; the merge command's closing steps remove it with its branch.
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
      the task's browser check and in the review command's `layout` mode.
- [ ] Hooks: each silent outside its area, each with a test, all wired into
      `settings.json`.
- [ ] Deterministic layer: linter, formatter, types, tests, git hooks, and one
      `validate` command that runs them; the commands that commit and push run
      it (the push skips a tree already validated), no git hook runs the whole
      gate, and lint-staged runs the formatter after the linter's fixes.
- [ ] A review command, if there is one, keeps a pass ledger in the personal
      space: reviews the delta since the last reviewed head, runs blind before
      reconciling, tags findings `new` / `missed` / `escalated` /
      `fix-critique`, opens every report with the same block — trajectory,
      a blocker / major / minor / nit table with zeros, the verdict — and
      recommends a fresh session. A finding whose mechanism a ledger already
      holds ends the report with a proposal to move it upstream.
- [ ] Review groups above the delegation threshold go to
      `.claude/agents/review-group.md` (`model: sonnet`, read-only tools,
      findings only), un-ignored in `.gitignore`; the review command passes
      `model=<name>` as the Agent call's model; synthesis and refutation
      stay with the session.
- [ ] The commit command, after a task's last commit or a round of review
      fixes, ends its report with the review command ready to paste: the
      range, what to skip, one code block per branch.
- [ ] The commands that commit, review and merge take a target — a branch or
      a worktree path — and run there: `git -C <tree>`, the gate in that
      tree.
- [ ] Every command ends with its next step as a block ready to paste, one
      per option; at a phase boundary through `/work-bootstrap:handoff`. The
      review's is the fix-round prompt naming the ledger, or the merge
      command when it reads ready; the merge's is the next task.
- [ ] The commit command compares the staged paths with its proposed list
      right before `git commit`, and after a commit the hook refused commits
      the same index again instead of staging the next group on top.
- [ ] Fixing review findings is a rule in `AGENTS.md` that loads the testing
      skill, and that skill asks for a reverted-fix test per finding, every
      state the fix touches, a transition table before any edit to state,
      and a finding or transition → test table that the commit command shows
      before it asks.
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
      ignored except its README.
- [ ] `.claude/README.md` is a map with links; the command index is in
      `.claude/COMMANDS.md`; nothing inside `commands/` is not a command.
- [ ] `.claude/project-profile.md` exists if any shared plugin is installed.
- [ ] The plugin set is recorded where Q10 put it — `enabledPlugins` in
      `.claude/settings.json` or `settings.local.json`.
- [ ] With Jira, the profile's `## Tracker` says how a processed answer is
      acknowledged — a reaction, or ask each time.
- [ ] No harness file contains a secret, an absolute path, or a person's name.
- [ ] The onboarding command runs and prints a green table — or rows with
      concrete actions.

Then report: what was created, what was changed, what was left out and why, and
which questions are still open.
