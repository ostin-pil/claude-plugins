# Agent prompt template

Substitute `{{SKILL_PATH}}` (the installed SKILL.md to execute) and `{{REPO}}`
(the path printed by the scenario's `setup.sh`), then run a fresh agent with it.
Keep the prompt faithful: it tells the agent to follow the skill, never what the
correct outcome is, so the skill's own logic is what's under test.

---

You are executing a lifecycle-kit skill against a throwaway TEST git repository,
as a benchmark of that skill. The repo is disposable; destructive git operations
(`git worktree remove`, `git branch -d/-D`, branch moves) are expected and safe
here. Operate ONLY on this one repo.

Test repo: {{REPO}}

Do this:
1. cd into the test repo.
2. Read and follow the skill's instructions from this file, verbatim:
   {{SKILL_PATH}}
   Resolve any `<manifest-key>` placeholders from the repo's
   `.claude/lifecycle-manifest.md`.
3. Actually perform the operations the skill prescribes (this is NOT a dry run).
4. Report, as plain text, what you changed and the reason per the skill's own
   logic.

Constraints: touch only {{REPO}}. There is no GitHub here; the remote is a local
bare repo, so do not run any `gh` command. If the skill calls for `gh`, note that
and use the underlying git state instead.
