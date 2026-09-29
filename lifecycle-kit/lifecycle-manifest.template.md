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
projects; change them only if your conventions differ. A project on Forgejo or
Gitea sets `forge: forgejo`; a repo with no remote by design sets `forge: none`
and gets the local-merge lifecycle described in `forges/none.md`. The build/test gate and
the product name are the values you must set. Optional knobs accept `none`
(`prose_gate`, `code_reviewer`, `issues_file`, `plan_doc`, `subpkg_guard`); the
skill that reads each one skips its step. See `examples/untype-manifest.md` for a
filled, real-world manifest.

If you change `log_dir` away from `sessions`, update `log_glob`, `log_archive`,
and `log_presence_regex` to match: those encode the directory and the
`YYYY-MM-DD` date form.

## Commit messages

Two commands in the kit create a commit: the session-log commit in
`/session-end`, and the local merge under `forge: none`. Both build the message
from `commit_convention` and `commit_trailers`, so a project's own rules reach
every commit the kit makes.

`commit_convention` is the subject pattern. The log commit fills it with type
`docs`, topic `sessions`, and a short description, so
`prefix(topic): short description` gives
`docs(sessions): add session 8 log for commit trailers`, and a convention with
no prefix, `short description`, gives
`add session 8 log for commit trailers`. The skill adds nothing the pattern does
not name. A local merge keeps git's own subject, `Merge <branch>`, under any
convention.

`commit_trailers` is either `none` or one or more `Key: value` trailer lines
joined by ` + ` (space, plus, space). Three valid values:

- `none`
- `"Signed-off-by: Jane Doe <jane@example.com>"`
- `"Co-Authored-By: Claude <model> <noreply@anthropic.com> + Claude-Session: <url>"`

Split on ` + `; each piece is one trailer line, kept in the order written. Two
placeholders are resolved at commit time:

- `<url>` is the session URL from the session's commit attribution, the value
  Claude Code gives for its `Claude-Session:` line.
- `<model>` is the name of the model running the skill, for example `Opus 5.5`.

Any other angle-bracket text in a trailer, such as the email address above, is
literal. If a placeholder cannot be resolved, the skill stops and asks the user
for the value. It never commits without the trailer and never drops the line it
could not fill. A project that sets `commit_trailers` usually enforces them with
a `commit-msg` hook, and a merge that hook refuses is left staged and unfinished
in the primary checkout.

The trailers follow the subject as one more `-m` that holds all the lines,
newline-separated:

```bash
git commit -m "<subject>" -m "<trailer 1>
<trailer 2>"
```

A separate `-m` per trailer would put each line in its own paragraph, and git
reads only the last paragraph of a message as trailers, so every trailer but the
last would stop being one. With `commit_trailers: none` there is no second `-m`
and the message is the subject alone.

```yaml
# product
product_name: <YourProduct>

# git integration (defaults suit most GitHub projects)
remote: origin
integration_ref: origin/main         # remote integration branch (authoritative)
local_main: main                     # local integration branch
pr_base: main                        # base branch for the session PR
requires_remote: true                # finalize/cleanup need a fetchable remote + a PR

# forge — which provider the finalize lifecycle drives. Presets are in the
# kit's forges/ directory; each implements the same nine-verb contract, so
# switching provider is this one key. Defaults to github when absent.
forge: github                        # github | forgejo | none
forge_url: none                      # self-hosted base URL, e.g. https://git.example.ts.net
forge_repo: none                     # owner/name on the forge; unused by github (gh infers it)

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
# (both are defined under "Commit messages" above)
commit_convention: "prefix(topic): short description"   # subject pattern; "short description" for no prefix
commit_trailers: none                # none, or "Key: value + Key: value"; <url> and <model> are filled in
subject_max: 72

# project knowledge & docs
issues_file: none                    # e.g. knowledge/decisions/issues.md
research_dir: research               # scanned recursively by report
reports_dir: reports                 # report output
jargon_terms: []                     # project/platform terms to strip from plain-mode reports
plan_doc: none                       # e.g. IMPLEMENTATION_PLAN.md
workflow_rule: .claude/rules/workflow.md   # repo-relative invariants doc the skills cite; copy the kit's bundled rules/workflow.md here (or point at your own). The skills run without it.
scratch_paths: [.claude/settings.local.json]   # known untracked noise to ignore
```
