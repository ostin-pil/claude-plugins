# Claude Code Settings Reference

Comprehensive reference for configuring Claude Code via `settings.json`, environment variables, and related mechanisms. Based on official documentation as of April 2026.

---

## 1. Configuration Scopes and Precedence

Claude Code uses a layered scope system. When the same setting appears in multiple scopes, the highest-priority scope wins.

### Precedence Order (highest to lowest)

| Priority | Scope | Location | Shared? |
|----------|-------|----------|---------|
| 1 | **Managed** | Server-managed, MDM/plist/registry, or `managed-settings.json` | Yes (deployed by IT) |
| 2 | **CLI flags** | `--model`, `--permission-mode`, etc. | No (session only) |
| 3 | **Local** | `.claude/settings.local.json` | No (gitignored) |
| 4 | **Project** | `.claude/settings.json` | Yes (committed to git) |
| 5 | **User** | `~/.claude/settings.json` | No (personal, all projects) |

### Array Merging

Array-valued settings (e.g., `permissions.allow`, `sandbox.filesystem.allowWrite`) are **concatenated and deduplicated** across scopes, not replaced. A managed scope adding `["/opt/tools"]` and a user scope adding `["~/.kube"]` results in both paths being active.

### Managed Settings Locations

- **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
- **Linux/WSL**: `/etc/claude-code/managed-settings.json`
- **Windows**: `C:\Program Files\ClaudeCode\managed-settings.json`

Within the managed tier, precedence is: server-managed > MDM/OS-level > file-based > HKCU registry (Windows). Drop-in directory `managed-settings.d/` supports fragments merged alphabetically (use numeric prefixes like `10-telemetry.json`).

### Verify Active Settings

Run `/status` inside Claude Code to see which settings sources are active and where they come from.

---

## 2. All Settings Fields

Add `"$schema": "https://json.schemastore.org/claude-code-settings.json"` to any settings file for editor autocomplete.

### Core Settings

| Key | Description | Default | Example |
|-----|-------------|---------|---------|
| `model` | Override default model | Current default | `"claude-sonnet-4-6"` |
| `availableModels` | Restrict models users can select via `/model` | All models | `["sonnet", "haiku"]` |
| `effortLevel` | Persist effort level across sessions | Not set | `"low"`, `"medium"`, `"high"` |
| `alwaysThinkingEnabled` | Enable extended thinking by default | `false` | `true` |
| `language` | Claude's response language; also sets voice dictation language | English | `"japanese"` |
| `outputStyle` | Adjust system prompt style | Not set | `"Explanatory"` |
| `agent` | Run main thread as a named subagent | Not set | `"code-reviewer"` |
| `autoUpdatesChannel` | Release channel: `"stable"` or `"latest"` | `"latest"` | `"stable"` |

### Permission Settings

| Key | Description | Example |
|-----|-------------|---------|
| `permissions.allow` | Array of rules to auto-allow tool use | `["Bash(git diff *)"]` |
| `permissions.ask` | Array of rules requiring confirmation | `["Bash(git push *)"]` |
| `permissions.deny` | Array of rules to block tool use | `["Read(./.env)", "WebFetch"]` |
| `permissions.additionalDirectories` | Additional working directories for file access | `["../docs/"]` |
| `permissions.defaultMode` | Default permission mode on startup | `"default"` |
| `permissions.disableBypassPermissionsMode` | Prevent bypass permissions mode | `"disable"` |
| `permissions.skipDangerousModePermissionPrompt` | Skip bypass confirmation prompt | `true` |

### Sandbox Settings

Nested under `"sandbox"`:

| Key | Description | Default |
|-----|-------------|---------|
| `enabled` | Enable bash sandboxing | `false` |
| `failIfUnavailable` | Exit if sandbox cannot start | `false` |
| `autoAllowBashIfSandboxed` | Auto-approve bash when sandboxed | `true` |
| `excludedCommands` | Commands that run outside sandbox | `[]` |
| `allowUnsandboxedCommands` | Allow `dangerouslyDisableSandbox` escape hatch | `true` |
| `filesystem.allowWrite` | Additional writable paths | `[]` |
| `filesystem.denyWrite` | Paths blocked from writing | `[]` |
| `filesystem.denyRead` | Paths blocked from reading | `[]` |
| `filesystem.allowRead` | Re-allow reads within denyRead regions | `[]` |
| `filesystem.allowManagedReadPathsOnly` | Only managed allowRead paths apply (managed only) | `false` |
| `network.allowedDomains` | Allowed outbound domains (supports wildcards) | `[]` |
| `network.allowUnixSockets` | Unix sockets accessible in sandbox | `[]` |
| `network.allowAllUnixSockets` | Allow all Unix socket connections | `false` |
| `network.allowLocalBinding` | Allow binding to localhost (macOS only) | `false` |
| `network.allowMachLookup` | XPC/Mach service names (macOS only) | `[]` |
| `network.allowManagedDomainsOnly` | Only managed domains apply (managed only) | `false` |
| `network.httpProxyPort` | Custom HTTP proxy port | Auto |
| `network.socksProxyPort` | Custom SOCKS5 proxy port | Auto |
| `enableWeakerNestedSandbox` | Weaker sandbox for Docker (Linux/WSL2, reduces security) | `false` |
| `enableWeakerNetworkIsolation` | Allow TLS trust service in sandbox (macOS, reduces security) | `false` |

### Worktree Settings

| Key | Description | Default | Example |
|-----|-------------|---------|---------|
| `worktree.symlinkDirectories` | Directories to symlink into each worktree | `[]` | `["node_modules", ".cache"]` |
| `worktree.sparsePaths` | Sparse-checkout paths (cone mode) | `[]` | `["packages/my-app", "shared/utils"]` |

To copy gitignored files (like `.env`) into new worktrees, create a `.worktreeinclude` file in the project root listing one path per line.

### MCP Settings

| Key | Description | Example |
|-----|-------------|---------|
| `enableAllProjectMcpServers` | Auto-approve all project `.mcp.json` servers | `true` |
| `enabledMcpjsonServers` | Specific MCP servers to approve | `["memory", "github"]` |
| `disabledMcpjsonServers` | Specific MCP servers to reject | `["filesystem"]` |
| `allowedMcpServers` | Allowlist of MCP servers (managed only) | `[{"serverName": "github"}]` |
| `deniedMcpServers` | Denylist of MCP servers (managed only) | `[{"serverName": "filesystem"}]` |
| `allowManagedMcpServersOnly` | Only managed allowlist applies (managed only) | `true` |

### Attribution Settings

Nested under `"attribution"`:

| Key | Description | Default |
|-----|-------------|---------|
| `commit` | Git commit attribution text | Generated with Claude Code + Co-Authored-By trailer |
| `pr` | Pull request description attribution | Generated with Claude Code |

Set to empty string `""` to hide attribution. The deprecated `includeCoAuthoredBy` still works but `attribution` takes precedence.

### Hook Settings

| Key | Description |
|-----|-------------|
| `hooks` | Object defining lifecycle event hooks (see hooks docs) |
| `disableAllHooks` | Disable all hooks and custom status line |
| `allowManagedHooksOnly` | Only managed/SDK hooks run (managed only) |
| `allowedHttpHookUrls` | URL patterns HTTP hooks may target (supports `*` wildcard) |
| `httpHookAllowedEnvVars` | Env var names HTTP hooks may interpolate into headers |

### UI and Display Settings

| Key | Description | Default |
|-----|-------------|---------|
| `prefersReducedMotion` | Reduce UI animations | `false` |
| `spinnerTipsEnabled` | Show tips in spinner | `true` |
| `spinnerTipsOverride` | Custom spinner tips (with `excludeDefault` option) | Built-in tips |
| `spinnerVerbs` | Custom action verbs for spinner | Built-in verbs |
| `showThinkingSummaries` | Show extended thinking summaries | `false` |
| `showClearContextOnPlanAccept` | Show clear-context option on plan accept | `false` |
| `respectGitignore` | `@` file picker respects .gitignore | `true` |
| `statusLine` | Custom status line command | Not set |
| `voiceEnabled` | Enable push-to-talk voice dictation | `false` |

### Auto Mode Settings

| Key | Description |
|-----|-------------|
| `autoMode` | Configure auto mode classifier (`environment`, `allow`, `soft_deny` arrays) |
| `disableAutoMode` | Set to `"disable"` to prevent auto mode activation |
| `useAutoModeDuringPlan` | Whether plan mode uses auto mode semantics | 

### Enterprise / Managed-Only Settings

| Key | Description |
|-----|-------------|
| `companyAnnouncements` | Announcements displayed at startup |
| `forceLoginMethod` | Restrict to `"claudeai"` or `"console"` accounts |
| `forceLoginOrgUUID` | Require login to specific org UUID(s) |
| `forceRemoteSettingsRefresh` | Block startup until remote settings fetched |
| `allowManagedPermissionRulesOnly` | Only managed permission rules apply |
| `channelsEnabled` | Allow channels for Team/Enterprise users |
| `allowedChannelPlugins` | Allowlist of channel plugins |
| `strictKnownMarketplaces` | Allowlist of plugin marketplaces |
| `blockedMarketplaces` | Blocklist of marketplace sources |
| `pluginTrustMessage` | Custom message on plugin trust warning |
| `disableSkillShellExecution` | Disable shell execution in skills |

### Other Settings

| Key | Description | Default |
|-----|-------------|---------|
| `env` | Environment variables for every session | `{}` |
| `cleanupPeriodDays` | Session file retention period | 30 |
| `apiKeyHelper` | Script to generate auth value | Not set |
| `awsAuthRefresh` | Script for AWS credential refresh | Not set |
| `awsCredentialExport` | Script outputting JSON AWS credentials | Not set |
| `fileSuggestion` | Custom `@` file autocomplete command | Built-in |
| `plansDirectory` | Where plan files are stored | `~/.claude/plans` |
| `includeGitInstructions` | Include git workflow in system prompt | `true` |
| `autoMemoryEnabled` | Enable auto memory | `true` |
| `autoMemoryDirectory` | Custom auto memory storage path | `~/.claude/projects/<project>/memory/` |
| `feedbackSurveyRate` | Probability (0-1) of session quality survey | Platform-dependent |
| `fastModePerSessionOptIn` | Fast mode requires per-session opt-in | `false` |
| `defaultShell` | Shell for `!` commands (`"bash"` or `"powershell"`) | `"bash"` |
| `disableDeepLinkRegistration` | Prevent `claude-cli://` protocol registration | Not set |

### Global Config Settings (in ~/.claude.json, NOT settings.json)

| Key | Description | Default |
|-----|-------------|---------|
| `autoConnectIde` | Auto-connect to running IDE | `false` |
| `autoInstallIdeExtension` | Auto-install IDE extension in VS Code | `true` |
| `editorMode` | Key binding mode: `"normal"` or `"vim"` | `"normal"` |
| `showTurnDuration` | Show turn duration messages | `true` |
| `terminalProgressBarEnabled` | Show terminal progress bar | `true` |
| `teammateMode` | Agent team display mode: `auto`, `in-process`, `tmux` | `auto` |

---

## 3. Permission System

### Rule Syntax

Permission rules follow the format `Tool` or `Tool(specifier)`. Rules are evaluated: **deny first, then ask, then allow**. First match wins.

| Rule | Effect |
|------|--------|
| `Bash` | Matches all Bash commands |
| `Bash(npm run *)` | Matches commands starting with `npm run` |
| `Bash(git *)` | Matches all git commands |
| `Read(./.env)` | Matches reading the `.env` file |
| `Read(./.env.*)` | Matches all `.env.*` files |
| `Read(./secrets/**)` | Matches everything under `secrets/` recursively |
| `Edit(./src/**)` | Matches editing files under `src/` |
| `WebFetch` | Matches all web fetch requests |
| `WebFetch(domain:example.com)` | Matches fetch requests to specific domain |

### Path Conventions in Permission Rules

- `./path` or `path` -- relative to project root
- `//path` -- absolute path
- `~/.path` -- relative to home directory
- `*` matches within a single path segment
- `**` matches across path segments recursively

### Security Note on Bash Patterns

Bash permission patterns have inherent limitations. A rule like `Bash(rm *)` only matches commands literally starting with `rm`. It does not catch `bash -c "rm file"` or piped commands. Bash deny rules are a convenience layer, not a security boundary. Use sandbox filesystem restrictions for hard enforcement.

---

## 4. Sandbox Configuration

### How It Works

- **macOS**: Uses Seatbelt (built-in, no dependencies)
- **Linux/WSL2**: Uses bubblewrap (`bwrap`) + socat (must be installed)
- **WSL1**: Not supported

### Key Behaviors

- **Filesystem**: By default, sandboxed commands can read the entire system but only write to the working directory. Configure `allowWrite`, `denyWrite`, `denyRead`, `allowRead` for fine-grained control.
- **Network**: Controlled via proxy. Only approved domains accessible. New domains trigger prompts.
- **dangerouslyDisableSandbox**: When a command fails due to sandbox restrictions, Claude may retry with this parameter, which routes the command through the normal permission flow. Set `allowUnsandboxedCommands: false` to completely disable this escape hatch.

### Sandbox Path Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `/` | Absolute path | `/tmp/build` |
| `~/` | Home directory | `~/.kube` |
| `./` or bare | Project root (project settings) or `~/.claude` (user settings) | `./output` |

### Example Configuration

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowLocalBinding": true
    }
  }
}
```

---

## 5. Worktree Settings

The `--worktree` flag creates git worktrees for parallel agent work. Two settings optimize this:

```json
{
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache", ".venv"],
    "sparsePaths": ["packages/my-app", "shared/utils"]
  }
}
```

- **symlinkDirectories**: Symlinked from main repo to avoid duplicating large directories on disk.
- **sparsePaths**: Only these directories are checked out via `git sparse-checkout` (cone mode). Faster in large monorepos.

### .worktreeinclude File

Create `.worktreeinclude` in the project root to copy gitignored files into new worktrees. List one path per line:

```
.env
.env.local
config/local.json
```

### Worktree Cleanup

Orphaned subagent worktrees are automatically cleaned up at startup based on `cleanupPeriodDays` (default: 30).

---

## 6. Model and Effort Settings

### Model Selection

```json
{ "model": "claude-opus-4-6" }
```

Or via environment variable: `ANTHROPIC_MODEL=claude-sonnet-4-6`

CLI flag: `claude --model claude-sonnet-4-6`

### Restrict Available Models

```json
{ "availableModels": ["sonnet", "haiku"] }
```

This restricts what appears in `/model` picker. Does not affect the Default option.

### Model Overrides (Provider-Specific IDs)

```json
{
  "modelOverrides": {
    "claude-opus-4-6": "arn:aws:bedrock:us-east-1:123456:inference-profile/opus"
  }
}
```

### Effort Level

Accepts `"low"`, `"medium"`, or `"high"`. Supported on Opus 4.6 and Sonnet 4.6.

```json
{ "effortLevel": "medium" }
```

Or via environment: `CLAUDE_CODE_EFFORT_LEVEL=low`

Or interactively: `/effort low`

### Extended Thinking

```json
{ "alwaysThinkingEnabled": true }
```

Control max thinking tokens via `MAX_THINKING_TOKENS` env var. Disable entirely with `CLAUDE_CODE_DISABLE_THINKING=1`.

---

## 7. MCP-Related Settings

### Approving Project MCP Servers

```json
{
  "enableAllProjectMcpServers": true
}
```

Or selectively:

```json
{
  "enabledMcpjsonServers": ["memory", "github"],
  "disabledMcpjsonServers": ["filesystem"]
}
```

### MCP Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TIMEOUT` | Server startup/connection timeout (ms) | Platform default |
| `MCP_TOOL_TIMEOUT` | Single tool invocation timeout (ms) | Platform default |
| `MAX_MCP_OUTPUT_TOKENS` | Maximum tokens for MCP tool output | 25,000 |

A warning appears when any MCP tool output exceeds 10,000 tokens. Tools setting `anthropic/maxResultSizeChars` use that value instead.

### MCP Server Locations

- **User scope**: `~/.claude.json`
- **Project scope**: `.mcp.json` in project root
- **Managed scope**: `managed-mcp.json` in system directory

### Managed MCP Configuration

```json
{
  "allowedMcpServers": [{ "serverName": "github" }],
  "deniedMcpServers": [{ "serverName": "filesystem" }],
  "allowManagedMcpServersOnly": true
}
```

Deny list always takes precedence over allow list.

---

## 8. claudeMdExcludes

Skip irrelevant `CLAUDE.md` files in monorepos or multi-team setups:

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

- Patterns are matched against **absolute file paths** using glob syntax.
- Configurable at any settings layer (user, project, local, managed). Arrays merge across layers.
- **Managed policy CLAUDE.md files cannot be excluded** -- organizational instructions always apply.
- Place in `.claude/settings.local.json` to keep exclusions personal.

---

## 9. Environment Variables

### Authentication and API

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key for requests |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header |
| `ANTHROPIC_BASE_URL` | Override API endpoint |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth access token |
| `CLAUDE_CODE_OAUTH_REFRESH_TOKEN` | OAuth refresh token |

### Cloud Provider Backends

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | Enable AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Enable Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY` | Enable Microsoft Foundry |
| `ANTHROPIC_BEDROCK_BASE_URL` | Override Bedrock endpoint |
| `ANTHROPIC_VERTEX_BASE_URL` | Override Vertex endpoint |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Override Foundry endpoint |

### Model Configuration

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_MODEL` | Model name override |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku-class model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet-class model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus-class model |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |
| `CLAUDE_CODE_EFFORT_LEVEL` | Effort level (`low`, `medium`, `high`, `max`, `auto`) |
| `MAX_THINKING_TOKENS` | Max tokens for extended thinking |

### Context and Tokens

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Disable 1M context window | Enabled |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens | Model default |
| `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` | Max concurrent read-only tools | 10 |
| `MAX_MCP_OUTPUT_TOKENS` | Max MCP tool output tokens | 25,000 |

### Timeouts

| Variable | Purpose | Default |
|----------|---------|---------|
| `API_TIMEOUT_MS` | API request timeout | 600,000 (10 min) |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash command timeout | 120,000 (2 min) |
| `BASH_MAX_TIMEOUT_MS` | Max bash timeout | 600,000 (10 min) |
| `MCP_TIMEOUT` | MCP server connection timeout | Platform default |
| `MCP_TOOL_TIMEOUT` | MCP tool invocation timeout | Platform default |

### Shell and Execution

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_SHELL` | Override shell detection |
| `CLAUDE_CODE_SHELL_PREFIX` | Prefix for all bash commands |
| `CLAUDE_ENV_FILE` | Shell script to source before bash commands |
| `CLAUDECODE` | Set to `1` in spawned environments |

### Context and Memory

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | Prevent loading CLAUDE.md files |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | Disable auto memory |
| `DISABLE_AUTO_COMPACT` | Disable automatic compaction |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Context % threshold for auto-compaction (1-100) |

### File Operations

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CONFIG_DIR` | Configuration directory | `~/.claude` |
| `CLAUDE_CODE_TMPDIR` | Temp directory | `/tmp` (macOS) |
| `CLAUDE_CODE_GLOB_TIMEOUT_SECONDS` | Glob tool timeout | 20s (60s on WSL) |
| `CLAUDE_CODE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Reset cwd after bash | `false` |

### Telemetry and Monitoring

| Variable | Purpose |
|----------|---------|
| `DISABLE_TELEMETRY` | Opt out of telemetry |
| `DISABLE_ERROR_REPORTING` | Opt out of Sentry |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | Enable OpenTelemetry collection |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable updater, feedback, telemetry |
| `DISABLE_AUTOUPDATER` | Disable auto-updates |

### Debug

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | Debug log path | `~/.claude/debug/<session>.txt` |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL` | Log level | `debug` |

### UI

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_SCROLL_SPEED` | Mouse wheel scroll multiplier (1-20) |
| `CLAUDE_CODE_DISABLE_MOUSE` | Disable mouse tracking in fullscreen |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | Disable terminal title updates |
| `CLAUDE_CODE_NO_FLICKER` | Enable fullscreen rendering (research preview) |

### Retries

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_MAX_RETRIES` | API request retries | 10 |

---

## 10. Recommended Configurations

### Minimal Personal Setup

`~/.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm run *)",
      "Bash(swift build *)",
      "Bash(swift test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  },
  "model": "claude-sonnet-4-6",
  "effortLevel": "medium"
}
```

### Project with Sandbox Enabled

`.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npx jest *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git status)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build"],
      "denyRead": ["~/.aws/credentials", "~/.ssh"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org", "registry.yarnpkg.com"]
    }
  }
}
```

### Enterprise Managed Settings

`/Library/Application Support/ClaudeCode/managed-settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(curl *)",
      "Bash(wget *)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "disableAutoMode": "disable",
  "forceLoginMethod": "console",
  "forceLoginOrgUUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "DISABLE_AUTOUPDATER": "1"
  },
  "companyAnnouncements": [
    "Remember: all code must pass security review before merge"
  ]
}
```

### Token-Efficient Setup

```json
{
  "effortLevel": "low",
  "env": {
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "4096",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "MAX_MCP_OUTPUT_TOKENS": "10000"
  }
}
```

### Monorepo with claudeMdExcludes

`.claude/settings.local.json`:

```json
{
  "claudeMdExcludes": [
    "**/packages/team-b/CLAUDE.md",
    "**/packages/team-c/.claude/rules/**"
  ],
  "worktree": {
    "symlinkDirectories": ["node_modules", ".yarn/cache"],
    "sparsePaths": ["packages/my-app", "shared/lib"]
  }
}
```

---

## Sources

- [Claude Code Settings (official docs)](https://code.claude.com/docs/en/settings)
- [Claude Code Environment Variables (official docs)](https://code.claude.com/docs/en/env-vars)
- [Claude Code Memory / CLAUDE.md (official docs)](https://code.claude.com/docs/en/memory)
- [Claude Code Sandboxing (official docs)](https://code.claude.com/docs/en/sandboxing)
- [Claude Code MCP (official docs)](https://code.claude.com/docs/en/mcp)
- [JSON Schema for settings](https://json.schemastore.org/claude-code-settings.json)
