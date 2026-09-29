# Forge preset — none

For a repo with no remote, by choice. The kit previously declared this out of
scope ("a no-remote mode would have to merge locally, which crosses the
never-merge-locally invariant, so it is a different product, not a knob"). That
reasoning holds for its own case and not for this one — see *When this is
honest* below. The gap it left was worse than the rule it protected: projects
with no remote ran `/session-start` and `/session-report`, then hand-merged
with no guard at all.

**Requires:** nothing. No remote, no token, no CLI.

## What changes

`none` does not stub out phase 3 — it replaces it. There is no push and no PR,
so the merge gate moves from "confirm on the forge" to "confirm locally", and
phase 4's remote steps become no-ops that still assert their target state.

`$MAIN` below is the primary checkout, `$BRANCH` the session branch, `$WT` its
worktree.

### Phase 3, replaced

0. **Re-entry.** If `pr_state "$BRANCH"` (below) reads `MERGED`, the merge
   already landed, for example one completed by hand after step 5. Skip to
   phase 4. If `git -C "$MAIN" rev-parse -q --verify MERGE_HEAD` prints a SHA,
   the primary checkout is mid-merge: report it and stop, and do not start
   another merge on top of it.
1. **No push.** Skip phase 3 step 1 entirely; there is nowhere to push.
2. **No PR.** Skip steps 2 and 3. The prose gate, if `prose_gate` is set, runs
   against the session log instead of a PR body — it is the only prose artifact
   a no-remote session produces.
3. **Merge gate.** Show the user the branch, its commit titles
   (`git -C "$WT" log <local_main>..HEAD --format='%s'`), and the diffstat, then
   **ask for explicit confirmation**. This is the same single human checkpoint
   the `github` path puts on the PR merge; without confirmation, stop and leave
   the branch open.
4. **Merge, with the target tree verified first.** The merge lands in whichever
   worktree holds `<local_main>` — usually `$MAIN`, and it may be **in active
   use by another session**. Two assertions, and they are not the same strength:

   ```bash
   git -C "$MAIN" rev-parse --abbrev-ref HEAD   # must be <local_main>
   git -C "$MAIN" status --porcelain            # inspect; see the intersection test
   ```

   Being on the wrong branch is a hard **stop**. A dirty tree is not, by
   itself: what matters is whether the merge would touch the dirty paths.
   Apply the same intersection test phase 4 step 2 uses, rather than demanding
   the tree be pristine:

   ```bash
   comm -12      <(git -C "$MAIN" status --porcelain | awk '{print $NF}' | sort -u)      <(git -C "$MAIN" diff --name-only <local_main>.."$BRANCH" | sort -u)
   ```

   **Non-empty output is a stop.** Merging would sweep another session's
   uncommitted work exactly as a stray `git add -A` would, which is the
   working-tree collision `workflow_rule` exists to prevent. Report and wait.

   **Empty output means the dirty files are none of your business** — git will
   not touch them, they stay uncommitted on top of the merge commit, and the
   merge is safe. Say so when reporting rather than blocking on an unrelated
   file. Note this is still a coordination question: the merge moves
   `<local_main>` under a session that may be mid-work, so surface it at the
   merge gate in step 3 and let the human decide.

   Then merge. The subject is `Merge $BRANCH` under any `commit_convention`.
   The trailers come from `commit_trailers`, resolved as the manifest
   template's *Commit messages* section describes, and follow as one more
   `-m` holding every trailer line, newline-separated:
   ```bash
   git -C "$MAIN" merge --no-ff "$BRANCH" -m "Merge $BRANCH"                  # commit_trailers: none
   git -C "$MAIN" merge --no-ff "$BRANCH" -m "Merge $BRANCH" -m "<trailers>"  # otherwise
   ```
   If a placeholder in `commit_trailers` cannot be resolved, stop and ask
   before merging; never merge without the trailer. `--no-ff` is not optional
   here. It is what keeps the session boundary visible in a history that has
   no PR to record it.
5. **If a hook refuses the merge message.** A `commit-msg` hook runs on a merge
   commit too. When it refuses, git prints
   `Not committing merge; use 'git commit' to complete the merge.` and leaves
   `$MAIN` mid-merge: `MERGE_HEAD` is set, the merged tree is staged, and
   `<local_main>` has not moved. Confirm the refusal was about the message and
   nothing else:

   ```bash
   git -C "$MAIN" rev-parse -q --verify MERGE_HEAD     # prints a SHA: mid-merge
   git -C "$MAIN" diff --name-only --diff-filter=U     # empty: no conflicts
   ```

   When both hold, the content merged cleanly and only the commit is missing.
   Report that plainly: the primary checkout is mid-merge, here is the hook's
   output, and this command completes the merge:

   ```bash
   git -C "$MAIN" commit -m "Merge $BRANCH" -m "<trailers>"
   ```

   `<trailers>` is what the hook asked for. Normally that is `commit_trailers`
   resolved. If the hook refused the manifest's own trailers, the manifest and
   the hook disagree; say so and name the line the hook wants. Run the command
   only on the user's go-ahead, then continue from step 0, which finds the
   branch merged and moves on to phase 4.

   Two rules from `finalize-worktree` still hold here. Never pass
   `--no-verify` to get past the hook, and never run `git merge --abort` on
   your own; the user decides between completing and aborting. If
   `MERGE_HEAD` is not set, or there are conflicted paths, this was not a
   message refusal: report it and stop, as for any failed merge.

### Phase 4, adjusted

Steps 1 and 2 (fetch, fast-forward local main) are no-ops — there is no
`<integration_ref>` distinct from `<local_main>`, and the merge already moved
it. Steps 3, 5 and 6 run unchanged. Step 4 is a no-op via
`remote_branch_delete`.

## Verbs

```bash
# pr_find $BRANCH -> empty. There are no PRs.
true

# pr_create -> not applicable; phase 3 above replaces it.

# pr_state $N -> OPEN | MERGED
# Local ancestry is the honest analogue of "did it merge": if the branch tip is
# reachable from <local_main>, the work landed. $N is the branch name here.
if git -C "$MAIN" merge-base --is-ancestor "$N" <local_main> 2>/dev/null
  then echo MERGED; else echo OPEN; fi

# pr_merge $BRANCH merge   -> the phase 3 steps 4 and 5 above, gate included.

# pr_find_merged $BRANCH -> "<branch>" | empty
git -C "$MAIN" merge-base --is-ancestor "$BRANCH" <local_main> 2>/dev/null &&
  echo "$BRANCH" || true

# remote_branch_delete $BRANCH -> no-op, exit 0. No remote holds a copy.
true

# merge_strategy_ok $STRATEGY -> true only for merge
[ "$STRATEGY" = merge ] && echo true || echo false
```

`merge_strategy` must be `merge` under this preset. `squash` and `rebase` both
leave the branch tip un-reachable from `<local_main>`, which breaks the
ancestry that `pr_state` and phase 4's safe `git branch -d` both depend on —
and unlike the forge providers there is no PR record to fall back on as proof
the work landed.

## When this is honest

The never-merge-locally rule prevents **local/remote divergence**: local `main`
drifting from the remote integration ref. That failure needs two writers of one
remote. A repo with no remote has one ref and cannot diverge from anything, so
the rule protects nothing here while its absence leaves real sessions unguarded.

What you genuinely give up, and should accept knowingly:

- **No off-machine copy.** A remote is a backup as a side effect; this is not.
  Arrange mirroring separately, and treat it as load-bearing rather than
  optional — it is the only copy.
- **No review surface.** No diff view, no comments, no CI.
- **No merge record beyond the commit.** `--no-ff` and a session log are the
  whole audit trail.

If any of those start to matter, `forge` is one key — switch to `forgejo` or
`github` and the rest of the kit is unchanged.
