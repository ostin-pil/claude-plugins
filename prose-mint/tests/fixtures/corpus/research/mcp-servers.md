# MCP Servers (Model Context Protocol) -- Deep Dive

*Compiled: 2026-04-09*

---

## 1. Transport Types Deep Dive

MCP uses JSON-RPC 2.0 (UTF-8 encoded) over pluggable transports. The spec defines two standard transports: **stdio** and **Streamable HTTP**. A legacy **HTTP+SSE** transport exists but is deprecated.

### 1.1 stdio

The most common and most interoperable transport. The client launches the MCP server as a **subprocess**.

**How it works:**
- Server reads JSON-RPC messages from `stdin`, writes responses to `stdout`
- Messages are newline-delimited, must NOT contain embedded newlines
- `stderr` is available for logging (never write non-MCP data to stdout)
- Client terminates the server by closing stdin and killing the subprocess

**Connection lifecycle:**
```
Client -> Launch subprocess
Client -> Write JSON-RPC to stdin
Server -> Write JSON-RPC to stdout
Server -> (optional) Write logs to stderr
Client -> Close stdin, terminate subprocess
```

**When to use:** Local tools, CLI integrations, development servers, anything running on the same machine. This is the default for Claude Code `--transport stdio`.

**Error handling:** If the process crashes, the client detects EOF on stdout. No reconnection -- the client must relaunch the subprocess.

**Critical logging rule:** Never use `console.log()` (TypeScript) or `print()` (Python) in stdio servers -- they write to stdout and corrupt the JSON-RPC stream. Use `console.error()` or `print(..., file=sys.stderr)` instead.

### 1.2 Streamable HTTP

Replaced the legacy HTTP+SSE transport in protocol version 2025-03-26. The server is an independent process handling multiple client connections over a single HTTP endpoint.

**How it works:**
- Server exposes one endpoint (e.g., `https://example.com/mcp`) supporting POST and GET
- Client sends JSON-RPC messages via HTTP POST
- Server responds with either `application/json` (single response) or `text/event-stream` (SSE stream)
- Client can open a GET-based SSE stream to receive server-initiated messages

**Session management:**
- Server MAY assign a session ID via `MCP-Session-Id` header during initialization
- Client MUST include this header on all subsequent requests
- Sessions can be explicitly terminated with HTTP DELETE
- Server responds 404 when a session expires, signaling the client to re-initialize

**Resumability:**
- Server MAY attach SSE event IDs for stream resumption
- Client reconnects with `Last-Event-ID` header to resume from where it left off
- Event IDs are per-stream, acting as cursors within that stream

**Security requirements:**
- Servers MUST validate the `Origin` header to prevent DNS rebinding
- Local servers SHOULD bind only to `127.0.0.1`, not `0.0.0.0`
- Servers SHOULD implement proper authentication

**When to use:** Remote/cloud servers, multi-tenant services, anything accessed over the network.

### 1.3 Legacy HTTP+SSE (Deprecated)

From protocol version 2024-11-05. Used two separate endpoints: one for SSE streaming (GET) and one for posting messages (POST). Still supported by many tools but should not be used for new servers.

**Backwards compatibility:** Clients wanting to support both old and new servers can attempt a POST to the server URL first. If it fails with 400/404/405, fall back to GET expecting an SSE stream with an `endpoint` event.

### 1.4 Transport Selection Guide

| Factor | stdio | Streamable HTTP |
|--------|-------|-----------------|
| Deployment | Local process | Remote/cloud service |
| Multi-client | No (1:1) | Yes (many:1) |
| Authentication | Via env vars | OAuth, headers, tokens |
| Reconnection | Relaunch process | Automatic via SSE resume |
| Firewall friendly | N/A (local) | Yes (standard HTTPS) |
| Claude Code default | Yes | Use `--transport http` |

---

## 2. Authentication Patterns

### 2.1 OAuth 2.0 (Recommended for Remote Servers)

Claude Code has first-class OAuth support. The flow:

1. Add the server: `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`
2. Run `/mcp` in Claude Code, select "Authenticate"
3. Browser opens for the OAuth login flow
4. Tokens stored securely in system keychain (macOS) and refreshed automatically

**OAuth metadata discovery chain:**
1. RFC 9728: `/.well-known/oauth-protected-resource`
2. Fallback to RFC 8414: `/.well-known/oauth-authorization-server`

**Override discovery** when the default chain fails:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "authServerMetadataUrl": "https://auth.example.com/.well-known/openid-configuration"
      }
    }
  }
}
```

**Pre-configured OAuth credentials** (when Dynamic Client Registration is unavailable):

```bash
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

The `--callback-port` flag fixes the localhost port for the redirect URI, matching what you registered in the provider's developer portal.

**CI environments** (non-interactive):

```bash
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

### 2.2 Static Headers (API Keys / Bearer Tokens)

```bash
# Bearer token
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

# API key
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"
```

### 2.3 Dynamic Headers (headersHelper)

For Kerberos, short-lived tokens, internal SSO, or any non-OAuth scheme. Claude Code runs a command and merges its stdout (JSON object) into connection headers.

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

Requirements:
- Command must output a JSON object of string key-value pairs to stdout
- 10-second timeout
- Dynamic headers override static `headers` with the same name
- Runs fresh on each connection (no caching)
- Environment vars `CLAUDE_CODE_MCP_SERVER_NAME` and `CLAUDE_CODE_MCP_SERVER_URL` are set

### 2.4 Environment Variable Injection

For stdio servers, pass secrets via `--env`:

```bash
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable \
  -- npx -y airtable-mcp-server
```

### 2.5 Environment Variable Expansion in .mcp.json

Supports `${VAR}` and `${VAR:-default}` syntax in `command`, `args`, `env`, `url`, and `headers`:

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

---

## 3. Building Custom MCP Servers

### 3.1 Available SDKs

| Language | Package | Notes |
|----------|---------|-------|
| TypeScript | `@modelcontextprotocol/sdk` | Official. Handler-based with Zod validation |
| Python | `mcp[cli]` (FastMCP) | Official. Type hints auto-generate tool schemas |
| Go | `github.com/mark3labs/mcp-go` | Community. Widely used |
| Rust | `rmcp` | Community |
| Java/Kotlin | `io.modelcontextprotocol:sdk` | Community |
| C# | `ModelContextProtocol` | Community |

### 3.2 TypeScript Example (Minimal)

```bash
mkdir my-server && cd my-server
npm init -y
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
```

`tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true
  },
  "include": ["src/**/*"]
}
```

`package.json` additions:
```json
{
  "type": "module",
  "bin": { "my-server": "./build/index.js" },
  "scripts": { "build": "tsc && chmod 755 build/index.js" }
}
```

`src/index.ts`:
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

server.registerTool(
  "greet",
  {
    description: "Greet a user by name",
    inputSchema: {
      name: z.string().describe("The user's name"),
    },
  },
  async ({ name }) => ({
    content: [{ type: "text", text: `Hello, ${name}!` }],
  })
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Server running on stdio");
}

main().catch(console.error);
```

Build and test: `npm run build && node build/index.js`

### 3.3 Python Example (Minimal)

```bash
uv init my-server && cd my-server
uv venv && source .venv/bin/activate
uv add "mcp[cli]" httpx
```

`server.py`:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def greet(name: str) -> str:
    """Greet a user by name.

    Args:
        name: The user's name
    """
    return f"Hello, {name}!"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

Run: `uv run server.py`

**Key difference:** Python's FastMCP uses type hints and docstrings to auto-generate tool schemas. TypeScript requires explicit Zod schemas.

### 3.4 Server Capabilities

MCP servers can expose three types of capabilities:
1. **Tools** -- Functions the LLM can call (with user approval)
2. **Resources** -- File-like data the client can read (API responses, file contents)
3. **Prompts** -- Pre-written templates for specific tasks

### 3.5 Connecting to Claude Code

```bash
# stdio server
claude mcp add --transport stdio my-server -- node /path/to/build/index.js

# Or for Python
claude mcp add --transport stdio my-server -- uv run /path/to/server.py
```

---

## 4. Lazy Loading / Tool Search Mechanism

### 4.1 The Problem

Each MCP tool definition consumes context tokens. With 5+ MCP servers exposing 50+ tools, tool definitions alone can eat 10-20% of the context window before any work begins.

### 4.2 How Tool Search Works

Shipped in Claude Code 2.1.7. Automatically activates when MCP tools would consume >10% of context.

**Loading sequence:**
1. **Session start:** Only tool *names* are loaded (not full schemas). These appear in `<system-reminder>` messages as "deferred tools"
2. **Task execution:** When Claude needs a tool, it calls `ToolSearch` with a query
3. **Schema loading:** ToolSearch returns the full JSON schema for matching tools
4. **Sticky-on latching:** Once loaded, a tool stays in context for the rest of the session (prevents cache invalidation from repeated load/unload)

**ToolSearch query patterns:**
- `"select:Read,Edit,Grep"` -- Fetch exact tools by name
- `"computer-use"` -- Keyword search matching tool name substrings
- `"+slack send"` -- Require "slack" in name, rank by remaining terms

### 4.3 Context Savings

Anthropic reports ~85% reduction in token overhead from MCP tool definitions. In practice, a session with 8 MCP servers might go from ~15K tokens of tool definitions to ~2K tokens of deferred names.

### 4.4 Impact on Server Developers

The `instructions` field in your MCP server metadata becomes critical. It helps Claude know *when* to search for your tools. Without good instructions, Claude may not discover your tools exist.

### 4.5 Configuration

Tool Search is automatic and on by default. To disable:

```json
// In Claude Code settings
{ "enable_tool_search": false }
```

Or via environment variable: `ENABLE_TOOL_SEARCH=false`

---

## 5. Top MCP Servers Deep Dive

### 5.1 GitHub

**Setup:**
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
# Then: /mcp -> Authenticate
```

**Key tools:** Repository management, PR creation/review, issue tracking, code search, file operations, branch management, release management.

**Usage examples:**
```
Review PR #456 and suggest improvements
Create a new issue for the bug we just found
Show me all open PRs assigned to me
Search for usages of deprecated API across our org
```

### 5.2 Playwright (Microsoft)

**Setup:**
```bash
claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest
```

**Key tools:** `browser_navigate`, `browser_click`, `browser_fill`, `browser_take_screenshot`, `browser_resize`, `browser_evaluate` (JavaScript execution), `browser_select_option`, `browser_hover`, `browser_drag`.

**Capabilities:** Multi-browser support (Chromium, Firefox, WebKit), 143+ device presets, responsive testing, test code generation, web scraping, console log monitoring.

**Usage examples:**
```
Navigate to our staging site and take a screenshot of the login page
Fill in the signup form with test data and submit it
Test the checkout flow on iPhone 14 viewport
```

### 5.3 PostgreSQL (via Bytebase dbhub)

**Setup:**
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

**Key tools:** SQL query execution, schema inspection, table listing, index information.

**Usage examples:**
```
What's our total revenue this month?
Show me the schema for the orders table
Find customers who haven't made a purchase in 90 days
```

**Best practice:** Always use a read-only database user for safety.

### 5.4 Context7 (Upstash)

**Setup:**
```bash
claude mcp add --transport stdio context7 -- npx -y @upstash/context7-mcp@latest
```

**Key tools:**
- `resolve-library-id` -- Takes a library name, returns a Context7-compatible library ID
- `get-library-docs` -- Retrieves current documentation for a library, with topic filtering and token limits

**Covers:** 9,000+ libraries and frameworks. Indexes new versions within days of release.

**Usage:** Add "use context7" to prompts to trigger documentation fetching:
```
How do I set up middleware in Next.js 15? use context7
What's the correct way to use React Server Components? use context7
```

**No authentication required** for basic usage. Optional API key from context7.com/dashboard for higher rate limits.

### 5.5 Figma

**Setup:**
```bash
claude mcp add --transport http figma https://mcp.figma.com/mcp
# Then: /mcp -> Authenticate with Figma account
```

**Key tools:** Read Figma files, extract design tokens (colors, typography, spacing), get layout data, inspect component properties.

**Usage examples:**
```
Extract the color palette from our design system file
Generate CSS for the card component in the homepage mockup
What spacing values are used in the navigation bar design?
```

### 5.6 Supabase

**Setup:**
```bash
claude mcp add --transport http supabase https://mcp.supabase.com
# Then: /mcp -> Authenticate
```

**Key tools:** Database queries, table schema management, migration creation, Edge Function deployment, storage operations.

**Usage examples:**
```
Design a users table with proper RLS policies
Write a migration to add a comments table
Deploy an Edge Function that sends welcome emails
Show me the schema for all tables in my project
```

### 5.7 Stripe

**Setup:**
```bash
claude mcp add --transport http stripe https://mcp.stripe.com
# Then: /mcp -> Authenticate
```

**Key tools:** Customer management, subscription handling, payment intent creation/confirmation, invoice generation, refund processing, Stripe documentation search.

**Usage examples:**
```
Create a new customer with email user@example.com
List all failed payments in the last 7 days
Set up a subscription plan at $29/month
Search Stripe docs for webhook best practices
```

### 5.8 Sentry

**Setup:**
```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

**Usage examples:**
```
What are the most common errors in the last 24 hours?
Show me the stack trace for error ID abc123
Which deployment introduced these new errors?
```

---

## 6. Scope Management

### 6.1 Three Scopes

| Scope | Flag | Loads in | Shared? | Stored in |
|-------|------|----------|---------|-----------|
| **Local** | `--scope local` (default) | Current project only | No | `~/.claude.json` (under project path) |
| **Project** | `--scope project` | Current project only | Yes (via git) | `.mcp.json` in project root |
| **User** | `--scope user` | All projects | No | `~/.claude.json` (top-level) |

### 6.2 Precedence

Local > Project > User. If a server with the same name exists at multiple scopes, the more specific scope wins. Local also overrides Claude.ai connector entries.

### 6.3 When to Use Each

**Local scope** (default): Personal dev servers, experimental configs, servers with credentials you don't want in version control.

```bash
claude mcp add --transport http stripe https://mcp.stripe.com
# Stored in ~/.claude.json under your project path
```

**Project scope**: Team-shared servers. The `.mcp.json` file gets committed to version control.

```bash
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

Resulting `.mcp.json`:
```json
{
  "mcpServers": {
    "paypal": {
      "type": "http",
      "url": "https://mcp.paypal.com/mcp"
    }
  }
}
```

**User scope**: Personal utility servers you want everywhere (e.g., your note-taking system, personal GitHub).

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### 6.4 Team Sharing Patterns

1. Commit `.mcp.json` to the repo (project scope) for shared servers
2. Use env var expansion for machine-specific values: `${API_KEY}`, `${DB_HOST:-localhost}`
3. Each developer adds their own credentials via local scope or env vars
4. Claude Code prompts for approval before using project-scoped servers (security gate)
5. Reset approval choices: `claude mcp reset-project-choices`

### 6.5 Plugin-Provided MCP Servers

Plugins can bundle MCP servers in `.mcp.json` at the plugin root or inline in `plugin.json`:

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": { "DB_URL": "${DB_URL}" }
    }
  }
}
```

Plugin servers auto-connect at session startup and appear alongside manually configured servers.

---

## 7. Debugging MCP Connections

### 7.1 Built-in Diagnostics

```bash
# Check status of all servers
/mcp                    # Inside Claude Code

# List configured servers
claude mcp list

# Get details for a specific server
claude mcp get my-server
```

### 7.2 Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Connection closed" on Windows | `npx` can't be executed directly | Wrap with `cmd /c`: `-- cmd /c npx -y @some/package` |
| stdout corruption (stdio) | Server uses `console.log()` or `print()` | Switch to `console.error()` or `print(..., file=sys.stderr)` |
| Server appears "offline" | Startup timeout exceeded | Set `MCP_TIMEOUT=10000 claude` (10 seconds) |
| Output too large warning | Tool output exceeds 10K tokens | Set `MAX_MCP_OUTPUT_TOKENS=50000` |
| OAuth redirect fails | Browser callback port mismatch | Use `--callback-port` matching registered redirect URI |
| "spawn ENOENT" | `claude` or server binary not in PATH | Use full path: `which claude` or `which npx` |
| Tools not found | Tool Search active, poor server instructions | Improve the `instructions` field in server metadata |

### 7.3 Timeout Configuration

```bash
# Set MCP server startup timeout (milliseconds)
MCP_TIMEOUT=10000 claude

# Set max output tokens per tool call
MAX_MCP_OUTPUT_TOKENS=50000 claude
```

**Known issue:** The default request timeout is 60 seconds (`DEFAULT_REQUEST_TIMEOUT_MSEC = 60000`). Custom timeout values configured in settings may be silently ignored for HTTP/SSE connections (tracked in GitHub issues). The `MCP_TIMEOUT` env var affects startup only, not per-request timeouts.

### 7.4 Debugging Tools

- **MCP Inspector** (`npx @modelcontextprotocol/inspector`): Official debugging tool that launches a browser UI for testing local servers interactively
- **Server logs**: For stdio servers, check stderr output. For HTTP servers, check your server's standard logging
- **Claude Code verbose mode**: Run with `CLAUDE_DEBUG=1 claude` for additional connection diagnostics

### 7.5 Debugging Checklist

1. Is the server binary/command accessible? (`which npx`, `which uv`)
2. Are environment variables set? (`claude mcp get <name>` shows config)
3. Is stdout clean? (No non-JSON-RPC output on stdout for stdio servers)
4. Is the server responding within timeout? (Increase `MCP_TIMEOUT` if slow startup)
5. For OAuth: Is the callback port correct? Can your browser reach `localhost:PORT/callback`?
6. For remote servers: Is the URL correct? Is the server accepting your protocol version?

---

## 8. MCP Ecosystem

### 8.1 Official Resources

- **Specification & docs:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Official registry:** [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) -- centralized metadata repository, namespace-authenticated
- **Reference servers:** [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) -- educational examples in multiple languages
- **Claude Code MCP docs:** [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
- **Anthropic MCP registry API:** `https://api.anthropic.com/mcp-registry/v0/servers` -- programmatic access to the registry

### 8.2 Community Registries

| Registry | Description | Scale |
|----------|-------------|-------|
| [Smithery](https://smithery.ai) | Closest to "Docker Hub for MCP." Install locally or run hosted. | 7,000+ servers |
| [MCP.so](https://mcp.so) | Community-led directory | 19,000+ entries |
| [PulseMCP](https://pulsemcp.com) | Curated directory with reviews | Hundreds of servers |
| [mcp.directory](https://mcp.directory) | Another community index | Growing |
| [Docker MCP Catalog](https://hub.docker.com/mcp) | Docker-hosted MCP servers | New, growing |

### 8.3 Registry Architecture

The official registry at registry.modelcontextprotocol.io is designed for **programmatic consumption by sub-registries** (Smithery, PulseMCP, Docker Hub, Anthropic, GitHub, etc.), not for direct end-user browsing. Server names follow a reverse-DNS format tied to verified GitHub accounts or domains.

### 8.4 Notable Server Categories

- **Developer tools:** GitHub, GitLab, Linear, Jira, Sentry, Datadog
- **Databases:** PostgreSQL, MySQL, SQLite, Redis, MongoDB, Supabase
- **Design:** Figma, Canva
- **Communication:** Slack, Discord, Gmail, Telegram
- **Cloud:** AWS, Azure, GCP, Cloudflare, Vercel
- **Payments:** Stripe, PayPal
- **Documentation:** Context7, Notion, Confluence
- **Browser:** Playwright, Puppeteer, Browserbase
- **Search:** Brave Search, Exa, Tavily
- **Memory:** Knowledge graph, vector stores

### 8.5 Using Claude Code as an MCP Server

Claude Code can itself act as an MCP server for other applications:

```bash
claude mcp serve
```

Configure in Claude Desktop:
```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

### 8.6 Importing from Claude Desktop

If you already have MCP servers configured in Claude Desktop:

```bash
claude mcp add-from-claude-desktop
# Interactive dialog to select which servers to import
```

### 8.7 Claude.ai MCP Servers in Claude Code

MCP servers configured at [claude.ai/settings/connectors](https://claude.ai/settings/connectors) automatically appear in Claude Code when logged in with the same account. Disable with `ENABLE_CLAUDEAI_MCP_SERVERS=false`.

---

## 9. Best Practices Summary

1. **Start small:** 3 servers max. Five is the ceiling before token overhead hurts performance
2. **Use HTTP transport for remote servers, stdio for local** -- don't fight the defaults
3. **Never commit secrets:** Use env var expansion in `.mcp.json`, keep API keys in local scope or env vars
4. **Leverage Tool Search:** With many servers, tool search automatically saves context. Write good server `instructions` to help discovery
5. **Use read-only credentials for databases** -- Claude can write SQL, so limit blast radius
6. **Test with MCP Inspector** before deploying: `npx @modelcontextprotocol/inspector`
7. **Check the official registry first** before building custom servers -- someone likely already built what you need
8. **For team projects:** Use project scope (`.mcp.json`) for shared servers, local scope for personal credentials

---

## Sources

- [MCP Transports Specification](https://modelcontextprotocol.io/legacy/concepts/transports)
- [Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp)
- [Build an MCP Server (Official Tutorial)](https://modelcontextprotocol.io/docs/develop/build-server)
- [MCP Registry](https://registry.modelcontextprotocol.io)
- [modelcontextprotocol/servers (GitHub)](https://github.com/modelcontextprotocol/servers)
- [Context7 (GitHub)](https://github.com/upstash/context7)
- [Playwright MCP (GitHub)](https://github.com/microsoft/playwright-mcp)
- [Stripe MCP Documentation](https://docs.stripe.com/mcp)
- [MCP Tool Search Explained (Claude Code)](https://claudefa.st/blog/tools/mcp-extensions/mcp-tool-search)
- [Best MCP Registries (TrueFoundry)](https://www.truefoundry.com/blog/best-mcp-registries)
- [Smithery Registry](https://smithery.ai)
