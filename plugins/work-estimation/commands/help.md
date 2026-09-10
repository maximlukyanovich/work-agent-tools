---
description: What work-estimation can do — commands, the method it applies, and the data format it expects.
argument-hint: '[<language code>]'
---

# /work-estimation:help

Introduce this plugin. **Read-only.**

Language: the conversation's, unless `$1` gives a code.

## Steps

1. **List the commands from their frontmatter.** Read `description` and
   `argument-hint` out of every file in `${CLAUDE_PLUGIN_ROOT}/commands/`.
   Use that path verbatim — never search the filesystem for the plugin.

2. **Show the order:** `/work-estimation:project` produces an estimate, `/work-estimation:update`
   recomputes it after the scope changes, `/work-estimation:export` carries it into the
   company workbook.

3. **State the method in five lines**: two rates of work, counting bottom-up
   without looking at the deadline, the provenance audit, coefficients as their
   own rows, whole hours rounded up. Point at `${CLAUDE_PLUGIN_ROOT}/skills/method/SKILL.md` for the
   rest.

4. **Name what it expects**: a data module in the format of
   `${CLAUDE_PLUGIN_ROOT}/reference/data-format.md`, and for export a copy of the company workbook
   template.

5. **Say what is present here** — is there an estimate module, is there a
   template. One line each.

## Hard rules

- **Never search the filesystem for the plugin.** Its files are at
  `${CLAUDE_PLUGIN_ROOT}` — use that path verbatim. A `find` over the disk is the
  failure this rule exists to prevent.
- Read-only. No file is written, no API call changes anything.
- The command list comes from frontmatter, not from memory.
- Keep it short: this is an introduction, not the manual.
