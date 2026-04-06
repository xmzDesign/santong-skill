---
name: harness-engineering
description: "Initialize a Harness Engineering framework in the current project. Use when user says 'harness', 'init harness', 'initialize framework', 'setup harness engineering', '/harness', or wants to set up a Plan-Build-Verify development workflow with specialized agents (planner, generator, evaluator). Creates CLAUDE.md, agent definitions, command templates, hooks, and documentation structure for autonomous AI-driven development."
---

# Harness Engineering Framework

One-click initialization of a complete Harness Engineering framework in any project directory.

Based on insights from OpenAI (Codex), Anthropic (3-agent GAN architecture), and LangChain (self-verify loops), this skill sets up:

- **3-agent architecture**: Planner (spec), Generator (build), Evaluator (test)
- **Sprint contracts**: Machine-verifiable "done" criteria before coding
- **Quality hooks**: Loop detection, pre-completion checklist, context injection
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
  CLAUDE.md                        # Project map (<80 lines)
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

After generating files, merge hook configuration into the project's `.claude/settings.json` (or create it):

```bash
python3 {{SKILL_PATH}}/scripts/merge_settings.py --target-dir "<CURRENT_PROJECT_DIR>"
```

This adds hook definitions without overwriting existing settings.

### Step 4: Verify Installation

Confirm all files were created:

```bash
ls -la CLAUDE.md .claude/agents/ .claude/commands/ .claude/hooks/ docs/
```

Report to the user what was created and how to start using it.

## Usage After Initialization

| Command | Purpose |
|---------|---------|
| `/plan <description>` | Create a feature specification from 1-4 sentences |
| `/build` | Build the most recent spec using sprint workflow |
| `/qa` | Run evaluator against current code |
| `/sprint <description>` | Full Plan-Build-Verify cycle from scratch |

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
