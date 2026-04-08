---
name: harness-engineering
description: "Initialize a Harness Engineering framework in the current project. Use when user says 'harness', 'init harness', 'initialize framework', 'setup harness engineering', '/harness', or wants to set up a Plan-Build-Verify development workflow with specialized agents (planner, generator, evaluator). Creates AGENTS.md (Codex), CLAUDE.md (Claude), agent definitions, command templates, hooks, and documentation structure for autonomous AI-driven development."
---

# Harness Engineering Framework

One-click initialization of a complete Harness Engineering framework in any project directory.

Based on insights from OpenAI (Codex), Anthropic (3-agent GAN architecture), and LangChain (self-verify loops), this skill sets up:

- **3-agent architecture**: Planner (spec), Generator (build), Evaluator (test)
- **Codex + Claude entry points**: `AGENTS.md` and `CLAUDE.md`
- **Sprint contracts**: Machine-verifiable "done" criteria before coding
- **Dual hook runtime**: Claude hooks (`.claude`) + Codex hooks (`.codex`)
- **Slash commands**: `/plan`, `/build`, `/qa`, `/sprint`
- **Golden principles**: 10 non-negotiable rules enforced across all agents

## When to Use

- Starting a new project and want structured AI-assisted development
- Want to set up Plan-Build-Verify-Fix workflow in current project
- User says "harness", "init harness", "setup framework", or similar

## Initialization Process

### Step 1: Gather Project Info

Before generating files, ask the user:

1. **Project name** (or detect from current directory name)
2. **Tech stack** (optional, e.g. "React + Node.js", "Python FastAPI", "Go microservice")
3. **Project type** (web app, API service, CLI tool, library, etc.)

If the user provides a description with `/harness <description>`, extract the info from context.

### Step 2: Generate Framework Files

Execute the scaffold script:

```bash
python3 {{SKILL_PATH}}/scripts/scaffold.py --project-name "<PROJECT_NAME>" --tech-stack "<TECH_STACK>" --project-type "<PROJECT_TYPE>" --target-dir "<CURRENT_PROJECT_DIR>"
```

This generates the following structure in the current project:

```
<project>/
  AGENTS.md                        # Codex guide / entrypoint
  CLAUDE.md                        # Project map (<80 lines)
  .codex/
    config.toml                    # Enable Codex hooks
    hooks.json                     # Codex hook registry
    hooks/
      loop-detector.py             # PreToolUse loop guard
      pre-completion-check.py      # Stop checklist reminder
      context-injector.py          # UserPromptSubmit context injection
  .claude/
    agents/
      planner.md                   # Spec creation agent
      generator.md                 # Implementation agent
      evaluator.md                 # Testing/grading agent
      doc-gardener.md              # Doc freshness agent
    commands/
      plan.md                      # /plan command
      build.md                     # /build command
      qa.md                        # /qa command
      sprint.md                    # /sprint command
    hooks/
      loop-detector.py             # File edit loop detection
      pre-completion-check.py      # Task completion checklist
      context-injector.py          # Session context middleware
  docs/
    architecture.md                # System design
    golden-principles.md           # Non-negotiable rules
    sprint-workflow.md             # Sprint process
    contracts/
      TEMPLATE.md                  # Sprint contract template
    specs/                         # (populated by planner)
    plans/                         # (populated by planner)
```

### Step 3: Configure Hooks

Hook configuration is auto-configured by `scaffold.py`:
- Claude hooks: merged into `.claude/settings.json` (or created)
- Codex hooks: merged into `.codex/hooks.json` (or created) and `.codex/config.toml` is scaffolded

### Step 4: Verify Installation

Confirm all files were created:

```bash
ls -la AGENTS.md CLAUDE.md .codex/ .codex/hooks/ .claude/agents/ .claude/commands/ .claude/hooks/ docs/
```

Run Codex hook self-check:

```bash
test -f .codex/config.toml && \
test -f .codex/hooks.json && \
test -f .codex/hooks/context-injector.py && \
test -f .codex/hooks/loop-detector.py && \
test -f .codex/hooks/pre-completion-check.py && \
python3 -m py_compile .codex/hooks/context-injector.py .codex/hooks/loop-detector.py .codex/hooks/pre-completion-check.py && \
echo "Codex hooks: OK"
```

Expected result:
- command exits with code `0`
- output includes `Codex hooks: OK`

Report to the user what was created and how to start using it.

## Usage After Initialization

| Command | Purpose |
|---------|---------|
| `/plan <description>` | Create a feature specification from 1-4 sentences |
| `/build` | Build the most recent spec using sprint workflow |
| `/qa` | Run evaluator against current code |
| `/sprint <description>` | Full Plan-Build-Verify cycle from scratch |

Codex users can run the same workflow by prompting:
- `plan <description>`
- `build <spec>`
- `qa <contract>`
- `sprint <description>`

Codex hook runtime is scaffolded in:
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/*.py`

Codex execution details (intent routing, output contracts, stop conditions) are defined in the generated `AGENTS.md`.

## Key Principles

The framework enforces these rules (see `docs/golden-principles.md` after install):

1. **Spec before code** - No implementation without a written spec
2. **Testable criteria** - Every feature has machine-verifiable acceptance criteria
3. **Self-verify first** - Generator must self-check before evaluator runs
4. **Loop awareness** - Editing same file 5+ times triggers a stop-and-reassess
5. **Contract-driven** - Sprint contracts define "done" before coding begins

## Architecture

For full details, read the generated `docs/architecture.md` after installation. Key flow:

```
User Prompt → Planner (spec) → Generator + Evaluator negotiate contract
→ Generator builds → Evaluator tests → Fix loop (max 3x) → Complete
```
