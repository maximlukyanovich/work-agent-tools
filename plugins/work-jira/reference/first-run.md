# First run: what to ask

Everything below is asked **once**, in a single batch, and written to
`.claude/project-profile.md`. A second run reads the profile and asks nothing.

Never ask what can be derived. Derive first:

| What | From |
| --- | --- |
| Instance URL, project key | the profile, else `.mcp.json` / `.env` |
| Allowed labels | `GET /rest/api/3/label` |
| Issue types and their ids | `createmeta` for the project |
| Workflow statuses | the workflow API |
| Platform, branches | `git remote`, `git branch` |
| Stack, quality commands | `package.json`, `pyproject.toml`, config files |

## The five questions

Each carries a recommended default, so the answer can be a nod.

1. **Language.** Summaries and descriptions — which language each?
   *Default: English for both.*

2. **Prefixes.** `[FE]` / `[BE]` in summaries — keep or drop?
   *Default: drop; the company standard leaves direction to the label.*
   If kept, record the reason alongside.

3. **Epic granularity.** A product surface, or a functional layer?
   *Default: product surface — it keeps "where is screen X?" a one-answer
   question.*

4. **Description sections.** The four required ones are fixed. Which of the
   optional ones apply: `Out of scope`, `Technical notes`, `Open questions`?
   *Default: all three, used when they earn their place.*

5. **Estimate basis.** Pessimistic, optimistic, or optimistic plus overheads
   (automated tests, responsive layout, localisation)?
   *Default: optimistic. If overheads are folded in, name which ones and their
   percentages.*

## What to write

Into `.claude/project-profile.md`, sections `## Tracker` and `## Issues`. Create
the file if it is absent; append the sections if it exists without them; never
rewrite sections owned by another plugin.

Record deviations from the company standard together with the reason for them.

## The one hard prerequisite

Credentials for the tracker. Without a working `.mcp.json` the command stops and
says how to get one — copy `.env.example`, fill it in, run the project's mcp sync
— rather than failing with "no tools found".
