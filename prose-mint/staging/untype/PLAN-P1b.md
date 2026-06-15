# P1b plan: land the prose-lint fallback-chain shim in Untype

## Goal

Make Untype consume the extracted `prose-lint` instead of carrying its own copy of the scanner, without changing any observable behavior and without breaking CI. After this lands, Untype's `bin/check-prose*.sh` and `bin/unwrap-prose.py` are thin shims; the canonical engine is `prose-lint`.

## Why a shim (not a hard switch)

CI runners have no `prose-lint` installed and installing it there is P3 (the reusable action). The shim resolves `prose-lint` for local dev and falls back to the vendored original for CI, so the migration carries zero CI risk and zero P3 coupling. It is fully reversible.

## Hard constraints (do not violate)

- Untype's `.githooks/pre-commit` refuses commits on `main`. Work rides one feature branch off freshly fetched `origin/main`, one PR per session, with a session log committed before merge (`.claude/rules/workflow.md`).
- The agent must not open the Untype PR, must not edit `.claude/**` (the self-mod classifier blocks it; it is not needed, the shim preserves the `bin/check-prose.sh` interface so the prose-check skill is unchanged).
- Frozen prose-lint fixtures and Untype source docs are never edited.

## Preconditions

- prose-lint is at `~/Projects/prose-lint` (the shims fall back to `~/Projects/prose-lint/bin/prose-lint` when not on PATH).
- `python3 staging/untype/verify_shims.py` in the prose-lint repo prints `SHIM VERIFY OK` (shim-shared == shim-fallback == original, byte for byte). Run it first; if it fails, stop and fix prose-lint, not Untype.

## Steps (you run these)

1. Fresh branch off the remote, per the one-PR-per-session rule:
   ```
   cd ~/Projects/Untype
   git fetch origin
   git switch -c feature/session-<N>-prose-lint-shim origin/main
   ```
2. Apply the staged change (renames originals to `*-impl`, drops in the shims; only moves and copies, never commits):
   ```
   sh ~/Projects/prose-lint/staging/untype/apply.sh
   ```
3. Optional, bulk-only scope (does not affect the CI gate or the skill, which scan single files):
   ```
   cp ~/Projects/prose-lint/staging/untype/prose-lint.toml .prose-lint.toml
   ```
4. Verify in the working tree before committing:
   ```
   git status                                  # 3 renames + 3 shims
   echo "An em dash — here." | bin/check-prose.sh --stdin --label t
   bin/check-prose-bulk.sh knowledge | tail -3  # behaves as before
   ```
   Output must match what Untype produced before the change (it will: prose-lint is byte-identical, proven by the prose-lint regression gate and the shim verify).
5. Commit the code change (atomic), then write the session log `sessions/<date>_session_<N>_prose-lint-shim.md`, then commit that.
6. Open one PR. Let Untype's prose CI gate run; it scans the PR body and changed docs and exercises the fallback path (no `prose-lint` on the runner), which is the vendored original, so it passes as before.
7. Merge per `workflow.md` (`gh pr merge --merge`; the remote MERGED state is the source of truth).

## Rollback

Before committing: `git checkout -- bin/ && git clean -f bin/`, or delete the branch. After merge: revert the PR; the `*-impl` files still contain the exact original logic, so a revert restores the prior state verbatim.

## Verification that it worked

- Untype CI green on the PR (fallback path == original).
- `/prose-check` in Untype still produces identical findings (it calls `bin/check-prose.sh`, now the shim, which locally resolves prose-lint).
- A deliberate em dash in a `knowledge/` doc is still flagged.

## Follow-ups (separate, not part of this PR)

- To make Untype CI use the shared tool instead of the vendored fallback: enable same-owner private-action access on `ProseMint`, tag a `v1`, and switch `.github/workflows/prose.yml` to the reusable action. That is the P3 consumption step, deliberately decoupled.
- Decide the final product name and retire the provisional `ProseMint`.
