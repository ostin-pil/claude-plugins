<!-- prose-check: skip all -->
# Prose Style Rule

A starter policy for user-facing prose: PR descriptions, issue and PR comments,
commit messages, release notes, README, and docs under `knowledge/` and
`research/`. It does not apply to session logs, `.claude/`, code comments, or
structured-data tables. Adapt the scope to the project.

The mechanical subset of this rule (punctuation, structural moves, AI-attribution
boilerplate, hard-wraps) is enforced by the **prose-mint** plugin: run
`/prose-check <path>` or `/prose-check <pr-number>`. The word list and the
positive guidance are judgment calls prose-mint does not police by default.

## Banned punctuation and formatting

- Em dashes (`—`). Use a period, comma, parenthesis, or rephrase.
- ASCII arrows (`→`). Write "to", "leads to", or use a numbered list.
- Bold-term-colon openers (`**Term**: prose`) used as a definition-list
  surrogate. Use a real table or a real sentence. Mark genuine record-schema
  files (trackers) with a `<!-- prose-check: skip bold-colon-opener -->` pragma.
- AI-attribution boilerplate: the "Generated with Claude Code" footer or a bare
  🤖 line, and `Co-Authored-By` trailers, in PR bodies or commit messages. Strip
  them every time.
- Hard-wrapping paragraphs at ~80 columns. One line per paragraph; let the
  renderer wrap.

## Banned structural moves

- "It's not X, it's Y."
- "Not only X, but Y."
- "This isn't about X. It's about Y."
- "No X. No Y. Just Z."

## Banned words and phrases

delve, dive into, navigate (figurative), underscore, leverage, harness (verb),
unpack, pave the way, pivotal, groundbreaking, cutting-edge, transformative,
seamless, robust (as praise), comprehensive (as praise), realm, landscape
(figurative). Phrases: "It's important to note", "When it comes to", "At its
core", "At the end of the day", "plays a crucial role in".

## Judgment calls the scanner cannot make

- **One connective doing all the work.** A single contrast pivot, usually
  "rather than", reused as the default joint between clauses. Once is fine;
  five times in a document means the relationship was defaulted to and never
  chosen. Fix per instance: "instead of", a full stop, or drop the contrast
  when both halves were true and unopposed.
- **A reference nobody can resolve.** "Rule 5", "criterion 8", "the third
  finding". Name it, quote the clause, or link it. A bare number is a lookup
  the reader cannot perform.
- **A principle restated in place of evidence.** A closing sentence that
  asserts the paragraph's own claim as a general truth and adds nothing
  checkable. Replace it with the failure it would cause, an example that
  breaks, or a measurement.

## Writing long prose

Draft paragraph by paragraph against a one-line brief for each, then
concatenate and read the whole for repeated connectives and duplicated claims.
Drafting top to bottom makes each sentence reach for the one before it, and
that reaching is what produces the tells above. Scan the merged result before
publishing it.

## Positive guidance

Lead with the conclusion. Vary sentence length. Use contractions. Drop the
preamble and the summary closing. Be specific and opinionated. Short paragraphs
over bullet lists when prose works.
