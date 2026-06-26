<!-- prose-check: skip ai-attribution, banlist -->
# Changelog

## Unreleased

Added `bin/warm-mcp-cache`, a one-shot helper that warms the uvx cache so the MCP server's first in-session connect does not time out on a cold download (issue #8). Documented the warm-up and the `/mcp` reconnect in ADOPTING.md and the README, and corrected the README's MCP launch line to the `uvx --from 'prose-mint[mcp]' prose-mint-mcp` form shipped in 0.1.0.

## 0.1.0 (2026-05-20)

First PyPI release, under the final product name **prose-mint** (the provisional `prose-lint` was rejected by PyPI's name-similarity check against the unrelated `proselint`; the rename also retires the "ProseMint" provisional that was hanging over the GitHub repo). Adds a `prose-mint-mcp` console script (`prose_mint.server:main`) and switches the Claude Code plugin's MCP launch to `uvx --from "prose-mint[mcp]" prose-mint-mcp`, retiring the absolute-path-to-local-checkout form documented as the v0 "Caveat, read before installing" in the README. Consumers can now `pipx install prose-mint`, `uv tool install prose-mint`, and install the plugin without cloning the repo to a fixed path. The Python package directory renamed `prose_lint/` to `prose_mint/`; the config file convention is now `.prose-mint.toml` (consumers carrying `.prose-lint.toml` need a one-line rename to keep auto-discovery working). The GitHub repo stays at `ostin-pil/ProseMint` for now; the action ref `uses: ostin-pil/ProseMint@v1` works unchanged.

### P0: standalone repo and behavior-preserving engine

Ported the Untype scanner into a standalone Python package. Detection logic (`engine.py`, `unwrap.py`) is verbatim; only the structure changed so the same analysis drives text, JSON, and bulk surfaces. A frozen corpus of 104 documents (96 real Untype docs plus 8 crafted edge cases) and a regression suite assert the engine reproduces the original scanner's text output byte-for-byte. `--json` is a new additive contract with its own tests.

Execution decisions pinned here:

| Decision | Choice |
|---|---|
| Python floor | 3.11+ (stdlib `tomllib`), runtime guard exits 3 below it |
| Config format | TOML via stdlib `tomllib`, no third-party dependency |
| Install | `pipx` / `uv tool install` console-script, plus a no-install `bin/prose-lint` launcher for source checkouts and CI |
| Positioning | structural-tells linter in v1; banlist advisory until v2; schema reserves the v2 fields |

### P1: per-project config layer

`rules_default.py` (canonical default as data) and `config.py`: `tomllib` discovery walking up from the scan target, deep-merge over the default, explicit `--config`. The engine takes an injected config; the default reproduces the source scanner exactly so every regression test stays unchanged. Bulk honors config scope. `[banlist]` is parsed and merged but inert in v1 with a stderr notice. The Untype migration (P1b) is deliberately deferred to a separate, user-gated step.

### Source sync: ai-attribution

Ported the one category Untype gained after the P0 snapshot (commit `d0a1cb7`): `ai-attribution`, catching the harness-default "Generated with Claude Code" footer, a bare 🤖 line, and Co-Authored-By trailers. It is a universal AI-tell, so it lives in the shared default. The regression golden was re-baselined against the current source scanner (now eight structural categories plus hard-wrap), keeping the gate's invariant "default config equals the source." The non-regex self-referential-status rule the source added alongside it stays advisory, like the banlist. Corpus is now 105 documents.

### P2 + P4: Claude Code plugin and MCP server

One plugin covers both surfaces. The repo doubles as a personal single-plugin marketplace (`.claude-plugin/marketplace.json` pointing at `./plugin`); installing it makes the `prose-check` skill, the `/prose-check` command, and the MCP server available in every project without per-repo copying. The skill and command resolve the `prose-lint` CLI from PATH then a local checkout. The MCP server (`prose_lint/server.py`, FastMCP) exposes read-only `scan_text` and `scan_files` over the in-process engine; it is credential-free, so Notion or Google Docs linting is done by composition (Claude fetches with the connected MCP, pipes text to `scan_text`). `fastmcp` is an optional extra, launched by the plugin via `uv run --with fastmcp`, so the core stays zero-dependency. Tool bodies are tested as plain functions in the dep-free suite (134 tests); an in-memory FastMCP client smoke verifies the wiring under uv.

### P3: reusable CI action

`action.yml` is a composite GitHub Action: set up Python 3.11, install prose-lint from its own checkout (`github.action_path`, no PyPI), scan the PR's changed non-deleted markdown, and scan the PR title+body. Scope is the consumer repo's `.prose-lint.toml`, not hardcoded paths (the one place the original Untype workflow was project-specific). Warn-only by default (log only, no PR comment, preserving the Untype decision); `strict: "true"` fails the build. `examples/prose.yml` is the one-stanza drop-in; prose-lint dogfoods the action on itself via `uses: ./`. `smoke_action.py` parses the manifests and runs the scan pipeline against a throwaway git repo, proving consumer-config scoping and the strict exit flow.

### P1b: Untype fallback-chain migration (staged)

`staging/untype/` holds the shims, `apply.sh`, an optional bulk-only `.prose-lint.toml`, and `verify_shims.py`. The shims resolve prose-lint (PATH, then local checkout) and fall back to the vendored original, so Untype CI keeps working with no `prose.yml` change and no P3 coupling. `verify_shims.py` proves shim(shared) equals shim(fallback) equals original byte-for-byte for scan, bulk, and unwrap. Not applied to Untype: the user runs `apply.sh` on an Untype feature branch and opens the one PR; `.claude/` is untouched (the skill interface is preserved).

### P5: mechanized banlist (opt-in)

The banlist is implemented and ships with content (the prose-style.md word and phrase list), but it is off by default. Turn it on with `[banlist] enabled = true`. It is opt-in because a mechanical matcher cannot disambiguate word sense, so it is false-positive-prone; default severity is `warn` (reported, never fails `--strict`), and a project can set `error` to enforce. Matching is whole-word and case-insensitive (no inflections), skips inline code spans, blockquotes, fenced code, and a `skip banlist` pragma. Off by default means it is not even a category, so the structural byte-for-byte regression gate is unaffected (all 105 cases still pass). The naming stays honest: structural detectors are the source port; the banlist is the prose-lint-only layer.

### Planned

Rename away from the provisional "ProseMint" repo name once a final name is chosen.
