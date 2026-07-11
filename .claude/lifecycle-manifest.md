# Lifecycle manifest

This repo's own `.claude/lifecycle-manifest.md`: the marketplace dogfoods
lifecycle-kit on itself. The six lifecycle skills (`session-start`,
`session-report`, `session-end`, `finalize-worktree`, `cleanup-worktrees`,
`report`) read this file for everything project-specific. It doubles as a
second worked example alongside `lifecycle-kit/examples/untype-manifest.md`,
this one for a Python + shell repo with no build step.

The git, branch, worktree, and session-log values are the template defaults
(they suit most GitHub projects). The build/test gate, code globs, prose gate,
and product name are the repo-specific values. Keep this a single fenced YAML
block.

```yaml
product_name: claude-plugins

# git integration
remote: origin
integration_ref: origin/main         # remote integration branch (authoritative)
local_main: main                     # local integration branch
pr_base: main                        # base branch for the session PR
requires_remote: true                # finalize/cleanup need a fetchable remote + gh-driven PR

# branches & worktrees
branch_pattern: "feature/session-{n}-{topic}"
branch_glob: "feature/*"
docs_log_branch: "docs/session-{n}-log"
worktree_dir: .claude/worktrees
worktree_pattern: "session-{n}-{topic}"
worktree_ignore: .git/info/exclude   # machine-local ignore, not committed
orphan_branch_globs: ["feature/session-*", "worktree-agent-*", "fix/*"]

# session logs
log_dir: sessions
log_archive: sessions/archive
log_index: sessions/INDEX.md
log_pattern: "{date}_session_{n}[_{suffix}].md"   # date = YYYY-MM-DD
log_glob: "sessions/[0-9]*_session*.md"
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'

# build / test gate — run in order, abort on the first failure
code_globs: ["prose-mint/**/*.py", "prose-mint/bin/*", "**/*.sh", "knowledge-kit/bin/*"]
build_commands: none                 # no compile step (Python + shell repo)
test_commands:
  - python -m pytest prose-mint/tests
  - shellcheck lifecycle-kit/hooks/*.sh knowledge-kit/bin/*.sh

# merge
merge_strategy: merge                # gh pr merge --merge; alternatives: squash | rebase

# prose gate (the marketplace's user-facing docs, scoped by .prose-mint.toml)
prose_gate: uvx prose-mint bulk --strict .
prose_rule: none

# code review (optional; none disables the step)
code_reviewer: none
review_command: none

# commit / PR convention
commit_convention: "prefix(topic): short description"
commit_trailers: none
subject_max: 72

# project knowledge & docs
issues_file: none
research_dir: research               # scanned recursively by report (absent here: report finds nothing)
reports_dir: reports
jargon_terms: [MCP, CLI, PR, uvx]    # strip from plain-mode reports
plan_doc: none
workflow_rule: lifecycle-kit/rules/workflow.md   # the bundled invariants doc, in-repo
scratch_paths: [.claude/settings.local.json]
```
