# harness_behind.py

Two modes. Without arguments it is the `SessionStart` hook: one
`systemMessage` for the developer when the project's baseline is missing,
older than the last entry of `CHANGES.md` or unknown to the installed plugin,
and silence otherwise — it never fails a session. With `--entries` it is
the audit's delta. Run it; this file is its contract.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/harness_behind.py" --entries [--project <dir>]
```

- **Project** — the directory holding `.claude/project-profile.md`;
  `$CLAUDE_PROJECT_DIR`, else the current directory. The baseline is the
  line `Baseline: <id>` in the profile's `## Harness` section.

## Output

The baseline's state on the first line, exit 0:

```
baseline: review-four-questions — 2 newer entries
baseline: handoff-every-commit — 0 newer entries
baseline: none — run the full audit, which sets one
baseline: off
baseline: gate-x — not in the installed plugin, whose last entry is handoff-every-commit; update it first
```

After `— N newer entries`, each entry after the baseline in order, whole —
its heading `## <date> · <id>` and every line up to the next entry, a
`Supersedes:` included — each after a blank line. The other states print
nothing more.

Exit 1, with the reason on stderr, when the profile does not exist.
