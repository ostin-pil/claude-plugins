# Scenario: session-start branch birth off the integration ref

**Skill:** `session-start`

**Setup** (`setup.sh`): local `main` is one stray, unpushed commit ahead of
`origin/main`. The working tree is on `main`.

**Run:** session-start carried through its branch-birth step (the harness
supplies session number 200 and topic `bench` to unblock the name; it never
supplies the base, which is what's under test).

**Expected** (`assert.sh`): exactly one `feature/*` branch is created, its tip
equals `origin/main`, and the stray local-main commit is not an ancestor of it.

**What it guards:** the stale-base gotcha. A naive `git switch -c <branch> main`
would inherit the stray commit; the skill must fetch and base off `origin/main`.
This is the "branch birth" invariant in `workflow.md`.

**gh:** none. Branch birth uses `git fetch` and `git switch -c` only.

**Baseline:** PASS.
