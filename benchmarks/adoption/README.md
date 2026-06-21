# Adoption benchmark

Tests whether the kit adopts cleanly into an arbitrary fresh repo. Portability
reduces almost entirely to one question: can the adoption flow (`ADOPTING.md`)
correctly infer the three ecosystem-specific manifest fields, `build_commands`,
`test_commands`, and `code_globs`? Everything else the plugins do is
ecosystem-blind (`knowledge-audit` scans Markdown, `session-archive` scans
`~/.claude` transcripts, `prose-mint` scans prose, the lifecycle skills drive
git and GitHub), so the inference of those three values is the real test.

## Layout

- `fixtures/<eco>/` — a minimal but realistic repo for one ecosystem. Nine so
  far: Node, Go, Python, Rust, a Makefile-driven C repo, an npm placeholder-test
  trap, `shell-ops-no-build` (a no-manifest ops repo grown from a real adoption
  probe), `pnpm-workspace` (a pnpm monorepo), and `jvm-gradle` (a Gradle Java
  project). The answer key is in `golden/<eco>.json`.
- `results/<eco>.json` — what an adoption run inferred for that fixture. Written
  by running the inference (a fresh agent following `ADOPTING.md` step 2 against
  the fixture), one JSON object with `product_name`, `build_commands`,
  `test_commands`, `code_globs`.
- `grade.py` — scores `results/` against `fixtures/*/golden.json` and prints a
  per-field report. Exits non-zero on any mismatch.

## Run

1. For each fixture, run the adoption inference against `fixtures/<eco>/` with a
   fresh agent (no prior context) and save its JSON to `results/<eco>.json`.
2. `python3 grade.py`

To test robustness to a cheaper model, pin the inference agents to a weaker
model, save to a parallel results dir, and grade that dir:
`python3 grade.py --results results-sonnet`. A Sonnet 4.6 run lives in
`results-sonnet/` with its report in `RESULTS-sonnet.md`. It first scored 23/24
(the weaker model invented a Python build step); a sharper step-2 instruction in
ADOPTING.md closed that to 24/24, which is the regression-net value of running the
benchmark against a cheaper model.

## What a miss means

A mismatch is a finding about `ADOPTING.md`, not about the fixture: the prompt
did not steer the inference to the right answer for that ecosystem. The fix is
usually a sharper instruction in `ADOPTING.md` step 2 (for example, "Python
projects usually have no build step; set `build_commands` to `none` rather than
inventing one"), after which the benchmark is re-run.

## Golden answers are opinions

The `accept` lists encode reasonable equivalents (`npm test` and `npm run test`,
`go build ./...` and `go build .`). The Python `build_commands` accepts an empty
list, because the discriminating case is whether the inference correctly
declines to invent a build step. Widen the `accept` lists rather than failing a
defensible answer.
