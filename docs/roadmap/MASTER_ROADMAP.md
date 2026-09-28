# Master Roadmap

> Complete 24-session curriculum map, derived from the course session decks (`sessions/phase1`, `Phase2`, `Phase3` in the course repo) and verified against the reference implementation repository.
> Compiled 2026-09-28. Anything not provable from source material is marked `UNKNOWN — REQUIRES SOURCE REVIEW`.

## Two framings of the same course

| Source | Framing |
| --- | --- |
| Course kickoff deck | **29 sessions / 80 hours / 4 phases** — Phase 1 S1–8, Phase 2 S9–16, Phase 3 S17–24, Phase 4 (Capstone) S25–29 |
| Decks actually present in the repo | **24 sessions + kickoff**, in 3 phase folders: `phase1` (S00–S08), `Phase2` (S09–S16), `Phase3` (S17–S24). There is **no Phase 4 folder and no S25–S29 deck**. |
| Reference implementation repo (`microservices-pro-platform`) | "Phase 1 = Sessions 1–8 complete; Phase 2 (S9–16) …" — aligns with the deck folders |

This training repo follows the **24-session structure** because that is the material that exists. Phase 4 / capstone work will be covered by the exam-prep track built in `docs/exam/` at the end.

## Session map

Exam-relevance legend: **ME** = Mid-Course Exam (Sessions 1–8, 15% of grade, held at the Session 9 anchor day) · **Cap** = Capstone project (35%) · **L** = lab grade (40%).

| # | Phase | Topic | Key concepts | Technologies | Hands-on | Lab | Depends on | Exam |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | — | Program Kickoff | Assessment model, 7-step session loop, platform port map, continuous capstone | — | No | — | — | Reference |
| 01 | 1 | Architecture & Spring Cloud (Service Discovery · Centralized Config · DDD) | Monolith vs microservices, bounded contexts, Eureka registration/lookup, Config Server, 12-Factor Factor III | Eureka Server/Client, Spring Cloud Config (native profile), Product Service, Actuator | Yes | **Lab 1** (doc) | — | **ME** |
| 02 | 1 | API Gateway Routing | Spring Cloud Gateway, WebFlux, Path predicate, `lb://` URI, GlobalFilter, response headers | Spring Cloud Gateway, Eureka client, LoggingFilter | Yes | **Lab 2A** (doc) | S1 | **ME** |
| 03 | 1 | Gateway Security | JWT validation (not issuance), Bearer extraction, whitelist routes, Redis token-bucket rate limiting | jjwt 0.11.5, Redis 7, `RequestRateLimiter`, `tools/jwt-generator` | Yes | **Lab 2B** (doc) + `session-03-jwt-testing` companion | S2 | **ME** |
| 04 | 1 | Resilience | Circuit Breaker states, Retry with exponential backoff, fallback methods, actuator CB endpoints | Resilience4j `spring-boot3`, `spring-boot-starter-aop`, order-service (+payment-service) | Yes | **Lab 3A** (doc) | S1 (S3 context) | **ME** |
| 05 | 1 | Resilience Advanced (Configuration Management in roadmap* ) | Bulkhead (semaphore), TimeLimiter, annotation stacking order `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry`, `CompletableFuture` | Resilience4j annotations, async controller | Yes | **Lab 3B** (doc) | S4 | **ME** |
| 06 | 1 | Service Communication | OpenFeign declarative clients, ErrorDecoder translation, JWT propagation, sync pre-check, inventory-service (8084) | OpenFeign, Inventory Service, Eureka, `RequestContextHolder` | Yes | **Lab 4A** (doc) | S1/S4/S5 | **ME** |
| 07 | 1 | Event Driven Architecture | Kafka topics, choreography saga (Order→Inventory→Payment), compensation, consumer groups, idempotent release | Spring Kafka, Kafka + Zookeeper (Confluent 7.6.1), domain events ×8 | Yes | **Lab 5A** (doc) | S6 | **ME** |
| 08 | 1 | Caching + Architecture Clinic #1 | `@Cacheable`/`@CacheEvict`, cache-aside, TTL, stale-list trap; critique of every Phase-1 decision; Technical Debt Register | Redis cache, Spring Cache abstraction | Yes | **Lab 6A** (doc) + **Clinic #1** (discussion) | S7 (JPA homework done) | **ME** |
| 09 | 2 | Docker Containerization | Multi-stage Dockerfiles, non-root user, HEALTHCHECK, compose networks, containerizing the whole platform | Docker, Docker Compose, `maven:3.9-eclipse-temurin-21` → `eclipse-temurin:21-jre-jammy` | Yes | **Lab 8A** (slide-only) | S1–S8 | Mid-exam anchor day |
| 10 | 2 | Testing Essentials + Unit & Integration Testing | JUnit 5, Mockito, parameterized tests, Testcontainers (real Postgres), test pyramid | Testcontainers 1.19.8, JUnit 5, Mockito, Spring Boot Test | Yes | **Lab 9A** (slide-only) | S9 | Cap |
| 11 | 2 | Testing: Contract & Chaos | Consumer-driven contracts (Pact), provider verification, WireMock stubbing/fault injection | Pact JVM 4.6.7, WireMock (spring-cloud-contract-wiremock) | Yes | **Lab 9B** (slide-only) | S10 | Cap |
| 12 | 2 | Saga Orchestration | Orchestrator vs choreography, command/result events, SagaState, compensation from the orchestrator, Kafka DLQ | Spring Kafka (commands: ProcessPayment, ReserveInventory, ReleaseInventory) | Yes | **Lab 10A** (slide-only) | S7 | Cap |
| 13 | 2 | CI/CD Pipelines with GitHub Actions | Workflow anatomy, JDK matrix, per-service test pipelines, build artifacts, triggers; notification-service (8085) | GitHub Actions, notification-service, `@RetryableTopic` (retry topics + DLT) | Yes | **Lab 11A** (slide-only) | S9–S12 | Cap |
| 14 | 2 | GitOps & Deployments | GitOps principles, ArgoCD Application manifests, declarative deploy, drift detection | ArgoCD (manifests only), k8s manifests | Yes | **Lab 11B** (slide-only) | S13 | Cap |
| 15 | 2 | Kubernetes Core | Pods, Deployments, Services, ConfigMaps/Secrets, probes, rollout; deploying the platform | Kubernetes (Docker Desktop / minikube), kubectl | Yes | **Lab 12A** (slide-only) | S9 | Cap |
| 16 | 2 | Kubernetes Advanced | HPA autoscaling, Helm chart authoring (templates, values, serviceaccount, RBAC), resource limits | Helm (chart apiVersion v2), HPA | Yes | **Lab 12B** (slide-only) | S15 | Cap |
| 17 | 3 | Observability Deep Dive | Metrics (Micrometer/Prometheus), distributed tracing (spans, Zipkin), structured JSON logging, Grafana dashboards | Micrometer Tracing (Brave), Prometheus v2.51.0, Zipkin 3, Grafana 10.4.2, logstash-logback-encoder 7.4 | Yes | **Lab 13** (slide-only) | S15 | Cap |
| 18 | 3 | CQRS Pattern | Command/query separation, read models/projections, domain events, cache eviction listeners | Spring Data projections, Keycloak arrives in this stage too | Yes | **Lab 14** (slide-only) | S8 | Cap |
| 19 | 3 | Security Part 1: Keycloak & OAuth2 | Identity provider, realms/clients/users, authorization-code flow, token issuance; Keycloak 24 | Keycloak 24.0.4 (realm export JSON) | Yes | **Lab 15** (slide-only) | S3 | Cap |
| 20 | 3 | Security Part 2: Client Credentials, Resource Server, RBAC | OAuth2 resource server in the gateway, retiring JwtAuthFilter/JwtUtil, service-to-service tokens, roles from JWT | `spring-boot-starter-oauth2-resource-server`, Keycloak | Yes | **Lab 16** (slide-only) | S19 | Cap |
| 21 | 3 | Service Mesh & mTLS: Istio | Sidecars, VirtualService, DestinationRule, PeerAuthentication (mTLS STRICT), traffic management over K8s | Istio, istioctl, k8s manifests | Yes | **Lab 17** (slide-only) | S15/S20 | Cap |
| 22 | 3 | Advanced Patterns: Outbox, Idempotency & API Versioning | Transactional outbox (polling publisher vs CDC), idempotency keys, dual-write problem, API versioning debt | JPA outbox table, `@Scheduled` publisher, idempotency records | Yes | **Lab 18** (doc) | S7/S8 | Cap |
| 23 | 3 | Performance & Load Testing | k6 smoke/load/stress scenarios, thresholds (p95/p99), correlating saturation with Bulkhead/CB, Zipkin traces | k6, actuator metrics, Zipkin | Yes | **Lab 19** (doc) | S5/S17/S20 | Cap |
| 24 | 3 | Architecture Clinic #2 + Phase 3 Wrap-Up | Review every decision since S1; Technical Debt Register closure; Phase 4 capstone preview | — (discussion) | No code | Clinic (discussion) | S8 | Cap |

\* The course `COURSE-ROADMAP.md` lists Session 05 as "Configuration Management" and Session 08 as "Phase Review", but the actual decks are `Session_05_Resilience_Advanced.pdf` and `Session_08_Caching_ArchClinic1.pdf`, and the reference repo maps S5→Lab 3B (Bulkhead/TimeLimiter) and S8→Redis caching + Clinic #1. **The decks and reference repo win**; the roadmap doc is stale. See `REFERENCE_DOCS_DIGEST.md` §7.

## Dependency graph (session → session)

```
S01 ─┬─▶ S02 ─▶ S03 ────────────────▶ S19 ─▶ S20 ─┐
     │                                              ├─▶ S23
     ├─▶ S04 ─▶ S05 ─▶ S06 ─▶ S07 ─▶ S08 ─┐        │
     │                          │          │        │
     │                          ├─▶ S12    ├─▶ S18 ─┘
     │                          │          │
     │                          └─▶ S22 ◀──┘   (outbox/idempotency close S8 clinic debt)
     │
     ├─▶ S09 ─▶ S10 ─▶ S11
     │     └─▶ S15 ─▶ S16 ─▶ S17
     │              └─▶ S21
     └─▶ S13 ─▶ S14
```

## Official lab documents (11)

| Lab doc | Session | Part | Graded |
| --- | --- | --- | --- |
| `session-01-lab-01.md` | 01 | Lab 1 | Yes |
| `session-02-lab-02.md` | 02 | Lab 2A | Yes |
| `session-03-lab-2b.md` | 03 | Lab 2B | Yes |
| `session-03-jwt-testing.md` | 03 | companion | No (testing guide for the jwt-generator tool) |
| `session-04-lab-3a.md` | 04 | Lab 3A | Yes |
| `session-05-lab-3b.md` | 05 | Lab 3B | Yes |
| `session-06-lab-4a.md` | 06 | Lab 4A | Yes |
| `session-07-lab-5a.md` | 07 | Lab 5A | Yes |
| `session-08-lab-6a.md` | 08 | Lab 6A | Yes |
| `session-22-lab-18.md` | 22 | Lab 18 | Yes |
| `session-23-lab-19.md` | 23 | Lab 19 | Yes |

Sessions 9–21 have **lab slides in the decks but no lab documents** in either repository (`UNKNOWN — REQUIRES SOURCE REVIEW` why). Their implementations are reconstructed from the deck lab slides + the reference branch diffs (see `ARCHITECTURE_EVOLUTION.md`).

## Assessment model (source: kickoff deck + `grading-rubric.md`)

| Component | Weight | Detail |
| --- | --- | --- |
| Daily Quizzes | 10% | 8 questions, end of every session, immediate feedback |
| Lab Grades | 40% | Feature 70% + Unit Tests 20% + Code Quality 10% (labs 18/19 on the branch state a different split — see digest §7) |
| Mid-Course Exam | 15% | Session 9 anchor day, 2h practical coding, covers Sessions 1–8 |
| Capstone | 35% | Team 70% + Individual 30% (Phases 4 / S25–29 per kickoff) |

Grade bands: Distinction 90–100 · Pass with Merit 75–89 · Pass 60–74 · Retake < 60.

Commit convention (enforced): `session-NN: short-description-of-what-was-done`. "No commit = no grade."

## Where the detailed material lives

| Need | File |
| --- | --- |
| Per-session study notes (17 sections each) | `docs/lectures/phase-{1,2,3}/session-XX.md` |
| Stage-by-stage architecture + git evidence | `docs/roadmap/ARCHITECTURE_EVOLUTION.md` |
| Official lab docs digested | `docs/roadmap/REFERENCE_DOCS_DIGEST.md` |
| Session → lab → deliverable mapping | `docs/roadmap/SESSION_TO_LAB_MAP.md` |
| Tooling inventory + install instructions | `docs/roadmap/PREREQUISITES.md` |
| Version matrix per technology | `docs/roadmap/TECHNOLOGY_MATRIX.md` |
| Skill progression tracker | `docs/roadmap/KNOWLEDGE_TRACKER.md` |
| Exam/capstone track | `docs/roadmap/EXAM_PREPARATION_ROADMAP.md` |
