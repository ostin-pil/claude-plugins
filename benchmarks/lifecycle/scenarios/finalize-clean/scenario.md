# Scenario: finalize-worktree (full flow, with a gh mock)

**Skill:** `finalize-worktree`

**Setup** (`setup.sh`): one `feature/*` worktree with a code commit and a
committed session log, ahead of `origin/main`, not yet pushed (the skill pushes).
It also creates a `GH_MOCK_DIR` for the mock's state and log.

**The gh mock** (`../../gh-mock/gh`) handles the exact `gh` calls the skill makes
and, for `pr merge`, actually lands the merge on the file remote so Phase 4's
fast-forward is real. `GH_MOCK_MERGE_MODE` selects the path:
- `clean` (default): merge, delete the remote branch, exit 0.
- `partial`: merge, keep the remote branch, exit 1 with the cross-worktree
  `--delete-branch` abort (the finding-3 case). The merge still landed.

**Run:** a fresh agent executes the skill with the mock on PATH, authorized to
confirm the one merge gate. Because a fresh shell does not persist env or cwd,
every command carries this prefix:

```
export PATH="<repo>/benchmarks/lifecycle/gh-mock:$PATH" \
  GH_MOCK_DIR="<mockdir>" GH_MOCK_REMOTE="<bare-remote>" GH_MOCK_MERGE_MODE=clean
```

`GH_MOCK_REMOTE` exists because a fresh shell can start in any directory; the
mock must not read the remote from cwd.

**Expected** (`assert.sh <repo> <mockdir>`): the merge is on `origin/main`; local
`main` fast-forwarded to it (never-merge-locally, ISS-W3); local and remote branch
deleted; worktree removed; `gh pr merge` called exactly once.

**What it guards:** the whole finalize path, and two incidents. ISS-W3: local
`main` only fast-forwards, never a divergent local merge (asserted as local
`main` == `origin/main` exactly). Assert-then-reconcile (sessions 82/83/85): in
`partial` mode the merge lands but `gh pr merge` exits non-zero; the skill must
not re-merge (it checks the remote state, which is `MERGED`) and Phase 4 cleans
up the lingering remote branch via `gh api ... DELETE`.

**Baseline:** clean mode PASS by a full agent run (all four git invariants) and a
deterministic replay (including the one-merge check). Partial mode validated by a
deterministic replay: `gh pr merge` called once after `MERGED`, and the lingering
remote branch reconciled via `gh api DELETE`.
