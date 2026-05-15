# Claude Code Workflows & Optimization Research

*Compiled: 2026-04-08*

---

## 1. The Ralph Loop

**Creator:** Geoffrey Huntley | **Implementation:** [snarktank/ralph](https://github.com/snarktank/ralph)

The simplest autonomous workflow — a bash loop that repeatedly feeds Claude Code the same prompt:

```bash
while true; do cat PROMPT.md | claude; done
```

### How it works

- Each iteration gets a **fresh context window** (no context rot)
- State persists via filesystem: `prd.json` (task status), `progress.txt` (learnings), `AGENTS.md` (patterns)
- Each cycle: read PRD -> pick highest-priority incomplete task -> implement -> verify (tests/typecheck/build) -> commit -> exit for fresh restart
- Set max iterations (25-50 overnight) to cap costs

### Key principles

- The loop is the hero, not the model — persistent iteration beats clever prompting
- Every task needs **automated verification** (tests, lint, build) — without pass/fail signals, the loop can't self-correct
- Atomic tasks that fit in one context window
- Plan and implement in **separate sessions**

### Variations

- **Ryan Carson's snarktank/ralph** — PRD-driven with `prd.json`, `progress.txt`, `AGENTS.md`
- **Cole Medin's quickstart** — [ralph-loop-quickstart](https://github.com/coleam00/ralph-loop-quickstart)
- **Adam Tuttle's 3-script approach** — `plan`, `ralph`, `ralph-install` scripts in `~/.bin/`
- **Stop hook approach** — uses Claude Code's stop hook instead of bash loop
- **Subagent parallelization** (Huntley) — primary loop delegates to up to 500 parallel subagents, serializes validation

### Reported results

- $50K contract MVP delivered for $297 in tokens
- 9 features overnight with passing tests
- 80-95% overnight completion rate

### Common failure modes

| Problem | Cause | Fix |
|---------|-------|-----|
| Infinite loop | Impossible task or vague criteria | Set max_iterations, sharpen completion criteria |
| Early exit | Agent declares done prematurely | Strengthen verification requirements |
| Quality degradation | Context filling with failed attempts | Fresh context per iteration (the loop handles this) |
| Feature drift | Vague specifications | Make specs specific, define exclusions |
| Runaway costs | Too many iterations | Cap iterations, split tasks smaller |

### Sources

- [ghuntley.com/ralph](https://ghuntley.com/ralph/)
- [snarktank/ralph on GitHub](https://github.com/snarktank/ralph)
- [Dev Interrupted interview](https://devinterrupted.substack.com/p/inventing-the-ralph-wiggum-loop-creator)
- [Adam Tuttle's workflow](https://adamtuttle.codes/blog/2026/my-ralph-workflow-for-claude-code/)

---

## 2. BMAD (Breakthrough Method for Agile AI-Driven Development)

**Creator:** Steve Kaplan | **Repo:** [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

Transforms Claude Code into a **virtual development team** with specialized agent personas.

### Four phases

Analysis -> Planning -> Solutioning -> Implementation

### Agent personas

PM (John), Architect (Winston), Developer (Amelia), UX Designer (Sally), Scrum Master (Bob), QA (Murat), Business Analyst (Mary), and more (12+ total).

### Installation

```bash
npx bmad-method install
```

Creates `_bmad/` folder with agent definitions, `.claude/commands/` with slash commands (`/bmad-help`, `/pm`, `/sm`, `/dev`, `/architect`).

### Core innovation

**Document sharding** — breaking specs into atomic, AI-digestible pieces instead of one massive document. Uses `MANDATORY-CHECKPOINT` instructions for reliable agent switching.

### Tradeoffs

- Steep learning curve (12+ agents, many concepts)
- Prescriptive (requires full PRD/architecture before code)
- High token consumption (~31K tokens/workflow run, $847/month in one example)
- Best for enterprise-scale projects with teams

### Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [Official Docs](https://docs.bmad-method.org/)
- [BMAD-AT-CLAUDE (Claude-specific port)](https://github.com/24601/BMAD-AT-CLAUDE)

---

## 3. GSD (Get Shit Done)

**Creator:** Lex Christopherson (TACHES) | **Repo:** [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | **48K+ GitHub stars**

### Core innovation

Solves **context rot** — quality degrades as context fills. GSD spawns fresh sub-agents per task so Task 50 has the same quality as Task 1.

### Installation

```bash
npx get-shit-done-cc@latest
```

### Four phases

1. `/gsd:discuss-phase` -> `PROJECT.md`
2. `/gsd:plan-phase` -> `REQUIREMENTS.md` + `ROADMAP.md`
3. `/gsd:execute-phase` -> fresh sub-agent per task (fit in ~50% of context window)
4. `/gsd:verify-work` -> verify against requirements, commit

### State files

`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` (persistent memory across sessions)

### Context rot thresholds

- 0-30% context: peak quality
- 50%+: starts rushing
- 70%+: hallucinations appear

### Tradeoffs

- 4:1 token overhead ratio (4 tokens orchestration per 1 token of code)
- Overkill for small tasks
- Best for solo devs building non-trivial projects

### Results

- 250K lines of code in one month (developer with zero app dev experience)
- 100K lines in two weeks with traceable commits

### GSD v2

[gsd-build/gsd-2](https://github.com/gsd-build/gsd-2) — now a TypeScript application that actively controls the agent session, not just a prompt framework.

### Sources

- [GSD GitHub](https://github.com/gsd-build/get-shit-done)
- [GSD-2 GitHub](https://github.com/gsd-build/gsd-2)
- [The New Stack on context rot](https://thenewstack.io/beating-the-rot-and-getting-stuff-done/)

---

## 4. Head-to-Head Comparison

| Dimension | Ralph Loop | BMAD | GSD |
|---|---|---|---|
| Philosophy | Brute-force iteration | Virtual agile team | Context engineering |
| Core innovation | Fresh context per loop | Document sharding + personas | Context rot prevention |
| Phases | Loop until done | Analysis/Plan/Solution/Implement | Discuss/Plan/Execute/Verify |
| Best for | Overnight autonomous builds | Enterprise/team projects | Solo devs, medium-large projects |
| Learning curve | Low (it's a bash loop) | Steep (12+ agents) | Moderate (4-phase cycle) |
| Token cost | High (cap with iterations) | ~31K/workflow | 4:1 overhead |
| Requires automated tests | Yes (critical) | No (but recommended) | No (has own verification) |

---

## 5. MCP Servers (Model Context Protocol)

### Transport types

```bash
# HTTP (recommended)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# With auth
claude mcp add --transport http stripe https://mcp.stripe.com \
  --header "Authorization: Bearer $TOKEN"

# Stdio (local process)
claude mcp add --transport stdio airtable -- npx -y airtable-mcp-server
```

### Scopes

| Scope | Flag | Stored In | Shared? |
|-------|------|-----------|---------|
| Local (default) | `--scope local` | `~/.claude.json` | No |
| Project | `--scope project` | `.mcp.json` | Yes (committed) |
| User | `--scope user` | `~/.claude.json` | No |

### Project `.mcp.json` with env var expansion

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": { "Authorization": "Bearer ${API_KEY}" }
    }
  }
}
```

### Top MCP servers

- **GitHub MCP** — PR management, issues, code search
- **Playwright MCP** — browser automation, E2E testing
- **PostgreSQL MCP** — database exploration
- **Context7** — live, version-specific library documentation
- **Figma MCP** — design tokens, layout data
- **Supabase MCP** — database, auth, storage
- **Stripe/PayPal** — payment integration

### Tips

- MCP Tool Search enables lazy loading, reducing context usage by ~95%
- `MCP_TIMEOUT=10000` configures startup timeout
- `MAX_MCP_OUTPUT_TOKENS=50000` increases output limit
- `enableAllProjectMcpServers: true` auto-approves `.mcp.json` servers

---

## 6. Skills (Custom Slash Commands)

### Skill structure

```
my-skill/
  SKILL.md           # Main instructions (required)
  template.md        # Template for Claude to fill in
  examples/
  scripts/
```

### Locations

| Scope | Path |
|-------|------|
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` |
| Project | `.claude/skills/<skill-name>/SKILL.md` |

### SKILL.md frontmatter

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true   # only user can invoke
allowed-tools: Bash Read Edit Grep Glob
context: fork                     # runs in isolated subagent
agent: Explore                    # subagent type
effort: high
paths:                            # conditional activation
  - "src/api/**/*.ts"
---
```

### Dynamic context injection

Use `` !`command` `` to run shell commands before skill content is sent:

```markdown
## PR context
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`
```

### String substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments |
| `$0`, `$1` | Positional arguments |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |

---

## 7. CLAUDE.md Rules & Memory

### File locations (loaded in order)

| Scope | Location | Shared? |
|-------|----------|---------|
| Managed policy | `/Library/Application Support/ClaudeCode/CLAUDE.md` | All org users |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via git |
| User | `~/.claude/CLAUDE.md` | Just you |
| Local | `./CLAUDE.local.md` (gitignored) | Just you |

### Best practices

- Target under 200 lines per file
- Use imperative instructions ("NEVER do X", "ALWAYS do Y")
- Use `@path/to/file` imports for additional content
- Move detailed rules to `.claude/rules/` with `paths:` frontmatter

### Path-specific rules

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Rules
- All endpoints must include input validation
```

### Auto memory

Stored in `~/.claude/projects/<project>/memory/MEMORY.md`. First 200 lines / 25KB loaded each session. Toggle with `/memory`.

---

## 8. Hooks

### Hook events

| Event | When |
|-------|------|
| `SessionStart` | Session begins/resumes |
| `UserPromptSubmit` | Before processing prompt |
| `PreToolUse` | Before tool call (can block) |
| `PostToolUse` | After tool succeeds |
| `Stop` | When Claude finishes responding |
| `Notification` | When Claude needs attention |
| `SubagentStart/Stop` | Subagent lifecycle |
| `PreCompact/PostCompact` | Context compaction |

### Hook types

- `command` — shell command
- `http` — HTTP request
- `prompt` — LLM judgment call
- `agent` — multi-turn verification

### Exit codes

- 0 = allow
- 2 = block (stderr becomes Claude's feedback)

### Example: auto-format after edits

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
      }]
    }]
  }
}
```

### Example: desktop notification

```json
{
  "hooks": {
    "Notification": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "osascript -e 'display notification \"Claude Code\" with title \"Claude Code\"'"
      }]
    }]
  }
}
```

### Example: block protected files

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/protect-files.sh"
      }]
    }]
  }
}
```

### Example: Stop hook for Ralph-style loop

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if all tasks are complete. If not, respond with what remains."
      }]
    }]
  }
}
```

---

## 9. CLI Reference

### Essential commands

```bash
claude                              # Interactive session
claude "refactor the auth module"   # Start with initial prompt
claude -p "explain this function"   # Non-interactive (print mode)
claude -c                           # Continue most recent session
claude -r "auth-refactor"           # Resume named session
claude -n "feature-work"            # Name a session
claude -w feature-auth              # Isolated git worktree
claude -w feature-auth --tmux       # Worktree with tmux panes
```

### Key flags

| Flag | Purpose |
|------|---------|
| `--model sonnet` / `--model opus` | Set model |
| `--effort high` / `max` | Thinking depth |
| `--permission-mode plan` | Read-only planning |
| `--enable-auto-mode` | Unlock auto in Shift+Tab cycle |
| `--max-budget-usd 5.00` | Spending limit (print mode) |
| `--max-turns 10` | Turn limit (print mode) |
| `--output-format json` | Parseable output |
| `--bare` | Skip hooks/skills/MCP |
| `--add-dir ../apps ../lib` | Extra directories |
| `--allowedTools "Bash(git *)" "Read"` | Pre-allow tools |

### Interactive shortcuts

- **Shift+Tab**: Cycle permission modes (default > acceptEdits > plan > auto)
- **Esc+Esc**: Rewind menu (undo code + conversation)
- `/cost`: Token consumption
- `/compact`: Reduce context
- `/model`: Switch models mid-session
- `/effort`: Change thinking depth

---

## 10. Multi-Agent & Cowork Patterns

### Agent Teams (experimental)

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

One **team lead** spawns **teammates** (full Claude Code instances). They share a task list and communicate via mailbox. Unlike subagents, teammates message each other directly.

**Controls:** `Shift+Down` (cycle), `Ctrl+T` (task list), `--teammate-mode tmux`

**Sweet spot:** 3-5 teammates, 5-6 tasks each. Token cost ~3-4x linear.

### Git worktrees

```bash
claude -w feature-a    # Terminal 1
claude -w feature-b    # Terminal 2
claude -w bugfix-123   # Terminal 3
```

Auto-cleanup if no changes. Use `.worktreeinclude` to copy gitignored files.

### Custom subagent definitions

`.claude/agents/security-reviewer.md`:
```markdown
---
model: sonnet
tools: [Read, Grep, Glob, "Bash(git:*)"]
isolation: worktree
---
You are a security code reviewer...
```

### Extended thinking / effort levels

```bash
claude --effort high    # Recommended approach
claude --effort max     # Maximum reasoning
/effort high            # Change mid-session
```

The old `ultrathink` keyword now just maps to `--effort high`.

---

## 11. Source Code Insights

Key findings from Claude Code's shipped JS bundle:

1. **CLAUDE.md is injected into the system prompt** — every line consumes context budget. Conciseness matters.

2. **Write tool requires prior Read** — anti-hallucination measure. Claude must read a file before overwriting.

3. **Edit tool uses exact string matching** — `old_string` must be unique or use `replace_all`. Line numbers from Read must NOT be included.

4. **Git Safety Protocol is hardcoded** — never force-push, never amend by default, always new commits. CLAUDE.md can complement but shouldn't fight these defaults.

5. **Parallel tool calls are encouraged** — architecture supports multiple simultaneous invocations.

6. **Deferred tool loading** — MCP and skill tools discovered on demand via `ToolSearch`, keeping baseline context lean.

7. **Grep uses ripgrep** — different syntax from GNU grep. Literal braces need escaping. Supports multiline mode.

8. **Default result caps** — Grep: 250 entries, Read: 2000 lines.

9. **Sandbox bypass exists** — `dangerouslyDisableSandbox` parameter on Bash tool, restricted by default.

10. **Glob returns by modification time** — most recently modified files first.

### Optimization tips from source analysis

- Use imperative, negative-space instructions in CLAUDE.md ("NEVER do X")
- Use absolute paths in build commands
- Keep files under 200 lines for faster reads and fewer edit conflicts
- Describe expected visual behavior in words (Claude can't see your screen)
- Fresh sessions per major task to avoid context rot

---

## 12. Settings Reference

### Recommended starter config (`~/.claude/settings.json`)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Read", "Edit", "Write", "Glob", "Grep", "Bash(git *)"],
    "deny": ["Bash(rm -rf *)", "Bash(git push --force *)"]
  },
  "effortLevel": "high",
  "autoMemoryEnabled": true
}
```

### Scope precedence (highest to lowest)

1. Managed (cannot be overridden)
2. CLI flags (session-only)
3. Local (`.claude/settings.local.json`)
4. Project (`.claude/settings.json`)
5. User (`~/.claude/settings.json`)

### Key settings

| Setting | Purpose |
|---------|---------|
| `$schema` | Editor autocomplete |
| `model` | Default model |
| `effortLevel` | Persist effort |
| `language` | Response language |
| `permissions` | Allow/deny/ask rules |
| `hooks` | Lifecycle automation |
| `autoMemoryEnabled` | Toggle auto memory |
| `enableAllProjectMcpServers` | Auto-approve .mcp.json |
| `sandbox.enabled` | Bash sandboxing |
| `worktree.symlinkDirectories` | Reduce disk usage |
| `claudeMdExcludes` | Skip irrelevant CLAUDE.md |

---

## 13. Community Workflow Patterns

### Boris Cherny's workflow (Claude Code creator)

Runs 10-15 sessions simultaneously — 5 terminal tabs, 5-10 web, some from phone. Each gets its own git worktree.

### Planning-first approach

1. Start in Plan Mode (`claude --permission-mode plan`)
2. One Claude drafts the plan
3. Second Claude reviews "as a staff engineer"
4. Execute only after plan approval
5. `Ctrl+G` to edit plan in your editor

### Three-tier approach

- **Tier 1**: Interactive single-session work
- **Tier 2**: Parallel worktree sprints (3-5 simultaneous)
- **Tier 3**: Agent teams draining a backlog overnight

### CLAUDE.md as living documentation

"Anytime we see Claude do something incorrectly, we add it to CLAUDE.md so it doesn't repeat next time." Updated multiple times a week, committed to git.

### Third-party orchestration tools

- **oh-my-claudecode** — multi-agent orchestration framework
- **Claude Code Agentrooms** (claudecode.run) — route tasks to specialized agents
- **parallel-code** — run Claude Code, Codex, and Gemini side by side
- **Nimbalyst** — desktop app for managing multiple AI sessions
