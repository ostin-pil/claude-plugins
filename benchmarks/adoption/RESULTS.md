# Adoption benchmark — baseline run

Fixtures inferred by fresh general-purpose agents (no prior context) following ADOPTING.md. Nine fixtures: the six original hand-built ones (go, makefile-c, node, npmdefault, python, rust), one grown from a real adoption probe (shell-ops-no-build), and two new-ecosystem additions (pnpm-workspace, jvm-gradle). Last run 2026-06-21.

## The no-build shell repo

`shell-ops-no-build` is the first fixture grown from a real adoption (an ops repo with no dependency manifest). It confirms the inference correctly declines a compiler build for a no-manifest repo, and it drove an ADOPTING.md improvement. On the first run both models set `test_commands` to `none`, while the real adoption it came from proposed `shellcheck` as a lint gate (accepted by the user unchanged). `none` is honest, but a linter is the more useful gate for a shell-dominant repo, so ADOPTING.md step 2 gained a shell-specific exception: a shell repo with no test framework uses `shellcheck` over its scripts. After the change both models propose `shellcheck scripts/*.sh`, with no regression on the other decline cases (npmdefault still declines its placeholder test, python still declines its build). The golden now requires a shellcheck variant, so a relapse to `none` is a regression this fixture catches.

## New ecosystems (monorepo and JVM)

`pnpm-workspace` (a two-package pnpm monorepo) and `jvm-gradle` (a Gradle Java project with a wrapper) extend coverage past the original single-package ecosystems. Both pass 4/4 on both models with no finding: the inference picks `pnpm -r build` over `npm run build` from the workspace and lockfile signals, and `./gradlew build` over bare `gradle` when the wrapper is present. These are the mainstream cases a real adoption is most likely to meet next, and the inference already handles them.

# Adoption inference benchmark

## go (go) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `gadget` | gadget |
| build_commands | PASS | `go build ./...` | go build ./... | go build . |
| test_commands | PASS | `go test ./...` | go test ./... | go test ./... -count=1 |
| code_globs | PASS | `go` | ext: go |

## jvm-gradle (jvm-gradle) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `orderservice` | orderservice |
| build_commands | PASS | `./gradlew build` | ./gradlew build | gradle build |
| test_commands | PASS | `./gradlew test` | ./gradlew test | gradle test |
| code_globs | PASS | `java` | ext: java |

## makefile-c (c-makefile) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `thing` | thing | makefile-c |
| build_commands | PASS | `make build` | make | make build |
| test_commands | PASS | `make test` | make test |
| code_globs | PASS | `c` | ext: c |

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

## pnpm-workspace (node-pnpm-workspace) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `acme-platform` | acme-platform |
| build_commands | PASS | `pnpm -r build` | pnpm -r build | pnpm build | pnpm run build |
| test_commands | PASS | `pnpm -r test` | pnpm -r test | pnpm test | pnpm run test |
| code_globs | PASS | `ts` | ext: ts |

## python (python-pyproject) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `sprocket` | sprocket |
| build_commands | PASS | `` | (none) | python -m build | none |
| test_commands | PASS | `pytest` | pytest | python -m pytest |
| code_globs | PASS | `py` | ext: py |

## rust (rust-cargo) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `cog` | cog |
| build_commands | PASS | `cargo build` | cargo build |
| test_commands | PASS | `cargo test` | cargo test |
| code_globs | PASS | `rs` | ext: rs |

## shell-ops-no-build (shell-ops-no-build) — 4/4

| field | verdict | inferred | accepted |
|---|---|---|---|
| product_name | PASS | `meshctl` | meshctl |
| build_commands | PASS | `` | (none) | none |
| test_commands | PASS | `shellcheck scripts/*.sh` | shellcheck variants |
| code_globs | PASS | `sh` | ext: sh |

---

**Total: 36/36 fields across 9 fixtures.**
