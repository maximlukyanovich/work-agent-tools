# The team file

`docs/local/team.md` in the project — who is who, kept by the developer.
**Personal and gitignored**: it holds names and Jira account ids, which never
go into committed harness files or into this plugin.

The tracker cannot answer these questions on its own: a role in Jira is a
group, not "who decides the copy on this screen", and an assignee says who
works on one issue, not whom to ask about the design. Without the file the
agent guesses an addressee from context — and a question to the designer
lands with the backend developer.

Read by `/work-jira:questions` and by `/work-jira:comment` whenever a comment
addresses or mentions someone. Missing → they offer to create it from the
shape below and ask the developer for every row; nothing is inferred.

```markdown
# Team

| Who | Role | Ask about |
| --- | --- | --- |
| <Name Surname> (<short name>) | <role as the team says it> | <what this person answers> |

## Jira mentions

| Who | accountId |
| --- | --- |
| <Name Surname> | <accountId> |

The account id comes from the tracker's user search, never from memory. A
mention is an ADF `mention` node with that id — typed text "@Name" notifies
no one.

## Rules

- Backend addressee: <e.g. the assignee of the backend issue that blocks ours>.
- Tone: <e.g. informal; questions phrased from "we">.
- Comment header: <e.g. "Questions for BE (FYI @Name):">.
- Notice header: <e.g. "For information (FYI @Name):"> — a phrase that reads
  as "for reference", never one that reads as "to be agreed"; a point that
  needs agreeing is a question.
- Channel per role: <e.g. DevOps questions go to the team chat, not the
  tracker> — a role whose questions do not belong in issue comments.
```

**Keep it current**: a new person, a changed role or a new tool account is a
one-line edit the same day. A stale row sends a question to the wrong person
— the failure this file exists to prevent.
