# Lab 01 — Product Service + Eureka + Config Server

> **Session 1 · Phase 1 · Foundations**
> Official lab document: `docs/labs/session-01-lab-01.md` (instructor material) · Duration: ~50 min
> Status: **PASS** (see [`acceptance.md`](acceptance.md))

## Objective

Stand up the first three runtime members of the platform and prove the two
foundational platform capabilities work end to end:

1. **Externalized configuration** — product-service reads a property that is *not* in its jar (12-Factor III).
2. **Service discovery** — product-service registers itself in a registry instead of being addressed by a hardcoded host.

## Why it matters (interview framing)

Everything later depends on these two. The gateway (Session 2) cannot route
`lb://PRODUCT-SERVICE` until a registry knows where PRODUCT-SERVICE is; no
service can be reconfigured without a redeploy until configuration lives
outside the artifact. This lab is where "a Spring Boot app" becomes "a member
of a distributed system".

## Prerequisites

| Requirement | State |
|---|---|
| JDK 21, Maven 3.9.10, Docker daemon, curl | PASS (`scripts/verify-environment.sh`) |
| Ports 5432 (postgres), 8888 (config), 8761 (eureka), 8081 (product) free | PASS — verified before start |
| Port 8080 | OCCUPIED by the unrelated IdentityIQ stack — **not needed by this lab** |
| Software installs | none required |

## Concepts introduced

| Concept | One-line mental model |
|---|---|
| Config Server (native backend) | A service whose HTTP API *is* a property source; clients pull at startup. |
| `spring.config.import: optional:configserver:…` | "Try to fetch config; if the server is down, start anyway." The `optional:` prefix is what makes it fail-soft. |
| Config precedence | Remote (Config Server) properties sit **above** the client's local `application.yml` but below command-line arguments / env vars. |
| Service registry (Eureka) | A phone book: instances POST their address on startup, then heartbeat every 30 s. |
| Client-side discovery | The *caller* asks the registry and picks an instance — no load balancer in the middle. |
| `register-with-eureka: false` / `fetch-registry: false` | The registry must not try to register with itself. |
| `enable-self-preservation: false` | **DEV ONLY.** Self-preservation keeps stale instances when heartbeats drop (partition safety) — disabling it makes dead instances disappear fast while debugging. |
| `prefer-ip-address: true` | Register by IP instead of hostname (matters on multi-NIC machines). |

## Architecture: what this lab adds

```
                ┌──────────────┐                         ┌────────────────┐
  client ─────▶ │  product-    │ ──── config import ───▶ │  config-server │
                │  service     │                         │      :8888     │
                │   :8081      │ ──── register ────────▶ │  (native)      │
                └──────────────┘                         └────────────────┘
                       │
                       ▼
                ┌────────────────┐        docker-compose (this lab)
                │  eureka-server │        ┌──────────────────────────┐
                │     :8761      │        │ postgres:16-alpine :5432 │
                └────────────────┘        └──────────────────────────┘
```

Not built here, deliberately: `api-gateway` (:8080, Session 2), Redis
(Session 3), Kafka (Session 7), JPA/PostgreSQL usage (Session 6–8),
Dockerfiles (Session 9). Postgres is started by compose but **nothing connects
to it yet** — it exists so the infrastructure contract is stable from day one.

## Files created

```
platform/ecommerce-platform/
├─ .gitignore
├─ docker-compose.yml                              postgres only
├─ README.md
├─ infrastructure/config-server/                   :8888, native backend
│  ├─ pom.xml                                      spring-cloud-config-server
│  └─ src/main/resources/
│     ├─ application.yml                           profile "native", classpath:/configs
│     ├─ configs/product-service.yml               the externalized property (app.source)
│     └─ ../../java/…/ConfigServerApplication.java @EnableConfigServer
├─ infrastructure/eureka-server/                   :8761
│  ├─ pom.xml                                      spring-cloud-starter-netflix-eureka-server
│  └─ src/main/resources/application.yml           no self-registration, no self-preservation
└─ services/product-service/                       :8081
   ├─ pom.xml                                      web + eureka-client + config + actuator
   └─ src/main/java/com/microservices/pro/productservice/
      ├─ Product.java                             record (id, name, description, price, category)
      ├─ ProductService.java                      in-memory ConcurrentHashMap + AtomicLong
      ├─ ProductController.java                   4 endpoints under /api/v1/products
      └─ ProductServiceApplication.java
```

## Decisions made here

- **ADR-001** — in-memory store instead of JPA (`docs/decisions/ADR-001-in-memory-product-store.md`).
  JPA arrives with the Session 6–8 block; the store is a deliberate placeholder, not an oversight.

## Deliberate differences from the reference implementation

See the table in [`acceptance.md`](acceptance.md#differences-from-the-reference-implementation).

## Running it

```bash
cd platform/ecommerce-platform
docker compose up -d

cd infrastructure/config-server && mvn spring-boot:run    # terminal 1 → :8888
cd infrastructure/eureka-server && mvn spring-boot:run    # terminal 2 → :8761
cd services/product-service     && mvn spring-boot:run    # terminal 3 → :8081
```

`scripts/verify-lab.sh 01` automates most of the acceptance checks.

## Observations to carry into Session 2

1. **Registered IP.** With `prefer-ip-address: true`, this machine registered
   `192.168.56.1` (a VirtualBox host-only adapter) rather than a Wi-Fi address.
   Verified reachable from the host (`GET http://192.168.56.1:8081/api/v1/products` → 200),
   so gateway routing should work — but if Session 2's `lb://PRODUCT-SERVICE`
   call fails to connect, **check this first** before suspecting the gateway.
2. **In-memory state is volatile.** Restarting product-service wipes the store
   and restarts ids at 1. Expected in Lab 1; it disappears when JPA lands.
3. **Eureka read latency.** Correct registration is not instantly visible in
   `/eureka/apps` (30 s response cache). See `ENGINEERING_LOG.md` entry 2.
4. **Test suites need memory headroom.** With all three services + Docker + Maven
   resident, forked surefire JVMs can fail to start on this machine and surface as a
   misleading Mockito "could not self-attach" error. Run `mvn test` with the services
   stopped, or check free RAM and any `hs_err_pid*.log` before touching build config.
   See `ENGINEERING_LOG.md` entry 3.
