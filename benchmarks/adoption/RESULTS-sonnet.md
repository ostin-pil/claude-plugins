# Adoption benchmark — weaker-model run (Sonnet 4.6)

The same six fixtures inferred by fresh `general-purpose` agents pinned to
`claude-sonnet-4-6` (no prior context), following ADOPTING.md as written. Run
2026-06-18. Results in `results-sonnet/`; grade with
`python3 grade.py --results results-sonnet`. The baseline (stronger-model) run is
`RESULTS.md` / `results/`, which scored 24/24.

The point of this run: ADOPTING.md is the only ecosystem-aware surface in the
kit, so the question is whether its inference instructions are robust to a
cheaper model. They mostly are. One field regressed.

## The one regression

`python` `build_commands`: Sonnet inferred `pip install -e .`; the baseline
correctly declined (an empty list). This fixture exists precisely to test whether
the inference invents a Python build step, and the weaker model did. An editable
install is not a build, and the manifest's `build_commands` is a pre-merge "does
it build" gate, so an invented install command is a real miss, not a defensible
variant. If ADOPTING.md gains a sharper instruction here ("Python projects
usually have no build step; set `build_commands` to none rather than inventing
one"), re-run this to confirm the gap closes. Everything else matched, including
the `npmdefault` placeholder-test trap (Sonnet correctly returned no test
command).

## Score

```
## go (go) — 4/4
## makefile-c (c-makefile) — 4/4
## node (node-typescript) — 4/4
## npmdefault (node-no-real-test) — 4/4
## python (python-pyproject) — 3/4   build_commands MISS: `pip install -e .` (should decline)
## rust (rust-cargo) — 4/4

Total: 23/24 fields across 6 fixtures.
```
