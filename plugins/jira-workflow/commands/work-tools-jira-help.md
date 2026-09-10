---
description: What jira-workflow can do — commands, the order they are applied in, and the conventions it carries.
argument-hint: '[<language code>]'
---

# /work-tools-jira-help

Introduce this plugin. **Read-only**, changes nothing, safe at any time.

Language: the conversation's, unless `$1` gives a code (`ru`, `en`, …). Not the
profile's issue language — that is a different setting.

## Steps

1. **List the commands from their own frontmatter.** Read `description` and
   `argument-hint` out of every `commands/*.md` in this plugin. Never type the
   list by hand: a hand-kept copy goes stale within weeks.

2. **Show the usual order**, since it does not follow from the names:

   ```
   /work-tools-jira-plan      propose the tree, get it approved
   /work-tools-jira-create    create it
   /work-tools-jira-questions collect what is still unclear on an issue
   /work-tools-jira-status    check whether an issue is really done
   /work-tools-jira-comment   post the result comment, offer a worklog
   ```

3. **Name the conventions it carries**, in two or three lines each: hierarchy
   from the company standard, the four required description sections, estimate
   basis, labels taken from the instance, descriptions written as ADF.

4. **Say what it expects from the project**: a profile with `## Tracker` and
   `## Issues`, and tracker credentials. State which of the two are present here
   — one line each, no diagnostics beyond that.

5. **Point at the skill** for the full rules: `skills/issues/SKILL.md`.

## Hard rules

- Read-only. No file is written, no API call changes anything.
- The command list comes from frontmatter, not from memory.
- Keep it short: this is an introduction, not the manual.
