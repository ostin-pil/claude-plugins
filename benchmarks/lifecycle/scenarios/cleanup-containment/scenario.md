# Scenario: cleanup-worktrees containment

**Skill:** `cleanup-worktrees`

**Setup** (`setup.sh`): a repo with a file-based remote and two non-primary
worktrees.
- `feature/session-901-done` is merged into `origin/main` (work contained).
- `feature/session-902-active` has a commit not in `origin/main` (unique work).

**Expected** (`assert.sh`): the skill sweeps the contained worktree and its
branch (901), and preserves the worktree whose work is not yet in the
integration ref (902).

**What it guards:** the "don't sweep a worktree that still holds unique work"
invariant, which is the session-131-survives behavior from the knowledge-kit
cutover. A regression here would delete an active session's work.

**gh:** none. Containment is measured with `git fetch` plus a
`rev-list`/`merged` check against `origin/main`; no GitHub is involved.

**Baseline:** PASS. The assertion is shown to discriminate (it FAILS against the
freshly set-up repo before the skill runs).
