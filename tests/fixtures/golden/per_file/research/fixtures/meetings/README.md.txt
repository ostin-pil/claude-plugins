prose-check: research/fixtures/meetings/README.md

[em-dash] 7 hit(s):
10:- `meeting-NN-<slug>.md` — synthetic transcript, ~500–1000 words, in
12:- `meeting-NN-<slug>.labels.json` — ground-truth labels:
13:  - `action_items` — concrete, ownable items the model is expected to extract.
16:  - `decisions` — explicit decisions stated in the meeting.
17:  - `notes` — free-form context that wouldn't be scored as an action item

[hard-wrap] 7 hit(s) — paragraphs broken across short lines; let the renderer wrap:
4:the Apple FM summary-quality benchmark in `Sources/UntypeBench/FMBenchmark.swift`.
21:design review, retro, hiring debrief, client kickoff, all-hands follow-up,
27:clear, ownable action items so the ground-truth labels are unambiguous.
28:Each action item in `labels.json` was hand-extracted from the transcript
32:plus character-level Levenshtein similarity (≥ 0.8) to match model output

total flagged lines: 14
