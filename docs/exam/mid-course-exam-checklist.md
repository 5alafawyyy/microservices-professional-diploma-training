# Mid-Course Exam Checklist (Sessions 1–8)

> Practical coding exam, 2 hours, individual, supervised at the Session 9 anchor day. 15% of the grade.
> Tick an item only when you have done it **from memory** (no notes, no reference branch) at least once.
> Plan and drills: `docs/roadmap/EXAM_PREPARATION_ROADMAP.md` §2.

## A. Boot the platform from zero

- [ ] `docker compose up -d`, wait for healthy, explain what postgres/redis/kafka are for
- [ ] Start config-server, eureka-server, product-service; verify 8761 + 8888/actuator/health
- [ ] Explain what `spring.config.import: optional:configserver:…` does and the meaning of `optional:`

## B. Write from scratch (no reference)

- [ ] Eureka Server: dependency, `@EnableEurekaServer`, port 8761, disable self-preservation (dev)
- [ ] Config Server: `@EnableConfigServer`, native profile, `classpath:/configs`, port 8888
- [ ] Product CRUD: service layer (`findAll`, `findById`→`Optional`, `save` assigning ids, `deleteById`)
- [ ] Product controller: 200 / 201 / 404 semantics; verify with curl
- [ ] ≥3 service-layer unit tests that compile and pass with `mvn test`
- [ ] Gateway: route to `lb://PRODUCT-SERVICE`, `Path` predicate, `AddResponseHeader`
- [ ] Gateway `GlobalFilter` + `Ordered` logging method/path/status
- [ ] `JwtUtil` (validate → Claims, throws `JwtException`) + `isTokenValid()` wrapper
- [ ] `JwtAuthFilter`: public routes, Bearer extraction, 401 JSON, `X-User-Id` / `X-User-Role`
- [ ] Rate limiting: `RequestRateLimiter`, IP `KeyResolver` with `@Primary`, yaml numbers
- [ ] Resilience stack on one method with correct order + four fallbacks with correct signatures
- [ ] All four resilience yaml blocks (window/threshold/wait; attempts/wait/multiplier; concurrent/wait; timeout/cancel)
- [ ] `InventoryClient` Feign interface + `ErrorDecoder` (409/404) + JWT propagation interceptor
- [ ] Kafka producer + two consumers with the correct distinct group ids
- [ ] Saga handlers for Order / Inventory / Payment incl. compensation (`releaseStock` idempotent)
- [ ] Caching annotations incl. the list-eviction trap

## C. Numbers you must not look up

- [ ] Ports: gateway 8080 · product 8081 · order 8082 · payment 8083 · inventory 8084 · notification 8085 · eureka 8761 · config 8888 · postgres 5432 · kafka 9092 · redis 6379 · zipkin 9411
- [ ] CB: window 10 / threshold 50 / open-wait 5s
- [ ] Retry: 3 attempts / 500ms / exponential ×2
- [ ] Bulkhead: 10 concurrent / 0ms wait
- [ ] TimeLimiter: 2s / cancel-running-future true
- [ ] Rate limit: replenish 10 / burst 20 / requested 1
- [ ] Cache TTL: 300000 ms
- [ ] Outbox poll: 1000 ms
- [ ] JWT dev secret: `microservices-pro-course-dev-secret-key-2026-min-256-bits`

## D. Explain without code (whiteboard-ready)

- [ ] Monolith vs microservices: the four claims and the four costs
- [ ] Bounded context rule and why a shared table is not a merge reason
- [ ] What discovery removes (hardcoded IPs, manual updates) and how registration works step by step
- [ ] Why config externalization matters (8 files → 1) and the 12-Factor link (Factor III)
- [ ] CB state machine: CLOSED → OPEN → HALF_OPEN with triggers and timings
- [ ] Choreography vs orchestration trade-off
- [ ] Cache-aside flow + eviction correctness

## E. Exam-day logistics

- [ ] Fresh clone of my repo builds (`mvn -q test` in every module)
- [ ] `./scripts/verify-environment.sh` PASS before leaving home
- [ ] Know the commit format: `session-NN: <description>`
