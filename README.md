# work-agent-tools

Claude Code plugins for a software project run by a team through a tracker:
setting up the agent harness with the project's own workflow commands, Jira work
to one standard, and estimates from a spec and a design. One author's toolkit,
grown on commercial projects and open to anyone — the rules are opinionated,
and each project tunes them through its own profile.

One repository: it is both the marketplace (`mluk-work-agent-tools`) and the
home of the plugins.

Why it exists: the method must not live as copies in every repository. Estimation
rules, the shape of a Jira issue and the order of project bootstrap are the same
everywhere; only keys, rates and the domain differ, and those stay in the project.

## Does it fit your project

Each plugin is enabled on its own, so a project takes only what fits.

- `work-bootstrap` — any repository, any stack: frontend, backend, monorepo,
  library, CLI. It writes the harness into the project, including workflow
  commands shaped to its branch chain, its forge (GitHub, or GitLab including
  self-hosted) and its tracker, and keeps it current with the method.
- `work-jira` — work tracked in Jira Cloud: issues created to one standard,
  statuses, comments, worklog.
- `work-estimation` — a project estimated before it starts, from a spec and a
  design handoff.

A solo project on GitHub without a tracker fits
[agent-tools](https://github.com/maximlukyanovich/agent-tools) better: there the
workflow commands ship in a plugin instead of being written into the project.

## Requirements

- Claude Code; 2.1.292 or later for the one-line start from scratch.
- `git`, and `gh` or `glab` signed in for the steps that open a pull or merge
  request.
- Python 3 — the plugins' scripts and the `work-bootstrap` session-start hook.
- For `work-jira`: a Jira Cloud site and a working `.mcp.json` with its
  credentials; without one the commands stop and say what is missing.
- For `/work-estimation:export`: the `.xlsx` workbook template to fill.

## Quick start

Once per machine — it adds the source and loads nothing into sessions:

```bash
claude plugin marketplace add maximlukyanovich/work-agent-tools
```

In an existing repository — install, then run `setup`:

```bash
claude plugin install work-bootstrap@mluk-work-agent-tools --scope project
claude "/work-bootstrap:setup"
```

`setup` looks at the code, asks only what the code cannot answer — including
which other plugins the project uses — shows a plan and, once you approve it,
writes the harness: `AGENTS.md`, the project profile, the workflow commands, and
the plugins in `.claude/settings.json`.

`--scope project` records a plugin in `.claude/settings.json`, which is
committed, so the team runs the same tooling; a teammate's clone runs the same
command once, and the file does not change. `--scope local` writes the
gitignored `.claude/settings.local.json` instead, for a project whose rules keep
AI settings out of git. `--scope user` works too, at a price: the plugins'
descriptions join every session on the machine, in unrelated projects as well.

From scratch, in an empty folder — `--marketplace` adds the marketplace when it
is not there yet:

```bash
mkdir my-app && cd my-app
claude plugin install work-bootstrap --marketplace maximlukyanovich/work-agent-tools --scope project && claude "/work-bootstrap:new"
```

`new` asks the stack, runs its generator, pins the versions, and makes the first
commit and the remote on your yes; `setup` follows in a fresh session.

Which plugins to enable:

| Project | Plugins |
| --- | --- |
| any repository | `work-bootstrap` |
| issues in Jira | + `work-jira` |
| estimated before it starts | + `work-estimation` |

An installed plugin is a copy in `~/.claude/plugins/cache/`. A project set up
by `setup` declares the marketplace with `autoUpdate`, so a new version arrives
by itself: the plugins carry no `version`, so every commit on `main` reaches
you, up to ten minutes after an interactive session's first message, and
`/reload-plugins` applies it to an open session. Without that declaration,
turn it on in `/plugin` → **Marketplaces** → `mluk-work-agent-tools` →
**Enable auto-update**. The repository is public, so the background check
needs no credential. By hand:

```bash
claude plugin marketplace update mluk-work-agent-tools
claude plugin update work-jira@mluk-work-agent-tools --scope project   # each installed plugin at its scope, then /reload-plugins
```

Updating delivers the method; it never edits a project. When a set-up project
falls behind, `work-bootstrap`'s session-start hook says so and
`/work-bootstrap:audit` proposes the edits.

## Where to start

Every plugin can introduce itself — read-only, safe to run at any time:

```bash
/work-bootstrap:help          what it can do for a repository's harness
/work-jira:help               what it can do with issues
/work-estimation:help  ru     what it can do with estimates, in Russian
```

Language follows the conversation; pass a language code to override. The help
commands are hidden from the model (`disable-model-invocation`), so they cost
no context until typed.

## Everyday use

The workflow commands are the project's own — `setup` writes them, and their
names and steps differ between repositories; the plugins supply the shared
half. A task in a Jira project typically runs in phases, each in a fresh
session:

```bash
/work-jira:next          what to take next from the board
/task PROJ-12            the project's command: branch, plan, open questions; no code before your yes
/commit                  the project's command: stage, check what changed, message by its convention
/code-review             the project's command: findings by severity, each with file:line
/promote                 the project's command: merge along the branch chain, then the result comment and the worklog
```

Every command ends with the next step as a block ready to copy;
`/work-bootstrap:handoff` prints it at a phase boundary. An estimate starts with
`/work-estimation:project`, with the spec and the design handoff at hand.

## Plugins

| Plugin | Kind | What it does |
| --- | --- | --- |
| [`work-bootstrap`](plugins/work-bootstrap/README.md) | generator + audit | Start a project in an empty folder; initialise or audit a repository's agent harness: `AGENTS.md`, the project profile, workflow commands, skills, hooks, MCP, docs. A session-start hook says when a set-up project is behind the method. |
| [`work-jira`](plugins/work-jira/README.md) | library | Jira work to one standard: `plan`, `create`, `questions`, `status`, `comment`, `next` — hierarchy, description shape, statuses, comments, worklog. Reads the project profile. |
| [`work-estimation`](plugins/work-estimation/README.md) | library | Estimate a project from a spec and a design handoff: `project`, `update`, `export` — decomposition, provenance audit, a markdown report and the estimate workbook. |

## How it's built

`work-bootstrap` generates: what `setup` writes, the workflow commands included,
becomes the project's own code, and a method change reaches it as an entry in
[`CHANGES.md`](plugins/work-bootstrap/CHANGES.md) that `audit` applies.
`work-jira` and `work-estimation` are libraries: the procedure stays here, and
the project contributes a profile, `.claude/project-profile.md`, that every
command reads first. The model — generator versus library, what lives here and
what in the project, precedence, command naming — is in
[`docs/design.md`](docs/design.md).

## Contributing

Issues and pull requests are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[MIT](LICENSE).
