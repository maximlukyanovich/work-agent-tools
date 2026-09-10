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
/plugin install project-bootstrap estimation jira-workflow
```

The repository is private, so ordinary git access is required — the same SSH key
or token you clone work projects with. Nothing extra to hand out.

Updating the method everywhere at once:

```bash
/plugin marketplace update mluk-work-agent-tools
```

Plugins install separately: `/plugin install estimation` does not pull Jira in.

## Where to start

Every plugin can introduce itself:

```bash
/work-tools-boot-help          what project-bootstrap can do
/work-tools-jira-help          what jira-workflow can do
/work-tools-est-help  ru       what estimation can do, in Russian
```

Each prints the plugin's surface: its commands with a line on each, the order
they are normally applied in, the skills it carries, and what it expects from the
project. Read-only, safe to run at any time.

Language follows the conversation; pass a language code to override.

## Plugins

| Plugin | What it does |
| --- | --- |
| `project-bootstrap` | Initialise or audit a repository's agent harness: `AGENTS.md`, skills, commands, hooks, MCP, docs. Stack-agnostic. |
| `estimation` | Estimate a project from a spec and a design handoff: decomposition, provenance audit, a markdown report and the company estimate workbook. |
| `jira-workflow` | Run Jira work the way the company standard requires: hierarchy, description shape, statuses, comments, worklog. |

## Two kinds of plugin

A plugin is either a generator or a library, and the choice is deliberate.

**A generator** runs once and writes files into the project. What it produces
becomes the project's own code: edited locally, never updated from here.
`project-bootstrap` is a generator — `AGENTS.md`, domain skills and hooks are
about one repository and have no shared version to track.

**A library** keeps its commands and skills here and is invoked from any project.
The project contributes only a profile that steers them. `jira-workflow` and
`estimation` are libraries — the method is identical everywhere, and the
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
differs, not just its parameters. One project has `/prepare-pr-texts`, another has
`/promote` and `/sync` — different processes around GitLab, too early to unify.
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

Every command starts with `work-tools-`, the marketplace's name, then the
plugin's area:

| Plugin | Commands |
| --- | --- |
| `project-bootstrap` | `/work-tools-boot-setup`, `/work-tools-boot-audit`, `/work-tools-boot-help` |
| `jira-workflow` | `/work-tools-jira-plan`, `/work-tools-jira-create`, `/work-tools-jira-questions`, `/work-tools-jira-status`, `/work-tools-jira-comment`, `/work-tools-jira-help` |
| `estimation` | `/work-tools-est-project`, `/work-tools-est-update`, `/work-tools-est-export`, `/work-tools-est-help` |

Two levels of filtering come out of it: `work-tools` lists everything shipped
from here, `work-tools-jira` narrows to one plugin. The length costs nothing —
completion fills it in — and it buys an unmistakable signal that the command is
shared and is changed by a merge here, not by editing a file in the project.

**A separator, not a colon.** `work-tools:jira-create.md` cannot exist on
Windows, git refuses to check it out there, and not one of the several hundred
commands across the installed marketplaces uses a colon in a filename. Claude
Code also appears to reserve the colon for its own plugin namespace, as in
`figma:figma-use`.

Two rules follow.

**A plugin command never takes a name a project is likely to use.** With this
prefix a collision is nearly impossible, but the rule still holds for what the
command *does*: `/task`, `/commit`, `/promote`, `/sync`, `/start` are procedures
that differ between repositories and belong to them. Only the shareable half
moves here.

**The prefix is fixed once.** Renaming it breaks muscle memory and every document
that quotes a command. If a plugin's subject drifts far enough that its area no
longer fits, that is a new plugin.

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
