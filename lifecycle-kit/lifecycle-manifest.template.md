# Lifecycle manifest (template)

Copy this file to `.claude/lifecycle-manifest.md` in your project and fill in
the values. The lifecycle skills read it from `<repo>/.claude/lifecycle-manifest.md`
at runtime; it is the only place per-project values live.

Two substitution forms appear in the skills. In prose a knob is named in
`code font` (descriptive). In a command body it appears as an angle-bracket
placeholder `<key>` at the exact substitution point; the model resolves `<key>`
to this file's value. Angle-bracket names that are not keys here (`<N>`,
`<branch>`, a SHA) are runtime values the skill computes.

The git, branch, worktree, and session-log defaults below suit most GitHub
projects; change them only if your conventions differ. The build/test gate and
the product name are the values you must set. Optional knobs accept `none`
(`prose_gate`, `code_reviewer`, `issues_file`, `plan_doc`, `subpkg_guard`); the
skill that reads each one skips its step. See `examples/untype-manifest.md` for a
filled, real-world manifest.

If you change `log_dir` away from `sessions`, update `log_glob`, `log_archive`,
and `log_presence_regex` to match: those encode the directory and the
`YYYY-MM-DD` date form.

```yaml
# product
product_name: <YourProduct>

# git integration (defaults suit most GitHub projects)
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

# session logs (defaults assume log_dir = sessions)
log_dir: sessions
log_archive: sessions/archive
log_index: sessions/INDEX.md
log_pattern: "{date}_session_{n}[_{suffix}].md"   # date = YYYY-MM-DD
log_glob: "sessions/[0-9]*_session*.md"
log_presence_regex: '^sessions/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_session.*\.md$'

# build / test gate (REQUIRED: set to your project's commands; run in order, abort on first failure)
code_globs: ["<glob that marks a code change, e.g. *.ts>"]
build_commands: [<your build command, e.g. npm run build>]
test_commands:
  - <your test command, e.g. npm test>
subpkg_guard: none                   # path that gates a trailing test_commands entry; none if not used

# merge
merge_strategy: merge                # gh pr merge --merge; alternatives: squash | rebase

# prose gate (optional; none disables the step)
prose_gate: none                     # e.g. bin/check-prose.sh
prose_rule: none

# code review (optional; none disables the step)
code_reviewer: none                  # subagent name under .claude/agents/
review_command: none                 # e.g. "/code-review high"

# commit / PR convention
commit_convention: "prefix(topic): short description"
commit_trailers: none                # e.g. none, or a Co-Authored-By policy
subject_max: 72

# project knowledge & docs
issues_file: none                    # e.g. knowledge/decisions/issues.md
research_dir: research               # scanned recursively by report
reports_dir: reports                 # report output
jargon_terms: []                     # project/platform terms to strip from plain-mode reports
plan_doc: none                       # e.g. IMPLEMENTATION_PLAN.md
workflow_rule: .claude/rules/workflow.md   # the lifecycle invariants doc (see kit README: companion file you provide)
scratch_paths: [.claude/settings.local.json]   # known untracked noise to ignore
```
