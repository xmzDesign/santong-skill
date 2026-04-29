# Testing, Security, Monitoring, Deployment, and Documentation Rules

Load this file for tests, security-sensitive code, authentication, authorization, monitoring, metrics, deployment, CI, configuration hardening, or project documentation.

## Security Rules

- Never hardcode passwords, tokens, API keys, signatures, credentials, private keys, or authorization values.
- Do not log raw secrets or authentication data.
- Use HTTPS or an approved secure channel for external calls.
- Use parameterized SQL and input validation to prevent injection.
- Store sensitive configuration in the approved encrypted configuration mechanism.
- Apply RBAC or the existing authorization mechanism for protected operations.
- Require extra care, audit, and rollback planning for sensitive or destructive operations.
- Do not rely on frontend-transmitted identity fields for authorization decisions.

## API Safety Rules

- Validate input at application boundaries.
- Do not expose raw system exception messages to external callers.
- Keep public error responses stable and safe.
- Use DTOs for external interfaces; do not expose entities or internal domain internals.
- Keep backward compatibility unless the task explicitly requests a breaking change.
- Public errors must not include internal class names, SQL, stack traces, or raw third-party errors.

## Testing Rules

- Add or update tests for core business logic changes.
- Use JUnit and Mockito conventions when adding unit tests.
- Mock external dependencies in unit tests.
- Use integration tests for critical persistence or cross-component flows when appropriate.
- Cover normal and exceptional paths for API changes.
- If tests cannot be run, state the smallest recommended validation command.

## Monitoring Rules

- Preserve existing Micrometer metric conventions.
- Keep business metrics stable and named consistently.
- Include useful business dimensions only when cardinality is controlled.
- Do not add high-cardinality labels such as raw IDs unless the existing monitoring design explicitly allows them.
- ERROR-level logs may trigger alerts, so avoid logging expected business validation failures as ERROR.
- Core links should expose latency, throughput, and error-rate visibility when the task changes operational behavior.

## Deployment and Configuration Rules

- Keep environment-specific values out of shared defaults unless safe.
- Do not commit production secrets or private deployment details.
- Maintain environment separation for dev, test, pre, and prod configurations.
- Preserve rollback compatibility for schema and API changes when possible.
- Production-impacting changes should include validation, rollout, or rollback notes.
- Schema changes require compatibility and rollback rehearsal notes before release.

## Documentation Rules

- Update documentation when public APIs, configuration keys, deployment steps, or operational behavior changes.
- Keep documentation concise and close to changed behavior.
- Prefer linking to authoritative specification files instead of duplicating long sections.
- Do not add noisy comments to code for obvious behavior.

## Quality Gate

Default verification:

```bash
mvn verify
```

Suggested repository scans:

```bash
rg -n "@Select\\(|@Update\\(|@Insert\\(|@Delete\\(" src/main/java
rg -n "logback|ordinal\\(\\)|select \\*|resultClass|\\$\\{" pom.xml src/main/java src/main/resources
rg -n "password|secret|token|authorization|privateKey|apiKey" src/main/java src/main/resources
```

## Review Checklist

Before finishing security/testing-sensitive changes, verify:

- No secrets are introduced.
- Logs are sanitized.
- Inputs are validated.
- Authorization and rate-limit impact are considered.
- Public errors are safe.
- Tests or validation steps are provided.
- Metrics and alerting impact are documented when operational behavior changes.
- Deployment and rollback notes exist for production-impacting changes.
