# Architecture Decision Records

> One decision, one file, named `ADR-NNN-short-title.md`. Written **at the moment the decision is made**,
> not retroactively. A decision made in a lab becomes an ADR in the same commit.

ADRs are the answer bank for the capstone's "why did you choose X?" questions and for the Session 8 and
Session 24 Architecture Clinics.

## Template

```markdown
# ADR-001: <decision title>

- **Date:** YYYY-MM-DD
- **Session / Lab:** Session NN / Lab N
- **Status:** proposed | accepted | superseded by ADR-XXX

## Context
What problem forced a decision. Include the constraint that made it non-obvious
(course constraint, Historical State Rule, dev-vs-prod, tooling available).

## Options considered
1. <option> — <pros> / <cons>
2. <option> — <pros> / <cons>

## Decision
The option chosen, in one sentence.

## Consequences
- What becomes easier.
- What becomes harder / what we now owe (technical debt, revisit-in-session note).

## Evidence
Commit, test, or command output that demonstrates the decision works.
```

## Planned / expected ADRs (from the course material's known decision points)

| ADR | Decision point | Session |
|---|---|---|
| ADR-001 | In-memory store vs JPA for Product in Lab 1 (and when it flips to JPA) | 1 / 8 |
| ADR-002 | Gateway: `lb://` discovery routing vs hardcoded URIs | 2 |
| ADR-003 | JWT validated at the gateway vs in each service | 3 |
| ADR-004 | Resilience annotation ordering and where fallbacks live | 4–5 |
| ADR-005 | Synchronous Feign pre-check vs event-only flow in the saga | 6–7 |
| ADR-006 | Cache eviction strategy (individual key + list key) | 8 |
| ADR-007 | Choreography vs orchestration for the saga | 12 |
| ADR-008 | Outbox pattern vs dual write | 22 |
| ADR-009 | Keycloak port/realm discrepancy resolution (record the truth used) | 19–20 |

## Records

| ADR | Title | Status | Date |
|---|---|---|---|
| [ADR-001](ADR-001-in-memory-product-store.md) | In-memory Product store (ConcurrentHashMap behind JPA-shaped signatures) | accepted | 2026-09-28 |
