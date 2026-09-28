# Phase 3 Roadmap — Advanced & Enterprise (Sessions 17–24)

> Goal: production-grade concerns — observability, CQRS, real identity/security, service mesh, reliability patterns (outbox/idempotency), performance engineering, and the second architecture clinic.
> Source framing: kickoff deck ("Phase 3 — Advanced & Enterprise, S17–24") + deck folder `Phase3/`.

## Phase outcome

```
   client ──OAuth2 (Keycloak realm)──▶ api-gateway (resource server, roles from JWT)
                                             │
                        ┌────────────────────┼───────────────────────┐
                        ▼                    ▼                       ▼
                  product-service      order-service ──Feign(service token)──▶ inventory
                  CQRS: command/       outbox_events                 payment (idempotency keys)
                  query split          @Scheduled publisher
                        │                    │
                        └──── Kafka :9092 ───┘
        observability: Prometheus ◀ /actuator/prometheus · Zipkin ◀ spans · Grafana dashboards · JSON logs
        mesh: Istio sidecars · VirtualService/DestinationRule · PeerAuthentication mTLS STRICT
        performance: k6 smoke/load/stress → bottleneck findings vs Bulkhead/CB behaviour (S5)
```

## Session-by-session

### Session 17 — Observability Deep Dive

- **Concepts:** the three pillars (metrics, logs, traces), Micrometer abstraction, span propagation across services, structured JSON logging, correlating a trace with logs and dashboard spikes.
- **Build:** order- and product-service gain `ObservabilityConfig`, `logback-spring.xml`, tracing deps; `observability/prometheus.yml` + Grafana datasource; compose adds `zipkin` (:9411), `prometheus` (:9090), `grafana` (:3000, admin/admin).
- **Lab:** Lab 13 (slide-only).
- **Acceptance (reconstructed):** one HTTP call to order-service produces a Zipkin trace containing order + inventory + payment spans; Prometheus scrapes `/actuator/prometheus`; Grafana dashboard shows request rate; logs are JSON with `traceId`.
- **Checkpoint commit:** `session-17: observability` (reference wording).
- **Note:** `logstash-logback-encoder` is the one pinned version (7.4); tracing deps are BOM-managed.

### Session 18 — CQRS Pattern

- **Concepts:** command/query responsibility separation, read models/projections, eventual consistency of the read side, domain events feeding projections, cache eviction from events.
- **Build:** product-service `ProductCommandService` + `ProductQueryService` + `ProductSummaryProjection` + `ProductChangedEvent` + `ProductCacheEvictionListener` (evicts the S8 cache when a command mutates state).
- **Lab:** Lab 14 (slide-only).
- **Acceptance (reconstructed):** command path writes via command service and publishes `ProductChangedEvent`; query path serves from the projection; cache is evicted on change (no stale reads).
- **Checkpoint commit:** `session-18: cqrs` (reference wording).

### Session 19 — Security Part 1: Keycloak & OAuth2

- **Concepts:** why an external IdP replacing `jwt-generator`, realms/clients/users/roles, authorization-code flow, access vs refresh tokens, token claims.
- **Build:** Keycloak 24.0.4 container (`:8180 → 8080`, `start-dev`, admin/admin DEV ONLY) + `keycloak/realm-export.json` (realm with clients/users/roles).
- **Lab:** Lab 15 (slide-only).
- **Acceptance (reconstructed):** Keycloak admin console reachable; realm import works; a user can obtain a token in the realm; token claims match what the gateway will validate.
- **Checkpoint commit:** `session-19: keycloak-oauth2` (verify wording against deck at lab time).
- **Discrepancy to resolve at lab time:** the S23 lab doc references realm `ecommerce-platform` on `:8180`, while the S18-19 reference stage places Keycloak on `:8180` too but earlier course material says `:8090` / realm `microservices-pro`. Verify at implementation time against the deck.

### Session 20 — Security Part 2: Client Credentials, Resource Server, RBAC

- **Concepts:** OAuth2 resource server in the gateway, replacing home-made `JwtAuthFilter`/`JwtUtil` with Spring Security; roles from JWT claims; client-credentials grants for service-to-service calls; retiring the jwt-generator tool.
- **Build:** gateway `SecurityConfig` + `UserContextEnrichmentFilter` (`spring-boot-starter-oauth2-resource-server` replaces jjwt); order-service `OrderServiceTokenClient` (service tokens for Feign); updated realm export.
- **Lab:** Lab 16 (slide-only).
- **Acceptance (reconstructed):** gateway validates Keycloak-issued tokens; role-restricted endpoints behave correctly; service-to-service call carries a client-credentials token; `JwtAuthFilter`/`JwtUtil`/`tools/jwt-generator` removed or clearly retired.
- **Checkpoint commit:** `session-20: oauth2-resource-server` (verify wording against deck at lab time).

### Session 21 — Service Mesh & mTLS: Istio

- **Concepts:** sidecar proxies, control/data plane, traffic management (VirtualService routing, DestinationRule subsets), mTLS (`PeerAuthentication` STRICT), mesh observability, when a mesh is worth its cost.
- **Build:** `k8s/istio/{virtual-service-product,destination-rule-product,peer-authentication}.yaml`; apply against the S15/16 cluster.
- **Lab:** Lab 17 (slide-only).
- **Acceptance (reconstructed):** sidecar injected into product-service pods; traffic routed through VirtualService (e.g. canary split); mTLS STRICT verified (`istioctl authn tls-check` or peer cert inspection).
- **Checkpoint commit:** `session-21: istio-mtls` (verify wording against deck at lab time).
- **Prerequisites:** Istio CLI installed (`PREREQUISITES.md`); cluster from S15/16.

### Session 22 — Advanced Patterns: Outbox, Idempotency & API Versioning

- **Concepts:** dual-write problem, transactional outbox, polling publisher vs CDC/Debezium, idempotency keys, at-least-once vs exactly-once delivery, API versioning debt from Clinic #1.
- **Build:** order-service `OutboxEvent`/`OutboxRepository`/`OutboxPublisher` (`@Scheduled` 1s poll); payment-service `IdempotencyRecord`/`IdempotencyRepository` + `Idempotency-Key` header handling on `POST /api/v1/payments`.
- **Lab:** Lab 18 (`docs/labs/lab-18/`).
- **Acceptance:** `createOrder()` writes order+outbox in one transaction (no direct Kafka send); publisher publishes within 1s after restart (proves no message loss when Kafka was down); duplicate idempotency key returns cached response, no double charge.
- **Checkpoint commit:** `session-22: add-outbox-pattern-and-idempotency-keys`.

### Session 23 — Performance & Load Testing

- **Concepts:** load vs stress vs smoke testing, VUs, thresholds (p95/p99), error-rate budgets, saturation analysis, correlating bottlenecks with the S5 resilience stack, using traces to explain failures.
- **Build:** `k6/{smoke-test.js, order-load-test.js, stress-test.js}`; findings document (`k6/FINDINGS.md`).
- **Lab:** Lab 19 (`docs/labs/lab-19/`).
- **Acceptance:** smoke passes (else stop); baseline recorded (req/s, P95, error rate); stress saturates the Bulkhead (available-concurrent-calls → 0) and/or opens the CB; actual firing order recorded vs the S5 prediction; ≥1 Zipkin trace correlated to a k6 error.
- **Checkpoint commit:** `session-23: add-k6-stress-test-and-bottleneck-findings`.
- **Prerequisites:** k6 installed; full stack up; `TEST_JWT` from Keycloak client-credentials.

### Session 24 — Architecture Clinic #2 + Phase 3 Wrap-Up

- **Format:** discussion only (like Clinic #1). Review every decision since Session 1; revisit the Technical Debt Register from Clinic #1 (which items were closed? which carried over?); Phase 4 capstone preview.
- **Deliverable:** updated Technical Debt Register + defended architecture decisions (see `docs/architecture/clinic-2.md` to be produced).
- **Lab:** none (clinic).

## Phase 3 completion criteria

- [ ] All 8 checkpoint commits present (`session-17` … `session-23`; S24 is a clinic).
- [ ] One trace demonstrably crosses ≥3 services in Zipkin; logs carry `traceId`.
- [ ] Gateway rejects tampered/expired Keycloak tokens; role checks proven.
- [ ] mTLS STRICT verified with `istioctl`.
- [ ] Outbox proven to survive a Kafka outage; idempotency proven with duplicate keys.
- [ ] k6 findings documented with real numbers.
- [ ] Technical Debt Register updated (Clinic #2) — every item either closed or consciously deferred.
- [ ] `docs/architecture/CURRENT_ARCHITECTURE.md` matches the final platform.
