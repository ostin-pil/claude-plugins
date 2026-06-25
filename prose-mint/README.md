<!-- prose-check: skip ai-attribution, banlist -->
# prose-mint

A linter for the structural tells of AI-flavored prose. It scans markdown for em dashes, ASCII arrows, "it's not X, it's Y" and its sibling clichés, bold-colon openers used as a definition-list surrogate, AI attribution boilerplate (the "Generated with Claude Code" footer, a bare 🤖 line, Co-Authored-By trailers), and paragraphs that were hard-wrapped instead of left for the renderer to wrap.

This started inside one project (Untype) as `bin/check-prose.sh` plus a Claude Code skill and a CI gate. It worked, but it was trapped in that repo: using it elsewhere meant copying files and hand-editing scope. prose-mint is the extraction: one engine, several surfaces (CLI, Claude Code plugin, reusable CI action, MCP server), with a shared default ruleset that each project can tune.

## What it does and does not do

It mechanically detects the structural tells above, always on. It also ships a mechanized banned-word and banned-phrase list (words like "delve", "leverage", "seamless"), but that is **off by default and opt-in** (`[banlist] enabled = true`). The reason is honesty about precision: a matcher cannot tell "navigate" the verb from the figurative tell, so the banlist is false-positive-prone. When on, it defaults to `warn` (reported, never fails `--strict`); a project can set `severity = "error"` to enforce. It skips inline code, blockquotes, fenced code, and a `skip banlist` pragma. What it still does **not** mechanize is the non-regex guidance against self-referential gate or CI-status narration ("prose-gate clean", "all tests green") in PR bodies; that stays a discipline for the author. The structural detectors remain the byte-for-byte port of the source scanner; the banlist is the prose-mint-only layer on top.

The detection logic is a faithful port of the Untype scanner and tracks it as the source evolves: when the source gains a category, prose-mint ports it into the shared default and re-baselines. A frozen corpus of 100+ real documents plus crafted edge cases pins the engine to the current source behavior byte-for-byte; the regression suite fails if it ever drifts.

## Install

Requires Python 3.11+ (the config layer uses the standard-library `tomllib`, which arrived in 3.11). There are no third-party dependencies.

From a checkout, without installing anything:

```
bin/prose-mint scan --file path/to/doc.md
```

As a command on your PATH:

```
pipx install /path/to/prose-mint      # or: uv tool install /path/to/prose-mint
prose-mint scan --file path/to/doc.md
```

## Usage

```
prose-mint scan  --file doc.md              # scan one file
prose-mint scan  --stdin --label "PR #5"    # scan piped text (PR bodies, etc.)
prose-mint scan  --file doc.md --json       # structured output for tools
prose-mint scan  --file doc.md --strict     # non-zero exit on any hit
prose-mint bulk  knowledge/ research/       # walk dirs, print a summary table
prose-mint bulk  --exclude '*/archive/*' .  # skip paths by glob
prose-mint unwrap --file doc.md             # join a hard-wrapped paragraph
```

Text output and bulk output are byte-for-byte compatible with the original scanner, so a project migrating to prose-mint sees identical findings. `--json` is a new, additive contract and carries the full hit list rather than the human report's first-five truncation.

### Pragmas

A document can opt out of categories with a top-of-file comment:

```
<!-- prose-check: skip em-dash, bold-colon-opener -->
```

Use `skip all` to silence every check. This is meant for structured-data files (trackers, schema tables) where a flagged pattern is the intended format.

### Russian documents

The em dash is ordinary punctuation in Russian, not a machine-text tell. When Cyrillic exceeds 30% of the alphabetic characters, the em-dash check is skipped for that file. Every other check still applies.

## Use it in every project (Claude Code plugin)

The repo is its own single-plugin marketplace. Add it once and the `prose-check` skill, the `/prose-check` command, and the MCP server are available in any project, no per-repo file copying:

```
claude plugin marketplace add ~/Projects/prose-mint
claude plugin install prose-mint@prose-mint
```

The marketplace name comes from `.claude-plugin/marketplace.json`, so the `add` command takes only the path. The same operations work as `/plugin marketplace add` and `/plugin install` from inside a Claude Code session.

The skill and command resolve `prose-mint` from `PATH` first, then a local checkout, so they work whether or not the CLI is installed globally.

Caveat, read before installing: the bundled MCP server is launched by an absolute path to this checkout (`/Users/costa/Projects/prose-mint`) in `plugin/.claude-plugin/plugin.json`. That is the v0 local-only reality, the package is not yet published, and `${CLAUDE_PLUGIN_ROOT}` cannot reach the repo because the Python package lives outside `plugin/`. It works on this machine because the repo lives at that path. If you move or clone the repo elsewhere the MCP server stops starting (the skill and command keep working, since they resolve at runtime). When prose-mint is published, replace that command with the `uvx`/console-script form and the tie disappears.

## MCP server

A thin server exposes two read-only tools over the same engine: `scan_text(text, label?)` and `scan_files(paths)`. It is credential-free by design. To lint a Notion page or Google Doc, Claude fetches the content with the MCP you already have connected and pipes the text to `scan_text`; this server holds no Notion or Drive auth. The plugin launches it via `uvx --from 'prose-mint[mcp]' prose-mint-mcp`, so `fastmcp` is an optional extra rather than a core dependency.

On a cold uvx cache the first connect downloads fastmcp and prose-mint, which can overrun Claude Code's MCP connect window and show "Failed to connect" until the cache is warm. Warm it once with `bin/warm-mcp-cache` (or the inline `uvx --from 'prose-mint[mcp]' prose-mint-mcp </dev/null`), then run `/mcp` to reconnect. The CLI and the `/prose-check` skill are unaffected. See issue #8.

## CI gate (reusable action)

Any repo gets the gate as one stanza. Drop `examples/prose.yml` into `.github/workflows/`:

```yaml
- uses: actions/checkout@v5
  with:
    fetch-depth: 0
- uses: ostin-pil/ProseMint@v1
```

The action lives in the private repo `ostin-pil/ProseMint` (provisional GitHub name; the tool, CLI, and plugin stay `prose-mint`). A consumer repo must have access to it: GitHub only lets a private repo's action run in other repos when same-owner private-action sharing is enabled (Settings, Actions, Access on `ProseMint`). The dogfood `uses: ./` inside this repo always works. The action sets up Python 3.11, installs prose-mint from its own checkout (no PyPI), scans the PR's changed markdown, and scans the PR title and body. What counts as in-scope is the consumer repo's `.prose-mint.toml`, not anything hardcoded in the action. It is warn-only by default (findings in the Actions log, no PR comment); set `strict: "true"` to fail the build on a hit. Inputs: `strict`, `scan-pr-body`, `python-version`, `config`. prose-mint dogfoods this action on itself via `uses: ./` in its own `.github/workflows/prose.yml`.

## Status

The GitHub repo is `ostin-pil/ProseMint` (private, provisional name); the tool, CLI, package, and plugin are `prose-mint` and may be renamed once a final name is chosen. Done: the standalone engine and byte-for-byte regression gate, the per-project config layer, the Claude Code plugin (skill, command, marketplace), the MCP server, the reusable CI action, the opt-in mechanized banlist, and the Untype fallback-chain migration (staged in `staging/untype/`, applied by you on an Untype branch). A drift guard fails the suite if the upstream Untype scanner gains a category prose-mint has not ported. The remaining open thread is renaming away from the provisional name and any future polish. See CHANGELOG.md for the phase log.
