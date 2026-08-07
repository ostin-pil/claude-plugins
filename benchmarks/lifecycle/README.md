# Lifecycle execution benchmark

Tests whether the lifecycle skills, when an agent actually runs them, produce the
correct git state — not whether the prose reads well. The adoption benchmark
showed manifest inference is solid; this one targets the higher risk, the skills'
behavior on real repos, especially the documented failure modes.

## How it works (offline by design)

Each scenario is three parts:

1. `setup.sh` builds a throwaway git repo with a **file-based remote** (a local
   bare repo), puts it in a known state, and prints the repo path on stdout.
   A file remote means `git fetch`, `push`, `branch`, and `worktree` all work
   with zero GitHub, so scenarios run offline and leave no real PRs behind.
2. A **fresh agent** executes one installed skill against that repo, following
   the skill's `SKILL.md` verbatim and resolving config from the repo's
   `.claude/lifecycle-manifest.md`. The prompt template is `run-agent-prompt.md`.
3. `assert.sh <repo>` checks the **ground-truth git state** and exits non-zero on
   any mismatch. The agent's self-report is never trusted; the assertion is.

The handful of behaviors that genuinely need `gh` (PR create and merge) will use
a small `gh` mock on PATH in a later scenario. The first scenarios are pure git,
where most of the lifecycle invariants and every documented incident actually
live.

## Run a scenario

```
REPO=$(scenarios/<name>/setup.sh)
# run a fresh agent with run-agent-prompt.md, substituting the skill path and $REPO
scenarios/<name>/assert.sh "$REPO"
```

## Scenarios

| Scenario | Skill | Asserts | gh? |
|---|---|---|---|
| `cleanup-containment` | cleanup-worktrees | a contained worktree is swept; one with unique work survives | no |
| `branch-birth` | session-start | the session branch is born off the integration ref, not the stray-ahead local main | no |
| `stale-read` | session-start | a session number minted after a concurrent claim lands mid-run avoids the collision, **and** the re-read that guarantees it actually happened (git mock + shim-trace assertion) | no |
| `ambiguous-finalize` | finalize-worktree | two candidates, no target: refuse, push and merge nothing | no |
| `finalize-clean` | finalize-worktree | full flow: merge lands, local main ff-only (ISS-W3), branch+worktree swept, one merge call; `partial` mode adds the assert-then-reconcile incident | mock |
| `finalize-already-merged` | finalize-worktree | re-entry on a PR already `MERGED`: skip the merge entirely (zero `gh pr merge` calls), reconcile local main + branch + worktree, delete the lingering remote branch via `gh api` | mock |

## The gh mock

Scenarios that exercise the merge path use `gh-mock/gh`, a stand-in placed first
on PATH. It handles the `gh` calls `finalize-worktree` makes, logs every call,
and for `pr merge` actually lands the merge on the file remote (so the
fast-forward is real). It reads `GH_MOCK_DIR` (state + log), `GH_MOCK_REMOTE` (the
bare remote, so it never depends on cwd), and `GH_MOCK_MERGE_MODE`
(`clean`|`partial`). Because a fresh shell persists neither env nor cwd, every
command in a mock scenario carries the export prefix shown in
`scenarios/finalize-clean/scenario.md`.

## The git mock

`git-mock/git` exists for one job the `setup.sh` model cannot do: change the
repo's world **while the agent is mid-run**. It forwards every call to the real
git and, after the first `fetch` returns, pushes a concurrent session's branch
to the bare remote. Counting fetches rather than sleeping is what keeps it
deterministic; a timer would race the agent's reading speed.

It reads `GIT_MOCK_DIR` (state + log), `GIT_MOCK_REAL` (an absolute path to the
real git, since the shim is first on PATH and cannot resolve `git` by name),
`GIT_MOCK_REMOTE` (the bare remote), and `GIT_MOCK_BRANCH` (the branch to land,
defaulting to `feature/session-6-concurrent`). `setup.sh` prints the exact
exports.

Scenarios using it must distinguish a **void** run from a failure. If the drift
never lands, the agent never met the condition under test, and the answer a
correct skill gives is indistinguishable from the answer a broken one gives.
`stale-read/assert.sh` exits 2 in that case and says so.

## What the assertions cannot see

Ground-truth git state is the right thing to assert and it has a hard limit:
it records what happened, never why. Where a skill's contribution is a *process
guarantee* rather than a distinct end state, an outcome check cannot attribute
the outcome to the skill.

`stale-read` is the worked example, run on both sides of its own fix on
2026-08-07 and passing on both by end state alone
(`scenarios/stale-read/scenario.md` has the detail). The pre-fix agent reached
the correct session number by distrusting a silent `git fetch` and going to `git
ls-remote`; the post-fix agent reached it by following the re-read block. A
guaranteed re-read and a diligent one leave the same refs behind.

## Asserting on the trace, not the self-report

The way out is narrower than it first looks. "The agent's self-report is never
trusted" rules out asking the agent what it did. It does not rule out watching.
A mock on `PATH` writes its own log of every call the agent made, from outside
the agent, and that log is evidence of *process* without being testimony.

`stale-read/assert-trace.sh` is the worked example: the pre-fix arm reads
session branches after one fetch, the post-fix arm after two, and asserting that
ordering separates two runs whose git state is identical. It is a proxy for
intent rather than proof of it, and it says so.

Two habits worth carrying into a new scenario. Check whether the behavior has an
end state a competent agent could not also reach by another route; if it does
not, the mock log is where to look. And keep the trace assertion in its own
script with recorded traces as fixtures, so a `selftest.sh` can regression-test
the assertion without spending agent runs on it.
