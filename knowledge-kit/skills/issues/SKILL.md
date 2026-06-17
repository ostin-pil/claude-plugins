---
name: issues
description: Track, search, and manage development issues and their solutions
allowed-tools: Read Write Edit Grep Glob Bash
---

Manage the project issue tracker. The tracker file and the session-log
directory both come from the lifecycle manifest, so this skill is project-
agnostic.

## Project configuration

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Two keys
drive this skill:
- `issues_file` — the tracker path (e.g. `knowledge/decisions/issues.md`). If it
  is `none`, the project has not adopted a tracker; tell the user to set
  `issues_file` (knowledge-kit ships a scaffold at
  `templates/knowledge/decisions/issues.md`) and stop.
- `log_dir` — where session logs live (e.g. `sessions`), used by `search`.

In the commands below, `<issues_file>` and `<log_dir>` mean those values.

## Commands

Parse the user's argument to determine the action:

### `/issues` (no argument) — List all issues
- Read `<issues_file>`
- Show a summary table: ID, title, status, date

### `/issues add <description>` — Add a new issue
- Read `<issues_file>` to get the next ISS number
- Create a new entry with the standard format (see below)
- Ask for any missing fields: symptom, root cause, fix, files, session number
- Write the updated file

### `/issues search <query>` — Search for related issues
- Grep `<issues_file>` for the query terms
- Also search session logs in `<log_dir>/` for related mentions
- Report matching issues with their status

### `/issues update <ISS-NNN> <status/info>` — Update an existing issue
- Find the issue by ID
- Update its status, add notes, or mark as resolved
- Include commit hash if available

### `/issues verify` — Check "Resolved (verify)" issues
- Find all issues with status "Resolved (verify)"
- Check the referenced files to see if the fixes are still present
- Update status to "Resolved" if confirmed, or "Regressed" if the fix was lost

## Entry Format

```markdown
## ISS-NNN: Short title
**Session**: N | **Date**: YYYY-MM-DD | **Status**: Open|Resolved|Resolved (verify)|Regressed

**Symptom**: What the user sees or experiences.

**Root Cause**: Why it happens.

**Fix**: What was done to resolve it.

**Commit**: `abc1234` (if available)

**Files**: List of affected files (if applicable)
```

## Status Values
- **Open** — Known issue, not yet fixed
- **Resolved** — Fixed and confirmed
- **Resolved (verify)** — Fixed but needs verification (e.g., may have been reverted)
- **Regressed** — Was fixed but the fix was lost

## Guidelines
- Always read the current file before writing to avoid data loss
- Increment the ISS number sequentially
- Link to session logs where the issue was discovered/fixed
- If an issue relates to a knowledge base entry, cross-reference it
