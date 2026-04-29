# Core AI Coding Rules

Use this file for rules that apply to every Java backend task. Load topic-specific rule files only when the task touches that area.

## Always Do

- Read the current task `spec/contract` before coding.
- Make the smallest safe change that satisfies the request.
- Inspect existing code before introducing new patterns.
- Reuse existing utilities, converters, exception types, response wrappers, configs, and naming conventions.
- Preserve public API compatibility unless the task explicitly requests an API change.
- Keep changes within the correct DDD layer.
- Validate with the smallest relevant test, build, static check, or manual verification.
- Before code/config/SQL changes, define impact scope, rollback path, and acceptance criteria.

## Never Do

- Do not duplicate framework glue, utility classes, mappers, converters, or exception classes.
- Do not bypass domain services from application services when business rules already exist.
- Do not put infrastructure annotations or mapper access into domain models or domain services.
- Do not expose raw system exception messages to external callers.
- Do not log secrets, tokens, passwords, signatures, credentials, private keys, or authorization values.
- Do not serialize enums with `ordinal()`.
- Do not expand scope without evidence.
- Do not skip verification and directly deliver.

## Pre-Change Gate

Before any code, scaffold, config, or SQL change, explicitly confirm:

1. Current `spec/contract` and repository constraints are read.
2. Relevant Java rule slices are loaded from `.harness/docs/java/rules/`.
3. Public contract impact is known: Dubbo/HTTP/API, DTOs, enums, response wrappers, compatibility.
4. DDD layer placement is known: package responsibility, dependency direction, Service/Repository/Adapter/Converter location.
5. Logging and exception boundaries are known: TraceId/MDC, masking, error codes, safe external responses.
6. SQL location is known: MyBatis SQL belongs in XML Mapper, not Java annotations.
7. SQL semantics are checked: count, NULL, pagination, table aliases, correction scripts.
8. ORM mapping is checked: explicit fields, `resultMap`, parameter binding, update field range, `update_time`.
9. Scheduling is checked: scheduled tasks use XXL-Job, no ad-hoc scheduler.
10. Migration is checked: application migration is not required by default unless the task explicitly asks for schema changes.
11. Distributed impact is declared: every Java change states whether Distributed Java Gate is triggered.

## Technology Baseline

- JDK: `1.8`.
- Build: Maven, including multi-module projects.

## Forbidden Dependencies

- MUST NOT add `gson` as the business JSON entry.
- MUST NOT add a parallel handwritten `jackson` business serialization entry, except Spring Web's default message conversion chain.
- MUST NOT add `logback` dependency chains or APIs.

## Done Criteria

A Java task is complete only when:

- The implementation follows the correct layer boundaries.
- Public contracts are intentionally unchanged or explicitly updated with compatibility notes.
- Sensitive data is protected in logs, config, tests, and docs.
- Exceptions and responses follow project conventions.
- Java Gate and Distributed Java Gate are recorded in spec/contract/build/qa.
- Validation commands and results are recorded.

## Relationship With Local Contracts

- User instructions and repository-local rules take precedence when stricter.
- This rule set is the default floor; local rules may tighten but not loosen it without explicit project decision.
- Conflicts must be recorded in task `spec/contract` with the decision and effective scope.
