# BMAD Method -- Deep Research

*Compiled: 2026-04-09*

---

## 1. Overview

BMAD (Breakthrough Method for Agile AI-Driven Development) is an open-source framework
that transforms AI coding assistants into structured virtual development teams. Created by
Steve Kaplan (GitHub: bmadcode), it provides specialized agent personas, deterministic
workflows, and document management patterns to make AI-assisted development repeatable and
production-grade.

The core thesis: instead of treating an AI assistant as a single generalist, assign it
distinct expert roles (PM, Architect, Developer, etc.) with scoped responsibilities,
constrained context, and explicit handoff points. Each role produces artifacts that feed
the next, mirroring a real agile team.

**Repo:** [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
**Docs:** [docs.bmad-method.org](https://docs.bmad-method.org/)
**Claude Port:** [24601/BMAD-AT-CLAUDE](https://github.com/24601/BMAD-AT-CLAUDE)
**npm:** `bmad-method` (v6.x as of April 2026)

---

## 2. The Four Phases

BMAD follows a waterfall-with-gates model where each phase produces documents that become
context for subsequent phases:

```
Analysis --> Planning --> Solutioning --> Implementation
```

1. **Analysis** -- Business Analyst (Mary) captures the problem domain, market research,
   competitive intelligence, constraints. Output: Project Brief.
2. **Planning** -- Product Manager (John) transforms the brief into a PRD with user
   stories, acceptance criteria, and prioritization. Output: PRD document.
3. **Solutioning** -- Architect (Winston) designs the technical architecture, data models,
   API contracts, deployment topology. Output: Architecture document, tech stack decisions.
4. **Implementation** -- Scrum Master (Bob) shards work into stories, Developer (Amelia)
   implements them, QA (Quinn) validates.

The system enforces mandatory checkpoint gates between phases -- you cannot skip from
Analysis to Implementation without completing Planning and Solutioning artifacts.

---

## 3. Agent Personas (The Full Roster)

BMAD ships with 12+ specialized agents in the BMM (BMad Method Module). Each is defined
as an `.agent.yaml` file that compiles into a runtime `.md` file with embedded XML
activation blocks.

### Core BMM Agents

| Agent | Name | Role | Personality |
|-------|------|------|-------------|
| Analyst | Mary | Business analysis, market research, competitive intelligence | Strategic treasure hunter; thrilled by clues and patterns. Uses Porter's Five Forces, SWOT, root cause analysis. |
| Product Manager | John | PRD creation, requirements elicitation, user stories | Relentless "WHY" questioner. Refuses to let vague requirements through. |
| Architect | Winston | System architecture, tech stack, scalability design | Holistic systems thinker. Bridges frontend/backend/infra. Pragmatic technology selection. |
| Developer | Amelia | Story implementation, strict test coverage | Ultra-succinct. Speaks in file paths and acceptance criteria IDs. No fluff, all precision. |
| Scrum Master | Bob | Sprint planning, story preparation, backlog management | Certified Scrum Master with deep technical background. Crisp, checklist-driven. |
| UX Designer | Sally | User research, interaction design, wireframes | 7+ years experience. Expert in user research and AI-assisted design tools. |
| QA Engineer | Quinn | Test automation, quality validation, regression | Systematic tester. Reviews stories, designs test cases, assesses non-functional requirements. |
| Technical Writer | Paige | Documentation, API docs, user guides | Clear technical communication. |
| Quick-Flow Solo Dev | Barry | Rapid prototyping, solo full-stack development | Streamlined workflow for smaller projects that don't need the full team. |

### Meta-Agents

| Agent | Role |
|-------|------|
| BMad Master | Orchestrator agent that coordinates multi-agent workflows and routing. |
| BMad Builder (BMB) | Creates custom agents -- users can define new `.agent.yaml` files for domain-specific "digital employees." |
| Party Mode Facilitator | Multi-agent discussion facilitator for brainstorming sessions. |

### Expansion Pack Agents (Examples)

The architecture expansion pack adds: Alex (Infrastructure Analyst), Morgan (Cloud
Architect), Taylor (Cost Optimizer), Jordan (Security Reviewer), Casey (Data Architect),
River (Integration Architect), Sam (Platform Engineer).

---

## 4. Agent-as-Code: YAML Definition Format

Agents are defined declaratively in `.agent.yaml` files and compiled into executable
Markdown via a build pipeline. Here is the schema structure:

```yaml
agent:
  metadata:
    name: "amelia"
    display_name: "Amelia - Developer"
    module: "bmm"           # which module owns this agent
    version: "6.0.0"
    hasSidecar: true         # companion directory at _bmad/{module}/{agent-name}/

  persona:
    role: "Senior Software Engineer"
    identity: "Amelia"
    style: "Ultra-succinct, speaks in file paths and acceptance criteria IDs"
    principles:
      - "Never implement without an approved story"
      - "Test coverage is non-negotiable"
      - "Follow architecture decisions exactly"

  critical_actions:
    - "Verify story approval status before coding"
    - "Run all tests before marking complete"

  menu:
    - trigger: "impl"
      name: "Implement Story"
      handler: "workflow"
      workflow: "implement-story"
    - trigger: "review"
      name: "Code Review"
      handler: "task"
      task: "code-review"

  prompts:
    - id: "story-check"
      description: "Verify story is approved"
      content: "Check the story file frontmatter for status: approved..."
```

### Compilation Pipeline

The build system (`npx bmad-method install`) transforms these YAML files through:

1. **Schema validation** -- ensures required fields are present
2. **Customization merging** -- deep-merges user overrides from `.agent.customize.yaml`
3. **Template variable substitution** -- replaces `{{project_name}}`, `{{module}}` etc.
4. **Activation block assembly** -- loads reusable XML fragments from
   `src/utility/agent-components/`
5. **Final generation** -- produces `.md` files with embedded XML activation blocks

The compiled agent file contains the persona text plus an XML activation block that tells
the AI IDE how to load the agent, display its menu, and route commands to workflows.

---

## 5. Document Sharding

Document sharding is the practice of breaking large specification documents (PRDs,
architecture docs) into smaller, focused files that fit within AI context windows.

### Why It Matters

A 50-page PRD exceeds most context windows and causes hallucination, lost context, and
inconsistency. Sharding produces atomic pieces where each shard becomes a self-contained
unit the AI can fully digest.

### How It Works

The `bmad-shard-doc` tool (also available as `npx bmad-method shard`) parses a Markdown
document using `@kayvan/markdown-tree-parser`:

1. Level 2 headings (`##`) become individual shard files
2. Heading levels are adjusted (L2 becomes L1 in the shard)
3. An `index.md` is generated linking all shards
4. Output goes to a structured directory

### Example: Sharding a PRD

**Before** -- one large file:
```
docs/prd.md  (3000 lines)
```

**After** -- sharded:
```
docs/prd/
  index.md
  01-overview.md
  02-user-personas.md
  03-epic-authentication.md
  04-epic-dashboard.md
  05-epic-reporting.md
  06-non-functional-requirements.md
  07-technical-constraints.md
```

### Who Shards What

- **Product Manager (John)** produces the monolithic PRD
- **Scrum Master (Bob)** shards the PRD into epic-focused files
- **Architect (Winston)** produces the architecture doc
- **Scrum Master (Bob)** shards architecture into component-specific docs

The Scrum Master is the designated executor of the sharding mechanism, ensuring each
developer story gets precisely the context it needs.

---

## 6. Checkpoint Gates and Workflow Enforcement

### Workflow Step Architecture

BMAD workflows use a **step-file micro-architecture** for disciplined execution:

```
_bmad/bmm/workflows/create-prd/
  workflow.yaml          # workflow config, metadata, options
  steps-c/               # "Create" mode steps
    01-gather-inputs.md
    02-define-personas.md
    03-identify-epics.md
    ...
    12-final-review.md
  steps-e/               # "Edit" mode steps (different flow)
```

Key properties of this architecture:

- **Micro-file design** -- each step is a self-contained instruction file
- **Just-in-time loading** -- only the current step file is loaded into context
- **Sequential enforcement** -- steps must complete in order
- **State tracking** -- progress tracked via YAML frontmatter in the output document

### Template-Output Checkpoints

Within workflow steps, `<template-output>` tags create mandatory user interaction points.
The AI must present output in the specified format and wait for user approval before
proceeding. This is the primary mechanism for human-in-the-loop control.

```xml
<template-output>
Present the following to the user for review:

## Epic: {{epic_name}}
- Stories: {{story_count}}
- Estimated complexity: {{complexity}}

Ask: "Does this epic breakdown look correct? [y/n]"
</template-output>
```

### Phase Gates

The system enforces gates between the four phases:

1. **Analysis -> Planning gate**: Project Brief must be complete and approved
2. **Planning -> Solutioning gate**: PRD must be complete with all epics defined
3. **Solutioning -> Implementation gate**: Architecture document must be approved,
   stories must be sharded and assigned to sprints

Attempting to skip a gate (e.g., jumping to `/dev` without an approved architecture) is
blocked by the workflow system.

### YOLO Mode

At any `<template-output>` checkpoint, users can select `[y] YOLO` to auto-approve
remaining checkpoints in a workflow. This trades safety for speed on well-understood
projects.

---

## 7. Installation and File Structure

### Installation

```bash
# Interactive install (recommended)
npx bmad-method install

# Non-interactive with flags
npx bmad-method install --directory . --modules bmm --yes

# Prerelease builds
npx bmad-method@next install
```

**Prerequisites:** Node.js v20+, Python 3.10+, uv package manager.

The installer prompts for:
1. Where to write the `_bmad/` folder (current directory recommended)
2. Which AI IDE you use (Claude Code, Cursor, Windsurf, etc.)
3. Which modules to install (BMM is the flagship)

### Directory Tree After Installation

```
project-root/
  _bmad/                          # Core BMAD runtime
    core/                         # Required core module
      config.yaml                 # Core configuration
      workflows/                  # Core workflows
      tasks/                      # Core tasks
    bmm/                          # BMad Method Module
      config.yaml                 # Module configuration
      agents/                     # Compiled agent .md files
        analyst.md
        product-manager.md
        architect.md
        developer.md
        scrum-master.md
        ux-designer.md
        qa-engineer.md
        technical-writer.md
        quick-flow-dev.md
      workflows/                  # Workflow definitions
        create-prd/
          workflow.yaml
          steps-c/
          steps-e/
        create-architecture/
        create-stories/
        implement-story/
        ...                       # 34+ workflows total
      tasks/                      # Reusable task definitions
      templates/                  # Output templates
      module-help.csv             # Catalog of agents, workflows, tasks

  _bmad-output/                   # Generated artifacts
    prd.md
    architecture.md
    stories/
    ...

  .claude/                        # Claude Code integration (if selected)
    commands/                     # Slash commands
      bmad-help.md
      bmad-agent-analyst.md
      bmad-agent-pm.md
      bmad-agent-architect.md
      bmad-agent-dev.md
      bmad-agent-sm.md
      bmad-agent-qa.md
      bmad-create-prd.md
      bmad-create-architecture.md
      ...
    skills/                       # Skill definitions
    settings.json                 # Hook configurations

  .cursor/                        # Cursor integration (if selected)
    rules/
    ...
```

### The `_bmad-output/` Directory

All generated artifacts land here, organized by type:
- PRDs, architecture docs, user stories
- Sprint plans, test plans
- Any sharded document output

---

## 8. The Claude-Specific Port (BMAD-AT-CLAUDE)

[24601/BMAD-AT-CLAUDE](https://github.com/24601/BMAD-AT-CLAUDE) is an early community
port that adapts BMAD specifically for Claude Code, predating the official multi-IDE
installer.

### Directory Structure

```
bmad-claude-integration/    # Claude-specific integration layer
bmad-core/                  # Core BMad functionality
  user-guide.md             # Usage documentation
common/                     # Shared utilities
dist/                       # Pre-built compiled files
docs/
  core-architecture.md      # Architecture documentation
expansion-packs/            # Domain-specific agent packs
tools/                      # Utility tools (flattener, etc.)
```

### Key Differences from Main Repo

| Aspect | Main BMAD-METHOD | BMAD-AT-CLAUDE |
|--------|-----------------|----------------|
| IDE support | 20+ IDEs (Claude, Cursor, Windsurf, etc.) | Claude Code only |
| Installation | `npx bmad-method install` | Manual copy / `npm run install:bmad` |
| Agent activation | IDE-specific (slash commands, @mentions) | Claude slash commands |
| Subagent support | Yes (v6+) | Early subagent integration via PR #359 |
| Maintenance | Active (bmad-code-org) | Community maintained |
| Version | v6.x | Based on earlier v4-v5 patterns |

### BMAD-AT-CLAUDE Subagent Architecture

The Claude port introduced Claude Code subagent patterns where each BMAD skill can
decompose complex workflows into independent subtasks executed by parallel subagents, each
getting its own 200K token context window. Subagent behavior is configured in
`bmad/config.yaml`.

### The Flattener Tool

Both repos include a codebase flattener:
```bash
npx bmad-method flatten --input /path/source --output codebase.xml
```
This produces a single XML file of your codebase for upload to web-based AI interfaces
(Gemini, ChatGPT).

---

## 9. Slash Commands and IDE Integration

### Claude Code Commands

After installation, BMAD creates slash commands in `.claude/commands/`. All use the
`bmad-` prefix:

| Command | Function |
|---------|----------|
| `/bmad-help` | Context-aware guidance. Ask "what's next?" at any point and it tells you the next step. Accepts natural language: `/bmad-help I just finished the architecture` |
| `/bmad-agent-pm` or `/pm` | Activate the Product Manager (John) persona |
| `/bmad-agent-architect` or `/architect` | Activate the Architect (Winston) persona |
| `/bmad-agent-dev` or `/dev` | Activate the Developer (Amelia) persona |
| `/bmad-agent-sm` or `/sm` | Activate the Scrum Master (Bob) persona |
| `/bmad-agent-qa` or `/qa` | Activate the QA Engineer (Quinn) persona |
| `/bmad-agent-analyst` | Activate the Analyst (Mary) persona |
| `/bmad-create-prd` | Start the PRD creation workflow |
| `/bmad-create-architecture` | Start the architecture workflow |

### How Activation Works

Each slash command file is a small Markdown prompt that:
1. Points to the compiled agent `.md` file in `_bmad/bmm/agents/`
2. Instructs the AI to load the persona, adopt the communication style, and display the
   agent's menu
3. Loads project configuration from `_bmad/bmm/config.yaml`

Example slash command file (`.claude/commands/bmad-agent-dev.md`):
```markdown
Load and activate the developer agent.

Read the agent file at: _bmad/bmm/agents/developer.md
Follow all activation instructions in the XML block.
Load project config from: _bmad/bmm/config.yaml
```

### Known Compatibility Issues

Claude Code has had ongoing issues with BMAD command discovery:
- Claude Code only discovers commands at the root of `.claude/commands/`, not nested
  subdirectories -- nested commands like `.claude/commands/bmad/dev.md` are invisible
- After the December 2025 extension update, Claude Code changed to require a
  `commands.json` manifest file, breaking existing BMAD installations
- Workaround: flatten all commands to root level with `bmad-` prefix naming

### Cursor/Windsurf Differences

Other IDEs use `@` mentions instead of slash commands:
- Cursor: `@pm`, `@architect`, `@dev` (rules in `.cursor/rules/`)
- Windsurf: similar pattern in `.windsurf/rules/`

---

## 10. Integration with Claude Code Features

### CLAUDE.md

BMAD can add project-level instructions to `CLAUDE.md` that establish conventions:
- Reference to `_bmad/` as the agent/workflow directory
- Instruction to use `/bmad-help` for guidance
- Project-specific constraints (tech stack, coding standards)

### Skills

The official BMAD installer creates skill files in `.claude/skills/` that map to BMAD
workflows. The community package
[aj-geddes/claude-code-bmad-skills](https://github.com/aj-geddes/claude-code-bmad-skills)
provides a more complete skills integration with auto-detection, memory integration, and
additional slash commands.

### Hooks

BMAD Skills uses Claude Code hooks in `.claude/settings.json`:

- **Session Start hooks** -- load BMAD environment variables and project context when a
  new session begins
- **Pre-Tool hooks** -- validate and log tool usage before execution; can filter by tool
  name via `matcher` field
- **Post-Tool hooks** -- track workflow progress after tool completion

### Subagents

BMAD v6+ leverages Claude Code's subagent capability to run parallel workstreams:
- Each skill can decompose into independent subtasks
- Each subagent gets its own 200K context window
- Results are aggregated by the parent agent
- Configured in `bmad/config.yaml` with `subagent` settings

---

## 11. Real-World Usage and Results

### Positive Reports

- Steve Kaplan (creator): Built a complete SaaS architecture in 4 hours that would have
  cost $50K and taken months with a traditional team
- Multiple blog posts report the framework makes AI output "repeatable, readable, and
  useful" vs. ad-hoc prompting
- The structured approach prevents the common "vibe coding" failure mode where AI
  generates plausible but broken code
- As of April 2026, the GitHub repo has significant community traction with 2000+ issues
  filed

### Documented Challenges

| Challenge | Detail |
|-----------|--------|
| **Token costs** | ~31,667 tokens per workflow run in early versions; one user reported $847/month |
| **Learning curve** | 6-7 agent personas, YAML configs, CLI commands, workflow concepts |
| **Workflow rigidity** | Plan-everything-first approach feels inflexible for exploratory projects |
| **Agent reliability** | Reports of agents marking stories "complete" while features remain broken (e.g., 9-hour authentication saga) |
| **IDE compatibility** | Ongoing friction with Claude Code command discovery, manifest file changes |

### Who It's For

BMAD works best for:
- **Greenfield projects** with well-defined scope
- **Solo developers** who want structure without a team
- **Teams** standardizing their AI-assisted workflow
- **Enterprise contexts** requiring documentation trails

It's less suited for:
- Quick prototypes or exploratory hacking
- Projects where requirements are genuinely unknown
- Developers who prefer lightweight, ad-hoc AI usage

---

## 12. Comparison: BMAD vs. Other Approaches

| Aspect | BMAD | Ralph Loop | Plain Claude Code |
|--------|------|-----------|-------------------|
| Structure | High (12+ agents, 34+ workflows) | Minimal (bash loop + PRD) | None (ad-hoc) |
| Setup cost | 15-30 min install + learning curve | 5 min | 0 |
| Token efficiency | High per-run (~31K/workflow) | Low per-iteration, high total | Varies |
| Best for | Enterprise, greenfield, teams | Overnight batch work | Quick tasks, exploration |
| Context management | Document sharding | Fresh context per loop | Manual |
| Human-in-the-loop | Checkpoint gates | Post-loop review | Continuous |
| Agent switching | Explicit persona activation | Single agent | Single agent |

---

## 13. Key Takeaways for Untype

### Worth adopting
- **Document sharding concept** -- our `IMPLEMENTATION_PLAN.md` could benefit from being
  split into phase-specific files that get loaded as context only when relevant
- **Phase gates** -- enforcing "does it build?" before moving to next phase (we already
  do this via `swift build` verification)
- **Agent persona separation** -- useful mental model even without BMAD tooling; plan in
  one session, implement in another

### Not worth adopting (for us)
- **Full BMAD installation** -- overkill for a solo project with clear scope
- **12-agent roster** -- we only need 2-3 mental modes (plan, implement, verify)
- **YAML agent definitions** -- our `CLAUDE.md` + session logs already provide sufficient
  structure
- **Workflow step files** -- too rigid for our iterative approach

### Concepts to borrow informally
- Keep planning artifacts (PRD, architecture) as separate, focused documents
- Use explicit "checkpoint" moments: build verification after every change
- Clear session boundaries: plan and implement in separate Claude sessions
- State in filesystem, not in conversation history

---

## Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [BMAD Official Docs](https://docs.bmad-method.org/)
- [BMAD-AT-CLAUDE](https://github.com/24601/BMAD-AT-CLAUDE)
- [aj-geddes/claude-code-bmad-skills](https://github.com/aj-geddes/claude-code-bmad-skills)
- [DeepWiki: BMM Module](https://deepwiki.com/bmad-code-org/BMAD-METHOD/4-bmad-method-module-(bmm))
- [DeepWiki: Agent Architecture](https://deepwiki.com/bmad-code-org/BMAD-METHOD/7.1-cis-overview)
- [Steve Kaplan: How I Build AI Apps 10x Faster](https://stevekaplanai.medium.com/the-bmad-method-how-i-build-ai-apps-10x-faster-than-traditional-dev-teams-23fddf0ff56e)
- [DEV Community: BMAD Framework](https://dev.to/extinctsion/bmad-the-agile-framework-that-makes-ai-actually-predictable-5fe7)
- [Benny Cheung: Applied BMAD](https://bennycheung.github.io/bmad-reclaiming-control-in-ai-dev)
- [Reenbit: BMAD for Production-Ready Development](https://reenbit.com/the-bmad-method-how-structured-ai-agents-turn-vibe-coding-into-production-ready-software/)
- [BMad Code Official Site](https://bmadcodes.com/)
- [BMAD Install Guide](https://docs.bmad-method.org/how-to/install-bmad/)
- [npm: bmad-method](https://www.npmjs.com/package/bmad-method)
