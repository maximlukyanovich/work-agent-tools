# Templates — The onboarding command

### The onboarding command

The project's start command is the first a newcomer runs, often in a clone
where nothing is installed yet. Committed `enabledPlugins` turns a plugin on
in every clone but downloads nothing, and trusting the folder only registers
the marketplaces the settings declare — so the settings declare every
marketplace `enabledPlugins` names: `mluk-work-agent-tools` from GitHub with
`autoUpdate`, so every raised plugin version reaches every clone on its own,
and `claude-plugins-official` when its plugins are on (an interactive first
start adds that one on its own, a profile used only from the CLI lacks it):

```json
"extraKnownMarketplaces": {
  "mluk-work-agent-tools": {
    "source": { "source": "github", "repo": "maximlukyanovich/work-agent-tools" },
    "autoUpdate": true
  }
}
```

When Q10 pinned a release, `source` also carries `"ref": "<tag>"` beside
`repo`: every clone stays on that tag, and moving to the next one is a
settings change that the next session start applies — on a machine whose
user settings do not declare `mluk-work-agent-tools` too, since a
declaration there wins over the project's.

The command then:

- **Installs what this checkout lacks.** It reads `enabledPlugins` and one
  `claude plugin list --json`, cut to `id`, `scope`, `enabled`,
  `projectPath`, `installPath` before it is read. An install counts when its
  scope is `user` or `managed`, or its `projectPath` is this checkout or
  another checkout of the same repository — the same
  `git rev-parse --path-format=absolute --git-common-dir`. A declared plugin
  with no install that counts is missing; one whose installs all have
  `enabled: false` is turned off here — a personal switch, left alone. The
  missing ones are installed on a yes with `--scope local` — the settings
  already turn them on, and a project-scope install writes into the
  committed `settings.json` — then `/reload-plugins` and the start command
  again, each as a code block. A plugin whose marketplace this machine does
  not know (`claude plugin marketplace list --json`) is not installed: a
  declared marketplace is registered by starting Claude Code at the
  repository root and trusting the folder, an undeclared one goes under
  `extraKnownMarketplaces` first. Neither needs
  `claude plugin marketplace add`, and at two scopes it does harm:
  `--scope local` replaces the committed entry, its `autoUpdate` and `ref`
  included,
  `--scope project` rewrites the committed `settings.json`.
- **Prints how to run the project** — the commands of `AGENTS.md` §2,
  verbatim, as code blocks ready to paste, from the repository root.
- **Lists the commands from their files** — the project's from
  `.claude/COMMANDS.md`, each enabled plugin's from the `description` line
  of `<installPath>/commands/*.md`: a command with
  `disable-model-invocation`, such as `help`, is missing from the session's
  own list.
