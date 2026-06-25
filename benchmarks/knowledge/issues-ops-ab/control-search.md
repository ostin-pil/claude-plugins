# Control prompt: issues search (no-skill arm)

The bare task a user would give, with no pointer to the `issues` skill and no hint
that the session logs are part of the search surface. The runner substitutes
`{{REPO}}`. Everything below the `---` is the prompt.

---

You are helping on a project. A teammate asked whether we have any tracked issues
related to "thermal throttling". Look through the project's issue tracking and
tell them what you find.

Repo: {{REPO}}

The tracker is at `knowledge/decisions/issues.md`; the project's conventions are
in `.claude/lifecycle-manifest.md` if you need them.

Report the matching issues with their IDs and status, or say there are none.
