# Session 22 — Advanced Patterns: Outbox, Idempotency & API Versioning

Source files: `Session_22_Advanced_Patterns.pdf` (23 pages, instructor deck — header: "Session 22 — Advanced Patterns: Outbox, Idempotency & API Versioning — Closing Technical Debt from Sessions 4, 7, and 8 · Architecture Clinic #2 Preparation", Monday, 3:00–5:30 PM, 2.5 hours, Phase 3 · Advanced & Enterprise); `session_22_Advanced-Patterens.pdf` (64 pages, full student-tutorial version, sections 1–68). Duplicate note: `session_22_Advanced_Patterens.pdf` is byte-identical to `session_22_Advanced-Patterens.pdf` (identical MD5 `d134819d7283de3168715ae050db4c8a`, both 64 pages) and was read only once. The 23-page instructor deck is a DIFFERENT, shorter version and was read in full.

## 1. Why this topic exists

- The session is a Technical Debt Register closeout, not new ground: three items named since Phase 1 (Session 8 Architecture Clinic #1 and Session 12 homework) — "No idempotency on payment retry — duplicate charge risk" and "No API versioning strategy — breaking change risk" — plus a third pattern (Outbox) closing a gap nobody noticed: Session 7's Saga DB commit succeeding while the Kafka publish that follows it fails.
- Three technical-debt questions the platform's earlier sessions introduced:
  1. What if the database transaction succeeds but the Kafka event is never published? → dual-write problem → Transactional Outbox Pattern.
  2. What if a payment request is retried after the first payment actually succeeded? → same business action could happen twice → Idempotency Keys.
  3. What happens when we need a breaking API change? → existing clients must not suddenly stop working → API Versioning and a deprecation window.
- Session 22 is deliberately practical: "We will modify the platform rather than build a separate toy application."
- Session 24 will hold Architecture Clinic #2; today's work is the LAST scheduled item on the Session 8/12 Technical Debt Register before that review, so Clinic #2 can ask: "Of the debt we named in Phase 1, what did we actually fix, and what did we consciously decide to leave, and why?" (Full discussion and Technical Debt Register v2 happen in Session 24 — not today.)

## 2. Core concepts

- Dual-write problem: `orderRepository.save(order)` and `kafkaTemplate.send(...)` are two independent operations against two separate systems (PostgreSQL and Kafka) with no single transaction covering both; any ordering (DB→Kafka or Kafka→DB) has a failure window.
- Transactional Outbox pattern: put the event into the SAME local database transaction as the business change — write `orders` + `outbox_events` in one PostgreSQL transaction; both database writes succeed or both roll back. After commit, a separate Outbox Publisher reads the outbox and publishes to Kafka.
- Publishing options: Polling Publisher (scheduled task periodically queries `WHERE published = false`) vs CDC (change data capture — a tool such as Debezium reads the database transaction log/WAL and publishes downstream). Course decision: POLLING PAYER — actually "Polling Publisher is the selected implementation because it teaches the Outbox pattern without introducing another infrastructure layer."
- Delivery semantics: Outbox provides AT-LEAST-ONCE delivery, NOT exactly-once (crash between publish success and `published=true` commit → event re-sent after restart). Duplicates are acceptable because the consumer must process idempotently (unique event identity or business state check).
- Idempotency key: a unique identifier for ONE logical operation; the same logical payment request must use the SAME key across all retry attempts; the server recognizes the key and returns the original stored result instead of executing again.
- Key belongs to the logical operation, not the HTTP attempt: one logical payment may have Attempt 1/2/3 — all three must use the SAME idempotency key.
- The critical retry rule: the key must be generated ONCE before (outside) the retry-wrapped call and passed in on every attempt.
- Concurrency race (important limitation): two simultaneous requests with the same key can both see "not found" and both charge; a simple check-then-insert is not sufficient for a fully production-grade implementation. A database uniqueness constraint helps detect duplicate insertion but does not automatically undo a payment already performed.
- Request mismatch protection: a production implementation should store a request fingerprint/hash; same key + same request → return original result; same key + different request → reject as misuse.
- Idempotency applies beyond payments: creating an order, submitting a payment, sending a command, processing a webhook, creating a shipment, charging a subscription, handling duplicate Kafka messages — whenever "same logical request + repeated delivery must not create repeated side effects".
- API Versioning: `/api/products` creates breaking-change risk; implement URI-based versioning (`/api/v1/products`); update API Gateway routes; maintain a temporary legacy route; use `Deprecation` and `Sunset` response headers; execute a practical migration/deprecation cycle.
- Important distinction: Outbox ≠ Idempotency. Outbox answers "How do I reliably record an event that must eventually be published?"; Idempotency answers "How do I prevent repeated processing of the same logical operation?" You often need both.
- Architecture Clinic #2 preparation: review the Technical Debt Register, identify what was fixed, what was intentionally left unresolved, and explain trade-offs rather than saying one design is "best".

## 3. Architecture

- Before (the problem):

```
OrderService
   |---> PostgreSQL
   |---> Kafka            <- two independent operations, failure window between them
```

- After (Transactional Outbox):

```
OrderService
   |
   v
PostgreSQL Transaction
   |---> orders
   |---> outbox_events
              |
              v
      Outbox Publisher        (scheduled poller)
              |
              v
            Kafka
              |
              v
      Idempotent Consumer
```

  The application no longer directly publishes the business event from `createOrder()`.
- Idempotency flow:

```
Request -> Read Idempotency-Key -> Does key exist?
   YES -> return stored/original result
   NO  -> Process payment -> Store result -> return result
```

  Caller view: `Order Service --(payment request, Idempotency-Key: ABC-123)--> Payment Service`; "first request → process; retry → return original result".
- API versioning architecture:

```
Old Client -> /api/products -> Legacy Compatibility Route -> /api/v1/products
New Client -> /api/v1/products
Gateway routes: product-service-v1 (Path=/api/v1/products/**) + product-service-legacy-redirect (Path=/api/products/** + RewritePath + Deprecation/Sunset headers)
```

- Combined view (how the three patterns fit): API Gateway → `/api/v1/products` → Product Service; Order Service → DB transaction (orders + outbox_events) → Outbox Publisher → Kafka → Idempotent Consumer; and Order Service → Payment Service with Idempotency-Key.
- End-to-end example taught: 1) Client `POST /api/v1/orders`; 2) Order Service — inside one PostgreSQL transaction INSERT order + INSERT outbox event, COMMIT; 3) Outbox Publisher → Kafka; 4) Payment operation with `Idempotency-Key: PAYMENT-ABC-123`; 5) Payment Service — first request: key not found → process → store; retry: key found → return stored result.
- Database tables: `orders` (+ `outbox_events`, one transaction), `idempotency_records` (PK = idempotencyKey).

## 4. Technologies

- PostgreSQL — the transactional store (orders + outbox in one local transaction; WAL cited for CDC).
- Kafka — event broker; `KafkaTemplate<String, String>`; topic `order-events`; `kafkaTemplate.send(...)` + `.get()` to await acknowledgement.
- Spring Boot / Spring Framework — `@Transactional`, `@Scheduled(fixedDelay = 1000)`, `@EnableScheduling` on a `@Configuration` class, `@Service`, `@Component`, JPA (`@Entity`, `@Table`, `@Id`, `@GeneratedValue(strategy = GenerationType.IDENTITY)`, `@Column(columnDefinition = "TEXT")`), `JpaRepository` derived queries, `@RestController`, `@RequestMapping`, `@PostMapping`, `@RequestHeader("Idempotency-Key")`, `@RequestBody`, `ResponseEntity`, `ObjectMapper` (Jackson `JsonProcessingException`), `UUID.randomUUID()`.
- Resilience4j (caller side) — existing `@Retry(name = "paymentService")` and `@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")` annotations interact with where the idempotency key is generated.
- Spring Cloud Gateway — `routes`, `Path=` predicate, `RewritePath` filter, `AddResponseHeader` filter; service URI `lb://PRODUCT-SERVICE`.
- HTTP headers — `Idempotency-Key`, `Deprecation: true`, `Sunset: Wed, 01 Oct 2026 00:00:00 GMT`.
- CDC tooling named as the alternative (not implemented): Debezium reading PostgreSQL WAL; "CDC + Debezium + Kafka Connect" named as what a larger organization may later choose.
- SQL technique for future hardening: `SELECT ... FOR UPDATE SKIP LOCKED`.
- Versions: no Spring Boot / Spring Cloud / PostgreSQL / Kafka / Debezium version numbers appear anywhere in these slides — UNKNOWN — REQUIRES SOURCE REVIEW.
- Not mentioned in this session: k6 (only in the "Next: Session 23" line), Istio/Kiali/Jaeger (S21 topic), concrete SQL DDL for the tables (only JPA entity sketches and field tables appear).

## 5. Important terminology

- Dual-write problem; failure window; PENDING order with no event; reversed-order problem (Kafka publish succeeds, DB save never happens → consumers receive OrderPlaced for an order that does not exist).
- Transactional Outbox; outbox table (`outbox_events`); Outbox Publisher; polling publisher; `published` flag; batch limit (`findTop100...`).
- Change Data Capture (CDC); PostgreSQL WAL; Debezium.
- At-least-once delivery; exactly-once (explicitly NOT guaranteed); duplicate events; idempotent consumer; unique event identity / business state check.
- Multi-instance warning: two Order Service pods can both discover the same unpublished row → duplicate publishing; production techniques named: row locking, `SELECT ... FOR UPDATE SKIP LOCKED`, claiming/lease columns, publisher ownership, CDC, Kafka producer configuration and consumer idempotency.
- Idempotency key; logical operation vs HTTP attempt; duplicate-payment problem; response lost / network timeout; retry; cached/original result.
- Request fingerprint / `request_hash` (called `requestHash`); same key + different request = misuse.
- Idempotency record fields: `idempotencyKey` (PK), `responseBody`, `statusCode`, `createdAt`.
- API Versioning; breaking change; URI-based versioning `/api/v1/products` vs `/api/v2/products`; header-based versioning (`Accept: application/vnd.api.v1+json`); query-parameter versioning (`/api/products?version=1`).
- Legacy redirect/rewriting route; compatibility route; deprecation window; `Deprecation` / `Sunset` headers; one-cycle migration strategy (4 phases).
- Technical Debt Register; Architecture Clinic #1 (Session 8) and #2 (Session 24); debt states: Fixed / Deliberately selected / Deliberately left / Future improvement.

## 6. Code concepts

- OutboxEvent entity:

```java
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String aggregateType;   // e.g. "Order"
    private String aggregateId;     // ID of the order
    private String eventType;       // e.g. "OrderPlaced"
    @Column(columnDefinition = "TEXT")
    private String payload;         // Serialized event
    private boolean published = false;
    private Instant createdAt = Instant.now();
    // getters and setters
}
```

- Repository with batch limit (not loading every unpublished event):

```java
public interface OutboxEventRepository extends JpaRepository<OutboxEvent, Long> {
    List<OutboxEvent> findTop100ByPublishedFalseOrderByCreatedAtAsc();
}
```

- OrderService.createOrder — one local transaction, NO `kafkaTemplate.send(...)` inside:

```java
@Transactional   // both writes, ONE atomic commit, or neither
public OrderResponse createOrder(OrderRequest request) {
    orderRepository.save(order);          // write 1
    OrderPlacedEvent event = new OrderPlacedEvent(...);
    OutboxEvent outboxEvent = new OutboxEvent();
    outboxEvent.setAggregateType("Order");
    outboxEvent.setAggregateId(order.getOrderId());
    outboxEvent.setEventType("OrderPlaced");
    outboxEvent.setPayload(toJson(event)); // ObjectMapper.writeValueAsString
    outboxRepository.save(outboxEvent);   // write 2 — same tx
    return new OrderResponse(order.getOrderId(), OrderStatus.PENDING, "Order received - processing...");
}
```

- OutboxPublisher — scheduled poller; waits for Kafka acknowledgement before marking published:

```java
@Component
public class OutboxPublisher {
    @Scheduled(fixedDelay = 1000)   // poll every 1 second
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> pending = outboxRepository.findTop100ByPublishedFalseOrderByCreatedAtAsc();
        for (OutboxEvent event : pending) {
            String topic = switch (event.getEventType()) {
                case "OrderPlaced" -> "order-events";
                default -> throw new IllegalStateException("Unknown event type: " + event.getEventType());
            };
            try {
                kafkaTemplate.send(topic, event.getAggregateId(), event.getPayload()).get(); // wait for ack
                event.setPublished(true);
                outboxRepository.save(event);
            } catch (Exception e) {
                // Leave the event unpublished; it will be retried by a later poll
                throw new IllegalStateException("Could not publish outbox event " + event.getId(), e);
            }
        }
    }
}
```

- Why `.get()`: `send()` is asynchronous — marking published immediately could mark complete before Kafka acknowledged. Student implementation uses `.send(...).get()`; production note: blocking on `.get()` is not necessarily best for high throughput — production can use async callbacks/futures plus batching, locking, retries, status management.
- IdempotencyRecord entity + controller:

```java
@Entity
@Table(name = "idempotency_records")
public class IdempotencyRecord {
    @Id private String idempotencyKey;          // primary key = database uniqueness guarantee
    @Column(columnDefinition = "TEXT") private String responseBody;
    private int statusCode;
    private Instant createdAt = Instant.now();
}

@PostMapping
public ResponseEntity<PaymentResponse> processPayment(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @RequestBody PaymentRequest request) {
    Optional<IdempotencyRecord> existing = idempotencyRepository.findById(idempotencyKey);
    if (existing.isPresent()) {                 // second request does NOT charge again
        IdempotencyRecord record = existing.get();
        return ResponseEntity.status(record.getStatusCode())
                .body(deserialize(record.getResponseBody(), PaymentResponse.class));
    }
    PaymentResponse response = paymentService.processPayment(request);
    // store responseBody + statusCode 200 under the key, then return
}
```

- WRONG key placement (new key per retry defeats the protection):

```java
@Retry(name = "paymentService")
public PaymentResponse callPayment(PaymentRequest request) {
    String key = UUID.randomUUID().toString();   // WRONG: Attempt 1 -> KEY-A, 2 -> KEY-B, 3 -> KEY-C
    return paymentClient.processPayment(key, request);
}
```

- CORRECT key placement (caller generates once, outside the retry-wrapped call):

```java
String idempotencyKey = UUID.randomUUID().toString();   // generated ONCE, before the @Retry-wrapped call
callPayment(request, idempotencyKey);

@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
@Retry(name = "paymentService")
public PaymentResponse callPayment(PaymentRequest request, String idempotencyKey) {
    return paymentClient.processPayment(idempotencyKey, request);  // SAME key on every retry attempt
}
```

- Controller versioning: `@RequestMapping("/api/products")` → `@RequestMapping("/api/v1/products")` (internal controller methods can remain unchanged if their contract has not changed).

## 7. Configuration

- Enable scheduling once: `@Configuration @EnableScheduling` class (empty config class in slides).
- `@Transactional` guarantees only that `orderRepository.save(order)` and `outboxRepository.save(outboxEvent)` are ONE local database transaction (BEGIN / INSERT order / INSERT outbox_event / COMMIT; on exception ROLLBACK). Important limitation: `@Transactional` does NOT create a transaction across PostgreSQL and Kafka; Kafka remains outside the database transaction — that is exactly why the publisher is a separate step.
- Gateway route for v1:

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: product-service-v1
          uri: lb://PRODUCT-SERVICE
          predicates:
            - Path=/api/v1/products/**
```

- Gateway legacy redirect/rewriting route (temporary, remove after one deprecation cycle):

```yaml
        - id: product-service-legacy-redirect
          uri: lb://PRODUCT-SERVICE
          predicates:
            - Path=/api/products/**
          filters:
            - RewritePath=/api/products/(?<segment>.*), /api/v1/products/${segment}
            - AddResponseHeader=Deprecation, true
            - AddResponseHeader=Sunset, "Wed, 01 Oct 2026 00:00:00 GMT"
```

  Old request `GET /api/products/P100` is internally rewritten to `GET /api/v1/products/P100`.
- Deprecation/Sunset semantics: compatibility response communicates `Deprecation: true` and `Sunset: Wed, 01 Oct 2026 00:00:00 GMT`; the architectural idea: do not surprise consumers with a breaking change when a controlled migration is possible.
- Polling frequency example: every 1 second (`@Scheduled(fixedDelay = 1000)`), batch of up to 100 unpublished events ordered by `createdAt`.
- No Kafka producer transactional/idempotent-producer configuration appears in the slides; the only named Kafka-related hardening is "Kafka producer configuration and consumer idempotency" (multi-instance warning list) — details UNKNOWN — REQUIRES SOURCE REVIEW.

## 8. Failure scenarios

- Crash after DB commit, before Kafka publish (without Outbox): order stays `PENDING` forever; no exception, no log line; customer sees "Order received — processing..." and it never processes; Saga does not continue (Inventory does not reserve stock).
- Reversed order fails differently: Kafka publish succeeds, app crashes, DB save never happens → consumers may receive `OrderPlaced` for an order that does not exist.
- Case analysis with Outbox: Case A — transaction never commits → both INSERTs ROLLBACK, no incomplete state; Case B — transaction commits → both records exist; crash immediately afterward → outbox record remains; on restart the publisher finds `published = false`, publishes to Kafka, event delivered.
- Crash after Kafka publish succeeds but before `published=true` commits → after restart the publisher sends the event again → duplicate delivery (this is why at-least-once, not exactly-once).
- Duplicate event consumption: if `OrderPlaced` is received twice, the consumer must not reserve inventory twice → unique event identity or business state check.
- Multiple Order Service instances: both discover the same unpublished row → duplicate publishing; the basic implementation does not coordinate concurrent publishers (see production techniques in §5).
- Duplicate payment: retry after a lost response charges the customer again (Attempt 2 → "Customer charged AGAIN").
- Concurrent same-key requests: both read not-found, both charge, both save (race) — findById followed by processing is not sufficient under concurrency.
- Same key used for a different request (ABC / amount=100 then ABC / amount=500): blindly returning the original result is wrong; store a request fingerprint and reject as misuse.
- Versioning failure modes: replacing `/api/products` directly → all consumers can break at once; deleting the legacy route immediately → old clients get 404.
- Marking outbox event published before Kafka acknowledgement → event may be lost while marked complete (send() is asynchronous).

## 9. Trade-offs

- Polling vs CDC: Polling — simple, easy to understand, no additional infrastructure, good for training and many moderate workloads; disadvantages — some delay, repeated queries overhead, multiple instances need careful coordination. CDC/Debezium — low latency, efficient at high throughput, avoids constant polling; disadvantages — more infrastructure, more operational complexity, more components to monitor. Course decision: Polling Publisher; "Debezium is worth knowing exists but adds real operational surface area for a training platform."
- `.send(...).get()` (correctness and clarity for the course) vs async callbacks/futures with batching/locking/retries/status (production note).
- Exactly-once: deliberately NOT assumed — "Complexity/trade-off" per the Technical Debt Register table; Outbox = reliable persistence + at-least-once publication.
- Advanced outbox locking (row locking, SKIP LOCKED, leases): basic implementation chosen in the course; left as "Future improvement — Course scope".
- URI-based versioning chosen (simple, visible, cacheable, works with the Session 2 Gateway Path predicate; a new major version = a genuinely new route). Header-based (Accept: application/vnd.api.v1+json) is "more correct" by some REST purists' standards but invisible in logs/browser testing and harder to demo live — "A stated trade-off, not an objectively 'correct' answer." Query parameter also possible but not selected. The lesson: "Choose a strategy deliberately and document the trade-off."
- Deprecation window: keep legacy route temporarily (clients migrate) vs removing immediately (404s) — "Do not surprise consumers."
- Architecture Clinic mindset: no requirement that every design must be the most sophisticated; polling may be correct for the current platform; a larger org may later choose CDC + Debezium + Kafka Connect — that does not mean the original decision was wrong. Architecture = requirements + constraints + trade-offs + operational reality.

## 10. Common mistakes

Seven mistakes named explicitly in the slides (Part 6):
1. Publishing directly from the transaction — assuming `@Transactional` + `orderRepository.save(...)` + `kafkaTemplate.send(...)` makes PostgreSQL and Kafka one transaction. It does not; the transaction is local to the database.
2. Marking outbox published too early — `kafkaTemplate.send(...); event.setPublished(true);` is dangerous because send() is asynchronous; wait for the Kafka acknowledgement.
3. Assuming Outbox means exactly-once — correct: Outbox = reliable persistence + at-least-once publication; consumers should tolerate duplicates.
4. Creating a new idempotency key on every retry (Retry 1 → KEY-A, 2 → KEY-B, 3 → KEY-C) — must reuse KEY-A on all attempts.
5. Reusing a key for different requests (KEY-A + payment $100, then KEY-A + payment $500) — the key identifies one logical operation; validate the request fingerprint.
6. Thinking a unique key solves everything — a database uniqueness constraint protects the record, not the external side effect; two concurrent requests can both charge; serious payment systems require concurrency and provider-level idempotency design.
7. Versioning only the controller — `@RequestMapping("/api/v1/products")` is not enough; also consider Gateway, tests, clients, documentation, external consumers, monitoring. "API versioning is an ecosystem concern, not just a controller annotation."

## 11. Interview questions

- Final Assessment (8 MCQs, with answers, from the student deck): Q1 dual-write problem = B (a database write and a Kafka publish are independent operations) · Q2 Outbox guarantee = C (durable recording of events together with the business transaction) · Q3 when to mark published = C (after successful Kafka acknowledgement) · Q4 same idempotency key received again = B (return the original stored result) · Q5 where to generate the key when the call is retried = B (once before the retry-wrapped operation) · Q6 chosen versioning strategy = C (URI-based) · Q7 why keep a legacy API route temporarily = B (to allow consumers time to migrate) · Q8 delivery semantic of a basic polling Outbox = C (at-least-once).
- Ten questions prepared for Session 24 (Architecture Clinic #2): 1) Which technical-debt item produced the greatest reliability improvement and why? 2) Why Outbox instead of directly publishing to Kafka? 3) Why polling instead of CDC? 4) Does Outbox guarantee exactly-once delivery — explain the failure window. 5) Why is consumer idempotency still necessary? 6) Why must the same idempotency key be reused across retries? 7) What happens if two requests with the same key arrive concurrently? 8) Why URI-based API versioning? 9) Why should a deprecated API not necessarily disappear immediately? 10) Which parts of the implementation are suitable for production and which need hardening?
- "What you should be able to explain without code" — whiteboard the three diagrams (Transactional Outbox; Idempotency; API Versioning flows).
- Take-Home Challenge (4 items): 1) Request Fingerprint — add `requestHash`; same key+same request → original result, same key+different request → reject. 2) Outbox Retry Information — add `attemptCount`, `lastAttemptAt`, `lastError`; expose useful logs on repeated failure. 3) Outbox Concurrency — research safe claiming with `SELECT ... FOR UPDATE SKIP LOCKED`; explain the trade-off first, do not implement blindly. 4) API v2 — design `/api/v2/products` with one intentional breaking change while `/api/v1/products` keeps working; explain Gateway routing for both.
- Daily quiz in class: 8 questions · 10 minutes · Google Forms or Kahoot.
- Instructor-deck framing question ("Architecture Clinic #2 can ask"): "Of the debt we named in Phase 1, what did we actually fix, and what did we consciously decide to leave, and why?"

## 12. What I must memorize

- The three mental-model sentences: Outbox — "Record the event atomically with the business change, then publish it asynchronously." Idempotency — "Give one logical operation one stable key, and reuse that key across retries." API Versioning — "Change contracts deliberately and give consumers a migration path."
- Problem→pattern table: DB update + Kafka event out of sync → Transactional Outbox; same request can execute multiple times → Idempotency; API contract can break consumers → API Versioning.
- Delivery semantics: Outbox = AT-LEAST-ONCE (not exactly-once); consumers must tolerate duplicates.
- The retry rule: key generated ONCE before the retry-wrapped operation; same key on every attempt.
- The 8 MCQ answers (B, C, C, B, B, C, B, C) and the three whiteboard flows.
- OutboxEvent fields (id, aggregateType, aggregateId, eventType, payload, published, createdAt); IdempotencyRecord fields (idempotencyKey, responseBody, statusCode, createdAt).
- Key configuration strings: `@Scheduled(fixedDelay = 1000)`; `@EnableScheduling`; `Path=/api/v1/products/**`; `RewritePath=/api/products/(?<segment>.*), /api/v1/products/${segment}`; `Deprecation: true`; `Sunset: Wed, 01 Oct 2026 00:00:00 GMT`.
- The seven named mistakes.

## 13. What I must understand

- Why the dual-write gap exists (two systems, no shared transaction) and why reversing the order does not fix it.
- Why `@Transactional` only covers the two PostgreSQL operations and not Kafka — and why the publisher is therefore a separate step.
- Why Outbox gives at-least-once (crash after publish, before `published=true` commit → re-send) and why duplicates are acceptable given idempotent consumers.
- Why multi-instance publishing needs coordination (row locking, SKIP LOCKED, leases, ownership, CDC).
- Why the idempotency key must survive unchanged across retries, and why generating it inside the retried method defeats the pattern.
- Why a simple check-then-insert has a concurrency race; what the database uniqueness constraint can and cannot protect.
- Why a request fingerprint is needed (same key + different request must be rejected).
- Why the course chose polling over CDC, and why polling can still be the correct decision at this scale.
- Why URI-based versioning was chosen and what trade-off was accepted; why the legacy route + Deprecation/Sunset window is kept for one cycle.
- When the patterns apply beyond payments (orders, commands, webhooks, shipments, subscriptions, duplicate Kafka messages).
- The Clinic mindset: what was fixed vs deliberately left (polling vs CDC = deliberately selected; exactly-once = deliberately left; advanced outbox locking = future improvement), and how to justify each.

## 14. What I should implement from memory

- Outbox (student deck Lab 1): create `OutboxEvent` with the 7 fields; create `OutboxEventRepository`; modify `OrderService.createOrder()` to save Order, create OrderPlaced event, save OutboxEvent inside `@Transactional`; remove the direct `kafkaTemplate.send(...)` from `createOrder()`; create `OutboxPublisher` using `@Scheduled`; verify `published = false` before publishing and `published = true` after successful Kafka acknowledgement.
- Outbox recovery test (Lab 2): start platform; create order; confirm order exists; confirm outbox row exists; stop Order Service before the next polling cycle; verify row remains unpublished; restart Order Service; verify Kafka receives `OrderPlaced`; verify the Saga continues.
- Idempotency (Lab 3): create `IdempotencyRecord` (idempotencyKey, responseBody, statusCode, createdAt); modify the payment endpoint to require `Idempotency-Key`; Request 1 with `TEST-123` → payment processed; Request 2 with the same key → original payment result returned, no second processing.
- Retry behavior (Lab 4): generate the key once (`UUID.randomUUID().toString()`), pass it into the retry-wrapped method, verify all attempts use the SAME key (Attempt 1/2/3 → KEY-123).
- API Versioning (Lab 5): change `/api/products` to `/api/v1/products`; update Gateway; add the temporary legacy route `/api/products/**` → `/api/v1/products/**`; add `Deprecation: true` and `Sunset: Wed, 01 Oct 2026 00:00:00 GMT`; test both URLs.
- Verification checklist from memory: Outbox — one transaction, direct publish removed, publisher polls, ack marks published, failure leaves event for retry, understand at-least-once; Idempotency — key required, first request performs, retry returns original, key generated outside the retried method, DB key unique, understand concurrent-request limitation; API Versioning — `/api/v1/products` exposed, Gateway v1 route, legacy route temporary, Deprecation header returned, Sunset communicated, understand migration cycle.
- Take-home challenges (fingerprint; outbox retry fields; SKIP LOCKED research with trade-off explanation; API v2 design) as practice extensions.

## 15. Relationship to previous sessions

- Closing technical debt from Sessions 4, 7, and 8 (both decks' subtitles).
- Session 1 — the ACID lesson is cited as the guarantee that makes the two-write transaction atomic.
- Session 2 — the Gateway Path predicate is why URI versioning was chosen; the gateway routing and service API contracts must evolve together.
- Session 4 — the duplicate-payment problem; the exact Session 4 warning quoted (Assessment Bank S04-Q05): "@Retry(maxAttempts=3) on a method calling Payment Service. Payment succeeds on attempt 1 but the response is lost. Retry attempts 2 and 3 may process the payment again — the customer is charged 2 or 3 times."
- Session 7 — the Saga's `OrderService.createOrder()` dual write (orderRepository.save then kafkaTemplate.send) and the saga flow that must continue on OrderPlaced. Instructor deck adds: the Saga consumers already check the current SagaState before acting — "this idempotency guard — built for the Saga — is exactly what makes at-least-once safe."
- Session 8 — Architecture Clinic #1 Technical Debt Register (idempotency gap, API versioning gap named there); Session 12 homework (debt items named and understood since Phase 1).
- Row in the S22 Technical Debt Register: Polling vs CDC "Originally Identified: Session 22 — Current State: Polling — Decision: Deliberately selected — Reason: Simplicity"; Exactly-once messaging: "Session 22 — Not assumed — Deliberately left — Complexity/trade-off"; Advanced outbox locking: "Session 22 — Basic implementation — Future improvement — Course scope".
- Phase 3 roadmap strip in the instructor deck: S17 Observ. → S18 CQRS → S19 Sec. Pt1 → S20 Sec. Pt2 → S21 Svc Mesh → S22 Adv. Pat. (LIVE) → S23 Perf. → S24 Arch. Cl. 2.

## 16. Relationship to future sessions

- Session 23 — Performance & Load Testing (with k6): Session 23's material explicitly says to consider the Session 22 Idempotency mechanism when load-testing `POST /api/orders` ("if the API supports Idempotency-Key, the test should use an appropriate test strategy rather than accidentally creating uncontrolled duplicate business operations").
- Session 24 — Architecture Clinic #2: the 10 prepared questions above; Technical Debt Register updated marking items RESOLVED with commit references; Final Technical Debt Register v2 happens in Session 24.
- Platform capability added (both decks): "Production-Grade Reliability & API Discipline" — the Saga's dual-write gap closed, payment retries can no longer double-charge, the platform has a real, dated API versioning strategy. Services updated: order-service (OutboxEvent + OutboxPublisher), payment-service (IdempotencyRecord handling), product-service + api-gateway (/api/v1/ + legacy redirect).
- Larger-organization evolution path named: CDC + Debezium + Kafka Connect.

## 17. Lab relationship

- Instructor deck — **Lab 18 — Close One Technical Debt Item End-to-End**: "Choose ONE of the three patterns and implement it fully — depth over breadth."
  - Option A — Transactional Outbox: OutboxEvent + OutboxPublisher; verify a killed process still publishes on restart.
  - Option B — Idempotency Keys: IdempotencyRecord + PaymentController; same key twice → only ONE charge.
  - Option C — API Versioning: `/api/v1/` prefix + Gateway legacy redirect with Deprecation/Sunset headers.
  - Duration: "10 min in-session + complete as homework" · Task D (all trainees): update the Technical Debt Register.
  - Acceptance criteria (exact): ONE of the three patterns fully implemented and verified; the specific failure mode the pattern addresses is demonstrably fixed; the Technical Debt Register is updated marking the item RESOLVED with a commit reference; a one-sentence prioritization note for each of the other two patterns; minimum 2 unit tests pass for the chosen pattern's core logic.
  - Checkpoint commit named in slides: `session-22: close-[outbox|idempotency|versioning]-technical-debt`.
- Student-tutorial deck — "PART 5 — LAB": Lab Goal checklist ([ ] Order Service uses Outbox / [ ] Payment Service supports Idempotency-Key / [ ] Product API uses /api/v1) plus five step-by-step labs: Lab 1 — Implement Outbox (6 tasks, see §14); Lab 2 — Test Outbox Recovery (9-step test + success criteria: crash → event is NOT lost → restart → outbox publisher retries); Lab 3 — Implement Idempotency (TEST-123 twice, second returns original result); Lab 4 — Test Retry Behavior (verifies SAME KEY on attempts 1–3); Lab 5 — API Versioning (both URLs tested). Closed by the Verification Checklist for Outbox / Idempotency / API Versioning.
- Demo named in the student deck ("19. Demo — Prove the Pattern"): start PostgreSQL, Kafka, Order Service, Inventory Service; create an order; immediately stop Order Service before the next polling cycle; inspect `orders` (PENDING) and `outbox_events` (published = false); restart Order Service → publisher finds unpublished → publishes → `published = true` → Saga continues.
- No separate graded homework beyond Lab 18's completion and the Task D debt register update is named in the instructor deck; the take-home challenges (4 items) are the student-deck extension material.
