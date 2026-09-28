# CURRENT ARCHITECTURE — Canonical Visual Mental Model

> **Canonical file (master prompt §9.1).** This is the single source of truth for "what the platform looks like right now".
> Update rules: full redraw at every lab milestone; milestone header at the top; never silently edit — each update is its own commit (`docs: update architecture for lab NN`).
> Statuses used in this repo: PASS / NOT VERIFIED / BLOCKED / NOT REVIEWED.

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

## How this file is used

- **Before each lab** (master prompt §13 before-lab briefing): paste the current block, mark the components the lab touches, show what will be added.
- **After each lab** (master prompt §17 LAB COMPLETE report): redraw with the new component(s) in place and commit the update.
- This file must always render as valid ASCII in a monospace viewer — no Unicode box-drawing beyond what the reference docs already use, no images.
