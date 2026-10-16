---
name: method
description: How to estimate a project from a spec and a design handoff — two rates of work, counting bottom-up, the provenance audit, coefficients and rounding. Use when producing, revising or reviewing a project estimate. Not for setting a single issue's estimate field — that is the issues skill.
---

# Estimation method

## The rule that matters most

**Count bottom-up and do not look at the deadline until the count is finished.**

An estimate calibrated against a number someone named is not an estimate. It gets
nudged silently, and the nudge lands on the largest lines because they have the
most room. On the project this method came from, the first pass was tuned to a
named total and understated the domain-components line by a factor of three —
thirty-five components for six hours. It survived review only because the
developer knew the number was wrong.

Compare with the deadline **after** the total exists. If they disagree, that is a
scope conversation, not an arithmetic one.

## Two rates of work

Not one coefficient over everything. Work splits into two kinds that cost
differently:

**Routine.** Porting a component or a screen that already exists as working code
in the design handoff, a form, a CRUD section, a static block. The work is
posing the task to an agent and checking the result in a browser.

**Decisions and sensitive logic.** Money — a cart, a total cost, a payment
confirmation. Realtime and streaming. A schema the AI produces at runtime.
Caching policy where showing a stale price costs real trust. Here you pay for a
developer who makes the calls and walks the edge cases. Whole large screens land
here too.

The band for each is a project setting; the profile records it. What is universal
is that the two exist and are told apart before a number is written.

Verification in a browser and the fixes that follow are **inside** the task's
hours, not a separate line.

## The provenance audit

Every line is classified by where it came from. Four groups:

| Group | Meaning |
| --- | --- |
| Confirmed | named in the spec **and** drawn in the design |
| Thin | one or two sentences in the spec, no mockup |
| Design-only | taken from the design, absent from the spec |
| Ours | in neither: foundation, infrastructure, cross-cutting work |

The report states the size of each group. The number that changes conversations
is groups two and three together: work the client either never described or
described in a sentence. On the project this came from it was 40% of the
estimate — and knowing that before signing is worth more than any single line.

An estimate without this audit looks equally confident everywhere, which is a lie.

## Coefficients

Overheads — responsive layout, localisation, automated tests — are **their own
rows**, not a multiplier hidden inside task hours. Then each can be discussed,
cut, or moved to a separate stream without touching anything else.

Rules:

- Whole hours. Round up. An estimate with halves invites arguments about halves.
- Tests are computed after the other overheads, on the sum, because tests cover
  them too.
- The rate for each is a project setting.

## Shape of the result

**Rows** carry: part of the project, epic, task, description, optimistic hours,
pessimistic hours, negative risk, positive risk. That is the shape of the
estimate workbook, and the markdown report keeps the same columns so the transfer
is mechanical.

**Epics are product surfaces**, not functional layers, unless the project says
otherwise. Then "where is screen X in this estimate?" has one answer.

**Risks are filled only where they change the number.** A risk on every row is
noise. A negative risk names the fork that would make the line more expensive; a
positive one names the condition under which the line disappears entirely —
including "we can drop this module", which is the cheapest kind of good news.

**Descriptions are written for the client**, not for the developer: what will
exist when this line is done, in plain language.

## Narrowing the scope

A reduced scope is a **filter over the full set**, never a hand-made copy. The
full estimate stays as the upper bound; the filter names which lines survive and
recomputes the coefficients from the new sum. Per-task hours do not change when
the scope narrows — only the composition does.

The same holds for the reverse: a line returning to scope brings its original
hours with it.

## When the design changes

The bundle version is checked against its source before the numbers are quoted,
not after. A local copy lags, and an estimate written against last week's screens
is wrong in ways that are invisible until implementation.

## What is not in these numbers

QA effort is estimated separately and depends on the
kind of work. Project roles — management, analysis, communication — are computed
by the workbook from the development sum. Say both plainly in the report: a
client who reads a frontend total as a project total will be surprised later.
