# Phase 2: the target layout

```
AGENTS.md                     canonical project rules. In git. Any agent reads it
CLAUDE.md                     thin layer: @AGENTS.md plus Claude specifics. In git
.claude/
  README.md                   map of the directory: what is where, who runs it
  COMMANDS.md                 the command index — here, not in commands/ (see below)
  project-profile.md          what the shared plugins read: tracker, rates, links
  settings.json               shared settings: plugins and their marketplaces, attribution, allowed MCP, hooks. In git
  settings.local.json         personal permissions. Gitignored
  commands/                   slash commands. Command files only — no README here
  agents/                     subagent definitions, e.g. the review groups. In git
  skills/                     the source of truth for skills. In git
    README.md                 skill index — the subdirectory is not scanned, safe here
    <name>-local/             personal skills. Gitignored by suffix
  hooks/                      PostToolUse and friends. In git
    README.md                 exit-code contract, how to add one
  hooks-local/                personal checks. Gitignored except README
.agents/
  skills/<name>               symlinks to .claude/skills/<name>. Cross-agent convention
.mcp.json.example             MCP servers with ${VAR} placeholders. In git
.mcp.json                     generated. Gitignored
.env.example                  variable template. In git
.env                          real values. Gitignored
scripts/sync-mcp.*            generates .mcp.json from the example plus .env
docs/
  README.md                   documentation index plus file conventions
  local/README.md             the personal space, the only committed file inside
```

Matching `.gitignore`:

```gitignore
# agent harness: share the project surface, keep the personal part local
.claude/*
!.claude/commands/
!.claude/agents/
!.claude/skills/
!.claude/settings.json
!.claude/hooks/
!.claude/README.md
!.claude/COMMANDS.md
!.claude/project-profile.md
.claude/skills/*-local/
.claude/hooks-local/*
!.claude/hooks-local/README.md
.claude/settings.local.json
.mcp.json
.env

# docs/local — personal space, except its README
docs/local/*
!docs/local/README.md
```

## Two traps that cost a rewrite

**The command index goes in `.claude/COMMANDS.md`, not in `commands/`.** Claude
Code registers **every** `.md` inside `commands/` as a slash command — including
`README.md`. It lands in the command list, is paid for in every session, and
looks like a command it is not. `.claude/` itself is not scanned, so the index
moves one floor up. Put one line at the top of `COMMANDS.md` saying why it is not
in `commands/`, or the next person moves it back.

The limitation applies **only** to `commands/`. `skills/` is scanned for
subdirectories containing `SKILL.md`, and `hooks/` is not scanned at all — so
`skills/README.md` and `hooks/README.md` are harmless and stay next to what they
describe.

**Skills are real directories in `.claude/skills/`, and `.agents/skills/<name>`
are symlinks to them — that direction, not the reverse.** Claude Code does not
resolve symlinks when scanning `.claude/skills/`, and custom skills simply vanish
from the list. Always edit the files under `.claude/skills/`; create the link
once:

```bash
ln -s ../../.claude/skills/<name> .agents/skills/<name>
```
