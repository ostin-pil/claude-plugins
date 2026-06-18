# Scenario: finalize-worktree refusal under ambiguity

**Skill:** `finalize-worktree`

**Setup** (`setup.sh`): two finalize candidates, each a `feature/*` worktree with
its own committed session log, and no explicit target given.

**Run:** finalize-worktree with no target specified.

**Expected** (`assert.sh`): the skill refuses (aborts or asks) and changes
nothing. No `feature/*` branch is pushed to origin, local `main` is unchanged,
and both candidate branches are intact.

**What it guards:** "more than one finalize candidate with no explicit target is
an abort-or-ask, never an auto-pick" (`workflow.md`, lifecycle skill design). An
auto-pick could merge the wrong session.

**gh:** none, on the correct path. The discriminating signal is that finalize
pushes the session branch *before* the gh step, so a wrong auto-pick leaves a
pushed branch on origin even though the gh merge cannot complete offline. A
later gh-mock scenario will make this airtight by catching a merge call
directly; until then, the no-push assertion is the proxy.

**Baseline:** PASS. The agent detected both candidates, refused to auto-pick
(falling back to abort-and-list when the interactive ask was unavailable), and
left the repo untouched. The assertion is shown to catch the bad case (it FAILs
when a candidate push is simulated).
