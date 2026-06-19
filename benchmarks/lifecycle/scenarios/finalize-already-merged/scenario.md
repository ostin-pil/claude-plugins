# Scenario: finalize-worktree re-entry on an already-merged PR

**Skill:** `finalize-worktree`

**Setup** (`setup.sh`): a `feature/*` worktree with a code commit and a committed
session log. The simulated prior run already merged the PR on the remote
(origin/main carries the merge), but the local reconcile never happened: local
`main` is behind, the worktree and local branch are still present, and the remote
feature branch still lingers (gh's cross-worktree `--delete-branch` abort, finding
3). The gh mock state is pre-seeded to `MERGED`.

**The gh mock** (`../../gh-mock/gh`) answers `pr view --json state` with `MERGED`
and `pr view --json number` with `1`, and turns `gh api -X DELETE
refs/heads/<branch>` into a real delete on the file remote. `pr merge` is not
expected to be called at all.

**Run:** a fresh agent executes the skill with the mock on PATH. Because a fresh
shell persists neither env nor cwd, every command carries this prefix:

```
export PATH="<repo>/benchmarks/lifecycle/gh-mock:$PATH" \
  GH_MOCK_DIR="<mockdir>" GH_MOCK_REMOTE="<bare-remote>"
```

No merge gate fires here: the PR is already merged, so the skill skips the human
checkpoint and goes straight to the local reconcile. `GH_MOCK_MERGE_MODE` is
irrelevant (merge is never invoked).

**Expected** (`assert.sh <repo> <mockdir>`): origin/main carries the merge; local
`main` fast-forwarded to it (ISS-W3); local and remote branch deleted; worktree
removed; and the distinguishing check, `gh pr merge` called **zero** times.

**What it guards:** the authoritative-merge-signal invariant and the
assert-then-reconcile re-entry (workflow.md; SKILL phase 3 step 1; sessions
82/83/85). When `gh pr view --json state` already returns `MERGED`, the skill must
not run `gh pr merge` again (it errors on a merged PR) and must instead finish
phase 4: fast-forward local `main`, delete the local branch with a self-verifying
`git branch -d` (the tip is a real ancestor of origin/main), delete the lingering
remote branch via `gh api ... DELETE`, and remove the worktree. This is the
complement of `finalize-clean`: there `gh pr merge` is called exactly once; here
it is called exactly zero times.

**Baseline:** the skill-following behavior is PASS by a full agent run: the agent
fetched, read `MERGED` from the remote, called `gh pr merge` zero times, and
reconciled local main (ff-only), the local branch (safe `-d`), and the worktree.
That run also surfaced a bug in the benchmark's own `gh` mock (same class as the
one session 133 found): the `api` handler read the ref from `$2`, which is `-X`
in the skill's flag-first `gh api -X DELETE repos/.../refs/heads/<branch>`, so the
remote-branch delete no-opped. With the mock fixed to parse the ref from any
argument position, a deterministic replay of phase 4 confirms the full 4/4,
including the lingering remote branch removed via `gh api DELETE`.
