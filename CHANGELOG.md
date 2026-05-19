<!-- prose-check: skip ai-attribution -->
# Changelog

## Unreleased

### P0: standalone repo and behavior-preserving engine

Ported the Untype/Bounce scanner into a standalone Python package. Detection logic (`engine.py`, `unwrap.py`) is verbatim; only the structure changed so the same analysis drives text, JSON, and bulk surfaces. A frozen corpus of 104 documents (96 real Untype docs plus 8 crafted edge cases) and a regression suite assert the engine reproduces the original scanner's text output byte-for-byte. `--json` is a new additive contract with its own tests.

Execution decisions pinned here:

| Decision | Choice |
|---|---|
| Python floor | 3.11+ (stdlib `tomllib`), runtime guard exits 3 below it |
| Config format | TOML via stdlib `tomllib`, no third-party dependency |
| Install | `pipx` / `uv tool install` console-script, plus a no-install `bin/prose-lint` launcher for source checkouts and CI |
| Positioning | structural-tells linter in v1; banlist advisory until v2; schema reserves the v2 fields |

### P1: per-project config layer

`rules_default.py` (canonical default as data) and `config.py`: `tomllib` discovery walking up from the scan target, deep-merge over the default, explicit `--config`. The engine takes an injected config; the default reproduces the source scanner exactly so every regression test stays unchanged. Bulk honors config scope. `[banlist]` is parsed and merged but inert in v1 with a stderr notice. The Bounce migration (P1b) is deliberately deferred to a separate, user-gated step.

### Source sync: ai-attribution

Ported the one category Untype gained after the P0 snapshot (commit `d0a1cb7`): `ai-attribution`, catching the harness-default "Generated with Claude Code" footer, a bare 🤖 line, and Co-Authored-By trailers. It is a universal AI-tell, so it lives in the shared default. The regression golden was re-baselined against the current source scanner (now eight structural categories plus hard-wrap), keeping the gate's invariant "default config equals the source." The non-regex self-referential-status rule the source added alongside it stays advisory, like the banlist. Corpus is now 105 documents.

### P2 + P4: Claude Code plugin and MCP server

One plugin covers both surfaces. The repo doubles as a personal single-plugin marketplace (`.claude-plugin/marketplace.json` pointing at `./plugin`); installing it makes the `prose-check` skill, the `/prose-check` command, and the MCP server available in every project without per-repo copying. The skill and command resolve the `prose-lint` CLI from PATH then a local checkout. The MCP server (`prose_lint/server.py`, FastMCP) exposes read-only `scan_text` and `scan_files` over the in-process engine; it is credential-free, so Notion or Google Docs linting is done by composition (Claude fetches with the connected MCP, pipes text to `scan_text`). `fastmcp` is an optional extra, launched by the plugin via `uv run --with fastmcp`, so the core stays zero-dependency. Tool bodies are tested as plain functions in the dep-free suite (134 tests); an in-memory FastMCP client smoke verifies the wiring under uv.

### P3: reusable CI action

`action.yml` is a composite GitHub Action: set up Python 3.11, install prose-lint from its own checkout (`github.action_path`, no PyPI), scan the PR's changed non-deleted markdown, and scan the PR title+body. Scope is the consumer repo's `.prose-lint.toml`, not hardcoded paths (the one place the original Bounce workflow was project-specific). Warn-only by default (log only, no PR comment, preserving the Bounce decision); `strict: "true"` fails the build. `examples/prose.yml` is the one-stanza drop-in; prose-lint dogfoods the action on itself via `uses: ./`. `smoke_action.py` parses the manifests and runs the scan pipeline against a throwaway git repo, proving consumer-config scoping and the strict exit flow.

### Planned

P1b Bounce migration (fallback-chain shim, staged for a Bounce session), P5 mechanized banlist (the v2 positioning flip).
