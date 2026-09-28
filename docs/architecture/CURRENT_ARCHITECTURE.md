# CURRENT ARCHITECTURE � Canonical Visual Mental Model

> **Canonical file (master prompt �9.1).** This is the single source of truth for "what the platform looks like right now".
> Update rules: full redraw at every lab milestone; milestone header at the top; never silently edit � each update is its own commit (docs: update architecture for lab NN).
> Statuses used in this repo: PASS / NOT VERIFIED / BLOCKED / NOT REVIEWED.

## Milestone 10 � After Lab 09A (Session 10 complete: Unit & Integration Tests)

**Date:** 2026-09-28
**State:** 7 containerized Spring Boot services, 3 containerized infrastructure services.

`
                        +---------------------------------------------+
                        �       TRAINING PLATFORM � MILESTONE 10      �
                        �           "test-driven platform"            �
                        +---------------------------------------------+
                                  [ DOCKER NETWORK: platform-net ]

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �    (container)    �               �    :6379     �
            /api/orders         �                   �               � (Rate Limiter�
                                �                   �               �  Token Bucket�
                                �                   � ?------------ +--------------+
                                +-------------------+                      �
                                          �                                �
                            +--------------------------+                   �
                            ?                          ?                   �
                     product-service             order-service             �
                       (container)                (container)              �
                      (Spring Cache) --------------------------------------+
                    (JPA / Postgres)            (Resilience4j stack)
                            �                   (KafkaProducer)
                            �                   (SagaEventHandler)
                            ?                          �
                     +--------------+                  �
                     �   postgres   �                  �
                     �    :5432     �                  �
                     +--------------+                  �
                                                       �
                           +---------------------------�
                           ?                           ?
                     (Apache Kafka)            inventory-service
                      :9092/:29092                (container)
                           ?                    (SagaEventHandler)
                           �                           ?
                           +---------------------------�
                                                       ?
                                                payment-service
                                                  (container)
                                                (SagaEventHandler)

     [ config-server:8888 (container) ]      [ eureka-server:8761 (container) ]
`

**What changed in this milestone:** No architectural changes. Testing layers introduced: @WebMvcTest for web layer isolation, @ParameterizedTest for data-driven testing, and @SpringBootTest combined with TestContainers for ephemeral database integration testing.
## Milestone 9 � After Lab 08A (Session 9 complete: Dockerize Platform)

**Date:** 2026-09-28
**State:** 7 containerized Spring Boot services, 3 containerized infrastructure services.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 9      �
                        �           "containerized platform"          �
                        +---------------------------------------------+
                                  [ DOCKER NETWORK: platform-net ]

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �    (container)    �               �    :6379     �
            /api/orders         �                   �               � (Rate Limiter�
                                �                   �               �  Token Bucket�
                                �                   � ?------------ +--------------+
                                +-------------------+                      �
                                          �                                �
                            +--------------------------+                   �
                            ?                          ?                   �
                     product-service             order-service             �
                       (container)                (container)              �
                      (Spring Cache) --------------------------------------+
                    (JPA / Postgres)            (Resilience4j stack)
                            �                   (KafkaProducer)
                            �                   (SagaEventHandler)
                            ?                          �
                     +--------------+                  �
                     �   postgres   �                  �
                     �    :5432     �                  �
                     +--------------+                  �
                                                       �
                           +---------------------------�
                           ?                           ?
                     (Apache Kafka)            inventory-service
                      :9092/:29092                (container)
                           ?                    (SagaEventHandler)
                           �                           ?
                           +---------------------------�
                                                       ?
                                                payment-service
                                                  (container)
                                                (SagaEventHandler)

     [ config-server:8888 (container) ]      [ eureka-server:8761 (container) ]
`

**What changed in this milestone:** All 7 Spring Boot services have been containerized using multi-stage Dockerfiles. They run as a non-root user (1001:1001) based on eclipse-temurin:21-jre-jammy. Health checks and dependency conditions have been configured in docker-compose.yml, bringing the entire platform under full Docker lifecycle management.
## Milestone 8 � After Lab 06A (Session 8 complete: Redis Caching)

**Date:** 2026-09-28
**State:** 8 runtime members live. Redis caching added to Product Service.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 8      �
                        �               "redis caching"               �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
            /api/orders         � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   � ?------------ +--------------+
                                +-------------------+                      �
                                          �                                �
                            +--------------------------+                   �
                            ?                          ?                   �
                     product-service             order-service             �
                         :8081                       :8082                 �
                      (Spring Cache) --------------------------------------+
                    (JPA / Postgres)            (Resilience4j stack)
                            �                   (KafkaProducer)
                            �                   (SagaEventHandler)
                            ?                          �
                     +--------------+                  �
                     �   postgres   �                  �
                     �    :5432     �                  �
                     +--------------+                  �
                                                       �
                           +---------------------------�
                           ?                           ?
                     (Apache Kafka)            inventory-service
                      :9092/:29092                   :8084
                           ?                    (SagaEventHandler)
                           �                           ?
                           +---------------------------�
                                                       ?
                                                payment-service
                                                     :8083
                                                (SagaEventHandler)
`

**What changed in this milestone:** product-service was upgraded from an in-memory Map to use Spring Data JPA backed by postgres. It also gained a caching layer using @Cacheable backed by 
edis, significantly reducing database load for read operations.

## Milestone 7 � After Lab 05A (Session 7 complete: Choreography Saga)

**Date:** 2026-09-28
**State:** 8 runtime members live (Kafka added). Distributed transaction via Choreography Saga.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 7      �
                        �             "choreography saga"             �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
            /api/orders         � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   �               +--------------+
                                +-------------------+
                                          �
                            +--------------------------+
                            ?                          ?
                     product-service             order-service
                         :8081                       :8082
                    (In-memory CRUD)            (Resilience4j stack)
                                                (KafkaProducer)
                                                (SagaEventHandler)
                                                       �
                           +---------------------------�
                           ?                           ?
                     (Apache Kafka)            inventory-service
                      :9092/:29092                   :8084
                           ?                    (SagaEventHandler)
                           �                           ?
                           +---------------------------�
                                                       ?
                                                payment-service
                                                     :8083
                                                (SagaEventHandler)
`

**What changed in this milestone:** net-new � kafka added to docker-compose.
Saga pattern implemented. order-service publishes OrderPlacedEvent instead of synchronously charging payment. inventory-service consumes it, reserves stock, and publishes InventoryReservedEvent. payment-service consumes it, charges payment, and publishes PaymentCompletedEvent (or PaymentFailedEvent). On failure, inventory-service releases stock.
(Note: OpenFeign sync pre-check remains active before Saga starts).

## Milestone 6 � After Lab 04A (Session 6 complete: Inventory & OpenFeign)

**Date:** 2026-09-28
**State:** 7 runtime members live. Order Service synchronously checks Inventory via OpenFeign before processing.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 6      �
                        �      "synchronous service communication"    �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
            /api/orders         � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   �               +--------------+
                                +-------------------+
                                          �
                            +--------------------------+
                            ?                          ?
                     product-service             order-service
                         :8081                       :8082
                    (In-memory CRUD)            (Resilience4j stack)
                                                       �
                                                 (OpenFeign Client)
                                                 (JWT Interceptor)
                                                       �
                                                       ?
                                               inventory-service
                                                     :8084
                                                (In-memory Store)
`

**What changed in this milestone:** net-new � inventory-service added.
order-service updated to use spring-cloud-starter-openfeign. It now synchronously calls GET /api/v1/inventory/check before processing a payment. If stock is unavailable, it returns REJECTED immediately. A FeignJwtInterceptor was added to propagate the JWT token down to inventory-service.

## Milestone 5 � After Lab 03B (Session 5 complete: Full Resilience Stack)

**Date:** 2026-09-28
**State:** 6 runtime members live. Order Service uses full Resilience4j stack.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 5      �
                        �      "full resilience stack applied"        �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
            /api/orders         � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   �               +--------------+
                                +-------------------+
                                          �
                            +--------------------------+
                            ?                          ?
                     product-service             order-service
                         :8081                       :8082
                    (In-memory CRUD)            (Resilience4j stack:)
                                                (@Bulkhead)
                                                (@TimeLimiter)
                                                (@CircuitBreaker)
                                                (@Retry)
                                                       �
                                                 (local bean call
                                                  to simulate HTTP)
                                                       �
                                                       ?
                                             (PaymentService bean)
`

**What changed in this milestone:** net-new � order-service added @Bulkhead (max 10 concurrent calls) and @TimeLimiter (2s timeout).
The createOrderAsync method now returns a CompletableFuture to support TimeLimiter aborts.
Verified: Order Service returns QUEUED on bulkhead full and PENDING on timeout.

## Milestone 4 � After Lab 03A (Session 4 complete: Circuit Breaker & Retry)

**Date:** 2026-09-28
**State:** 6 runtime members live. Order Service added with Resilience4j circuit breaking.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 4      �
                        �       "resilience against failure"          �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
            /api/orders         � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   �               +--------------+
                                +-------------------+
                                          �
                            +--------------------------+
                            ?                          ?
                     product-service             order-service
                         :8081                       :8082
                    (In-memory CRUD)            (Resilience4j)
                                                (CircuitBreaker,
                                                 Retry, Fallback)
                                                       �
                                                 (local bean call
                                                  to simulate HTTP)
                                                       �
                                                       ?
                                             (PaymentService bean)
`

**What changed in this milestone:** net-new � order-service (:8082) and payment-service scaffolding.
order-service exposes POST /api/orders which calls a local PaymentService bean with an artificial 50% failure rate.
Annotated with Resilience4j @CircuitBreaker and @Retry to handle failures smoothly via fallback.
(Note: Code also pre-includes async structure for Session 5).
Verified: Order Service correctly falls back to returning PENDING orders when Payment fails continuously.

## Milestone 3 � After Lab 02B (Session 3 complete: Gateway Security & Rate Limiting)

**Date:** 2026-09-28
**State:** 5 runtime members live. API Gateway secured with JWT and Rate Limiting. Redis added.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 3      �
                        �     "secured entry point + rate limiting"   �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+ ?------------ +--------------+
               :8080            �   api-gateway     �               �    redis     �
            /api/v1/products    �      :8080        �               �    :6379     �
                                � (JwtAuthFilter)   �               � (Rate Limiter�
                                � (RequestRateLim.) �               �  Token Bucket�
                                � (LoggingFilter)   �               +--------------+
                                +-------------------+
                                          �
                                          ?
                                   product-service
                                      :8081
                                (In-memory CRUD)
                                          �
    config import -------------------------------------------------- register (lb://)
                             �                          �
                             ?                          ?
                     +----------------+         +---------------+
                     � config-server  �         � eureka-server �
                     �     :8888      �         �     :8761     �
                     +----------------+         +---------------+
`

**What changed in this milestone:** net-new � 
edis (:6379, via docker-compose).
Added JwtAuthFilter to validate JWT Bearer tokens and extract roles/user ids for non-public routes.
Added RequestRateLimiter via Redis with Token Bucket (10 replenish rate, 20 burst).
Verified: /api/v1/products POST returns 401 without token, 429 when rate limit exceeded.

**Observation carried forward:** Product-service registers on a VirtualBox IP. Gateway correctly resolves it.
## Milestone 2 � After Lab 02A (Session 2 complete: API Gateway Routing)

**Date:** 2026-09-28
**State:** 4 runtime members live. API Gateway added as the single entry point.

`
                        +---------------------------------------------+
                        �        TRAINING PLATFORM � MILESTONE 2      �
                        �       "single entry point + routing"        �
                        +---------------------------------------------+

                                         lb://PRODUCT-SERVICE
             client ----------? +-------------------+
               :8080            �   api-gateway     �
            /api/v1/products    �      :8080        �
                                � (GlobalFilter:    �
                                �  LoggingFilter)   �
                                � (StripPrefix=0)   �
                                +-------------------+
                                          �
                                          ?
                                   product-service
                                      :8081
                                (In-memory CRUD)
                                          �
    config import -------------------------------------------------- register (lb://)
                             �                          �
                             ?                          ?
                     +----------------+         +---------------+
                     � config-server  �         � eureka-server �
                     �     :8888      �         �     :8761     �
                     +----------------+         +---------------+
`

**What changed in this milestone:** net-new � pi-gateway (:8080, reactive WebFlux stack).
Added path routing for /api/v1/products/** forwarding via lb://PRODUCT-SERVICE (Eureka load balancer).
Added LoggingFilter for pre/post logging. Added X-Platform header in responses.
Verified: Gateway routes traffic properly to Product Service.

**Observation carried forward:** Product-service registers on a VirtualBox IP. Gateway correctly resolves it.

## Milestone 1 — After Lab 01 (Session 1 complete: config + discovery foundations)

**Date:** 2026-09-28
**State:** 3 runtime members live, verified by curl + registry query. No gateway, no persistence, no messaging yet.

```
                        ┌─────────────────────────────────────────────┐
                        │        TRAINING PLATFORM — MILESTONE 1      │
                        │       "a service that knows where it is"    │
                        └─────────────────────────────────────────────┘

                                          config import
                     ┌────────────────────────────────────────────┐
                     │                                            ▼
              ┌──────────────┐                          ┌────────────────────┐
   client ──▶ │  product-    │                          │   config-server    │
     :8081    │  service     │                          │        :8888       │
   (direct)   │  :8081       │                          │  native profile    │
              │              │                          │  classpath:/configs│
              │ Product      │                          │  └ product-service │
              │  record      │                          │      .yml          │
              │ ProductService│                         │    (app.source =   │
              │  Concurrent- │                          │     config-server) │
              │  HashMap     │                          └────────────────────┘
              │ ProductController
              │  GET/POST/DELETE                      register + heartbeat
              │  /api/v1/products        │                    every 30 s
              └───────────┬──────────────┘
                          └──────────────────▶ ┌────────────────────┐
                                               │   eureka-server    │
                                               │       :8761        │
                                               │  no self-register  │
                                               │  no self-preserv.  │
                                               │  registry:         │
                                               │   PRODUCT-SERVICE  │
                                               │        UP          │
                                               └────────────────────┘

   docker-compose (lab-01 state):
     postgres:16-alpine   :5432   healthy — STARTED but NOT YET USED by any service
     (redis :6379 → session 3 · kafka :9092 → session 7 · zipkin/prometheus/grafana → session 17)
     (api-gateway :8080 → session 2 · Dockerfiles for app containers → session 9)

   NOT PRESENT AT THIS MILESTONE (deliberate — Historical State Rule):
     ✗ api-gateway        ✗ persistence (JPA)      ✗ Redis cache
     ✗ Kafka / saga       ✗ resilience (CircuitBreaker/Bulkhead/Retry)
     ✗ security (JWT)     ✗ service discovery *consumers* (nobody calls product-service yet)
```

**What changed in this milestone:** net-new — `config-server` (:8888, native backend serving
`configs/product-service.yml`), `eureka-server` (:8761, `register-with-eureka: false`,
`enable-self-preservation: false` DEV ONLY), `product-service` (:8081, in-memory CRUD over
`/api/v1/products`), `docker-compose.yml` (postgres only). Verified: config pulled by the client
(`ConfigServerConfigDataLoader: Fetching config from server at http://localhost:8888`), registration
accepted (`Registered instance PRODUCT-SERVICE/localhost:product-service:8081 with status UP`),
all 4 endpoints returning 200/201/404/204 as specified, 8 unit tests green.

**Observation carried forward:** product-service registers as `192.168.56.1:8081`
(VirtualBox host-only adapter, `prefer-ip-address: true`). Reachable from the host (HTTP 200), so
Session 2's `lb://PRODUCT-SERVICE` route should resolve — verify this first if gateway routing fails.

## Milestone 0 — Pre-Lab-01 (reconnaissance complete, no code written)

**Date:** 2026-09-28
**State:** nothing built yet. Empty platform skeleton. This is the starting line.

```
                        ┌─────────────────────────────────────────────┐
                        │        TRAINING PLATFORM — MILESTONE 0      │
                        │                 (empty)                     │
                        └─────────────────────────────────────────────┘

   Nothing exists yet.

   Will be created by Lab 1 (Session 1):
     services/product-service      :8081   ──┐
     infrastructure/config-server  :8888   ──┤  all three register with
     infrastructure/eureka-server  :8761   ──┘  each other's discovery

   Infrastructure containers available for Lab 1 (Docker only):
     postgres:16-alpine            :5432      (healthy via `docker compose ps`)
     redis:7-alpine                :6379      (first used by Lab 2B)
     kafka / zookeeper             :9092      (first used by Lab 5A)
```

## Target end state — after Phase 3 (reference: ARCHITECTURE_EVOLUTION.md)

This is where the platform is going. It is **not** permission to build ahead (Historical State Rule):

```
                                  ┌────────────────────┐
              client ───────────▶ │  api-gateway :8080 │◀── Keycloak :8090 (S19-20)
                                  │  JWT ├ rate-limit  │
                                  └─────┬──────────────┘
             ┌──────────────┬───────────┼───────────┬──────────────┐
             ▼              ▼           ▼           ▼              ▼
     product-service  order-service  payment-  inventory-   notification-
        :8081            :8082      service    service       service :8085
     (Redis cache S8)  (Saga,      :8083      :8084         (Kafka consumer)
                        Outbox S22) (idem. S22)
             │              │           │           │
             └──────────────┴─────┬─────┴───────────┘
                                  │
                  ┌───────────────┼───────────────────────────┐
                  ▼               ▼                           ▼
           Kafka :9092      Eureka :8761              Config Server :8888
         (topics: order-    (discovery)               (centralized config)
          events, payment-
          events, inventory-
          events)
                                  │
        ┌─────────────────────────┼───────────────────────────────┐
        ▼                         ▼                               ▼
  Observability (S17)      Kubernetes (S15-16)              Service Mesh (S21)
  Zipkin :9411             Deployments/Services/Probes      Istio + mTLS
  Prometheus :9090         HPA, ConfigMaps, Secrets         (peer auth)
  Grafana :3000
                                  │
                                  ▼
                        CI/CD (S13) → GitOps/ArgoCD (S14)
                        GitHub Actions pipelines → cluster sync
```

## Milestone history

| Milestone | Lab | Date | What changed |
|---|---|---|---|
| 0 | — | 2026-09-28 | Reconnaissance complete. Platform empty. Waiting for Lab 1 confirmation. |
| 1 | 01 | 2026-09-28 | config-server :8888 (native) + eureka-server :8761 + product-service :8081 (in-memory CRUD) + compose(postgres). Config import and service registration verified. |
| 2 | 02A | 2026-09-28 | api-gateway :8080. Configured path route /api/v1/products/** to lb://PRODUCT-SERVICE. Added LoggingFilter and X-Platform response header. |
| 3 | 02B | 2026-09-28 | Added Redis :6379 to compose. Added JwtAuthFilter for authentication and RequestRateLimiter using Redis token bucket. |
| 4 | 03A | 2026-09-28 | Added order-service and payment-service. Implemented Circuit Breaker and Retry on Order->Payment call. |
| 5 | 03B | 2026-09-28 | Added Bulkhead and TimeLimiter to order-service. Changed order processing to CompletableFuture for TimeLimiter support. |
| 6 | 04A | 2026-09-28 | Added inventory-service. Configured OpenFeign in order-service to synchronously check stock before payment. |
| 7 | 05A | 2026-09-28 | Added Kafka to compose. Implemented Choreography Saga across Order, Inventory, and Payment services. |
| 8 | 06A | 2026-09-28 | Upgraded product-service to use Postgres and Redis caching. |
| 9 | 08A | 2026-09-28 | Containerized all 7 services using multi-stage Dockerfiles and docker-compose. |
| 10 | 09A | 2026-09-28 | Added @WebMvcTest, @ParameterizedTest, and TestContainers to product-service. |
| 11 | 09B | 2026-09-28 | Implemented Pact consumer/provider contracts and WireMock for order-service. |
| 12 | 10A | 2026-09-28 | Saga Orchestration with State Machine across Order, Inventory, and Payment services. |
| 13 | 11A | 2026-09-28 | CI/CD pipelines with GitHub Actions. Notification Service added to handle payment-events. |
| 14 | 11B | 2026-09-28 | Kubernetes manifests and ArgoCD application for GitOps deployments of product-service. |
| 15 | 12A | 2026-09-28 | Kubernetes Core concepts applied: Secrets, Resource Requests/Limits, and Liveness/Readiness probes. |
| 16 | 12B | 2026-09-28 | Helm chart created for product-service, HPA configured, and RBAC applied for least-privilege security. |
| 17 | 13A | 2026-09-28 | Observability stack added: Zipkin (tracing), Prometheus (metrics), Grafana (dashboards). Structured JSON logging enabled. |
| 18 | 13B | 2026-09-28 | CQRS Command/Query split implemented in product-service. |
| 19 | 15 | 2026-09-28 | Keycloak OIDC Provider added for centralized identity and access management. |
| 20 | 16 | 2026-09-28 | API Gateway migrated to OAuth2 Resource Server. Client Credentials configured for inter-service calls. |
| 21 | 17 | 2026-09-28 | Istio Service Mesh enabled. Strict mTLS enforced, VirtualService/DestinationRule added for 80/20 Canary routing. |

## How this file is used

- **Before each lab** (master prompt §13 before-lab briefing): paste the current block, mark the components the lab touches, show what will be added.
- **After each lab** (master prompt §17 LAB COMPLETE report): redraw with the new component(s) in place and commit the update.
- This file must always render as valid ASCII in a monospace viewer — no Unicode box-drawing beyond what the reference docs already use, no images.
