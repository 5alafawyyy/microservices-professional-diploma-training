# Architecture Evolution

> Derived from actual repository evidence on 2026-09-28 (branch analysis of microservices-pro-platform).

## How to read this document

- Evidence base: read-only inspection of the reference clone at `_references/microservices-pro-platform` (paths quoted; no checkout, no fetch, no writes). The only artifact produced by this analysis is this file.
- Commands used throughout: `git log --format='%h %p %s'`, `git show --stat <commit>`, `git show <ref>:<path>`, `git ls-tree -r --name-only <ref>`, `git diff --stat/--shortstat/--numstat/--name-status <a> <b>`.
- A "stage" is one session group of the training programme. Each stage exists as a branch **pair**: `session-XX-wip-main` (trainee skeleton, TODOs left in place) and `session-XX-wip-reference` (completed reference solution). 13 stages exist as branch pairs.
- `Changed:` reports the grouped diff of the stage tip against the **previous stage tip** on the same lineage. "Groups" are the top-level repository areas: `services/`, `infrastructure/`, `tools/`, `docs/`, `.github/workflows/`, `k8s/`, `helm/`, `observability/`, `keycloak/`, `k6/`, and root files (`docker-compose.yml`, `README.md`, …). The reference lineage is quoted first; the `-wip-main` mirror second.
- Stages 8–13 (session-13-14 onward) are **single-commit branches forked from the sessions-1-8 snapshot**, not cumulative branches. For those stages the consecutive-stage diff contains large artificial "deletions"; therefore each section also gives the stage's **own commit** diff (`git show --stat`), which is the meaningful measure. This is a property of the repository as it exists, not an interpretation.
- `Commits:` lists the subject lines that belong to the stage (oldest → newest) on each lineage.
- Tech versions are only ever quoted from `pom.xml`, `docker-compose.yml` or workflow files. No version is guessed.
- Anything that could not be proven from the repository is marked `UNKNOWN — REQUIRES SOURCE REVIEW`.

## Branch model of the reference repository

Two branch families exist: for every stage, `session-XX-wip-main` (skeleton) and `session-XX-wip-reference` (solution). Two additional long-lived branches exist: `origin/main` (= `aad53b2`, subject `session-06-07-08`) and `origin/reference` (= `39bb3c6`, subject `session-06-07-08`). Their trees are identical to the `session-06-07-08` tips (`git diff --stat 52add5a 39bb3c6` and `git diff --stat f1237d9 aad53b2` are both empty) — they are the "sessions 1-8 snapshot" both later fragments fork from.

Branch tip inventory (verified by `git log -1 <ref>`):

| Stage | `session-XX-wip-main` tip | `session-XX-wip-reference` tip |
| --- | --- | --- |
| session-01-02 | `9c81543` | `398c4a2` |
| session-03 | `794745a` | `84ad7e3` |
| session-04 | `1eda551` | `2c2f623` |
| session-06-07-08 | `f1237d9` | `52add5a` |
| session-09 | `44f3516` | `de2c118` (branch is spelled `origin/session-09-wip-referenc` — missing trailing `e`) |
| session-10-11 | `6baf680` | `45d35be` |
| session-12 | `479ea22` | `ee20245` |
| session-13-14 | `42cd25e` | `9e4a98b` |
| session-15-16 | `e900998` | `123a076` |
| session-17 | `25de035` | `6af10f2` |
| session-18-19 | `29f6cb1` | `4dd0f94` |
| session-20-21 | `8f37f52` | `fddfcd8` |
| session-22-23 | `ecae40b` | `18b3b34` |

### wip-main vs wip-reference relationship

At every stage the two branches have **identical directory trees**; `git diff --name-status` between the pair contains only `M` (modified) entries, all of them Java files (plus one `Dockerfile` at session-09). The skeleton contains unfinished method bodies/TODOs; the reference contains the completed code. Diff sizes grow with the amount of code a stage introduces:

| Stage | Pair diff (`git diff --shortstat origin/<stage>-wip-main origin/<stage>-wip-reference`) |
| --- | --- |
| session-01-02 | 4 files, +89/−35 |
| session-03 | 8 files, +249/−70 |
| session-04 | 10 files, +373/−115 |
| session-06-07-08 | 18 files, +704/−233 |
| session-09 | 26 files, +967/−396 |
| session-10-11 | 31 files, +1 208/−452 |
| session-12 | 34 files, +1 522/−509 |
| session-13-14 | 20 files, +776/−265 |
| session-15-16 | 18 files, +704/−233 |
| session-17 | 20 files, +719/−243 |
| session-18-19 | 21 files, +808/−254 |
| session-20-21 | 21 files, +882/−255 |
| session-22-23 | 19 files, +771/−243 |

At session-22-23 the skeleton contains 95 `TODO` markers versus 3 in the reference; the 3 remaining TODOs in the reference are benign code comments (`infrastructure/api-gateway/src/main/java/com/microservices/pro/apigateway/filter/JwtAuthFilter.java` line 50, `services/order-service/src/main/java/com/microservices/pro/orderservice/OrderSagaEventHandler.java` line 45, `services/product-service/src/main/java/com/microservices/pro/productservice/ProductService.java` line 15). The 19 files that differ at session-22-23 are: `RateLimitConfig`, `JwtAuthFilter`, `LoggingFilter`, `JwtUtil` (api-gateway); `InventoryController`, `InventorySagaHandler`, `InventoryService` (inventory-service); `FeignJwtInterceptor`, `InventoryErrorDecoder`, `OrderController`, `OrderSagaEventHandler`, `OrderService`, `OutboxPublisher` (order-service); `PaymentController`, `PaymentProcessor`, `PaymentSagaHandler` (payment-service); `ProductController`, `ProductService` (product-service).

### Lineage caveats (important when reading diffs)

- The repository contains **parallel rewritten copies** of the same stage commits (same subject lines and identical trees, different SHAs). Verified with `git diff --stat`:
  - `git diff --stat 84ad7e3 8cc3260` is empty (the 03-branch tip and the 03 copy on the 04 branch are the same tree).
  - `git diff --stat 2c2f623 0ba4548` is empty (the 04 commit exists twice).
  - `git diff --stat 398c4a2 c410931` = 1 file, 2+/2− (the two earliest copies differ only by one small edit).
  - E.g. the 03 branch (`84ad7e3`) does **not** descend from the 01-02 branch tip (`398c4a2`); it descends from `c410931`. The 04 branch descends from `398c4a2` through its own copies `f68c13b → 06006d4 → 79d994b → 8cc3260`.
- Reference lineage that is genuinely cumulative: `… 398c4a2 → f68c13b → 06006d4 → 79d994b → 8cc3260 → 2c2f623 → 0ba4548 → 39bb3c6 → de2c118 (09) → 45d35be (10-11) → ee20245 (12)`; verified by `git log --format='%h %p %s'`.
- Stages session-13-14 … session-22-23 are **each a single commit whose parent is `39bb3c6` (reference) / `aad53b2` (main)** — verified via `git rev-parse <tip>^`. They do not contain the session-09…12 material; their `docker-compose.yml` is either the untouched sessions-1-8 base file (blob `a475b7fe` — contains only `postgres`, `redis`, `zookeeper`, `kafka`) or a "Add this block to the existing docker-compose.yml" snippet. Why the training repository was organised this way is `UNKNOWN — REQUIRES SOURCE REVIEW`.
- Branch-name typo: the session-09 reference branch is `origin/session-09-wip-referenc` (no trailing `e`).

## Stage-by-stage evolution

### Stage 1 — session-01-02: platform foundation (product-service, Eureka, Config Server, API Gateway)

```
              ┌──────────────┐   lb://PRODUCT-SERVICE    ┌─────────────────┐
  client ───▶ │ api-gateway  │ ────────────────────────▶ │ product-service │   in-memory store
              │    :8080     │                           │      :8081      │
              └──────┬───────┘                           └────────┬────────┘
                     │  discovery                        config import
                     ▼                                            ▼
              ┌───────────────┐                         ┌────────────────┐
              │ eureka-server │ ◀──── register ──────── │ config-server  │
              │     :8761     │                         │ :8888 (native) │
              └───────────────┘                         └────────────────┘
  docker-compose: postgres (postgres:16-alpine) only — services run via `mvn spring-boot:run`
```

- Components: `services/product-service` (only service); `infrastructure/api-gateway`, `infrastructure/config-server`, `infrastructure/eureka-server`; no `tools/`, no `k6/`. Total tracked files at the tip: 37.
- Compose: single container `postgres` (`postgres:16-alpine`); comments state Eureka/Config/Gateway/Product run on the host until session 9.
- Tech: Spring Boot `3.3.4` (parent `spring-boot-starter-parent` per module — there is **no root/aggregator pom** at any stage), Java `21`, Spring Cloud `2023.0.3` (`spring-cloud-dependencies` import), `spring-boot-starter-web`, `spring-cloud-starter-netflix-eureka-client`, `spring-cloud-starter-config`, `spring-boot-starter-actuator`. Gateway route: `product-service` → `lb://PRODUCT-SERVICE`, `Path=/api/v1/products/**`, `StripPrefix=0`, `AddResponseHeader=X-Platform, microservices-pro`; config-server `spring.profiles.active: native` with `classpath:/configs`.
- Commits (reference): `0df1c7e` reference: complete session-01 and session-02 implementation · `6654af8` update repo url · `c410931` update LoggingFilterTest · `398c4a2` fix: update text spring -boot-starter-web. (main: `ffefaea` main: session-01 and session-02 skeleton with TODOs for students · `83c7817` update repo url · `317176e` update LoggingFilterTest · `9c81543` fix: update text spring -boot-starter-web.)
- Tests: `LoggingFilterTest`, `ProductServiceTest`.
Changed: no previous stage — this is the initial state (`git ls-tree -r 398c4a2` = 37 files; root contains no `pom.xml`).
Evidence: branches `session-01-02-wip-main`/`-reference`; `git ls-tree -r --name-only 398c4a2`; `git show 398c4a2:infrastructure/api-gateway/src/main/resources/application.yml`; `git show 398c4a2:services/product-service/pom.xml`.

### Stage 2 — session-03: JWT authentication + rate limiting on the gateway, jwt-generator tool, session CI

```
  client ───▶ ┌────────────────────────────┐    ┌─────────────────┐
              │        api-gateway :8080   │───▶│ product-service │  :8081
              │ JwtAuthFilter → JwtUtil    │    └─────────────────┘
              │ RequestRateLimiter ──┐     │
              └────────┬─────────────┼─────┘
                       │ discovery   ▼ redis:7-alpine  (token-bucket counters)
              ┌────────────────┐        ┌──────────────┐        ┌──────────────────┐
              │ eureka-server  │        │ tools/       │        │ config-server    │
              │    :8761       │        │ jwt-generator│───▶ dev JWTs (jjwt 0.11.5)
              └────────────────┘        └──────────────┘        └──────────────────┘
```

- Components: unchanged modules + **new** `tools/jwt-generator` (standalone CLI, not a Spring service, not in compose, deliberately not built by CI).
- Compose: `redis` (`redis:7-alpine`) added next to `postgres`. The compose header explains Redis here backs the gateway `RequestRateLimiter`, not the session-8 `@Cacheable` cache.
- Tech: `jjwt` `0.11.5` (`jjwt-api`/`-impl`/`-jackson`) in api-gateway and jwt-generator; gateway `application.yml` gains `jwt.secret: ${JWT_SECRET:microservices-pro-course-dev-secret-key-2026-min-256-bits}` (must match the generator's default) and `RequestRateLimiter` args `replenishRate: 10`, `burstCapacity: 20`, `requestedTokens: 1`, `key-resolver: "#{@ipKeyResolver}"`.
- Commits (reference): `f60f882` session-03: add-jwt-auth-filter-and-rate-limiting · `1b6b1f0` fix: update text spring -boot-starter-web · `263459e` fix: use MockServerHttpRequest instead of ServerRequest · `73048fc` remove duplicated folder reference · `84ad7e3` update JwtAuthFilter. (main: `641f97d` (skeleton) · `a622d49` · `794745a`.)
- Tests: + `JwtAuthFilterTest`, `JwtUtilTest`.
Changed: `git diff --stat 398c4a2 84ad7e3` (ref) = 18 files, +1 056/−18 → docs 5(+297/−6) · tools 3(+248) · infrastructure 7(+434) · workflows 1(+38, `session-03-validation.yml`) · root 2 (README, docker-compose). Main mirror (`9c81543 794745a`) = 18 files, +934/−21 → infrastructure 7(+312/−2) · root 2(+39/−13).
Evidence: branches `session-03-*`; `git diff --name-status 398c4a2 84ad7e3`; `git show 84ad7e3:infrastructure/api-gateway/src/main/resources/application.yml`; `git ls-tree -r 84ad7e3 -- tools/jwt-generator` (3 files added: `README.md`, `pom.xml`, `JwtGeneratorApplication.java`).

### Stage 3 — session-04: order-service and payment-service with Resilience4j

```
                    ┌────────────────────────┐        ┌───────────────────┐
  client ───▶ gateway │      order-service     │        │  payment-service  │
                      │         :8082          │  X     │       :8083       │
                      │ OrderService           │──────▶ │ PaymentController │
                      │  @Bulkhead→@TimeLimiter│ (no network yet: in-process stub) │
                      │  →@CircuitBreaker→@Retry│       └───────────────────┘
                      └────────────────────────┘
```

- Components: + `services/order-service` (OrderController, OrderRequest/Response, OrderService, PaymentRequest/Response, **in-process `PaymentService` stub**, RetryLogger), + `services/payment-service` (PaymentController, PaymentRequest/Response).
- Compose: **unchanged** (`git diff 84ad7e3 2c2f623 -- docker-compose.yml` is empty); only README changed at root.
- Tech: `resilience4j-spring-boot3` + `spring-boot-starter-aop` added to order-service (Resilience4j version is BOM-managed — concrete resolved version `UNKNOWN — REQUIRES SOURCE REVIEW`). No Feign, no Kafka, no JPA yet. OrderService stack: `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry`, all targeted at the *in-process* payment stub — a class comment states wiring a real HTTP call is intentionally deferred to session 6 (OpenFeign).
- Commits (reference): `2c2f623` session-04: add-circuit-breaker-and-retry-on-order-payment. (main: `1eda551` skeleton.)
- Tests: + `OrderServiceTest`.
Changed: `git diff --stat 84ad7e3 2c2f623` (ref) = 26 files, +1 224/−13 → services 18(+756) · docs 6(+378/−7) · workflows 1(+81, `session-04-05-validation.yml`) · root 1 (README). Main mirror (`794745a 1eda551`) = 27 files, +1 147/−15 → services 18(+677) · infrastructure 1(+2/−2).
Evidence: branches `session-04-*`; `git show 2c2f623:services/order-service/pom.xml`; `git show 2c2f623:services/order-service/src/main/java/com/microservices/pro/orderservice/OrderService.java`; `git diff 84ad7e3 2c2f623 -- docker-compose.yml` (empty).

### Stage 4 — session-06-07-08: inventory-service, Feign, Kafka choreography saga, CQRS-style cache

```
   ┌─────────────────┐   Feign   ┌───────────────────┐
   │  order-service  │──────────▶│ inventory-service │  :8084
   │     :8082       │           │ InventorySagaHandler│
   │ OrderSagaEventHandler       └─────────┬─────────┘
   │ ProductRepository/JPA                 │
   └────────┬────────┘                     ▼
            │  topics: order-events → payment-events → inventory-events
            ▼
   ┌─────────────────┐
   │ payment-service │  :8083   PaymentSagaHandler (choreography saga)
   └─────────────────┘
   docker-compose: + zookeeper (confluentinc/cp-zookeeper:7.6.1) + kafka (confluentinc/cp-kafka:7.6.1)
```

- Components: + `services/inventory-service` (full module incl. 8 event classes); order-service gains `InventoryClient` (@FeignClient), `InventoryErrorDecoder`, `FeignJwtInterceptor`, JPA `Order`/`OrderRepository`, `OrderSagaEventHandler`; payment-service gains `PaymentProcessor`, `PaymentSagaHandler`; product-service gains `ProductRepository` (+ JPA/PostgreSQL + `@Cacheable`/`@CacheEvict`, `@EnableCaching`).
- Compose: `zookeeper` (`confluentinc/cp-zookeeper:7.6.1`) and `kafka` (`confluentinc/cp-kafka:7.6.1`) added; result: `postgres`, `redis`, `zookeeper`, `kafka` (51+/16− in docker-compose.yml).
- Tech: `spring-kafka` (unpinned → version from Boot BOM: `UNKNOWN — REQUIRES SOURCE REVIEW`), `spring-cloud-starter-openfeign`, `spring-boot-starter-data-jpa`, `postgresql`, Kafka JSON serializers/deserializers; 8 shared event classes per service (`OrderPlacedEvent`, `PaymentCompleted/FailedEvent`, `InventoryReserved/ReservationFailed/ReleasedEvent`, `OrderConfirmed/CancelledEvent`).
- Commits (reference): `0ba4548` session-04: add-circuit-breaker-and-retry-on-order-payment (tree-identical copy) · `52add5a` session-06-07-08. (main: `c14fbed` · `f1237d9`.)
- Tests: + `OrderSagaEventHandlerTest`, `OrderSagaTest` (order), `PaymentSagaHandlerTest` (payment), `InventorySagaTest`, `InventoryServiceTest` (inventory).
Changed: `git diff --stat 2c2f623 52add5a` (ref) = 82 files, +2 805/−240 → services 70(+1 910/−135) · docs 9(+686/−81) · workflows 1(+149, `session-06-07-08-validation.yml`) · root 2(+60/−24). Main mirror (`1eda551 f1237d9`) = 82 files, +2 545/−193 → services 70(+1 650/−88).
Evidence: branches `session-06-07-08-*`; `git ls-tree -r 52add5a -- services/inventory-service/src/test`; `git show 52add5a:docker-compose.yml`; `git diff --stat f1237d9 aad53b2` and `git diff --stat 52add5a 39bb3c6` (both empty → snapshot identity).

### Stage 5 — session-09: Docker containerization

```
  ┌──────────────────────────────────────────────────────────────────┐
  │ docker-compose.yml — network platform-net                        │
  │   postgres · redis · zookeeper · kafka                           │
  │   config-server:local   eureka-server:local   api-gateway:local  │
  │   product-service:local  order-service:local                     │
  │   payment-service:local  inventory-service:local                 │
  └──────────────────────────────────────────────────────────────────┘
```

- Components: no new modules; every module gets `Dockerfile` + `.dockerignore` (7 modules × 2 = 14 files). Dockerfile pattern: multi-stage `maven:3.9-eclipse-temurin-21` builder → `eclipse-temurin:21-jre-jammy` runtime, non-root `appuser`, `HEALTHCHECK` via `curl /actuator/health`.
- Compose: 7 application containers added, images `microservices-pro/<module>:local`: `config-server`, `eureka-server`, `api-gateway`, `product-service`, `inventory-service`, `payment-service`, `order-service`.
- Tech: no new Java libraries; container base images as above; JWT secret remains env-driven.
- Commits (reference): `de2c118` session-09: docker-containerization. (main: `44f3516`.)
- Tests: none added.
Changed: `git diff --stat 52add5a de2c118` (ref) = 18 files, +1 117/−28 → root 1(+261/−28, docker-compose) · docs 2(+269: lab 8a, trainer 09) · infrastructure 6(+219, Dockerfiles) · workflows 1(+112, `session-09-validation.yml`) · services 8(+256). This equals the stage's own commit (`git show --stat de2c118` = 18 files, +1 117/−28) because its parent `39bb3c6` has the same tree as `52add5a`. Main mirror (`f1237d9 44f3516`) = 18 files, +1 023/−34.
Evidence: branches `session-09-wip-main`/`session-09-wip-referenc`; `git show de2c118:docker-compose.yml`; `git show de2c118:services/product-service/Dockerfile`; `git show --stat de2c118`.

### Stage 6 — session-10-11: automated testing (Pact, WireMock, Testcontainers)

```
  [ProductServiceIntegrationTest] ── Testcontainers ──▶ postgres:16 container
  [OrderServiceInventoryContractTest · Pact consumer] ──▶ (pact contract)
  [InventoryServicePactVerificationTest · Pact provider] ◀── replays the contract
  [OrderServicePaymentWireMockTest] ── WireMock stub ──▶ payment HTTP API
```

- Components: unchanged modules; test sources and two test `application.properties` files added.
- Compose: unchanged (no root group in the diff).
- Tech: `testcontainers` `1.19.8` (`testcontainers-bom` import, product-service), `au.com.dius.pact.consumer:junit5` `4.6.7` (order-service consumer) and `au.com.dius.pact.provider` `4.6.7` (inventory-service provider), `spring-cloud-contract-wiremock` (BOM-managed).
- Commits (reference): `45d35be` session-10-11: testing. (main: `6baf680`.)
- Tests: + `InventoryServicePactVerificationTest`, `OrderServiceInventoryContractTest`, `OrderServicePaymentWireMockTest`, `ProductControllerTest`, `ProductServiceIntegrationTest`, `ProductServiceParameterizedTest`.
Changed: `git diff --stat de2c118 45d35be` (ref) = 17 files, +1 158/−84 → services 12(+688/−84) · docs 4(+381: labs 9a/9b, trainer 10/11) · workflows 1(+89, `session-10-11-validation.yml`). Main mirror (`44f3516 6baf680`) = 17 files, +949/−60 → services 12(+479/−60).
Evidence: branches `session-10-11-*`; `git show 45d35be:services/product-service/pom.xml`; `git diff --name-status de2c118 45d35be`.

### Stage 7 — session-12: saga orchestration

```
  ┌─────────────────────────────┐                 commands           ┌───────────────────┐
  │        order-service        │  ProcessPaymentCommand ── Kafka ──▶│ payment-service   │
  │  OrderSagaOrchestrator      │  ReserveInventoryCommand ────────▶ │ PaymentSagaCommandHandler
  │  SagaState · SagaKafkaConfig│  ReleaseInventoryCommand ────────▶└─────────┬─────────┘
  └──────────────┬──────────────┘                                  ┌─────────▼─────────┐
                 └───────── result events (PaymentResultEvent,     │ inventory-service │
                            InventoryResultEvent, InventoryReleasedEvent) InventorySagaCommandHandler
                                                                  └───────────────────┘
  (the session-06-07-08 choreography handlers remain in the tree)
```

- Components: order-service `saga/` package (`OrderSagaOrchestrator`, `SagaKafkaConfig`, `saga/SagaState`, `saga/commands/{ProcessPaymentCommand,ReserveInventoryCommand,ReleaseInventoryCommand}`, `saga/results/{InventoryReleasedEvent,InventoryResultEvent,PaymentResultEvent}`); inventory-service `InventorySagaCommandHandler`; payment-service `PaymentSagaCommandHandler`.
- Compose: unchanged.
- Tech: no new libraries — orchestration built on existing spring-kafka.
- Commits (reference): `ee20245` session-12: saga-Orchestration. (main: `479ea22`.)
- Tests: + `OrderSagaOrchestratorTest`.
Changed: `git diff --stat 45d35be ee20245` (ref) = 18 files, +1 067/−49 → services 15(+790/−49) · docs 2(+193) · workflows 1(+84, `session-12-validation.yml`). Main mirror (`6baf680 479ea22`) = 18 files, +810/−49 → services 15(+533/−49).
Evidence: branches `session-12-*`; `git diff --name-status 45d35be ee20245`.

### Stage 8 — session-13-14: CI/CD (notification-service, GitHub Actions, ArgoCD manifests)

> Topology note: this branch is a single commit forked from `39bb3c6` (sessions 1-8 snapshot), so it does **not** contain the session-09…12 files. The "Changed" line below therefore mixes real additions with artificial deletions; the stage's own commit is shown separately.

```
  ┌────────────────────────────┐      ┌──────────────────────────────────────────┐
  │  notification-service      │      │  .github/workflows/                      │
  │  (payment-events consumer) │      │   notification-service-ci.yml (new)     │
  │  @RetryableTopic →         │      │   product-service-ci.yml (new)           │
  │   payment-events-retry-0/1 │      └──────────────────────────────────────────┘
  │   payment-events-dlt       │      ┌──────────────────────────────────────────┐
  │  :8085 (compose snippet)   │      │  k8s/argocd/product-service-app.yaml     │
  └────────────────────────────┘      │  k8s/product-service/{configmap,         │
                                      │    deployment, deployment-canary, service}
                                      └──────────────────────────────────────────┘
```

- Components: + `services/notification-service` (Dockerfile, .dockerignore, pom, `NotificationService` with `@RetryableTopic`, `NotificationServiceApplication`, application.yml); + `k8s/` (5 manifests, incl. ArgoCD Application); compose replaced by an "add this block" snippet for `notification-service` (`microservices-pro/notification-service:local`, port 8085, listens on existing `payment-events` topic; retry topics auto-created).
- Tech: no new poms/dependencies beyond the module's own; no version pins added.
- Commits (reference): `9e4a98b` session-13-14: CICD. (main: `42cd25e`.) Own commit: 18 files, +969/−76.
- Tests: none added (notification-service ships without tests).
Changed: `git diff --stat ee20245 9e4a98b` (ref) = 69 files, +1 063/−3 351 → services 40(+359/−1 710) · docs 12(+339/−843) · k8s 5(+173) · infrastructure 6(−219) · workflows 5(+175/−285: 3 session workflows dropped, 2 added) · root 1(+17/−294, compose→snippet). Main mirror (`479ea22 42cd25e`) = 70 files, +1 035/−2 821. **Own commit `9e4a98b` = 18 files, +969/−76** — the meaningful stage diff.
Evidence: branches `session-13-14-*`; `git show --stat 9e4a98b`; `git rev-parse 9e4a98b^` = `39bb3c6`; `git show 9e4a98b:docker-compose.yml`.

### Stage 9 — session-15-16: Kubernetes (plain manifests + Helm chart)

```
  ┌───────────────────────────────────┐    ┌───────────────────────────────────────────┐
  │ helm/product-service-chart        │    │ k8s/product-service                       │
  │  Chart.yaml (apiVersion v2,       │    │  deployment.yaml   hpa.yaml   secret.yaml │
  │   version 0.1.0, appVersion 1.0.0)│    └───────────────────────────────────────────┘
  │  values.yaml                      │    (the fragment's own commit adds these; the
  │  templates/: deployment, hpa,     │     13-14 ArgoCD manifest is not present on
  │   role, rolebinding, service,     │     this branch — topology artifact)
  │   serviceaccount                  │
  └───────────────────────────────────┘
```

- Components: + `helm/product-service-chart` (8 files); + `k8s/product-service/{deployment,hpa,secret}.yaml`. No new services.
- Compose: equals the sessions 1-8 base blob `a475b7fe` (postgres/redis/zookeeper/kafka only).
- Tech: Helm chart API `v2`, chart `version 0.1.0`, `appVersion "1.0.0"`; Helm CLI version itself is not pinned in the repository (`UNKNOWN — REQUIRES SOURCE REVIEW`). No new Java dependencies.
- Commits (reference): `123a076` session-15-16: kubernetes. (main: `e900998`.) Own commit: 15 files, +663.
- Tests: none added.
Changed: `git diff --stat 9e4a98b 123a076` (ref) = 32 files, +699/−929 → docs 8(+349/−339) · helm 8(+190) · k8s 7(+84/−133) · workflows 2(−175, the CI files from 13-14) · root 1(+76/−32) · services 6(−250). Main mirror (`42cd25e e900998`) = 32 files, +699/−889. **Own commit = 15 files, +663.**
Evidence: branches `session-15-16-*`; `git show --stat 123a076`; `git ls-tree -r 123a076 -- helm k8s`.

### Stage 10 — session-17: observability (Zipkin, Prometheus, Grafana, tracing, logback)

```
  services ──/actuator/prometheus──▶ prom/prometheus:v2.51.0 (scrapes prometheus.yml)
                                          │
  spans ──zipkin-reporter-brave──▶ openzipkin/zipkin:3 ──▶ Grafana 10.4.2 (datasource: prometheus)
  logs ──logstash-logback-encoder 7.4 (logback-spring.xml in order + product)
```

- Components: + `observability/prometheus.yml`, `observability/grafana/datasources/prometheus.yml`; order- and product-service gain `ObservabilityConfig.java`, `logback-spring.xml`, pom + application.yml updates.
- Compose: replaced by a snippet adding `zipkin` (`openzipkin/zipkin:3`, :9411), `prometheus` (`prom/prometheus:v2.51.0`, :9090), `grafana` (`grafana/grafana:10.4.2`, :3000).
- Tech: `micrometer-tracing-bridge-brave`, `io.zipkin.reporter2:zipkin-reporter-brave`, `micrometer-registry-prometheus` (all BOM-managed → concrete versions `UNKNOWN — REQUIRES SOURCE REVIEW`), `net.logstash.logback:logstash-logback-encoder` `7.4` (pinned), Testcontainers test deps added to the poms.
- Commits (reference): `6af10f2` session-17. (main: `25de035`.) Own commit: 13 files, +580/−243.
- Tests: none added.
Changed: `git diff --stat 123a076 6af10f2` (ref) = 28 files, +580/−906 → services 8(+274/−176) · docs 6(+205/−349) · observability 2(+53) · k8s 3(−124) · helm 8(−190) · root 1(+48/−67). Main mirror (`e900998 25de035`) = 28 files, +575/−906. **Own commit = 13 files, +580/−243.**
Evidence: branches `session-17-*`; `git show 6af10f2:services/order-service/pom.xml`; `git show 6af10f2:docker-compose.yml`.

### Stage 11 — session-18-19: Keycloak + product command/query split + cache eviction listener

```
  ┌───────────────────────┐        ┌────────────────────────────────────────────┐
  │ keycloak (24.0.4)     │        │ product-service (on this branch)           │
  │ :8180 → 8080  start-dev│       │  ProductCommandService  ProductQueryService│
  │ realm-export.json     │        │  ProductSummaryProjection                  │
  │ admin/admin (DEV ONLY) │       │  ProductChangedEvent → ProductCacheEvictionListener
  └──────────┬────────────┘        └────────────────────────────────────────────┘
             └── token issuer for the gateway (OAuth2 arrives in session-20-21)
```

- Components: + `keycloak/realm-export.json`; product-service: `ProductCommandService`, `ProductQueryService`, `ProductSummaryProjection`, `ProductChangedEvent`, `ProductCacheEvictionListener` + `ProductCommandServiceTest`.
- Compose: replaced by a snippet adding `keycloak` (`quay.io/keycloak/keycloak:24.0.4`, host port 8180 → 8080, `start-dev`, admin/admin DEV ONLY, manual or `KC_IMPORT` realm import).
- Tech: Keycloak image `24.0.4`; no new Java dependencies.
- Commits (reference): `4dd0f94` session-18-19. (main: `29f6cb1`.) Own commit: 12 files, +663/−76.
- Tests: + `ProductCommandServiceTest`.
Changed: `git diff --stat 6af10f2 4dd0f94` (ref) = 24 files, +839/−589 → services 14(+478/−274) · docs 6(+280/−205) · keycloak+observability group 3(+50/−53: `keycloak/realm-export.json` added; `observability/prometheus.yml` + `observability/grafana/datasources/prometheus.yml` removed) · root 1(+31/−57, `docker-compose.yml` incl. the keycloak snippet). Main mirror (`25de035 29f6cb1`) = 24 files, +756/−584. **Own commit = 12 files, +663/−76.**
Evidence: branches `session-18-19-*`; `git show --stat 4dd0f94`; `git show 4dd0f94:docker-compose.yml`.

### Stage 12 — session-20-21: OAuth2 resource server in the gateway + Istio manifests

```
  client ── JWT (Keycloak realm) ──▶ ┌───────────────────────────┐
                                     │ api-gateway               │
                                     │  SecurityConfig           │
                                     │  UserContextEnrichmentFilter│
                                     │  spring-boot-starter-oauth2-│
                                     │  resource-server (replaces jjwt)
                                     └────────────┬──────────────┘
        k8s/istio/ ────────────────────────────┐   │ order-service OrderServiceTokenClient
         virtual-service-product.yaml          │   ▼
         destination-rule-product.yaml         (service-to-service token)
         peer-authentication.yaml
```

- Components: api-gateway `SecurityConfig`, `UserContextEnrichmentFilter`; order-service `OrderServiceTokenClient`; `k8s/istio/{virtual-service-product, destination-rule-product, peer-authentication}.yaml`; updated `keycloak/realm-export.json`. On this branch the session-18-19 product-service command/query classes are absent (topology artifact — they belong to the 18-19 branch).
- Compose: equals the sessions 1-8 base blob `a475b7fe` again (the 18-19 keycloak snippet is not carried over; keycloak must be added per the 18-19 instructions).
- Tech: `spring-boot-starter-oauth2-resource-server` replaces `jjwt` in the gateway pom (version BOM-managed → `UNKNOWN — REQUIRES SOURCE REVIEW`); Istio manifests are unpinned (`UNKNOWN — REQUIRES SOURCE REVIEW`). Vault appears only in comments as a Session-21 production note — no Vault configuration or dependency exists anywhere in the repository.
- Commits (reference): `fddfcd8` session-20-21. (main: `8f37f52`.) Own commit: 13 files, +697/−89.
- Tests: none added.
Changed: `git diff --stat 4dd0f94 fddfcd8` (ref) = 24 files, +725/−704 → docs 8(+251/−280) · infrastructure 4(+198/−89) · services 7(+90/−302) · k8s 3(+77) · keycloak 1(+33/−2) · root 1(+76/−31). Main mirror (`29f6cb1 8f37f52`) = 24 files, +569/−621. **Own commit = 13 files, +697/−89.**
Evidence: branches `session-20-21-*`; `git diff --name-status 4dd0f94 fddfcd8`; `git show fddfcd8:infrastructure/api-gateway/pom.xml`.

### Stage 13 — session-22-23: transactional outbox + idempotency + k6 performance testing

```
  ┌────────────────────────────┐          ┌───────────────────────────────┐
  │ order-service              │          │ payment-service               │
  │  OutboxEvent               │  poll    │  IdempotencyRecord            │
  │  OutboxRepository          │─@1s────▶ Kafka                          │
  │  OutboxPublisher (@Scheduled)│        │  IdempotencyRepository        │
  └────────────────────────────┘          │  PaymentController (idempotency key)
                                          └───────────────────────────────┘
  k6/  smoke-test.js (1 VU) · order-load-test.js (5→10→0 VUs) · stress-test.js (5→20→40→60 VUs)
```

- Components: + `k6/{smoke-test.js, order-load-test.js, stress-test.js}`; order-service `OutboxEvent` (`@Table("outbox_events")`), `OutboxPublisher` (`@Scheduled` fixedDelay 1000 ms), `OutboxRepository`; payment-service `IdempotencyRecord`, `IdempotencyRepository`, `PaymentController` (modified); docs labs 22/23 + trainer 22/23.
- Compose: equals the sessions 1-8 base blob `a475b7fe` (unchanged).
- Tech: no new libraries (no pom changes in this commit); k6 version is not pinned in the repository (`UNKNOWN — REQUIRES SOURCE REVIEW`). k6 scenarios: smoke = 1 VU/10 s GET `/api/v1/products`, p95 < 500 ms, failed < 1%; order-load = staged 5→10→0 VUs POST `/api/orders` using a `TEST_JWT` Keycloak access token env var, p95 < 800 ms / p99 < 2 000 ms / errors < 5%; stress = ramp 5→20→40→60 VUs, saturates Bulkhead (max 10) → TimeLimiter (2 s) → CircuitBreaker (50%), diagnose via Zipkin :9411.
- Commits (reference): `18b3b34` session-22-23. (main: `ecae40b`.) Own commit: 13 files, +755/−18.
- Tests: none added.
- Last commit subjects on `session-22-23-wip-reference` (newest first): `18b3b34` session-22-23 · `39bb3c6` session-06-07-08 · `0ba4548` session-04: add-circuit-breaker-and-retry-on-order-payment · `8cc3260` update JwtAuthFilter · `79d994b` remove duplicated folder reference · `06006d4` fix: use MockServerHttpRequest instead of ServerRequest · `f68c13b` session-03: add-jwt-auth-filter-and-rate-limiting · `398c4a2` fix: update text spring -boot-starter-web · `c410931` update LoggingFilterTest · `6654af8` update repo url.
Changed: `git diff --stat fddfcd8 18b3b34` (ref) = 26 files, +844/−715 → docs 8(+279/−251) · k6 3(+176) · services 7(+300/−108) · keycloak 1(−81) · k8s 3(−77) · infrastructure 4(+89/−198). Main mirror (`8f37f52 ecae40b`) = 26 files, +782/−554. **Own commit = 13 files, +755/−18.**
Evidence: branches `session-22-23-*`; `git show --stat 18b3b34`; `git diff --stat fddfcd8 18b3b34`; `git show 18b3b34:k6/smoke-test.js`.

## Final platform state (session-22-23-wip-reference)

Tip `18b3b34`; 146 tracked files. **Critical caveat:** this branch is a fragment forked from the sessions-1-8 snapshot, so the final tree contains sessions 1-8 + session 22-23 content only. `Dockerfile`s, `k8s/`, `helm/`, `observability/`, `keycloak/` and `services/notification-service` do **not** exist at this tip — they live only on their own stage branches (verified: none of these paths appear in `git ls-tree -r 18b3b34`).

```
                          ┌───────────────────────────────────────────────────────┐
   client ──▶ :8080 ────▶ │                    api-gateway                        │
                          │  JwtAuthFilter + JwtUtil (jjwt 0.11.5)                │
                          │  RequestRateLimiter (10 r/s, burst 20, ipKeyResolver) │
                          │  route: product-service → lb://PRODUCT-SERVICE        │
                          │  discovery.locator: enabled (DEV ONLY)                │
                          └──────┬──────────────────────────────────┬─────────────┘
                                 │ discovery (Eureka)               │ token bucket
                                 ▼                                  ▼
                          ┌───────────────┐                  ┌───────────────┐
                          │ eureka-server │◀── register ─────│ redis :6379   │
                          │    :8761      │                  └───────────────┘
                          └───────────────┘
                          ┌───────────────┐    native profile, classpath:/configs
                          │ config-server │    configs/api-gateway.yml · configs/product-service.yml
                          │    :8888      │    (NOT a git config-repo)
                          └───────────────┘

   ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │ product-service │   │  order-service  │   │ inventory-service│   │ payment-service  │
   │      :8081      │   │      :8082      │   │      :8084       │   │      :8083       │
   │ JPA + @Cacheable│   │ JPA + Outbox    │   │ Kafka saga       │   │ Kafka saga +     │
   │ @CacheEvict ×5  │   │ @Scheduled 1 s  │   │ handler          │   │ idempotency      │
   └────────┬────────┘   └────────┬────────┘   └────────┬─────────┘   └────────┬─────────┘
            │ JPA                 │ JPA + outbox         │ publish/consume      │ idempotency
            ▼                     ▼                      ▼                      ▼
   ┌────────────────────────────────────┐    ┌──────────────────────────────────────────┐
   │  postgres:16-alpine (:5432)        │    │ confluentinc/cp-kafka:7.6.1 (:9092)      │
   │  db microservices_pro              │    │ confluentinc/cp-zookeeper:7.6.1 (:2181)  │
   └────────────────────────────────────┘    └──────────────────────────────────────────┘

   docker-compose.yml (blob a475b7fe): postgres · redis · zookeeper · kafka   (no app containers)
   tools/jwt-generator — standalone CLI: --username (trainee) --roles (ROLE_CUSTOMER) --expiry (30m)
   k6/ — smoke-test.js · order-load-test.js · stress-test.js (run against :8080)
```

### Services and key classes (package root `com.microservices.pro.<module>`)

- `infrastructure/api-gateway` — `ApiGatewayApplication`, `config/RateLimitConfig`, `filter/JwtAuthFilter`, `filter/LoggingFilter`, `security/JwtUtil`; tests `JwtAuthFilterTest`, `LoggingFilterTest`, `JwtUtilTest`.
- `infrastructure/config-server` — `ConfigServerApplication`; `src/main/resources/application.yml` + `configs/api-gateway.yml`, `configs/product-service.yml`.
- `infrastructure/eureka-server` — `EurekaServerApplication`.
- `services/product-service` — `Product`, `ProductController`, `ProductRepository`, `ProductService` (`@Cacheable`/`@CacheEvict` ×5), `ProductServiceApplication` (`@EnableCaching`); test `ProductServiceTest`.
- `services/order-service` — `Order`, `OrderController`, `OrderRepository`, `OrderRequest`, `OrderResponse`, `OrderService`, `OrderStatus`, `OrderSagaEventHandler` (`@KafkaListener`), `OutboxEvent` (`@Table("outbox_events")`), `OutboxPublisher` (`@Scheduled`), `OutboxRepository`, `InventoryClient` (`@FeignClient`), `InventoryErrorDecoder`, `FeignJwtInterceptor`, `PaymentRequest`, `PaymentResponse`, `PaymentService`, `RetryLogger`, `StockCheckResponse`, `InsufficientStockException`, `OrderNotFoundException`, `ProductNotFoundException`, `ServiceUnavailableException`, `events/` ×8; tests `OrderSagaEventHandlerTest`, `OrderSagaTest`, `OrderServiceTest`.
- `services/payment-service` — `PaymentController`, `PaymentProcessor`, `PaymentSagaHandler` (`@KafkaListener` + `KafkaTemplate`), `IdempotencyRecord`, `IdempotencyRepository`, `PaymentException`, `PaymentRequest`, `PaymentResponse`, `PaymentServiceApplication`, `events/` ×8; test `PaymentSagaHandlerTest`.
- `services/inventory-service` — `InventoryController`, `InventorySagaHandler` (`@KafkaListener` + `KafkaTemplate`), `InventoryService`, `StockItem`, `StockCheckResponse`, `InsufficientStockException`, `InventoryServiceApplication`, `events/` ×8; tests `InventorySagaTest`, `InventoryServiceTest`.
- `tools/jwt-generator` — `JwtGeneratorApplication` (jjwt 0.11.5, default secret identical to the gateway's fallback; README states it will be replaced by Keycloak/OAuth2 in Session 20). Not a service, not in compose, not built by CI.
- `k6/` — three scripts (see Stage 13); thresholds as listed there.

### Key infrastructure configuration (verbatim facts)

- api-gateway `application.yml`: port 8080; `spring.config.import: optional:configserver:http://localhost:8888`; Redis `localhost:6379` (rate-limiter counters; comment: production Vault in Session 21); `discovery.locator.enabled: true` marked DEV ONLY + `lower-case-service-id: true`; one explicit route (`product-service` → `lb://PRODUCT-SERVICE`, `Path=/api/v1/products/**`, `StripPrefix=0`, `AddResponseHeader=X-Platform, microservices-pro`, `RequestRateLimiter`); `jwt.secret` with dev fallback; `management` exposes `health,info,gateway`.
- config-server `application.yml`: port 8888; `spring.profiles.active: native`; `spring.cloud.config.server.native.search-locations: classpath:/configs` — **file/classpath-based, not a git config-repo** (a comment explains this is deliberate; git-backed config is homework). Both config files contain only `app.source: "config-server"`.
- eureka-server `application.yml`: port 8761; `register-with-eureka: false`; `fetch-registry: false`; `enable-self-preservation: false` (DEV ONLY comments).
- `.github/workflows/` (6 files): `pr-validation.yml` — commit-message validation + test-all-modules; `session-01-validation.yml` — product-service tests + eureka/config compile; `session-02-validation.yml` — gateway tests + guard failing if `spring-boot-starter-web` is added to the gateway; `session-03-validation.yml` — same guard + JWT tests (jwt-generator deliberately not built); `session-04-05-validation.yml` — order resilience + payment build; `session-06-07-08-validation.yml` — order Feign + saga + inventory tests. All use JDK 21 (temurin).
- `docs/` (28 files): `architecture/{bounded-contexts, platform-overview}.md`; `grading/grading-rubric.md`; `labs/` 11 files (sessions 01, 02, 03-jwt-testing, 03-lab-2b, 04, 05, 06, 07, 08, 22, 23); `setup/{github-workflow, local-setup, troubleshooting}.md`; `trainer/` 11 files.

## Technology versions over time

| Technology | Version | First appears |
| --- | --- | --- |
| Java | 21 | session-01-02 (all modules, all stages) |
| Spring Boot (parent) | 3.3.4 | session-01-02 (constant thereafter; no root aggregator pom exists) |
| Spring Cloud BOM | 2023.0.3 | session-01-02 (constant thereafter) |
| Spring Cloud Gateway (WebFlux) | via Cloud BOM | session-01-02/02 |
| Netflix Eureka Server/Client, Spring Cloud Config (native) | via Cloud BOM | session-01-02 |
| PostgreSQL (container) | postgres:16-alpine | session-01-02 |
| jjwt (api/impl/jackson) | 0.11.5 | session-03 |
| Redis (container) | redis:7-alpine | session-03 |
| Resilience4j (spring-boot3) | BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | session-04 |
| Spring Kafka | Boot-BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | session-06-07-08 |
| OpenFeign | via Cloud BOM | session-06-07-08 |
| Kafka / ZooKeeper (containers) | confluentinc/cp-kafka:7.6.1 · cp-zookeeper:7.6.1 | session-06-07-08 |
| Dockerfile runtime (app containers) | maven:3.9-eclipse-temurin-21 → eclipse-temurin:21-jre-jammy | session-09 |
| Testcontainers | 1.19.8 | session-10-11 |
| Pact (JVM, consumer+provider) | 4.6.7 | session-10-11 |
| spring-cloud-contract-wiremock | via Cloud BOM | session-10-11 |
| Helm chart schema | apiVersion v2 (chart 0.1.0, appVersion 1.0.0) | session-15-16 |
| Micrometer Tracing (Brave) + zipkin-reporter-brave + micrometer-registry-prometheus | Boot-BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | session-17 |
| logstash-logback-encoder | 7.4 | session-17 |
| Zipkin / Prometheus / Grafana (containers) | openzipkin/zipkin:3 · prom/prometheus:v2.51.0 · grafana/grafana:10.4.2 | session-17 |
| Keycloak (container) | quay.io/keycloak/keycloak:24.0.4 | session-18-19 |
| Spring Security (OAuth2 Resource Server) | via `spring-boot-starter-oauth2-resource-server`, BOM-managed — replaces jjwt in the gateway | session-20-21 |
| Istio (manifests only) / ArgoCD (Application manifest only) | not pinned in repo — `UNKNOWN — REQUIRES SOURCE REVIEW` | session-20-21 / session-13-14 |
| k6 (scripts only) | not pinned in repo — `UNKNOWN — REQUIRES SOURCE REVIEW` | session-22-23 |
| CI runner JDK | 21 (temurin) | session-01-02 workflows |

## UNKNOWNs / open questions

1. `UNKNOWN — REQUIRES SOURCE REVIEW` — resolved concrete versions of every BOM-managed dependency (Resilience4j, spring-kafka, Micrometer Tracing/registry, oauth2-resource-server, spring-cloud-contract-wiremock); the repository only pins what is listed above.
2. `UNKNOWN — REQUIRES SOURCE REVIEW` — provenance of the parallel rewritten commit copies (identical trees, different SHAs/parents, e.g. `84ad7e3` vs `8cc3260`, `2c2f623` vs `0ba4548`). The repository history was clearly re-created/rewritten; why and in which order is not recorded.
3. `UNKNOWN — REQUIRES SOURCE REVIEW` — whether a single fully cumulative branch (containing the session-09…12 + 13-14…22-23 artifacts together) exists anywhere outside this clone. No such branch exists in this clone; the "complete platform" only exists as the union of stage branches.
4. `UNKNOWN — REQUIRES SOURCE REVIEW` — whether the late fragment branches (13-14 onward) are a deliberate teaching device (each stage checked out as "snapshot + just this session's diff") or a repository-organisation artifact. Evidence (single commits, "add this block" compose snippets) is consistent with deliberate staging but does not prove it.
5. Vault (Session 21): referenced only in code comments (api-gateway/product-service `application.yml`, `docs/labs/session-03-jwt-testing.md`) as a production note. No dependency, config, compose service or code exists — effectively not implemented in the repository.
6. Istio version, ArgoCD version, Helm CLI version and k6 version are not pinned anywhere in the repository.
7. `UNKNOWN — REQUIRES SOURCE REVIEW` — concrete lab-by-lab mapping between the 24-session curriculum and the branch stage names beyond what the docs filenames show (e.g. `session-22-lab-18` even though the branch is named session-22-23).
8. Branch-name typo (`session-09-wip-referenc`) — verify against the remote naming convention before any automation depends on it.
