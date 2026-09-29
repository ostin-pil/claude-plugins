# Scenario: session-end commits under a commit-msg hook (forge: none)

**Skill:** `session-end`, which delegates to `session-report` and
`finalize-worktree`, and through it to `forges/none.md`.

**Why it exists.** Before lifecycle-kit 0.3.3 the two commits the kit makes
ignored the manifest. The log commit hardcoded one project's
`docs(sessions): ...` subject with no trailers, and the `forge: none` merge was
`-m "Merge $BRANCH"` with no trailer. In a project whose `commit-msg` hook
requires a trailer, the hook refused that merge and left it staged in the
primary checkout (Puri session 3).

**Setup** (`setup.sh [hook|legacy|refuse]`): a repo with no remote and
`forge: none`, one `feature/session-501-trailers` worktree with a work commit and
an uncommitted session log.

| Mode | Manifest | Hook | Expected |
|---|---|---|---|
| `hook` | `commit_convention: "short description"`, two trailers, one with `<model>` | refuses any commit, merges included, whose *parsed* trailer block lacks either | log commit and merge both pass the hook; log subject has no prefix |
| `legacy` | `prefix(topic): short description`, `commit_trailers: none` | none | messages exactly as before 0.3.3: `docs(sessions): add\|update session 501 log for ...` and a bare `Merge <branch>` |
| `refuse` | as `hook` | as `hook`, plus merge commits need `Ticket: BENCH-1`, which the manifest lacks | log commit passes; the merge is refused and left mid-merge for the user, not aborted, not bypassed |

The hook reads `git interpret-trailers --parse`, not a grep of the message, so
trailers split across paragraphs (one `-m` per trailer) fail it. Only the last
paragraph of a message is a trailer block.

**Run:** a fresh agent executes `session-end` against the repo, authorized to
confirm the one merge gate and nothing else. It is told where the kit root is,
since the skill delegates to sibling skills and a forge preset. No `gh`, no
remote.

**Expected** (`assert.sh <repo> <mode>`): see the table. `hook` and `legacy` also
require the branch and worktree gone and no merge in progress. `refuse` requires
`MERGE_HEAD` set to the branch tip, no conflicted paths, `main` unmoved, and the
branch kept. An aborted merge is told apart from one never started by
`ORIG_HEAD`, which is per-worktree and which setup never sets in the primary.
Exit 2 (VOID) in `refuse` mode means the run never reached the merge.

**Not asserted:** that the `refuse` report names the completing command
(`git commit -m "Merge <branch>" -m "<trailers>"`). That is a message, not git
state; read it in the transcript.

**Assertion check:** deterministic replays on 2026-09-29. The correct commands
pass every mode. These fail: the pre-0.3.3 messages under `hook`, one `-m` per
trailer under `hook` (the hook refuses the log commit), trailers under `legacy`,
`--no-verify` and `merge --abort` under `refuse`. A `refuse` run that never
merges is VOID.

**Baseline:** 2026-09-29, one fresh Opus 5.5 agent per mode against the 0.3.3
skills. All three PASS. `hook`: log commit `add session 501 log for trailers`
and the merge both accepted by the hook, `<model>` filled as `Opus 5.5`.
`legacy`: `docs(sessions): add session 501 log for trailers` and a bare
`Merge feature/session-501-trailers`. `refuse`: merge left mid-merge, report
named the missing `Ticket: BENCH-1` as a manifest/hook disagreement and gave the
completing `git commit` with it added. No agent added a trailer the manifest did
not name, including the `Claude-Session:` line from its own attribution
instructions.
