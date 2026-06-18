# lifecycle-kit

Session lifecycle and reporting skills for Claude Code, driven by a single
per-project config file. The skills handle the repeating shape of focused work:
brief where a session left off, write and gate the session log, land the
session's one PR, sweep stale worktrees, and generate status reports.

## What you get

Six skills, all invocable as slash commands:

| Skill | Does |
| --- | --- |
| `session-start` | Briefs where the project left off and opens a clean per-session branch off the integration ref |
| `session-report` | Writes or updates today's session log |
| `session-end` | Build/test gate, commits the log, finalizes the session PR, sweeps worktrees |
| `finalize-worktree` | Lands a feature-branch session as one merge-commit PR, then reconciles local state |
| `cleanup-worktrees` | Prunes worktrees and branches already contained in the integration ref |
| `report` | Generates a status report from git history, session logs, and research docs |

## How it is configured

Everything project-specific lives in one file the skills read at runtime:
`<repo>/.claude/lifecycle-manifest.md`. The skills' command bodies use `<key>`
placeholders; the model resolves each from that manifest. Claude Code has no
load-time templating, so resolution is the model reading the manifest (every
skill instructs it to); there is no automatic substitution step.

Setup in a project:

1. Copy `lifecycle-manifest.template.md` to `<repo>/.claude/lifecycle-manifest.md`.
2. Fill in `product_name`, `build_commands`, `test_commands`, and `code_globs`. The git, branch, worktree, and log defaults suit most GitHub projects.
3. Set or disable the optional knobs (`prose_gate`, `code_reviewer`, `issues_file`, `plan_doc`): a real value wires the step in, `none` skips it.

`examples/untype-manifest.md` is a filled, real-world manifest to copy from.

## Preconditions

A GitHub remote is required (`requires_remote: true`). `finalize-worktree`,
`session-end`'s finalize phase, and `cleanup-worktrees`' containment check all
need a fetchable remote reached through a `gh`-driven PR. A no-remote project can
run `report` plus the read-only half of `session-start` and `session-report`,
but not the finalize lifecycle; that is a deliberate scope choice, because a
local-merge fallback would cross the kit's never-merge-locally invariant.

A `SessionStart` hook (`hooks/validate-manifest.sh`) checks the manifest exists,
has the required keys, and that the remote is configured when required. It warns;
it never blocks the session.

## Bundled rules

The skills encode the lifecycle invariants directly (one PR per session, never
merge locally, one worktree per concurrent session, assert-then-reconcile, and
the REST-not-`gh pr edit` rule), so they run with no companion file. The full
statement of those invariants ships with the kit at `rules/workflow.md`, and the
skills cite it by the repo-relative path `.claude/rules/workflow.md`, which the
manifest's `workflow_rule` key defaults to. Copy the bundled file there if you
want the reference doc in your own repo:

```
cp <plugin>/rules/workflow.md .claude/rules/workflow.md
```

The default is that repo-relative path rather than
`${CLAUDE_PLUGIN_ROOT}/rules/workflow.md`, because `${CLAUDE_PLUGIN_ROOT}` does
not reliably expand in skill-body Bash (it does expand in hooks, which is why the
SessionStart hook still uses it). A repo-relative path resolves through the git
toplevel, the way the skills already reference it. Point `workflow_rule` at your
own path if you maintain a project-specific version.

## Install

Distributed through the `claude-plugins` marketplace:

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@ostin-pil-plugins
```

Then do the per-project setup above (copy the manifest template and fill it).
