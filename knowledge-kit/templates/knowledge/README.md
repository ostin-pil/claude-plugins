# Knowledge

Project-internal docs that are not code, not session logs, and not research.
Each subfolder has its own scope; start here. This is a starter skeleton from
knowledge-kit; add, rename, or drop subfolders to fit the project.

## Subfolders

| Folder | Holds |
|---|---|
| `decisions/` | Tracked issues and open decisions. Key files: `decisions/issues.md` (the `ISS-NNN` tracker the issues skill manages) and `decisions/open-decisions.md` (`OD-NNN`, things surfaced but not yet decided). |
| `audits/` | Code-health, security, and review reports. The knowledge-audit skill writes here when run with `save`. |
| `workflow/` | How-we-work notes: process, conventions, and learnings promoted out of session logs. |
| `setup/` | One-time environment and setup notes. |

## When to add a file here

If it's a tracked issue or an open decision, it goes in `decisions/`. If it's an
audit or review, `audits/`. If it's a how-we-work note or a promoted learning,
`workflow/`. If it's one-time setup, `setup/`. When in doubt, drop it at the root
and open a small PR.

## How this connects to the skills

- The **knowledge-audit** skill scans this tree (plus `research/` and the session
  logs) for orphaned docs, stale docs, and learnings that were never promoted out
  of a session log into one of these durable homes.
- The **issues** skill manages `decisions/issues.md`.
- Promotion (graduating a session-log learning into `decisions/` or a durable doc
  here) is the act that keeps insight from staying trapped in the logs.
