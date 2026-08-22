# Forge preset — github

The kit's original behavior, unchanged. Every command below is what the skills
called inline before the verb table existed, so `forge: github` is a no-op
refactor for any project already on GitHub.

**Requires:** `gh` on PATH and authenticated (`gh auth status`). `gh api` fills
`{owner}`/`{repo}` from the current repo, so `forge_url` and `forge_repo` are
unused and should stay `none`.

## Verbs

```bash
# pr_find $BRANCH -> "<number> <url>" | empty
gh pr view "$BRANCH" --json number,url -q '"\(.number) \(.url)"' 2>/dev/null || true

# pr_create $BRANCH $BASE $TITLE $BODYFILE -> "<number> <url>"
gh pr create --base "$BASE" --head "$BRANCH" \
  --title "$TITLE" --body-file "$BODYFILE" >/dev/null &&
gh pr view "$BRANCH" --json number,url -q '"\(.number) \(.url)"'

# pr_body_get $N -> body
gh pr view "$N" --json body -q .body

# pr_edit $N $TITLE $BODYFILE
# REST, never `gh pr edit` — that issues a GraphQL projectCards query which
# errors under the Projects-classic sunset and aborts with nothing changed.
gh api "repos/{owner}/{repo}/pulls/$N" -X PATCH \
  -f title="$TITLE" -F body=@"$BODYFILE" >/dev/null

# pr_state $N -> OPEN | MERGED | CLOSED
gh pr view "$N" --json state -q .state

# pr_merge $N $STRATEGY
gh pr merge "$N" --"$STRATEGY" --delete-branch

# pr_find_merged $BRANCH -> "<number>" | empty
gh pr list --state merged --head "$BRANCH" --json number -q '.[0].number // empty'

# remote_branch_delete $BRANCH
gh api -X DELETE "repos/{owner}/{repo}/git/refs/heads/$BRANCH"

# merge_strategy_ok $STRATEGY -> true | false
case "$STRATEGY" in
  merge)  gh repo view --json mergeCommitAllowed -q .mergeCommitAllowed ;;
  squash) gh repo view --json squashMergeAllowed -q .squashMergeAllowed ;;
  rebase) gh repo view --json rebaseMergeAllowed -q .rebaseMergeAllowed ;;
  *) echo false ;;
esac
```

## Known behavior the skills rely on

- `pr_merge`'s `--delete-branch` does local cleanup that is **best-effort and
  aborts across worktrees** (`fatal: 'main' is already used by worktree at ...`).
  That abort is not a merge failure — the remote merge already landed. Phase 4
  owns the local reconcile and re-verifies it, so never retry `pr_merge` on that
  signal; re-merging a merged PR errors.
- The authoritative merge signal is `pr_state` returning `MERGED`, never an
  exit code.
