# The project profile

`.claude/project-profile.md` — what the shared plugins read before doing
anything. Committed: it is a project decision, not a personal setting.

It is **sectioned**, and each plugin owns its sections. `work-bootstrap`
writes the whole file; another plugin installed on its own creates or appends
only its own section and never rewrites someone else's.

```markdown
# Project profile

Read by every shared tool before it acts. This file outranks the defaults those
plugins ship; only what the developer says in the current session outranks it.

## Tracker
System, instance URL, project key, allowed labels, where credentials come from.

## Issues
Language of summaries and descriptions. Prefixes, and the reason if they deviate
from the standard. Epic granularity. Required and optional description sections.

## Estimation
The two work rates and their bands. Coefficients and their percentages. Which
number goes into the estimate field. What is tracked as separate work.

## Sources of truth
Spec and design, as durable links. The local copy path, if there is one, marked
as a copy that lags.

## Repository
Branch chain and platform. Languages: committed, user-facing, conversation. The
gate command.
```

Two rules that keep it useful:

**Only decisions.** Anything an API answers in one call — labels, issue type ids,
statuses — is fetched, not copied. A copy becomes a second truth that goes stale
in silence.

**Deviations carry their reason.** A project that departs from the company
standard records why, so the next reader sees a decision rather than a mistake.
