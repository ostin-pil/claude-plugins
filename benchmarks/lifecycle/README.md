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
| `ambiguous-finalize` | finalize-worktree | two candidates, no target: refuse, push and merge nothing | no |
| `finalize-clean` | finalize-worktree | full flow: merge lands, local main ff-only (ISS-W3), branch+worktree swept, one merge call; `partial` mode adds the assert-then-reconcile incident | mock |

## The gh mock

Scenarios that exercise the merge path use `gh-mock/gh`, a stand-in placed first
on PATH. It handles the `gh` calls `finalize-worktree` makes, logs every call,
and for `pr merge` actually lands the merge on the file remote (so the
fast-forward is real). It reads `GH_MOCK_DIR` (state + log), `GH_MOCK_REMOTE` (the
bare remote, so it never depends on cwd), and `GH_MOCK_MERGE_MODE`
(`clean`|`partial`). Because a fresh shell persists neither env nor cwd, every
command in a mock scenario carries the export prefix shown in
`scenarios/finalize-clean/scenario.md`.
