# claude-plugins

A Claude Code plugin marketplace, hosted as a monorepo. One repo, one place to
add, one CI, shared dev tooling, and atomic changes across plugins that overlap.

## Plugins

| Plugin | Status | What it does |
| --- | --- | --- |
| [`lifecycle-kit`](./lifecycle-kit) | v0.1 (scaffolded) | Session lifecycle and reporting skills driven by a per-project manifest |
| `prose-mint` | planned | Prose-quality scanner (currently a standalone checkout at `~/Projects/prose-lint`); migrating in is deliberate work because the `check-prose.sh` fallback chain resolves through that path |

## Install (in a consuming project)

Add the marketplace once, then install any plugin from it.

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@claude-plugins
```

The marketplace id is the `name` field in `.claude-plugin/marketplace.json`
(`claude-plugins`). To try it before this repo is on GitHub, add it from the
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
  lifecycle-manifest.template.md
  examples/untype-manifest.md
  README.md
```

## Before publishing

The marketplace and plugin manifests reference `ostin-pil/claude-plugins`; adjust
the `url`, `homepage`, and `repository` fields if the GitHub owner or repo name
differs. Pick and add a `license` (omitted for now). Then create the GitHub repo
and push; consumers add it with `/plugin marketplace add <owner>/<repo>`.
