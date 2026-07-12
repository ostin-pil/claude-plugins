---
name: session-start
description: Brief the user on where the project left off and suggest the next slice, using recent session logs, git history, and the roadmap
allowed-tools: Bash Read Glob Grep AskUserQuestion
---

Produce a concise in-chat briefing for starting a new work session. Read-only on repo content (no Write/Edit), but may run `git fetch`, `git switch -c`, and `git worktree add` so the session opens on a clean per-session branch born off `origin/main`.

Counterpart to `/session-end`, which finalizes a session. This is the
"where am I?" command; `/session-end` is the "wrap it up" command.

## Project configuration

The manifest is this skill's configuration. If
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md` does not exist, the
project has not adopted the kit: say so, offer to create it from
`${CLAUDE_PLUGIN_ROOT}/lifecycle-manifest.template.md` (the marketplace `ADOPTING.md`
carries a repo-inspecting setup prompt), and stop. Never infer the keys and run anyway.

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a
step names a manifest key in `code font` (`log_glob`, `log_dir`,
`log_pattern`, `log_index`, `log_archive`, `branch_pattern`, `worktree_dir`,
`worktree_pattern`, `issues_file`, `plan_doc`), use that key's value.
Command bodies write these as `<key>` substitution placeholders
(`<integration_ref>`, `<local_main>`, `<remote>`); replace each with the
manifest value before running. The surrounding detection prose still names
`feature/*`, `main`, and `origin/main` with Untype's values for readability.
The collision examples ("session-99") are documentation, not configuration.

## Argument

`$ARGUMENTS` is an optional focus area (e.g. `overlay`, `ux`, `transcription`). If given, bias the "Suggested next slice" picks toward items in that area. If absent, suggest broadly.

## Steps

1. **Preflight — divergence check.** `git fetch <remote> --prune 2>/dev/null` (silent failure is fine — offline is OK; `--prune` so the step-7 remote-branch check below sees an accurate `origin/*`, not just `origin/main`). Then compare `git rev-list --left-right --count <integration_ref>...<local_main>` and `git rev-list --left-right --count <local_main>...HEAD` to detect three failure modes a parallel terminal can introduce:
   - Local `main` is behind `origin/main` — another machine pushed.
   - Local `main` has commits ahead of `origin/main` *and* the user is unaware (rare).
   - `HEAD` is on a `feature/*` branch but the user thinks they're on `main` (or vice-versa).
   - **Shared-checkout collision.** You are in the *primary checkout* (not a linked worktree), on a non-`main` branch, at session start, while `git worktree list` shows only that one checkout. That means another session likely left its branch here and you are about to share its working tree — the exact failure the worktree rule guards against (`.claude/rules/workflow.md`, "Concurrent sessions: one worktree each"). Detect it with `git rev-parse --git-dir` (a path containing `/worktrees/` means you are already isolated in a linked worktree, which is fine) plus `git worktree list`.
   Surface any of these in the briefing's "Where we left off" line; don't silently move on. If local `main` is ahead of `origin/main` with stray direct commits, flag it: under one-PR-per-session those should not be there (see `.claude/rules/workflow.md`). If the shared-checkout signal fired, treat it as stop-and-isolate: warn explicitly and, in step 7, lead with the worktree option.

2. **Find the latest session log.** `ls <log_glob> | sort | tail -3` (`log_glob` is `sessions/[0-9]*_session*.md` for Untype) — the lexicographically last log matching `log_pattern` (the glob skips `log_index` and the `log_archive` subdir; prefer non-worktree-suffixed ones if multiple share a date, and the highest `N` if dates tie). Read it in full, focusing on `## What's next`, `## Build status`, `## Commits`, and the branch line at the top. Also note the highest session number from filenames — feeds the step-7 pre-flight.

3. **Diff against current git state.**
   - Get the last commit hash from the session log's `## Commits` section. If the log has no `## Commits` section (older logs predate it), fall back to the merge-base of the session branch with `origin/main`, or the previous log's last commit, as the anchor.
   - `git log --oneline <that-hash>..HEAD` — anything shipped after the log was written.
   - `git status --short` — uncommitted work-in-progress to flag.
   - `git branch --show-current` — confirm current branch matches the session's branch.

4. **Pull open follow-ups.**
   - From the session log's `## What's next` (Immediate + Candidate next slices).
   - From `issues_file` (`knowledge/decisions/issues.md` for Untype), unless it is `none` — entries whose status is not Resolved/Closed (look for `Status:` lines or section headers).
   - Dedupe.

5. **Skim `plan_doc`** (`IMPLEMENTATION_PLAN.md` for Untype), unless it is `none`, for phase/roadmap context only if a follow-up references it. Don't quote it in the briefing — just use it to disambiguate.

6. **Print the briefing in chat** with these sections:

   - **Where we left off** — one short paragraph (branch, last session number, what landed, build status). Include the divergence flag from step 1 if any.
   - **Shipped since the last log** — bullets from step 3's `git log`, or "no commits since last log".
   - **Uncommitted work** — flag dirty files from `git status`, or "clean tree".
   - **Open follow-ups** — bulleted, deduped list from step 4.
   - **Suggested next slice** — 1–2 picks with a one-line rationale each. Bias by `$ARGUMENTS` if given. Phrase as a recommendation, not a decision.

7. **Branch birth.** A session is one branch, one PR (`.claude/rules/workflow.md`, "Session lifecycle: one PR per session"). The branch must be born off a freshly fetched `origin/main`, never off whatever the working tree currently points at.

   **Compute the next session number `N` with a collision pre-flight.** Do not just take the highest log filename + 1: a concurrent session can have already claimed that number on a branch you have not pulled, which is exactly the session-99/session-99 collision (two sessions independently picked 99 because nothing checked branches). Take `N` as one more than the **maximum session number across all three sources**, then assert the chosen `N` is unclaimed:
   - Log filenames: the highest `_session_<n>_` in `sessions/` (step 2).
   - Branches, local **and** remote: `git branch -a --list '*session-*' | grep -oE 'session-[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1` (run after the step-1 `git fetch`, so `origin/*` refs are current).
   - Recent history: `git log --all --oneline | grep -oE 'session-[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1`.

   With `N` chosen, confirm it is free before claiming it: `git branch -a --list "*session-$N-*"` must be empty and no `<log_dir>/*_session_${N}[._]*` may exist (the `[._]` matches both the suffixless `_session_${N}.md` and the suffixed `_session_${N}_<topic>.md`; a bare `_${N}_` glob silently misses the suffixless form). If either is non-empty, increment `N` by one and repeat this check until both come back empty, then claim that `N`. State the chosen `N` and that the pre-flight passed in the briefing.

   This skill is the **sole authority** that mints a session number. `N` is claimed by the branch name it creates (`branch_pattern`, `feature/session-<N>-<topic>` for Untype); from here on `/session-report` and `/session-end` read `N` from that branch name and never recompute it from log filenames. A session's identity is the pair `(N, <suffix>)`, not `N` alone: parallel workstreams off the same session may share `N` with distinct suffixes (`_audio`, `_api`), so the log filename, not the bare number, is the unique key.

   Derive a one-word `<topic>` slug from `$ARGUMENTS` or the picked next slice (e.g. `audit-sweep`, `omnibox`, `bench`). Ask the user via `AskUserQuestion` how to open the session — three answers:

   - **New feature branch (default)** — `git fetch <remote>` then `git switch -c <branch_pattern> <integration_ref>` (Untype: `git switch -c feature/session-<N>-<topic> <integration_ref>`). All session work and the session log land here; `/session-end` merges it as one PR.
   - **New worktree (isolated or parallel work)** — `git fetch <remote>` then `git worktree add <worktree_dir>/<worktree_pattern> -b <branch_pattern> <integration_ref>` (Untype: `git worktree add .claude/worktrees/session-<N>-<topic> -b feature/session-<N>-<topic> <integration_ref>`). Same one-PR lifecycle; `/session-end` phase 3 finalizes the worktree. If step 1 raised the shared-checkout collision signal, present this option first and mark it recommended; isolating from the other session's checkout is the whole point.
   - **Stay on the current branch** — proceed without switching. Only for a trivial one-commit fix that will not itself become a session needing its own PR.

   Report the new branch (or worktree path). If `git status` is dirty (step 3 flagged it), do NOT switch or spawn — print a warning that uncommitted work would follow the branch and ask the user to handle it first. Branching off `origin/main` is what removes the stale-base gotcha; do not substitute the local `main` ref, which can carry stray commits.

## Constraints

- Repo content is read-only: no Write, no Edit, no commits, no file creation in the working tree.
- Allowed git mutations: `git fetch` (always safe); `git switch -c <new-branch> <integration_ref>`; `git worktree add <path> -b <new-branch> <integration_ref>`. All only when the user accepts step 7. No `git switch` to an existing branch — that mutates HEAD silently. No `git push`, no `git reset`, no `git merge`.
- Always create the session branch from `origin/main`, never from the current working tree or the local `main` ref.
- Keep the briefing to ~30 lines — summarize, don't paste.
- If the latest session is several days stale and `git log` shows substantial activity since, say so explicitly so the user knows the "what's next" list may be outdated.
- No emojis.
