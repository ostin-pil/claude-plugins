# Apple Foundation Models — summary-quality benchmark

A `UntypeBench` subcommand that compares Apple's on-device Foundation
Models against a cloud baseline (`openrouter:openai/gpt-4o-mini`) on
action-item extraction across a hand-labeled meeting corpus. The result
feeds a pivot-decision trigger.

## Why this exists

The pivot synthesis memo (`pivot-decision-synthesis-2026-05-04.md` §4.2(B)
and §4.3) gates two parked pivots — A3 (privacy-first meeting notes) and
V3 (mobile voice-revision) — on whether Apple FM is good enough that the
"everything stays on your Mac" claim is technically defensible. The named
trigger:

> Apple FM passes the summary-quality benchmark (≥ 70% of GPT-4o quality
> on action-item extraction across 10 fixture meetings).

This harness produces the number that fires that trigger.

### Caveat — baseline is gpt-4o-mini, not full gpt-4o

The synthesis memo cites "GPT-4o" literally. The harness compares against
`openrouter:openai/gpt-4o-mini` (routing through OpenRouter so the bench
reuses the single `UNTYPE_OPENROUTER_KEY` rather than a separate OpenAI
key — pass-through pricing is identical). mini is weaker than full 4o,
so a 70% ratio against mini is an easier bar than 70% against full 4o.
Read the trigger result with that in mind — when the result is read into
the synthesis memo, it should call out the baseline explicitly.

To rerun against full `gpt-4o`, add `openRouterGPT4o = "openrouter:openai/gpt-4o"`
to the `ProviderID` enum and pass `--providers apple:fm-system,openrouter:openai/gpt-4o`.

## How to run

### Pre-flight (no API calls, no FM calls)

```bash
swift run UntypeBench fm-benchmark --dry-run
```

Loads the 10 fixtures from `research/fixtures/meetings/`, parses every
labels file, and exits. Validates that the scaffold is working without
burning API credits or invoking FM.

### Full run

```bash
export UNTYPE_OPENROUTER_KEY=sk-or-...
swift run UntypeBench fm-benchmark
```

Defaults: `--providers apple:fm-system,openrouter:openai/gpt-4o-mini`,
`--fixtures research/fixtures/meetings`, `--out research`.

Output: `research/apple-fm-benchmark-results-YYYY-MM-DD.md` — per-fixture
recall/precision table, aggregate row, trigger verdict (PASSED / FAILED /
INDETERMINATE), and the raw model summary text for each (provider,
fixture) pair.

### Requirements

- macOS 26 on **Apple-Intelligence-eligible hardware** with the feature
  turned on and the FM model downloaded. The current dev Mac is *not*
  eligible (`providerUnavailable: This Mac does not support Apple
  Intelligence.`) — this bench has to be run on a separate machine
  (e.g. an M-series Mac with Apple Intelligence enabled). On ineligible
  hardware the bench logs the reason and skips FM, leaving only the
  cloud baseline run, which is not useful on its own.
- An OpenRouter API key resolved via `UNTYPE_OPENROUTER_KEY` env var or
  the Untype keychain (`openrouter.apiKey` account).
- ~10–30 minutes of wall time (10 fixtures × 2 models × ~30–90 s/call,
  plus scoring).

### Where to run it

This needs to live on a Mac with Apple Intelligence enabled. The
`research/fixtures/meetings/` corpus and the `UntypeBench` source travel
with the repo, so the run is just `git pull && swift run UntypeBench
fm-benchmark` on the eligible machine. Drop the resulting
`apple-fm-benchmark-results-YYYY-MM-DD.md` back into `research/` and
commit from there.

## What the trigger feeds into

When the bench runs, take the aggregate FM-vs-cloud ratio from the report
and append a one-line verdict to `pivot-decision-synthesis-2026-05-04.md`
§4.2(B):

> macOS 26 Apple FM benchmark: PASSED / FAILED at <ratio> against
> gpt-4o-mini on 10-fixture corpus.

**If PASSED:** A3 (privacy meeting notes) and V3 (mobile voice-revision)
both stay viable on the technical axis. The synthesis updates only the
trigger row.

**If FAILED:** A3's privacy positioning is flagged as non-trivial — the
"everything stays on your Mac" claim no longer holds for action-item
extraction quality. V3's Apple-FM gate fires; both pivots get demoted in
the trigger matrix.

## Methodology

- **Fixtures:** synthetic meeting transcripts (no real recordings — see
  `research/fixtures/meetings/README.md` for the privacy rule).
- **Prompt:** pinned in `Sources/UntypeBench/FMBenchmark.swift`. Asks for
  two sections — Action Items and Decisions — with strict formatting and
  no-invention rules.
- **Scoring:** action-item recall and precision via substring containment
  plus Levenshtein similarity ≥ 0.8 (`FMBenchmarkScorer.swift`).
  Per-fixture ratio = FM recall / cloud recall. Aggregate ratio averages
  across fixtures. Decisions and free-form notes are not scored.
- **Why not LLM-as-judge or BLEU/ROUGE:** action-item recall is what the
  synthesis trigger actually gates on. Lexical-overlap metrics measure
  something else; LLM-as-judge adds a third-model dependency without
  changing the >70% / <70% answer.

## Limitations

- **Strict match threshold.** The scorer's 0.8 Levenshtein cutoff plus
  substring containment will miss heavy paraphrases. Example: ground
  truth "Wei sends Lin a note today asking to add Theo to the hiring
  rotation" vs. model output "add Theo to hiring rotation" — both
  criteria miss. Both providers are scored against the same threshold,
  so the FM-vs-cloud *ratio* stays informative; absolute recall may look
  conservative compared to a human-judged baseline. If absolute recall
  matters for downstream decisions, raise the threshold or supplement
  with human review of misses.
- **Single prompt.** The summarization prompt is pinned in
  `FMBenchmark.swift`. Different prompts may favor different models. The
  trigger gates on this specific prompt — change it and the trigger
  number is no longer comparable to prior runs.
- **Synthetic transcripts.** Real meetings have crosstalk, false starts,
  and ambient context. The fixture corpus is clean dialogue. Treat the
  trigger result as a ceiling, not a guarantee, of real-meeting quality.

## Re-run cadence

One-shot decision. Re-run quarterly only if the synthesis triggers ask
for it (e.g. after a macOS update bumps FM model quality), or before any
public-facing privacy claim that depends on this.
