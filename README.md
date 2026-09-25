# agent-tools

Shared Claude Code tooling for team projects. One repository: it is both the
marketplace and the home of the plugins.

Why it exists: the method must not live as copies in every repository. Estimation
rules, the shape of a Jira issue and the order of project bootstrap are the same
everywhere; only keys, rates and the domain differ, and those stay in the project.

## Installing

Once per machine:

```bash
/plugin marketplace add https://github.com/maximlukyanovich/work-agent-tools.git
/plugin install work-bootstrap@mluk-work-agent-tools work-jira@mluk-work-agent-tools work-estimation@mluk-work-agent-tools
```

The repository is private, so ordinary git access is required — the same SSH key
or token you clone work projects with. Nothing extra to hand out.

Updating the method everywhere at once:

```bash
/plugin marketplace update mluk-work-agent-tools
```

Plugins install separately: `/plugin install work-estimation@mluk-work-agent-tools`
does not pull Jira in.

The `@mluk-work-agent-tools` suffix names the catalogue. The short form works while
the plugin name is unique across every catalogue on the machine; the full form
works always, so it is the one written here.

## Where to start

Every plugin can introduce itself:

```bash
/work-bootstrap:help          what it can do for a repository's harness
/work-jira:help               what it can do with issues
/work-estimation:help  ru     what it can do with estimates, in Russian
```

Each prints the plugin's surface: its commands with a line on each, the order
they are normally applied in, the skills it carries, and what it expects from the
project. Read-only, safe to run at any time.

Language follows the conversation; pass a language code to override.

## Plugins

| Plugin | What it does |
| --- | --- |
| `work-bootstrap` | Initialise or audit a repository's agent harness: `AGENTS.md`, skills, commands, hooks, MCP, docs. Stack-agnostic. |
| `work-estimation` | Estimate a project from a spec and a design handoff: decomposition, provenance audit, a markdown report and the company estimate workbook. |
| `work-jira` | Run Jira work the way the company standard requires: hierarchy, description shape, statuses, comments, worklog. |

## Two kinds of plugin

A plugin is either a generator or a library, and the choice is deliberate.

**A generator** runs once and writes files into the project. What it produces
becomes the project's own code: edited locally, never updated from here.
`work-bootstrap` is a generator — `AGENTS.md`, domain skills and hooks are
about one repository and have no shared version to track.

**A library** keeps its commands and skills here and is invoked from any project.
The project contributes only a profile that steers them. `work-jira` and
`work-estimation` are libraries — the method is identical everywhere, and the
differences (tracker key, language, prefixes, which description sections apply)
are data, not code.

| | Generator | Library |
| --- | --- | --- |
| Appears in the project | `AGENTS.md`, domain skills, hooks, the profile | profile lines only |
| Commands come from | the project | the plugin |
| Updating the method | not updated; it is project code now | `/plugin marketplace update` |

The reason to prefer a library wherever possible: five projects using a generator
means five copies of a skill, and a fix to a Jira quirk has to be made five
times. That is the exact failure this repository exists to prevent.

**When a command still belongs to the project:** when the procedure itself
differs, not just its parameters. One project has `/prepare-pr-texts`, another
has `/promote` and `/sync` — different processes around GitLab, too early to unify.
Such commands stay local and coexist with the plugin's.

The test: if the difference fits in a profile line, it is a library. If the
procedure differs, it is a local command.

## Method here, project there

**Here — the method.** How to estimate, which sections an issue description
carries, how to work around the Jira editor's quirks, templates for `AGENTS.md`
and skills, wrappers over the APIs.

**In the project — the profile and the domain.** Tracker key, hourly rates,
coefficients, links to the spec and the design, domain skills (design system,
layer boundaries, localisation), hooks.

The rule of thumb: if a rule survives a change of project, it belongs here. If it
names concrete paths, keys or a design system, it belongs to the project.

### Precedence

Every skill in this repository reads the project profile before it does anything,
and treats it as authoritative. Order, strongest first:

1. What the developer says in the current session.
2. The project profile — `.claude/project-profile.md`.
3. The project's own `AGENTS.md` and skills.
4. The defaults in this repository.

A plugin never dictates the language of issue descriptions, the naming of
branches or the shape of a summary. It supplies a recommended default, reads the
profile, and asks when the profile is silent. A project that deviates from the
company standard — with a reason — records the deviation in its profile, and the
plugin follows it.

## Command naming

Claude Code prefixes a plugin's commands with the plugin name and a colon by
itself — `/figma:figma-use`, and so `/work-jira:create` here. So the prefix lives
in the **plugin name**, and the command name stays short.

| Plugin | Commands |
| --- | --- |
| `work-bootstrap` | `/work-bootstrap:setup`, `:audit`, `:help` |
| `work-jira` | `/work-jira:plan`, `:create`, `:questions`, `:status`, `:comment`, `:help` |
| `work-estimation` | `/work-estimation:project`, `:update`, `:export`, `:help` |

Two levels of filtering fall out of it: typing `work` lists everything shipped
from here, `work-jira` narrows to one plugin. Nothing is repeated — the area is
in the plugin, the verb is in the command.

**Never put a colon in a filename.** The separator is the harness's; a file named
`plan:create.md` cannot be checked out on Windows. And never repeat the plugin
name inside the command name: `/work-jira:jira-create` is what that produces.

Two rules follow.

**A plugin command never takes over a job the project owns.** `/task`,
`/commit`, `/promote`, `/sync`, `/start` are procedures that differ between
repositories and stay there; only the shareable half moves here. The namespace
prevents the name clash, but not the confusion of two commands doing the same
job.

**Plugin names are fixed once.** Renaming one changes every command it ships and
every document quoting them. If a plugin's subject drifts far enough that its
name no longer fits, that is a new plugin.

## Layout

```
.claude-plugin/marketplace.json   the catalogue: lists the plugins below
plugins/<name>/
  .claude-plugin/plugin.json      plugin manifest
  commands/*.md                   slash commands — procedures a human invokes
  skills/<name>/SKILL.md          knowledge the agent loads by itself
  scripts/                        executable parts: generators, API wrappers
  reference/                      material read one file at a time, not whole
  README.md                       what the plugin does
```

Descriptions surface from three places, and all three matter: the plugin's entry
in `marketplace.json` is the shop window in `/plugin`; a command's frontmatter
`description` is what slash-command completion shows; a skill's `description` is
what the agent uses to decide whether to load it. README files are read by people
on the web — no tool renders them.

## How this grows

The method comes out of real work. A rule earned on a live project lands here as
a merge — otherwise three projects from now we have three diverging copies again,
only this time in notes. Candidates accumulate under `docs/local/` in the working
repositories.
