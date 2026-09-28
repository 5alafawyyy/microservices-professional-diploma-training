# Phase 1 Roadmap — Foundations (Sessions 00–08)

> Goal: understand microservices architecture and build the platform foundation: service discovery, centralized config, API gateway, security, resilience, service communication, event-driven architecture, caching.
> Phase 1 ends with **Architecture Clinic #1** (Session 8) and is immediately followed by the **Mid-Course Exam** (Session 9 anchor day, covers Sessions 1–8).

## Phase outcome

By the end of Phase 1 the platform must be:

```
client → api-gateway :8080 (LoggingFilter + JwtAuthFilter + RequestRateLimiter)
              │ Eureka lookup
   ┌──────────┼────────────────────┬──────────────────┐
   ▼          ▼                    ▼                  ▼
product    order               inventory          payment
 :8081      :8082                :8084              :8083
 JPA+Redis  Feign pre-check      stock reserve/     saga step
 cache      saga initiator       release
   │          │                    │                  │
   └──────────┴──── Kafka :9092 (order-events / inventory-events / payment-events) ────┘
```

Precisely what exists after each session is documented in `ARCHITECTURE_EVOLUTION.md` (stage-by-stage, with git evidence).

## Session-by-session

### Session 00 — Program Kickoff (no code)

- **Deliverable:** understanding of the assessment model (Quizzes 10 / Labs 40 / Mid exam 15 / Capstone 35), the 7-step session loop, the port map, and the "no commit = no grade" rule.
- **Study note:** `docs/lectures/phase-1/session-00-kickoff.md`.

### Session 01 — Architecture & Spring Cloud

- **Concepts:** monolith pain, microservices definition, bounded contexts, Eureka mechanics, Config Server mechanics, 12-Factor Factor III.
- **Build:** Eureka Server (:8761), Config Server (:8888, `native` profile), Product Service (:8081, in-memory CRUD API + Eureka + Config).
- **Lab:** Lab 1 — `docs/labs/lab-01/` (see `SESSION_TO_LAB_MAP.md`).
- **Acceptance:** postgres healthy; `PRODUCT-SERVICE` in Eureka; GET/POST/DELETE endpoints; 404 for missing id; ≥3 unit tests; `mvn test` green.
- **Checkpoint commit:** `session-01: add-product-service-eureka-config`.
- **Homework (becomes required groundwork for S08):** convert Product to JPA + PostgreSQL (`@Entity`, `JpaRepository`, `@DataJpaTest` ≥ 2 cases).

### Session 02 — API Gateway Routing

- **Concepts:** gateway as single entry point, WebFlux vs MVC (no `spring-boot-starter-web` in the gateway pom!), Path predicate, `lb://` via Eureka, GlobalFilter + Ordered.
- **Build:** `infrastructure/api-gateway` (:8080) with a `product-service` route and `LoggingFilter`; `X-Platform` response header.
- **Lab:** Lab 2A.
- **Acceptance:** `API-GATEWAY` in Eureka; `GET http://localhost:8080/api/v1/products` proxied; `[GATEWAY]` log line; `X-Platform: microservices-pro`; ≥2 filter tests.
- **Checkpoint commit:** `session-02: add-api-gateway-with-product-route-and-logging-filter`.

### Session 03 — Gateway Security

- **Concepts:** validation vs issuance ("we are validating JWTs, not issuing them"), Bearer tokens, whitelist (public) routes, token-bucket rate limiting (`replenishRate` vs `burstCapacity`).
- **Build:** `JwtUtil` + `JwtAuthFilter` (jjwt 0.11.5), `X-User-Id`/`X-User-Role` header propagation, `RateLimitConfig` + Redis-backed `RequestRateLimiter` (10 r/s, burst 20), `tools/jwt-generator` CLI for dev tokens.
- **Lab:** Lab 2B + companion `session-03-jwt-testing.md`.
- **Acceptance:** GET public 200 without token; POST 401 without token; POST 201 with valid token; 25 rapid requests → ~20×200 then 429; `X-RateLimit-Remaining` header; 5 unit tests.
- **Checkpoint commit:** `session-03: add-jwt-auth-filter-and-rate-limiting`.
- **Critical:** never build a login endpoint — token issuance is Session 20's job.

### Session 04 — Resilience

- **Concepts:** circuit breaker states (CLOSED/OPEN/HALF_OPEN), failure-rate threshold, sliding window, retry with exponential backoff, fallback methods, why `spring-boot-starter-aop` is mandatory.
- **Build:** order-service (:8082) calling an in-process payment stub wrapped in `@CircuitBreaker` + `@Retry`; payment-service (:8083) with configurable `failure-rate`.
- **Lab:** Lab 3A.
- **Acceptance:** CONFIRMED on success / PENDING on failure; `/actuator/circuitbreakers` shows OPEN after ≥5 failures, HALF_OPEN after 5s; `[RETRY]` logs with visible 500ms→1000ms backoff; ≥3 tests.
- **Checkpoint commit:** `session-04: add-circuit-breaker-and-retry-on-order-payment`.

### Session 05 — Resilience Advanced

- **Concepts:** bulkhead (concurrency limit), time limiter (2s timeout), async `CompletableFuture` controller, **exact annotation order** `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry` (outermost-first).
- **Build:** extend order-service `createOrderAsync()` with the full stack.
- **Lab:** Lab 3B.
- **Acceptance:** 15 concurrent requests → ~10 processed + ~5 `QUEUED`; `payment.delay-ms=3000` → PENDING in ~2s; `[BULKHEAD]`/`[TIMEOUT]` logs; reflection test proving annotation presence.
- **Checkpoint commit:** `session-05: add-bulkhead-and-timelimiter-to-order-payment`.

### Session 06 — Service Communication

- **Concepts:** declarative HTTP clients (OpenFeign), service-name resolution via Eureka (no hardcoded host:port), `ErrorDecoder` translating HTTP status → domain exceptions, JWT propagation between services.
- **Build:** inventory-service (:8084) with `checkStock`; order-service `InventoryClient` + `InventoryErrorDecoder` + `FeignJwtInterceptor`; stock pre-check before payment.
- **Lab:** Lab 4A.
- **Acceptance:** `INVENTORY-SERVICE` in Eureka; `PROD-001` qty 5 → 200; `PROD-003` → 409; order rejected on 409; inventory logs show forwarded `Authorization`; tests green.
- **Checkpoint commit:** `session-06: add-inventory-service-and-feign-client`.

### Session 07 — Event Driven Architecture

- **Concepts:** Kafka topics/partitions/consumer groups, choreography saga, compensation, idempotency of compensation, the 5 distinct consumer-group IDs trap.
- **Build:** `OrderPlacedEvent` → inventory reserve → `InventoryReservedEvent` → payment → `PaymentCompletedEvent` → order CONFIRMED; `PaymentFailedEvent` → inventory release → `InventoryReleasedEvent` → order CANCELLED.
- **Lab:** Lab 5A.
- **Acceptance:** POST returns PENDING + orderId instantly; happy path → CONFIRMED; `failure-rate=1.0` → CANCELLED; all 3 topics receiving; `[SAGA] COMPENSATION` log; tests green.
- **Checkpoint commit:** `session-07: add-choreography-saga-order-inventory-payment`.
- **Critical:** the S6 Feign pre-check stays; `createOrderAsync()` is not deleted.

### Session 08 — Caching + Architecture Clinic #1

- **Concepts:** cache-aside, `@Cacheable`/`@CacheEvict`, TTL, the stale-list trap (evicting one key leaves `'all'` stale), cache stampede considerations.
- **Build:** product-service caching via Redis (TTL 300s), eviction on save/delete including `evictAllProductsCache()`.
- **Lab:** Lab 6A.
- **Acceptance:** miss → hit on repeated GET; `redis-cli KEYS products*` + `TTL < 300`; save/delete evicts both keys; ≥3 tests.
- **Checkpoint commit:** `session-08: add-redis-caching-to-product-service`.
- **Clinic #1 (discussion, no code):** defend every Phase-1 decision; compile the **Technical Debt Register** (8 known items — see digest §2; it carries forward to Clinic #2 in Session 24).

## Phase 1 completion criteria

- [ ] All 9 checkpoint commits present (`session-01` … `session-08`).
- [ ] `mvn test` green in every module.
- [ ] Full stack runs locally per Lab-1 startup order.
- [ ] Technical Debt Register written (Clinic #1 output).
- [ ] Mid-Course Exam (S1–8) completed — see `docs/exam/`.
- [ ] `docs/architecture/CURRENT_ARCHITECTURE.md` matches the S8 platform state.
