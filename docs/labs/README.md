# Labs

> One directory per lab. Directory naming: use the official lab document name when one exists;
> otherwise use the deck's own label (`lab-8a`, `lab-9a`, …). Never invent a number the sources do not use.
> Full mapping and acceptance criteria: `docs/roadmap/SESSION_TO_LAB_MAP.md`.

## Per-lab directory template

```
docs/labs/lab-NN/
├─ README.md            before-lab briefing (objective, why, prerequisites, current architecture block)
├─ acceptance.md        the acceptance criteria as a tickable list + exact evidence commands
├─ notes.md             my notes while building (free-form)
└─ evidence/            curl outputs, screenshots, log excerpts proving the criteria
```

## Index

| Dir | Session | Lab | Official doc | Status |
|---|---|---|---|---|
| `lab-01/` | 1 | Product Service + Eureka + Config | `session-01-lab-01.md` | **complete** — 7/7 PASS |
| `lab-02/` | 2 | API Gateway + Product route (2A) | `session-02-lab-02.md` | not started |
| `lab-03/` | 3 | JWT filter + rate limiting (2B) | `session-03-lab-2b.md` | not started |
| `lab-03-jwt-testing/` | 3 | jwt-generator companion (not graded) | `session-03-jwt-testing.md` | not started |
| `lab-04/` | 4 | Circuit breaker + retry (3A) | `session-04-lab-3a.md` | not started |
| `lab-05/` | 5 | Bulkhead + TimeLimiter (3B) | `session-05-lab-3b.md` | not started |
| `lab-06/` | 6 | Inventory + Feign (4A) | `session-06-lab-4a.md` | not started |
| `lab-07/` | 7 | Saga happy path + compensation (5A) | `session-07-lab-5a.md` | not started |
| `lab-08/` | 8 | Redis caching (6A) | `session-08-lab-6a.md` | not started |
| `lab-08a/` | 8 | Architecture Clinic #1 | deck only (no code) | not started |
| `lab-9a/` … `lab-16/` | 9–16 | Phase 2 labs | slide-only (reconstructed criteria in PHASE_2_ROADMAP) | not started |
| `lab-17/` … `lab-23/` | 17–23 | Phase 3 labs (`lab-18`, `lab-19` have official docs) | mixed | not started |
| `lab-24/` | 24 | Architecture Clinic #2 | deck only | not started |

Each directory is created **in the session that owns it** — not upfront (Historical State Rule applies to
docs as well).
