# CLAUDE.md Rules and Memory System -- Comprehensive Reference

Research compiled April 2026. Based on official Claude Code documentation and community best practices.

---

## 1. File Loading Order and Precedence

Claude Code loads instruction files from multiple scopes. All discovered files are **concatenated into context** rather than overriding each other. More specific locations take precedence over broader ones because they appear later in the context window (last-read wins for conflicting instructions).

### The Full Hierarchy (broadest to most specific)

| Priority | Scope | Location | Shared With |
|----------|-------|----------|-------------|
| 1 (lowest) | **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | All users on machine (deployed by IT) |
| 2 | **User instructions** | `~/.claude/CLAUDE.md` | Just you, all projects |
| 3 | **User rules** | `~/.claude/rules/*.md` | Just you, all projects |
| 4 | **Project instructions** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via source control |
| 5 | **Project rules** (unconditional) | `./.claude/rules/*.md` (no `paths` frontmatter) | Team via source control |
| 6 | **Local instructions** | `./CLAUDE.local.md` | Just you, current project |
| 7 (highest) | **Subdirectory CLAUDE.md** | `./subdir/CLAUDE.md` | Team via source control (loaded on demand) |

### How Merging Works

- Files are **concatenated**, not merged or overridden. Every loaded file contributes to context.
- Within each directory level, `CLAUDE.local.md` is appended **after** `CLAUDE.md`, so personal notes are the last thing Claude reads at that level.
- User-level rules (`~/.claude/rules/`) load **before** project rules, giving project rules higher effective priority.
- Managed policy CLAUDE.md **cannot be excluded** by individual settings. It always applies.
- When instructions conflict, Claude may pick one arbitrarily. The last-read instruction has a slight edge due to recency bias in the context window.

### Directory Tree Walking

Claude Code walks **up** the directory tree from the current working directory, loading `CLAUDE.md` and `CLAUDE.local.md` at each level. If you run Claude in `foo/bar/`, it loads:

1. `foo/CLAUDE.md` + `foo/CLAUDE.local.md`
2. `foo/bar/CLAUDE.md` + `foo/bar/CLAUDE.local.md`

Files in **ancestor directories** above the working directory are loaded in full at launch. Files in **subdirectories** below the working directory load **on demand** when Claude reads files in those subdirectories.

### Excluding Files in Monorepos

The `claudeMdExcludes` setting skips specific files by path or glob pattern:

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

This can be configured at any settings layer (user, project, local, managed policy). Arrays merge across layers. Managed policy CLAUDE.md files cannot be excluded.

### Additional Directories

The `--add-dir` flag gives Claude access to directories outside the main working directory. By default their CLAUDE.md files are **not** loaded. Set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to include them:

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

`CLAUDE.local.md` files in additional directories are never loaded.

---

## 2. Path-Specific Rules (.claude/rules/)

### Structure

Place markdown files in `.claude/rules/`. Each file covers one topic. Files are discovered **recursively**, so subdirectories work:

```
your-project/
  .claude/
    CLAUDE.md
    rules/
      code-style.md       # Unconditional (no paths frontmatter)
      testing.md
      frontend/
        react-patterns.md # Path-scoped
      backend/
        api-design.md     # Path-scoped
      security.md
```

### Path Scoping with YAML Frontmatter

Add a `paths` field in YAML frontmatter to scope rules to specific files. Without `paths`, rules load unconditionally at launch (same priority as `.claude/CLAUDE.md`).

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

### When Path-Scoped Rules Activate

Path-scoped rules trigger **when Claude reads files matching the pattern**, not on every tool use. If Claude never opens a file matching `src/api/**/*.ts`, that rule never loads.

### Glob Pattern Reference

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root only |
| `src/components/*.tsx` | React components in one specific directory |
| `src/**/*.{ts,tsx}` | Brace expansion for multiple extensions |

Multiple patterns can be combined:

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

### Symlinks for Sharing Rules

The `.claude/rules/` directory supports symlinks. You can maintain a shared rule set and link it into multiple projects:

```bash
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```

Circular symlinks are detected and handled gracefully.

### Difference from Cursor

Cursor uses `globs:` in frontmatter; Claude Code uses `paths:`. The functionality is similar but the syntax differs.

---

## 3. @import Syntax

### Basic Usage

CLAUDE.md files can import additional files using `@path/to/file` syntax. Imported files are expanded and loaded into context at launch alongside the CLAUDE.md that references them.

```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

### Path Resolution

- **Relative paths** resolve relative to the file containing the import, not the working directory.
- **Absolute paths** are allowed.
- **Home directory expansion** works: `@~/.claude/my-instructions.md`.

### Nesting Depth

Imported files can recursively import other files, with a **maximum depth of five hops**. This prevents infinite recursion while allowing reasonable decomposition.

### Security: First-Time Approval

The first time Claude Code encounters external imports in a project, it shows an approval dialog listing the files. If you decline, the imports stay disabled and the dialog does not appear again.

### AGENTS.md Compatibility

If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

### Cross-Worktree Imports

A gitignored `CLAUDE.local.md` only exists in the worktree where you created it. To share personal instructions across worktrees, import from your home directory:

```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

---

## 4. Writing Effective Rules

### Size Target

Target **under 200 lines** per CLAUDE.md file. Longer files consume more context and reduce adherence. Claude Code's system prompt consumes roughly 50 of the approximately 150-200 effective instruction slots before compliance degrades. That leaves around 100 slots for your rules.

### The Litmus Test

For each line, ask: **"Would removing this cause Claude to make mistakes?"** If not, cut it.

### What to Include vs Exclude

| Include | Exclude |
|---------|---------|
| Bash commands Claude cannot guess | Anything Claude can figure out by reading code |
| Code style rules that differ from defaults | Standard language conventions Claude already knows |
| Testing instructions and preferred runners | Detailed API documentation (link instead) |
| Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
| Architectural decisions specific to your project | Long explanations or tutorials |
| Developer environment quirks (required env vars) | File-by-file descriptions of the codebase |
| Common gotchas or non-obvious behaviors | Self-evident practices like "write clean code" |

### Specificity Over Vagueness

Write instructions that are concrete enough to verify:

- **Good**: "Use 2-space indentation"
- **Bad**: "Format code properly"
- **Good**: "Run `npm test` before committing"
- **Bad**: "Test your changes"
- **Good**: "API handlers live in `src/api/handlers/`"
- **Bad**: "Keep files organized"

### Emphasis for Critical Rules

Adding emphasis markers like "IMPORTANT" or "YOU MUST" or "NEVER" improves adherence for critical rules. Use sparingly -- if everything is emphasized, nothing is.

### Structure

Use markdown headers and bullets to group related instructions. Claude scans structure the same way a human reader does. Organized sections are easier to follow than dense paragraphs.

### Example of a Well-Written CLAUDE.md

```markdown
# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, not the whole test suite, for performance

# Architecture
- State machine in AppState.swift drives all UI -- never mutate UI directly
- All async work uses Swift concurrency (async/await), not Combine

# Rules
- NEVER use storyboards or XIBs -- all UI is programmatic
- NEVER add dependencies beyond HotKey unless explicitly discussed
- Keep each Swift file under 200 lines -- split if larger
```

### Negative-Space Instructions

"NEVER do X" rules are effective. They define boundaries Claude should not cross:

```markdown
- NEVER use Combine -- use async/await and @Observable
- NEVER commit .env files or credentials
- NEVER run terraform destroy without explicit user instruction
```

These work well because they are unambiguous -- there is no room for interpretation.

---

## 5. Anti-Patterns

### The Kitchen Sink CLAUDE.md

**Problem**: File grows to 500+ lines. Important rules get lost in noise. Claude ignores half of it.

**Fix**: Ruthlessly prune. Split into `.claude/rules/` files with path scoping. Use `@import` for detailed content. If Claude already does something correctly without the instruction, delete the instruction.

### Fighting Hardcoded Defaults

**Problem**: Writing rules that try to override Claude's built-in behaviors or system prompt instructions. For example, telling Claude to "always respond in a specific persona" when the system prompt already defines its behavior.

**Fix**: Focus on project-specific context that Claude cannot know. Do not try to change fundamental model behavior through CLAUDE.md.

### Rules That Should Be Hooks

**Problem**: Critical rules like "always run linting after file edits" placed in CLAUDE.md. CLAUDE.md is advisory (approximately 80% compliance). Claude may skip it.

**Fix**: If something must happen every time with zero exceptions, make it a hook in `settings.json`. Hooks are deterministic (100% execution). Use CLAUDE.md for guidance, hooks for guarantees.

### Duplicate Information

**Problem**: Repeating what Claude can discover by reading the codebase. Describing every file and its purpose. Restating standard language conventions.

**Fix**: Only document what is non-obvious. Claude can read `package.json` itself. Tell it the things it would get wrong without your help.

### Conflicting Instructions

**Problem**: Two CLAUDE.md files (or a CLAUDE.md and a rule) give contradictory guidance. Claude picks one arbitrarily.

**Fix**: Review all instruction sources periodically. In monorepos, use `claudeMdExcludes` to skip irrelevant files from other teams.

### Stale Instructions

**Problem**: CLAUDE.md references files, patterns, or conventions that no longer exist in the codebase.

**Fix**: Treat CLAUDE.md like code. Review it during code review. Prune it regularly. Test changes by observing whether Claude's behavior actually shifts.

### Context Waste

**Problem**: Long tutorials, explanations, or documentation embedded directly in CLAUDE.md. Every token consumed by CLAUDE.md is a token unavailable for conversation.

**Fix**: Link to documentation rather than embedding it. Use `@import` for detailed content that only some sessions need. Use skills for domain knowledge that is only sometimes relevant.

---

## 6. Auto Memory System

### Overview

Auto memory lets Claude accumulate knowledge across sessions without manual effort. Claude saves notes about build commands, debugging insights, architecture, code style preferences, and workflow habits. It decides what is worth remembering based on whether the information would be useful in a future conversation.

### Storage Location

Each project gets its own memory directory:

```
~/.claude/projects/<project>/memory/
  MEMORY.md            # Concise index, loaded every session
  debugging.md         # Detailed notes (loaded on demand)
  api-conventions.md   # Topic files Claude creates as needed
```

The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory. Outside a git repo, the project root is used.

### The 200-Line / 25KB Limit

The first **200 lines** of `MEMORY.md`, or the first **25KB** (whichever comes first), are loaded at the start of every conversation. Content beyond that threshold is **not loaded** at session start.

This limit applies only to `MEMORY.md`. CLAUDE.md files are loaded in full regardless of length (though shorter files produce better adherence).

Claude keeps `MEMORY.md` concise by moving detailed notes into separate topic files, which are read on demand using standard file tools.

### CLAUDE.md vs Auto Memory

| | CLAUDE.md | Auto Memory |
|---|---|---|
| **Who writes it** | You | Claude |
| **What it contains** | Instructions and rules | Learnings and patterns |
| **Scope** | Project, user, or org | Per working tree |
| **Loaded into** | Every session (full file) | Every session (first 200 lines / 25KB) |
| **Use for** | Coding standards, workflows, architecture | Build commands, debugging insights, discovered preferences |

### Enabling / Disabling

Auto memory is on by default (requires Claude Code v2.1.59+). Toggle via:

- `/memory` command in a session
- `autoMemoryEnabled` in project settings
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` environment variable

### Custom Storage Location

Set `autoMemoryDirectory` in user or local settings (not accepted from project settings for security reasons):

```json
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

### Editing Memory

Auto memory files are plain markdown. Edit or delete them at any time. Use `/memory` to browse and open files from within a session.

When you say "remember X" to Claude, it saves to auto memory. To write to CLAUDE.md instead, say "add this to CLAUDE.md" explicitly, or edit via `/memory`.

---

## 7. CLAUDE.md as Living Documentation

### The Correction Loop

The most effective pattern for maintaining CLAUDE.md:

1. Claude makes a mistake.
2. You correct Claude in conversation.
3. If the same mistake would happen next session, add a rule to CLAUDE.md.
4. If Claude makes the same mistake a second time despite the rule, check whether the file is too long (rule lost in noise) or the instruction is ambiguous.

### When to Add to CLAUDE.md

Add when:

- Claude makes the same mistake a second time
- A code review catches something Claude should have known
- You type the same correction or clarification you typed last session
- A new teammate would need the same context to be productive

### Team Workflows

- **Check CLAUDE.md into git** so the whole team contributes and benefits.
- Review CLAUDE.md changes in PRs the same way you review code changes.
- Use `CLAUDE.local.md` (gitignored) for personal preferences that should not affect teammates.
- The file compounds in value over time as the team discovers more edge cases and conventions.

### Surviving Compaction

Project-root CLAUDE.md **survives compaction**: after `/compact`, Claude re-reads it from disk and re-injects it. Nested CLAUDE.md files in subdirectories are **not** re-injected automatically; they reload the next time Claude reads a file in that subdirectory.

Instructions given only in conversation will be lost after compaction. Add conversation-only instructions to CLAUDE.md to make them persist.

You can customize compaction behavior in CLAUDE.md itself:

```markdown
When compacting, always preserve the full list of modified files and any test commands.
```

---

## 8. Interaction with Other Systems

### CLAUDE.md vs Hooks

| Concern | Use |
|---------|-----|
| Behavioral guidance ("prefer X over Y") | CLAUDE.md |
| Hard enforcement ("always lint after edit") | Hooks (settings.json) |
| Compliance: ~80% | CLAUDE.md |
| Compliance: 100% | Hooks |

CLAUDE.md is delivered as a **user message** after the system prompt, not as part of the system prompt itself. For system-prompt-level instructions, use `--append-system-prompt` (must be passed every invocation).

### CLAUDE.md vs Skills

| Concern | Use |
|---------|-----|
| Always-on context (every session) | CLAUDE.md |
| On-demand domain knowledge | Skills (.claude/skills/) |
| Task-specific workflows | Skills |
| Multi-step procedures | Skills |

Skills load when invoked or when Claude determines they are relevant. CLAUDE.md loads every session. If an instruction is only relevant sometimes, it wastes context in CLAUDE.md but works well as a skill.

### CLAUDE.md vs Settings

| Concern | Use |
|---------|-----|
| Block specific tools, commands, or file paths | Settings: `permissions.deny` |
| Enforce sandbox isolation | Settings: `sandbox.enabled` |
| Code style and quality guidelines | CLAUDE.md |
| Behavioral instructions for Claude | CLAUDE.md |

Settings rules are enforced by the client regardless of what Claude decides. CLAUDE.md instructions shape behavior but are not a hard enforcement layer.

### CLAUDE.md vs Subagents

Subagents can maintain their own auto memory. For investigations that read many files, delegate to a subagent to avoid polluting your main context. The subagent reports back a summary without the individual file reads cluttering your conversation.

### The InstructionsLoaded Hook

Use the `InstructionsLoaded` hook to log exactly which instruction files are loaded, when they load, and why. This is particularly useful for debugging path-specific rules or lazy-loaded files in subdirectories.

---

## 9. Real-World CLAUDE.md Examples

### Minimal Effective Example (Small Project)

```markdown
# Build
- `npm run dev` starts the dev server on port 3000
- `npm test` runs Jest; prefer single-file runs for speed

# Style
- TypeScript strict mode, no `any`
- Use ES modules, not CommonJS
- Functional components with hooks, no class components

# Rules
- NEVER commit .env files
- Run typecheck after code changes
```

### Production Backend Example

```markdown
# Project
FastAPI service. Python 3.12. PostgreSQL + Redis.

# Commands
- `make test` -- runs pytest with coverage
- `make lint` -- runs ruff + mypy
- `make migrate` -- applies Alembic migrations

# Architecture
- Handlers in src/api/routes/, business logic in src/services/
- All DB access through repository pattern in src/repositories/
- Background tasks use Celery, defined in src/tasks/

# Rules
- NEVER write raw SQL outside src/repositories/
- NEVER skip type annotations on public functions
- All new endpoints require OpenAPI docstrings
- Always run `make lint` before committing

# Testing
- Use pytest fixtures, not setUp/tearDown
- Mock external services, never hit real APIs in tests
- Test files mirror src/ structure in tests/
```

### Monorepo Example

```markdown
# Monorepo: acme-platform
Turborepo. Node 20. pnpm workspaces.

# Packages
- apps/web -- Next.js frontend
- apps/api -- Express backend
- packages/ui -- shared component library
- packages/db -- Prisma schema and client

# Commands
- `pnpm turbo run build --filter=<package>` -- build one package
- `pnpm turbo run test --filter=<package>` -- test one package
- `pnpm lint` -- lint everything

# Rules
- NEVER import from apps/ into packages/
- Shared types go in packages/types/
- New components in packages/ui/ require Storybook stories
```

### Infrastructure / Safety-Critical Example

```markdown
# Infrastructure
Terraform + AWS. Three environments: dev, staging, prod.

# Commands
- `terraform plan -var-file=env/<env>.tfvars`
- `terraform apply` (dev only without approval)

# CRITICAL SAFETY RULES
- NEVER run `terraform destroy` without explicit user instruction
- NEVER modify prod tfvars without showing the plan first
- NEVER commit AWS credentials or secrets
- Always show plan output to user before suggesting apply
- Changes to IAM policies require explicit confirmation
```

---

## Sources

- [How Claude remembers your project -- Official Docs](https://code.claude.com/docs/en/memory)
- [Best Practices for Claude Code -- Official Docs](https://code.claude.com/docs/en/best-practices)
- [Claude Code settings -- Official Docs](https://code.claude.com/docs/en/settings)
- [Claude Code Rules: Stop Stuffing Everything into One CLAUDE.md](https://medium.com/@richardhightower/claude-code-rules-stop-stuffing-everything-into-one-claude-md-0b3732bca433)
- [CLAUDE.md Examples and Best Practices 2026](https://www.morphllm.com/claude-md-examples)
- [The Full CLAUDE.md Hierarchy](https://www.rushis.com/the-full-claude-md-hierarchy-from-enterprise-policy-to-subdirectory-rules/)
- [Claude Code Best Practices: Lessons From Real Projects](https://ranthebuilder.cloud/blog/claude-code-best-practices-lessons-from-real-projects/)
- [How Claude Code rules actually work](https://joseparreogarcia.substack.com/p/how-claude-code-rules-actually-work)
- [Claude Code Gets Path-Specific Rules](https://paddo.dev/blog/claude-rules-path-specific-native/)
- [Anatomy of the .claude Folder](https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/)
- [Claude Code Hooks and Skills Guide](https://genaiunplugged.substack.com/p/claude-code-skills-commands-hooks-agents)
- [CLAUDE.md Mastery](https://claudefa.st/blog/guide/mechanics/claude-md-mastery)
