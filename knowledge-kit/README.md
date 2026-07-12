<!-- prose-check: skip ai-attribution -->
# knowledge-kit

Knowledge-base skills for Claude Code, driven by the same per-project
`.claude/lifecycle-manifest.md` that lifecycle-kit uses. They keep a project's
accumulated insight from scattering: track issues, audit the knowledge base for
rot, and archive session transcripts before Claude Code prunes them.

## What you get

Three skills, all invocable as slash commands:

| Skill | Does |
| --- | --- |
| `knowledge-audit` | Scans tracked Markdown for orphaned docs, stale docs, and session-log learnings that were never promoted to a durable home. Read-only; prints a one-page report. |
| `issues` | Manages an `ISS-NNN` issue-and-solution tracker at `issues_file`. Add, search, update, verify. |
| `session-archive` | Renders this project's Claude Code transcripts to a scrubbed, browsable Markdown archive and optionally backs it up (rsync, git, or attended Google Drive). A mandatory redaction gate runs before any byte is written or synced. |

Plus templates a consumer copies in: a starter `knowledge/` tree, a generic
`prose-style` rule, and two git hooks.

## How the scripts are bundled

`knowledge-audit` and `session-archive` run helper scripts (`knowledge-audit.sh`,
`session-archive.sh`, each a shim over a stdlib-only Python impl). They ship in
this plugin's `bin/`, which Claude Code adds to the Bash tool's PATH while the
plugin is enabled, so the skills call them by bare name. They are deliberately
**not** referenced through `${CLAUDE_PLUGIN_ROOT}`: that variable does not
reliably expand in skill-body Bash, whereas the `bin/`-on-PATH mechanism is the
documented one.

## Evidence

`knowledge-audit` is a deterministic script with a golden precision and recall
test (`benchmarks/knowledge`): 1.0 on both over the planted corpus. It flags the
two orphaned docs and the unpromoted session learning while leaving cited and
already-promoted docs untouched.

`session-archive`'s redaction is benchmarked against a naive control in
`benchmarks/knowledge/ab`, with the same `claude -p --safe-mode` isolation as
lifecycle-kit. Twelve secrets are planted in a transcript and the verdict counts
how many survive into the output. The gated skill leaks zero on every trial and
every tier by construction: it re-scans the written archive and exits non-zero
if any high-confidence secret remains. The control is probabilistic. Sonnet and
Opus caught all twelve on every trial, but one Haiku trial leaked four at once,
including an obvious `sk-ant-` key, and reported in the same output that "no
actual secrets are exposed." The worth of the skill is the guarantee on a task
where one miss is a breach, rather than a better average.

`issues` is measured across `add`, `verify`, and `search`, and it is mostly
consistency insurance. `add` ties with the control at every tier, because the
tracker is self-documenting. `verify`'s strict 9/9 against the control's 0/9
reads as a rout but is really a vocabulary win: the control detects every
reverted fix and only names the status inconsistently. `search` is the one
consequential cell, where the skill's "grep the session logs as well as the
tracker" instruction turns Sonnet's confident wrong "no such issue" into the
right answer. Full tables and caveats are in
`benchmarks/knowledge/issues-ab/RESULTS.md`.

## Install

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install knowledge-kit@ostin-pil-plugins
```

## Per-project setup

1. **Manifest keys.** Append the block in `manifest-keys.md` to your
   `.claude/lifecycle-manifest.md` (the file lifecycle-kit already uses; if you
   don't run lifecycle-kit, create it with just these keys). At minimum set
   `knowledge_dir`, `issues_file`, and `log_dir`. The `archive_*` keys are all
   `none`-able; leave `archive_dest_default: none` until you've reviewed a
   `--dry-run` archive.

2. **Knowledge skeleton (optional).** Copy `templates/knowledge/` into your repo
   to scaffold the directory the skills write into:
   ```
   cp -R <plugin>/templates/knowledge/ ./knowledge/
   ```
   It seeds a routing `README.md`, an empty `decisions/issues.md`, and
   `decisions/open-decisions.md`. Skip any file you already have.

3. **prose-style rule (optional).** `templates/rules/prose-style.md` is a generic
   policy that pairs with the prose-mint plugin. Copy it to
   `.claude/rules/prose-style.md` and adapt the scope.

4. **Git hooks (optional).** Two hooks live in `templates/git-hooks/`. Claude
   Code plugins can't install git hooks for you, so copy them in once:
   ```
   cp <plugin>/templates/git-hooks/commit-msg .git/hooks/commit-msg
   cp <plugin>/templates/git-hooks/prepare-commit-msg .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/commit-msg .git/hooks/prepare-commit-msg
   ```
   `commit-msg` strips `Co-Authored-By` trailers; `prepare-commit-msg` appends a
   `Session-date:` trailer so a day's commits are grep-able as a unit. Both use
   BSD `sed` (macOS); on GNU/Linux drop the empty `''` after `-i` in `commit-msg`.

See the monorepo's `ADOPTING.md` for the end-to-end adoption flow across
lifecycle-kit, prose-mint, and knowledge-kit.
