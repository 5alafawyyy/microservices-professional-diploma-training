# Technology Matrix

> Version facts quoted from `pom.xml`, `docker-compose.yml` and workflow files of the reference repository only. BOM-managed dependencies whose concrete version is not written in the repository are marked `UNKNOWN — REQUIRES SOURCE REVIEW` (they resolve from the imported BOM at build time).

## Runtime & build

| Technology | Version | First appears | How pinned | Evidence |
| --- | --- | --- | --- | --- |
| Java | 21 | Session 01 | `java.version` property in every module pom | module `pom.xml` |
| Spring Boot | 3.3.4 | Session 01 | `spring-boot-starter-parent` parent per module (no root aggregator pom exists) | module `pom.xml` |
| Spring Cloud | 2023.0.3 | Session 01 | `spring-cloud-dependencies` BOM import | module `pom.xml` |
| Maven (build) | 3.9-eclipse-temurin-21 (Docker builder image) | Session 09 | Dockerfile | `services/*/Dockerfile` |
| Maven (local/CI) | 3.9+ required | Session 01 | documented requirement | `docs/setup/local-setup.md` |
| JDK runtime (containers) | eclipse-temurin:21-jre-jammy | Session 09 | Dockerfile | `services/*/Dockerfile` |
| CI runner JDK | 21 (temurin) | Session 01 | workflow `actions/setup-java` | `.github/workflows/*.yml` |

## Spring Cloud components (Cloud BOM 2023.0.3)

| Component | First appears | Notes |
| --- | --- | --- |
| Netflix Eureka Server / Client | Session 01 | `spring-cloud-starter-netflix-eureka-server/client`; `enable-self-preservation: false` DEV ONLY |
| Spring Cloud Config Server | Session 01 | **native** profile with `classpath:/configs` — file-based, deliberately not a git config-repo |
| Spring Cloud Gateway (WebFlux) | Session 02 | gateway pom must NOT contain `spring-boot-starter-web` |
| OpenFeign | Session 06 | `spring-cloud-starter-openfeign` + `@EnableFeignClients` |
| spring-cloud-contract-wiremock | Session 11 | test scope |

## Resilience

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| Resilience4j `spring-boot3` + `spring-boot-starter-aop` | BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 04 | annotations silently ignored without the AOP starter; order-service only |
| CircuitBreaker config | `sliding-window-size 10`, `failure-rate-threshold 50`, `wait-duration-in-open-state 5s` | Session 04 | application.yml |
| Retry config | `max-attempts 3`, `wait-duration 500ms`, exponential backoff ×2 | Session 04 | application.yml |
| Bulkhead config | `max-concurrent-calls 10`, `max-wait-duration 0ms` | Session 05 | semaphore type |
| TimeLimiter config | `timeout-duration 2s`, `cancel-running-future true` | Session 05 | async `CompletableFuture` |

## Messaging

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| Spring Kafka | Boot-BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 07 | `spring-kafka` starter |
| Apache Kafka (container) | confluentinc/cp-kafka:7.6.1 | Session 07 | compose service `kafka` :9092 |
| ZooKeeper (container) | confluentinc/cp-zookeeper:7.6.1 | Session 07 | compose service `zookeeper` :2181 |
| Topics | `order-events`, `inventory-events`, `payment-events` | Session 07 | JSON serdes; `spring.json.trusted.packages` required |
| Retry topics / DLT | `payment-events-retry-0/1`, `payment-events-dlt` | Session 13 | `@RetryableTopic` in notification-service |

## Data & caching

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| PostgreSQL (container) | postgres:16-alpine | Session 01 | db `microservices_pro`; `ddl-auto: update` DEV ONLY |
| Spring Data JPA | Boot BOM | Session 06-08 stage (product + order) | `Product` becomes `@Entity` |
| Redis (container) | redis:7-alpine | Session 03 | rate-limiter store (S3) + response cache (S8) |
| Spring Cache abstraction | Boot BOM | Session 08 | `spring.cache.type: redis`, `spring.cache.redis.time-to-live: 300000` |
| Outbox table | `outbox_events` | Session 22 | order-service, `@Scheduled` publisher (fixedDelay 1000 ms) |
| Idempotency store | `IdempotencyRecord` | Session 22 | payment-service, `Idempotency-Key` header |

## Security

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| jjwt (api/impl/jackson) | 0.11.5 | Session 03 | gateway + `tools/jwt-generator`; shared dev secret fallback |
| Keycloak (container) | quay.io/keycloak/keycloak:24.0.4 | Session 19 | `start-dev`, :8180→8080, `keycloak/realm-export.json` |
| Spring Security OAuth2 Resource Server | Boot-BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 20 | **replaces** jjwt in the gateway; retires `JwtAuthFilter` |
| Istio mTLS (`PeerAuthentication` STRICT) | unpinned — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 21 | manifests under `k8s/istio/` |

## Observability

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| Micrometer Tracing (Brave bridge) + zipkin-reporter-brave + micrometer-registry-prometheus | Boot-BOM-managed — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 17 | order + product service |
| Zipkin (container) | openzipkin/zipkin:3 | Session 17 | :9411 |
| Prometheus (container) | prom/prometheus:v2.51.0 | Session 17 | :9090, `observability/prometheus.yml` |
| Grafana (container) | grafana/grafana:10.4.2 | Session 17 | :3000, admin/admin, Prometheus datasource |
| logstash-logback-encoder | 7.4 | Session 17 | pinned; JSON logs with traceId |

## Testing

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| JUnit 5 / Mockito | Boot BOM | Session 01 | unit tests from Lab 1 onward |
| Testcontainers | 1.19.8 (`testcontainers-bom`) | Session 10 | product-service integration test, real postgres:16 |
| Pact (JVM) | 4.6.7 | Session 11 | consumer (order) + provider (inventory) |
| WireMock (`spring-cloud-contract-wiremock`) | Cloud BOM | Session 11 | chaos/fault injection for payment calls |

## Containers & orchestration

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| Docker Compose file | `platform-net` network, images `microservices-pro/<module>:local` | Session 09 | 7 app containers + 4 infra |
| Kubernetes manifests | unpinned kubectl/cluster | Session 15 | `k8s/product-service/*`, `k8s/istio/*` |
| Helm | chart `apiVersion: v2`, chart `version 0.1.0`, `appVersion "1.0.0"`; CLI version unpinned — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 16 | `helm/product-service-chart` |
| ArgoCD | Application CRD manifest only; version unpinned — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 14 | `k8s/argocd/product-service-app.yaml` |

## Performance

| Technology | Version | First appears | Notes |
| --- | --- | --- | --- |
| k6 | unpinned — `UNKNOWN — REQUIRES SOURCE REVIEW` | Session 23 | smoke (1 VU), load (5→10→0 VUs), stress (5→20→40→60 VUs) |

## Tooling not in any pom

| Tool | Purpose | First appears |
| --- | --- | --- |
| `tools/jwt-generator` (own Maven project, jjwt 0.11.5) | standalone CLI issuing dev JWTs (username/roles/expiry); not in compose, not built by CI; **retired in Session 20** | Session 03 |
| `k6/` scripts | performance scenarios | Session 23 |
| `keycloak/realm-export.json` | realm/client/user/role definitions | Session 19 |

## Summary of unresolved versions

| Dependency | Why unresolved |
| --- | --- |
| Resilience4j, Spring Kafka, Micrometer Tracing + Prometheus registry, OAuth2 Resource Server, WireMock | BOM-managed; the repo never writes the concrete resolved version |
| Istio, ArgoCD, Helm CLI, k6 | tools/CLIs not pinned in any file |
| Postgres/Redis/Kafka/Keycloak/Zipkin/Prometheus/Grafana container versions | pinned — listed above |

Resolution plan: at lab time, capture `mvn dependency:tree` output for BOM-managed versions and `tool version` output for CLIs, then record the observed values in this matrix (they must come from the actual build, not from guessing).
