# Design

How the work is split between the plugins and the projects that use them.
Installing and using them is in the [README](../README.md).

## Two kinds of plugin

A plugin is either a generator or a library, and the choice is deliberate.

**A generator** runs once and writes files into the project. What it produces
becomes the project's own code: edited locally, never overwritten from here.
`work-bootstrap` is a generator — `AGENTS.md`, domain skills and hooks are
about one repository and have no shared version to track. What does evolve
is the **method** behind them, and a change a project should carry over is
an entry in `plugins/work-bootstrap/CHANGES.md`: the project records the last
entry it applied as its baseline, a `SessionStart` hook says when it is
behind, and `/work-bootstrap:audit` checks only the entries after it.

**A library** keeps its commands and skills here and is invoked from any project.
The project contributes only a profile that steers them. `work-jira` and
`work-estimation` are libraries — the method is identical everywhere, and the
differences (tracker key, language, prefixes, which description sections apply)
are data, not code.

| | Generator | Library |
| --- | --- | --- |
| Appears in the project | `AGENTS.md`, domain skills, hooks, the profile | profile lines only |
| Commands come from | the project | the plugin |
| Updating the method | not updated; it is project code now | a raised version, through `autoUpdate` or `claude plugin update` |

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
plugin's standard — with a reason — records the deviation in its profile, and the
plugin follows it.

## Command naming

Claude Code prefixes a plugin's commands with the plugin name and a colon by
itself — `/figma:figma-use`, and so `/work-jira:create` here. So the prefix lives
in the **plugin name**, and the command name stays short.

| Plugin | Commands |
| --- | --- |
| `work-bootstrap` | `/work-bootstrap:new`, `:setup`, `:audit`, `:handoff`, `:help` |
| `work-jira` | `/work-jira:plan`, `:create`, `:questions`, `:status`, `:comment`, `:next`, `:help` |
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

## How this grows

The method comes out of real work. A rule earned on a live project lands here as
a merge — otherwise three projects from now we have three diverging copies again,
only this time in notes. Candidates accumulate under `docs/local/` in the working
repositories.
