# Scenario: session-start acts on a stale read

**Skill:** `session-start`

**Setup** (`setup.sh`): the repo carries session logs through 5 and no session
branches, so every source the pre-flight consults tops out at 5. Local `main`
matches `origin/main`. Nothing is wrong yet.

**Drift** (`git-mock/git`): the shim passes every call through to the real git
and, after the agent's **first** `fetch` returns, pushes
`feature/session-6-concurrent` to the bare remote. That is a concurrent session
claiming 6 in the window between the skill's step-1 fetch and its branch birth.

**Run:** session-start carried through its branch-birth step. The harness
supplies the branch-birth choice (new feature branch) and the topic `bench` to
unblock the question; it never supplies the number, which is what's under test.
The shim dir goes first on `PATH`, with `GIT_MOCK_DIR`, `GIT_MOCK_REAL` and
`GIT_MOCK_REMOTE` exported (setup.sh prints the exact exports).

**Expected** (`assert.sh`): the agent creates exactly one session branch, its
number is 7 or higher, and its tip equals `origin/main`. A branch named
`feature/session-6-*` is the failure: it means the number was minted from the
step-1 snapshot, after 6 had already been claimed.

**What it guards:** the stale-read gotcha, distinct from the stale-base one
`branch-birth` covers. Steps 2 through 6 read logs and history, which takes
minutes, so acting on step-1 state at step 7 mints a number another session
already took. This is the aboard incident of 2026-08-05, where two sessions
independently picked 41 and one had to renumber after the fact.

**Void vs fail:** `assert.sh` exits 2 when the concurrent branch never reached
the remote, because a run where the drift did not fire proves nothing and 6
would look correct. Exit 1 is a genuine skill failure. Do not read a void run
as a pass.

**gh:** none. Branch birth uses `git fetch` and `git switch -c` only.

**Baseline:** not yet run. The mechanics are verified (the shim fires on the
first fetch, the drift lands, and `assert.sh` discriminates void, fail and pass
against hand-staged git state), but the agent leg has not been executed.
