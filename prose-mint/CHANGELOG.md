<!-- prose-check: skip ai-attribution, banlist -->
# Changelog

## Unreleased

Fixed the Windows failures, which were three separate implicit-encoding and platform-default assumptions rather than one.

- `scan` and `bulk` now write UTF-8 regardless of the platform's default encoding. A finding quotes the offending line, so the output carries whatever the document carries, and a redirected stdout on Windows falls back to the ANSI code page. cp1252 cannot encode an ASCII arrow, the robot emoji in an AI-attribution footer, or any Cyrillic, so two of the eight structural categories and every Russian document killed the process with `UnicodeEncodeError` on exactly the input the scanner exists to report. It failed only when redirected, so an interactive run looked healthy while CI and any `| tee` died. The em dash is at 0x97 in cp1252, which is why the most-reported category never crashed and this went unseen.
- `bulk`'s walk order no longer depends on the platform. `sorted()` over `Path` objects compares a case-folded key on Windows and raw bytes on POSIX, so `README.md` sorted before `meeting.md` on Linux and after it on Windows. The walk order is the report's order, so one corpus produced two documents and the byte-for-byte golden was unmatchable on one platform by construction.
- The test suite stopped reading and writing in the platform encoding: sixteen `subprocess.run(..., text=True)` calls decoded child output with the locale encoding, and five `read_text()` calls read UTF-8 fixtures back as cp1252. Golden comparison now normalises path separators, keeping `bulk` output native for the reader while the POSIX-captured fixtures stay portable.
- On Windows the suite goes from 139 passed / 5 failed to 151 passed / 0 failed. Linux behaviour is unchanged; every fix is a no-op where UTF-8 and byte-order sorting are already the default.

Fixed the two phrase rules that could not match the canonical renderings of the constructions they target, found when the frozen corpus was analyzed for the distribution writeup (the crafted edge sampler contains both forms, and neither fired; the byte-stable goldens had captured the miss as expected output).

- `no-X-no-Y-just-Z` no longer requires line-start position and title-case fragments; fragment bounds keep it a slogan detector. It previously had zero detections across the whole corpus.
- `not-X-but-Y` gains the canonical comma arm and drops the "but" arm, whose only detection in 366 measured files was a false positive on natural comparative speech. The em-dash and "rather" arms are retained.
- Goldens regenerated from the fixed source scanner, in lockstep with the same two-line change in Untype (its `fix/prose-phrase-rule-patterns`), keeping the default-equals-source invariant. Net golden delta: the edge sampler gains its two intended hits, one meeting fixture loses the false positive.
- `regen_golden.py` now documents that it must run with HOME and PATH pinned: Untype's `check-prose.sh` is a fallback-chain shim that otherwise resolves to an installed or checked-out prose-mint, making the capture circular.

## 0.1.1 (2026-07-12)

Maintenance release, cut from the `ostin-pil/claude-plugins` monorepo (prose-mint now lives there as a plugin and a reusable action, not in a standalone repo).

- Added a `--no-config` flag to `scan` and `bulk` (mutually exclusive with `--config`) that ignores any ambient `.prose-mint.toml` and runs the built-in default ruleset. The regression suite uses it so the goldens, captured from the config-less source scanner, stay valid regardless of a parent config above the working directory.
- Added `bin/warm-mcp-cache`, a one-shot helper that warms the uvx cache so the MCP server's first in-session connect does not time out on a cold download (issue #8). Documented the warm-up and the `/mcp` reconnect in ADOPTING.md and the README.
- Refreshed the docs for the published package: install and marketplace instructions point at PyPI and the monorepo, and the stale v0 absolute-path MCP caveat is gone. Enriched the package metadata (author, project URLs, MIT classifier) and made the version dynamic from `prose_mint.__version__`.
- Removed `staging/untype/`, the unapplied pre-rename Untype migration, from the package tree. Releases are now published to PyPI by `.github/workflows/release.yml` on a `prose-mint-v*` tag.

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

Promote the opt-in banlist toward a v2 default once its precision is tuned, and keep the structural detectors in sync with the upstream source scanner via the drift guard.
