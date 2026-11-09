# Updates

Where a plugin is recorded, how a new version reaches a project, how releases
are cut, and how a project pins one.

The once-per-machine `claude plugin marketplace add` declares the marketplace
in your user settings — skip it on a machine that works in a project pinned to
a release, see [Pinning a release](#pinning-a-release).

`--scope project` records a plugin in `.claude/settings.json`, which is
committed, so the team runs the same tooling; a teammate's clone runs the same
`claude plugin install` once, and the file does not change. `--scope local`
writes the gitignored `.claude/settings.local.json` instead, for a project
whose rules keep AI settings out of git. `--scope user` works too, at a price:
the plugins' descriptions join every session on the machine, in unrelated
projects as well.

## Versions and updates

Every plugin carries a `version` in its `plugin.json`, and `claude plugin list`
shows the one you have. A major means your project must act, a minor brings a
new rule, command or template section, a patch rewords or fixes; the rule is
in [`AGENTS.md`](../AGENTS.md) §2.

An installed plugin is a copy in `~/.claude/plugins/cache/`, replaced only when
the plugin's version changes. A project set up by `setup` declares the
marketplace with `autoUpdate` and follows `main`: every raised version arrives
by itself, up to ten minutes after an interactive session's first message, and
`/reload-plugins` applies it to an open session. Without that declaration,
turn it on in `/plugin` → **Marketplaces** → `mluk-work-agent-tools` →
**Enable auto-update**. The repository is public, so the background check
needs no credential. By hand:

```bash
claude plugin marketplace update mluk-work-agent-tools
claude plugin update work-tracker@mluk-work-agent-tools --scope project   # each installed plugin at its scope, then /reload-plugins
```

Updating delivers the method; it never edits a project. When a set-up project
falls behind, `work-bootstrap`'s session-start hook says so and
`/work-bootstrap:audit` proposes the edits.

### Releases

Each merged batch is released: an annotated tag `vYYYY.MM.DD` on `main` — the
merge's date, `.2` for a second batch that day — and a GitHub
[release](https://github.com/maximlukyanovich/work-agent-tools/releases) whose
notes list every plugin's version against the previous release, then what a
project must do — a major, a removed plugin, the `CHANGES.md` entries
`/work-bootstrap:audit` applies — then the merged pull requests. The date says
which release you run; a plugin's version says whether you must act. A released
tag is never moved.

### Pinning a release

A project that follows `main` gets every raised version as it lands. A team
that moves between releases deliberately pins a tag instead — `ref` inside
`source`, `autoUpdate` kept:

```json
"extraKnownMarketplaces": {
  "mluk-work-agent-tools": {
    "source": { "source": "github", "repo": "maximlukyanovich/work-agent-tools", "ref": "vYYYY.MM.DD" },
    "autoUpdate": true
  }
}
```

The latest tag is the first line of
`git ls-remote --tags --refs --sort=-v:refname https://github.com/maximlukyanovich/work-agent-tools 'v*'`.
`setup` asks whether a project follows `main` or pins a release, and writes
the latest tag itself.

A pin holds on a machine under two conditions:

- **The user settings do not declare the marketplace.** The once-per-machine
  `claude plugin marketplace add` writes it into `~/.claude/settings.json`
  without `ref`. The project's declaration wins the merge, but Claude Code
  2.1.319 refuses a source that differs from the user settings' entry: a
  session in the pinned project either registers no marketplace at all or
  keeps the clone already registered from `main` and installs the plugins
  from it. Skip the add on a machine that works in a pinned project — trusting
  the folder registers the marketplace from the project's settings — or delete
  the `mluk-work-agent-tools` entry under `extraKnownMarketplaces` in
  `~/.claude/settings.json`; a project set up by `setup` declares it in its own
  settings.
- **The plugins update in the project's own session.** The catalogue is one
  clone per machine, and a session in another project fetches it from that
  project's source. A session start in the pinned project fetches its tag
  back, and `autoUpdate` then works from it; `claude plugin update` takes the
  clone as the machine's last session left it, so after a session elsewhere it
  moves the pinned project to that source.

Moving to the next tag:

1. A pull request in the project changes `ref`; its reviewer reads the
   releases between the two tags.
2. After the merge, each developer starts an interactive session at the
   repository root: the session fetches the catalogue from the new tag.
3. The plugins follow through `autoUpdate`, up to ten minutes after that
   session's first message, and `/reload-plugins` applies them. To move at
   once, run `claude plugin update <plugin>@mluk-work-agent-tools --scope <scope>`
   for each installed plugin right after that start, before a session in
   another project.
4. When the releases list `CHANGES.md` entries, `work-bootstrap`'s
   session-start hook says the project is behind: `/work-bootstrap:audit`.

Rolling back is the same move to an older tag; going back to `main` is
removing `ref`. Two commands look right and do not do it:
`claude plugin marketplace update` does not see a changed `ref` — only a
session start does — and `claude plugin marketplace add` replaces the declared
source, its `ref` included.
