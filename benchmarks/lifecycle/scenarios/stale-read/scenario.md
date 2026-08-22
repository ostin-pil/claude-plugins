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

**Baseline (2026-08-07): pre-fix fails, post-fix passes.** The scenario
discriminates, but only because of the process assertion in `assert-trace.sh`,
added later the same day. The end-state checks alone do not, and the record of
that is kept below because it is the whole reason that assertion exists.

| Arm | `session-start` | End-state checks | `assert-trace.sh` | Overall |
| --- | --- | --- | --- | --- |
| pre-fix | 0.2.0 | pass | **FAIL**, 1 fetch before the first session read | `VERDICT: FAIL`, exit 1 |
| post-fix | 0.2.2 | pass | ok, 2 fetches before it | `VERDICT: PASS`, exit 0 |

Both shim traces are kept under `fixtures/`, and `selftest.sh` runs the
assertion against them, so a regression in the assertion itself is caught
without spending two agent runs to find out.

### The end-state result, and why it was not enough

Two arms were run against installed lifecycle-kit versions, one either side of
the fix this scenario was written for:

| Arm | `session-start` | Branch created | `assert.sh` |
| --- | --- | --- | --- |
| pre-fix | 0.2.0, no "Re-read before acting" block in step 7 | `feature/session-7-bench` | `VERDICT: PASS`, exit 0 |
| post-fix | 0.2.2, block present | `feature/session-7-bench` | `VERDICT: PASS`, exit 0 |

Neither run was void: the shim landed `feature/session-6-concurrent` on the
remote in both. Both arms issued exactly three `git` fetches, so even the fetch
count fails to separate them.

How the pre-fix arm got to 7, from its shim log. Its step-1 fetch is prescribed
as `git fetch <remote> --prune 2>/dev/null`, which throws away the `* [new
branch]` progress lines, so a fetch that did real work is indistinguishable from
a no-op. Running the pre-flight's branch source, `git branch -a --list
'*session-*'`, then returned nothing, because the drift had landed on the remote
and no local tracking ref existed for it yet. The agent did not accept that. It
ran `git ls-remote origin`, which reads the remote directly and did show the
concurrent claim, chased the discrepancy through `show-ref`, `for-each-ref` and
the `remote.origin.fetch` refspec, re-fetched to materialize the tracking ref,
and only then computed `N`. It reached 7 by refusing to trust a quiet fetch, not
because the skill told it to re-read.

The post-fix arm's log is the skill's text executed literally: fetch, then the
four named facts (`rev-parse <integration_ref>`, `worktree list`, `branch -a
--list '*session-*'`, `status --short`), then `N`.

**Why end state cannot separate them.** The behavior under test is a process
guarantee, that the fixed skill *always* re-reads. End state is an outcome, and
a guaranteed re-read and a lucky one leave byte-identical git state. Retiming
the drift does not close the gap either: the fixed skill's re-read happens
before its pre-flight computes `N`, so any drift early enough to be missed by a
skill without the block is also early enough to be caught by one with it, and
any drift later than that is missed by both.

**What closed it.** The harness distrusts the agent's *self-report* (`README.md`,
"the agent's self-report is never trusted"), and that rule was read too broadly
at first, as ruling out any evidence about process. The shim's log is not a
self-report. It is a mechanical record the harness writes itself, from the
outside, of every `git` invocation the agent made, and the agent neither
produces it nor knows its contents. Asserting on it keeps the distrust intact.

The two arms are plainly different in that record: the pre-fix arm reads session
branches after one fetch and has to redo the work, the post-fix arm reads them
after two. `assert-trace.sh` tests exactly that, and the ordering is a proxy
rather than proof of intent, which its header says plainly.

**What it still cannot do.** An unfixed skill whose operator happens to fetch
twice before the pre-flight passes this check. The assertion is strictly more
than the outcome checks can see, and it fails the recorded pre-fix trace, which
is the property that matters. It is not a proof that the re-read was deliberate.
