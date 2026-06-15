# Lifecycle manifest

The six lifecycle and reporting skills (`session-start`, `session-report`,
`session-end`, `finalize-worktree`, `cleanup-worktrees`, `report`) read
this file for everything project-specific: the build and test gate, the
session-log directory and naming, the branch and worktree conventions, the
integration ref, the merge strategy, the prose gate, the code reviewer, the
product name, and the project's directory layout.

How it is consumed: a skill refers to a knob two ways. In prose it names the
key in `code font` (descriptive: "use `worktree_dir`"). In a command body it
writes the key as an angle-bracket placeholder `<key>` at the exact
substitution point (`git switch -c <branch> <integration_ref>`, run
`<build_commands>`). The angle-bracket form is the operative one: whatever runs
the skill resolves `<key>` to this file's value for that key. In Claude Code
that resolver is the model itself, reading this manifest (every skill's preamble
instructs it to); Claude Code has no load-time templating, so there is no
automatic string substitution. The `<key>` convention exists so that resolution
is unambiguous, and so an external tool could pre-render the same way (for tests,
or a non-model consumer). Angle-bracket names that are *not* manifest keys
(`<N>`, `<branch>`, `<topic>`, a SHA) are runtime fills the skill computes, not
manifest substitutions; a resolver leaves them alone. The skill prose is the transferable skeleton; this block is the
only place per-project values live. To stand the
kit up on another project, copy the six skills and edit this file: the command
bodies are tokenized with `<key>` placeholders (session 122), so they resolve
from this manifest with no per-command hand-edits. The narration prose around
the commands still names Untype's values illustratively; it runs nothing, so a
port can leave it. The Porting section below covers what remains (a
GitHub-remote precondition and the `none` sentinel). The tokenization was driven
by the ketin trial port (session 120,
`knowledge/workflow/lifecycle-kit-portability-2026-06-14.md`).

What is *not* here, by design: incident references in the skills (e.g.
"session 85", "finding 3") are documentation of why a guard exists, not
configuration; they stay in the skill prose. Generic git and `gh` mechanics
are not project knobs either. Only values that legitimately differ between
projects belong below. Every value is Untype's current behavior, so reading
through the manifest changes nothing for this repo.

When the skills are lifted into a Claude Code plugin, this file stays a
project-level config each adopting project populates, and a skill guarantees it
is in context by reading it at the top (a `SessionStart` hook can validate it is
present and well-formed). This block is the resolution contract either way. Keep
it a single fenced YAML block.

```yaml
product_name: Untype

# git integration
remote: origin
integration_ref: origin/main         # remote integration branch (authoritative)
local_main: main                     # local integration branch
pr_base: main                        # base branch for the session PR
requires_remote: true                # the finalize/cleanup lifecycle needs a fetchable remote + gh-driven PR; the kit targets remote-backed projects only (Gap 2, session 122). No-remote subset: report + read-only session-start/session-report

# branches & worktrees
branch_pattern: "feature/session-{n}-{topic}"   # a session's branch
branch_glob: "feature/*"             # finalize candidate detection
docs_log_branch: "docs/session-{n}-log"          # docs-only-session exception
worktree_dir: .claude/worktrees      # where session worktrees live
worktree_pattern: "session-{n}-{topic}"          # worktree dir name under worktree_dir
worktree_ignore: .git/info/exclude   # how worktree_dir is ignored (machine-local, not committed)
orphan_branch_globs: ["feature/session-*", "worktree-agent-*", "fix/*"]   # cleanup orphan sweep

# session logs
log_dir: sessions
log_archive: sessions/archive        # older logs moved here
log_index: sessions/INDEX.md
log_pattern: "{date}_session_{n}[_{suffix}].md"  # date = YYYY-MM-DD; suffix is the workstream tag
log_glob: "sessions/[0-9]*_session*.md"          # listing glob (excludes INDEX.md and archive/)
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'   # finalize-worktree session-log presence check (grep BRE); encodes log_dir + log_pattern's date form

# build / test gate — run in order, abort on the first failure
code_globs: ["*.swift"]              # a "code session" (build/test gate applies) is any diff touching these
build_commands: [swift build]
test_commands:
  - swift test
  - swift test --package-path Packages/UntypeCore   # guarded by subpkg_guard
subpkg_guard: Packages/UntypeCore/Package.swift      # run the last test_command only if this path exists

# merge
merge_strategy: merge                # gh pr merge --merge; alternatives: squash | rebase

# prose gate
prose_gate: bin/check-prose.sh       # resolve via `git rev-parse --show-toplevel`
prose_rule: .claude/rules/prose-style.md

# code review — advisory, never blocks the merge
code_reviewer: code-reviewer         # subagent at .claude/agents/code-reviewer.md
review_command: "/code-review high"

# commit / PR convention (full rules in CLAUDE.md §Commits)
commit_convention: "prefix(topic): short description"
commit_trailers: none                # no Co-Authored-By
subject_max: 72                      # commit subject length ceiling

# project knowledge & docs
issues_file: knowledge/decisions/issues.md   # open follow-ups
research_dir: research               # scanned recursively (research/**/*.md)
reports_dir: reports                 # report output, prose-gated
jargon_terms: [SPM, TCC, AX, IUO]    # project/platform-specific terms to strip from plain-mode reports (on top of generic software jargon)
plan_doc: IMPLEMENTATION_PLAN.md     # may be "none" if the project has no plan doc
workflow_rule: .claude/rules/workflow.md
scratch_paths: [.claude/settings.local.json, tools/__pycache__/, tools/test_output.md]   # known untracked noise
```

## Porting to another project

Copying the six skills and editing this manifest now ports every command body unchanged: the operative literals are `<key>` placeholders (session 122) resolved from this manifest. Two things still constrain a port, and one thing a port should understand about what is and is not tokenized.

Command bodies are tokenized; narration is not. Every operative literal in the four categories the ketin trial flagged is now a `<key>` placeholder resolved from this manifest: the build/test gate (`<build_commands>` / `<test_commands>` in `session-end` Phase 1 and `finalize-worktree` Phase 2 step 5), the git refs (`<integration_ref>` / `<local_main>` / `<remote>` across the four git skills), the session-log presence check (`<log_presence_regex>` in `finalize-worktree` Phase 2 step 4), and the `report` globs (`<log_dir>` / `<log_archive>` / `<research_dir>`). The prose around the commands still names Untype's values for readability (e.g. "born off `origin/main`"); that narration runs nothing, so a port can leave it untouched or update it for taste. A parsing core only ever substitutes the `<key>` placeholders, never the prose.

A GitHub remote is required, by decision (`requires_remote: true`). `finalize-worktree`, `session-end`'s finalize phase, and `cleanup-worktrees`' containment check all need `remote` / `integration_ref` to be a real, fetchable remote reached through a `gh`-driven PR. The kit officially targets remote-backed projects only. A no-remote mode is deliberately out of scope: it would have to merge locally, which crosses the never-merge-locally invariant (`workflow_rule`, ISS-W3) that exists for a documented divergence incident, so it is a different product, not a knob. On a no-remote repo the write/finalize lifecycle does not run; the subset that does is `report` plus the read-only half of `session-start` and `session-report` (briefing and log-writing, minus the `git fetch` and the branch-birth). `requires_remote` exists so the eventual plugin core can assert the precondition up front and fail with one clear message instead of a cryptic git error mid-finalize.

Optional knobs accept `none`. `prose_gate`, `code_reviewer`, `issues_file`, and `plan_doc` may be set to `none` (or left empty) on a project that has no prose gate, no code reviewer, no issues file, or no plan doc. The skill that reads each one skips the corresponding step instead of executing a path named `none`. The required keys (the git refs, the log conventions, the build gate) have no `none` form.
