# knowledge-kit manifest keys

knowledge-kit's skills read the same project-level `.claude/lifecycle-manifest.md`
that lifecycle-kit uses; they only borrow it as a config store. Append the block
below to that manifest (inside the YAML fence). If you do not run lifecycle-kit,
the keys still work: the skills resolve them by reading the file.

Three of these keys (`research_dir`, `log_dir`, `issues_file`) are already in
lifecycle-kit's template, so set them once and both kits read them. The rest are
knowledge-kit's own.

```yaml
# knowledge base (knowledge-audit)
knowledge_dir: knowledge             # project-internal docs root (knowledge-audit scans this)
research_dir: research               # scanned recursively (research/**/*.md); shared with lifecycle-kit
audit_stale_days: 90                 # flag docs with no commit in this many days
issues_file: knowledge/decisions/issues.md   # ISS-NNN tracker for the issues skill; none disables it

# session archive (the session-archive skill; all keys none-able)
archive_scope_default: cwd               # cwd (slugs derived from the working dir) | all | an explicit project-slug dir name
archive_export_dir: .archive/sessions    # machine-local scratch; the scrubbed Markdown lands here before any sync
archive_format: markdown                 # markdown (only format shipped so far)
archive_home_redact: none                # absolute home prefix rewritten to ~ in the output (e.g. /Users/you); none disables
archive_scrub_extra: none                # path to a file of extra `name<TAB>regex` redaction rules, or none
archive_dest_default: none               # none | rsync | git | gdrive — overridable per run with --dest
archive_rsync_target: none               # e.g. user@nas:/volume1/claude-archive/ ; none = unconfigured (skip)
archive_gdrive_folder: none              # Drive folder for the attended connector upload; none = skip
archive_git_repo: none                   # path/URL of a SEPARATE private archive repo (never this project's repo); none = skip
archive_git_branch: main                 # branch to commit/push the archive on
archive_retention_days: none             # prune exported sessions older than N days; none = keep all
```

Set `archive_home_redact` to your home directory before the first non-dry-run
archive, so absolute paths are rewritten to `~`. Leave `archive_dest_default` at
`none` until you have reviewed a `--dry-run` redaction report and configured a
destination.
