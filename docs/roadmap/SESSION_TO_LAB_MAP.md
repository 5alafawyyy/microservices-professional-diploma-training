# Session → Lab Map

> Purpose: decide, for every session, what kind of work it contains. The course does **not** use a 1:1 "Session N = Lab N" scheme (Lab 18 lives in Session 22, Lab 19 in Session 23; Sessions 9–21 have slide-only labs).
> Sources: session decks, the 11 official lab documents, trainer checklists, and the reference repository's stage branches. Uncertainties marked `UNKNOWN — REQUIRES SOURCE REVIEW`.

## Categories

| Category | Meaning | Graded? |
| --- | --- | --- |
| **Lecture** | Conceptual teaching only, no code | No |
| **Demonstration** | Instructor implements live; trainee follows | No |
| **Exercise** | Guided implementation by the trainee | Sometimes |
| **Lab** | Trainee implements independently against acceptance criteria | Yes (40%) |
| **Homework** | Independent extension after the session | Recommended; feeds later sessions |
| **Architecture clinic** | Design critique discussion, no code | No (but feeds capstone) |

## Full mapping

| Session | Lecture | Demonstration / Live coding | Lab | Lab label | Official lab doc | Homework | Clinic | Modifies platform? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00 Kickoff | Yes | — | — | — | — | Pre-reading S1 | — | No |
| 01 Architecture & Spring Cloud | Yes | Eureka/Config/Product setup | **Yes** | Lab 1 | `session-01-lab-01.md` | JPA + Postgres for Product (becomes required by S8) | — | Yes — creates product-service, eureka-server, config-server |
| 02 API Gateway Routing | Yes | Gateway route + LoggingFilter | **Yes** | Lab 2A | `session-02-lab-02.md` | `/actuator/services` route; explore gateway actuator | — | Yes — creates api-gateway |
| 03 Gateway Security | Yes | JwtAuthFilter + rate limiter | **Yes** | Lab 2B | `session-03-lab-2b.md` | Externalize `PUBLIC_ROUTES`; test expired token | — | Yes — gateway security + Redis |
| 03 companion | — | JWT test walkthroughs | No (companion) | — | `session-03-jwt-testing.md` | — | — | No (tooling only) |
| 04 Resilience | Yes | CB + Retry live | **Yes** | Lab 3A | `session-04-lab-3a.md` | Gateway route for `/api/payments/**` | — | Yes — creates order-service, payment-service |
| 05 Resilience Advanced | Yes | Bulkhead + TimeLimiter live | **Yes** | Lab 3B | `session-05-lab-3b.md` | Actuator endpoints experiment, `max-wait-duration` experiment | — | Yes — order-service async stack |
| 06 Service Communication | Yes | Feign client live | **Yes** | Lab 4A | `session-06-lab-4a.md` | Gateway route `/api/inventory/**`; inventory persistence (debt) | — | Yes — creates inventory-service + Feign call |
| 07 Event Driven Architecture | Yes | Kafka saga live | **Yes** | Lab 5A | `session-07-lab-5a.md` | Notification service (deferred to S13); race after pre-check | — | Yes — Kafka + saga handlers |
| 08 Caching + Clinic #1 | Yes | Redis cache-aside live | **Yes** | Lab 6A | `session-08-lab-6a.md` | Cache inventory check (30s TTL) — decide if correct; close 1 debt item | **Yes** (Clinic #1, 50 min) | Yes — caching layer |
| 09 Docker | Yes | Multi-stage Dockerfile live | **Yes** | Lab 8A | — (slide-only) | Flyway/Liquibase migration (recommended) | — | Yes — containerization |
| 10 Testing Essentials | Yes | JUnit/Mockito/Testcontainers | **Yes** | Lab 9A | — (slide-only) | Extend integration suite | — | Tests only |
| 11 Contract & Chaos Testing | Yes | Pact + WireMock live | **Yes** | Lab 9B | — (slide-only) | — | — | Tests only |
| 12 Saga Orchestration | Yes | Orchestrator live | **Yes** | Lab 10A | — (slide-only) | — | — | Yes — orchestrated saga |
| 13 CI/CD | Yes | GitHub Actions live | **Yes** | Lab 11A | — (slide-only) | — | — | Yes — notification-service :8085 |
| 14 GitOps | Yes | ArgoCD manifests | **Yes** | Lab 11B | — (slide-only) | — | — | k8s manifests |
| 15 Kubernetes Core | Yes | kubectl deploy live | **Yes** | Lab 12A | — (slide-only) | — | — | Yes — K8s deployment |
| 16 Kubernetes Advanced | Yes | Helm + HPA live | **Yes** | Lab 12B | — (slide-only) | — | — | Yes — Helm chart, HPA |
| 17 Observability | Yes | Tracing + metrics live | **Yes** | Lab 13 | — (slide-only) | Add dashboards/alerts | — | Yes — observability stack |
| 18 CQRS | Yes | Command/query split live | **Yes** | Lab 14 | — (slide-only) | — | — | Yes — product-service CQRS |
| 19 Keycloak & OAuth2 | Yes | Keycloak setup live | **Yes** | Lab 15 | — (slide-only) | — | — | Yes — IdP container + realm |
| 20 OAuth2 Resource Server | Yes | Gateway security live | **Yes** | Lab 16 | — (slide-only) | — | — | Yes — retires JwtAuthFilter |
| 21 Istio & mTLS | Yes | Mesh config live | **Yes** | Lab 17 | — (slide-only) | — | — | Yes — Istio manifests |
| 22 Outbox & Idempotency | Yes | Outbox live (15 min) | **Yes** | Lab 18 | `session-22-lab-18.md` | Idempotency keys (part of lab) | — | Yes — outbox + idempotency |
| 23 Performance & Load Testing | Yes | k6 live | **Yes** | Lab 19 | `session-23-lab-19.md` | Findings write-up (part of lab) | — | k6 scripts only |
| 24 Clinic #2 + Wrap-Up | Yes | — | **No** | — | — | Capstone preparation | **Yes** (Clinic #2) | No |

## Lab naming discrepancies (reported, not resolved)

The decks, lab docs and reference branches use several numbering schemes:

1. **Doc labels vs session numbers:** the lab documents use short labels (Lab 1, 2A, 2B, 3A, 3B, 4A, 5A, 6A) that do not match session numbers. Labs 1–6A map to Sessions 1–8.
2. **Slide-only lab numbers:** the decks refer to labs as 8A (S9), 9A/9B (S10/S11), 10A (S12), 11A/11B (S13/S14), 12A/12B (S15/S16), 13 (S17), 14 (S18), 15 (S19), 16 (S20), 17 (S21). Some decks reportedly use different numbers for the same lab (e.g. "Lab 11A" vs "Lab 13", "Lab 19" vs "Lab 23") — `UNKNOWN — REQUIRES SOURCE REVIEW`, verify per-session when that lab is built.
3. **Branch names vs lab docs:** the reference branch for Labs 18/19 is `session-22-23-wip-reference`, while the labs are named `session-22-lab-18` and `session-23-lab-19` (session number, not lab number).
4. **Grading split differs** for Labs 18/19 ("Feature 70 + Code Quality 20 + Design Choice badge 10") vs the standard rubric (see digest §7).

**Rule adopted by this training repo:** name each lab directory `docs/labs/lab-NN/` using the **official lab document name when one exists**; otherwise use the deck's lab label (`lab-8a`, `lab-9a`, …). Never invent a number the sources do not use.

## Missing lab documents

Sessions 9–21 have no lab `.md` documents anywhere in either repository (`UNKNOWN — REQUIRES SOURCE REVIEW`). For those sessions the implementation target is reconstructed from:

1. the deck's lab slides (inside `sessions/Phase2|Phase3/*.pdf`),
2. the reference branch pair for that stage (`session-XX-wip-main` skeleton → `session-XX-wip-reference` solution),
3. the stage diff documented in `ARCHITECTURE_EVOLUTION.md`.

Their acceptance criteria in `PHASE_2_ROADMAP.md` / `PHASE_3_ROADMAP.md` are marked "(reconstructed)" until the lab is actually built, at which point they must be re-checked against the deck slides.
