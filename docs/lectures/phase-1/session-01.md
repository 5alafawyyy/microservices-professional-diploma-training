# Session 1 — Architecture & Spring Cloud (Service Discovery · Centralized Config · Domain-Driven Design)

Source files: Session_01_Architecture_SpringCloud.pdf (25 pages, read in full)

## 1. Why this topic exists

The deck starts from the monolith: "One codebase. One deployment. One database. One team touches everything." Its problems: any change requires a full redeploy; one bug can crash the entire system; scaling means scaling EVERYTHING; teams block each other constantly. The driving question: "What if Product, Order, and Payment could each be built, deployed, and scaled INDEPENDENTLY?" — "This is the Microservices Architecture — and it's what we build for the next 29 sessions."

It then solves two foundational gaps the rest of the course depends on:
1. Service discovery (how Order finds Product without hardcoded addresses).
2. Centralized configuration (how 8 services stop having 8 scattered application.yml files).

## 2. Core concepts

- Microservices definition (slide quote): "An architectural style where an application is composed of small, independently deployable services, each owning its own data and business capability."
  - Gain: independent deployment; selective scaling; team autonomy; technology flexibility.
  - Cost: operational complexity; network latency between services; distributed debugging; data consistency challenges.
- Bounded Context (slide quote): "A Bounded Context is a logical boundary within which a domain model is defined and consistent. It is the foundation for how we split our platform into services."
  - Product Catalogue — "Read-heavy. Changes rarely. Owned by Catalogue team."
  - Inventory — "Write-heavy. Changes on every order. Owned by Fulfilment team."
  - Order Management — "Orchestrates the purchase flow. Owned by Commerce team."
  - Rule: "Different bounded contexts ⇒ different services. Same database table ⇒ NOT a reason to merge services."
- Service discovery problem: without it — hardcoded IP `10.0.0.42:8081`; "Kubernetes reassigns IPs constantly"; "Every new instance breaks all callers"; "Manual config update on every deploy". With Eureka — services register themselves by NAME; Order asks "Where is PRODUCT-SERVICE?"; Eureka returns the current live address; new instances register automatically.
- Eureka mechanics (4 steps as printed): 1. Registers on startup; 2. "Where is PRODUCT-SERVICE?"; 3. Returns IP:PORT; 4. Calls Product Service directly using the returned address. "Both services register with Eureka on startup."
- Config problem: change a DB password without centralized config = edit 8 application.yml files; redeploy all 8 services; easy to miss one (inconsistent state); secrets scattered across many repos. With Spring Cloud Config Server: one Git repo holds config for ALL services; change once — services pull the update; per-environment config: dev / staging / prod; "Directly implements 12-Factor App, Factor III".
- 12-Factor App Factor III: "Store config in the environment". "Configuration that varies between deployments (database URLs, credentials, feature flags) must NOT be hardcoded in the codebase. It must be externalized." The slide names three factors: Codebase ("One codebase, tracked in Git, many deploys"), Config ("Strict separation of config from code"), Backing Services ("Treat DB, cache, queue as attached resources").
- Config Server mechanics: Git Repository (config files) -> Config Server :8888 -> "reads on startup + refresh" -> Product / Order / Payment Service. "Each service calls Config Server at startup: spring.config.import: configserver:http://localhost:8888".

## 3. Architecture

Discovery flow: Product Service and Order Service both register with Eureka Server (8761); Order queries by name; Eureka returns the live IP:PORT; Order calls the service directly.

Config flow: Git repo (config files) -> Config Server (:8888) -> each microservice pulls its config at startup via `spring.config.import`.

Platform state after this session (slide "What We Added to the Platform Today"): NEW Eureka Server (8761); NEW Config Server (8888); NEW Product Service (8081) with "CRUD API + Eureka + Config integration". Capability added: "Service Discovery & Centralized Configuration".

## 4. Technologies

- `spring-cloud-starter-netflix-eureka-server` (Eureka Server dependency; groupId org.springframework.cloud).
- `@EnableEurekaServer`, `@EnableConfigServer`.
- Eureka client registration via `eureka.client.service-url.defaultZone` (Product Service).
- Spring Cloud Config Server backed by a Git repository (`spring.cloud.config.server.git.uri`).
- Actuator health endpoint (`/actuator/health`).
- Maven (`mvn test` acceptance criterion).
- Ports: Eureka 8761, Config Server 8888, Product Service 8081.

Exact versions: UNKNOWN — REQUIRES SOURCE REVIEW (this deck states no versions; the Session 2 Continued deck mentions Java 21, Spring Boot 3.3.x, Spring Cloud 2023.x in the course context).

## 5. Important terminology

- Bounded Context — logical boundary where a domain model is defined and consistent; the criterion for splitting services.
- Service Discovery — services register by NAME and are resolved dynamically to live addresses.
- self-preservation — Eureka's protection mode; `enable-self-preservation: false` is "DEV ONLY".
- 12-Factor App, Factor III (Config) — store config in the environment; externalize what varies between deployments.
- Backing Services — DB, cache, queue treated as attached resources.
- defaultZone — Eureka client property pointing to the registry URL.
- `optional:` prefix — in `spring.config.import`, lets a service still start if Config Server is down.

## 6. Code concepts

Eureka Server (Step 1):

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
</dependency>
```

```java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
```

Config Server (Step 3):

```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

Product Service client side (Step 4): registers as `product-service` and imports config (`optional:configserver:http://localhost:8888`) plus Eureka `defaultZone` — shown in section 7.

## 7. Configuration

Eureka Server `application.yml`:

```yaml
server:
  port: 8761
eureka:
  client:
    register-with-eureka: false   # this IS the registry
    fetch-registry: false
  server:
    enable-self-preservation: false  # DEV ONLY
```

Slide note: "enable-self-preservation:false is fine for a single-node dev setup. In production with multiple Eureka nodes, this must be true to handle network partitions correctly."

Config Server `application.yml`:

```yaml
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/your-org/config-repo
```

Product Service `application.yml`:

```yaml
spring:
  application:
    name: product-service
  config:
    import: "optional:configserver:http://localhost:8888"
    # optional: prefix = service still starts if Config Server is down
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka
```

## 8. Failure scenarios

- Hardcoded addresses break whenever instances change (new IPs, scaling, K8s reassigns IPs constantly; manual config updates on every deploy).
- Config drift: DB password changes require editing 8 files and redeploying 8 services; one missed service = inconsistent state.
- Config Server down: without the `optional:` prefix, services fail to start ("optional: prefix missing causes startup failure").
- Eureka shows a service as DOWN despite it running — slide says "Wait 30s — Eureka heartbeat interval; this is expected, not a bug".
- Service not appearing in Eureka — check `eureka.client.service-url.defaultZone` matches the server's actual port.
- "Connection refused" to Config Server — "Config Server must start BEFORE other services — start it first".
- Port already in use (8761/8888/8081) — `lsof -i :8761` then kill the conflicting process.
- Production network partitions — self-preservation must be `true` on multi-node Eureka.

## 9. Trade-offs

- Microservices gains vs costs (see section 2): independent deployment, selective scaling, team autonomy, technology flexibility vs operational complexity, network latency, distributed debugging, data consistency challenges.
- Single-node dev vs production Eureka: `enable-self-preservation: false` is acceptable for one node; "In production with multiple Eureka nodes, this must be true to handle network partitions correctly."
- Service split criterion: bounded contexts decide services; "Same database table ⇒ NOT a reason to merge services."
- Centralized config vs startup coupling: config must be externalized (Factor III), but the Config Server becomes a startup dependency unless the `optional:` prefix is used.

## 10. Common mistakes

- Hardcoding IPs/ports instead of registering by name.
- Splitting (or merging) services based on database tables rather than bounded contexts.
- Forgetting the `optional:` prefix in `spring.config.import` (service fails to start when Config Server is down).
- Starting services before the Config Server ("Config Server must start BEFORE other services").
- Wrong `defaultZone` port (service never appears in Eureka).
- Assuming instant registration: a service may show DOWN for ~30s (heartbeat interval) — "expected, not a bug".
- Enabling `enable-self-preservation: false` in production multi-node setups.

## 11. Interview questions

The deck does not label interview questions. The closest source-backed questions are its Daily Quiz topics: "Service Discovery · Bounded Context · 12-Factor App · Eureka · Spring Cloud Config", plus its Session 2 cold-call questions ("What problem does an API Gateway solve? What is a Route Predicate? Why use lb:// instead of http://?"). Explicit interview question list: UNKNOWN — REQUIRES SOURCE REVIEW.

## 12. What I must memorize

- The definition of microservices (independently deployable services owning their own data and business capability) and the 4 gains / 4 costs.
- "Different bounded contexts ⇒ different services. Same database table ⇒ NOT a reason to merge services."
- Eureka dance: register on startup by NAME -> ask "Where is PRODUCT-SERVICE?" -> returns IP:PORT -> direct call.
- Config: one Git repo; per-environment dev/staging/prod; Factor III quote "Store config in the environment".
- Ports: Eureka 8761, Config 8888, Product 8081; Product Service name `product-service`.
- Annotations: `@EnableEurekaServer`, `@EnableConfigServer`; property paths `eureka.client.service-url.defaultZone`, `spring.config.import: optional:configserver:...`.
- Lab 1 acceptance criteria and commit message `session-01: add-product-service-eureka-config`.

## 13. What I must understand

- Why discovery removes hardcoded addresses and how "new instances register automatically".
- Why config must be externalized (12-Factor III) and how `optional:` changes startup behaviour.
- Why the Config Server must start before its clients.
- Why `enable-self-preservation` differs between single-node dev and multi-node production.
- Why bounded context (domain ownership: Catalogue / Fulfilment / Commerce teams) — not schema — defines service boundaries.

## 14. What I should implement from memory

Lab 1 ("Build Product Service + Connect Infrastructure"):
1. Create Eureka Server — Port 8761, `@EnableEurekaServer`.
2. Create Config Server — Port 8888, connect to Git config repo.
3. Build Product Service — CRUD REST API + connect to Eureka & Config.
4. Write Unit Tests — Minimum 3 tests — service layer logic.

From memory you should be able to write: the Eureka server yml (register-with-eureka/fetch-registry false), the `@EnableConfigServer` class + git uri yml, the Product Service yml (name, `optional:configserver:` import, defaultZone), and run `mvn test` with POST/GET product endpoints.

## 15. Relationship to previous sessions

This is Session 1 of 29 (Offline Anchor Day) and "Session 1 of 8 in Phase 1". It has no previous technical session; the kickoff deck introduces the full 29-session roadmap. Within Phase 1's map: S1 Architecture (LIVE), S2 Gateway Core, S3 Gateway Adv., S4 Resilience CB, S5 Resilience BH, S6 OpenFeign, S7 Saga+Kafka, S8 Caching+Clinic.

## 16. Relationship to future sessions

- Slide: "Today we lay the foundation everything else depends on." Key takeaway: "Every pattern from Session 2 onward builds directly on what you built today."
- Direct consumers: Session 2 (Gateway routes via Eureka with `lb://`, recap shows Config :8888 / Eureka :8761 / Product :8081 running), Session 3 (JWT secret noted as "In production, this comes from HashiCorp Vault (Session 21)").
- Pre-Session 2 homework points forward: read "Spring Cloud Gateway — Overview" at spring.io/projects/spring-cloud-gateway; cold-call questions: What problem does an API Gateway solve? What is a Route Predicate? Why use lb:// instead of http://?

## 17. Lab relationship

Exact slide content — "HANDS-ON: Lab 1 — Build Product Service + Connect Infrastructure" with the 4 steps quoted in section 14. "DEFINITION OF DONE — Lab 1 Acceptance Criteria": Eureka Dashboard (localhost:8761) shows PRODUCT-SERVICE as UP; GET /actuator/health on Product Service returns {"status":"UP"}; Config Server successfully serves config to Product Service on startup; POST /api/products creates a new product and returns 201 Created; GET /api/products/{id} returns the correct product or 404; "All unit tests pass: mvn test"; "Commit pushed: session-01: add-product-service-eureka-config". The deck's Demo step verifies registration ("If you see PRODUCT-SERVICE with status UP — Eureka registration is working correctly"; `curl http://localhost:8081/actuator/health` -> {"status":"UP"}). Pre-Session 2 reading: 15 minutes, Spring Cloud Gateway overview. Daily Quiz: "8 Questions · 10 Minutes" on Service Discovery, Bounded Context, 12-Factor App, Eureka, Spring Cloud Config.
