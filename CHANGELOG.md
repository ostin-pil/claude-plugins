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

### Planned

P1 config layer and Bounce migration, P2 Claude Code plugin, P3 reusable CI action, P4 thin MCP server, P5 mechanized banlist (the v2 positioning flip).
