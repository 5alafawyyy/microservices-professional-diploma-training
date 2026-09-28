# Lab 03B — Session 5

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Add Bulkhead and TimeLimiter to isolate thread exhaustion.

## 2. Problem Being Solved
Slow downstream services cause upstream thread pools to fill up, hanging the entire application.

## 3. Architecture
* **Before the lab:** Order service vulnerable to thread exhaustion if Payment service is slow but not throwing errors.
* **After the lab:** Order service limits concurrent calls (Bulkhead) and enforces strict async timeouts (TimeLimiter).
* **Architectural Impact:** Prevents cascading resource exhaustion.

## 4. Concepts Explained
Semaphore Bulkhead, ThreadPool Bulkhead, TimeLimiter, Async execution.

## 5. Prerequisites
Lab 03A.

## 6. Precise Implementation Tasks
1. Add @Bulkhead.
2. Add @TimeLimiter.
3. Return CompletableFuture.

## 7. Important Configuration
`resilience4j.timelimiter.instances.*`, `resilience4j.bulkhead.instances.*`

## 8. Expected Files/Components
`order-service/.../PaymentClient.java`

## 9. Acceptance Criteria
Calls exceeding timeout immediately trigger fallback; concurrent calls are capped.

## 10. Verification Commands/Tests
Add `Thread.sleep` to payment service.

## 11. Expected Behavior
TimeLimiter triggers fallback after configured duration.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** TimeLimiter without CompletableFuture return type fails at runtime.
* **Troubleshooting Guidance:** Ensure method returns `CompletableFuture` and class is proxied by Spring.

## 13. Relationship to Curriculum
* **Context:** Completes Resilience4j stack for Order Service.
* **Source Evidence:** Official document `session-05-lab-3b.md`.
* **Related Commit(s):** `session-05: add-bulkhead-and-timelimiter`
