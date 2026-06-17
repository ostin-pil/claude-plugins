---
name: knowledge-audit
description: Audit the knowledge base for orphaned docs, stale docs, and unpromoted session learnings, and print a one-page health summary
allowed-tools: Bash Read Grep
---

Produce a knowledge-health summary for the project so insights compound instead
of scattering. The audit is three checks over the repo's tracked Markdown:
orphaned docs (no other file references them), stale docs (no commit in N days),
and unpromoted learnings (recent session logs whose decisions aren't reflected
anywhere durable under the knowledge directory). The scan is `knowledge-audit.sh`
(a shim over `knowledge-audit-impl.py`); this skill runs it, presents the report,
and helps act on it. Read-only by default: it never deletes a flagged doc or
promotes a learning on its own.

## Where the scan script lives

`knowledge-audit.sh` ships inside this plugin's `bin/`, which Claude Code adds to
the Bash tool's PATH while knowledge-kit is enabled. Invoke it by bare name, not
through a repo path; do not expect a copy in the consuming project's `bin/`.

## Project configuration

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a step
names a manifest key in `code font` (`knowledge_dir`, `research_dir`, `log_dir`,
`audit_stale_days`), use that key's value. These keys are knowledge-kit's own;
see the kit README and `manifest-keys.md` for the block to add to the manifest.
A project that has not added them can pass the equivalents as flags.

## Arguments

`$ARGUMENTS` is optional:
- `--stale-days N` — override `audit_stale_days` for this run.
- `--recent-logs N` — how many of the most recent session logs to check for
  unpromoted learnings (default 8).
- `save` — after presenting, save the report under `<knowledge_dir>/audits/`
  (see step 4). Off by default; the audit is a transient health check.

## Steps

1. **Run the scan** from the repo root, resolving the dirs and threshold from
   the manifest:
   ```
   knowledge-audit.sh \
     --knowledge-dir <knowledge_dir> --research-dir <research_dir> \
     --log-dir <log_dir> --stale-days <audit_stale_days>
   ```
   It prints a Markdown report to stdout and exits 0. It reads git history and
   tracked files only; it writes nothing.

2. **Present the report** to the user. Read it as guidance, not gospel, and say
   so where it matters:
   - **Orphaned docs**: the check matches the full repo-relative path, so a doc
     referenced only by a README category table, by a brace-expanded list, or
     after a rename can read as orphaned. Confirm before treating one as dead.
     A genuine orphan is a candidate for an index entry, a cross-link, or
     archival, not automatic deletion.
   - **Stale docs**: a dated snapshot going stale is usually intentional. Treat
     staleness as informational.
   - **Unpromoted learnings**: this is the actionable part. Each listed session
     has decisions in its log that aren't referenced anywhere under
     `knowledge_dir`, so they live only in the log.

3. **Offer to promote (only when asked).** For an unpromoted learning the user
   wants to keep, read the cited session log, then draft a durable home for it:
   an `OD-NNN` entry in `<knowledge_dir>/decisions/open-decisions.md`, an entry
   in the `issues_file`, or a short knowledge doc under the right subfolder (see
   the knowledge directory's `README.md` for routing). Write it as its own
   commit following the commit convention; the user decides which learnings earn
   promotion. Do not promote in bulk or without confirmation.

4. **Save the report (only when `save` is passed).** Write it to
   `<knowledge_dir>/audits/knowledge-audit-<YYYY-MM>.md`. If the project runs a
   prose gate (`prose_gate` is not `none`), scan the saved file with it and fix
   any flagged lines before committing.

## Constraints

- Read-only by default. Flag, never delete: the audit never removes a doc it
  calls orphaned or stale.
- Promotion and report-saving happen only on explicit request, each as its own
  commit. The audit itself produces no commit.
- The findings are heuristic. Surface the caveats in step 2 so the user decides;
  do not present orphan or staleness lists as definitive.
