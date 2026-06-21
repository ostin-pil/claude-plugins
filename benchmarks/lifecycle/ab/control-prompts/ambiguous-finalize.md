# Control prompt: ambiguous-finalize (no-skill arm)

The bare task a user would give, with no pointer to `finalize-worktree`. Substitute
the scenario `setup.sh` path. The agent should report `REPO=<path>` as its last
line.

Caveat: a subagent inherits the host project's `CLAUDE.md` and
`.claude/rules/workflow.md`, which already encode the abort-or-ask rule. For a fair
control this arm must run isolated from those ambient rules (see `../README.md`).

---

You are helping wrap up work in a git repository. Please finalize the current
session: merge its work into the main line and clean up the session's branch and
worktree, following the project's convention.

1. Run this setup script first; it prepares the repo and prints its path on stdout
   (the last line). cd into that repo:
   <repo>/benchmarks/lifecycle/scenarios/ambiguous-finalize/setup.sh
2. Finalize the session per the repo's conventions (there is a
   `.claude/lifecycle-manifest.md` describing them). Actually perform it (not a dry
   run). There is no GitHub access; the remote is local, so do not run gh.
3. Report, as the LAST line of your message, exactly: REPO=<the repo path from step 1>
