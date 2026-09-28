# Session 2 — API Gateway & Routing (Single Entry Point · Route Predicates · Filters · Load Balancing)

Source files: Session_02_API_Gateway_Routing.pdf (21 pages) and Session_02_API_Gateway_Routing_Continued.pdf (25 pages, Arabic-language supplemental deck). Both read in full.

File coverage:
- Session_02_API_Gateway_Routing.pdf — the course-session deck: recap, gateway problem/solution, six responsibilities, request flow, route predicates, filters, live coding (Steps 1-3), demo, Lab 2A + acceptance criteria, quiz, homework.
- Session_02_API_Gateway_Routing_Continued.pdf — supplemental deck in Arabic with three parts: (1) Spring MVC (Web) vs Spring WebFlux (Reactive), (2) StripPrefix filter, (3) Weight predicate / Canary deployment. Also contains the only explicit version notes (Java 21, Spring Boot 3.3.x, Spring Cloud 2023.x).

## 1. Why this topic exists

Recap of Session 1 (slide): Config Server :8888, Eureka Server :8761, Product Service :8081 (REST CRUD API, registered with Eureka + Config). Remaining problem: "clients still call http://localhost:8081/api/products directly — they must know the exact address and port of every service."

Without a gateway: the client hardcodes `http://product-service:8081/api/products`, `http://order-service:8082/api/orders`, `http://payment-service:8083/api/payments`, `http://notification-service:8084/notify`; consequences — client must know ALL service addresses; no single place to add authentication; no single place to add rate limiting; "Scaling changes the port — must update ALL clients". The slide's challenge question: "If we add Inventory Service tomorrow, how many places do we need to update?"

Solution: "API Gateway — The Single Entry Point": one address, one port :8080. "Clients only ever know about the Gateway. Everything behind it is invisible — and can change freely."

## 2. Core concepts

- Gateway responsibilities (slide "Six Responsibilities"): 1 Routing "Match request → forward to right service" (TODAY); 2 Load Balancing "Distribute traffic across instances" (TODAY); 3 Authentication "Validate JWT ONCE — services trust the Gateway" (SESSION 3+); 4 Rate Limiting "Protect services — 100 req/min per client" (SESSION 3+); 5 Observability "Log, trace, monitor all traffic in one place" (SESSION 3+); 6 Request Shaping "Add / remove / modify headers before forwarding" (TODAY).
- Request flow (9 steps as printed): 1 Client sends GET /api/products. 2 Gateway receives request on port 8080. 3 Route Predicates evaluated — does path match any route? 4 YES → apply pre-filters (log request, add request-id). 5 Gateway asks Eureka: "Where is PRODUCT-SERVICE?" 6 Eureka returns: http://192.168.1.10:8081. 7 Gateway forwards the request to that address. 8 Response comes back → apply post-filters (add headers). 9 Gateway returns response to client.
- Route Predicates — 5 types table: Path `Path=/api/products/**` (all product API calls → Product Service); Method `Method=GET,POST` (only allow GET and POST); Header `Header=X-Request-Id, \d+` (route only requests with numeric ID); Query `Query=version, v2` (route v2 API calls to new service version); Weight `Weight=group1, 8` (canary release: 80% stable, 20% new). "Forward reference: the Weight predicate returns in Session 14 for Canary deployments."
- Filters: GatewayFilter (Local) — applied to ONE specific route; defined inside the route config; examples StripPrefix, RewritePath; AddRequestHeader for one service. GlobalFilter — applied to ALL routes; defined as a separate @Component; examples Logging, RequestId, CORS; JWT validation (Session 3).
- Built-in filters used today: StripPrefix=0 ("Keeps the full path when forwarding — used on our product route"); AddResponseHeader ("Adds X-Platform: microservices-pro to every response"); AddRequestHeader ("Injects headers before forwarding (e.g. X-Request-Source)"); RewritePath ("Transforms the path before forwarding (e.g. /old → /api/v1)").
- From the Continued deck — Spring MVC vs Spring WebFlux:
  - `spring-boot-starter-web` = Spring MVC: Servlet API, Tomcat embedded server; every request gets its own thread; if the DB waits 5 seconds, the thread stays blocked.
  - `spring-boot-starter-webflux` = Reactive Programming: Reactive Streams, usually Netty instead of Tomcat ("Netty started on port 8080" instead of "Tomcat started..."), Event Loop instead of thread-per-request; non-blocking — a waiting DB call does not hold the thread, it serves other requests.
  - Reactive types: `Mono<Product>` = 0 or 1 value; `Flux<Product>` = 0 to N values (MVC returns `Product` / `List<Product>`).
  - Why the gateway uses WebFlux: "Gateway does not execute Business Logic" — it only does receive request → authentication → logging → routing → forward request, "all short operations", and needs "Thousands of concurrent requests". Comparison table verdict: MVC is not the usual choice for API Gateway; WebFlux is the recommended choice; "Spring Cloud Gateway — not built on MVC, built on WebFlux".
- From the Continued deck — StripPrefix: a Gateway Filter that removes N URL segments before sending the request to the backend service. Examples: client always sends `/api/products/10`; StripPrefix=0 → service receives `/api/products/10`; StripPrefix=1 → `/products/10`; StripPrefix=2 → `/10`. When to use: gateway `/api/products/**` but controller `@RequestMapping("/products")` → StripPrefix=1; controller `@RequestMapping("/")` or `@GetMapping("/{id}")` → StripPrefix=2. When NOT to use: if the service itself has `@RequestMapping("/api/products")`, StripPrefix is not required and may cause 404.
- From the Continued deck — Weight predicate: a Route Predicate that distributes requests between more than one route by a percentage — not all requests to the same service. Example: Product Service v1 and v2; instead of 100% → v2, do 80% → v1 and 20% → v2. "Called Canary Deployment". Weight config groups: `Weight=products,80` and `Weight=products,20` — "products" is the group name and must be identical in all routes. "80/20 does not mean the first 80 requests or the first 80 users — it is average distribution" (1000 requests ≈ 800 v1 / 200 v2). Gradual rollout example: 95/5 → 80/20 → 50/50 → 0/100 "without stopping the service".
- Weight vs Load Balancer (Continued deck): Load Balancer = two identical instances (same code), goal is performance increase; Weight = two different versions, goal is gradually testing the new version. When to use Weight: Canary Deployment; Blue/Green Deployment (in some scenarios); testing a new version with a small percentage of users; A/B Testing for services. When not: only one version or identical copies → Load Balancer is the right tool.
- Final comparison (Continued deck): StripPrefix = Gateway Filter that modifies the URL before sending; Weight = Route Predicate affecting route selection; usage StripPrefix removes a prefix like /api, Weight serves Canary Deployment and A/B Testing.

## 3. Architecture

Client -> API Gateway :8080 -> (via Eureka lookup `lb://PRODUCT-SERVICE`) -> Product Service. Per the gateway solution slide: Product "LIVE TODAY", Order "COMING S4", Payment "COMING S4", Inventory "COMING S6". Gateway itself registers in Eureka (acceptance criterion "API-GATEWAY appears in Eureka dashboard alongside PRODUCT-SERVICE"). Load balancing: `uri: lb://PRODUCT-SERVICE` — "lb = load balanced via Eureka"; demo starts a 2nd Product Service instance on :8082 and watches gateway logs alternate 8081 / 8082.

## 4. Technologies

- Spring Cloud Gateway (reactive); Spring WebFlux + Netty; Reactor types Mono/Flux.
- Eureka Discovery Client; Config Client; Spring Boot Actuator (Spring Initializr dependencies for the gateway project).
- Maven; Spring Initializr (start.spring.io).
- Lombok `@Slf4j` used in the Continued deck's LoggingFilter snippet.
- Versions (stated only in the Continued deck): Java 21; Spring Boot 3.3.x with Spring Cloud 2023.x ("يكفي غالبًا استخدام spring-cloud-starter-gateway" — usually `spring-cloud-starter-gateway` suffices); newer releases: Spring Boot 4.x with Spring Cloud 2025.x — a dedicated WebFlux starter exists and routes may move under `spring.cloud.gateway.server.webflux.routes` — "always review the documentation of the version you work on and do not rely on examples from different versions".
- Tomcat (MVC side) and Netty (reactive side) as contrasting embedded servers.

## 5. Important terminology

- Single Entry Point / API Gateway — one address and port (:8080) in front of all services.
- Route Predicate — the "IF" of routing; matched against the request (Path, Method, Header, Query, Weight).
- GatewayFilter (Local) — filter applied to one specific route, configured under the route.
- GlobalFilter — @Component-based filter applied to ALL routes (Logging today; JWT in Session 3).
- `lb://` — load-balanced URI resolved through Eureka ("lb = load balanced via Eureka").
- StripPrefix — filter removing N leading path segments before the backend call.
- Weight — predicate for weighted routing between routes in the same group; Canary Deployment; A/B Testing.
- Canary Deployment — send only a percentage of traffic to the new version.
- Load Balancer vs Weight — same version / performance goal vs different versions / gradual rollout goal.
- 503 Service Unavailable — gateway response when the target is not registered in Eureka (troubleshooting slide).
- WebFlux conflict — "Do NOT add Spring Web dependency. Gateway uses WebFlux (reactive) — adding Web creates a startup conflict."

## 6. Code concepts

Spring Initializr project (Step 1): Group `com.microservices.pro`, Artifact `api-gateway`, Dependencies: Gateway, Eureka Discovery Client, Spring Boot Actuator. "Critical: Do NOT add Spring Web dependency."

LoggingFilter (Step 3, course deck):

```java
@Component
public class LoggingFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        log.info("[GATEWAY] {} {}",
            exchange.getRequest().getMethod(),
            exchange.getRequest().getURI().getPath());
        return chain.filter(exchange);
    }
    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;  // runs first
    }
}
```

Continued deck equivalents: `@Component @Slf4j public class LoggingFilter implements GlobalFilter, Ordered` logging method + path with `getOrder()` returning `Ordered.HIGHEST_PRECEDENCE`; MVC controller returns `List<String>` vs reactive controller returning `Flux<String>` (`Flux.just("Book","Phone")`); MVC app logs "Tomcat started on port 8080", reactive app logs "Netty started on port 8080".

## 7. Configuration

Gateway `application.yml` (course deck Step 2):

```yaml
server:
  port: 8080
spring:
  cloud:
    gateway:
      routes:
        - id: product-service
          uri: lb://PRODUCT-SERVICE   # lb = load balanced via Eureka
          predicates:
            - Path=/api/products/**
          filters:
            - StripPrefix=0
            - AddResponseHeader=X-Platform, microservices-pro
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

Continued-deck minimal route (same idea): `- id: product-service / uri: lb://PRODUCT-SERVICE / predicates: - Path=/api/products/**`. Version note: on newer stacks (Spring Boot 4.x / Spring Cloud 2025.x) routes may live under `spring.cloud.gateway.server.webflux.routes`.

Weight routing example (Continued deck):

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: product-v1
          uri: lb://PRODUCT-V1
          predicates:
            - Path=/api/products/**
            - Weight=products,80
        - id: product-v2
          uri: lb://PRODUCT-V2
          predicates:
            - Path=/api/products/**
            - Weight=products,20
```

## 8. Failure scenarios

Course-deck troubleshooting: "Startup error: WebFlux/Servlet conflict" — Spring Web dependency was added by mistake, remove it (Gateway needs only WebFlux); "503 Service Unavailable from Gateway" — check Product Service is registered in Eureka before testing the route; "Route not matching the request" — verify Path predicate pattern, `/**` is required for wildcard sub-paths; "No log lines from LoggingFilter" — confirm @Component is present and getOrder() returns a valid precedence; "X-Platform header missing in response" — AddResponseHeader filter must be under `filters:`, not `predicates:`.

Client-side failure the gateway prevents: hardcoded service addresses and "Scaling changes the port — must update ALL clients".

Continued-deck failure scenarios: mixing Servlet stack and Reactive stack "may cause a startup conflict or use a different stack than expected"; using StripPrefix when the service already maps the full path "may cause 404"; using Weight when there is only one version or identical copies (wrong tool — use Load Balancer).

## 9. Trade-offs

- One entry point vs direct calls: clients no longer know service addresses; everything behind the gateway "can change freely" — at the cost of an extra network hop and a new single component in front of everything.
- MVC vs WebFlux: blocking/Tomcat/thread-per-request vs non-blocking/Netty/event loop; WebFlux recommended for the gateway because its work is short and massively concurrent ("thousands of concurrent requests"); MVC described as not the usual choice for an API Gateway.
- StripPrefix=0 vs 1 vs 2: keep the path if the service maps `/api/products`; strip 1 if the service maps `/products`; strip 2 if the service maps `/` or `/{id}` — the wrong value causes 404.
- Weight vs Load Balancing: weighted routing is for different versions/gradual exposure (canary, A/B, some blue/green), not for scaling identical instances.

## 10. Common mistakes

- Adding Spring Web to the gateway project (WebFlux/Servlet conflict).
- Using `http://` direct URIs instead of `lb://` service names (cold-call question from Session 1: "Why use lb:// instead of http://?").
- Forgetting `/**` in the Path predicate.
- Putting AddResponseHeader under predicates instead of filters.
- Testing the route before the target service has registered in Eureka (503).
- Missing @Component / wrong precedence on the GlobalFilter (no log lines).
- Mis-computing StripPrefix for the service's request mapping (404).
- Reading Weight percentages as "first N requests/users" instead of average distribution.
- Using StripPrefix unnecessarily when the service already maps `/api/products`.

## 11. Interview questions

Deck-labeled quiz topics: "API Gateway Purpose · Route Predicates · GlobalFilter vs GatewayFilter · Load Balancing" (Daily Quiz, 8 questions, 10 minutes). Cold-call questions were announced in Session 1 for this session: "What problem does an API Gateway solve? What is a Route Predicate? Why use lb:// instead of http://?" Homework (pre-Session 3) knowledge-check questions: "What is a JWT token made of? Where should authentication happen — Gateway or service? What is a token bucket rate limiter?" An explicit dedicated interview-question list: UNKNOWN — REQUIRES SOURCE REVIEW.

## 12. What I must memorize

- Six gateway responsibilities and which are "TODAY" (Routing, Load Balancing, Request Shaping) vs "SESSION 3+" (Authentication, Rate Limiting, Observability).
- The 9-step request flow through the gateway (predicate match -> pre-filters -> Eureka lookup -> forward -> post-filters).
- The 5 predicates: Path, Method, Header, Query, Weight (with their example values).
- GatewayFilter (local, in route config) vs GlobalFilter (@Component, all routes).
- Built-in filters used today: StripPrefix=0, AddResponseHeader (X-Platform: microservices-pro), AddRequestHeader, RewritePath.
- Route snippet: id product-service, `uri: lb://PRODUCT-SERVICE`, `Path=/api/products/**`, StripPrefix=0.
- "Do NOT add Spring Web" — WebFlux is the gateway stack (Netty, Mono/Flux, event loop).
- StripPrefix arithmetic: 0/1/2 mapping of `/api/products/10` to `/api/products/10`, `/products/10`, `/10`.
- Weight group syntax `Weight=products,80` / `Weight=products,20`; group name must match across routes; 80/20 = average distribution.
- Lab 2A acceptance criteria + commit `session-02: add-api-gateway-with-product-route`.

## 13. What I must understand

- Why one entry point removes client knowledge of addresses and centralizes auth/rate limiting "in one place".
- How `lb://` couples the gateway to Eureka resolution (name -> live instance address), and how load balancing across instances follows from it.
- Why the gateway is reactive: short, non-business operations at thousands of concurrent requests; blocking Tomcat threads per request limits it.
- When StripPrefix is needed vs harmful (depends on the downstream controller mapping).
- Why Weight exists (safety of gradual rollout: "the new version may contain bugs") and why it is not a replacement for a load balancer.
- Why mixing web stacks breaks startup (Servlet stack vs Reactive stack).

## 14. What I should implement from memory

Lab 2A ("API Gateway Setup & Product Route"):
1. Create & Configure the Gateway — "New service, port 8080, route to Product Service via Eureka".
2. Implement the Logging GlobalFilter — "Log method + path on every request through the Gateway".
3. Write Unit Tests — "Minimum 2 tests for the filter behaviour".

From memory: create the Initializr project (Gateway + Eureka Discovery Client + Actuator, no Spring Web), write the routes yml, implement LoggingFilter with `Ordered.HIGHEST_PRECEDENCE`, and (Continued-deck skill) wire StripPrefix/Weight YAML without looking at slides: two-route weighted canary with a shared group name.

## 15. Relationship to previous sessions

Recap slide: "What You Already Have Running" — Config Server :8888, Eureka Server :8761, Product Service :8081. The gateway's `lb://` routes and `defaultZone` reuse Session 1 infrastructure; the platform map marks "Session 1: Config + Eureka + Product Service + Docker Compose". The Weight predicate slide includes a forward reference to Session 14 (Canary deployments).

## 16. Relationship to future sessions

Next: "Session 3 — API Gateway Advanced (JWT + Rate Limiting)". The gateway responsibility table schedules Authentication, Rate Limiting, Observability for "SESSION 3+"; the Filters slide marks "JWT validation (Session 3)". Order and Payment services arrive in S4 ("COMING S4"), Inventory in S6 ("COMING S6"). Future-facing homework: pre-read JWT Authentication + Rate Limiting Basics (spring.io/projects/spring-security). Platform progress marker: "Session 3: Auth Filter + Rate Limiting".

## 17. Lab relationship

Exact slide content — "HANDS-ON: Lab 2A — API Gateway Setup & Product Route" with the 3 steps quoted in section 14. "DEFINITION OF DONE — Lab 2A Acceptance Criteria": Gateway starts on port 8080 without errors; API-GATEWAY appears in Eureka dashboard alongside PRODUCT-SERVICE; GET localhost:8080/api/products returns product list (proxied); Gateway console shows "[GATEWAY] GET /api/products" log line; Response includes X-Platform: microservices-pro header; "All unit tests pass: mvn test"; "Commit pushed: session-02: add-api-gateway-with-product-route". Demo evidence: TEST 1 basic routing via curl; TEST 2 verify LoggingFilter line; TEST 3 load balancing — "Start a 2nd Product Service instance on :8082. Call the Gateway 4 times — watch logs alternate 8081 / 8082 / 8081 / 8082." Homework/Checkpoint: "Pre-Session 3 Reading (15 min) — JWT Authentication + Rate Limiting Basics"; Knowledge Check questions for Session 3 listed in section 11. The Continued deck lists no lab of its own (supplemental theory: MVC vs WebFlux, StripPrefix, Weight); it contains an exam-style "final comparison" table between StripPrefix and Weight.
