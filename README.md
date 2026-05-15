# prose-lint

A linter for the structural tells of AI-flavored prose. It scans markdown for em dashes, ASCII arrows, "it's not X, it's Y" and its sibling clichés, bold-colon openers used as a definition-list surrogate, and paragraphs that were hard-wrapped instead of left for the renderer to wrap.

This started inside one project (Untype) as `bin/check-prose.sh` plus a Claude Code skill and a CI gate. It worked, but it was trapped in that repo: using it elsewhere meant copying files and hand-editing scope. prose-lint is the extraction: one engine, several surfaces (CLI, Claude Code plugin, reusable CI action, MCP server), with a shared default ruleset that each project can tune.

## What v1 does and does not do

v1 is honest about its scope. It mechanically detects the structural tells above. It does **not** enforce the banned-word and banned-phrase list that a project's prose rule documents (words like "delve", "leverage", "seamless"). That list stays advisory in v1, a discipline for the author, not a check the tool runs. Mechanized banlist enforcement with severity levels and context suppression is planned for v2; the config schema already reserves space for it so v2 lands without reworking projects. Until then, this is a structural-tells linter, and the name on the tin says so.

The detection logic is a faithful port of the original Untype scanner. A frozen corpus of 100+ real documents plus crafted edge cases pins the engine to the source behavior byte-for-byte; the regression suite fails if it ever drifts.

## Install

Requires Python 3.11+ (the config layer uses the standard-library `tomllib`, which arrived in 3.11). There are no third-party dependencies.

From a checkout, without installing anything:

```
bin/prose-lint scan --file path/to/doc.md
```

As a command on your PATH:

```
pipx install /path/to/prose-lint      # or: uv tool install /path/to/prose-lint
prose-lint scan --file path/to/doc.md
```

## Usage

```
prose-lint scan  --file doc.md              # scan one file
prose-lint scan  --stdin --label "PR #5"    # scan piped text (PR bodies, etc.)
prose-lint scan  --file doc.md --json       # structured output for tools
prose-lint scan  --file doc.md --strict     # non-zero exit on any hit
prose-lint bulk  knowledge/ research/       # walk dirs, print a summary table
prose-lint bulk  --exclude '*/archive/*' .  # skip paths by glob
prose-lint unwrap --file doc.md             # join a hard-wrapped paragraph
```

Text output and bulk output are byte-for-byte compatible with the original scanner, so a project migrating to prose-lint sees identical findings. `--json` is a new, additive contract and carries the full hit list rather than the human report's first-five truncation.

### Pragmas

A document can opt out of categories with a top-of-file comment:

```
<!-- prose-check: skip em-dash, bold-colon-opener -->
```

Use `skip all` to silence every check. This is meant for structured-data files (trackers, schema tables) where a flagged pattern is the intended format.

### Russian documents

The em dash is ordinary punctuation in Russian, not a machine-text tell. When Cyrillic exceeds 30% of the alphabetic characters, the em-dash check is skipped for that file. Every other check still applies.

## Status

P0 is done: the standalone engine and the byte-for-byte regression gate. Later phases add the per-project config layer, a Claude Code plugin, a reusable CI action, and a thin MCP server. See CHANGELOG.md for the phase log.
