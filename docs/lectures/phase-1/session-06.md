# Session 6 — Inter-Service Communication (Sync vs Async · OpenFeign · Design Choices · JWT Propagation)

Source files: Session_06_OpenFeign_Communication.pdf; Session_06_InterService_Communication_Continued.pdf

Coverage map (two decks, one note):
- Session_06_OpenFeign_Communication.pdf — the live-session deck: where-we-are, sync/async decision framework, building Inventory Service, OpenFeign client, ErrorDecoder, JWT propagation, WebClient closing, Lab 4A + DoD, troubleshooting.
- Session_06_InterService_Communication_Continued.pdf — the seminar deck: "Part 1 — Foundations of Communication in Microservices", "Part 2 — Communication Patterns, Messaging, Event Streaming & Distributed Systems", "Part 3 — Building Synchronous Communication in Spring Boot". It covers sync/async, blocking/non-blocking, programming styles, CompletableFuture, Reactive (Mono/Flux), Eventual Consistency, RabbitMQ, Kafka, Spring Cloud Bus, gRPC, and client-code comparisons.

Deck identity: "Session 6 of 29", Monday 3:00 PM – 5:30 PM, 2.5 Hours, Online Session, Phase 1. Slide 3: "This Session Is Not About OpenFeign — It is about how engineers DECIDE communication patterns." "The real skill is not writing @FeignClient -- it is answering: 'Why did I choose this pattern, and not another one?'"

## 1. Why this topic exists

- Problem: "Order Service Doesn't Actually Check Inventory" — `createOrder()` goes straight to Payment; nothing stops an order for a product with ZERO stock. Customer orders 5 units of PROD-003; PROD-003 has 0 units; Order Service has no way to know; Payment succeeds, Order is CONFIRMED; "Warehouse has nothing to ship. Customer is angry."
- Today's goal: "build Inventory Service, and connect it to Order Service -- synchronously, with intent."
- Seminar framing: unlike a monolith, each microservice is an independent application with its own database, business logic, deployment — "they must communicate over the network" (HTTP request or publish event via Kafka). "Inter-Service Communication."
- The most important question (seminar): "Do I need the answer immediately?" — "This single question determines almost everything."
- Sessions 6 & 7 are "where you move from 'how do I use the tool' to 'how do I design the architecture'."

## 2. Core concepts

- Sync vs Async Decision — Three Questions (main deck):
  - Q1 "Does the caller need the answer to CONTINUE?" YES → Sync (Feign/WebClient); NO → Async (Kafka, Session 7).
  - Q2 "Is the operation reversible if it fails?" YES → Sync is fine, retry; NO → Saga + compensation (S7).
  - Q3 "Is eventual consistency acceptable?" NO → Sync (check stock NOW); YES → Async (notify later).
  - Platform mapping: Order→Inventory (check stock) SYNC; Order→Notification (send email) ASYNC; Order→Payment (charge card) SYNC.
- Seminar decision framework: Q1 immediate answer? Q2 can this happen later? Q3 can I accept a short delay? Business mapping table: Order→Inventory Sync; Order→Product Sync; Order→Payment Sync; Order→Notification Async; Order→Audit Log Async; Order→Analytics Async. "Make the decision based on the required communication semantics." Golden rule: "Need answer NOW? → OpenFeign / RestClient / WebClient; Need answer LATER? → Kafka; Need a TASK executed? → RabbitMQ; Need Config Refresh? → Spring Cloud Bus; Need Maximum Performance? → gRPC."
- Synchronous (seminar): caller sends request and waits; "Think of making a phone call." Characteristics: immediate response, easy to understand, usually HTTP or gRPC, usually blocking. Advantages: simple, immediate answer, easy debugging. Disadvantage: if downstream is slow, caller threads remain occupied.
- Asynchronous (seminar): send a message and continue; "Think about sending an email." Characteristics: no waiting, better scalability, independent services, better fault tolerance. Drawbacks: more complex, harder debugging, no immediate response. Sync vs Async table: waits yes/no; immediate result yes/no; HTTP/gRPC vs Kafka/RabbitMQ; complexity lower/higher; scalability moderate/excellent; typical use read/validation vs notifications/analytics/logging.
- Blocking vs Non-Blocking (seminar): blocking = thread waits (one thread per request); non-blocking = thread sends and becomes free (event loop; 10,000 requests ↔ 20 threads). "Blocking is NOT the opposite of Asynchronous... Blocking describes what happens to the thread." "Blocking and Non-Blocking are execution models. They do NOT describe business communication." HTTP can be blocking or non-blocking depending on the client library.
- Programming styles (seminar): Imperative (tell HOW — RestTemplate) · Fluent API (method chaining — RestClient, WebClient) · Declarative (declare WHAT — OpenFeign) · Reactive (process streams — WebClient).
- CompletableFuture (seminar): `CompletableFuture.supplyAsync(...)`, later `future.join()`; standard Java, asynchronous, parallel execution, good for Spring MVC; not recommended inside WebFlux. vs Reactive: Java Standard vs Project Reactor; async vs async + streams; one result vs Mono or Flux; thread-based vs event loop. Example: two 500ms calls sequentially = 1000ms; parallel = max(500,500) ≈ 500ms.
- Reactive Programming (seminar): asynchronous model based on streams; nothing executes until someone subscribes; focuses on non-blocking, high scalability, backpressure, event-driven. Mono = 0..1 items ("like Optional<Product> but asynchronous"); Flux = 0..N items ("like List<Product> but asynchronous").
- Eventual Consistency (seminar): microservices often accept a small delay; order created → inventory updated → email sent → analytics updated; improves scalability, performance, availability "at the cost of immediate consistency". Good for: emails, notifications, analytics, audit logs, recommendations. Not good for: bank transfer confirmation, stock validation before purchase, authentication.
- REST clients compared (both decks): RestTemplate — imperative, blocking, deprecated, "legacy"; OpenFeign — declarative interface, recommended (sync); WebClient — reactive/functional, recommended (reactive). RestClient — "Spring Boot 3.2 introduced RestClient", modern synchronous client, "Recommended MVC replacement". OpenFeign = "Best synchronous service-to-service communication", "almost zero HTTP code". Why Feign doesn't support reactive: "Feign is built around HTTP Request → Wait → Response. Blocking model. Reactive applications never wait."
- Kafka vs RabbitMQ quick model (seminar): RabbitMQ = Message Broker (Producer → Exchange → Queue → Consumer; reliable delivery, routing, acknowledgements); best for email, SMS, background jobs, payment processing, task scheduling, work queues. Kafka = Event Streaming Platform (Producer → Topic → Consumer Group; extremely fast, durable on disk, replayable, distributed); best for event sourcing, analytics, streaming, microservices events, audit logs. Rule of thumb: RabbitMQ "Do this work" (task-oriented); Kafka "This event happened" (event-oriented). Comparison: ordering queue vs partition order; throughput medium vs extremely high; replay no vs yes; retain history usually no vs yes; complexity lower vs higher; learning curve easier vs harder.
- Spring Cloud Bus (seminar): without it, `POST /actuator/refresh` must be called service-by-service; with it, "One refresh triggers all services" via RabbitMQ (`spring-cloud-starter-bus-amqp`) or Kafka (`spring-cloud-starter-bus-kafka`).
- gRPC (seminar): Google's high-performance protocol using HTTP/2 + Protocol Buffers instead of JSON; faster, smaller payloads, strong contracts (compile-time safety), streaming; harder debugging (not human-readable), less browser-friendly; good for internal microservices (high-performance), NOT ideal for public APIs, mobile clients, frontends.
- Feign ErrorDecoder concept: "By default, Feign wraps ALL HTTP errors as generic FeignException. ErrorDecoder translates them into meaningful domain exceptions your business logic can handle."
- JWT propagation: "The JWT travels with the request through the ENTIRE service chain. Gateway validates it once. Order Service reads it. Order forwards it to Inventory via a RequestInterceptor. Inventory can independently check who the user is."
- Zero DB sharing (seminar, platform rules): "Each service owns its own database... No service is allowed to access another service's database. Only APIs or Events."

## 3. Architecture

- Platform after S6: API Gateway → Product Service, Order Service, Inventory Service (8084), Notification Service; each with its own DB (Product DB, Order DB, Inventory DB, Notification DB). Notification is annotated "S7" (future work) in the platform diagram.
- Flow built today: Client → POST /api/orders → Order Service `createOrderAsync()` (Resilience4j stack) → Step 1: Feign call to Inventory Service via Eureka (`INVENTORY-SERVICE`) → Step 2 (only if stock OK): Payment Service → OrderResponse.
- Inventory Service internals: Controller (`GET /api/v1/inventory/check`) → InventoryService (in-memory ConcurrentHashMap) → StockItem / StockCheckResponse records; 409 CONFLICT when unavailable, 200 OK when available.
- Feign call path: `@FeignClient(name = "INVENTORY-SERVICE", path = "/api/v1/inventory")` interface; Feign resolves the address via Eureka — "no hardcoded URL anywhere". `name` "must match the Eureka service name EXACTLY".
- JWT chain: Client → Gateway (validates) → Order Service (forwards) → Inventory Service (also enforces security).
- Seminar decision tree (final): Need immediate response? YES → Reactive? YES → WebClient; NO → OpenFeign / RestClient / RestTemplate (legacy). NO → Event-driven? → Kafka; Reliable task processing? → RabbitMQ; Config refresh? → Spring Cloud Bus; Max performance internal? → gRPC.
- Feature timeline (seminar "What Will We Build?"): Session 6 Order→Inventory OpenFeign; Session 7 Order→Notification Kafka; Session 15 Gateway→WebClient reactive.

## 4. Technologies

- OpenFeign: `spring-cloud-starter-openfeign`; `@EnableFeignClients`; `@FeignClient`; `RequestInterceptor`; `ErrorDecoder`; `@RequestParam` bindings; Feign client injection by Spring.
- Eureka (service naming/resolution: S2/S3 infrastructure) and Spring Cloud Config (Inventory dependency list includes "Spring Cloud Config").
- Spring Web, Spring Boot Actuator (Inventory dependencies).
- Resilience4j stack from S5 applied to `createOrderAsync()` (`@Bulkhead(...) @TimeLimiter(...) @CircuitBreaker(...) @Retry(...)`).
- RestClient — "Spring Boot 3.2 introduced RestClient" (only version fact in these decks).
- WebClient (reactive; `bodyToMono`, `lb://INVENTORY-SERVICE` Eureka load-balancing URI; warning `.block()` in reactive context = bad practice); used internally by Spring Cloud Gateway ("it is WebFlux-based — but we don't write it ourselves").
- RestTemplate — deprecated; only legacy projects.
- CompletableFuture (Java standard); Project Reactor Mono/Flux (seminar).
- RabbitMQ (seminar, message broker), Kafka (seminar, event streaming; detailed in S7), Spring Cloud Bus (bus-amqp / bus-kafka), gRPC (HTTP/2 + Protocol Buffers).
- Java records (`StockItem`, `StockCheckResponse`, `OrderCreatedEvent` example in seminar uses records).
- Versions: only "Spring Boot 3.2 introduced RestClient" is stated. All other version numbers (OpenFeign, Spring Cloud release train, Java) → UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- Inter-Service Communication; Synchronous / Asynchronous; Blocking / Non-Blocking; Event Loop.
- Imperative / Fluent / Declarative / Reactive; Backpressure; Mono / Flux; Eventual Consistency.
- Message Broker (RabbitMQ: Exchange, Queue, Acknowledgements) vs Event Streaming Platform (Kafka: Topic, Consumer Group, Replay, Partition order).
- Declarative HTTP client, Feign Proxy, domain exception, ErrorDecoder, `methodKey`.
- RequestInterceptor, JWT propagation, trust chain, Authorization header.
- 409 Conflict, `InsufficientStockException`, `ProductNotFoundException`, `ServiceUnavailableException`.
- "no instances available" (Feign/Eureka error), load balancing (`lb://`).
- Temporal coupling (seminar: sync has it, async is "more temporally decoupled").

## 6. Code concepts

- Inventory domain: `public record StockItem(String productId, int availableQuantity, int reservedQuantity)` with `public boolean hasStock(int requested) { return availableQuantity - reservedQuantity >= requested; }`.
- `public record StockCheckResponse(String productId, int requestedQuantity, boolean available, int remainingStock) {}`.
- In-memory store: `ConcurrentHashMap<>(Map.of("PROD-001", new StockItem("PROD-001", 100, 0), "PROD-002", new StockItem("PROD-002", 5, 0), "PROD-003", new StockItem("PROD-003", 0, 0)))` — comment: "In-memory store (PostgreSQL added as homework)".
- Controller: `@GetMapping("/check")` with `@RequestParam String productId, @RequestParam int quantity`; returns `ResponseEntity.status(HttpStatus.CONFLICT).body(response)` when `!response.available()`.
- Order Service main class: `@EnableFeignClients // REQUIRED -- scans for @FeignClient interfaces`.
- Feign interface: duplicate `StockCheckResponse` in Order Service — "StockCheckResponse must be duplicated here (or use a shared library). For this course: duplicate the record -- shared libs discussed in Session 14."
- `createOrderAsync()`: inside `CompletableFuture.supplyAsync`: `StockCheckResponse stock = inventoryClient.checkStock(request.getProductId(), request.getQuantity());` → if `!stock.available()` return `new OrderResponse("REJECTED", "Insufficient stock: only " + stock.remainingStock() + " available")` → else process payment → `CONFIRMED`.
- `InventoryErrorDecoder implements ErrorDecoder`: `decode(String methodKey, Response response)` → switch on `response.status()`: `case 409 -> new InsufficientStockException("Product out of stock")`; `case 404 -> new ProductNotFoundException("Product not found")`; `case 503 -> new ServiceUnavailableException("Inventory unavailable")`; default → `FeignException.InternalServerError`.
- `FeignJwtInterceptor implements RequestInterceptor`: `apply(RequestTemplate template)` → reads `ServletRequestAttributes` via `RequestContextHolder.getRequestAttributes()` → `template.header(HttpHeaders.AUTHORIZATION, authHeader)`. "Applies to ALL Feign clients in Order Service automatically."
- WebClient sample: `WebClient.builder().baseUrl("lb://INVENTORY-SERVICE").build().get().uri(...).retrieve().bodyToMono(StockCheckResponse.class).block();` with "WARNING: calling .block() inside a WebClient chain defeats its entire purpose -- never do it in production code."
- Seminar examples: OpenFeign (`@FeignClient(name = "inventory-service")` + `@GetMapping`), RestClient (`restClient.get().uri(...).retrieve().body(...)`), WebClient (`bodyToMono` returns `Mono<InventoryResponse>`), RestTemplate (`getForObject`, "Still works. But deprecated.").

## 7. Configuration

- Inventory Service coordinates: `services/inventory-service`; dependencies "Spring Web, Eureka Discovery Client, Spring Cloud Config, Actuator"; "Port: 8084".
- pom.xml (Order Service): `org.springframework.cloud:spring-cloud-starter-openfeign` (no version shown).
- `@FeignClient(name = "INVENTORY-SERVICE", path = "/api/v1/inventory")` — name must match the Eureka service name exactly.
- Feather/WebClient URI pattern: `lb://INVENTORY-SERVICE` (Eureka load balancing), example `uri("/api/v1/inventory/check?productId={id}&quantity={qty}", id, qty)`.
- Spring Cloud Bus starters (seminar): `spring-cloud-starter-bus-amqp` (RabbitMQ) or `spring-cloud-starter-bus-kafka` (Kafka); manual alternative: `POST /actuator/refresh`.
- No `application.yml` snippets for Inventory Service are shown in these decks (only port and dependency list) → UNKNOWN — REQUIRES SOURCE REVIEW for its full config.

## 8. Failure scenarios

- Business failure prevented: ordering PROD-003 (0 stock) previously reached CONFIRMED; now Order Service returns REJECTED before payment is attempted.
- Demo failure path: POST /api/orders with PROD-003, quantity 1 → Feign call via Eureka → Inventory responds 409 — out of stock → Order Service response `REJECTED -- "Insufficient stock: only 0 available"`; success path with PROD-001 → CONFIRMED.
- Slow downstream (seminar): sync call blocks the Order Service thread; "The thread remains occupied. Performance decreases."
- Troubleshooting table (main deck, 5 rows):
  - Feign client returns "no instances available" → "Inventory Service must be UP and registered in Eureka before Order Service starts calling it".
  - @FeignClient interface has no implementation → "Missing @EnableFeignClients on the main application class".
  - ErrorDecoder not catching errors → "Register as @Component -- Spring must discover it as a bean to wire into Feign".
  - JWT not appearing in Inventory logs → "Check FeignJwtInterceptor is a @Component and Authorization header exists on the original request".
  - StockCheckResponse fields don't match → "Record fields must match Inventory's response exactly -- duplicate the record carefully".
- Seminar caveat: "HTTP client may serialize requests..." is S5; here the analog risk is Feign resolving an unregistered service name (name mismatch with Eureka).

## 9. Trade-offs

- Sync vs Async framework (both decks): sync is simple, immediate, debuggable, but creates temporal coupling and blocks threads; async gives throughput/scalability/loose coupling but is more complex, harder to debug, and delivers eventual consistency only.
- OpenFeign vs WebClient (main deck): "OpenFeign for ALL service-to-service calls -- blocking, simpler, matches our Spring MVC stack" vs WebClient only for WebFlux, streaming (SSE, chunked), fine-grained per-call control (custom timeouts, codecs).
- Declarative vs imperative: Feign "almost zero HTTP code" but requires interface + shared/duplicated DTOs and a blocking model (no reactive support).
- Duplicating DTO records per service (chosen in-course) vs shared library ("shared libs discussed in Session 14").
- ErrorDecoder: mapping HTTP status codes to domain exceptions keeps business logic clean, but is an extra bean to register and maintain.
- JWT propagation: each service can enforce security independently, at the cost of passing headers through every hop.

## 10. Common mistakes

- Forgetting `@EnableFeignClients` (no implementation generated).
- Assuming Order calls Payment before Inventory — order is: check inventory BEFORE payment (stock check is Step 1).
- Forgetting ErrorDecoder `@Component` (Spring must discover it as a bean).
- Expecting the interceptor to survive without an incoming request context / missing Authorization header.
- Sloppy duplication of `StockCheckResponse` in Order Service (field mismatch).
- Using `.block()` inside a WebClient chain — "never do it in production code".
- Starting Order Service before Inventory Service is registered in Eureka.

## 11. Interview questions

Note: the main deck has no "Interview Questions" section; the Daily Quiz topics are "Sync vs Async Decision • OpenFeign vs WebClient • JWT Propagation • ErrorDecoder". The seminar ends with a "Final Decision Tree"/"Golden Rule". The three Pre-Session 7 knowledge-check questions are stated verbatim in the deck (see section 17). Questions derived from the slides:

- What is the advantage of OpenFeign over RestTemplate? (Declarative interface, no HTTP code, Eureka resolution; RestTemplate is deprecated/verbose.)
- When should Order Service call Inventory synchronously? (When the answer is needed immediately to continue — stock check.)
- What does @EnableFeignClients do? (Scans for @FeignClient interfaces and generates implementations — REQUIRED on the main application class.)
- Sync or async for Order→Notification and why? (Async — order should not wait for email.)
- Why doesn't Feign support reactive? (It is built on a blocking request-wait-response model.)
- What does an ErrorDecoder do? (Translates HTTP errors that Feign would wrap as generic FeignException into domain exceptions.)
- How does the JWT reach Inventory Service? (Gateway validates once; Order Service forwards the Authorization header via a RequestInterceptor.)
- Kafka vs RabbitMQ rule of thumb? ("Do this work" task-oriented vs "This event happened" event-oriented.)

## 12. What I must memorize

- The 3-question decision framework and the platform mapping (Order→Inventory sync, Order→Payment sync, Order→Notification async).
- Client matrix: RestTemplate (imperative, deprecated) / RestClient (modern MVC replacement, Spring Boot 3.2) / OpenFeign (declarative, recommended sync) / WebClient (reactive, recommended reactive).
- `@EnableFeignClients` is REQUIRED; `@FeignClient(name=...)` must match Eureka name exactly; path = base path.
- Inventory Service port 8084; endpoint `GET /api/v1/inventory/check`; 200 vs 409 behavior; stock data (PROD-001=100, PROD-002=5, PROD-003=0).
- ErrorDecoder status map: 409→InsufficientStockException, 404→ProductNotFoundException, 503→ServiceUnavailableException.
- JWT flow: Gateway validates → Order forwards via RequestInterceptor → Inventory can enforce.
- The sync call order inside `createOrderAsync`: inventory check FIRST, payment SECOND only if stock OK.
- Commit tag `session-06: add-inventory-service-and-feign-client`.

## 13. What I must understand

- Why the decision is about communication semantics, not technology preference ("Why did I choose this pattern, and not another one?").
- Why sync is correct for stock checks and async for notifications (answer needed now vs later; reversibility; eventual consistency acceptable?).
- Why sync creates temporal coupling and thread-blocking risk, linking back to S5's slow-service problem.
- Why the DTO must be duplicated exactly (Feign deserialization contract) and what the shared-library alternative would be (S14).
- Why RestClient exists (RestTemplate deprecated; Spring Boot 3.2) and why WebClient is not suitable for this MVC stack.
- Eventual consistency: it is a trade (scalability/performance/availability vs immediate consistency) and is not acceptable for bank transfers, stock validation before purchase, authentication.

## 14. What I should implement from memory

- Build Inventory Service: records (`StockItem`, `StockCheckResponse`), in-memory ConcurrentHashMap store, controller with 200/409 semantics, Eureka registration, port 8084.
- Order Service: add Feign dependency + `@EnableFeignClients`; declare `InventoryClient`; call stock check before payment inside the existing resilience stack; REJECTED handling.
- `InventoryErrorDecoder` with the 4-case switch.
- `FeignJwtInterceptor` as `@Component` reading the incoming Authorization header and forwarding it.
- Minimum 3 unit tests covering Feign call + error handling.

## 15. Relationship to previous sessions

- Builds directly on S5: the Feign call is inserted inside `createOrderAsync()` which already carries `@Bulkhead @TimeLimiter @CircuitBreaker @Retry` (the annotation stack appears verbatim in the S6 code slide).
- Builds on S2/S3 infrastructure: Eureka service discovery (Feign resolves `INVENTORY-SERVICE` via Eureka) and the secured Gateway (JWT validated once, propagated onward).
- Where-we-are row: "S5 Resilience BH" → "S6 OpenFeign (LIVE)".
- Platform progress: "Sessions 1-5: Config + Eureka + Gateway + Payment + Order (full resilience)"; "Session 6: Inventory Service + OpenFeign -- first real service-to-service call".
- Seminar recap of monolith vs microservices and own-database rule reinforces S1 architecture decisions.

## 16. Relationship to future sessions

- Next: "Session 7 -- Distributed Transactions: Saga Pattern + Kafka" — Wednesday, 3:00 PM–5:30 PM, Online. Pre-reading (15 min): "Saga Pattern + Distributed Transactions", microservices.io/patterns/data/saga.html.
- Seminar "What We Use In This Course" mapping: Session 6 OpenFeign; Session 7 Kafka (asynchronous event communication); Session 10+ CompletableFuture (parallel processing); Session 12+ Saga Pattern + Kafka (distributed transactions); Session 15+ Reactive WebClient (advanced reactive communication); Session 20+ Spring Cloud Bus (distributed configuration refresh).
- Caveat (deck inconsistency, recorded as-is): the seminar's Session 12+ row lists "Saga Pattern — Kafka" while the live S7 deck implements the choreography Saga in Session 7 and defers only Saga Orchestration to Session 12.
- Shared DTO/library topic deferred to Session 14 ("shared libs discussed in Session 14").
- Notification Service appears on the platform diagram marked "S7" — the async consumer built in Session 7.

## 17. Lab relationship

- Hands-on slide: "Lab 4A -- Inventory Service + OpenFeign Order Call" with 4 items:
  1. "Build Inventory Service — New service, port 8084, in-memory stock with 3 products"
  2. "Add OpenFeign Client to Order Service — InventoryClient interface, check stock before payment"
  3. "JWT Propagation — FeignJwtInterceptor forwards Authorization header"
  4. "Write Unit Tests — Minimum 3 tests covering Feign call + error handling"
- Definition of Done (Lab 4A Acceptance Criteria, 7 items):
  - "GET /api/v1/inventory/check?productId=PROD-001&quantity=5 → 200, available:true"
  - "GET .../check?productId=PROD-003&quantity=1 → 409, available:false"
  - "POST /api/orders with PROD-003 → REJECTED (insufficient stock)"
  - "POST /api/orders with PROD-001 → CONFIRMED (stock checked + payment processed)"
  - "JWT forwarded to Inventory Service -- visible in Inventory's logs"
  - "ErrorDecoder translates 409 into InsufficientStockException"
  - "All 3 unit tests pass: mvn test"
  - "Commit: session-06: add-inventory-service-and-feign-client"
- Checkpoint slide ("BEFORE SESSION 7") repeats: "Inventory Service running on :8084; Order rejects PROD-003 (no stock); Order confirms PROD-001 (has stock); JWT visible in Inventory logs; Pushed: session-06: ...".
- Homework named in the slides: the Inventory in-memory store comment says "PostgreSQL added as homework" (PostgreSQL persistence for Inventory Service is homework; not part of lab acceptance criteria).
- Daily Quiz: "8 Questions — 10 Minutes"; topics "Sync vs Async Decision • OpenFeign vs WebClient • JWT Propagation • ErrorDecoder".
- Pre-Session 7 reading (15 min) with knowledge check questions (verbatim): "What is Choreography Saga vs Orchestration Saga?", "What happens if Payment succeeds but Inventory fails?", "What is a Kafka consumer group?".
- Demos in the deck: "Testing Inventory Service Directly" (PROD-001 → 200 available:true; PROD-003 → 409) and "The Full Chain -- Order Checks Inventory First" (PROD-003 → REJECTED; PROD-001 → CONFIRMED, watch both services' logs).
- Seminar deck has no lab of its own — it is the theory/patterns seminar for the same session.
