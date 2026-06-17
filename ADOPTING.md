# Adopting the kit in a repo

Two parts: install the plugins once per machine, then set up each repo. The
per-repo setup is mostly one manifest file, and the paste-to-Claude prompt below
writes it for you by inspecting the repo.

## 1. Install the plugins (once per machine)

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install lifecycle-kit@ostin-pil-plugins
/plugin install prose-mint@ostin-pil-plugins
/plugin install knowledge-kit@ostin-pil-plugins
```

The plugins are user-scoped, so once installed they're available in every
project. To try the marketplace from a local checkout before it's on GitHub:
`/plugin marketplace add ~/Projects/claude-plugins`.

## 2. Set up a repo (paste this to Claude Code from the repo root)

> Set this repo up to use the lifecycle-kit, prose-mint, and knowledge-kit plugins.
>
> 1. If `/session-start` isn't available, install the plugins first (see the marketplace add + install commands in the kit's ADOPTING.md).
> 2. Inspect the repo to infer the **build command(s)**, the **test command(s)**, and a **glob that marks a code change** (e.g. `*.ts`, `*.go`, `*.py`, `*.rs`). Read whatever manifest exists: `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `Package.swift`, `Makefile`, `build.gradle`. If ambiguous, ask me before guessing.
> 3. Create `.claude/lifecycle-manifest.md`: start from lifecycle-kit's `lifecycle-manifest.template.md`, then append knowledge-kit's `manifest-keys.md` block. Fill `product_name`, `build_commands`, `test_commands`, `code_globs`, `knowledge_dir`, `issues_file`, and `log_dir`. Keep the git/branch/worktree/log defaults unless this repo's conventions differ. Set every optional knob (`prose_gate`, `code_reviewer`, `plan_doc`, `subpkg_guard`, and all `archive_*`) to `none` unless the repo already has that thing. Wire `prose_gate` to prose-mint only if I want the prose gate enforced.
> 4. Ask me whether to copy the optional knowledge-kit templates: the `knowledge/` skeleton (routing README + empty `issues.md`/`open-decisions.md`), the generic `prose-style` rule into `.claude/rules/`, and the two git hooks into `.git/hooks/` (`chmod +x` them). Only copy what I confirm and what doesn't already exist.
> 5. Confirm a GitHub remote exists (`git remote -v`). The finalize lifecycle (`session-end`, `finalize-worktree`, `cleanup-worktrees`) requires one; without it only `report` and the read-only half of session-start/report work.
> 6. Show me the resulting `.claude/lifecycle-manifest.md` and a one-line summary of what you set, what you copied, and what I should review. Don't commit anything until I've reviewed it.

## 3. Manual fallback

If you'd rather do it by hand:

1. Copy `lifecycle-kit/lifecycle-manifest.template.md` to
   `.claude/lifecycle-manifest.md`, then append the YAML block from
   `knowledge-kit/manifest-keys.md` inside the same fence.
2. Edit `product_name`, `build_commands`, `test_commands`, `code_globs`,
   `knowledge_dir`, `issues_file`. The rest of the defaults suit most GitHub
   projects.
3. Optional: copy `knowledge-kit/templates/knowledge/` to `./knowledge/`, the
   `prose-style` rule to `.claude/rules/`, and the git hooks to `.git/hooks/`
   (`chmod +x`). See `knowledge-kit/README.md` for the exact commands.

## What each plugin needs from the repo

| Plugin | Required | Optional |
| --- | --- | --- |
| lifecycle-kit | `.claude/lifecycle-manifest.md` with `product_name`, `build_commands`, `test_commands`, `code_globs`; a GitHub remote | tune git/branch/log keys |
| prose-mint | nothing | a `.prose-mint.toml` for per-repo scope and thresholds |
| knowledge-kit | the `knowledge_*` / `issues_file` keys appended to the manifest | the `knowledge/` skeleton, the prose-style rule, the git hooks, the `archive_*` keys |

## Preconditions

A GitHub remote is required for the finalize lifecycle (lifecycle-kit is
remote-only by design). A no-remote repo can still run `report`, `knowledge-audit`,
`session-archive`, and `issues`, plus the read-only half of session-start and
session-report.
