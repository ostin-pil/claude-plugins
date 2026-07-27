<!-- prose-check: skip ai-attribution, banlist -->
# prose-mint

A linter for the structural tells of AI-flavored prose. It scans markdown for em dashes, ASCII arrows, "it's not X, it's Y" and its sibling clichés, bold-colon openers used as a definition-list surrogate, AI attribution boilerplate (the "Generated with Claude Code" footer, a bare 🤖 line, Co-Authored-By trailers), and paragraphs that were hard-wrapped instead of left for the renderer to wrap.

This started inside one project (Untype) as `bin/check-prose.sh` plus a Claude Code skill and a CI gate. It worked, but it was trapped in that repo: using it elsewhere meant copying files and hand-editing scope. prose-mint is the extraction: one engine, several surfaces (CLI, Claude Code plugin, reusable CI action, MCP server), with a shared default ruleset that each project can tune.

## What it does and does not do

It mechanically detects the structural tells above, always on. It also ships a mechanized banned-word and banned-phrase list (words like "delve", "leverage", "seamless"), but that is **off by default and opt-in** (`[banlist] enabled = true`). The reason is honesty about precision: a matcher cannot tell "navigate" the verb from the figurative tell, so the banlist is false-positive-prone. When on, it defaults to `warn` (reported, never fails `--strict`); a project can set `severity = "error"` to enforce. It skips inline code, blockquotes, fenced code, and a `skip banlist` pragma. What it still does **not** mechanize is the non-regex guidance against self-referential gate or CI-status narration ("prose-gate clean", "all tests green") in PR bodies; that stays a discipline for the author. The structural detectors remain the byte-for-byte port of the source scanner; the banlist is the prose-mint-only layer on top.

The detection logic is a faithful port of the Untype scanner and tracks it as the source evolves: when the source gains a category, prose-mint ports it into the shared default and re-baselines. A frozen corpus of 100+ real documents plus crafted edge cases pins the engine to the current source behavior byte-for-byte; the regression suite fails if it ever drifts.

## Install

Requires Python 3.11+ (the config layer uses the standard-library `tomllib`, which arrived in 3.11). There are no third-party dependencies.

As a command on your PATH, from PyPI:

```
pipx install prose-mint               # or: uv tool install prose-mint
prose-mint scan --file path/to/doc.md
```

Without installing anything, straight from PyPI:

```
uvx prose-mint scan --file path/to/doc.md
```

From a source checkout, no install:

```
bin/prose-mint scan --file path/to/doc.md
```

## Usage

```
prose-mint scan  --file doc.md              # scan one file
prose-mint scan  --stdin --label "PR #5"    # scan piped text (PR bodies, etc.)
prose-mint scan  --file doc.md --json       # structured output for tools
prose-mint scan  --file doc.md --strict     # non-zero exit on any hit
prose-mint scan  --file doc.md --no-config  # ignore any .prose-mint.toml, use defaults
prose-mint bulk  knowledge/ research/       # walk dirs, print a summary table
prose-mint bulk  --exclude '*/archive/*' .  # skip paths by glob
prose-mint unwrap --file doc.md             # join a hard-wrapped paragraph
```

`--config <path>` pins an explicit config; `--no-config` ignores project
config entirely and runs the built-in default ruleset (useful for a canonical,
reproducible scan regardless of where it runs). The two are mutually exclusive.

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

prose-mint ships in the [`claude-plugins`](https://github.com/ostin-pil/claude-plugins) marketplace. Add the marketplace once and the `prose-check` skill, the `/prose-check` command, and the MCP server are available in any project, no per-repo file copying:

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install prose-mint@ostin-pil-plugins
```

The marketplace id (`ostin-pil-plugins`) is the `name` field in the marketplace manifest. The same operations work as `claude plugin marketplace add` / `claude plugin install` on the CLI.

The skill and command resolve `prose-mint` from `PATH` first, then `uvx prose-mint`, so they work whether or not the CLI is installed globally. The MCP server launches via `uvx --from 'prose-mint[mcp]' prose-mint-mcp`, pulling the published package with no fixed checkout path required.

## MCP server

A thin server exposes two read-only tools over the same engine: `scan_text(text, label?)` and `scan_files(paths)`. It is credential-free by design. To lint a Notion page or Google Doc, Claude fetches the content with the MCP you already have connected and pipes the text to `scan_text`; this server holds no Notion or Drive auth. The plugin launches it via `uvx --from 'prose-mint[mcp]' prose-mint-mcp`, so `fastmcp` is an optional extra rather than a core dependency.

On a cold uvx cache the first connect downloads fastmcp and prose-mint, which can overrun Claude Code's MCP connect window and show "Failed to connect" until the cache is warm. Warm it once with `bin/warm-mcp-cache` (or the inline `uvx --from 'prose-mint[mcp]' prose-mint-mcp </dev/null`), then run `/mcp` to reconnect. The CLI and the `/prose-check` skill are unaffected. See issue #8.

### What it reads, and what it never does

You are installing something that reads your files, so here is the whole of it. Every claim below is checkable against [`prose_mint/server.py`](./prose_mint/server.py), which is about a hundred lines.

**What it reads**

- `scan_text(text, ...)` reads the string you hand it. Nothing on disk.
- `scan_files(paths)` reads exactly the paths you list, as UTF-8, one at a time. It does not walk directories, expand globs, or follow a path you did not name.
- For each scanned file it looks for a `.prose-mint.toml`, walking up from that file through its parent directories and stopping at the first one it finds. **This is the one thing it reads that you did not explicitly pass**, and on a deeply nested path the walk can reach above your project root. Pin it with `config_path` (or the CLI's `--config`), or switch the discovery off entirely with `--no-config`.

**What it never does**

- **No network.** The package contains no HTTP client, no socket code, and no telemetry or analytics. `grep -rE "requests|urllib|httpx|socket|telemetry|analytics" prose_mint/` returns nothing. `fastmcp` is the transport for the local stdio connection and is an optional extra.
- **No writes.** Both tools are annotated `readOnlyHint`. Nothing is created, modified, or deleted; findings are advisory and come back as a return value.
- **No credentials.** It authenticates to nothing and stores nothing. `scan_text` exists precisely so the MCP you already trust fetches the content and pipes text in, which is why no Notion or Drive auth lives here.
- **No daemon.** It runs over stdio, launched by the plugin for the session. There is no hosted service and no account.

The reason this section exists: a linter that reads your prose is exactly the kind of tool that should say what it does with it, in a year when MCP servers have shipped surprises.

## CI gate (reusable action)

Any repo gets the gate as one stanza:

```yaml
- uses: actions/checkout@v5
  with:
    fetch-depth: 0
- uses: ostin-pil/claude-plugins/prose-mint@main
```

The action is the `prose-mint` package root inside the public `claude-plugins` monorepo. It sets up Python, installs prose-mint from that checkout, scans the PR's changed markdown, and scans the PR title and body. What counts as in-scope is the consumer repo's `.prose-mint.toml`, not anything hardcoded in the action. It is warn-only by default (findings in the Actions log, no PR comment); set `strict: "true"` to fail the build on a hit. Inputs: `strict`, `scan-pr-body`, `python-version`, `config`. prose-mint dogfoods this action on itself via `uses: ./` in `.github/workflows/prose.yml`.

## Status

prose-mint lives in the [`claude-plugins`](https://github.com/ostin-pil/claude-plugins) monorepo and is published to PyPI as [`prose-mint`](https://pypi.org/project/prose-mint/). Done: the standalone engine and byte-for-byte regression gate, the per-project config layer, the Claude Code plugin (skill, command, marketplace), the MCP server, the reusable CI action, and the opt-in mechanized banlist. A drift guard fails the suite if the upstream Untype scanner (the source of the detection logic) gains a category prose-mint has not ported. See CHANGELOG.md for the phase log.
