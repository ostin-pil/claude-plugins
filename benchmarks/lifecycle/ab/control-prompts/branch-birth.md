# Control prompt: branch-birth (no-skill arm)

The bare task a user would give, with no pointer to `session-start` and no hint of
the disciplines under test. The runner has already run `setup.sh` and substitutes
`{{REPO}}` and `{{GH_NOTE}}`. Everything below the `---` is the prompt.

---

You are helping in a git repository. I'm starting a new work session and want my
work on its own feature branch, per the project's convention.

Repo: {{REPO}}

1. cd into the repo.
2. Create the new session's feature branch (session number 200, topic `bench`) so
   I can start working on it. Follow the repo's conventions; there is a
   `.claude/lifecycle-manifest.md` if you need them. Actually create the branch
   (not a dry run).

{{GH_NOTE}}

Report, in plain text, what branch you created and from what starting point.
