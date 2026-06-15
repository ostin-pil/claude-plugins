---
name: cleanup-worktrees
description: Prune stale worktrees and their branches whose work is already in main
allowed-tools: Bash Read
---

Sweep leftover worktrees under `worktree_dir` (`.claude/worktrees/` for
Untype) and the branches they reference. Counterpart to `/finalize-worktree`:
finalize handles the happy path (merge + remove one worktree), this handles
the accumulated debris from parallel-agent sessions that were abandoned,
crashed, or whose work already landed via a different path.

## Project configuration

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a
step names a manifest key in `code font` (`worktree_dir`, `worktree_ignore`,
`orphan_branch_globs`, `scratch_paths`), use that key's value. The containment
commands write the ref as `<integration_ref>` and the remote as `<remote>`;
replace each with the manifest value before running. The surrounding prose still
names `origin/main` with Untype's value for readability. The `ahead=0`
containment proof and the `-D`-vs-`-d` seam are the skill's logic, not
configuration.

## Safety rule

A worktree/branch is **safe to delete** only if every commit on its branch
is already contained in `origin/main`, the authoritative integration ref —
i.e. `git rev-list --count <integration_ref>..<branch>` is `0` after a fresh
`git fetch <remote> --prune`. Measuring against local `main` would miss a
branch already merged on GitHub but not yet fast-forwarded locally, which
is the most common real debris this skill exists to sweep. Dirty working
trees do not count as unique work if they only touch the manifest's
`scratch_paths` (e.g. `.claude/settings.local.json`) or other ignored/noise files.

Anything with `ahead > 0` is **never** auto-deleted by this skill. Report it
and ask the user.

## Process

### Phase 1 — Enumerate

1. `git worktree list` — list every worktree
2. For each non-primary worktree, record: path, branch (or detached HEAD), ref
3. `git worktree list --porcelain` if you need the machine-readable form

### Phase 2 — Classify each worktree

First `git fetch <remote> --prune` so containment is measured against the
real merged state. Then, for each non-primary worktree branch `$B`
(measured against `origin/main`, never local `main`):

```
ahead=$(git rev-list --count <integration_ref>..$B 2>/dev/null)
behind=$(git rev-list --count $B..<integration_ref> 2>/dev/null)
dirty=$(git -C <worktree-path> status --porcelain)
```

If `$ahead` comes back empty (a bad or missing ref, with stderr swallowed
by `2>/dev/null`), treat the branch as **unique-work** and report it.
Never classify an unparseable count as safe.

Classify as:

- **safe** — `ahead=0` and (`dirty` is empty, OR `dirty` only touches the
  manifest's `scratch_paths` (for Untype: `.claude/settings.local.json`,
  gitignored, plus `tools/__pycache__/` and `tools/test_output.md`, untracked
  build/test scratch not actually in `.gitignore`), or other genuinely ignored files)
- **unique-work** — `ahead > 0`. Has commits not in main.
- **dirty-real** — `ahead=0` but `dirty` contains real uncommitted edits to
  tracked source files. Could be in-progress work.
- **detached** — worktree is on a detached HEAD. Treat as `unique-work`
  unless the HEAD SHA is an ancestor of `origin/main`
  (`git merge-base --is-ancestor $SHA <integration_ref>`), in which case **safe**.

Also list any **orphan local branches** matching `orphan_branch_globs`
(`feature/session-*`, `worktree-agent-*`, `fix/*` for Untype) that are not
checked out in any worktree: the same `ahead=0`-against-`origin/main` check
applies, so those are safe to delete even without a worktree attached. The
session-branch glob (`feature/session-*` for Untype) is the dominant
convention `/session-start` and `/session-end` use, and a session whose PR
merged on GitHub leaves exactly such an orphan; omitting it was this skill's
main blind spot.

### Phase 3 — Report, then confirm

Show the user a table:

```
worktree                  branch                            class         notes
agent-xxxxxxx             worktree-agent-xxxxxxx            safe          ahead=0, dirty only in settings.local.json
agent-yyyyyyy             feature/foo                       unique-work   ahead=3 — will NOT touch
agent-zzzzzzz             fix/bar                           dirty-real    ahead=0 but 2 tracked files modified
```

Then list what will be removed if the user confirms:

- N worktrees to `git worktree remove --force`
- M branches to `git branch -D`

**Always get explicit confirmation before deleting.** Use AskUserQuestion if
the situation is non-trivial, otherwise a direct prompt. Never auto-delete
anything classified as `unique-work` or `dirty-real`.

### Phase 4 — Execute

On confirmation:

1. `git worktree remove --force <path>` for each safe worktree
   (`--force` is needed because of noise dirty state; we've already verified
   there's no real work to lose)
2. `git branch -D <branch>` for each safe branch (including orphans).
   Use `-D` not `-d`: some ancestor-only branches appear "not merged" to
   git's merge detector even with `ahead=0`. This is the deliberate
   inverse of `/finalize-worktree`, which forbids `-D` and relies on a
   self-verifying `-d`. The two are not in conflict; the difference is the
   proof of containment. `-D` is safe here only because Phase 2 already
   proved `ahead=0` (every commit on the branch is in `main`) before this
   line runs. Finalize has no such precomputed proof in its flow, so it
   must let `-d` verify. Never reach for `-D` without an independent
   containment proof first.
3. `git worktree prune -v` to clear any stale admin state
4. Leave the `worktree_dir` directory itself in place — it's ignored
   via `worktree_ignore` (`.git/info/exclude` for Untype, a machine-local
   exclude that does not survive a fresh clone, so do not assume `.gitignore`
   covers it) and is reused by future agent runs

### Phase 5 — Verify

```bash
git worktree list        # only the primary worktree should remain (unless some were kept)
git branch               # only surviving branches
ls .claude/worktrees/    # empty (or only kept worktrees)
```

Report a one-line summary: `Removed N worktrees and M branches. P kept
(reason).`

## Out of scope

This skill only touches worktrees and their branches. If the primary
repo has other untracked cruft (e.g. `index.js`, `tools/test_output.md`,
scratch files), **flag them** in the final report but do not delete — those
need a separate review.

## Arguments

- No arguments: sweep everything under `worktree_dir` plus orphan branches
  matching `orphan_branch_globs` (`worktree-agent-*` / `fix/*` and the
  session glob for Untype).
- `$ARGUMENTS` = `--dry-run`: run phases 1–3 only, report, do not delete.
