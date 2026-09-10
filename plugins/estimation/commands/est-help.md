---
description: What estimation can do — commands, the method it applies, and the data format it expects.
argument-hint: '[<language code>]'
---

# /est-help

Introduce this plugin. **Read-only.**

Language: the conversation's, unless `$1` gives a code.

## Steps

1. **List the commands from their frontmatter** — `description` and
   `argument-hint` out of every `commands/*.md` here. Never typed by hand.

2. **Show the order:** `/est-project` produces an estimate, `/est-update`
   recomputes it after the scope changes, `/est-export` carries it into the
   company workbook.

3. **State the method in five lines**: two rates of work, counting bottom-up
   without looking at the deadline, the provenance audit, coefficients as their
   own rows, whole hours rounded up. Point at `skills/method/SKILL.md` for the
   rest.

4. **Name what it expects**: a data module in the format of
   `reference/data-format.md`, and for export a copy of the company workbook
   template.

5. **Say what is present here** — is there an estimate module, is there a
   template. One line each.
