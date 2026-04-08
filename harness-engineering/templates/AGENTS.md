# {{PROJECT_NAME}} Agent Guide

This project uses a Harness Engineering workflow. In Codex, treat this file as the operational contract for Plan -> Build -> Verify execution.

## Quick Start (Codex)

Use one of these intents:

1. `plan <feature description>`
2. `build <spec file or latest spec>`
3. `qa <contract file or latest contract>`
4. `sprint <feature description>` (full cycle)

## Codex Intent Router

When a user request matches one of the intents below, execute the corresponding flow.

| Intent | Trigger Examples | Required Actions | Required Outputs |
|---|---|---|---|
| `plan` | "plan login flow", "write spec for X" | Clarify ambiguity, inspect relevant code, author spec | `docs/specs/<feature>.md` |
| `build` | "build latest spec", "implement checkout spec" | Read spec + contract, implement scoped sprint, self-verify | Code changes + sprint report |
| `qa` | "qa latest contract", "evaluate feature X" | Read contract, test and grade each criterion | Structured QA report + score |
| `sprint` | "sprint build auth", "full cycle for X" | Run plan + contract + build + qa + fix loop | Spec + contract + implementation + score |

## Execution Contract

### Plan Contract

- Do not write implementation code.
- Spec must include:
  - Problem statement
  - User stories
  - Machine-verifiable acceptance criteria
  - Component boundaries
  - Data flow
  - Error handling
  - At least 3 edge cases
  - Dependencies
- Store to: `docs/specs/<feature-name>.md`

### Build Contract

- Read target spec from `docs/specs/`.
- Read target contract from `docs/contracts/`.
- If contract is missing, create it from `docs/contracts/TEMPLATE.md` before implementation.
- Implement only in-scope items from the contract.
- Self-verify before handing off:
  - Build/compile passes
  - Tests pass (existing + new)
  - Acceptance criteria checked one-by-one
  - No debug artifacts

### QA Contract

- Grade only against the contract criteria.
- Use status per criterion: `PASS`, `FAIL`, `PARTIAL`.
- Score formula:
  - `score = (pass + 0.5 * partial) / total * 100`
- Threshold: `80`.
- Include for every FAIL:
  - expected behavior
  - actual behavior
  - reproduction steps
  - suggested fix

### Sprint Contract

- Order is strict:
  1. Plan
  2. Contract
  3. Build
  4. QA
  5. Fix loop (if needed)
  6. Doc freshness
- Fix loop max iterations: `3`.
- If still below threshold after 3 iterations:
  - stop
  - summarize unresolved failures
  - ask for scope reduction or manual intervention

## Operational Rules

- Spec before code.
- Contract before build.
- One sprint at a time.
- No hidden scope expansion.
- Fail loudly with evidence.
- Prefer boring, reversible solutions.

## Codex Hook Runtime

- Codex hooks are defined in `.codex/hooks.json`.
- Hook scripts live in `.codex/hooks/`.
- Feature flag is enabled in `.codex/config.toml`.
- Hook goals:
  - PreToolUse loop detection
  - UserPromptSubmit context injection
  - Stop-time completion checklist reminder

## Project Layout

- `AGENTS.md`: Codex operational entrypoint
- `CLAUDE.md`: Claude entrypoint
- `.codex/config.toml`: Codex hook feature flag
- `.codex/hooks.json`: Codex hook registry
- `.codex/hooks/`: Codex hook scripts
- `.claude/agents/`: role definitions
- `.claude/commands/`: canonical command workflows
- `.claude/hooks/`: loop/context/check hooks
- `docs/specs/`: feature specs
- `docs/contracts/`: sprint contracts
- `docs/plans/`: planning artifacts

## Prompt Examples (Codex)

- `plan add passwordless login with email magic link`
- `build latest spec`
- `qa latest contract`
- `sprint add organization switcher in dashboard`

## Tech Stack

- Project: `{{PROJECT_NAME}}`
- Type: `{{PROJECT_TYPE}}`
- Stack: `{{TECH_STACK}}`
