# Microservices Professional Diploma — Progressive Training Platform

> A learning repository built **lab by lab**, in the exact historical order the course teaches them.
> Every session produces a working, tested increment of one real platform: the **Enterprise E-Commerce Platform**.

## What this repository is

This is **not** a copy of a finished project. It is a reconstruction built from scratch, following the course material session by session, so that every technology arrives only when the course introduces it.

- **Learning repo:** `microservices-professional-diploma-training` (this repository — your work, your commits).
- **Course material (read-only):** the instructor's decks and lab documents.

## Historical State Rule

This repository is frozen at the completion boundary of Session 23 / Session 24. Code was implemented progressively based on the reference architecture.

## Course Structure

| Phase | Sessions | Focus |
|---|---|---|
| **Phase 1 — Foundation & Core Patterns** | 1–8 | Service Discovery, API Gateway, Circuit Breakers, Choreography Saga, Caching |
| **Phase 2 — Quality & Deployment** | 9–16 | Docker, Testcontainers, Contract Testing, Orchestration Saga, ArgoCD GitOps, K8s |
| **Phase 3 — Advanced & Enterprise** | 17–24 | Micrometer Metrics, Zipkin Tracing, CQRS, Keycloak OAuth2, Istio mTLS, K6 Load Testing |

## Repository Layout

```text
microservices-professional-diploma-training/
├── README.md
├── docs/
│   ├── roadmap/               # Training progression trackers
│   ├── lectures/              # Session notes & material summaries
│   ├── labs/                  # Frozen historical source lab documents (Labs 1-6A)
│   ├── architecture/          # ADRs and current state diagrams
│   ├── decisions/             # ADR markdown files
│   ├── testing/               # Test strategy notes
│   ├── exam/                  # Knowledge readiness and sync audits
│   ├── ENGINEERING_LOG.md     # Capstone evidence & troubleshooting log
│   └── COMMANDS.md            # Command reference guide
├── platform/
│   └── ecommerce-platform/    # Microservices source code
├── k6/                        # Load and performance test scripts
└── scripts/                   # Verification utilities
```

## How to Study

1. **Read** the session's lecture note in `docs/lectures/` *before* watching/reading the deck — the note mirrors the deck's structure and marks what must be memorized vs understood.
2. **Brief** — read the "before-lab briefing" in the lab directory (objective, why it matters, prerequisites, what the platform looks like right now).
3. **Build** the lab yourself. Use the lab document's tasks; use the reference branch only *after* your acceptance checks pass, to compare.
4. **Verify** — run `./scripts/verify-lab.sh <lab>` and complete the MANUAL items.
5. **Document** — update `docs/architecture/CURRENT_ARCHITECTURE.md`, add any ADR, log anything you debugged in `docs/ENGINEERING_LOG.md`, and move the topic forward in `docs/roadmap/KNOWLEDGE_TRACKER.md`.
6. **Commit** — one milestone commit per lab: `session-NN: <description>` (exact message from the lab doc). "No commit = no grade for that lab."

## How to Run the Platform

```bash
cd platform/ecommerce-platform
docker compose up -d                     # postgres, redis, kafka
docker compose ps                        # wait for healthy

cd infrastructure/config-server && mvn spring-boot:run     # :8888
cd infrastructure/eureka-server && mvn spring-boot:run     # :8761
cd services/product-service     && mvn spring-boot:run     # :8081
```

Full command reference for every tool (Maven, Docker, psql, redis-cli, kafka, curl, JWT, kubectl, k6):
**[`docs/COMMANDS.md`](docs/COMMANDS.md)**

## Git Identity and Security Rules

This repository is pushed **only** to the personal GitHub account. Before every push:

```bash
git remote -v                 # must point at the personal repo
git config --local user.name  # must be the personal identity
git config --local user.email # must be the personal email
ssh -T git@github-personal    # must greet the personal account
```

Identity is set **repository-local only** — global git config is never modified. Instructor repositories are read-only: never fork, push, or modify them.

## Current Status

| Metric | Status |
|---|---|
| **Course Phase** | Phase 3 — Observability & Advanced Patterns |
| **Current Session** | Session 24 completed (Architecture Wrap-Up) |
| **Platform State** | Implementation reconstructed through Lab 19 (Session 23) boundary. |
| **Overall Readiness** | **Sessions 1–24 curriculum implementation/review completed; independent knowledge validation and capstone readiness assessment remain.** |
| **Architecture** | [Current Architecture](docs/architecture/CURRENT_ARCHITECTURE.md) |
| **Readiness Audit** | [Knowledge Readiness Audit](docs/exam/KNOWLEDGE_READINESS_AUDIT.md) |

## Milestone Log

| Date | Event |
|---|---|
| 2026-09-28 | Reconnaissance complete: curriculum mapped, labs mapped, prerequisites audited, knowledge base created. |
| 2026-09-28 | Lab 1 complete: config-server + eureka-server + product-service built and verified end-to-end; pushed to GitHub. |
| 2026-09-28 | Lab 2A complete: api-gateway built and verified; port 8080 was free. Unit tests passed. |
| 2026-09-28 | Lab 2B complete: Redis added to compose; JwtAuthFilter and RequestRateLimiter added to api-gateway. |
| 2026-09-28 | Lab 3A complete: order-service and payment-service scaffolding added. Circuit Breaker & Retry patterns applied. |
| 2026-09-28 | Lab 3B complete: Bulkhead & TimeLimiter applied on order-service. Full Resilience4j stack verified. |
| 2026-09-28 | Lab 4A complete: inventory-service built. order-service uses OpenFeign to synchronously check stock. |
| 2026-09-28 | Lab 5A complete: Kafka added to compose. Choreography Saga implemented across Order, Inventory, Payment. |
| 2026-09-28 | Lab 6A complete: Product Service upgraded to Postgres and Redis caching. |
| 2026-09-28 | Lab 8A complete: All 7 services containerized using multi-stage Dockerfiles. |
| 2026-09-28 | Lab 9A complete: Implemented @WebMvcTest, @ParameterizedTest, and TestContainers integration tests for Product Service. |
| 2026-09-28 | Lab 9B complete: Pact consumer/provider contracts and WireMock for order-service. |
| 2026-09-28 | Lab 10A complete: Saga Orchestration with State Machine added for Order, Inventory, Payment services. |
| 2026-09-28 | Lab 11A complete: CI/CD GitHub Actions pipelines + Notification Service implementation for event tracking. |
| 2026-09-28 | Lab 11B complete: Kubernetes manifests and ArgoCD GitOps deployment for product-service. |
| 2026-09-28 | Lab 12A complete: Added K8s Secrets, Resource Requests/Limits, and Liveness/Readiness probes. |
| 2026-09-28 | Lab 12B complete: Added HPA, Helm Chart, and RBAC policies. |
| 2026-09-28 | Lab 13A complete: Integrated Zipkin, Prometheus, Grafana, and structured JSON logging. |
| 2026-09-28 | Lab 13B complete: Applied CQRS Command/Query split to product-service. |
| 2026-09-28 | Lab 15 complete: Keycloak container added with manual token flow verification. |
| 2026-09-28 | Lab 16 complete: API Gateway migrated to OAuth2 Resource Server. Client Credentials configured. |
| 2026-09-28 | Lab 17 complete: Istio Service Mesh enabled with strict mTLS and 80/20 traffic split. |
| 2026-09-28 | Lab 18 complete: Outbox pattern in order-service and Idempotency in payment-service. |
| 2026-09-28 | Lab 19 complete: k6 load testing scripts and bottleneck findings written. |
| 2026-09-28 | Session 24 complete: Architecture Clinic #2 (Wrap-Up) conducted and technical debt evaluated. |

## Note on Special Characters

If you encounter any special characters not understood by the system or editor, please ensure that your environment and text editors are fully configured to use UTF-8 encoding. This issue typically happens when files are read or written using cp1252 (Windows-1252) instead of UTF-8.
