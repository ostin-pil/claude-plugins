You are archiving Claude Code session transcripts into a scrubbed Markdown
archive, as a benchmark of the session-archive skill. Follow the skill
instructions appended below, verbatim.

The transcripts to archive are under: {{PROJECTS}}
Write the archive to: {{OUT}}

There is no project manifest here, so use these values directly instead of
resolving manifest keys: scope `all`, `--projects-dir {{PROJECTS}}`,
`--out {{OUT}}`, `--home /nonexistent`, destination `none` (local archive only,
no sync). The conversion script `session-archive.sh` is on your PATH; invoke it
by bare name as the skill says. Pass `--full` so every session renders.

Actually perform it (this is not a dry description). Report what you ran and the
gate result.
