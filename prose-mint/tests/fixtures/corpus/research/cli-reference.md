# Claude Code CLI Reference

Comprehensive reference for the Claude Code command-line interface, covering all flags,
scripting patterns, worktree mode, session management, interactive shortcuts, permission
modes, piping, environment variables, and configuration commands.

Based on official documentation at [code.claude.com/docs](https://code.claude.com/docs/en/cli-reference)
as of April 2026.

---

## 1. CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `claude` | Start interactive session | `claude` |
| `claude "query"` | Start session with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Print mode -- query, respond, exit | `claude -p "explain this function"` |
| `cat file \| claude -p "query"` | Process piped content | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | Continue most recent conversation | `claude -c` |
| `claude -c -p "query"` | Continue via print mode | `claude -c -p "check for type errors"` |
| `claude -r "session" "query"` | Resume session by ID or name | `claude -r "auth-refactor" "finish PR"` |
| `claude update` | Update to latest version | `claude update` |
| `claude auth login` | Sign in (supports `--email`, `--sso`, `--console`) | `claude auth login --console` |
| `claude auth logout` | Sign out | `claude auth logout` |
| `claude auth status` | Show auth status as JSON (`--text` for readable) | `claude auth status` |
| `claude agents` | List all configured subagents | `claude agents` |
| `claude auto-mode defaults` | Print built-in auto mode classifier rules as JSON | `claude auto-mode defaults > rules.json` |
| `claude mcp` | Configure MCP servers | See MCP docs |
| `claude plugin` | Manage plugins (alias: `claude plugins`) | `claude plugin install code-review@claude-plugins-official` |
| `claude remote-control` | Start a Remote Control server | `claude remote-control --name "My Project"` |
| `claude setup-token` | Generate long-lived OAuth token for CI | `claude setup-token` |

---

## 2. CLI Flags -- Complete List

### Session & Prompt Control

| Flag | Description | Example |
|------|-------------|---------|
| `--print`, `-p` | Non-interactive mode -- print response and exit | `claude -p "query"` |
| `--continue`, `-c` | Load most recent conversation in current directory | `claude -c` |
| `--resume`, `-r` | Resume session by ID or name, or show picker | `claude -r auth-refactor` |
| `--name`, `-n` | Set display name for the session | `claude -n "my-feature-work"` |
| `--session-id` | Use a specific session UUID | `claude --session-id "550e8400-..."` |
| `--fork-session` | Create new session ID when resuming | `claude --resume abc --fork-session` |
| `--from-pr` | Resume sessions linked to a GitHub PR | `claude --from-pr 123` |
| `--no-session-persistence` | Don't save session to disk (print mode only) | `claude -p --no-session-persistence "query"` |

### Model & Effort

| Flag | Description | Example |
|------|-------------|---------|
| `--model` | Set model (alias like `sonnet`/`opus` or full name) | `claude --model claude-sonnet-4-6` |
| `--effort` | Effort level: `low`, `medium`, `high`, `max` (Opus 4.6 only) | `claude --effort high` |
| `--fallback-model` | Fallback when default model is overloaded (print mode) | `claude -p --fallback-model sonnet "query"` |

### Permission & Safety

| Flag | Description | Example |
|------|-------------|---------|
| `--permission-mode` | Start in a mode: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` | `claude --permission-mode plan` |
| `--enable-auto-mode` | Add `auto` to the Shift+Tab cycle | `claude --enable-auto-mode` |
| `--dangerously-skip-permissions` | Skip all permission prompts (equivalent to `--permission-mode bypassPermissions`) | `claude --dangerously-skip-permissions` |
| `--allow-dangerously-skip-permissions` | Add `bypassPermissions` to cycle without starting in it | `claude --permission-mode plan --allow-dangerously-skip-permissions` |
| `--permission-prompt-tool` | MCP tool to handle permission prompts in non-interactive mode | `claude -p --permission-prompt-tool mcp_auth "query"` |

### Tool Control

| Flag | Description | Example |
|------|-------------|---------|
| `--allowedTools` | Tools that execute without prompting (supports glob patterns) | `--allowedTools "Bash(git log *)" "Read"` |
| `--disallowedTools` | Tools removed from context entirely | `--disallowedTools "Edit"` |
| `--tools` | Restrict available built-in tools (`""` for none, `"default"` for all) | `--tools "Bash,Edit,Read"` |

### System Prompt

| Flag | Description | Example |
|------|-------------|---------|
| `--system-prompt` | Replace entire default system prompt | `--system-prompt "You are a Python expert"` |
| `--system-prompt-file` | Replace with file contents | `--system-prompt-file ./prompts/review.txt` |
| `--append-system-prompt` | Append to the default prompt | `--append-system-prompt "Always use TypeScript"` |
| `--append-system-prompt-file` | Append file contents to default prompt | `--append-system-prompt-file ./style-rules.txt` |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections to first user message (improves cache reuse) | `claude -p --exclude-dynamic-system-prompt-sections "query"` |

`--system-prompt` and `--system-prompt-file` are mutually exclusive. The append flags can combine with either.

### Output & Input Format

| Flag | Description | Example |
|------|-------------|---------|
| `--output-format` | Output format: `text` (default), `json`, `stream-json` | `claude -p "query" --output-format json` |
| `--input-format` | Input format: `text`, `stream-json` | `claude -p --input-format stream-json` |
| `--json-schema` | Validate JSON output against a schema (print mode) | `--json-schema '{"type":"object",...}'` |
| `--include-partial-messages` | Include partial streaming events (requires `stream-json`) | `claude -p --output-format stream-json --include-partial-messages "query"` |
| `--include-hook-events` | Include hook lifecycle events in stream | `claude -p --output-format stream-json --include-hook-events "query"` |
| `--replay-user-messages` | Re-emit user messages from stdin back on stdout | Requires `stream-json` for both input and output |
| `--verbose` | Full turn-by-turn output | `claude --verbose` |

### Budget & Limits

| Flag | Description | Example |
|------|-------------|---------|
| `--max-turns` | Limit agentic turns (print mode only, no default limit) | `claude -p --max-turns 3 "query"` |
| `--max-budget-usd` | Maximum dollar spend before stopping (print mode only) | `claude -p --max-budget-usd 5.00 "query"` |

### Worktree & Directories

| Flag | Description | Example |
|------|-------------|---------|
| `--worktree`, `-w` | Start in isolated git worktree | `claude -w feature-auth` |
| `--tmux` | Create tmux session for worktree (requires `-w`) | `claude -w feature-auth --tmux` |
| `--add-dir` | Add additional working directories | `claude --add-dir ../apps ../lib` |

### Startup & Discovery

| Flag | Description | Example |
|------|-------------|---------|
| `--bare` | Minimal mode -- skip hooks, skills, plugins, MCP, memory, CLAUDE.md | `claude --bare -p "query"` |
| `--init` | Run initialization hooks and start interactive mode | `claude --init` |
| `--init-only` | Run initialization hooks and exit | `claude --init-only` |
| `--maintenance` | Run maintenance hooks and start interactive mode | `claude --maintenance` |
| `--disable-slash-commands` | Disable all skills and commands | `claude --disable-slash-commands` |

### MCP & Plugins

| Flag | Description | Example |
|------|-------------|---------|
| `--mcp-config` | Load MCP servers from JSON files (space-separated) | `claude --mcp-config ./mcp.json` |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config` | `claude --strict-mcp-config --mcp-config ./mcp.json` |
| `--plugin-dir` | Load plugins from a directory (repeat for multiple) | `claude --plugin-dir ./my-plugins` |

### Agents & Teams

| Flag | Description | Example |
|------|-------------|---------|
| `--agent` | Specify agent for current session | `claude --agent my-custom-agent` |
| `--agents` | Define subagents dynamically via JSON | `claude --agents '{"reviewer":{...}}'` |
| `--teammate-mode` | Agent team display: `auto`, `in-process`, `tmux` | `claude --teammate-mode in-process` |

### Remote & Web

| Flag | Description | Example |
|------|-------------|---------|
| `--remote` | Create web session on claude.ai | `claude --remote "Fix the login bug"` |
| `--remote-control`, `--rc` | Start session with Remote Control enabled | `claude --rc "My Project"` |
| `--teleport` | Resume a web session locally | `claude --teleport` |

### Browser & IDE

| Flag | Description | Example |
|------|-------------|---------|
| `--chrome` | Enable Chrome browser integration | `claude --chrome` |
| `--no-chrome` | Disable Chrome browser integration | `claude --no-chrome` |
| `--ide` | Auto-connect to IDE on startup | `claude --ide` |

### Settings & Config

| Flag | Description | Example |
|------|-------------|---------|
| `--settings` | Path to settings JSON file or JSON string | `claude --settings ./settings.json` |
| `--setting-sources` | Comma-separated sources: `user`, `project`, `local` | `claude --setting-sources user,project` |
| `--betas` | Beta headers for API requests (API key users) | `claude --betas interleaved-thinking` |
| `--channels` | MCP channel notifications to listen for (research preview) | `claude --channels plugin:notifier@marketplace` |

### Debug & Info

| Flag | Description | Example |
|------|-------------|---------|
| `--debug` | Enable debug mode with optional category filter | `claude --debug "api,mcp"` |
| `--debug-file` | Write debug logs to specific file | `claude --debug-file /tmp/claude-debug.log` |
| `--version`, `-v` | Output version number | `claude -v` |

---

## 3. Print Mode (-p) and Scripting

Print mode is the foundation for non-interactive use: scripts, CI/CD, and programmatic access.

### Basic Usage

```bash
# Simple query
claude -p "What does the auth module do?"

# Pipe content in
cat build-error.txt | claude -p "explain the root cause" > output.txt

# Git diff review
git diff | claude -p "review this diff for security issues"

# PR review
gh pr diff "$1" | claude -p --append-system-prompt "You are a security engineer." --output-format json
```

### Output Formats

```bash
# Plain text (default)
claude -p "summarize this project" --output-format text

# JSON with metadata (session_id, usage, result)
claude -p "summarize this project" --output-format json

# Stream JSON -- newline-delimited objects in real-time
claude -p "explain recursion" --output-format stream-json
```

### Structured Output with JSON Schema

```bash
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

The structured result appears in the `structured_output` field of the JSON response.

### Extracting Fields with jq

```bash
# Get just the text result
claude -p "Summarize this project" --output-format json | jq -r '.result'

# Stream tokens in real-time
claude -p "Write a poem" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

### Budget and Turn Limits

```bash
# Cap spending at $5
claude -p --max-budget-usd 5.00 "refactor this module"

# Limit to 3 agentic turns
claude -p --max-turns 3 "fix the failing tests"
```

### Bare Mode for CI

Add `--bare` to skip loading hooks, plugins, MCP servers, CLAUDE.md, and auto memory.
This ensures consistent behavior across machines:

```bash
claude --bare -p "Summarize this file" --allowedTools "Read"
```

Bare mode is recommended for scripted/SDK calls and will become the default for `-p` in
a future release. Authentication must come from `ANTHROPIC_API_KEY` or `apiKeyHelper`.

### Auto-Approving Tools in Scripts

```bash
# Allow specific git commands
claude -p "Create a commit for staged changes" \
  --allowedTools "Bash(git diff *)" "Bash(git log *)" "Bash(git commit *)"

# Auto-approve file edits
claude -p "Apply lint fixes" --permission-mode acceptEdits
```

The `--allowedTools` pattern uses prefix matching: `Bash(git diff *)` matches any command
starting with `git diff`. The space before `*` matters -- without it, `git diff*` would
also match `git diff-index`.

### Continuing Conversations in Scripts

```bash
# First request
claude -p "Review this codebase for performance issues"

# Follow-up on the same session
claude -p "Now focus on database queries" --continue

# Capture session ID for explicit resume
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

### CI/CD Integration Example

```json
{
  "scripts": {
    "lint:claude": "claude -p 'you are a linter. look at changes vs main and report typos. report filename:line then description. no other text.'"
  }
}
```

---

## 4. Worktree Mode (-w)

### Creating Worktrees

```bash
# Named worktree
claude --worktree feature-auth
# Creates .claude/worktrees/feature-auth/ with branch worktree-feature-auth

# Auto-generated name
claude --worktree
# Creates something like .claude/worktrees/bright-running-fox/

# With tmux pane
claude -w feature-auth --tmux
```

Worktrees are created at `<repo>/.claude/worktrees/<name>` and branch from `origin/HEAD`.

### Base Branch

The worktree branches from `origin/HEAD`. If the remote default branch changed after clone,
re-sync with:

```bash
git remote set-head origin -a
```

For full control over worktree creation (different base per invocation), configure a
`WorktreeCreate` hook.

### .worktreeinclude

Git worktrees don't include untracked files (like `.env`). Add a `.worktreeinclude` file
to your project root to auto-copy them:

```
.env
.env.local
config/secrets.json
```

Uses `.gitignore` syntax. Only files that match a pattern AND are gitignored get copied.
Tracked files are never duplicated.

**Note:** `.worktreeinclude` works in the Desktop app and CLI with `--worktree`. It applies
to worktrees created with `-w`, subagent worktrees, and parallel sessions in the desktop app.

### Subagent Worktrees

Configure `isolation: worktree` in a subagent's frontmatter, or ask Claude to "use
worktrees for your agents." Each subagent gets its own isolated worktree.

### Cleanup

- **No changes**: worktree and branch removed automatically on exit
- **Changes exist**: Claude prompts to keep or remove
- **Orphaned subagent worktrees**: auto-cleaned at startup after `cleanupPeriodDays`
  (only if no uncommitted changes, untracked files, or unpushed commits)
- **User worktrees** (from `--worktree`): never auto-cleaned

Add `.claude/worktrees/` to `.gitignore` to hide worktree contents.

---

## 5. Session Management

### Starting Sessions

| Method | Description |
|--------|-------------|
| `claude` | New interactive session |
| `claude -n "name"` | New session with a name |
| `claude -c` | Continue most recent session in this directory |
| `claude -r "name-or-id"` | Resume by name or session ID |
| `claude -r` (no arg) | Open interactive session picker |
| `claude --from-pr 123` | Resume sessions linked to a PR |

### Naming Sessions

```bash
# At startup
claude -n auth-refactor

# During a session
/rename auth-refactor

# In the picker: navigate to session, press R to rename
```

### Session Picker Shortcuts

| Shortcut | Action |
|----------|--------|
| Up/Down | Navigate sessions |
| Right/Left | Expand/collapse grouped sessions |
| Enter | Select and resume |
| P | Preview session content |
| R | Rename session |
| / | Search/filter |
| A | Toggle current directory vs all projects |
| B | Filter to current git branch |
| Esc | Exit picker |

### Session Storage

Sessions are stored at `~/.claude/projects/<project-path>/`. Each project directory contains:
- Individual session files as `.jsonl` (complete conversation transcripts)
- `sessions-index.json` with metadata: summaries, message counts, git branches, timestamps

Sessions from the same git repository (including worktrees) appear together in the picker.
Sessions created by `claude -p` don't appear in the picker but can be resumed by session ID.

### Forking Sessions

```bash
# Fork when resuming
claude --resume abc123 --fork-session

# During a session
/branch my-experiment
```

Forked sessions are grouped under their root session in the picker.

---

## 6. Interactive Shortcuts

### General Controls

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Cancel current input or generation |
| Ctrl+D | Exit session |
| Ctrl+G or Ctrl+X Ctrl+E | Open prompt in external text editor |
| Ctrl+L | Clear prompt input (keeps history) |
| Ctrl+O | Toggle transcript viewer (shows tool details) |
| Ctrl+R | Reverse search command history |
| Ctrl+V / Cmd+V | Paste image from clipboard |
| Ctrl+B | Background running tasks (tmux users: press twice) |
| Ctrl+T | Toggle task list |
| Ctrl+X Ctrl+K | Kill all background agents (press twice within 3s) |
| Up/Down | Navigate command history |
| Left/Right | Cycle dialog tabs |
| Esc + Esc | Rewind or summarize to a previous point |
| Shift+Tab | Cycle permission modes: default -> acceptEdits -> plan -> [auto] -> [bypass] |
| Alt+P / Option+P | Switch model picker |
| Alt+T / Option+T | Toggle extended thinking |
| Alt+O / Option+O | Toggle fast mode |

### Text Editing

| Shortcut | Action |
|----------|--------|
| Ctrl+K | Delete to end of line |
| Ctrl+U | Delete to start of line |
| Ctrl+Y | Paste deleted text |
| Alt+Y (after Ctrl+Y) | Cycle paste history |
| Alt+B | Move cursor back one word |
| Alt+F | Move cursor forward one word |

### Multiline Input

| Method | Shortcut |
|--------|----------|
| Quick escape | `\` + Enter |
| macOS default | Option+Enter |
| iTerm2/WezTerm/Ghostty/Kitty | Shift+Enter (native) |
| Control sequence | Ctrl+J |
| Paste mode | Paste directly |

### Quick Prefixes

| Prefix | Action |
|--------|--------|
| `/` at start | Slash command or skill |
| `!` at start | Bash mode (run command, output added to context) |
| `@` | File path autocomplete |

### Voice Input

| Shortcut | Action |
|----------|--------|
| Hold Space | Push-to-talk dictation (requires voice dictation enabled) |

---

## 7. Slash Commands (Complete List)

| Command | Description |
|---------|-------------|
| `/add-dir <path>` | Add a working directory for file access |
| `/agents` | Manage subagent configurations |
| `/autofix-pr [prompt]` | Spawn web session to auto-fix PR CI failures and review comments |
| `/batch <instruction>` | [Skill] Orchestrate parallel changes across codebase |
| `/btw <question>` | Side question without adding to conversation history |
| `/branch [name]` | Fork the conversation at this point (alias: `/fork`) |
| `/chrome` | Configure Chrome integration |
| `/claude-api` | [Skill] Load Claude API reference for your language |
| `/clear` | Clear conversation history (aliases: `/reset`, `/new`) |
| `/color [color]` | Set prompt bar color (`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`) |
| `/compact [instructions]` | Compact conversation with optional focus |
| `/config` | Open Settings interface (alias: `/settings`) |
| `/context` | Visualize context usage as colored grid |
| `/copy [N]` | Copy Nth-latest assistant response to clipboard |
| `/cost` | Show token usage statistics |
| `/debug [description]` | [Skill] Enable debug logging and troubleshoot |
| `/desktop` | Continue session in Desktop app (alias: `/app`) |
| `/diff` | Interactive diff viewer for uncommitted and per-turn changes |
| `/doctor` | Diagnose installation and settings |
| `/effort [level]` | Set effort: `low`, `medium`, `high`, `max` (Opus 4.6), `auto` |
| `/exit` | Exit CLI (alias: `/quit`) |
| `/export [filename]` | Export conversation as plain text |
| `/extra-usage` | Configure extra usage for rate limits |
| `/fast [on\|off]` | Toggle fast mode |
| `/feedback [report]` | Submit feedback (alias: `/bug`) |
| `/help` | Show help and available commands |
| `/hooks` | View hook configurations |
| `/ide` | Manage IDE integrations |
| `/init` | Initialize project with CLAUDE.md |
| `/insights` | Analyze your Claude Code sessions |
| `/install-github-app` | Set up Claude GitHub Actions |
| `/install-slack-app` | Install Claude Slack app |
| `/keybindings` | Open keybindings config file |
| `/login` | Sign in |
| `/logout` | Sign out |
| `/loop [interval] <prompt>` | [Skill] Run prompt on recurring interval |
| `/mcp` | Manage MCP server connections |
| `/memory` | Edit CLAUDE.md files, manage auto-memory |
| `/mobile` | QR code for mobile app (aliases: `/ios`, `/android`) |
| `/model [model]` | Select/change AI model (left/right arrows adjust effort) |
| `/passes` | Share free week of Claude Code |
| `/permissions` | Manage allow/ask/deny rules (alias: `/allowed-tools`) |
| `/plan [description]` | Enter plan mode with optional task |
| `/plugin` | Manage plugins |
| `/powerup` | Interactive feature lessons with demos |
| `/privacy-settings` | View/update privacy settings |
| `/release-notes` | View changelog |
| `/reload-plugins` | Reload active plugins |
| `/remote-control` | Enable Remote Control from claude.ai (alias: `/rc`) |
| `/remote-env` | Configure remote environment for web sessions |
| `/rename [name]` | Rename session (auto-generates if no name given) |
| `/resume [session]` | Resume conversation or open picker (alias: `/continue`) |
| `/rewind` | Rewind conversation and/or code (alias: `/checkpoint`) |
| `/sandbox` | Toggle sandbox mode |
| `/schedule [description]` | Create/manage cloud scheduled tasks |
| `/security-review` | Analyze branch changes for security vulnerabilities |
| `/setup-bedrock` | Configure Amazon Bedrock |
| `/setup-vertex` | Configure Google Vertex AI |
| `/simplify [focus]` | [Skill] Review changed files for quality issues, then fix |
| `/skills` | List available skills |
| `/stats` | Visualize daily usage, sessions, streaks |
| `/status` | Show version, model, account, connectivity |
| `/statusline` | Configure status line |
| `/tasks` | List/manage background tasks (alias: `/bashes`) |
| `/teleport` | Pull web session into terminal (alias: `/tp`) |
| `/terminal-setup` | Configure terminal keybindings |
| `/theme` | Change color theme |
| `/ultraplan <prompt>` | Draft plan with browser review |
| `/upgrade` | Open upgrade page |
| `/usage` | Show plan usage and rate limits |
| `/voice` | Toggle push-to-talk voice dictation |
| `/web-setup` | Connect GitHub to Claude Code on the web |

---

## 8. Permission Modes

### Overview

| Mode | Auto-approved | Best for |
|------|---------------|----------|
| `default` | Reads only | Getting started, sensitive work |
| `acceptEdits` | Reads, file edits, filesystem commands (`mkdir`, `touch`, `rm`, `mv`, `cp`, `sed`) | Iterating on code you review afterward |
| `plan` | Reads only (edits blocked) | Exploring before changing |
| `auto` | Everything, with background classifier safety checks | Long tasks, reducing prompt fatigue |
| `dontAsk` | Only pre-approved tools from `permissions.allow` | Locked-down CI |
| `bypassPermissions` | Everything except protected paths | Isolated containers/VMs only |

### Switching Modes

- **During session**: Shift+Tab cycles `default` -> `acceptEdits` -> `plan`
  - `auto`: appears after `--enable-auto-mode`
  - `bypassPermissions`: appears after starting with `--dangerously-skip-permissions` or `--allow-dangerously-skip-permissions`
  - `dontAsk`: never in cycle; set with `--permission-mode dontAsk`
- **At startup**: `claude --permission-mode plan`
- **As default**: set `permissions.defaultMode` in settings.json

### Auto Mode Requirements

- **Plan**: Team, Enterprise, or API (not Pro/Max)
- **Model**: Claude Sonnet 4.6 or Opus 4.6
- **Provider**: Anthropic API only (not Bedrock/Vertex/Foundry)
- Enable with `--enable-auto-mode`

Auto mode blocks by default: `curl | bash`, sending data to external endpoints, production
deploys, mass deletion, IAM changes, force push, pushing to main. Allows: local file ops,
declared dependency installs, read-only HTTP, pushing to current/created branch.

### Protected Paths (Never Auto-Approved)

Directories: `.git`, `.vscode`, `.idea`, `.husky`, `.claude` (except `.claude/commands`,
`.claude/agents`, `.claude/skills`, `.claude/worktrees`)

Files: `.gitconfig`, `.gitmodules`, `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`,
`.profile`, `.ripgreprc`, `.mcp.json`, `.claude.json`

---

## 9. Piping and Integration Patterns

### Pipe Content In

```bash
# Explain a file
cat src/auth.py | claude -p "explain this module"

# Review a diff
git diff main | claude -p "review for bugs"

# Process build errors
npm run build 2>&1 | claude -p "explain and suggest fixes"

# PR review
gh pr diff 42 | claude -p "security review" --output-format json
```

### Pipe Output Out

```bash
# Save explanation
claude -p "document this API" > api-docs.md

# Chain with other tools
claude -p "list all TODO comments" --output-format json | jq -r '.result'
```

### In Build Scripts

```json
{
  "scripts": {
    "lint:claude": "claude -p 'review changes vs main for typos'",
    "review": "gh pr diff | claude -p 'code review' --output-format json"
  }
}
```

### GitHub Actions / CI

```bash
# Generate long-lived token for CI
claude setup-token

# In CI, use bare mode + API key for consistency
ANTHROPIC_API_KEY="$SECRET" claude --bare -p "run tests and report" --allowedTools "Bash,Read"
```

---

## 10. Environment Variables

### Authentication

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key (overrides subscription billing) |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header (Bearer prefix) |
| `ANTHROPIC_BASE_URL` | Override API endpoint for proxy/gateway |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth access token (from `claude setup-token`) |
| `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` | OAuth refresh token for automated provisioning |

### Model Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `ANTHROPIC_MODEL` | Model to use | Latest Sonnet |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | Custom model ID for picker | None |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents | Same as main |
| `CLAUDE_CODE_EFFORT_LEVEL` | Effort: `low`, `medium`, `high`, `max`, `auto` | `auto` |

### Cloud Providers

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | Enable Amazon Bedrock |
| `ANTHROPIC_BEDROCK_BASE_URL` | Override Bedrock endpoint |
| `CLAUDE_CODE_USE_VERTEX` | Enable Google Vertex AI |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID for Vertex |
| `CLAUDE_CODE_USE_FOUNDRY` | Enable Microsoft Foundry |
| `ANTHROPIC_FOUNDRY_API_KEY` | Foundry API key |

### Thinking & Reasoning

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_DISABLE_THINKING` | Disable extended thinking | Enabled |
| `MAX_THINKING_TOKENS` | Max tokens for thinking | Model-specific |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Disable adaptive reasoning (Opus/Sonnet 4.6) | Enabled |

### Timeouts & Performance

| Variable | Purpose | Default |
|----------|---------|---------|
| `API_TIMEOUT_MS` | API request timeout | 600000 (10 min) |
| `BASH_DEFAULT_TIMEOUT_MS` | Default bash command timeout | 120000 (2 min) |
| `BASH_MAX_TIMEOUT_MS` | Max bash timeout model can set | 600000 (10 min) |
| `CLAUDE_CODE_MAX_RETRIES` | API retry count | 10 |

### Context & Memory

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | Don't load CLAUDE.md files | Loads them |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Disable auto memory | Active |
| `DISABLE_AUTO_COMPACT` | Disable auto-compaction at context limit | Enabled |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Context % (1-100) triggering auto-compact | ~95% |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens | Model-specific |

### Bash & Commands

| Variable | Purpose | Default |
|----------|---------|---------|
| `BASH_MAX_OUTPUT_LENGTH` | Max chars in bash output before truncation | Model-dependent |
| `CLAUDECODE` | Set to `1` in Claude-spawned shells | Not set in hooks |
| `CLAUDE_CODE_SHELL` | Override shell detection | Auto-detected |
| `CLAUDE_CODE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Return to project dir after each command | Disabled |

### Display & UI

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_NO_FLICKER` | Enable fullscreen rendering (research preview) |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | Don't update terminal title |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION` | Show prompt suggestions | Enabled |
| `CLAUDE_CODE_SYNTAX_HIGHLIGHT` | Enable syntax highlighting in diffs |

### Background & Tasks

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disable background task support and Ctrl+B |
| `CLAUDE_CODE_DISABLE_CRON` | Disable scheduled tasks |
| `CLAUDE_CODE_TASK_LIST_ID` | Share task list across sessions |

### Telemetry & Updates

| Variable | Purpose |
|----------|---------|
| `DISABLE_TELEMETRY` | Opt out of telemetry |
| `DISABLE_AUTOUPDATER` | Disable auto-updates |
| `DISABLE_ERROR_REPORTING` | Opt out of Sentry error reporting |

### Directories

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CONFIG_DIR` | Override config directory | `~/.claude` |
| `CLAUDE_CODE_TMPDIR` | Override temp directory | `/tmp` (macOS) |

### Network & Proxy

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | Let proxy do DNS resolution |
| `CLAUDE_CODE_CLIENT_CERT` | Client cert for mTLS |
| `CLAUDE_CODE_CLIENT_KEY` | Client key for mTLS |

### Security

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Disable 1M context window |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | Strip credentials from subprocess environments |

---

## 11. Configuration via CLI

### claude config

```bash
# List all settings
claude config list

# Get a specific setting
claude config get permissions.defaultMode

# Set a value
claude config set permissions.defaultMode acceptEdits

# Add to an array
claude config add permissions.allow "Bash(npm test)"

# Remove from an array
claude config remove permissions.allow "Bash(npm test)"
```

### claude mcp

```bash
# Add an MCP server
claude mcp add my-server -- npx -y @example/mcp-server

# List registered servers
claude mcp list

# Remove a server
claude mcp remove my-server
```

MCP servers are stored in:
- `~/.claude.json` -- global
- `.mcp.json` -- project-scoped (at project root)

### Configuration Scopes

| Scope | Location | Shared? |
|-------|----------|---------|
| Managed | Server-managed / plist / registry | Yes (deployed by IT) |
| User | `~/.claude/settings.json` | No |
| Project | `<project>/.claude/settings.json` | Yes (committed to repo) |
| Local | `<project>/.claude/settings.local.json` | No (gitignored) |

Settings can also be set via environment variables using the `env` key in settings.json:

```json
{
  "env": {
    "ANTHROPIC_MODEL": "claude-opus-4-1",
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "API_TIMEOUT_MS": "900000"
  }
}
```

### claude plugin

```bash
# Install a plugin
claude plugin install code-review@claude-plugins-official

# List installed plugins
claude plugin list

# Remove a plugin
claude plugin remove code-review
```

---

## Sources

- [CLI Reference](https://code.claude.com/docs/en/cli-reference) -- Official CLI flags and commands
- [Run Claude Code Programmatically](https://code.claude.com/docs/en/headless) -- Print mode and Agent SDK
- [Permission Modes](https://code.claude.com/docs/en/permission-modes) -- Mode descriptions and configuration
- [Settings](https://code.claude.com/docs/en/settings) -- Configuration files and scopes
- [Environment Variables](https://code.claude.com/docs/en/env-vars) -- Complete env var reference
- [Commands](https://code.claude.com/docs/en/commands) -- Slash command reference
- [Interactive Mode](https://code.claude.com/docs/en/interactive-mode) -- Keyboard shortcuts and features
- [Common Workflows](https://code.claude.com/docs/en/common-workflows) -- Worktrees, sessions, piping patterns
