---
name: prose-check
description: This skill should be used when the user asks to "prose-check", "scan for AI tells", "check this doc/PR for AI-flavored writing", "run prose-mint", mentions em dashes / ASCII arrows / bold-colon openers / "not X but Y" / AI-attribution boilerplate as a writing problem, or wants a markdown file or pull-request body checked before committing or merging. Works in any project once the plugin is installed.
argument-hint: "[path | PR-number] (empty = current branch's PR)"
allowed-tools: [Bash, Read]
version: 0.1.0
---

# prose-check

Scan a markdown file or a pull-request body for structural AI-prose tells
using the shared `prose-mint` tool. Read-only: surface findings, never edit
files or PR bodies, never "fix" silently.

## Resolve the tool

Use the first that works, in order:

1. `prose-mint` on `PATH` (installed via `pipx`/`uv tool install`)
2. `uvx prose-mint` (runs the published package with no install; needs `uv`)

Treat whichever resolves as `<tool>` below. If neither is available, report
that prose-mint is not installed and stop. Do not fall back to guessing or
hand-scanning.

## Run

Parse the argument:

- **Numeric or `#NNN`** (a PR): require `gh`. If `gh` is missing or auth
  fails, report and stop.
  `gh pr view NNN --json title,body -q '.title + "\n\n" + .body' | <tool> scan --stdin --label "PR #NNN"`
- **A path**: `<tool> scan --file <path>`
- **Empty**: resolve the current branch's PR with
  `gh pr view --json number,title,body`. If there is no PR, ask the user
  for a path or PR number rather than guessing.

`prose-mint` auto-discovers the project's `.prose-mint.toml` by walking up
from the target, so per-project scope and thresholds apply automatically.

## Tells the scanner cannot see

`prose-mint` detects patterns with fixed shapes. Three common tells have no
fixed shape, so they need a reading. Check for them by eye whenever reviewing
or writing prose, and raise them the same way the tool raises its own findings.

**One connective doing all the work.** A single contrast pivot, most often
"rather than", reused as the default joint between clauses. Once is fine. Five
times in a document means the relationship between those clauses was never
chosen, only defaulted to. The fix is per-instance: some want "instead of",
some want a full stop, and some want the contrast dropped because both halves
were true and unopposed. Frequency is the signal, so count before judging.

**A reference nobody can resolve.** "Rule 5", "criterion 8", "the third
finding". The writer has the list in front of them; a reader next week does
not, and a reader outside the project never did. Name the thing, quote the
clause, or link it. A number alone is a lookup the reader cannot perform.

**A principle restated in place of evidence.** A sentence that closes a
paragraph by asserting the paragraph's own claim as a general truth, adding
nothing checkable. It reads as emphasis and functions as padding. Shapes to
watch for: "X is the Y this Z exists to prevent", "that is what makes this
work", "which is the whole point". Cut it, or replace it with the concrete
reason: a failure it would cause, an example that breaks, a measurement.

None of these are mechanized. The first is a frequency judgment the current
threshold model cannot express per phrase; the second and third depend on what
a reader already knows.

## Compose long prose in blocks, then merge

When writing or rewriting text content of any length (a PR body, a release
note, a design doc, a report), do not draft it top to bottom in one pass. Write
each paragraph as its own block, against its own brief, and assemble them only
once every block stands up on its own.

The reason is mechanical. Drafting linearly makes each sentence reach for the
one before it, and the reaching is what produces the tells: a connective gets
reused because it worked a paragraph ago, a claim gets restated as a principle
because the paragraph felt thin, a reference gets shortened to a number because
it was spelled out earlier. Blocks break that chain. A paragraph written in
isolation has to carry its own weight, and the crutches become visible when
they are the only thing holding it up.

Practically:

1. List what each paragraph has to do, in a sentence each.
2. Write each one against that brief alone, without reading the neighbours.
3. Concatenate, then read the whole for transitions, repeated connectives, and
   claims that now appear twice.
4. Scan the merged result before publishing it.

This also makes revision cheap. When a reviewer objects to one paragraph, that
paragraph is a unit that can be rewritten without disturbing the rest, which is
what makes "rewrite this section" a small request instead of a rewrite.

## Check a PR body before it is published

CI scans PR bodies with the built-in ruleset, which is not always the project's
own file ruleset: a repo may disable `hard-wrap` for files that wrap at 80
columns by choice, while the body is scanned with it enabled. Run the same
check locally first, on the text you are about to post:

```
cat body.md | <tool> scan --stdin --label "PR #NNN" --strict
```

That is the command the CI action runs, so a clean result here is a clean gate.
Doing this costs one command and saves a red build and a force-push.

## Report

Print the scanner output verbatim. Do not paraphrase or restate the counts
as prose ("gate clean", "0 flagged"); the tool's output is the source of
truth. Then, for the highest-count reported category only, offer up to five
concrete rewrite suggestions. Suggestions only: make no edits unless the
user explicitly asks.
