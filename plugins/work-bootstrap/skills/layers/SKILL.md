---
name: layers
description: The five layers an instruction can live on — deterministic checks, agent hooks, documents, skills, commands — how to choose between them, what each costs, and the anti-patterns that make a harness expensive. Use when setting up or auditing an agent harness, or deciding which layer a new rule belongs on. Not for ordinary edits to AGENTS.md.
---

# Five layers

Layers differ by **who runs them** and **what they cost**. That is the only
criterion for choosing: a rule lives on the cheapest layer that can catch it.

| Layer | Who runs it | When | What goes here | Cost |
| --- | --- | --- | --- | --- |
| Deterministic checks — linter, formatter, type-check, tests, git hooks | the tool, git | on command and on commit | anything expressible as a lint rule, a schema, a type or a test | zero context |
| Agent hooks | the harness, automatically | right after a file is written | machine-checkable invariants the linter cannot express, or expresses too late | ~0 tokens on a clean pass |
| Documents — `AGENTS.md`, `CLAUDE.md` | loaded every session | always | canonical project rules: architecture, conventions, agreements | paid every session |
| Skills | the agent, on context match | when the task falls in the skill's area | rules that need understanding: how to decompose a component, how to record provenance | paid only when loaded |
| Commands | a human, explicitly | on invocation | step-by-step procedures with confirmation points | paid on invocation |

**Duplication across layers is sometimes deliberate.** A hook catches a violation
a second after the file is written, the linter at `validate`, review before the
merge request — different costs of the same error, not redundancy. **Duplication
within a layer is always a bug:** copies drift, and it stops being clear which
one is true.

## Why hooks and commands exist at all when the rules are written down

An agent decides for itself when to clarify and when to act from memory, and with
a firm spec in hand that instinct to "not bother the user" reliably makes the
result worse. The mechanical layer takes the decision away: a hook fires every
time, a command runs a fixed procedure with confirmation points. A rule written
only as prose is obeyed probabilistically.

## Keeping it cheap

The harness is paid for by every session.

- **Zero duplication.** A rule exists in one place; other files link to it in one
  line.
- **Do not load what is not needed.** Precise skill descriptions: a vague one
  either never loads or loads always.
- **Mechanics to the mechanical layer.** Anything a linter, a type or a test can
  catch is caught there, at zero context cost.
- **Silent hooks.** A hook outside its area exits without a word. An ordinary
  edit should produce no feedback at all.
- **Read-only by default** for commands: fewer mutations, fewer confirmation
  cycles.
- **Short documents.** Documentation surface is paid forever and dilutes the
  signal. Walk `AGENTS.md` periodically and delete what the linter now expresses.
- **Periodic cleanup.** A command nobody invokes, a skill that never loads, a
  hook with steady false positives — deleted.

## Anti-patterns

- **The same rule in several files.** Copies diverge; the agent gets
  contradictory instructions and picks one at random.
- **Writing into an instruction what a linter catches.** Expensive, unreliable,
  and it competes with the real signal.
- **Empty placeholder directories and stub READMEs.** An agent cannot tell "TODO"
  from "real but empty" and starts building on what does not exist.
- **Vague skill descriptions.** The skill either never loads or always does.
- **Compiling a vendor into the structure.** Tracker, design tool, git platform
  are abstractions; concrete names appear only in the files tied to the answer
  about them.
- **Copying examples with someone else's domain in them.** Examples in a skill
  are written for this project's domain.
- **Deferring deprecation warnings.** Migrate in the same commit the warning
  appeared in.
- **`git add -A` on a repository with history.** Risk of committing local files.
  Paths are listed explicitly.
- **Bypassing a hook with `--no-verify`.** A broken hook is fixed, not skipped.
- **Leaving a generator's boilerplate.** The agent reads it as a working example
  and reproduces it.
- **Adding a hook, command or skill "just in case".** Each artefact costs
  maintenance. The reason to add one is a confirmed, repeated pain — not a
  hypothesis.
