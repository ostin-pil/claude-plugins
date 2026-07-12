# claude-plugins

A Claude Code plugin marketplace, hosted as a monorepo. One repo, one place to
add, one CI, shared dev tooling, and atomic changes across plugins that overlap.

## Plugins

| Plugin | Status | What it does |
| --- | --- | --- |
| [`lifecycle-kit`](./lifecycle-kit) | v0.1 | Session lifecycle and reporting skills on a per-project manifest: build/test-gated PR finalize, safe-under-ambiguity, session logs, and status reports (the parts built-in worktrees leave out) |
| [`prose-mint`](./prose-mint) | v0.1 (absorbed from `ostin-pil/ProseMint`, history preserved) | Structural-tells linter for AI-flavored prose; ships the `prose-check` skill, a `/prose-check` command, and an MCP server. The plugin is `prose-mint/plugin`; the Python tool and tests sit alongside it |
| [`knowledge-kit`](./knowledge-kit) | v0.1 | Knowledge-base skills on the same manifest: `knowledge-audit`, `issues`, `session-archive`. Ships a knowledge-skeleton template and the two git-hook templates |

New to all three? [`ADOPTING.md`](./ADOPTING.md) is the end-to-end setup flow for a repo.

## Install (in a consuming project)

Add the marketplace once, then install any plugin from it.

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@ostin-pil-plugins
/plugin install prose-mint@ostin-pil-plugins
/plugin install knowledge-kit@ostin-pil-plugins
```

The marketplace id is the `name` field in `.claude-plugin/marketplace.json`
(`ostin-pil-plugins`). To try it before this repo is on GitHub, add it from the
local path instead:

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

## License

MIT, see [`LICENSE`](./LICENSE).
