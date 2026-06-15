# Meeting fixture corpus

Synthetic meeting transcripts paired with hand-labeled action items. Used by
the Apple FM summary-quality benchmark in `Sources/UntypeBench/FMBenchmark.swift`.

## Files

Each fixture is a pair:

- `meeting-NN-<slug>.md` — synthetic transcript, ~500–1000 words, in
  speaker-tagged dialogue form.
- `meeting-NN-<slug>.labels.json` — ground-truth labels:
  - `action_items` — concrete, ownable items the model is expected to extract.
    5–8 per meeting. Each is written from the transcript verbatim or with
    light paraphrase, in declarative form.
  - `decisions` — explicit decisions stated in the meeting.
  - `notes` — free-form context that wouldn't be scored as an action item
    but is useful for future ground-truth review.

The 10 fixtures span: product review, sales discovery, sprint planning,
design review, retro, hiring debrief, client kickoff, all-hands follow-up,
1:1, board prep.

## Methodology

Transcripts were drafted from realistic meeting agendas and seeded with
clear, ownable action items so the ground-truth labels are unambiguous.
Each action item in `labels.json` was hand-extracted from the transcript
text.

The benchmark scorer (`FMBenchmarkScorer.swift`) uses substring containment
plus character-level Levenshtein similarity (≥ 0.8) to match model output
sentences against these labels — so paraphrased extractions still count,
but a missed item is a missed item.

## Privacy rule

**Synthetic transcripts only. Never commit a real meeting recording or
transcript.**

If a future contributor wants to evaluate the harness against real
meetings, they should:

1. Anonymize the transcript (names, company, deal sizes, dates).
2. Run locally — do not commit the anonymized transcript to this repo.
3. Treat the result as a one-shot data point, not a regression fixture.

This corpus is committed because it's safe to commit: nothing in it
references a real person, company, deal, or system.
