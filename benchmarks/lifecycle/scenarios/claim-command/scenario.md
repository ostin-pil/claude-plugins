# Scenario: session-start runs the project's path claim

**Skill:** `session-start`

**Why it exists.** Worktrees keep parallel sessions off one HEAD but not out of
one file. A project that has each session claim the paths it will edit names
the command in `claim_command` (lifecycle-kit 0.3.4), and `session-start` runs
it in the new checkout. The skill already uses "claim" for the session number,
and a refused number is retried at the next one. A refused *path* claim must not
be: retrying it under a new number would leave two sessions where the user asked
for one, and still no claim.

**Setup** (`setup.sh [claim|refuse|none]`): a file remote (offline), one earlier
session log (session 6), and a live concurrent branch,
`feature/session-7-other`, on the remote. A correct run mints 8. The claim
script, `tools/claim.sh`, logs every call (branch and toplevel) in the common
git dir, where the assertion reads it.

| Mode | `claim_command` | Claim script | Expected |
|---|---|---|---|
| `claim` | `"sh tools/claim.sh"` | claims `src/` for the branch it is on | run once, inside the new worktree, on `feature/session-8-*`; `src/` claimed by it |
| `refuse` | as `claim` | refuses: `src/` is held by `feature/session-7-other` | run once; no second session branch; the session 8 worktree kept; the other claim untouched |
| `none` | `none` | as `claim` | the script never runs |

**Run:** a fresh agent executes `session-start` against the repo. The harness
supplies the answer to the skill's one question ("New worktree", topic `bench`),
never the number and never what to do about the claim.

**Expected** (`assert.sh <repo> <mode>`): see the table. Every mode also needs
exactly one new session branch, numbered 8, with its worktree, and a clean
primary checkout. Exit 2 (VOID) means no session branch was created, so the
claim step was never reached.

**Not asserted:** that the `refuse` report shows the script's output and leaves
the choice to the user. That is a message, not git state; read it in the
transcript.

**Assertion check:** deterministic replays on 2026-10-11. The correct commands
pass every mode. These fail: never claiming and claiming from the primary
checkout under `claim`; retrying at session 9, removing the worktree, and
claiming twice under `refuse`; claiming anyway under `none`. A run that creates
no branch is VOID.

**Baseline:** 2026-10-11, one fresh Opus 5.5 agent per mode against the 0.3.4
skill. All three PASS. Each minted 8 past the live `feature/session-7-other`,
which has no log. `claim`: the script ran once from the new worktree and printed
`feature/session-8-bench claims: src/`. `refuse`: it ran once, the agent showed
the two lines of refusal verbatim, said the next step was the user's from the
options they named, and kept the worktree. `none`: the agent saw `tools/claim.sh`
in the repo and did not run it, because the manifest does not name it.
