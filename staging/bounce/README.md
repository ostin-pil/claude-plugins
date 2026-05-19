<!-- prose-check: skip ai-attribution -->
# Bounce migration (staged, not applied)

This directory is the P1b fallback-chain flip for Bounce, ready for you to land. Nothing here has touched the Bounce repo. I do not open the Bounce PR and I do not edit `.claude/` (the self-mod classifier blocks it and it is not needed: the shim keeps the `bin/check-prose.sh` interface, so the prose-check skill works unchanged).

## What it does

`bin/check-prose.sh`, `bin/check-prose-bulk.sh`, and `bin/unwrap-prose.py` become thin shims that resolve, in order: `prose-lint` on PATH, then `~/Projects/prose-lint/bin/prose-lint`, then the vendored original (the current scripts, renamed to `*-impl`). Local dev gets the shared tool. CI, which has no `prose-lint`, hits the vendored original and behaves exactly as before, so `prose.yml` needs no change and does not break. This is why the flip does not depend on P3.

## Why it is safe

`verify_shims.py` builds a sandbox from your current Bounce scripts and proves the shim is byte-identical across all three paths (shared tool, fallback, original) for scan, bulk, and unwrap. prose-lint itself is already proven byte-identical to the source by the P0 regression gate and the real-repo dogfood. The optional `.prose-lint.toml` is limited to `[scope]`, which affects only `prose-lint bulk <dir>`, not the single-file scans the CI gate and skill run, so it cannot change gate output.

## How to land it (your steps)

```
cd ~/Projects/Bounce
git fetch origin
git switch -c feature/session-<N>-prose-lint-shim origin/main
sh ~/Projects/prose-lint/staging/bounce/apply.sh
# optional: cp ~/Projects/prose-lint/staging/bounce/prose-lint.toml .prose-lint.toml
git status                       # review the renames + shims
# commit, write sessions/<date>_session_<N>_prose-lint-shim.md,
# open one PR, let the Bounce prose CI gate run, merge per workflow.md
```

`apply.sh` refuses to run on `main` and only renames and copies; you commit and open the one PR. To back out before committing: `git checkout -- bin/ && git clean -f bin/`, or just delete the branch.

## Follow-up after this lands

To later make Bounce CI use the shared tool too (instead of the vendored fallback), the action `ostin-pil/ProseMint@v1` must be reachable from Bounce: enable same-owner private-action access on the ProseMint repo, and tag a `v1`. Until then the fallback keeps CI correct with zero coupling.
