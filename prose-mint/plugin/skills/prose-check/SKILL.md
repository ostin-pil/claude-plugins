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

## Report

Print the scanner output verbatim. Do not paraphrase or restate the counts
as prose ("gate clean", "0 flagged"); the tool's output is the source of
truth. Then, for the highest-count reported category only, offer up to five
concrete rewrite suggestions. Suggestions only: make no edits unless the
user explicitly asks.
