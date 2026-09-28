# Session 4 — Resilience Patterns · Circuit Breaker · Retry · Exponential Backoff · Graceful Degradation

Source files: `Session_04_Resilience_CircuitBreaker.pdf`

> Slides deck title: "Session 4 — Resilience Patterns / Circuit Breaker · Retry · Exponential Backoff · Graceful Degradation". Slot: Monday 3:00–5:30 PM (Online). Position: Session 4 of 29.

## 1. Why this topic exists

The deck opens with the **Black Friday story**: on peak sales day, 50,000 users hit the platform at the same time. Everything is fine until...

- **Payment Service** starts getting slow: it takes **10 seconds** instead of the usual **200ms**.
- **Order Service** calls Payment and waits. It has **200 threads**. All 200 threads are now waiting on Payment.
- Order Service has **no threads left** to handle new requests.
- Now the **Gateway** calls Order Service — and Order gets no response.
- The Gateway returns **503 to ALL users** — even users browsing Products (a completely unrelated service).
- The team restarts... it gets worse. They **add retries** to "be safe" — that makes it worse.
- Root cause: **ONE slow service. Not even down — just slow. This is Cascading Failure.**

Why retries made it worse (as taught in the story): every retry is an extra request piled onto an already-overloaded Payment Service.

The session's stated approach: **BOTH** resilience strategies:
- **Fail Fast** — from the **Circuit Breaker** (stop calling a failing service immediately).
- **Fail Safe** — via a **fallback response** (return something useful instead of an error).

## 2. Core concepts

- **Partial Failure vs Cascading Failure** — one component failing should not take down the whole system; without resilience, it does (cascade).
- **Fail Fast** — stop hammering a failing dependency instead of waiting on every call.
- **Fail Safe** — degrade gracefully: answer with a fallback instead of an error.
- **Circuit Breaker** — a state machine (CLOSED / OPEN / HALF-OPEN) that wraps a remote call and short-circuits it when the failure rate is too high.
- **Retry** — re-attempt transient failures, with **Exponential Backoff** to avoid thundering herd.
- **Graceful Degradation** — the fallback response (e.g., order accepted as PENDING while payment is unavailable).
- **Resilience4j patterns overview (deck table):** Circuit Breaker, Retry, Fallback (**today, Session 4**); Bulkhead, Rate Limiter, TimeLimiter (**Session 5**).

### Circuit Breaker state machine (deck diagram)

```
CLOSED ──(failure rate ≥ threshold)──▶ OPEN
OPEN ──(waitDuration elapsed)──▶ HALF-OPEN
HALF-OPEN ──(all probes succeed)──▶ CLOSED
HALF-OPEN ──(any probe fails)──▶ OPEN
```

Deck quote: "Without HALF-OPEN, the Circuit Breaker would stay OPEN forever."

### Circuit Breaker configuration (per the deck)

| Property | Value | Meaning |
|---|---|---|
| `sliding-window-size` | 10 | last N calls are counted |
| `failure-rate-threshold` | 50 | % failures that trips OPEN |
| `wait-duration-in-open-state` | 5s | time before trying HALF-OPEN |
| `permitted-calls-in-half-open` | 3 | probes allowed in HALF-OPEN |
| `register-health-indicator` | true | expose state via Actuator health |

### Retry — when it helps vs when it hurts (deck table)

**Helps:**
- Transient network glitch
- Temporary DB pool exhaustion
- Service restarting (2–3 seconds)
- DNS delay

**Hurts:**
- Overloaded service
- Logic error (retry will fail again, deterministically)
- Thundering herd (many clients retrying amplify the outage)
- Payment already processed

Deck warning: "**Never retry a payment call without idempotency checks** — retry = double charge."

### Exponential Backoff (deck arithmetic)

- Attempt 1 → wait **500ms × 2⁰ = 500ms**
- Attempt 2 → wait **500ms × 2¹ = 1000ms**
- Attempt 3 → wait **500ms × 2² = 2000ms**

(multiplier 2)

## 3. Architecture

Call path and where each pattern sits:

```
Client → API Gateway (8080)
          → Order Service (8082)
              └── @CircuitBreaker("paymentService", fallback = "paymentFallback")
                    └── @Retry("paymentService")  ← Retry wraps INSIDE CircuitBreaker
                          └── Payment Service (8083, called via OpenFeign/REST)
```

Order-of-wrapping taught by the deck: **Circuit Breaker wraps Retry** — flow: CB check first; if OPEN → fallback immediately; if CLOSED → retry attempts run below. Consequence stated: "**3 retry attempts = 3 failures recorded by the CB. Design your thresholds accordingly.**"

Platform progress for this session:
- **NEW Payment Service** (port **8083**) with a configurable failure rate.
- **UPDATED Order Service** with Circuit Breaker + Retry + `paymentFallback`.

## 4. Technologies

- **Resilience4j** — dependency `io.github.resilience4j:resilience4j-spring-boot3`.
- **Spring AOP** — dependency `spring-boot-starter-aop`. Deck note: "**AOP is REQUIRED — Resilience4j annotations use Spring AOP**."
- **Spring Boot Actuator** — health indicator + `circuitbreakers` endpoint for state inspection.
- **Spring Boot 3.x** (starter name `resilience4j-spring-boot3`).
- Exact Resilience4j **version number**: UNKNOWN — REQUIRES SOURCE REVIEW (deck specifies artifacts, not versions).
- (Context from earlier sessions: Java 21, Spring Boot 3.3.x, Spring Cloud 2023.x — not repeated in this deck's slides.)

## 5. Important terminology

- **Cascading Failure** — failure of one service taking down its callers, and their callers, chain-wise.
- **Fail Fast / Fail Safe** — stop calling vs degrade gracefully.
- **Sliding Window (COUNT_BASED)** — counts the last N calls (here 10) to compute failure rate.
- **Failure Rate Threshold** — % of failures (here 50) that trips OPEN.
- **Wait Duration in Open State** — time (here 5s) before HALF-OPEN probing.
- **HALF-OPEN** — probe state using `permitted-calls-in-half-open` (3) test calls.
- **Fallback (method)** — alternative method returning a degraded response (`paymentFallback`).
- **Retry / max-attempts / wait-duration** — re-attempt policy and base delay (500ms).
- **Exponential Backoff multiplier** — each wait multiplied by 2.
- **Thundering Herd** — synchronized retries overwhelming an already-overloaded service.
- **Idempotency** — the safety property required before retrying payments (deck: "retry = double charge").
- **RetryRegistry / EventPublisher** — Resilience4j API used by `RetryLogger` to observe retry events.

## 6. Code concepts

### Circuit Breaker annotation + fallback (Order Service)

```java
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
```

Fallback:

```java
public OrderResponse paymentFallback(OrderRequest request, Throwable ex) {
    return new OrderResponse("PENDING", "Will retry payment");
}
```

Critical rule from the deck: "**Fallback signature must match the original EXACTLY + one extra `Throwable` parameter. If it doesn't match, Spring silently ignores it.**"

### Retry annotation

```java
@Retry(name = "paymentService") // Retry wraps INSIDE CircuitBreaker
```

### Payment Service stub with controlled failures

```java
if (random.nextInt(10) < 5) {
    throw new RuntimeException("Payment Service unavailable");
}
return new PaymentResponse("APPROVED", request.getAmount());
```

(≈50% failure rate — aligned with the `failure-rate-threshold: 50` config.)

### RetryLogger (observability for retries)

- `@Component` class, `@Autowired RetryRegistry retryRegistry`.
- `@PostConstruct attachRetryListeners()`:
  - `retryRegistry.retry("paymentService").getEventPublisher()`
  - `.onRetry(...)` / `.onSuccess(...)` handlers.
- Logs lines like `[RETRY] Attempt #n`.

## 7. Configuration

### Maven dependencies

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

### application.yml (Order Service)

```yaml
resilience4j:
  circuitbreaker:
    instances:
      paymentService:
        sliding-window-type: COUNT_BASED
        sliding-window-size: 10
        failure-rate-threshold: 50
        wait-duration-in-open-state: 5s
        permitted-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
        register-health-indicator: true
  retry:
    instances:
      paymentService:
        max-attempts: 3
        wait-duration: 500ms
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2
        retry-exceptions:
          - java.lang.RuntimeException
        ignore-exceptions:
          - java.lang.IllegalArgumentException

management:
  health:
    circuitbreakers:
      enabled: true
  endpoints:
    web:
      exposure:
        include: health,circuitbreakers
```

## 8. Failure scenarios

- **The Black Friday cascade itself:** one slow service → thread pool exhaustion in the caller → 503 for everyone (including unrelated features). Retries amplify it.
- **CB never opens:** `slidingWindowSize` is too large for the observed traffic (deck troubleshooting: try `size: 5`, `threshold: 50`).
- **No AOP dependency:** the annotation has **no effect** (deck troubleshooting: missing `spring-boot-starter-aop`).
- **Fallback signature mismatch:** Spring **silently ignores** the fallback (no error, no fallback).
- **Retry not visible in logs:** need the `RetryLogger` and a **matching instance name** (`paymentService`).
- **404 on actuator endpoint:** endpoint not exposed — check `management.endpoints.web.exposure.include`.
- **Retry on payment without idempotency:** double charge (deck's explicit warning).

## 9. Trade-offs

- **Fail Fast vs Fail Safe** — deck explicitly says "**Our approach: BOTH**": fail fast from the Circuit Breaker + fail safe via the fallback response.
- **Retry helps vs hurts** — helps on transient faults (network glitch, DB pool exhaustion, restart, DNS); hurts on overload/logic errors/thundering herd/already-processed payments (see §2 table).
- **CB wrapping Retry** — wrapped this way, 3 retry attempts record 3 failures against the CB window; thresholds must be designed with that multiplier in mind.
- **OPEN state cost** — while OPEN, calls are rejected immediately even if the dependency has recovered; traded for protection of the caller's threads. HALF-OPEN exists to re-test recovery; "without HALF-OPEN the Circuit Breaker would stay OPEN forever."

## 10. Common mistakes

- Adding retries during an outage to "be safe" — makes the cascade worse (from the Black Friday story).
- Retrying payments without idempotency checks ("retry = double charge").
- Forgetting `spring-boot-starter-aop` → annotations silently do nothing.
- Getting the fallback signature wrong (must match + extra `Throwable`) → silently ignored.
- Setting `slidingWindowSize` too large → CB never opens.
- Forgetting to expose actuator endpoints / enable `management.health.circuitbreakers.enabled` → no state visibility.
- Ignoring that retries multiply CB-recorded failures (3 attempts = 3 failures).

## 11. Interview questions

- Quiz topics listed by the deck: "**Circuit Breaker States · Fallback Methods · Retry vs Idempotency · Exponential Backoff**."
- The deck itself does not list full interview questions: UNKNOWN — REQUIRES SOURCE REVIEW.

## 12. What I must memorize

Memorize — stated explicitly or shown as key facts on the slides:

- The four CB state transitions and their triggers: CLOSED → (failure rate ≥ threshold) → OPEN → (waitDuration) → HALF-OPEN → (all probes succeed) → CLOSED; any HALF-OPEN failure → OPEN.
- Default-for-this-session values: `sliding-window-size 10`, `failure-rate-threshold 50`, `wait-duration-in-open-state 5s`, `permitted-calls-in-half-open 3`.
- Retry config: `max-attempts 3`, `wait-duration 500ms`, `enable-exponential-backoff true`, `exponential-backoff-multiplier 2`.
- Backoff arithmetic: 500 × 2⁰ = 500ms → 500 × 2¹ = 1000ms → 500 × 2² = 2000ms.
- Both dependencies: `resilience4j-spring-boot3` + **AOP required**.
- Fallback rule: signature matches original EXACTLY + one extra `Throwable`; mismatch → silently ignored.
- Wrapping order: Circuit Breaker wraps Retry; 3 retry attempts = 3 CB-recorded failures.

## 13. What I must understand

Understand (per what the slides teach):

- **Why** partial failure becomes cascading failure (thread pool exhaustion at the caller; 503 for unrelated features).
- **Why** both strategies are needed (fail fast + fail safe) and how CB and fallback divide the work.
- **Why** HALF-OPEN exists ("Without HALF-OPEN, the Circuit Breaker would stay OPEN forever").
- **When** retry helps vs hurts (transient vs overload/logic/already-processed).
- **Why** payments must be idempotent before being retried.
- **Why** CB-wrapping-Retry changes how many failures the CB window sees.

## 14. What I should implement from memory

Per the deck (Lab 3A steps and demo):

- Create a **Payment Service** (new service, port **8083**) with a **configurable failure rate** and a stub returning `PaymentResponse("APPROVED", amount)`.
- Apply `@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")` on the Order Service payment call.
- Write `paymentFallback(OrderRequest, Throwable)` returning `OrderResponse("PENDING", "Will retry payment")`.
- Add `@Retry(name = "paymentService")` with 3 attempts, 500ms → 1000ms exponential wait.
- Add a `RetryLogger` (`@Component`, `RetryRegistry`, `@PostConstruct`, `EventPublisher.onRetry/onSuccess`) logging `[RETRY] Attempt #n`.
- The full `application.yml` block from §7 (circuitbreaker + retry instances + actuator exposure).
- Demo script: 10+ `POST /api/orders` → OPEN in logs; `/actuator/circuitbreakers` shows `state: OPEN`; after 5s → HALF_OPEN; after 3 successes → CLOSED.
- Write **minimum 3 unit tests** covering CB + retry behaviour (Lab 3A step 4).

## 15. Relationship to previous sessions

- Builds on the running platform from Sessions 1–3: Eureka/Config (S1), API Gateway (S2), Gateway Security/rate limiting (S3).
- Adds the resilience layer between **Order Service (8082)** from Session 1's platform map and a **new Payment Service (8083)**, both behind the Gateway (8080).
- Session 3's `RequestRateLimiter` protected the gateway edge; Session 4 protects **service-to-service** calls inside the platform.

## 16. Relationship to future sessions

- **Session 5 — Resilience Advanced: Bulkhead & TimeLimiter** (deck lists Bulkhead, Rate Limiter, TimeLimiter as the remaining Resilience4j patterns; pre-session reading: Resilience4j — Bulkhead & TimeLimiter, resilience4j.readme.io).
- Pre-Session 5 knowledge check (from the deck): difference Bulkhead vs Circuit Breaker; why TimeLimiter requires `CompletableFuture`; what is thread pool exhaustion.

## 17. Lab relationship

**Lab 3A — "Circuit Breaker & Retry on Payment Service"** (deck terms):

1. **Create Payment Service with Controlled Failures** — new service, port **8083**, configurable failure rate.
2. **Apply `@CircuitBreaker` on Order Service** — fallback returns a **PENDING** order response.
3. **Add Retry with Exponential Backoff** — **3 attempts**, **500ms → 1000ms** wait.
4. **Write Unit Tests** — **minimum 3 tests** covering CB + retry behaviour.

Acceptance criteria (deck):
- **CONFIRMED** on success; **PENDING** on consistent failure.
- CB state **OPEN** after 5+ failures; **HALF_OPEN** after 5s.
- Retry logs **#1/#2/#3**; exponential timing **500 → 1000ms**.
- **`mvn test`** passes.
- Commit: **`session-04: add-circuit-breaker-and-retry-on-order-payment`**.

Checkpoint / Definition of Done (deck):
- CB opens (visible as **OPEN** in **Actuator**).
- Fallback returns **PENDING**.
- Retry attempts visible in logs.
- Exponential backoff timing observed.
- "**Pushed: session-04: ...**".

Demo verification (deck): 10+ `POST /api/orders` → after ~5 failures **OPEN** appears in logs; `/actuator/circuitbreakers` shows `state: OPEN`; after **5s** → **HALF_OPEN**; after **3 successes** → **CLOSED**.

Troubleshooting (deck):
- Annotation has no effect → missing `spring-boot-starter-aop`.
- Fallback silently ignored → signature mismatch.
- CB never opens → `slidingWindowSize` too large (try `size: 5`, `threshold: 50`).
- No retry lines in logs → use `RetryLogger` with matching instance name.
- **404** on actuator → add `health,circuitbreakers` to `management.endpoints.web.exposure.include`.
