# claude-plugins

A Claude Code plugin marketplace, hosted as a monorepo. One repo, one place to
add, one CI, shared dev tooling, and atomic changes across plugins that overlap.

**What you get in 30 seconds:** three installable plugins that cover the parts of a
working session Claude Code leaves to you. Gated session logs and PR finalize
(`lifecycle-kit`), a linter for the structural tells of AI-flavored prose
(`prose-mint`), and knowledge-base upkeep (`knowledge-kit`). Add the marketplace once,
install what you want, skip the rest.

## Plugins

| Plugin | Status | What it does |
| --- | --- | --- |
| [`lifecycle-kit`](./lifecycle-kit) | v0.1 | Session lifecycle and reporting skills on a per-project manifest: build/test-gated PR finalize, safe-under-ambiguity, session logs, and status reports (the parts built-in worktrees leave out) |
| [`prose-mint`](./prose-mint) | v0.1 (absorbed from `ostin-pil/ProseMint`, history preserved) | Structural-tells linter for AI-flavored prose; ships the `prose-check` skill, a `/prose-check` command, and an MCP server. The plugin is `prose-mint/plugin`; the Python tool and tests sit alongside it |
| [`knowledge-kit`](./knowledge-kit) | v0.1 | Knowledge-base skills on the same manifest: `knowledge-audit`, `issues`, `session-archive`. Ships a knowledge-skeleton template and the two git-hook templates |

New to all three? [`ADOPTING.md`](./ADOPTING.md) is the end-to-end setup flow for a repo.

## Mods

Four small Claude Code mods live under [`mods/`](./mods). Each is a hooks module that draws a
row above the prompt or adds a status-line entry, and none needs a manifest. Install any of
them on its own.

| Mod | What it shows |
| --- | --- |
| [`context-effort`](./mods/context-effort) | How full the context window is, and the reasoning effort the model is running at |
| [`plan-meter`](./mods/plan-meter) | The subscription's 5-hour and weekly usage, with warnings near the limits and a per-model ledger (`/meter`) |
| [`agent-count`](./mods/agent-count) | How many sub-agents actually ran, nested ones included, as a line for a session log (`/agent-count`) |
| [`session-band`](./mods/session-band) | The live parallel sessions in a repo run on `feature/session-<n>-<thread>-<what>` worktrees, with warnings when two share a thread or `main` has moved |

```
/plugin install context-effort --marketplace ostin-pil/claude-plugins
```

The same line installs the others by name. With the marketplace already added, `/plugin install context-effort@ostin-pil-plugins` does it too.

## Install (in a consuming project)

Add the marketplace once, then install any plugin from it.

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@ostin-pil-plugins
/plugin install prose-mint@ostin-pil-plugins
/plugin install knowledge-kit@ostin-pil-plugins
```

The marketplace id is the `name` field in `.claude-plugin/marketplace.json`
(`ostin-pil-plugins`). To work on the plugins locally, add the marketplace from a
checkout instead:

```
/plugin marketplace add ~/Projects/claude-plugins
```

## Layout

```
.claude-plugin/marketplace.json     # lists every plugin in the repo
.github/workflows/prose.yml         # prose gate over the marketplace docs
.prose-mint.toml                    # prose-gate scope + enabled categories
LICENSE                             # MIT
lifecycle-kit/
  .claude-plugin/plugin.json
  skills/<six>/SKILL.md
  hooks/hooks.json + validate-manifest.sh
  rules/workflow.md                 # bundled invariants (zero companion files)
  lifecycle-manifest.template.md
  examples/untype-manifest.md
  README.md
prose-mint/                         # absorbed from ostin-pil/ProseMint (history preserved)
  plugin/                           # the Claude Code plugin (skill, command, MCP)
  prose_mint/ bin/ tests/ ...       # the Python tool
knowledge-kit/
  .claude-plugin/plugin.json
  skills/{knowledge-audit,issues,session-archive}/SKILL.md
  bin/                              # knowledge-audit + session-archive scripts (on PATH when enabled)
  templates/                        # knowledge skeleton, prose-style rule, git hooks
  manifest-keys.md                  # manifest block to append in a consumer
  README.md
mods/{agent-count,context-effort,plan-meter,session-band}/
  .claude-plugin/plugin.json
  hooks/hooks.json + register.tsx   # the hooks module
  types/index.d.ts                  # the mod's state contract
  README.md
ADOPTING.md                         # end-to-end repo setup across all three plugins
```

## CI

Two workflows run on every PR. `.github/workflows/tests.yml` runs the
prose-mint pytest suite (the byte-for-byte regression gate and the config,
banlist, JSON, MCP-body, and plugin-manifest tests) across Python 3.11-3.13,
plus `shellcheck` over the bundled shell scripts. `.github/workflows/prose.yml`
runs the bundled prose-mint action over changed markdown, scoped by
`.prose-mint.toml` to the marketplace's user-facing docs (the structural-tell
categories; hard-wrap is off because these docs wrap by choice).

The absorbed `prose-mint` keeps its own `pyproject.toml` and `action.yml`, and
the monorepo vendors it as a plugin and a reusable action (`uses:
./prose-mint`). Its Python package is published to PyPI as
[`prose-mint`](https://pypi.org/project/prose-mint/).

## Tags that predate the subtree merge

Absorbing `ostin-pil/ProseMint` preserved its history and moved every file in
that package one level down. Two annotated tags sit before the move, at the old
root:

| Tag | Commit | Package root at that tag |
| --- | --- | --- |
| `v1` | `aa57678` | `prose_lint/`, at the repo root |
| `v0.1.0` | `7f1edc8` | `prose_mint/`, at the repo root |

Diffing either against `main` the obvious way compares two layouts and reports
the whole package as deleted and re-added:

```
git diff --stat v0.1.0..main             # ~450 stat lines, nearly all path moves
```

Give the diff the subtree on the newer side and it says something:

```
git diff --stat v0.1.0 main:prose-mint   # 24 files
git diff --stat v1     main:prose-mint   # 42 files
```

Both tags are reachable from `main`, so the names are labels and no history
depends on them. Neither is on this repo's remote either; `git ls-remote --tags
origin` lists only `prose-mint-v0.1.1`. They live in clones that also fetched
the ProseMint remote. `prose-mint/CHANGELOG.md` records `v1` as frozen for
consumers on `uses: ostin-pil/ProseMint@v1`, and that ref resolves in the
`ostin-pil/ProseMint` repo rather than here, so a local copy of the tag is not
what keeps it working.

Releases cut from this repo carry the plugin prefix (`prose-mint-v0.1.1`) and
sit at the post-merge layout, so they diff against `main` without any of this.

## License

MIT, see [`LICENSE`](./LICENSE).
