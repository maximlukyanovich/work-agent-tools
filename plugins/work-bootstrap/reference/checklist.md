# Final check

Run it and show the result. Anything unchecked is reported, not quietly skipped.

- [ ] `AGENTS.md` exists, covers the seven sections, and does not contradict the
      code.
- [ ] `CLAUDE.md` imports it and duplicates not a single line of it.
- [ ] Skills: real directories under `.claude/skills/`, working symlinks in
      `.agents/skills/`, each with a precise `description`.
- [ ] Commands: only the ones actually needed, each with frontmatter and a hard-
      rules section; shared rules live in the index, not in every file.
- [ ] Any command that merges ends by offering the closing steps — result
      comment, worklog, branch deletion, anything raised for another team —
      as one question carrying the current state, and merges without deleting
      the branch.
- [ ] Hooks: each silent outside its area, each with a test, all wired into
      `settings.json`.
- [ ] Deterministic layer: linter, formatter, types, tests, git hooks, and one
      `validate` command that runs them.
- [ ] MCP: the example in git, the generated file and `.env` ignored, generation
      works.
- [ ] `docs/README.md` and `docs/local/README.md` exist; `docs/local/` is fully
      ignored except its README.
- [ ] `.claude/README.md` is a map with links; the command index is in
      `.claude/COMMANDS.md`; nothing inside `commands/` is not a command.
- [ ] `.claude/project-profile.md` exists if any shared plugin is installed.
- [ ] No harness file contains a secret, an absolute path, or a person's name.
- [ ] The onboarding command runs and prints a green table — or rows with
      concrete actions.

Then report: what was created, what was changed, what was left out and why, and
which questions are still open.
