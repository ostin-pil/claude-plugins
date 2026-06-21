# Control prompt: finalize-clean (no-skill arm)

The bare task a user would give, with no pointer to `finalize-worktree` and no hint
of the never-merge-locally / single-merge / reconcile-the-remote-branch
disciplines. The runner has already run `setup.sh`, exported the `gh` mock env, and
substitutes `{{REPO}}` and `{{GH_NOTE}}`. Everything below the `---` is the prompt.

---

You are helping wrap up work in a git repository. Please finalize the current
session: get its work merged into the main line through a pull request and clean up
the session's branch and worktree, following the project's convention.

Repo: {{REPO}}

1. cd into the repo.
2. Finalize the session per the repo's conventions (there is a
   `.claude/lifecycle-manifest.md` describing them). Actually perform it (not a dry
   run).

{{GH_NOTE}}

Report, in plain text, what you finalized and how.
