# lifecycle-kit

Session lifecycle and reporting skills for Claude Code, driven by a single
per-project config file. The skills handle the repeating shape of focused work:
brief where a session left off, write and gate the session log, land the
session's one PR, sweep stale worktrees, and generate status reports.

## What this adds over built-in worktrees

Recent Claude Code (the 2.1.x line) already automates the mechanical parts of a
worktree session. Background agents commit, push, and open a draft PR when they
finish (2.1.198), stale agent worktrees are pruned once their PR merges
(2.1.105), and auto memory carries some context across sessions (2.1.32). This
kit is the layer those defaults leave out:

- A gated finalize. The session PR lands only after the project's own
  `build_commands` and `test_commands` pass; the built-in auto-PR opens a draft
  whether or not your gate is green.
- A refuse-under-ambiguity rule. When two branches or worktrees are equally
  plausible finalize targets, the skill stops and asks rather than guessing a
  tiebreak (the Evidence section shows why that matters).
- Session logs as durable, human-readable artifacts committed next to the code,
  rather than JSONL transcripts plus ephemeral memory.
- Manifest-driven status reports over git history, session logs, and research
  docs.

The native features are named by version so the boundary stays honest as they
move. Where the platform absorbs a step, the manifest lets you drop it.

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

The finalize lifecycle needs a forge, selected by the `forge` manifest key.
Presets live in `forges/` and each implements the same nine-verb contract, so
the provider is one key rather than a fork:

| `forge` | Transport | Needs a remote | Merge gate |
|---|---|---|---|
| `github` (default) | `gh` | yes | PR on GitHub |
| `forgejo` | `curl` + `jq`, `$FORGEJO_TOKEN` | yes | PR on Forgejo/Gitea |
| `none` | local git only | no | local, `--no-ff` |

`forge` defaults to `github` when absent, so manifests written before the key
existed keep working unchanged.

`none` supersedes what used to be a documented scope hole. A no-remote project
previously got `report` plus the read-only half of `session-start` and
`session-report` and nothing else, on the grounds that a local-merge fallback
would cross the never-merge-locally invariant. That invariant guards against
local/remote divergence, which needs two writers of one remote. It therefore
protects nothing on a repo that has no remote, while its absence left those
sessions finalizing by hand with no guard at all. `forges/none.md` sets out the
shape and what it genuinely costs.

A `SessionStart` hook (`hooks/validate-manifest.sh`) validates the manifest of a
project that has adopted the kit: required keys present, remote configured when
required, and the selected forge's own preconditions (`gh` on PATH, or `jq` plus
`forge_url`/`forge_repo`/`$FORGEJO_TOKEN`, or `merge_strategy: merge`). It
warns; it never blocks the session.

The kit is user-scoped, so the hook runs in every repo on the machine. A repo with
no `.claude/lifecycle-manifest.md` has simply not adopted the kit, which is the
resting state of most repos, so the hook stays **silent** there rather than warning
about setup nobody asked for. The skills raise the missing-manifest message
themselves when one is actually invoked, and offer to write the manifest from the
template.

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

## Evidence

The skills are benchmarked against a naive control in `benchmarks/lifecycle`.
Both arms run a fresh `claude -p --safe-mode` agent (no host config, plugin, or
hooks); the skill arm gets the skill procedure inlined, the control gets only
the task. Verdicts are ground-truth git state, never the agent's self-report.
N=3 per cell across Haiku 4.5, Sonnet 4.6, and Opus 4.8.

The load-bearing result is `ambiguous-finalize`. Asked to finalize when two
targets are equally plausible, the control refuses to guess only 1/3, 0/3, and
1/3 of the time (Haiku, Sonnet, Opus); the skill refuses 3/3 wherever it can
execute (Sonnet and Opus). This is capability the model lacks unaided at every
tier, Opus included: left to itself it invents a tiebreak two times in three.

The other cells are consistency rather than capability, and the README says so.
`branch-birth` is 0/3 control against 3/3 skill on Sonnet but a 3/3 tie on Opus,
because a strong agent reads the integration ref from the manifest on its own.
`cleanup-containment` even ties in the control's favor (3/3 against 2/3), and
the skill's one miss was conservative: it kept the worktree with unmerged work
and only under-swept. Full tables and the honest read are in
`benchmarks/lifecycle/ab/RESULTS.md`. The sample is small (N=3), and the value
is scenario by scenario, not a single headline number.

## Install

Distributed through the `claude-plugins` marketplace:

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@ostin-pil-plugins
```

Then do the per-project setup above (copy the manifest template and fill it).
