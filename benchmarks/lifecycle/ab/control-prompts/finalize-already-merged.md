# Control prompt: finalize-already-merged (no-skill arm)

The bare task a user would give on a re-entry, with no pointer to
`finalize-worktree` and no statement that the PR is already merged. The user only
knows a prior wrap-up attempt didn't finish; the agent must discover the remote
state itself. Saying "already merged" here would leak the exact discipline under
test (check the authoritative remote PR state; never re-merge a merged PR). The
runner has already run `setup.sh`, exported the `gh` mock env, and substitutes
`{{REPO}}` and `{{GH_NOTE}}`. Everything below the `---` is the prompt.

---

You are helping wrap up work in a git repository. An earlier attempt to finalize
this session didn't fully complete. Please finish finalizing it: make sure its
work is integrated into the main line and clean up the session's branch and
worktree, following the project's convention.

Repo: {{REPO}}

1. cd into the repo.
2. Finish finalizing the session per the repo's conventions (there is a
   `.claude/lifecycle-manifest.md` describing them). Actually perform it (not a dry
   run).

{{GH_NOTE}}

Report, in plain text, what state you found things in and what you did to finish.
