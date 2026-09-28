# Session 5 — Resilience Advanced (Bulkhead · TimeLimiter · Complete Defense Layer)

Source files: Session_05_Resilience_Advanced.pdf

Deck identity: "Session 5 of 29", 2.5 Hours, Online Session, Wednesday 3:00 PM – 5:30 PM, Phase 1 — Foundation & Core Patterns. Position in phase: S1 Architecture · S2 Gateway Core · S3 Gateway Adv. · S4 Resilience CB · S5 Resilience BH (LIVE) · S6 OpenFeign · S7 Saga+Kafka · S8 Caching+Clinic. Slide 2 framing: "Last session: stop calling broken services. Today: survive SLOW ones too."

## 1. Why this topic exists

- Session 4 solved: Payment Service is BROKEN (throws errors) — Circuit Breaker opens, fails fast, fallback returns PENDING.
- Still unsolved: Payment Service is SLOW (10s instead of 200ms) but technically UP — "Circuit Breaker doesn't see this as a failure yet."
- Concrete math from the deck: 50 threads call Payment, each waits 10 seconds; Order Service thread pool: 200 threads total; "After ~6 minutes: ALL 200 threads consumed"; "New orders cannot be created -- even though Payment is 'UP'."
- Second problem framing ("Problem First -- Part 2"): Why "Slow" Is More Dangerous Than "Down": Payment 30s per request → Order has a 60-second HTTP timeout so it waits → 10 requests × 30 seconds = 300 seconds of thread blocking → 200 threads all consumed after ~6 minutes.
- Stated solution: "Do not wait indefinitely. If Payment takes > 2 seconds → fail fast. TimeLimiter enforces this at the Resilience4j level -- cleaner than HTTP timeouts."
- Bulkhead framing: "Bulkhead limits the BLAST RADIUS when a service is merely slow."

## 2. Core concepts

- Bulkhead metaphor (verbatim): "A ship's hull is divided into watertight compartments. If one floods, the others are sealed off -- the ship stays afloat. One hole does not sink everything." Diagram: OrderProduct unaffected, OrderInventory unaffected, OrderPayment "Flooded -- isolated here".
- Without Bulkhead: Payment slow eats all 200 threads; Inventory also dies; entire Order Service goes down. With Bulkhead (Semaphore): PaymentService max 10 concurrent, InventoryService max 20 concurrent; only 10 threads affected; remaining 190 threads stay free; "Only Payment-related orders are QUEUED".
- Semaphore Bulkhead vs ThreadPool Bulkhead (engineering decision):
  - Semaphore: limits number of concurrent calls; caller thread; blocks if limit reached; best for Reactive / WebFlux services; config key `max-concurrent-calls`; "Used for OrderPayment".
  - ThreadPool: executes calls in separate thread pool; returns immediately — non-blocking; best for traditional blocking services; config key `maxThreadPoolSize + queueCapacity`; "Discussed as alternative".
- TimeLimiter: without it, thread blocked the whole 30s; with `timeout-duration: 2s`: 0–2s wait → at 2s TIMEOUT → cancel future → timeoutFallback() → PENDING returned immediately. "HTTP timeout is a blunt instrument -- it just cuts the connection. TimeLimiter is smarter: it cancels the Future AND records the failure with the CircuitBreaker."
- Why TimeLimiter requires CompletableFuture: "Java cannot reliably interrupt a running thread mid-execution. There is no 'handle' to cancel -- the thread just keeps blocking." A Future IS a cancellable handle; TimeLimiter calls `future.cancel()` at the 2-second mark -- "the only way to enforce a hard timeout in Java". Hence the payment call is wrapped in `CompletableFuture.supplyAsync()`.
- Execution order of the four annotations (slide 14 and "THE BIG PICTURE"): 1. Bulkhead (slot available?) → 2. TimeLimiter (within 2s?) → 3. CircuitBreaker (CB closed?) → 4. Retry (attempt call) → 5. Actual call `paymentService.processPayment()`. "Outermost protects first. If Bulkhead's slot is full, the call never even reaches TimeLimiter, CircuitBreaker, or Retry."
- Exception → fallback mapping: BulkheadFullException → bulkheadFallback(); TimeoutException → timeoutFallback(); Rejected → paymentFallback(); "Each retry is a new attempt through the CB".
- Pattern → failure mode summary (slide 18): Bulkhead → thread pool exhaustion → QUEUED response when >10 concurrent; TimeLimiter → slow service (not down) → PENDING after 2s; CircuitBreaker → repeated failures → OPEN, fast fail; Retry → transient single failure → Retry #1,2,3 in logs with backoff; Fallback → unrecoverable failure → graceful PENDING.

## 3. Architecture

- Normal flow: Client → Gateway → Order Service → Payment Service → APPROVED → Order: CONFIRMED.
- Failure flow: Bulkhead full (BulkheadFullException) → TimeLimiter timeout after 2s → Retry 3 attempts → CircuitBreaker OPEN → Fallback: Order PENDING.
- Order Service is where the defense layer lives; Bulkhead isolates the Payment call (`max 10 concurrent`), Inventory (max 20 per slide 5) stays unaffected.
- Async plumbing: `createOrderAsync()` returns `CompletableFuture<OrderResponse>`; controller returns `CompletableFuture<ResponseEntity<OrderResponse>>` via `.thenApply`. "Spring MVC handles CompletableFuture transparently. Client sees a normal synchronous HTTP response -- async is internal only."
- Platform state after S5: Config + Eureka + Product + Gateway (secured) from S1–3; Payment + Order with Circuit Breaker + Retry from S4; S5 = "Complete Resilience Layer -- Bulkhead + TimeLimiter".

## 4. Technologies

- Resilience4j — annotations `@Bulkhead`, `@TimeLimiter` (stacked with `@CircuitBreaker`, `@Retry` from Session 4); config namespaces `resilience4j.bulkhead.instances.*`, `resilience4j.timelimiter.instances.*`.
- Spring Boot / Spring MVC async controllers (CompletableFuture return type, `thenApply`).
- Java `CompletableFuture` (`supplyAsync`, `completedFuture`), `java.util.concurrent.TimeoutException`.
- Spring Boot Actuator — acceptance criterion: "Actuator shows both CB state AND bulkhead metrics".
- Testing tools mentioned only in troubleshooting: background `curl` jobs (`for i in {1..15}; do curl ... & done; wait`), "or k6/Gatling for true concurrency".
- Versions: the deck states NO version numbers (Resilience4j, Spring Boot, Java versions not mentioned anywhere) → UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- Bulkhead (watertight compartment isolation), Semaphore Bulkhead, ThreadPool Bulkhead, blast radius, fail fast.
- `max-concurrent-calls`, `max-wait-duration`, `timeout-duration`, `cancel-running-future`.
- `BulkheadFullException`, `TimeoutException`, `fallbackMethod`, `QUEUED`, `PENDING`, `CONFIRMED`.
- Hard timeout, cancellable handle, `future.cancel()`.
- Execution order: Bulkhead → TimeLimiter → CircuitBreaker → Retry → Actual Call.
- Thread pool exhaustion, queue/queued orders.

## 6. Code concepts

- `@Bulkhead(name = "paymentService", fallbackMethod = "bulkheadFallback")` on the existing method, stacked with `@CircuitBreaker` and `@Retry`; fallback: `public OrderResponse bulkheadFallback(OrderRequest request, BulkheadFullException ex)` → logs `[BULKHEAD] Concurrent limit reached` → returns `new OrderResponse("QUEUED", "System busy -- your order is queued")`.
- Async wrapper: `@TimeLimiter(name = "paymentService", fallbackMethod = "timeoutFallback")` on `public CompletableFuture<OrderResponse> createOrderAsync(...)` returning `CompletableFuture.supplyAsync(() -> { paymentService.processPayment(...); return new OrderResponse("CONFIRMED", payment.getTransactionId()); })`.
- `timeoutFallback(OrderRequest request, TimeoutException ex)` logs `[TIMEOUT] Payment exceeded 2s limit` and returns `CompletableFuture.completedFuture(new OrderResponse("PENDING", "Payment timed out"))`.
- Controller: `return orderService.createOrderAsync(request).thenApply(response -> ResponseEntity.ok(response));`
- Slowness simulation in Payment Service: `@Value("${payment.delay-ms:0}") private long delayMs;` and `if (delayMs > 0) { Thread.sleep(delayMs); }`.
- Test expectation: "Set payment.delay-ms=3000. Call POST /api/orders. See PENDING in ~2s, not 3s. CB records the timeout as a failure."

## 7. Configuration

```yaml
# application.yml -- Order Service
resilience4j:
  bulkhead:
    instances:
      paymentService:
        max-concurrent-calls: 10
        max-wait-duration: 0ms      # alternative: max-wait-duration: 500ms
  timelimiter:
    instances:
      paymentService:
        timeout-duration: 2s
        cancel-running-future: true
```

```yaml
# application.yml -- Payment Service
payment:
  failure-rate: 0.5   # 50% failure -- change to 0.0 to test recovery (Session 4)
  delay-ms: 3000      # 3000 (3s) to trigger the 2s TimeLimiter on Order Service
```

- Comment on the bulkhead config: "max 10 simultaneous calls to Payment; do NOT wait, do NOT queue -- fail immediately if full".

## 8. Failure scenarios

- Slow-service thread exhaustion (the core scenario): each pattern addresses a distinct failure mode — see the pattern→failure-mode table in section 2.
- Demo 1 — Bulkhead, 15 concurrent requests: 10 requests → CONFIRMED or CB/Retry fallback, "reached Payment Service"; 5 requests → QUEUED "System busy", "never reached Payment Service". "The Bulkhead protected Payment Service from overload -- 5 requests never even reached it."
- Demo 2 — Timeout timeline: t=0 request sent; t=2s `[TIMEOUT] Payment exceeded 2s limit` and response `{"status":"PENDING"}`; t=3s Payment would have responded but is never reached.
- Troubleshooting table (Common Issues & Solutions):
  - TimeLimiter not triggering on slow payment → "Verify cancel-running-future: true and method returns CompletableFuture -- not synchronous".
  - timeoutFallback() not being called → "Fallback return type must be CompletableFuture<OrderResponse> -- must match exactly".
  - Bulkhead never triggers (always passes through) → "max-wait-duration: 0ms required -- default waits indefinitely, same as no Bulkhead".
  - BulkheadFullException not caught by CB → "Bulkhead and CB have separate fallbacks -- does not propagate to paymentFallback()".
  - Concurrent test not triggering Bulkhead → "HTTP client may serialize requests -- use background & jobs or k6/Gatling for true concurrency".

## 9. Trade-offs

- Semaphore vs ThreadPool bulkhead: semaphore chosen for Order→Payment (blocking MVC stack); ThreadPool "discussed as alternative" (non-blocking, separate pool).
- `max-wait-duration: 0ms` (fail immediately, QUEUED) vs `500ms` (wait briefly for a slot before failing).
- TimeLimiter vs plain HTTP timeout: HTTP timeout "just cuts the connection"; TimeLimiter cancels the Future and records the failure with the CircuitBreaker — "cleaner than HTTP timeouts".
- Async wrapper cost: changes method signature/controller plumbing; fallback must return the exact `CompletableFuture<OrderResponse>` type; "async is internal only" so the client sees no difference.

## 10. Common mistakes

- (Slide 24, exact list — see section 8 for the fixes.) Missing `cancel-running-future: true` or returning a synchronous type so TimeLimiter silently does nothing.
- Fallback signature/return type not matching exactly (especially `CompletableFuture<OrderResponse>`).
- Omitting `max-wait-duration: 0ms` so the bulkhead waits indefinitely and never triggers.
- Expecting `BulkheadFullException` to reach the CircuitBreaker fallback — the two have separate fallbacks.
- Testing concurrency with a client that serializes requests, so the bulkhead limit is never reached.

## 11. Interview questions

Note: this deck has no section labelled "Interview Questions". The Daily Quiz topics (slide 22) are "Bulkhead Types • TimeLimiter • CompletableFuture • Full Stack Execution Order", and the engineering-decision slides contain exam-style Q&A. Questions below are derived from those slides:

- Which pattern solves which failure mode? (Bulkhead = thread pool exhaustion; TimeLimiter = slow service; CircuitBreaker = repeated failures; Retry = transient failure; Fallback = unrecoverable failure.)
- Why does TimeLimiter require CompletableFuture? (Java cannot reliably interrupt a running thread; a Future is the only cancellable handle; `future.cancel()` enforces a hard timeout.)
- In what order do the four annotations execute, and what are the consequences? (Bulkhead → TimeLimiter → CircuitBreaker → Retry → Actual Call; outermost protects first; each retry is a new attempt through the CB.)
- Difference between Semaphore and ThreadPool bulkhead, and which one did we choose and why? (Semaphore chosen for OrderPayment; ThreadPool discussed as alternative.)
- What does the client see when the bulkhead is full vs when the timeout fires? (QUEUED vs PENDING after 2s.)
- Why is HTTP timeout "a blunt instrument" compared to TimeLimiter? (It cuts the connection but does not cancel the Future or record the failure with the CB.)

## 12. What I must memorize

- Execution order: 1 Bulkhead → 2 TimeLimiter → 3 CircuitBreaker → 4 Retry → 5 Actual Call.
- Config keys and values: `max-concurrent-calls: 10`, `max-wait-duration: 0ms`, `timeout-duration: 2s`, `cancel-running-future: true`.
- Fallback statuses: full bulkhead → `QUEUED` ("System busy -- your order is queued"); timeout → `PENDING` ("Payment timed out").
- Log prefixes: `[BULKHEAD]`, `[TIMEOUT]`.
- Lab 3B acceptance criteria and the commit tag (section 17).
- That the async method must return `CompletableFuture` and the fallback type must match exactly.

## 13. What I must understand

- Why "slow" is more dangerous than "down" (CB does not see slow as failure; threads pile up; ~6 minutes to exhaust 200 threads).
- Why only 10 of 200 threads are affected with a semaphore bulkhead, and why the other 190 stay free.
- Why CompletableFuture is mandatory for a hard timeout (no cancellable handle on a running thread).
- Why the outermost annotation protects first, and how each exception maps to its own fallback.
- Why "each retry is a new attempt through the CB" matters for CB state accounting.

## 14. What I should implement from memory

- Add both yml config blocks (bulkhead + timelimiter instances for `paymentService`).
- Annotate `createOrderAsync()` with the full stack (`@Bulkhead` + `@TimeLimiter` + `@CircuitBreaker` + `@Retry`) and write both fallbacks (`bulkheadFallback` returning QUEUED, `timeoutFallback` returning PENDING as `CompletableFuture.completedFuture`).
- Convert the controller to the async signature with `.thenApply`.
- Add the `payment.delay-ms` simulation and the 15-concurrent-request test; at least 3 unit tests covering Bulkhead + TimeLimiter.
- Verify Actuator shows both CB state and bulkhead metrics.

## 15. Relationship to previous sessions

- Direct continuation of Session 4 (Circuit Breaker + Retry): "Circuit Breaker Stops Broken Calls. But What About Slow Ones?" — S5 completes the resilience layer on the same Order→Payment call.
- Where-we-are row: "S4 Resilience CB" → "S5 Resilience BH (LIVE)".
- Platform progress recap: "Sessions 1-3: Config + Eureka + Product + Gateway (secured)"; "Session 4: Payment + Order -- Circuit Breaker + Retry"; "Session 5: Complete Resilience Layer -- Bulkhead + TimeLimiter".
- The existing `@CircuitBreaker`/`@Retry` annotations from S4 remain stacked on the same method; the S4 test config `payment.failure-rate` is reused ("change to 0.0 to test recovery (Session 4)").

## 16. Relationship to future sessions

- Next session: "Session 6 -- Inter-Service Communication: OpenFeign & WebClient" — Monday, 3:00–5:30 PM, Online.
- Pre-Session 6 reading (15 min) is specified: "OpenFeign & Declarative HTTP Clients", spring.io/projects/spring-cloud-openfeign.
- The full resilience stack built here is applied to the Feign call in S6 (`createOrderAsync` gains the inventory check inside its `supplyAsync` block).
- Later sessions per roadmap strip: S6 OpenFeign, S7 Saga+Kafka, S8 Caching+Clinic (Phase 1 ends).

## 17. Lab relationship

- Hands-on slide: "Lab 3B -- Full Resilience Stack on OrderPayment" with 3 items:
  1. "Add Semaphore Bulkhead — max-concurrent-calls: 10, bulkheadFallback returns QUEUED"
  2. "Add TimeLimiter with Async Wrapper — 2s timeout, CompletableFuture, timeoutFallback returns PENDING"
  3. "Write Unit Tests — Minimum 3 tests covering Bulkhead + TimeLimiter behaviour"
- Definition of Done (Lab 3B Acceptance Criteria, 7 items):
  - "15 concurrent requests: ~10 CONFIRMED/fallback, ~5 QUEUED"
  - "payment.delay-ms=3000 → PENDING response arrives in ~2 seconds"
  - "Actuator shows both CB state AND bulkhead metrics"
  - "Logs show [BULKHEAD] and [TIMEOUT] prefixes for fallbacks"
  - "Full stack on createOrderAsync(): @Bulkhead+@TimeLimiter+@CircuitBreaker+@Retry"
  - "All 3 unit tests pass: mvn test"
  - "Commit: session-05: add-bulkhead-and-timelimiter-to-order-payment"
- Checkpoint commit slide ("BEFORE SESSION 6") repeats: "15 concurrent → ~5 QUEUED; 3s delay → PENDING in ~2s; Both fallbacks return correct status; Full annotation stack on createOrderAsync(); Pushed: session-05: ...".
- Daily Quiz: "8 Questions — 10 Minutes"; topics "Bulkhead Types • TimeLimiter • CompletableFuture • Full Stack Execution Order".
- Pre-Session 6 reading (15 min) with knowledge check questions: "What is the advantage of OpenFeign over RestTemplate?", "When should Order Service call Inventory synchronously?", "What does @EnableFeignClients do?".
- No separate homework beyond the lab/DoD is mentioned; the deck's only other exercise-like item is the 15-request concurrency test in the demo.
