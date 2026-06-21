You are executing a lifecycle-kit skill against a throwaway TEST git repository,
as a benchmark of that skill. The repo is disposable; destructive git operations
(git worktree remove, git branch -d/-D, branch moves, pushes to its local remote)
are expected and safe here. Operate ONLY on this one repo.

Test repo: {{REPO}}

Do this:
1. cd into the test repo.
2. Follow the skill instructions appended below, verbatim. Resolve any
   <manifest-key> placeholders from the repo's .claude/lifecycle-manifest.md.
3. Actually perform the operations the skill prescribes (this is NOT a dry run).
4. Report, as plain text, what you changed and the reason per the skill's logic.

{{GH_NOTE}}
