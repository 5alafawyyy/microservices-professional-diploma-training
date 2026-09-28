# Exam Preparation Roadmap

> Part of the reconnaissance deliverable set. Evidence base: course decks (`_references/microservices-professional-diploma/sessions/`), reference repository (`_references/microservices-pro-platform`), and the digests in `docs/roadmap/`.

## 1. What is actually assessed

| Component | Weight | Format (from kickoff deck) | Covers |
|---|---|---|---|
| Daily Quizzes | 10% | 8 questions, end of every session, 10 min, immediate feedback | That session only |
| Lab Grades | 40% | Feature 70% + Unit Tests 20% + Code Quality 10%, one lab per session | The session's lab |
| Mid-Course Exam | **15%** | 2 hours, practical coding, individual, supervised at the Offline Anchor Day | **Sessions 1–8** |
| Capstone Project | 35% | Team 70% + Individual Contribution 30% | Whole platform |

Grade bands: Distinction 90–100 · Merit 75–89 · Pass 60–74 · Retake < 60.

Two facts that shape all exam prep:

1. **The mid-course exam is practical coding, not multiple choice.** It is sitting at the Session 9 anchor day, supervised. Anecdotal course material ("Assessment Bank — 64 exam questions with explanations") exists for quizzes, but the exam itself is a code-writing exercise over Phase 1 material.
2. **The capstone is 35% of the grade and spans everything.** No separate capstone deck exists; per this repo's structure, capstone preparation lives in `docs/exam/` and the platform itself is the capstone deliverable.

## 2. Mid-Course Exam plan (Sessions 1–8)

### 2.1 Topic checklist (exam scope)

Everything in Phase 1 can appear. Prioritized by how likely it is to be a coding task:

**Very likely to be coded from scratch in the exam:**

- [ ] Eureka Server module: `@EnableEurekaServer`, port 8761, `application.yml`, registration verification in the dashboard.
- [ ] Config Server module: `@EnableConfigServer`, native profile + `classpath:/configs`, port 8888, `spring.config.import: optional:configserver:...` on the client.
- [ ] Product CRUD REST API: `Map<Long, Product>` (or JPA), `findAll` / `findById` → `Optional` / `save` (id assigned if missing) / `deleteById`, controller with 200/201/404 semantics.
- [ ] Gateway route in YAML: `lb://PRODUCT-SERVICE`, `Path` predicate, `StripPrefix=0`, `AddResponseHeader`.
- [ ] `GlobalFilter` + `Ordered`: log method/path/status, set `getOrder()`.
- [ ] JWT validation filter: whitelist public routes, 401 on missing/invalid, `X-User-Id` / `X-User-Role` headers.
- [ ] Rate limiter config: `RequestRateLimiter` + IP `KeyResolver` (`@Primary`), `replenishRate: 10`, `burstCapacity: 20`.
- [ ] Resilience4j stack on a method: `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry` with correct fallback signatures.
- [ ] YAML for each resilience module: CB (window 10, threshold 50, 5s open), Retry (3 attempts, 500ms, exponential ×2), Bulkhead (10 concurrent, 0ms wait), TimeLimiter (2s, cancel future).
- [ ] OpenFeign client: `@FeignClient(name = "INVENTORY-SERVICE", path = "...")`, `ErrorDecoder`, JWT propagation interceptor.
- [ ] Kafka producer/consumer: correct topic names, **5 distinct consumer group IDs**, event classes.
- [ ] Saga choreography handlers: OrderPlaced → reserved/failed → payment → confirmed/cancelled, compensation path.
- [ ] Redis caching annotations: `@Cacheable` (list + by-id), `@CacheEvict` (individual + `evictAllProductsCache()`).

**Likely as short-answer / whiteboard (anchor day includes whiteboard):**

- [ ] Monolith vs microservices trade-offs (independent deploy, selective scaling, operational cost, network latency).
- [ ] Bounded context rule: different context ⇒ different service; shared table ⇏ merge.
- [ ] What Eureka solves vs hardcoded IPs; self-preservation (DEV ONLY flag).
- [ ] Why config externalization = 12-Factor Factor III; what the `optional:` prefix does.
- [ ] Circuit breaker states (CLOSED → OPEN → HALF_OPEN) and their triggers/timings.
- [ ] Choreography vs orchestration trade-off.
- [ ] Cache-aside flow and why the list key must be evicted alongside individual keys.
- [ ] Why the gateway pom must not contain `spring-boot-starter-web`.

### 2.2 Memorization list (must be dictionary-accurate)

Ports: Gateway 8080 · Product 8081 · Order 8082 · Payment 8083 · Inventory 8084 · Notification 8085 · Eureka 8761 · Config 8888 · PostgreSQL 5432 · Kafka 9092 · Redis 6379 · Zipkin 9411.

Numbers: CB window 10 / threshold 50% / wait 5s · Retry 3 / 500ms / ×2 · Bulkhead 10 / 0ms · TimeLimiter 2s · rate limit replenish 10 / burst 20 · cache TTL 300000ms · outbox poll 1000ms · JWT dev secret `microservices-pro-course-dev-secret-key-2026-min-256-bits`.

Commit format: `session-NN: <short-description>` — the exact strings for Labs 1–8 are listed in `SESSION_TO_LAB_MAP.md`.

### 2.3 Practice cycle (before the anchor day)

| Weekend slot | Activity |
|---|---|
| 2 weeks before | Re-implement Lab 1 + Lab 2 from a blank folder, no reference. Time-box: 60 min. |
| 1.5 weeks before | Re-implement Lab 3A/3B resilience stack + all YAML numbers from memory. Verify with `/actuator/circuitbreakers`. |
| 1 week before | Re-implement Lab 4A Feign client + ErrorDecoder + JWT interceptor from memory. |
| 5 days before | Re-implement Lab 5A saga handlers + consumer-group table. Draw the message flow on paper. |
| 3 days before | Re-implement Lab 6A caching + the S08-Q04 eviction trap. |
| 2 days before | Full dry run: fresh clone of own repo, follow own `docs/COMMANDS.md`, stand the whole Phase-1 platform up and verify every acceptance criterion in `SESSION_TO_LAB_MAP.md`. |
| 1 day before | Read `docs/lectures/phase-1/*` section 12 ("What I must memorize") and 15/16 (session relationships). No new topics. |

### 2.4 Exam-day strategy (2 hours)

1. **Read all tasks first** (5 min). Identify which need infra (Eureka/Config/Kafka/Redis) and start those containers immediately so they warm up while you code.
2. **Code the service layer + unit tests before wiring infrastructure** — most marks are on the feature, and tests can pass with mocked dependencies even if a container is unhealthy.
3. **Verify acceptance criteria in order** — each lab's list is ordered from simplest to most complex; if time runs out, you keep the marks for the verified prefix.
4. **Commit exactly once per completed task** with the prescribed message. "No commit = no grade."

## 3. Capstone plan (35%)

Capstone = the platform in `platform/ecommerce-platform` as it exists at the end of Phase 3. Team component 70% / individual 30%.

- Individual contribution evidence = the engineering log (`docs/ENGINEERING_LOG.md`) plus per-lab commits with correct messages; the log distinguishes "I did" from "the team did".
- Team component = a coherent platform: all services, gateway security, resilience, saga, caching, containers, K8s manifests, CI/CD, observability, and the architecture clinic resolutions.
- The capstone is graded on what runs: keep the platform always runnable (`scripts/verify-environment.sh` + `scripts/verify-lab.sh` are the self-check).
- Architecture decisions must be answerable: each ADR in `docs/decisions/` is one prepared answer to a "why did you do X?" capstone question.

## 4. Active-recall drilling plan (levels 1–6)

Per master prompt §24, every topic moves through: 1 READ → 2 UNDERSTAND → 3 EXPLAIN → 4 IMPLEMENT → 5 DEBUG → 6 TEACH.

| Level | Drill | Evidence in this repo |
|---|---|---|
| 3 Explain | Write the topic's explanation in the lecture note's own words, then diff against the deck in your head. | `docs/lectures/*/session-NN.md` §1–2 |
| 4 Implement | Re-code the lab from the note only (no reference branch, no doc). | `platform/` commit for that lab |
| 5 Debug | Deliberately break it (wrong group id, missing AOP starter, wrong fallback signature) and fix from the symptom. | `docs/ENGINEERING_LOG.md` entries |
| 6 Teach | Explain on the whiteboard to a peer / write the exam-prep answer in your own words. | This file + quiz notes in `docs/exam/` |

Level 6 test: if the explanation requires the code open, it is not yet at level 6.

## 5. `docs/exam/` file plan

| File | Purpose |
|---|---|
| `docs/exam/mid-course-exam-checklist.md` | The §2.1/§2.2 checklists as a tickable file; update after each lab. |
| `docs/exam/quiz-notes.md` | One entry per session quiz: the 8 questions you missed/flagged + why. |
| `docs/exam/traps.md` | The course's known traps (S08-Q04 eviction, consumer-group typo, AOP starter, wrong fallback signature, gateway web starter, `#result.id` vs `#product.id`, Keycloak port/realm discrepancy). One line each: trap → detection → fix. |
| `docs/exam/mock-exams/mock-01.md` … | Self-written mock exam sets (task + expected artifacts + acceptance criteria), one per phase. |
| `docs/exam/capstone-questions.md` | "Why did you choose X?" questions with the ADR pointer that answers each. |

`quiz-notes.md` and `traps.md` are created now (empty templates); the rest are created when their phase completes.
