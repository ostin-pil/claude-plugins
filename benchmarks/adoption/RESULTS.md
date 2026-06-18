# Adoption benchmark — baseline run

Fixtures inferred by fresh general-purpose agents (no prior context) following ADOPTING.md as written. Run 2026-06-18.

# Adoption inference benchmark

## go (go) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `gadget` | gadget |
| build_commands | PASS | `go build ./...` | go build ./... | go build . |
| test_commands | PASS | `go test ./...` | go test ./... | go test ./... -count=1 |
| code_globs | PASS | `go` | ext: go |

## makefile-c (c-makefile) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `thing` | thing | makefile-c |
| build_commands | PASS | `make build` | make | make build |
| test_commands | PASS | `make test` | make test |
| code_globs | PASS | `c, h` | ext: c |

## node (node-typescript) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `widget` | widget |
| build_commands | PASS | `npm run build` | npm run build |
| test_commands | PASS | `npm test` | npm test | npm run test |
| code_globs | PASS | `ts` | ext: ts |

## npmdefault (node-no-real-test) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `thinger` | thinger |
| build_commands | PASS | `npm run build` | npm run build |
| test_commands | PASS | `` | (none) | none |
| code_globs | PASS | `ts` | ext: ts |

## python (python-pyproject) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `sprocket` | sprocket |
| build_commands | PASS | `python -m build` | (none) | python -m build | none |
| test_commands | PASS | `pytest` | pytest | python -m pytest |
| code_globs | PASS | `py` | ext: py |

## rust (rust-cargo) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `cog` | cog |
| build_commands | PASS | `cargo build` | cargo build |
| test_commands | PASS | `cargo test` | cargo test |
| code_globs | PASS | `rs` | ext: rs |

---

**Total: 24/24 fields across 6 fixtures.**
