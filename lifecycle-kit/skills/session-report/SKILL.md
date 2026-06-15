---
name: session-report
description: Update or create today's session log in the session-log folder
allowed-tools: Bash Read Edit Write Glob Grep
---

Update the session log for today's work. This is the report-writing half
of the session lifecycle — it records what happened. No build gating and
no worktree finalization. `/session-end` invokes this skill as one of its
phases; you can also run it standalone to checkpoint mid-session.

## Project configuration

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a
step names a manifest key in `code font` (`log_dir`, `log_pattern`,
`branch_pattern`, `docs_log_branch`, `build_commands`, `test_commands`), use
that key's value. The suffix examples (`_audio`, `_api`) are illustrative.

1. Determine the session number `N` and the log filename from the branch, never by minting a new number. `/session-start` is the sole authority that mints `N` (it bakes it into the branch name at branch birth); this skill only consumes it.
   - Normal case, on a `branch_pattern` branch (`feature/session-<N>-<topic>` for Untype): `N` is that number and `<suffix>` is the topic slug (or a `_audio`/`_api`-style workstream suffix when several agents log in parallel). Parse both from `git branch --show-current`.
   - Log-only exception, on a `docs_log_branch` (`docs/session-<N>-log`) branch: `N` is that number, no suffix.
   - Standalone on `main` with no session branch (rare): do not invent a number from filenames. If today already has a session log, update it; otherwise ask the caller for `N`.
   - The log file follows `log_pattern` under `log_dir` (`sessions/YYYY-MM-DD_session_<N>[_<suffix>].md` for Untype) for the current date. The identity is the pair `(N, suffix)`: a suffixed log and a bare-`N` log are distinct files, so worktree agents each get their own log and never collide. If it exists, update it (step 5); if not, create it from the pattern in the most recent existing log.
2. Read the current session file and the previous one for format reference.
3. Update the session file with:
   - `## Context` — 1-paragraph framing
   - `## What happened` — numbered sections with details
   - `## Files changed` — table: file | change
   - `## Build status` — the `build_commands`/`test_commands` result. If the caller (e.g. `/session-end`) passed pre-computed output via `$ARGUMENTS`, fold it in verbatim rather than re-running the commands. Otherwise mark as "not re-run this session" — do not run build/test from this skill.
   - `## Decisions worth remembering` — non-obvious calls made
   - `## What's next` — immediate + deferred
   - `## Commits` — this session's commits as `<short-sha> <title>`, newest last; `/session-start` reads the last entry as its "shipped since" anchor, so keep it current
   - The header block at the top, in the format `/session-start` parses: an H1 `# Session <N>: <theme>` title, then `**Date**:`, `**Branch**:` (the `branch_pattern` branch, `feature/session-<N>-<topic>` for Untype, with worktree path if any), and `**Type**:` lines
4. Keep the format consistent with existing session logs in `log_dir`.
5. Do not remove existing content — append or update sections as needed.
6. No emojis.

## Arguments

`$ARGUMENTS` is optional. If the caller (typically `/session-end`) passes
pre-computed build/test output, fold it into `## Build status` verbatim.
