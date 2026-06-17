<!-- prose-check: skip bold-colon-opener -->
# Issue & Solution Tracker

Problems encountered during development and how they were resolved. Each entry
records its symptom, root cause, fix, and the session it was handled in. The
`issues` skill (knowledge-kit) reads and updates this file; its path is the
`issues_file` manifest key.

The pragma on line 1 tells prose-mint's gate to allow the `**Field**:` record
schema below (it is structured data, not prose).

## Format

```markdown
## ISS-NNN: Short title
**Session**: N | **Date**: YYYY-MM-DD | **Status**: Open|Resolved|Resolved (verify)|Regressed

**Symptom**: What the user sees or experiences.

**Root Cause**: Why it happens.

**Fix**: What was done to resolve it.

**Commit**: `abc1234` (if available)

**Files**: List of affected files (if applicable)
```

## Status values

- **Open** — known issue, not yet fixed
- **Resolved** — fixed and confirmed
- **Resolved (verify)** — fixed but needs verification (e.g. may have been reverted)
- **Regressed** — was fixed but the fix was lost

---

<!-- Add entries below, newest last. Number them sequentially: ISS-001, ISS-002, ... -->
