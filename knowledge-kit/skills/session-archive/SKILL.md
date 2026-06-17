---
name: session-archive
description: Export Claude Code session transcripts to a scrubbed, browsable Markdown archive and back it up to a configured destination (rsync, Google Drive, or git)
context: fork
agent: general-purpose
allowed-tools: Bash Read Glob Grep Write
---

Render this project's Claude Code session transcripts (the JSONL files under
`~/.claude/projects/<slug>/`) into a scrubbed, browsable Markdown archive and,
optionally, push that archive to a backup destination. The transcripts are
plaintext and contain secrets, file contents, and absolute paths, so the render
step runs a mandatory redaction pass *before* any byte is written, and no
destination sync runs until that pass has completed and you have reviewed its
report. The conversion is `session-archive.sh` (a shim over
`session-archive-impl.py`); this skill orchestrates it and the sync.

## Where the conversion script lives

`session-archive.sh` ships inside this plugin's `bin/`, which Claude Code adds to
the Bash tool's PATH while knowledge-kit is enabled. Invoke it by bare name, not
through a repo path; do not expect a copy in the consuming project's `bin/`.

## Project configuration

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a step
names a manifest key in `code font` (`archive_scope_default`,
`archive_export_dir`, `archive_home_redact`, `archive_scrub_extra`,
`archive_dest_default`, `archive_rsync_target`, `archive_gdrive_folder`,
`archive_git_repo`, `archive_git_branch`, `archive_retention_days`), use that
key's value. These keys are knowledge-kit's own; see the kit README and
`manifest-keys.md` for the block to add to the manifest. A key set to `none`
means the corresponding step is skipped, not run against a path literally named
`none` (same convention as the optional lifecycle knobs). This config block is
adjacent to the lifecycle skills, not part of that family; it only borrows the
manifest as a config store.

## Arguments

`$ARGUMENTS` is optional. Forms (any order):

- `cwd` (default, from `archive_scope_default`) — the slug derived from the
  current directory plus any sub-slug (e.g. `…-myproject-research`). `all` —
  every project under `~/.claude/projects`. A project-name fragment (e.g.
  `myproject`, matched against the tail of the slug) — just that one. Pass a
  fragment, not the leading-dash slug, which the argument parser would read as a
  flag.
- `--dest <name>` — override `archive_dest_default` for this run: `rsync`,
  `git`, `gdrive`, or `none`.
- `--dry-run` — render + scrub + report only; never touches a destination and
  never updates the incremental state. Use this for the first run on a new
  machine or after changing scrub rules.
- `--full` — re-render every session, ignoring the incremental state.
- `--no-thinking` — omit `thinking` blocks (leaner archive for sharing).

## Steps

Run in order. Abort on the first failure; never proceed to a later phase if an
earlier one errored.

1. **Resolve config.** Read the manifest and set the scope, destination, and the
   `<archive_*>` values. If the user passed a `--dest`, it wins over
   `archive_dest_default`.

2. **Render and scrub.** Run the converter from the repo root:
   ```
   session-archive.sh <scope> \
     --out <archive_export_dir> --home <archive_home_redact> \
     [--scrub-extra <archive_scrub_extra>] [--full] [--dry-run] [--no-thinking]
   ```
   Omit `--scrub-extra` when `archive_scrub_extra` is `none`. The script writes
   one Markdown file per session under `<archive_export_dir>/<sanitized-slug>/`,
   an `index.md` per slug, an `_archive-state.json`, and an
   `_redaction-report.txt`. Output directory names are sanitized so they don't
   carry the username. `<archive_export_dir>` is machine-local scratch; never
   commit it to this repo (add it to `.git/info/exclude`). Editing the scrub
   rules (`archive_scrub_extra` or the built-in set) changes the ruleset
   signature, which invalidates the incremental state and forces a full
   re-scrub automatically; no `--full` needed.

3. **Check the gate.** The script enforces the gate itself: after rendering it
   re-scans the written archive for high-confidence secrets (credential shapes
   and the home path in either form) and **exits non-zero (3) if any survived**,
   writing `GATE=FAIL` and the offending paths into the report. So gate the sync
   on the exit code, not on judgment. On a non-zero exit, do not sync: read
   `<archive_export_dir>/_redaction-report.txt`, add a pattern to
   `archive_scrub_extra`, and re-run from step 2. On exit 0 (`GATE=PASS`),
   surface the totals-by-rule to the user. If `--dry-run`, stop here regardless
   and tell the user to review, then re-run without it.

4. **Sync to the destination.** Only when step 2 exited 0 (gate passed). Sync
   only `<archive_export_dir>` (the scrubbed output), never the raw JSONL.
   Branch on the resolved destination:
   - `none` — local archive only; report the path and stop.
   - `rsync` — if `archive_rsync_target` is `none`, report that it is
     unconfigured and stop; else
     `rsync -av --delete <archive_export_dir>/ <archive_rsync_target>`.
   - `git` — if `archive_git_repo` is `none`, stop. Else mirror the export into
     that **separate** repo's working tree (never this project's repo; the
     archive is large and append-only and would bloat history), then
     `git -C <archive_git_repo> add -A`,
     `git -C <archive_git_repo> commit -m "archive: <date>"`, and
     `git -C <archive_git_repo> push origin <archive_git_branch>`.
   - `gdrive` — attended only. The native claude.ai Google Drive connector is
     OAuth-gated; its upload tools appear only after an interactive auth and it
     cannot complete OAuth in a headless or scheduled run. If the write tools
     are unavailable, tell the user this destination needs an interactive
     session (or a configured `rclone`) and stop; do not fail silently. When
     available, upload the contents of `<archive_export_dir>` into
     `archive_gdrive_folder`.

5. **Retention prune (optional).** If `archive_retention_days` is not `none`,
   remove exported session files older than that many days from
   `<archive_export_dir>` (and the matching destination). Note that the source
   transcripts themselves age out of `~/.claude/projects` after Claude Code's
   `cleanupPeriodDays` (default 30), so the archive only ever holds what was
   captured before that window; keep the run cadence shorter than it.

## Scheduling (optional, not wired by default)

This skill is on-demand. To run it periodically once the redaction report is
trusted, the user picks one of:
- `CronCreate` with `durable: true` writes `.claude/scheduled_tasks.json` and
  survives restarts, but a *recurring* job auto-expires after 7 days and fires
  only while a REPL is idle, so it must be re-armed.
- A claude.ai cloud routine (`RemoteTrigger`) is true headless cron.
Scheduled runs must target `rsync` or `git`; `gdrive` is attended-only. Pick a
cadence shorter than `cleanupPeriodDays` (30d) or sessions age out before
capture; daily at an off-`:00` minute is a reasonable default.

## Constraints

- Raw JSONL is never synced or committed. Only `<archive_export_dir>` leaves the
  machine, and only after the render script exits 0 (the enforced gate passed)
  and the report is reviewed.
- `--dry-run` is read-only with respect to every destination and to the
  incremental state.
- Read-only with respect to this project's working tree: the only writes are
  under `<archive_export_dir>` and, for the `git` destination, the separate
  archive repo.
