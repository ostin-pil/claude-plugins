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

### Planned

P1b Bounce migration (user-gated), P2 Claude Code plugin, P3 reusable CI action, P4 thin MCP server, P5 mechanized banlist (the v2 positioning flip).
