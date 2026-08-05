---
name: finalize-worktree
description: Merge a feature-branch session (worktree or branch-only) into main via one merge-commit PR, then clean up
allowed-tools: Bash Read Grep Glob AskUserQuestion Agent
---

Finalize a session: verify it is clean and mergeable, land it on `main`
through exactly one merge-commit PR, fast-forward the local `main` ref
from `origin/main`, then delete the branch (and, if the session ran in a
worktree, remove the worktree). Handles both shapes a session can take
under `.claude/rules/workflow.md`: an isolated `feature/*` worktree, or a
`feature/*` branch checked out in the primary tree with no worktree.

It never merges locally. It pushes the session branch itself with a normal,
non-force push; the one human checkpoint is an explicit confirmation before
the PR is merged. Everything else goes through `gh`. The fix for the
local-vs-`origin/main` divergence (ISS-W3) is the never-merge-locally
discipline, independent of remote merge strategy: local `main` only ever
fast-forwards from `origin/main` after the remote merge, so it cannot
diverge from the GitHub result. The PR is merged with `--merge` (a merge
commit), which keeps the merged branch tip a real ancestor of
`origin/main` so the local branch deletes with a self-verifying
`git branch -d`, never a forced `-D`.

## Project configuration

The manifest is this skill's configuration. If
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md` does not exist, the
project has not adopted the kit: say so, offer to create it, and stop. Never infer
the keys and run anyway. The kit ships the template as
`lifecycle-manifest.template.md`; locate the installed copy with
`find ~/.claude/plugins -path '*lifecycle-kit*' -name lifecycle-manifest.template.md | head -1`.
The marketplace's `ADOPTING.md` carries a repo-inspecting setup prompt.

Read `.claude/lifecycle-manifest.md` first (resolve it via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a
step below names a manifest key in `code font` (`build_commands`,
`test_commands`, `subpkg_guard`, `merge_strategy`, `pr_base`, `branch_glob`,
`branch_pattern`, `prose_gate`, `code_reviewer`, `review_command`, `log_dir`,
`log_presence_regex`), substitute that key's value; the manifest is the single
source of truth for them. The git commands below write the refs as `<key>`
placeholders (`<integration_ref>`, `<local_main>`, `<remote>`); replace each
with the manifest value before running. The surrounding prose still names
`origin/main` and `main` with Untype's values for readability. Incident
references ("session 85", "finding 3") are documentation of why a guard
exists, not configuration.

## Arguments

- No arguments: detect the session from context (phase 1). With exactly
  one finalize candidate this is unambiguous; with more than one the
  skill does not guess (see phase 1 step 2).
- `$ARGUMENTS` = worktree path or branch name — target that specific
  worktree or branch.
- `--skip-build` anywhere in `$ARGUMENTS`: skip the build/test preflight.
  `/session-end` passes this because its phase 1 already gated build/test.
  When invoked standalone without it, the build/test preflight runs.
- `--review` anywhere in `$ARGUMENTS`: auto-dispatch the committed
  `code_reviewer` subagent on the branch diff before the PR (phase 2 step
  6). Without it, the skill only prints a recommendation to run
  `review_command` by hand. Either way the review is advisory; it never
  blocks the merge.

## Preconditions

Abort with a clear message if any of the following is true. Do **not** attempt to fix them — leave that to the user, since each has multiple valid responses:

1. No `branch_glob` session can be found (no `branch_glob` worktree and the primary tree is not on a `branch_glob` branch)
2. Branch does not match `branch_pattern` (refuse to finalize `main` or other protected refs)
3. Session tree has uncommitted changes (`git status --porcelain` non-empty), session log included — the log must already be committed onto this branch (one-PR-per-session: the log rides this PR)
4. Branch has zero commits ahead of `origin/main` (nothing to merge)
5. No session log for today matching the manifest's `log_pattern` under `log_dir` (`sessions/YYYY-MM-DD_session*.md` for Untype) is present in the branch's commits (`<integration_ref>..HEAD`)

In **worktree mode** the primary worktree's state is **not** a
precondition: the skill never touches the primary working tree, it only
fast-forwards the `main` ref after the remote merge, so the primary
checkout may be on any branch with work in progress. In **branch-only
mode** the primary tree *is* the target, so precondition 3 (clean tree,
session log already committed) applies to it; `/session-end` phase 2.5
has already committed the log and stopped on any other dirt, so this
holds in the normal flow.

## Process

Run all checks against the session's tree (`$WT`) using `git -C "$WT"`;
in branch-only mode `$WT` is the primary tree. Report each step as it runs.

### Phase 1 — Detect the session shape and the primary path

1. `git worktree list --porcelain` to enumerate worktrees. The **first** `worktree ` line is the primary worktree — record it as `$MAIN`. Do not hardcode a path; the on-disk repo directory name is not the product name.
2. Enumerate **all finalize candidates**: every worktree whose branch matches `branch_glob`, plus `$MAIN` itself if it is on a `branch_glob` branch (a branch-only candidate). A primary tree on `main` or on a branch outside `branch_glob` (e.g. a parallel `chore/*` or `docs/*` session) is **not** a candidate and does not block — ignore it. Then:
   - `$ARGUMENTS` names a worktree path or branch: target exactly that. **worktree mode** if the target is a non-primary worktree, else **branch-only mode**.
   - No `$ARGUMENTS`, exactly one candidate: target it (mode by the same rule).
   - No `$ARGUMENTS`, more than one candidate: **do not guess.** Ask the user which (AskUserQuestion); if running non-interactively (e.g. invoked from `/session-end`), abort and print the candidate list, instructing the caller to pass an explicit target. Auto-picking can push and merge an unrelated parallel session's in-progress work (session 85).
   - Zero candidates: abort (precondition 1).
3. Record `$MODE` (`worktree` or `branch-only`), `$WT` (tree path), `$BRANCH` (branch name).

### Phase 2 — Verify clean and mergeable

1. Confirm `$BRANCH` matches `branch_glob` — abort otherwise.
2. `git -C $WT status --porcelain` — must be empty (precondition 3).
3. `git -C $WT fetch <remote>` then `git -C $WT log <integration_ref>..HEAD --oneline` — must be non-empty (precondition 4).
4. Session log present: `git -C $WT log <integration_ref>..HEAD --name-only --format= | grep '<log_presence_regex>'` must return at least one path (precondition 5). `log_presence_regex` encodes `log_dir` plus `log_pattern`'s date form; it is the manifest's value, not a literal to hand-edit. If missing, stop and tell the user to run `/session-end` first.
5. Build/test preflight, unless `--skip-build` was passed: `cd "$WT"`, then run each entry in `<build_commands>` in order, aborting on the first failure; then each entry in `<test_commands>` in order, same abort rule. The final `test_commands` entry runs only when `subpkg_guard` exists (a path check), so it no-ops cleanly where that sub-package is absent. Skipped when invoked from `/session-end` (its phase 1 owns this gate).
6. **Pre-PR review.** Code review before the PR is advisory and never blocks the merge, so by default this skill recommends it rather than running it. Two paths:
   - **Default**: print one line recommending the user run `review_command` before the push in phase 3 (skip the line if `code_reviewer` is `none`). Nothing is dispatched.
   - **`--review` in `$ARGUMENTS`**: if `code_reviewer` is `none` the project has no reviewer, so print that and skip; otherwise dispatch the committed `code_reviewer` subagent (Untype: `code-reviewer`, at `.claude/agents/code-reviewer.md`) via the Agent tool, scoped to `git -C "$WT"`'s `<integration_ref>...HEAD` (three-dot diff: the branch's own changes), and print its findings inline.
   The review is **advisory and never blocks** — do not abort on findings. The user decides whether a finding earns a fix commit before phase 3 (which is fine: more commits on an open branch ride the same PR). On a docs/config-only diff the subagent returns "no code changes" cheaply, so `--review` is safe to pass unconditionally.

### Phase 3 — Push, PR, merge

1. Push the session branch (non-force). The agent runs this itself. Use the unambiguous `HEAD:` refspec form — a bare branch arg has been split by terminal line-wrap and silently not pushed (session 85):
   ```
   git -C "$WT" push -u <remote> HEAD:<BRANCH>
   ```
   Never force-push (`--force`/`-f` are denied and are never the answer; if a normal push is rejected as non-fast-forward, stop and report). If the push command is denied in this environment (the push allow-rule has not been applied), fall back to emitting that exact line for the user to run with the `!` prefix and wait. Either way, **assert it actually landed** before continuing: `git -C "$WT" ls-remote --heads <remote> "$BRANCH"` is non-empty and its SHA equals `git -C "$WT" rev-parse HEAD`. If not, the push did not land — retry (or re-emit the line) and wait; do not proceed to the PR.
2. Detect or create the PR. `gh pr view "$BRANCH" --json number,url` if it exists; otherwise `gh pr create --base <pr_base> --head "$BRANCH"` (`pr_base` is `main` for Untype) with a title following the project PR-title convention (`CLAUDE.md` §Commits: `prefix(topic): short description`, never a narrative `Session N: ...` title) and a body that leads with a one-paragraph summary, then lists the branch's commit titles (`git -C $WT log <integration_ref>..HEAD --format='%s'`). If the PR already exists with a wrong title, fix it by REST PATCH (`gh api ... -X PATCH -f title=...`, see step 3), never `gh pr edit`.
3. Prose-check the PR body before merging (prose rule; finalize creates the PR so it owns this scan). If `prose_gate` is `none`, the project has no prose gate; skip this step and merge without it. Otherwise the gate is the manifest's `prose_gate` (Untype: `bin/check-prose.sh`):
   ```bash
   gh pr view <n> --json body -q .body | "$(git rev-parse --show-toplevel)/<prose_gate>" --stdin --strict --label "PR #<n>"
   ```
   `--strict` makes the scan exit non-zero on any hit (without it the scan prints findings but exits 0, leaving the re-scan loop no termination signal to test). On a non-zero exit, rewrite the corrected body to a temp file and PATCH it via REST — not `gh pr edit`, which issues a GraphQL `projectCards` query that errors under the GitHub Projects-classic sunset (sessions 82–83). The same REST PATCH sets the title (`-f title=...`), so use it for any title fix on an existing PR too:
   ```bash
   gh api repos/{owner}/{repo}/pulls/<n> -X PATCH -f title="prefix(topic): ..." -F body=@<tmpfile>
   ```
   `gh api` substitutes `{owner}`/`{repo}` from the current repo; `-f` sends a string field and `-F field=@file` sends the file's literal contents, sidestepping multi-line shell quoting. Re-scan until clean.
4. **First check whether the PR already merged.** A prior run can have merged it on GitHub but aborted before phase 4 reconciled locally (gh's cross-worktree `--delete-branch` abort, finding 3), and re-running `/session-end` re-enters this phase. `gh pr view <n> --json state -q .state`: if it is already `MERGED`, do **not** run `gh pr merge` again (it errors on a merged PR) — skip straight to phase 4, which is idempotent and finishes the local reconcile. Only when the state is `OPEN`, **pause for the merge gate**: show the PR URL and a one-line summary, and ask the user to confirm the merge before proceeding. This is the single human checkpoint now that the push is automated; without an explicit confirmation, stop and leave the PR open. On confirmation, merge it with the manifest's `merge_strategy`: `gh pr merge <n> --<merge_strategy> --delete-branch` (Untype: `--merge`). This assumes the repo allows that strategy (for the merge-commit case, check once with `gh repo view --json mergeCommitAllowed`); if the repo disallows it `gh pr merge` fails, so set `merge_strategy` to one the repo allows (`squash`/`rebase`) and note that a squash or rebase tip is then not an ancestor of `origin/main`, which changes the branch-delete safety in phase 4 step 4. The authoritative success signal is the **remote** state, not this command's exit code: confirm `gh pr view <n> --json state -q .state` returns `MERGED`. `--delete-branch`'s local cleanup (checkout default, delete local branch) is best-effort and **aborts before merging back when it cannot `git checkout main`** — e.g. `fatal: 'main' is already used by worktree at ...` when another worktree holds `main` (finding 3, session 85). That abort is **not** a merge failure: the GitHub merge already landed and phase 4 owns (and re-verifies) the local reconcile. Only a genuine **remote** failure is fatal — merge conflicts, required checks red, or PR not `MERGED`: report and stop, do not retry `gh pr merge` (re-merging a merged PR errors) and never force.

### Phase 4 — Reconcile local state to the merged result

Only if phase 3 confirmed the PR is `MERGED` on GitHub. This phase is
**assert-then-reconcile**: it never assumes what `gh` did or did not do
locally (gh's `--delete-branch` is unreliable across worktrees, finding
3). Every step checks actual state and acts only if its target is unmet;
all steps are idempotent and safe to re-run. Mode (`worktree` vs
`branch-only`) changes only step 3.

The worktree is removed **before** the branch it holds is deleted. That order
is load bearing, not cosmetic: git refuses to delete a branch that any worktree
has checked out, so in worktree mode the branch delete cannot succeed until the
worktree is gone. `/cleanup-worktrees` sequences its own removals the same way.

1. `git -C "$MAIN" fetch <remote> --prune` (refresh `origin/main`; prune the deleted remote ref).
2. **Target: local `main` == `origin/main`.** Skip if already equal. Else find the worktree `$M` whose checked-out branch is `main` per `git -C "$MAIN" worktree list` (often `$MAIN`; in branch-only mode gh may have moved a tree onto `main`):
   - `$M` exists: it must fast-forward. First confirm the merge changeset does not intersect `$M`'s dirty or untracked paths (compare `git -C "$M" status --porcelain` against `git -C "$M" diff --name-only <local_main> <integration_ref>`). No intersection and the move is a true fast-forward: `git -C "$M" merge --ff-only <integration_ref>`. Intersection, or not a fast-forward: **stop and report** — a dirty file blocks it or local `main` diverged; never force.
   - No worktree has `main` checked out: `git -C "$MAIN" branch -f <local_main> <integration_ref>` (ref-only; touches no working tree).
3. **Target: worktree gone (worktree mode only).** If `$WT` is not `$MAIN`: `git -C "$MAIN" worktree remove "$WT"` then `git -C "$MAIN" worktree prune`. `worktree remove` fails safe if `$WT` still has local changes (shouldn't, by phase 2). In branch-only mode there is no worktree; skip this step. This precedes the branch delete because `$WT` has `$BRANCH` checked out.
4. **Target: local `$BRANCH` gone.** Requires step 3 to have run: while a worktree holds `$BRANCH`, `git branch -d` fails with `cannot delete branch '<BRANCH>' used by worktree at ...`, which is a checkout conflict rather than a containment signal and must not be read as one. If `git -C "$MAIN" rev-parse --verify --quiet "refs/heads/$BRANCH"` resolves: `git -C "$MAIN" branch -d "$BRANCH"`. With `--merge` the merged tip is a real ancestor of `origin/main`, so `-d` (safe delete) succeeds and **self-verifies**. If `-d` refuses under a `--merge` merge *and* no worktree holds the branch, it is genuinely unmerged: **stop and report; never reach for `-D`**. (If the PR was merged with `--squash` or `--rebase`, the branch tip is not an ancestor of `origin/main`, so `-d` refuses even though the work landed. Then do not force blindly: confirm the PR is `MERGED` and the branch's net diff against `origin/main` is empty (`git -C "$MAIN" diff --quiet <integration_ref> "$BRANCH"`), and only then delete; that containment check replaces `-d`'s self-verification.)
5. **Target: remote `$BRANCH` gone.** If `git -C "$MAIN" ls-remote --heads <remote> "$BRANCH"` is non-empty (gh's `--delete-branch` aborted before deleting it, finding 3): `gh api -X DELETE "repos/{owner}/{repo}/git/refs/heads/$BRANCH"` (REST, no `git push`, no GraphQL).
6. **Verify the end state — all must hold, report any that do not:** `git -C "$MAIN" rev-parse <local_main>` equals `git -C "$MAIN" rev-parse <integration_ref>`; `git -C "$MAIN" branch --list "$BRANCH"` is empty; `git -C "$MAIN" ls-remote --heads <remote> "$BRANCH"` is empty; in worktree mode `git -C "$MAIN" worktree list` no longer mentions `$WT`. Do not paper over a failed check.

## Report format

```
✓ Pushed and merged PR #<n> ($BRANCH, merged into main)
  <integration_ref> now <sha>; local main fast-forwarded to match
✓ Removed worktree $WT                  (worktree mode only)
✓ Branch $BRANCH deleted (remote + local)

One PR for the session. Nothing left unpushed.
```

In branch-only mode the worktree line is omitted; the branch line is the
same `deleted (remote + local)`. Phase 4 reconciles the local tree
itself (assert-then-reconcile); it does not rely on gh's `--delete-branch`.

## Rules

- Never finalize `main`, `master`, or any branch outside `branch_glob`.
- Push the session branch with a normal, non-force push; never force-push (`--force`/`-f` stay denied and are never the answer here). If the push is denied in this environment, fall back to handing the user the `!`-prefixed line. The human checkpoint is the merge gate (phase 3 step 4), not the push.
- Never merge locally — the PR is merged on GitHub (the manifest's `merge_strategy`, `--merge` for Untype); local `main` only fast-forwards from `origin/main`.
- Never force-delete a branch. `--merge` makes the merged tip a real ancestor of `origin/main`, so phase 4's `git branch -d "$BRANCH"` is a safe self-verifying delete; if it refuses, that is a real "not merged" signal — stop, do not override with `-D`. (`/cleanup-worktrees` does use `-D`, and correctly: it deletes only after its own independent `ahead=0` containment proof. The seam is the proof, not the flag — `-D` is permitted only where containment in `main` is already established by other means; finalize's flow has no such precomputed proof, so it must rely on `-d` self-verifying.)
- Never skip hooks (`--no-verify`, etc.); never auto-abort a conflicted or failed merge — leave state for the user.
- The pre-PR review (phase 2 step 6) is advisory: surface findings, never abort or block the merge on them. Build/test (step 5) is the only hard code gate.
- Never run phase 4 unless the PR is confirmed `MERGED` on GitHub (`gh pr view <n> --json state`), not merely that phase 3's command exited 0.
- Phase 4 owns the local reconcile in both modes and never assumes gh's `--delete-branch` succeeded (it is unreliable across worktrees, finding 3). In worktree mode it touches no primary feature work: it only fast-forwards `main` (a ref move, or an ff in whichever tree has `main` checked out) and removes `$WT`. It stops rather than forcing when local `main` cannot fast-forward.
- In branch-only mode there is no worktree; never run `worktree remove` or `worktree prune`.
