# Adoption benchmark — weaker-model run (Sonnet 4.6)

The same six fixtures inferred by fresh `general-purpose` agents pinned to
`claude-sonnet-4-6` (no prior context), following ADOPTING.md. Results in
`results-sonnet/`; grade with `python3 grade.py --results results-sonnet`. The
baseline (stronger-model) run is `RESULTS.md` / `results/`.

This run is what motivated the step-2 sharpening in ADOPTING.md. The point: that
guide is the only ecosystem-aware surface in the kit, so the question is whether
its inference instructions hold up on a cheaper model.

## What the first run found, and the fix

On the first run (ADOPTING.md as originally written) Sonnet scored 23/24. The one
miss was `python` `build_commands`: it inferred `pip install -e .` where the
baseline correctly declined. That fixture exists precisely to test whether the
inference invents a Python build step, and the weaker model did. An editable
install is setup, not a build, so it was a real miss.

The fix was a sharper step-2 instruction: "Not every project has a real build
step or a real test step; when there is none, set that field to `none` rather
than inventing one," with the editable-install case called out by name. After
that change, Sonnet returns an empty `build_commands` for the Python fixture and
scores 24/24, with no over-correction on the four fixtures that do have a real
build (go, node, rust, makefile-c still infer theirs).

## Score (Sonnet, after the sharpening)

```
## go (go) — 4/4
## makefile-c (c-makefile) — 4/4
## node (node-typescript) — 4/4
## npmdefault (node-no-real-test) — 4/4   (placeholder test correctly declined)
## python (python-pyproject) — 4/4        (build correctly declined; was the lone miss)
## rust (rust-cargo) — 4/4
## shell-ops-no-build — 4/4               (no-manifest ops repo; build declined, test=none like Opus)

Total: 28/28 fields across 7 fixtures.
```

The `shell-ops-no-build` fixture (added 2026-06-20 from a real adoption probe) grades the same on both models: build correctly declined, `test_commands` set to `none`. See `RESULTS.md` for the open observation about a linter gate.
