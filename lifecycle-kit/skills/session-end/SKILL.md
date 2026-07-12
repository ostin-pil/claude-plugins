---
name: session-end
description: Finalize today's work session — update the session log, gate it with build+test, finalize the session's one PR (worktree or branch-only), and sweep stale worktrees
allowed-tools: Bash Read Edit Write Glob Grep
---

Finalize the current work session. Counterpart to `/session-start`.

This skill is the end-of-work wrap-up: record what happened, verify the
tree still builds, land the session's one PR (whether the work was in a
worktree or a `feature/*` branch in the primary tree), and prune any
stale worktrees that accumulated.

## Project configuration

The manifest is this skill's configuration. If
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md` does not exist, the
project has not adopted the kit: say so, offer to create it from
`${CLAUDE_PLUGIN_ROOT}/lifecycle-manifest.template.md` (the marketplace `ADOPTING.md`
carries a repo-inspecting setup prompt), and stop. Never infer the keys and run anyway.

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a
phase names a manifest key in `code font` (`code_globs`, `build_commands`,
`test_commands`, `subpkg_guard`, `log_dir`, `log_pattern`, `docs_log_branch`,
`commit_convention`, `commit_trailers`, `subject_max`, `merge_strategy`,
`scratch_paths`), use that key's value. Command bodies write these as `<key>`
substitution placeholders (`<integration_ref>`, `<local_main>`, `<remote>`,
`<build_commands>`, `<test_commands>`); replace each with the manifest value
before running. The surrounding detection prose still names `feature/*`,
`main`, and `origin/main` with Untype's values for readability. Incident
references ("session 85") are documentation, not configuration.

## Resolve the session tree first

Every phase below operates on the session's own tree `$WT` and its branch
`$SESSION_BRANCH`. Resolve both before phase selection; never assume the
current working directory is the session tree. Under a parallel session it
is not, and a bare `git branch --show-current` in the wrong tree is exactly
the session-85 failure. This resolution is re-derivable and refuses to
guess.

1. If `git rev-parse --git-dir` contains `/worktrees/`, the agent is
   already inside the session's linked worktree: `$WT` is
   `git rev-parse --show-toplevel`, `$SESSION_BRANCH` is
   `git -C "$WT" branch --show-current`. Done.
2. Otherwise the agent is in the primary checkout. Enumerate candidates
   with `git worktree list --porcelain`: every `feature/*` worktree, plus
   the primary itself if it is on a `feature/*` branch.
   - Primary on a `feature/*` branch, no `feature/*` worktree: branch-only.
     `$WT` is the primary, `$SESSION_BRANCH` is that branch.
   - Exactly one `feature/*` worktree, primary on `main`: worktree mode.
     `$WT` is that worktree, `$SESSION_BRANCH` its branch.
   - More than one candidate: **do not guess** (a parallel session is
     live). Stop and ask the user to re-run `/session-end` with the
     session's branch as an argument (it is passed through as the finalize
     target). Never auto-pick: finalizing the wrong tree is session 85.
   - Zero candidates: no session branch (research/discussion only). `$WT`
     is the primary; phases 3 and 4 fall to the docs-only path.

Every later phase runs against `$WT` (`git -C "$WT" ...`, build/test with
`cd "$WT"`, the session log under `$WT/sessions/`). `$SESSION_BRANCH` is the
session's identity from here on, not whatever the cwd happens to be on.

## Phase selection

Not every session needs every phase. Phase selection determines which
phases to run. There are two modes: **auto-detect** (default) and
**manual flags** (when `$ARGUMENTS` contains any `--skip-*` or `--full`
flag).

### Mode A — Auto-detect (default, no flags provided)

Two independent signals decide the phases. They are orthogonal: the file
classification gates only build/test; an open session branch gates
finalize, and worktree existence gates cleanup.

**Signal 1 — file classification (gates phase 1 only).** Inspect the
session's changes:

```bash
{ git -C "$WT" diff <integration_ref> --name-only; git -C "$WT" diff --name-only; git -C "$WT" diff --cached --name-only; } | sort -u
```

- **Code session** — any file matching `code_globs` in the diff (Untype: `*.swift`): phase 1 (build/test) runs.
- **Config/docs session** — nothing in the diff matches `code_globs`; only non-code
  files (`.md`, `.json`, files under `.claude/`, `sessions/`, `knowledge/`, `bin/`): phase 1 is skipped.
- **No changes** — nothing in the diff: phase 1 is skipped; phase 2.5
  no-ops if the log is unchanged.

This classification has no bearing on phases 3 and 4.

**Signal 2 — open session branch and worktrees (gates phases 3 and 4).**
Read off `$SESSION_BRANCH`/`$WT` resolved above, not a fresh
`git branch --show-current` (which reads the cwd, not the session tree):

- The session has an open `feature/*` branch — in a worktree, or
  checked out in the primary tree: phase 3 (finalize) runs, regardless
  of which file types changed. A docs-only session still needs its one
  PR merged. `/finalize-worktree` self-detects worktree vs branch-only.
- Any worktree (stale or otherwise) exists: phase 4 (cleanup) runs.
- No open `feature/*` branch and no worktrees: phases 3 and 4 are
  skipped (e.g. a research/discussion-only session whose log rode its
  own `docs/*` PR via phase 2.5's sanctioned exception).

Phases 2, 2.5, and 5 always run.

Print the detected signals and the resulting plan before starting:

```
Files: config/docs (no .swift)              phase 1 skipped
Session: feature/session-82-x (no worktree) phase 3 runs (branch-only)
Worktrees: none                             phase 4 skipped
Phases: 2, 2.5, 3, 5   Skipping: 1 (no code changes), 4 (no worktrees)
```

### Mode B — Manual flags (any flag present in `$ARGUMENTS`)

When `$ARGUMENTS` contains one or more flags, skip auto-detection and
use the flags to control which phases run:

| Flag                | Effect                                    |
|---------------------|-------------------------------------------|
| `--skip-build`      | Skip phase 1 (build & test gate)          |
| `--skip-worktree`   | Skip phase 3 (finalize the session PR)    |
| `--skip-cleanup`    | Skip phase 4 (cleanup stale worktrees)    |
| `--full`            | Force ALL phases regardless of other flags |

Flags can be combined: `--skip-build --skip-cleanup` runs phases 2,
2.5, 3, and 5.

`--full` overrides everything — all phases run unconditionally.

Any non-flag text in `$ARGUMENTS` is passed through to `/finalize-worktree`
and `/cleanup-worktrees` as before (e.g., to target a specific worktree).

Print the active flags and resulting phase plan before starting.

## Phases

Run selected phases in order. If a phase fails, report clearly and
stop — do not paper over failures or proceed to later phases.

Several phases below say to "delegate to" or "call" another skill
(`/session-report`, `/finalize-worktree`, `/cleanup-worktrees`). There is
no separate invocation primitive: that means read the named skill's
`SKILL.md` and execute its steps inline, in this same agent, with the
arguments given. "Call /finalize-worktree" is "follow finalize-worktree's
instructions now," not a sub-process. The phase still owns whether to run
the delegate at all (phase selection) and what arguments to pass it.

### Phase 1 — Build & test gate

*Skippable via auto-detect (config/docs or no-changes session) or `--skip-build`.*

Before writing any log, confirm the working tree is healthy. Results of
this phase get folded into the session log's `## Build status` section.

Run the manifest's `build_commands` then `test_commands` against the session
tree (`cd "$WT"` first — the session tree, not necessarily the cwd). Run each
entry in `<build_commands>` in order, aborting on the first non-zero exit; then
each entry in `<test_commands>` in order, same abort rule. Capture each
command's combined stdout+stderr and show only the tail (the gate cares about
pass/fail and the first error, not the full transcript). The final
`test_commands` entry runs only when `subpkg_guard` exists (a path check), so it
no-ops cleanly on a project with no separate sub-package suite.

Record for the log, one line per `build_commands` / `test_commands` entry and
its result (clean / failed with the first error; N/M passing / failed with the
first failure). Treat the test result as the union of all `test_commands`
entries: a green subset (e.g. a root suite that does not cover a sub-package)
does not imply the whole passed.

If either fails, **still write the session log** so today's work is
preserved, but mark `## Build status` accordingly and **stop before
phase 3** (do not finalize a session that doesn't build). The user
decides whether to fix forward or roll back.

When phase 1 is skipped, pass `"build/test: skipped (no code changes)"`
to `/session-report` so the log records why no build status exists.
`/finalize-worktree` is invoked with `--skip-build` in phase 3 so it
does not re-run a gate this phase already owns.

### Phase 2 — Write/update today's session log

*Always runs.*

Delegate to `/session-report`, passing the verbatim build/test summary
from phase 1 (the `build_commands`/`test_commands` results) as its argument
so it can fold the result into `## Build status` without re-running the checks.

Do **not** reimplement the log-writing logic here — `/session-report`
owns the format, the filename convention (including worktree suffix), the
"append, don't overwrite" rule, and reading `N` from the branch. Run it
against the session tree so the log lands under `$WT/sessions/` and
`N`/suffix come from `$SESSION_BRANCH`, not the cwd. This phase is complete
when `/session-report` reports it has updated or created the session file;
record that path as `$LOG_FILE`.

### Phase 2.5 — Commit the session log

*Always runs (no-ops if nothing to commit).*

The session log is a real artifact and must be committed before phase 3
runs, otherwise `/finalize-worktree` will (correctly) refuse a dirty
session tree.

The invariant (`.claude/rules/workflow.md`): the log is committed to an
open branch before that branch's PR merges, never onto `main` directly
and never onto a branch whose PR already merged.

1. **Survey the session tree.** `git -C "$WT" status --porcelain` (the
   session tree, not the cwd) — classify each line:
   - The session log file written by phase 2 (matching `log_pattern`
     under `log_dir`, `sessions/YYYY-MM-DD_session*.md` for Untype) — **commit this**.
   - Other uncommitted tracked files — **do not touch**. The
     atomic-commits rule says the user commits those as their own
     logical units.
   - Untracked files, ignored noise (the manifest's `scratch_paths` and
     `worktree_dir`, e.g. `.claude/settings.local.json`,
     `.claude/worktrees/`) — ignore.

2. **Pick the landing branch.** Normal path: `$SESSION_BRANCH` (resolved
   above) is an open `feature/*` branch whose work PR has not merged.
   Commit the log onto it in `$WT` so it rides the one session PR.

   Fallback, only these cases: `$SESSION_BRANCH` is empty or `main` (no
   session branch, research/discussion-only), or
   `gh pr list --state merged --head "$SESSION_BRANCH"` shows its PR
   already merged (if that `gh` call errors rather than returning empty,
   treat the state as unknown and stop; a silent `gh` failure must not be
   read as "not merged", or the log lands on an already-merged branch).
   Then do not commit onto it; instead `git fetch <remote>`
   then `git switch -c <docs_log_branch> <integration_ref>` (`docs_log_branch` is
   `docs/session-{n}-log` for Untype) and commit the log there for a small
   standalone docs PR. Sanctioned exception, not a parallel default.

3. **Stage and commit only the session log, in `$WT`:**
   ```bash
   git -C "$WT" add "$LOG_FILE"
   git -C "$WT" commit -m "docs(sessions): add session <N> log for <short topic>"
   ```
   Follow `commit_convention` (`prefix(topic): short description`; see
   `CLAUDE.md` §Commits). `commit_trailers` is `none` (no `Co-Authored-By`).
   Keep the title within `subject_max` (72) chars. `add` for a new log,
   `update` for an appended one. `$LOG_BRANCH` is `$SESSION_BRANCH` (or the
   `docs_log_branch` name from the fallback). Treat it as
   **re-derivable**, not a remembered string: it is the branch that
   contains this commit, `git -C "$WT" branch --contains <commit-sha>`.
   Phase 3 recomputes it that way and refuses if the two disagree; it is
   the session's identity, not the primary checkout.

4. **If other tracked files are still dirty**, print a warning listing
   them; the user commits them before phase 3 can proceed. Then **stop**
   — the log is committed so nothing is lost.

5. **If the only dirty file was the session log**, report the commit
   hash and proceed to phase 3.

Delegating to `/commit` is also fine if it matches the same rules, but
the explicit `git add <one-file>` + `git commit -m` pattern is safer
here because it guarantees only the session log lands in this commit.

### Phase 3 — Finalize the session PR

*Runs when the session has an open `feature/*` branch (worktree or
branch-only); skippable via `--skip-worktree`.*

Only run this phase if the `build_commands` and all `test_commands` passed in
phase 1 (or phase 1 was skipped — in that case the build gate does not apply).

1. The target is `$LOG_BRANCH` from phase 2.5 — the branch the session log
   was committed onto. Re-derive it rather than trusting a remembered
   string: `git -C "$WT" branch --contains <log-commit-sha>` must name
   `$LOG_BRANCH`, and that must equal `$SESSION_BRANCH`. If they disagree,
   **stop and report** — the recorded identity drifted (a parallel session,
   or a survey of the wrong tree), and finalizing would target the wrong
   branch (session 85). Do **not** fall back to the cwd or the primary
   checkout. If phase 2.5 was a no-op (no log to commit), there is no
   session to finalize here — skip to phase 4.
2. Call `/finalize-worktree "$LOG_BRANCH" --skip-build` — always pass the
   branch explicitly so its phase 1 cannot guess. `--skip-build` because
   phase 1 already owns the build gate. It self-detects worktree vs
   branch-only mode, owns the push, the merge confirmation gate, PR
   creation, prose-check, the merge (`merge_strategy`), local `main`
   reconcile, and (worktree mode) worktree removal — do not reimplement any of it here.
3. `/finalize-worktree` itself aborts on an ambiguous candidate set; the
   explicit `$LOG_BRANCH` argument is what disambiguates. Never finalize
   a branch other than `$LOG_BRANCH` from this skill.
4. If there is no open `feature/*` branch at all (research/discussion
   session whose log rode its own `docs/*` PR via phase 2.5's
   sanctioned exception), skip to phase 4. That `docs/*` log PR stays
   assistant-driven by design — a rare exception, not the recurring
   gap this phase closes.

**Resuming a partial finalize.** If a prior run merged the PR on GitHub but
aborted before the local reconcile finished, just re-run `/session-end`
with `--skip-build` (the log is already committed). Phase 2.5 no-ops
(nothing new to commit), and `/finalize-worktree` detects the already-`MERGED`
PR and skips to its idempotent phase 4 reconcile. Never re-run
`gh pr merge` by hand; it errors on a merged PR.

### Phase 4 — Cleanup stale worktrees

*Runs when worktrees exist to sweep; skippable via `--skip-cleanup`.*

After finalization (or if phase 3 was a no-op), sweep any leftover
debris by invoking `/cleanup-worktrees`. That skill has its own safety
rules (only deletes worktrees/branches where `ahead=0` and dirty state
is allowlisted noise) and always confirms before deleting.

If no worktrees exist, this phase is skipped.

### Phase 5 — Report

*Always runs.*

Print a short summary:

```
✓ build / test gate
✓ sessions/2026-04-14_session_25.md updated
✓ committed <sha> — docs(sessions): ...
✓ finalize-worktree: PR #<n> merged   (or: skipped — no open session branch)
✓ cleanup-worktrees: N removed         (or: skipped — no worktrees)
```

For skipped phases, use `—` instead of `✓` or `✗`, with the reason:

```
— build / test gate (skipped, no code changes)
✓ sessions/2026-04-14_session_25.md updated
✓ committed <sha> — docs(sessions): ...
— finalize-worktree (skipped, no open session branch)
— cleanup-worktrees (skipped, no worktrees)
```

If phase 2.5 stopped because of dirty non-log files, the summary should
end with the uncommitted files listed and phases 3–4 marked as
`— skipped, dirty session tree`.

If any phase failed, replace the check with `✗` and the failure reason.

## Rules

- **Don't push from this skill.** `/finalize-worktree` now pushes the session branch itself (a non-force push) and pauses for your confirmation before merging; let it own both the push and the merge gate. Force-push, rebase, `reset --hard`, `clean`, and `checkout --` stay out of scope here as everywhere.
- **Never force-delete branches.** Cleanup and finalize both handle
  deletion with their own safety rules; don't reimplement.
- **No emojis** in the session log.
