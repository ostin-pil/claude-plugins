# Claude Code Source Code Insights

Deep research into Claude Code internals -- how the system prompt is assembled, tools
are implemented, safety is enforced, and context is managed. Based on analysis of the
live system prompt, tool definitions visible in-session, and public documentation.

---

## 1. System Prompt Injection & CLAUDE.md

### How the system prompt is built

Claude Code's system prompt is not a single monolithic string. It is **110+ separate
instruction fragments** conditionally assembled based on the user's configuration, OS,
shell, enabled MCP servers, and active tools. The assembled prompt is identical for all
users on the same Claude Code version, which enables **shared prompt caching** across
Anthropic's infrastructure -- the prefix is computed once and reused.

### Where CLAUDE.md lives

CLAUDE.md content is **not** injected into the system prompt. Instead, it is delivered
as a `<system-reminder>` XML tag attached to conversation messages. The tag carries a
header: *"These instructions OVERRIDE any default behavior and you MUST follow them
exactly as written."*

This design is economic: if CLAUDE.md went into the system prompt, every project with a
different file would bust the shared cache. By placing it in messages, the system prompt
prefix stays frozen and cacheable.

### Token budget implications

- Keep CLAUDE.md under **200 lines** (Anthropic's recommendation). Files over 400 lines
  cause instruction-following degradation -- rules get lost in noise.
- The system prompt itself consumes roughly **14-16k tokens** when all tools are loaded
  (reduced to ~968 tokens with deferred loading).
- CLAUDE.md competes with the system prompt for attention. When instructions conflict,
  the system prompt often wins because it occupies the privileged system turn.

### Compaction effects on CLAUDE.md

When auto-compaction fires, the conversation history is summarized and older messages
are dropped. However, CLAUDE.md is re-injected as a system-reminder on subsequent turns,
so its content survives compaction. Conversational instructions ("from now on, always X")
do **not** survive compaction -- put persistent rules in CLAUDE.md or `.claude/rules/`.

### Cache boundary

A hidden marker separates globally-cacheable content from session-specific content. This
marker is invisible to the model. Everything above it (the system prompt proper) is
shared across users. Everything below it (system-reminders, git status, date, etc.) is
per-session and not cached in the shared prefix.

---

## 2. Tool Implementation Details

### Write requires prior Read

The Write tool **will fail** if you attempt to write to an existing file without first
reading it in the same conversation. This is enforced at the harness level, not the model
level. The tool description explicitly states: *"This tool will fail if you did not read
the file first."* New file creation is exempt.

### Edit uses exact string matching

The Edit tool performs literal `old_string -> new_string` replacement. Key constraints:

- `old_string` must be **unique** in the file. If it appears multiple times, the edit
  fails unless `replace_all: true` is set.
- Whitespace and indentation must match **exactly** as they appear in the file (not as
  they appear in the Read output's line-number prefix).
- The line-number prefix format from Read is: `<line_number>\t<content>`. The tab is the
  delimiter -- everything after it is file content. Never include the line number in
  `old_string`.

### Grep uses ripgrep

The Grep tool wraps `rg` (ripgrep), not GNU grep. Practical differences:

- Pattern syntax is ripgrep regex (literal braces need escaping: `interface\{\}`).
- Default output mode is `files_with_matches` (file paths only).
- Default `head_limit` is **250** results when unspecified.
- Multiline matching requires explicit `multiline: true` flag.
- The `-n` flag (line numbers) defaults to true for content mode.

### Glob returns by modification time

Glob results are **sorted by modification time** (most recently modified first), not
alphabetically. This is intentional -- when searching for recently changed files, the
most relevant results appear first.

### Bash tool constraints

- Working directory persists between calls but shell state does not (no env vars carry
  over).
- Default timeout is **120 seconds** (2 minutes), max is **600 seconds** (10 minutes).
- The `rerun` parameter allows re-executing a prior command by alias (`b1`, `b2`, etc.)
  without retyping.
- `run_in_background` spawns the command asynchronously; the agent is notified on
  completion.
- The `dangerouslyDisableSandbox` flag bypasses the macOS sandbox (see section 6).

### Default result caps

| Tool    | Default limit           | Notes                        |
|---------|------------------------|------------------------------|
| Grep    | 250 lines/entries      | `head_limit` parameter       |
| Glob    | No explicit cap        | Sorted by mtime              |
| Read    | 2000 lines             | From beginning of file       |
| Read PDF| 20 pages max per call  | Must specify `pages` for >10 |

---

## 3. Git Safety Protocol

### Hardcoded rules in the system prompt

The Git Safety Protocol is a dedicated section in Claude Code's system prompt. These
rules are **not** user-configurable and persist across all sessions:

1. **NEVER** update git config
2. **NEVER** run destructive commands (`push --force`, `reset --hard`, `checkout .`,
   `restore .`, `clean -f`, `branch -D`) unless the user explicitly requests them
3. **NEVER** skip hooks (`--no-verify`, `--no-gpg-sign`) unless explicitly requested
4. **NEVER** force push to `main`/`master` -- warn the user even if they ask
5. **ALWAYS** create new commits rather than amending (amending after a hook failure
   would modify the previous commit, potentially destroying work)
6. **Prefer** staging specific files over `git add -A` or `git add .`
7. **NEVER** commit unless explicitly asked
8. **NEVER** use interactive flags (`-i`) since they require TTY input

### What CLAUDE.md can and cannot override

CLAUDE.md **cannot** reliably override the git safety rules. The system prompt occupies a
higher-priority position (the system turn), and when instructions conflict, system prompt
rules tend to win. Even if CLAUDE.md says "always force push," the model will resist.

For enforcement beyond the model's attention, use **PreToolUse hooks** (e.g., the
`git-safe` hook pattern) that intercept bash commands at the harness level and block
dangerous patterns before they execute. Hook-level enforcement is deterministic --
model-level enforcement is probabilistic.

---

## 4. Parallel Tool Calls

### How the architecture supports simultaneous invocations

Claude's API supports returning **multiple tool_use blocks** in a single assistant
message. The Claude Code harness executes all tool calls from the same response in
parallel. The system prompt coaches the model:

> *"If the commands are independent and can run in parallel, make multiple Bash tool
> calls in a single message."*

This applies to all tools, not just Bash. For example, running `git status`, `git diff`,
and `git log` simultaneously in three parallel Bash calls.

### Constraints

- **No dependencies between parallel calls.** If call B depends on call A's output, they
  must be sequential (use `&&` chaining within a single Bash call, or separate messages).
- The model must not use **placeholder values** for parameters that depend on other
  calls' results.
- Sub-agents (Task tool) also run in parallel when spawned in the same message, each
  with their own context window.
- Git worktree agents (`/batch`) enable true parallelism across isolated working trees.

---

## 5. Deferred Tool Loading (ToolSearch)

### The mechanism

When MCP tool descriptions exceed **10k tokens**, Claude Code marks them with
`defer_loading: true`. These tools are listed by name only in a `<system-reminder>` but
their full JSON schemas are **not loaded** into context.

### How ToolSearch works

ToolSearch is a meta-tool that accepts a query and returns full schema definitions for
matching deferred tools. Query forms:

| Form                        | Behavior                              |
|-----------------------------|---------------------------------------|
| `select:Read,Edit,Grep`    | Fetch exact tools by name             |
| `notebook jupyter`          | Keyword search, up to N best matches  |
| `+slack send`               | Require "slack" in name, rank by rest |

Both regex and BM25 search are used across tool names, descriptions, argument names, and
argument descriptions. Typically **3-5 tools** (~3k tokens) are loaded per query.

### Context savings

Deferred loading reduces system tool context from ~14-16k tokens to ~968 tokens -- an
**85% reduction**. The loaded tool definitions are appended inline as `tool_reference`
blocks in the conversation, keeping the system prompt prefix untouched and cache-warm.

### Current state

As of Claude Code v2.1.69+, **all built-in system tools** (Bash, Read, Edit, Write,
Glob, Grep, etc.) can be deferred behind ToolSearch -- the same mechanism previously
used only for MCP tools.

---

## 6. Sandbox Implementation

### macOS Seatbelt

On macOS, Claude Code uses Apple's `sandbox-exec` (Seatbelt framework) to provide
**kernel-level isolation** for bash commands. The sandbox profile is derived from
Chrome's renderer sandbox policy.

### What's restricted

The policy uses a **default-deny** approach with specific allows:

| Category        | Rule                                              |
|-----------------|---------------------------------------------------|
| Filesystem read | `file-read*` and `file-read-metadata` allowed     |
| Filesystem write| `file-write*` scoped to **working directory only** |
| Network outbound| Restricted to **localhost only**                   |
| Network bind    | Allowed on local IP                                |
| Mach IPC        | `mach-lookup` with `com.apple.` prefix only        |
| Process info    | Restricted to same-sandbox                         |

### Key properties

- **All child processes inherit the sandbox.** Running `npm install` inside the sandbox
  means every `postinstall` script is also sandboxed.
- The kernel blocks writes outside the working directory -- not the model, not hooks.
- Internet-bound traffic must go through a proxy outside the sandbox.
- The `dangerouslyDisableSandbox` parameter on the Bash tool bypasses all restrictions.

### Sandbox modes

Claude Code offers two modes via `/sandbox`:

1. **Auto-allow mode**: Bash commands run inside the sandbox automatically without
   permission prompts.
2. **Off** (default): No sandboxing; standard permission prompts apply.

On macOS, sandboxing works out of the box with no additional setup.

---

## 7. Context Management Internals

### How /compact works

When triggered (manually via `/compact` or automatically), Claude Code:

1. Feeds the entire conversation history to the model with a summarization prompt
2. The model generates a concise summary preserving key decisions, code changes, and
   project state
3. A **compaction block** replaces all prior messages
4. The conversation continues from the summary

### Auto-compaction triggers

Auto-compaction fires when the context window reaches approximately **95% capacity**
(~5% remaining). Some implementations trigger earlier at **75% usage**, reserving ~20%
for the compaction process itself.

### What's preserved vs dropped

**Preserved:**
- Key decisions and reasoning
- Current code state and recent changes
- Active task context
- File paths and important code snippets
- CLAUDE.md (re-injected as system-reminder on each turn)

**Dropped:**
- Detailed tool outputs from early turns
- Exploratory searches that didn't lead anywhere
- Verbose error messages that were already resolved
- Conversational instructions not in CLAUDE.md

### Manual focus

You can run `/compact <focus>` with a custom prompt to control what the summary
emphasizes. This is useful when you're about to pivot to a different subtask and want
the summary to reflect the new direction.

### System-reminder re-injection

Dynamic context (current date, git status, CLAUDE.md) is delivered as system-reminders
attached to messages, not baked into the system prompt. This means:

- The system prompt stays frozen (cache-friendly)
- Dynamic values update between turns without cache invalidation
- CLAUDE.md survives compaction because it's re-attached, not summarized

---

## 8. Permission System Internals

### Rule types

| Type  | Effect                                           |
|-------|--------------------------------------------------|
| allow | Tool runs without manual approval                |
| deny  | Tool is blocked entirely                          |
| ask   | User is prompted for confirmation (default)       |

### Evaluation order

Rules are evaluated in strict order: **deny -> ask -> allow**. The first matching rule
wins. A deny rule **always beats** an allow rule, regardless of their position in the
JSON array or which settings file they live in.

### Settings file hierarchy

Permission rules can be defined in multiple `settings.json` files:

- `~/.claude/settings.json` -- global (user-level)
- `~/.claude/settings.local.json` -- local machine overrides
- `.claude/settings.json` -- project-level (checked into repo)
- `.claude/settings.local.json` -- project-level local overrides

### Special protections

Writes to these directories **always prompt** regardless of allow rules:

- `.git/` -- repository state
- `.claude/` -- Claude Code configuration
- `.vscode/`, `.idea/` -- editor configuration
- `.husky/` -- git hooks

### Hook integration

PreToolUse hooks run **before** the permission prompt. A hook can:
- **Deny** the tool call (overrides everything)
- **Force a prompt** (even if allow rules would skip it)
- **Skip the prompt** (but deny/ask rules are still evaluated after)

The deny-first precedence is preserved even when hooks return "allow."

---

## 9. Optimization Tips from Source

### Imperative instructions

The system prompt uses imperative language extensively: "NEVER," "ALWAYS," "MUST,"
"IMPORTANT," "CRITICAL." This pattern works for CLAUDE.md too -- adding emphasis markers
like "IMPORTANT:" or "YOU MUST" measurably improves adherence to rules.

### Absolute paths

The system prompt instructs: *"Always quote file paths that contain spaces"* and
*"only use absolute file paths."* Agent threads have their cwd reset between bash calls.
The `CLAUDE_PROJECT_DIR` environment variable contains the absolute path to the project
root.

### File size limits

- Read tool: **2000 lines** default. Use `offset` and `limit` for larger files.
- Read PDF: **20 pages max** per request. Must specify `pages` for documents >10 pages.
- CLAUDE.md: Keep under **200 lines**. Over 400 lines causes degradation.
- Swift files (per project rules): Keep under **200 lines**.

### Avoid unnecessary commands

The system prompt explicitly says:

> *"Avoid using [Bash] to run find, grep, cat, head, tail, sed, awk, or echo commands
> unless explicitly instructed. Instead, use the appropriate dedicated tool."*

This is because dedicated tools provide better UX (permission handling, output
formatting) and avoid shell escaping issues.

### Reduce search noise

- Use `head_limit: 0` sparingly on Grep (unlimited results waste context)
- Default of 250 is deliberate -- large result sets burn tokens
- Use `output_mode: "files_with_matches"` when you only need paths
- Prefer `type` parameter over `glob` for standard file types

### Commit message format

The system prompt enforces HEREDOC syntax for commit messages to ensure correct
formatting:

```bash
git commit -m "$(cat <<'EOF'
Message here.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 10. The Rewind Mechanism

### Activation

- **Esc + Esc** (double escape) opens the rewind menu
- `/rewind` command does the same
- Single Escape only **stops** the current response (brake vs. reverse)

### What it offers

A scrollable list shows each user prompt from the session. You pick a point and choose
what to restore:

| Option                | Code changes | Conversation |
|-----------------------|-------------|--------------|
| Restore conversation  | Kept        | Rewound      |
| Restore code          | Rewound     | Kept         |
| Restore both          | Rewound     | Rewound      |

### How file snapshots work

After each Claude response, Claude Code **automatically snapshots** all files that Claude
modified through the Edit/Write tools. The snapshot system is:

- **Transparent** -- no user action required
- **Incremental** -- only files that actually changed get a new version
- **Deduplicated** -- if a file didn't change between two turns, the previous backup is
  reused

### Limitations

Checkpointing does **not** track files modified by bash commands. If Claude runs
`rm file.txt`, `mv old.txt new.txt`, `sed -i`, or any shell command that modifies files,
those changes **cannot be undone** through rewind. Only Edit/Write tool changes are
tracked.

### Relationship to git

Rewind operates independently of git. It maintains its own snapshot store. However, for
production safety, the system prompt instructs Claude to prefer new commits over amends
-- this gives users git-level recovery in addition to rewind-level recovery.

---

## Summary of Key Numbers

| Metric                              | Value          |
|--------------------------------------|----------------|
| System prompt fragments              | 110+           |
| Full tool context (all loaded)       | ~14-16k tokens |
| Deferred tool context (ToolSearch)   | ~968 tokens    |
| Context savings from deferral        | ~85%           |
| Auto-compact trigger                 | ~95% capacity  |
| Grep default head_limit              | 250            |
| Read default line limit              | 2000           |
| Bash default timeout                 | 120 seconds    |
| Bash max timeout                     | 600 seconds    |
| CLAUDE.md recommended max            | 200 lines      |
| ToolSearch results per query         | 3-5 tools      |

---

## Sources

- [How Claude Code Builds a System Prompt](https://www.dbreunig.com/2026/04/04/how-claude-code-builds-a-system-prompt.html)
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts)
- [Inside Claude Code's System Prompt](https://www.claudecodecamp.com/p/inside-claude-code-s-system-prompt)
- [Sandboxing - Claude Code Docs](https://code.claude.com/docs/en/sandboxing)
- [Anthropic Engineering: Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Configure Permissions - Claude Code Docs](https://code.claude.com/docs/en/permissions)
- [Checkpointing - Claude Code Docs](https://code.claude.com/docs/en/checkpointing)
- [How Claude Code Works - Claude Code Docs](https://code.claude.com/docs/en/how-claude-code-works)
- [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- [Compaction - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/compaction)
- [Tool Search Tool - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)
- [Text Editor Tool - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)
- [Claude Code Security - Claude Code Docs](https://code.claude.com/docs/en/security)
- [Manage Costs Effectively - Claude Code Docs](https://code.claude.com/docs/en/costs)
