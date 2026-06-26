# Control prompt: issues verify (no-skill arm)

The bare task a user would give, with no pointer to the `issues` skill and no
statement of the verify procedure (check the referenced files; transition to
Resolved or Regressed). The runner substitutes `{{REPO}}`. Everything below the
`---` is the prompt.

---

You are helping maintain a project. Several issues in the tracker are marked with
the status "Resolved (verify)": they were fixed at some point, but the fix needs
to be re-confirmed, because some of them may have been reverted since. Please go
through those issues and bring the tracker up to date.

Repo: {{REPO}}

The tracker is at `knowledge/decisions/issues.md`; the project's conventions are
in `.claude/lifecycle-manifest.md` if you need them.

cd into the repo and actually update the tracker file (this is not a dry
description). Report what you changed and why.
