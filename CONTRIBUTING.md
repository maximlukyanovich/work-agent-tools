# Contributing

Issues and pull requests are welcome — a rule that misfired in your project, a
trap worth naming, a fix.

- Plugin texts, commits and pull requests are in English.
- A rule that names your project's paths, keys or design system belongs in
  your project's profile, not here. No real project is named — not its name,
  issue keys, paths or quotes, in the change or in the pull request; examples
  use `PROJ-N`.
- A change to what a set-up project must carry over — the templates, the
  checklist, `audit` — comes with an entry in
  [`plugins/work-bootstrap/CHANGES.md`](plugins/work-bootstrap/CHANGES.md).
- A change to a plugin's files, its README aside, raises that plugin's
  `version` in `plugin.json` — the levels are in [`AGENTS.md`](AGENTS.md) §2.
  Without the raise the change reaches nobody.
- Before opening a pull request, run `python3 scripts/check.py` after
  `git fetch` — it compares versions against `origin/main`; in a fork, pass
  `--base upstream/main` — and the tests, `python3 -m unittest discover -s
  tests`. Run the changed command or skill once in a real repository, and
  say in the pull request where and how. To try a plugin straight from a checkout, without installing:
  `claude --plugin-dir <checkout>/plugins`.

The conventions — commit format, command naming, descriptions — are in
[`AGENTS.md`](AGENTS.md) §3, the checks in §4 and the layout in §5; the model
behind the plugins is in [`docs/design.md`](docs/design.md).
