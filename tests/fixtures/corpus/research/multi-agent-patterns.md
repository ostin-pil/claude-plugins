# Claude Code Multi-Agent & Cowork Patterns

Comprehensive research into parallel execution, agent orchestration, and multi-session workflows in Claude Code (current as of April 2026).

---

## Table of Contents

1. [Agent Teams (Experimental)](#1-agent-teams-experimental)
2. [Git Worktrees for Parallelism](#2-git-worktrees-for-parallelism)
3. [Custom Subagent Definitions](#3-custom-subagent-definitions)
4. [Built-in Subagent Types](#4-built-in-subagent-types)
5. [Isolation Modes](#5-isolation-modes)
6. [Extended Thinking & Effort Levels](#6-extended-thinking--effort-levels)
7. [Third-Party Orchestration](#7-third-party-orchestration)
8. [Boris Cherny's Workflow](#8-boris-chernys-workflow)
9. [The Three-Tier Approach](#9-the-three-tier-approach)

---

## 1. Agent Teams (Experimental)

**Status:** Experimental, disabled by default. Shipped with Opus 4.6 in February 2026. Requires Claude Code v2.1.32+.

### Enabling

Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` to `1` either in your shell or in `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Architecture

An agent team consists of four components:

| Component     | Role                                                              |
|:------------- |:----------------------------------------------------------------- |
| **Team lead** | The main session that creates the team, spawns teammates, coordinates |
| **Teammates** | Separate Claude Code instances working on assigned tasks          |
| **Task list** | Shared list of work items that teammates claim and complete       |
| **Mailbox**   | Messaging system for direct inter-agent communication             |

### Tools Unlocked

Enabling the flag unlocks: `TeamCreate`, `TaskCreate`, `TaskUpdate`, `TaskList`, `SendMessage`.

### Mailbox Communication

- Teammates can **message** a specific teammate by name or **broadcast** to all.
- Messages are delivered automatically; the lead doesn't need to poll.
- When a teammate finishes, it automatically notifies the lead.
- The shared task list coordinates work; tasks have states: pending, in progress, completed.
- Tasks can have dependencies that auto-unblock when upstream tasks complete.
- Task claiming uses **file locking** to prevent race conditions.

### Display Modes

Configured via `--teammate-mode` flag or `teammateMode` in `~/.claude.json`:

- **In-process** (default): All teammates run in your main terminal. Navigate with `Shift+Down` to cycle through them. Works in any terminal.
- **Split panes** (`tmux`): Each teammate gets its own pane. Requires tmux or iTerm2 with the `it2` CLI. Use `tmux -CC` in iTerm2 for best results on macOS.
- **Auto**: Uses split panes if already in tmux, in-process otherwise.

### Sweet Spot: 3-5 Teammates

The official docs recommend starting with **3-5 teammates** for most workflows. This balances parallel work with manageable coordination. Having **5-6 tasks per teammate** keeps everyone productive without excessive context switching. For example, 15 independent tasks suggests 3 teammates as a good starting point. Three focused teammates often outperform five scattered ones.

### Subagents vs Agent Teams

| Aspect            | Subagents                              | Agent Teams                                 |
|:------------------|:---------------------------------------|:--------------------------------------------|
| Context           | Own window; results return to caller   | Own window; fully independent               |
| Communication     | Report back to main agent only         | Teammates message each other directly       |
| Coordination      | Main agent manages all work            | Shared task list with self-coordination     |
| Best for          | Focused tasks, result matters          | Complex work requiring discussion           |
| Token cost        | Lower                                 | Higher (each teammate is a full instance)   |

### Best Practices

- Give teammates enough context in the spawn prompt (they don't inherit conversation history).
- Use plan approval for risky tasks: the teammate works read-only until the lead approves.
- Avoid file conflicts by ensuring each teammate owns different files.
- Use hooks: `TeammateIdle`, `TaskCreated`, `TaskCompleted` for quality gates.
- Always clean up through the lead, not through teammates.

### Known Limitations

- No session resumption with in-process teammates.
- Task status can lag (teammates may fail to mark tasks complete).
- One team per session; no nested teams.
- Lead is fixed; cannot be transferred.
- Split panes not supported in VS Code terminal, Windows Terminal, or Ghostty.

---

## 2. Git Worktrees for Parallelism

### The `--worktree` / `-w` Flag

Claude Code has native worktree support. Instead of manually running `git worktree add`, you do it in one step:

```bash
# Named worktree
claude --worktree feature-auth

# Auto-generated name (e.g., "bright-running-fox")
claude --worktree

# Another parallel session
claude --worktree bugfix-123
```

Worktrees are created at `<repo>/.claude/worktrees/<name>` and branch from `origin/HEAD`. The branch is named `worktree-<name>`.

### .worktreeinclude

Git worktrees are fresh checkouts that don't include untracked files like `.env`. Create a `.worktreeinclude` file at your project root using `.gitignore` syntax:

```
.env
.env.local
config/secrets.json
```

Only files matching a pattern **and** also gitignored get copied. Tracked files are never duplicated.

### Auto-Cleanup

When you exit a worktree session:

- **No changes:** Worktree and branch removed automatically.
- **Changes or commits exist:** Claude prompts you to keep or remove.
- **Subagent worktrees** orphaned by crashes are auto-removed at startup once older than `cleanupPeriodDays` (if no uncommitted changes, no untracked files, no unpushed commits).

### Running 3-5 Worktrees Simultaneously

Open multiple terminal tabs/windows and launch separate worktree sessions:

```bash
# Terminal 1
claude -w feature-auth

# Terminal 2
claude -w feature-payments

# Terminal 3
claude -w bugfix-login
```

Each session gets its own directory, its own branch, its own files on disk. They share the same `.git` history and remote connections. Add `.claude/worktrees/` to your `.gitignore`.

### Base Branch Control

`origin/HEAD` determines the base branch. To re-sync: `git remote set-head origin -a`. For full control per invocation, configure a `WorktreeCreate` hook.

---

## 3. Custom Subagent Definitions

### File Location & Scope

Subagents are Markdown files with YAML frontmatter, stored at different scopes:

| Location                     | Scope             | Priority    |
|:-----------------------------|:------------------|:------------|
| Managed settings             | Organization-wide | 1 (highest) |
| `--agents` CLI flag          | Current session   | 2           |
| `.claude/agents/`            | Current project   | 3           |
| `~/.claude/agents/`          | All your projects | 4           |
| Plugin's `agents/` directory | Where enabled     | 5 (lowest)  |

### Frontmatter Format

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
isolation: worktree
effort: high
permissionMode: default
maxTurns: 20
memory: project
background: false
color: blue
skills:
  - api-conventions
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github
hooks:
  PreToolUse:
    - matcher: ""
      hooks:
        - type: command
          command: "echo checking"
---

You are a code reviewer. Analyze code and provide specific,
actionable feedback on quality, security, and best practices.
```

### All Supported Frontmatter Fields

| Field             | Required | Description                                                  |
|:------------------|:---------|:-------------------------------------------------------------|
| `name`            | Yes      | Unique identifier (lowercase, hyphens)                       |
| `description`     | Yes      | When Claude should delegate to this subagent                 |
| `tools`           | No       | Tools allowlist; inherits all if omitted                     |
| `disallowedTools` | No       | Tools denylist, removed from inherited set                   |
| `model`           | No       | `sonnet`, `opus`, `haiku`, full model ID, or `inherit`       |
| `permissionMode`  | No       | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns`        | No       | Maximum agentic turns before stopping                        |
| `skills`          | No       | Skills to inject at startup (full content, not just names)   |
| `mcpServers`      | No       | MCP servers (inline defs or references to configured ones)   |
| `hooks`           | No       | Lifecycle hooks scoped to this subagent                      |
| `memory`          | No       | `user`, `project`, or `local` for cross-session learning     |
| `background`      | No       | `true` to always run as background task                      |
| `effort`          | No       | `low`, `medium`, `high`, `max` (Opus 4.6 only)              |
| `isolation`       | No       | `worktree` for isolated git worktree                         |
| `color`           | No       | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt`   | No       | Auto-submitted first user turn when running as main agent    |

### CLI-Defined Subagents

For quick testing without files on disk:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer.",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### Restricting Subagent Spawning

Use `Agent(worker, researcher)` in the `tools` field to whitelist which subagents a coordinator can spawn. Omit `Agent` entirely to prevent spawning any subagents.

---

## 4. Built-in Subagent Types

Claude Code ships with several built-in subagents that are automatically invoked when appropriate.

### Explore

- **Model:** Haiku (fast, low-latency, cost-effective)
- **Tools:** Read-only (no Write/Edit)
- **Purpose:** File discovery, code search, codebase exploration
- **Behavior:** Claude specifies a thoroughness level per invocation: **quick** (targeted lookups), **medium** (balanced), or **very thorough** (comprehensive analysis).
- **Use case:** When Claude needs to understand a codebase without making changes. Keeps exploration out of your main context.

### Plan

- **Model:** Inherits from main conversation
- **Tools:** Read-only (no Write/Edit)
- **Purpose:** Codebase research for planning
- **Behavior:** Active during Plan Mode. Gathers context before Claude presents a strategy. Prevents infinite nesting since subagents cannot spawn other subagents.

### General-Purpose

- **Model:** Inherits from main conversation
- **Tools:** All tools
- **Purpose:** Complex research, multi-step operations, code modifications
- **Use case:** When the task requires both exploration and modification, complex reasoning, or multiple dependent steps.

### Other Built-in Agents

| Agent             | Model  | When used                                         |
|:------------------|:-------|:--------------------------------------------------|
| statusline-setup  | Sonnet | When you run `/statusline`                        |
| Claude Code Guide | Haiku  | When you ask about Claude Code features           |

### Key Design Principle

Subagents **cannot spawn other subagents**. This prevents infinite nesting. The main agent delegates down one level only. For multi-level coordination, use Agent Teams instead.

---

## 5. Isolation Modes

### What Worktree Isolation Provides

When `isolation: worktree` is set in a subagent's frontmatter (or you use `--worktree`), each agent gets:

**Isolated (per-agent):**
- Working directory (separate files on disk)
- Git branch (separate commit history)
- File modifications (no clobbering)

**Shared (across all agents on the machine):**
- Repository history and remote connections (same `.git`)
- Environment variables
- Local databases and running services
- Network access (local dev server, APIs)
- Process space (no container isolation)

### Subagent Worktree Isolation

Configure in the agent's frontmatter:

```yaml
---
name: parallel-worker
description: Works on tasks in isolation
isolation: worktree
---
```

Or ask Claude: "use worktrees for your agents."

Each subagent gets its own worktree that is **automatically cleaned up** when it finishes without changes. If it has changes, the worktree is preserved.

### Agent Teams Isolation

Agent team teammates do **not** automatically get worktree isolation. They share the same working directory by default. To avoid file conflicts, either:
- Ensure each teammate works on different files.
- Use subagent definitions with `isolation: worktree` for teammates.

### Important Caveat

Worktree isolation is **filesystem only**. There is no process isolation, no container boundary. A subagent in a worktree can still hit your local dev server, write to a shared database, or call external APIs. Plan accordingly.

---

## 6. Extended Thinking & Effort Levels

### Effort Levels

Control thinking depth via `/effort` command, `--effort` flag, or the `CLAUDE_CODE_EFFORT_LEVEL` environment variable:

| Level    | Behavior                                           |
|:---------|:---------------------------------------------------|
| `low`    | Simple tasks, fast responses, minimal reasoning    |
| `medium` | Moderate tasks, balanced speed and depth           |
| `high`   | Deep reasoning (default), thorough analysis        |
| `max`    | Maximum depth, **Opus 4.6 only**                   |

### Adaptive Reasoning (Opus 4.6 & Sonnet 4.6)

On these models, thinking uses **adaptive reasoning**: the model dynamically allocates thinking tokens based on effort level rather than using a fixed budget. This is the recommended way to tune the speed/depth tradeoff.

### Thinking Trigger Keywords

These keywords in your prompt influence thinking budget allocation:

| Keyword                        | Approximate Budget |
|:-------------------------------|:-------------------|
| `think`                        | ~4,000 tokens      |
| `think hard` / `megathink`     | ~10,000 tokens     |
| `think harder` / `ultrathink`  | ~31,999 tokens     |

**Important:** These keywords only work in Claude Code (the CLI tool), not in claude.ai's web interface.

### The `ultrathink` Keyword

Adding "ultrathink" anywhere in your prompt sets effort to `high` for that turn on Opus 4.6 and Sonnet 4.6. It allocates the maximum ~31,999 token thinking budget. Best used for:
- Complex architecture decisions
- Debugging difficult issues
- Deep code analysis
- Multi-step implementation planning

### Configuration Options

| Scope              | Method                                            |
|:-------------------|:--------------------------------------------------|
| Per-turn           | Include "ultrathink" in prompt                    |
| Session toggle     | `Option+T` (macOS) / `Alt+T`                     |
| Per-session        | `/effort` command or `/model` settings            |
| Environment        | `CLAUDE_CODE_EFFORT_LEVEL` env var                |
| Global default     | `/config` toggle                                  |
| Token cap          | `MAX_THINKING_TOKENS` env var                     |
| Subagent override  | `effort` field in frontmatter                     |

### Viewing Thinking

Press `Ctrl+O` to toggle verbose mode and see internal reasoning displayed as gray italic text.

---

## 7. Third-Party Orchestration

### oh-my-claudecode (OMC)

**Repo:** [github.com/yeachan-heo/oh-my-claudecode](https://github.com/yeachan-heo/oh-my-claudecode)

Multi-agent orchestration layer on top of Claude Code. Claims 3-5x speedup and 30-50% token savings through 32 specialized agents.

**5 Execution Modes:**

| Mode       | Description                                                    |
|:-----------|:---------------------------------------------------------------|
| Team       | Staged pipeline: Plan -> PRD -> Exec -> Verify -> Fix         |
| Ultrawork  | Burst-parallel execution for massive refactors                 |
| Ultrapilot | Multi-component builds with parallel dispatch                  |
| Ralph      | Self-healing loops: auto-verify and fix until 100% validated   |
| Autopilot  | Detects intent, auto-orchestrates from 19 agents               |

**Key features:** Automatic task decomposition, parallel agent execution, native plan mode integration, 32 specialized agents covering architecture through unit testing.

### Agentrooms

**Repo:** [github.com/baryhuang/claude-code-by-agents](https://github.com/baryhuang/claude-code-by-agents)
**Site:** [claudecode.run](https://claudecode.run/)

Desktop app and API for multi-agent Claude Code orchestration. Coordinates local and remote agents through `@mentions`.

**Key features:**
- Task routing to specialized agents via `@agent-name` mentions
- Automatic task decomposition
- Mix of local agents and remote machines (Mac Minis, cloud instances)
- Desktop and web interfaces
- Open source (MIT)

### parallel-code

**Repo:** [github.com/johannesjo/parallel-code](https://github.com/johannesjo/parallel-code)

Desktop app that gives every AI coding agent its own git branch and worktree automatically. Supports Claude Code, Codex CLI, and Gemini CLI side by side from one interface.

**Key features:**
- Each task gets its own branch and worktree automatically
- Run multiple AI agents in parallel with zero conflicts
- Keyboard-driven UI (mouse optional)
- Free, open source (MIT)
- Requires Node.js v18+

### Nimbalyst

**Site:** [nimbalyst.com](https://nimbalyst.com)

Claude Code GUI and session manager with visual editors, multi-session orchestration, and task tracking.

**Key features:**
- 7+ visual editors (markdown, code, CSV, UI mockups, Excalidraw, ERDs, Mermaid)
- Kanban board for multi-session orchestration
- Inline diff review
- Git worktree isolation per agent
- Mobile accessibility
- Free for individual users
- Founded by the Evergage team (acquired by Salesforce in 2020)

---

## 8. Boris Cherny's Workflow

Boris Cherny, creator of Claude Code, shared his workflow in early 2026. He calls parallel execution **"the single biggest productivity unlock"** and says the entire Claude Code engineering team agrees.

### Session Distribution

He maintains **10-15 concurrent Claude Code sessions**:
- ~5 in terminal (tabbed, numbered, with OS notifications)
- 5-10 in the browser
- Additional mobile sessions started in the morning and checked later

### Key Principles

1. **Plan Mode first:** Goes back and forth with Claude in Plan Mode until satisfied, then switches to auto-accept edits mode. Claude "can usually one-shot it" from there.

2. **Worktree isolation:** Each task gets its own worktree with its own branch via `claude --worktree`.

3. **Sweep-back interval:** Checks sessions every 15-20 minutes. Uses iTerm2 system notifications that ping when a session finishes or needs input.

4. **Model choice:** Exclusively uses Opus 4.5 with thinking. Even though it's bigger and slower than Sonnet, "since you have to steer it less and it's better at tool use, it is almost always faster than using a smaller model."

5. **CLAUDE.md discipline:** Maintains a single CLAUDE.md file in the repo. Anytime Claude does something incorrectly, the team adds it to CLAUDE.md so Claude knows not to do it next time. Accumulates project-specific corrections over time.

6. **Vanilla setup:** Surprisingly minimal customization. "Claude Code works great out of the box, so I personally don't customize it much." Each team member uses it differently.

### Notification Setup

Uses `Notification` hooks in `settings.json` to get desktop notifications:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

---

## 9. The Three-Tier Approach

A mental model for scaling Claude Code usage, from interactive pair-programming to fully autonomous overnight runs.

### Tier 1: Interactive (Single Session)

**When:** Real-time collaboration, exploration, learning the codebase, decisions requiring human judgment.

**How:** One Claude Code session. Use Plan Mode for safe exploration. Toggle between normal and auto-accept as confidence grows. Use `/effort` to control thinking depth per task.

**Best for:** Debugging a tricky issue, designing an API, reviewing code, exploring an unfamiliar codebase.

### Tier 2: Parallel Worktrees (Manual Multi-Session)

**When:** Multiple independent tasks that can proceed without inter-agent coordination.

**How:** Open 3-5 terminal windows, each with `claude --worktree <name>`. Each session works on a separate branch with its own files. Human orchestrates by switching between terminals.

**Best for:** Feature sprints (auth + payments + onboarding in parallel), bug-fix batches, parallel refactoring of independent modules.

**Setup pattern:**
```bash
# Terminal 1: interactive lead session
claude

# Terminal 2-4: worktree sessions
claude -w feature-auth
claude -w feature-payments
claude -w refactor-tests
```

Use Notification hooks to know when sessions need attention. Sweep back every 15-20 minutes.

### Tier 3: Agent Teams (Overnight / Autonomous)

**When:** Complex, multi-faceted work that benefits from inter-agent communication and can run with minimal supervision.

**How:** Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. Describe the team structure and task in natural language. The lead spawns teammates, assigns tasks, synthesizes results.

**Best for:** Large code reviews with multiple perspectives, investigating bugs with competing hypotheses, building new modules with clear boundaries, cross-layer changes (frontend + backend + tests).

**Setup pattern:**
```
Create an agent team with 4 teammates:
- One for the API layer
- One for the frontend components  
- One for integration tests
- One for documentation updates
Use worktree isolation for each. Require plan approval before implementation.
```

### Choosing the Right Tier

| Factor                | Tier 1           | Tier 2            | Tier 3              |
|:----------------------|:-----------------|:------------------|:--------------------|
| Human oversight       | Continuous       | Periodic sweeps   | Minimal             |
| Coordination          | N/A              | Human-managed     | Automated (lead)    |
| Token cost            | Baseline         | Linear scaling    | Highest             |
| Inter-agent comms     | N/A              | None              | Mailbox + task list |
| File conflict risk    | None             | Low (worktrees)   | Low (worktrees)     |
| Setup complexity      | Zero             | Low               | Medium              |
| Best session count    | 1                | 3-5               | 3-5 teammates       |

### Combining Tiers

Most productive developers use all three tiers daily:
- **Morning:** Start Tier 3 agent team on a large refactor while having coffee.
- **Focus time:** Tier 1 interactive session for the tricky design problem.
- **Sprint time:** Tier 2 parallel worktrees for knocking out 3-4 independent tasks.
- **End of day:** Launch another Tier 3 team for overnight code review or test generation.

---

## Sources

- [Claude Code Docs: Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Docs: Custom Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Docs: Common Workflows (Worktrees)](https://code.claude.com/docs/en/common-workflows)
- [VentureBeat: Boris Cherny's Workflow](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are)
- [Boris Cherny on Threads](https://www.threads.com/@boris_cherny/post/DTBVlMIkpcm/)
- [oh-my-claudecode on GitHub](https://github.com/yeachan-heo/oh-my-claudecode)
- [Agentrooms on GitHub](https://github.com/baryhuang/claude-code-by-agents)
- [parallel-code on GitHub](https://github.com/johannesjo/parallel-code)
- [Nimbalyst](https://nimbalyst.com)
- [Claude Code Thinking Triggers](https://kentgigger.com/posts/claude-code-thinking-triggers)
- [Anthropic: Visible Extended Thinking](https://www.anthropic.com/news/visible-extended-thinking)
- [Claude Code Worktree Guide (claudefa.st)](https://claudefa.st/blog/guide/development/worktree-guide)
- [Claude Code Agent Teams Guide (claudefa.st)](https://claudefa.st/blog/guide/agents/agent-teams)
- [Addy Osmani: The Code Agent Orchestra](https://addyosmani.com/blog/code-agent-orchestra/)
