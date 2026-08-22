# Forge presets

The lifecycle skills used to call `gh` directly, which pinned the whole
write/finalize half of the kit to GitHub. These presets lift those calls behind
a small verb table so the provider is one manifest key:

```yaml
forge: github        # github | forgejo | none
forge_url: none      # base URL, self-hosted providers only
forge_repo: none     # owner/name on the forge, self-hosted providers only
```

`forge` defaults to `github` when the key is absent, so a manifest written
before this existed keeps working unchanged.

## The verb contract

Every preset implements these nine verbs. **Outputs are normalized** — a skill
reads the same shape whatever the provider is, and never branches on `forge`
itself except where a preset says a phase changes shape.

| Verb | Arguments | Stdout contract |
|---|---|---|
| `pr_find` | `$BRANCH` | `<number> <url>`, or empty if none |
| `pr_create` | `$BRANCH` `$BASE` `$TITLE` `$BODYFILE` | `<number> <url>` |
| `pr_body_get` | `$N` | the body, raw |
| `pr_edit` | `$N` `$TITLE` `$BODYFILE` | nothing; exit 0 on success |
| `pr_state` | `$N` | exactly `OPEN`, `MERGED`, or `CLOSED` |
| `pr_merge` | `$N` `$STRATEGY` | nothing; exit 0 on success |
| `pr_find_merged` | `$BRANCH` | `<number>`, or empty |
| `remote_branch_delete` | `$BRANCH` | nothing; exit 0 on success |
| `merge_strategy_ok` | `$STRATEGY` | `true` or `false` |

`pr_state` is the one that earns its normalization. GitHub returns a single
`state` field; Forgejo returns `state: open|closed` **plus** a separate `merged`
boolean, so a closed-but-merged PR reads as `CLOSED` unless the preset maps it.
Getting that wrong would let phase 4 run against an unmerged branch, which is
the one thing `workflow_rule` says must never happen.

## Choosing a preset

| | `github` | `forgejo` | `none` |
|---|---|---|---|
| Transport | `gh` | `curl` + `jq` | local git only |
| Needs a remote | yes | yes | no |
| PRs | real | real | none — merge gate is local |
| Phase 3 shape | push → PR → merge | push → PR → merge | merge `--no-ff` locally |
| Auth | `gh auth login` | `$FORGEJO_TOKEN` | n/a |

`none` is not a degraded `github`. It is the honest shape for a repo that has
no remote by choice, and it replaces phase 3 rather than stubbing it. See
`none.md` for what that costs.

## Adding a provider

Copy `forgejo.md`, change the endpoints, keep the output contract. The skills
call verbs, so a new preset needs no skill edits. Add its name to the `forge`
enum in `hooks/validate-manifest.sh`.
