---
name: report
description: Generate a project status report from git history, session logs, and research docs over a given time or commit range
context: fork
agent: general-purpose
allowed-tools: Bash Read Glob Grep Write
---

Generate a project status report for the project (`product_name`, Untype). The report covers: what was achieved, research conducted, current state, and what's next.

## Project configuration

The manifest is this skill's configuration. If
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md` does not exist, the
project has not adopted the kit: say so, offer to create it, and stop. Never infer
the keys and run anyway. The kit ships the template as
`lifecycle-manifest.template.md`; locate the installed copy with
`find ~/.claude/plugins -path '*lifecycle-kit*' -name lifecycle-manifest.template.md | head -1`.
The marketplace's `ADOPTING.md` carries a repo-inspecting setup prompt.

Read `.claude/lifecycle-manifest.md` first (resolve via
`$(git rev-parse --show-toplevel)/.claude/lifecycle-manifest.md`). Where a step
names a manifest key in `code font` (`product_name`, `log_dir`, `log_archive`,
`log_glob`, `log_pattern`, `research_dir`, `reports_dir`, `plan_doc`,
`prose_gate`, `prose_rule`, `jargon_terms`), use that key's value. The plain-mode
before/after examples are Untype-flavored illustrations of the technique, not
configuration.

## Argument Parsing

The user passes `$ARGUMENTS` which can be one of these forms (all optional — no argument means "everything"):

**Audience flag (can appear anywhere in the arguments):**
- `plain` — write the report for a non-technical audience (see Plain Mode below)
- If `plain` is absent, produce the default developer-oriented report

**Time-based:**
- `last week`, `last 3 days`, `today`, `yesterday` — human-readable relative ranges
- `Apr 8`, `2026-04-08` — single date (from that date to now)
- `Apr 8-10`, `2026-04-08..2026-04-10` — date range (inclusive)
- `..Apr 10`, `..2026-04-10` — up to that date (from the beginning)

**Git-based:**
- `abc1234` — single commit hash (from that commit to HEAD)
- `abc1234..def5678` — commit range
- `..def5678` — from the beginning up to that commit

Strip `plain` from the arguments before parsing the time/git range.

Parse the argument and determine:
- `GIT_SINCE` / `GIT_UNTIL`: for `git log --since/--until` (time-based)
- `GIT_RANGE`: for `git log <range>` (hash-based)
- `SESSION_DATE_FILTER`: which session files to include

For a hash range, derive `SESSION_DATE_FILTER` from the commit dates so the
session and research sections cover the same window as the commits:
`git log -1 --format=%cs <start>` and `git log -1 --format=%cs <end>` give
the inclusive date bounds. Without this the hash-range form scopes the
commit list but leaves the session and research sections unscoped.

If no argument is given (after stripping flags), include all history.

## Steps

1. **Gather git history** for the determined range:
   ```
   git log --oneline [--since=X] [--until=Y]
   ```
   or for hash ranges:
   ```
   git log --oneline <range>
   ```
   Do not silently cap the list. The old `head -60` truncated the
   time-based form but not the hash-range form, an asymmetry that dropped
   commits without saying so. If the range is large, summarize and state
   the total (`git log --oneline <range> | wc -l`) rather than cutting rows
   silently.

2. **Identify session logs** in `log_dir` and `log_archive` that fall within the range. Session files are named per `log_pattern` (`YYYY-MM-DD_session*.md`); older logs are moved under `log_archive`, so a range that reaches into earlier months must scan both (`<log_dir>/*_session*.md` and `<log_archive>/*_session*.md`, i.e. `sessions/*_session*.md` and `sessions/archive/*_session*.md` for Untype) or it silently misses over half the project's history. Filter by date extracted from filenames. Read all matching session files.

3. **Identify research docs** under `research_dir` recursively (`<research_dir>/**/*.md`; the tree has several subdirectories, so a flat `<research_dir>/*.md` listing misses most of it). Read the first ~30 lines of each to get title, date, and purpose. Include research docs whose dates fall within the range. For the date, use the git-add date as authoritative (`git log --diff-filter=A --format=%cs -1 -- <file>`) and fall back to a date written in the file's content only when git shows none; picking whichever is convenient makes the same doc drift in and out of an identical range from one run to the next.

4. **Read `plan_doc`** (`IMPLEMENTATION_PLAN.md` for Untype) to understand which phases exist and cross-reference with what was done.

5. **Compile the report** with these sections:
   - **Header**: "`product_name` Status Report {REPORT_END_DATE}" (e.g. "Untype Status Report ...") with the date range covered (no em dash in the output; `reports_dir` is prose-gated)
   - **Research Conducted**: Table of research docs with file, session, and summary. Skip this section if no research falls in range.
   - **What Was Achieved**: Organized by day, with a table of phases/features and their status. Derived from session logs and git commits.
   - **Current State**: What's working now, what's not yet tested, known gaps.
   - **What's Next**: Immediate priorities + post-MVP roadmap items. Derived from session "next steps" and remaining implementation plan phases.

6. **Save the report** to `<reports_dir>/Status Report {REPORT_END_DATE}.md` (`reports/` for Untype; create the directory if missing). `REPORT_END_DATE` is the end of the reporting range in `YYYY-MM-DD` form — the explicit end date if provided, otherwise today. If a report for that end date already exists but covers a different range (e.g. `report last week` and `report yesterday` run on the same day), do not silently overwrite it; name this one `<reports_dir>/Status Report {START} to {END}.md` instead.

7. **Prose-gate the saved file.** If `prose_gate` is `none`, the project has no prose gate; skip this step (the file is done after step 6). Otherwise `reports_dir` is prose-gated (`prose_rule`, `.claude/rules/prose-style.md`), so scan the file before handing it over with the manifest's `prose_gate`: `/prose-check <reports_dir>/<file>` (or `"$(git rev-parse --show-toplevel)/<prose_gate>" "<reports_dir>/<file>"`, i.e. `bin/check-prose.sh` for Untype). Fix any flagged lines and re-save until clean, then tell the user the file path. This applies to both the technical and the `plain` variants.

## Formatting Rules

- Use GitHub-flavored Markdown tables where appropriate
- Keep it concise — summarize, don't copy entire session logs
- Use `code formatting` for file paths and commands
- No emojis unless the user requests them

## Plain Mode

When `plain` is present in the arguments, rewrite the entire report for a non-technical audience (e.g. stakeholders, managers, designers). The data-gathering steps are identical — only the output changes.

**Language rules for plain mode:**
- No commit hashes, file paths, function names, class names, or code formatting
- No internal jargon: generic software terms (protocol, refactor, seam, harness, etc.) and the manifest's project/platform-specific `jargon_terms` (Untype: SPM, TCC, AX, IUO)
- Use a neutral voice describing what the product gained, not who did the work. Avoid first-person-singular "I built" framing, which wrongly implies a solo effort; the project has more than one contributor. If the user names a voice ("we", or a specific author), follow it; otherwise default to neutral.
- Describe outcomes in terms of what the app can do now, not how the code changed
- "Voice recognition is more accurate" not "enabled addsPunctuation on SFSpeechRecognizer"
- "There is now an automated test suite for transcription quality" not "TranscriptionHarness with bufferReplay and urlDirect modes"
- "Several stability issues are fixed" not "guarded AX force-casts, cancelled owned tasks in deinit"

**Section adjustments for plain mode:**
- **Research Conducted** → **Research & Investigation**: drop the file column, keep a plain-English summary of what was investigated and what was learned
- **What Was Achieved**: use prose paragraphs or simple bullet lists instead of tables. Group by theme (e.g. "Voice recognition improvements", "Testing infrastructure", "App stability") not by session number. Session numbers may appear as parenthetical context but should not be the organizing principle.
- **Current State**: split into "What's working" and "Known limitations" in plain language
- **What's Next**: frame as product priorities, not engineering tasks. "Improve recognition accuracy with real-world audio testing" not "Drop 5–10 human recordings under bench/audio/"
- **Commit summary**: omit entirely

**File naming:** save as `<reports_dir>/Status Report {REPORT_END_DATE} (plain).md` (`reports/` for Untype) so it doesn't overwrite the technical version.
