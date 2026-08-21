# Forge preset — forgejo

For self-hosted Forgejo (and Gitea, which shares the v1 API). Uses `curl` and
`jq` rather than a CLI, so nothing extra needs installing beyond `jq` — the
`tea` CLI works too but is not assumed.

**Requires:** `curl`, `jq`, and `$FORGEJO_TOKEN` in the environment (Forgejo →
Settings → Applications → Generate Token, scopes `write:repository`,
`write:issue`). `forge_url` and `forge_repo` are both required, unlike the
`github` preset.

Set once per shell so the verbs stay readable:

```bash
API="<forge_url>/api/v1/repos/<forge_repo>"
AUTH=(-H "Authorization: token $FORGEJO_TOKEN" -H 'Content-Type: application/json')
```

## Verbs

```bash
# pr_find $BRANCH -> "<number> <url>" | empty
# The v1 API has no head filter, so list open PRs and match .head.ref client-side.
curl -fsSL "${AUTH[@]}" "$API/pulls?state=open&limit=50" |
  jq -r --arg b "$BRANCH" '.[] | select(.head.ref == $b) | "\(.number) \(.html_url)"' | head -1

# pr_create $BRANCH $BASE $TITLE $BODYFILE -> "<number> <url>"
jq -Rs --arg h "$BRANCH" --arg b "$BASE" --arg t "$TITLE" \
   '{head:$h, base:$b, title:$t, body:.}' < "$BODYFILE" |
  curl -fsSL "${AUTH[@]}" -X POST -d @- "$API/pulls" |
  jq -r '"\(.number) \(.html_url)"'

# pr_body_get $N -> body
curl -fsSL "${AUTH[@]}" "$API/pulls/$N" | jq -r '.body // ""'

# pr_edit $N $TITLE $BODYFILE
jq -Rs --arg t "$TITLE" '{title:$t, body:.}' < "$BODYFILE" |
  curl -fsSL "${AUTH[@]}" -X PATCH -d @- "$API/pulls/$N" >/dev/null

# pr_state $N -> OPEN | MERGED | CLOSED
# Forgejo splits this across two fields: state is open|closed and merged is a
# separate boolean, so a merged PR reads as "closed". Map merged first or
# phase 4 will refuse to run on a PR that did merge.
curl -fsSL "${AUTH[@]}" "$API/pulls/$N" |
  jq -r 'if .merged then "MERGED" elif .state == "open" then "OPEN" else "CLOSED" end'

# pr_merge $N $STRATEGY
jq -n --arg do "$STRATEGY" '{Do:$do, delete_branch_after_merge:true}' |
  curl -fsSL "${AUTH[@]}" -X POST -d @- "$API/pulls/$N/merge"

# pr_find_merged $BRANCH -> "<number>" | empty
curl -fsSL "${AUTH[@]}" "$API/pulls?state=closed&limit=50" |
  jq -r --arg b "$BRANCH" '.[] | select(.merged == true and .head.ref == $b) | .number' | head -1

# remote_branch_delete $BRANCH
curl -fsSL "${AUTH[@]}" -X DELETE "$API/branches/$BRANCH"

# merge_strategy_ok $STRATEGY -> true | false
curl -fsSL "${AUTH[@]}" "$API" | jq -r --arg s "$STRATEGY" '
  if   $s == "merge"  then .allow_merge_commits
  elif $s == "squash" then .allow_squash_merge
  elif $s == "rebase" then .allow_rebase
  else false end // false'
```

## Differences from `github` that the skills must respect

- **`pr_merge` deletes the remote branch itself** via
  `delete_branch_after_merge`, and unlike gh's `--delete-branch` it does no
  local cleanup at all — so it never hits gh's cross-worktree abort. Phase 4's
  `remote_branch_delete` is still correct to run: it is written
  assert-then-reconcile and no-ops when the branch is already gone.
- **`-f` makes curl exit non-zero on HTTP errors**, which is what the skills'
  abort-on-failure steps expect. Keep it on every call.
- **Token in the environment, not a config file.** If `$FORGEJO_TOKEN` is
  unset, every verb fails with a 401 that looks like a network error. Check it
  before phase 3 rather than debugging mid-merge.
- Forgejo's `Do` accepts `merge`, `squash`, `rebase`, `rebase-merge`, and
  `fast-forward-only`. Only the first three are valid `merge_strategy` values
  in the manifest, and they map straight through.
