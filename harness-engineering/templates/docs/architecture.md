# Architecture

System design for the Harness Engineering Framework.

---

## System Diagram

```
User
  |
  v
[/sprint <desc>] -----> [Planner Agent]
                              |
                              v
                        docs/specs/<name>.md
                              |
                              v
                    [Contract Negotiation]
                     /                  \
            [Generator]  <------->  [Evaluator]
                    |                      |
                    v                      v
              Source Code          Test Results + Grade
                    |                      |
                    +-------- fix --------+
                              |
                              v
                    [Score >= 80?] --No--> Fix Loop (max 3x)
                              |
                            Yes
                              v
                    [Doc Gardener] --> docs/ updated
                              |
                              v
                         Sprint Complete
```

## Agent Relationships

```
Planner ---> produces spec ---> Generator reads spec
Generator --> proposes contract --> Evaluator reviews
Evaluator --> grades output --> Generator fixes (if needed)
Generator --> completes sprint --> Doc Gardener audits
```

## Hook Injection Points

```
Claude Runtime:
  UserPromptSubmit --> .claude/hooks/context-injector.py
  PreToolUse(Edit|Write|MultiEdit) --> .claude/hooks/loop-detector.py
  PostToolUse(TaskUpdate) --> .claude/hooks/pre-completion-check.py

Codex Runtime:
  UserPromptSubmit --> .codex/hooks/context-injector.py
  PreToolUse(Edit|Write|MultiEdit) --> .codex/hooks/loop-detector.py
  Stop --> .codex/hooks/pre-completion-check.py
```

## Component Inventory

| Component | File | Role |
|-----------|------|------|
| Codex Guide | `AGENTS.md` | Codex entry point and workflow rules |
| Project Map | `CLAUDE.md` | Claude entry point, progressive disclosure hub |
| Planner Agent | `.claude/agents/planner.md` | Expands prompts into specs |
| Generator Agent | `.claude/agents/generator.md` | Implements features |
| Evaluator Agent | `.claude/agents/evaluator.md` | Tests and grades |
| Doc Gardener | `.claude/agents/doc-gardener.md` | Maintains doc freshness |
| /plan command | `.claude/commands/plan.md` | Triggers planner |
| /build command | `.claude/commands/build.md` | Triggers generator+evaluator |
| /qa command | `.claude/commands/qa.md` | Triggers standalone evaluation |
| /sprint command | `.claude/commands/sprint.md` | Triggers full cycle |
| Loop Detector | `.claude/hooks/loop-detector.py` | Prevents edit doom loops |
| Pre-Completion | `.claude/hooks/pre-completion-check.py` | Quality gate before done |
| Context Injector | `.claude/hooks/context-injector.py` | Session context awareness |
| Codex Hook Config | `.codex/hooks.json` | Codex hook registration |
| Codex Hook Scripts | `.codex/hooks/*.py` | Codex runtime hook handlers |
| Codex Hook Feature Flag | `.codex/config.toml` | Enables Codex hooks |
| Golden Principles | `docs/golden-principles.md` | Non-negotiable rules |
| Sprint Workflow | `docs/sprint-workflow.md` | Process documentation |
| Contract Template | `docs/contracts/TEMPLATE.md` | Sprint contract structure |

## MCP Tool Mapping

| MCP Tool | Used By | Purpose |
|----------|---------|---------|
| Playwright | Evaluator | E2E testing, browser automation |
| Chrome DevTools | Evaluator | Console errors, network, performance |
| zai-mcp-server | Evaluator | Visual verification of UI output |
| web_reader | Planner | Fetch external documentation |

## Sprint Lifecycle

```
State: IDLE
  |
  [plan/sprint intent from Claude slash command or Codex prompt]
  v
State: PLANNING  (Planner produces spec)
  |
  [spec approved]
  v
State: CONTRACTING  (Generator + Evaluator negotiate)
  |
  [contract agreed]
  v
State: BUILDING  (Generator implements)
  |
  [self-verify passed]
  v
State: VERIFYING  (Evaluator tests)
  |
  [score >= 80]
  v
State: COMPLETE  (docs updated, sprint log recorded)
  |
  [score < 80 & iterations < 3]
  v
State: FIXING  (Generator addresses failures)
  |
  [return to VERIFYING]
```

## Extension Guide

### Adding a New Agent

1. Create `.claude/agents/<name>.md` with frontmatter (name, description, tools)
2. Define the agent's role, constraints, and output format
3. Reference the agent in `CLAUDE.md` and/or `AGENTS.md` usage sections
4. Create a corresponding command in `.claude/commands/<name>.md` if needed

### Adding a New Hook

1. Create the hook script in `.claude/hooks/<name>.py` and/or `.codex/hooks/<name>.py`
2. Register it in `.claude/settings.json` (Claude) and/or `.codex/hooks.json` (Codex)
3. Output contract:
   - Claude: `{}` allow, `{"decision":"block","reason":"..."}` block, `{"systemMessage":"..."}` inject
   - Codex: prefer `hookSpecificOutput` payloads (e.g. `permissionDecision` / `additionalContext`); legacy `{"decision":"block","reason":"..."}` also accepted

### Adding a New Command

1. Create `.claude/commands/<name>.md` with frontmatter (description, argument-hint)
2. Define the workflow steps in the body
3. Reference existing agents via the Agent tool
