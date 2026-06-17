<!-- prose-check: skip bold-colon-opener -->
# Open Decisions

Tracks matters surfaced and acknowledged but not yet decided. Distinct from:

- **`issues.md`**, concrete bugs or regressions with a fix shape. Move an entry
  here to `issues.md` once the decision is made and the work is scoped.
- **Session logs**, what happened in a given session.

An entry belongs here when *we know it exists* but *we have not yet decided what
to do about it*. Close it (delete or strike through) once decided, leaving a
one-line resolution note pointing to the resulting `ISS-NNN`, commit, or session
log. The knowledge-audit skill points unpromoted session learnings here.

## Format

```
## OD-NNN: Short title
**Surfaced**: session N / commit / report
**Status**: needs data | needs decision | needs scope | parked
**Trigger to revisit**: the empirical or external event that should unblock the decision

**Context**: what surfaced this and why it isn't a one-liner.

**Options**:
- A: …
- B: …

**Open question**: the single thing a person needs to answer.
```

## Status values

- `needs data`, answer is empirical; revisit after the next measurement or run.
- `needs decision`, non-empirical; a person has to choose.
- `needs scope`, work shape is unclear (effort vs payoff TBD).
- `parked`, known and deliberately deferred; the trigger event is in the future.

---

<!-- Add entries below. Number them sequentially: OD-001, OD-002, ... -->
