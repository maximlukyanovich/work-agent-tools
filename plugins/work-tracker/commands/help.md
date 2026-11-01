---
description: What work-tracker can do — commands, the order they are applied in, and the conventions it carries.
argument-hint: '[<language code>]'
disable-model-invocation: true
---

# /work-tracker:help

Introduce this plugin. **Read-only**, changes nothing, safe at any time.

Language: the conversation's, unless `$1` gives a code (`ru`, `en`, …). Not the
profile's issue language — that is a different setting.

## Steps

1. **List the commands from their own frontmatter.** Read `description` and
   `argument-hint` out of every `commands/*.md` in this plugin. Never type the
   list by hand: a hand-kept copy goes stale within weeks.

2. **Show the usual order**, since it does not follow from the names:

   ```
   /work-tracker:plan       propose the tree, get it approved
   /work-tracker:create     create it
   /work-tracker:next       pick what to take next — unblocked, by what it unblocks
   /work-tracker:questions  collect what is still unclear on an issue
   /work-tracker:status     check whether an issue is really done
   /work-tracker:comment    post the result comment, ask for the status, offer a worklog
   /work-tracker:check-actuals  once work is under way: hours logged against the estimate
   ```

3. **Name the conventions it carries**, in two or three lines each: hierarchy
   from the standard, the four required description sections, estimate
   basis, labels taken from the instance, descriptions in the tracker's own
   format through its adapter, other issues as cards and linked `relates to`; every question for someone
   outside the team checked against its sources as soon as it is drafted.

4. **Say what it expects from the project**: a profile with `## Tracker` and
   `## Issues`, and access to the tracker as its adapter names it — Jira's
   ships here and is the recommended one. State which of the two are present here
   — one line each, no diagnostics beyond that.

5. **Point at the skill** for the full rules: `${CLAUDE_PLUGIN_ROOT}/skills/issues/SKILL.md`.

## Hard rules

- **Never search the filesystem for the plugin.** Its files are at
  `${CLAUDE_PLUGIN_ROOT}` — use that path verbatim. A `find` over the disk is the
  failure this rule exists to prevent.
- Read-only. No file is written, no API call changes anything.
- The command list comes from frontmatter, not from memory.
- Keep it short: this is an introduction, not the manual.
