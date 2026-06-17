# claude-plugins

A Claude Code plugin marketplace, hosted as a monorepo. One repo, one place to
add, one CI, shared dev tooling, and atomic changes across plugins that overlap.

## Plugins

| Plugin | Status | What it does |
| --- | --- | --- |
| [`lifecycle-kit`](./lifecycle-kit) | v0.1 | Session lifecycle and reporting skills driven by a per-project manifest |
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

## Before publishing

Pick and add a `license` (omitted for now). The absorbed `prose-mint` keeps its
own `pyproject.toml` and `action.yml`; decide whether its CI/release runs from
this monorepo or stays retired with the old `ostin-pil/ProseMint` repo.
