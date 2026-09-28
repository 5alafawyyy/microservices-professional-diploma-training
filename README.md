# Microservices Professional Diploma — Progressive Training Platform

> A learning repository built **lab by lab**, in the exact historical order the course teaches them.
> Every session produces a working, tested increment of one real platform: the **Enterprise E-Commerce Platform**.

## What this repository is

This is **not** a copy of a finished project. It is a reconstruction built from scratch, following the course
material session by session, so that every technology arrives only when the course introduces it.

- **Learning repo:** `microservices-professional-diploma-training` (this repository — your work, your commits).
- **Course material (read-only):** the instructor's decks and lab documents.
- **Reference implementation (read-only):** the instructor's completed platform, used only to compare
  *after* a lab is finished — never to copy code into an unfinished lab.

The rule that governs everything here:

> **Historical State Rule** — the platform must be a faithful representation of the course at the moment of each
> session. No Kafka in a session that has not taught Kafka. No circuit breaker before Session 4.
> Each lab adds exactly what its session introduces.

## Course structure (24 sessions, 3 phases)

| Phase | Sessions | Focus |
|---|---|---|
| **Phase 1 — Foundation & Core Patterns** | 1–8 | Config + Eureka, API Gateway + Security, Resilience4j, OpenFeign + Saga + Kafka, Redis caching |
| **Phase 2 — Quality & Deployment** | 9–16 | Docker + Compose, Integration & Contract Testing, Saga orchestration, CI/CD, GitOps, Kubernetes |
| **Phase 3 — Advanced & Enterprise** | 17–24 | Observability, CQRS, Keycloak + OAuth2, Service Mesh + mTLS, Outbox/Idempotency, Load Testing, Architecture Clinic #2 |

Session titles, per-session topics, lab labels, dependencies, and acceptance criteria:
**[`docs/roadmap/MASTER_ROADMAP.md`](docs/roadmap/MASTER_ROADMAP.md)**

> Note on terminology: the original kickoff deck describes a 29-session programme with a 4-session capstone.
> The actual session decks and lab documents that exist cover **24 sessions** in three phases. This repository
> follows the 24-session structure; capstone preparation lives in [`docs/exam/`](docs/exam/).

## Repository layout

```
microservices-professional-diploma-training/
├─ README.md                       ← you are here (includes CURRENT STATUS)
├─ docs/
│  ├─ roadmap/                     MASTER_ROADMAP, PHASE_1/2/3_ROADMAP, SESSION_TO_LAB_MAP,
│  │                               PREREQUISITES, TECHNOLOGY_MATRIX, KNOWLEDGE_TRACKER,
│  │                               EXAM_PREPARATION_ROADMAP, ARCHITECTURE_EVOLUTION, REFERENCE_DOCS_DIGEST
│  ├─ lectures/phase-1/…phase-3/   17-section notes per session (concepts → interview questions)
│  ├─ labs/                        one directory per lab (objective, tasks, acceptance criteria, evidence)
│  ├─ architecture/                CURRENT_ARCHITECTURE.md  ← the canonical ASCII mental model
│  ├─ decisions/                   ADRs (one decision, one file)
│  ├─ testing/                     test strategy notes per phase
│  ├─ exam/                        quiz notes, traps, exam checklists
│  ├─ ENGINEERING_LOG.md           problems hit and how they were solved (capstone evidence)
│  └─ COMMANDS.md                  copy-paste command reference for every tool used
├─ platform/ecommerce-platform/     THE platform — grows one lab at a time
│  ├─ services/                    product, order, payment, inventory, notification
│  ├─ infrastructure/              eureka-server, config-server, api-gateway
│  ├─ tools/                       jwt-generator (Session 3, retired in Session 20)
│  └─ docker-compose.yml           postgres, redis, kafka, zookeeper
└─ scripts/
   ├─ verify-environment.sh        PASS/MISSING report for every tool the course needs
   ├─ verify-lab.sh <lab>          automated slice of a lab's acceptance criteria
   └─ reset-lab.sh                 clean-state helper between labs
```

## How to study

1. **Read** the session's lecture note in `docs/lectures/` *before* watching/reading the deck — the note
   mirrors the deck's structure and marks what must be memorized vs understood.
2. **Brief** — read the "before-lab briefing" in the lab directory (objective, why it matters, prerequisites,
   what the platform looks like right now).
3. **Build** the lab yourself. Use the lab document's tasks; use the reference branch only *after*
   your acceptance checks pass, to compare.
4. **Verify** — run `./scripts/verify-lab.sh <lab>` and complete the MANUAL items.
5. **Document** — update `docs/architecture/CURRENT_ARCHITECTURE.md`, add any ADR, log anything you
   debugged in `docs/ENGINEERING_LOG.md`, and move the topic forward in `docs/roadmap/KNOWLEDGE_TRACKER.md`.
6. **Commit** — one milestone commit per lab: `session-NN: <description>` (exact message from the lab doc).
   "No commit = no grade for that lab."

## How to run the platform

```bash
cd platform/ecommerce-platform
docker compose up -d                     # postgres (+ redis/kafka from later sessions)
docker compose ps                        # wait for healthy

cd infrastructure/config-server && mvn spring-boot:run     # :8888
cd infrastructure/eureka-server && mvn spring-boot:run     # :8761
cd services/product-service     && mvn spring-boot:run     # :8081
```

Full command reference for every tool (Maven, Docker, psql, redis-cli, kafka, curl, JWT, kubectl, k6):
**[`docs/COMMANDS.md`](docs/COMMANDS.md)**

## Git identity and security rules (non-negotiable)

This repository is pushed **only** to the personal GitHub account. Before every push:

```bash
git remote -v                 # must point at the personal repo
git config --local user.name  # must be the personal identity
git config --local user.email # must be the personal email
ssh -T git@github-personal    # must greet the personal account
```

If any check shows the work account (`ahmedemad1998` / `github-work` / `id_ed25519_work`): **stop**, do not
push, and fix the configuration with the user. Identity is set **repository-local only** — global git config
is never modified. Instructor repositories are read-only: never fork, push, or modify them.

## CURRENT STATUS

> Block updated at every lab milestone. Statuses: PASS / NOT VERIFIED / BLOCKED / NOT REVIEWED.

| Item | Value |
|---|---|
| **Current phase** | Phase 1 — Foundation & Core Patterns |
| **Current session** | Session 3 — **Lab 2B complete** (7/7 acceptance criteria PASS) |
| **Last lab completed** | Lab 2B — Gateway Security & Rate Limiting (Session 3) |
| **Next lab** | Lab 3A — Resilience (Circuit Breaker & Retry) (Session 4) |
| **Platform state** | 4 modules built and verified running: config-server :8888, eureka-server :8761, product-service :8081, api-gateway :8080. Redis and Postgres containers healthy. |
| **Architecture diagram** | [Milestone 3](docs/architecture/CURRENT_ARCHITECTURE.md) — secured entry point + rate limiting |
| **Environment** | PASS for Phase 1 tooling. Redis running via Docker. |
| **Blockers** | None. |

### Milestone log

| Date | Event |
|---|---|
| 2026-09-28 | Reconnaissance complete: curriculum mapped, labs mapped, prerequisites audited, knowledge base created. |
| 2026-09-28 | Lab 1 complete: config-server + eureka-server + product-service built and verified end-to-end; pushed to GitHub. |
| 2026-09-28 | Lab 2A complete: api-gateway built and verified; port 8080 was free. Unit tests passed. |
| 2026-09-28 | Lab 2B complete: Redis added to compose; JwtAuthFilter and RequestRateLimiter added to api-gateway. |
