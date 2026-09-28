# Lab 03A — Session 4

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Scaffold Order and Payment services; apply Circuit Breaker and Retry.

## 2. Problem Being Solved
Synchronous inter-service calls fail cascadingly when downstream services crash.

## 3. Architecture
* **Before the lab:** No inter-service resilience.
* **After the lab:** Order Service protected by Resilience4j Circuit Breaker against Payment Service failures.
* **Architectural Impact:** Introduces fault tolerance.

## 4. Concepts Explained
Circuit Breaker states (Closed, Open, Half-Open), Exponential Backoff Retry.

## 5. Prerequisites
Lab 02B.

## 6. Precise Implementation Tasks
1. Scaffold services.
2. Add Resilience4j dependency.
3. Add @CircuitBreaker and @Retry.

## 7. Important Configuration
`resilience4j.circuitbreaker.instances.*`

## 8. Expected Files/Components
`order-service`, `payment-service`

## 9. Acceptance Criteria
Order service invokes fallback method when payment service is down.

## 10. Verification Commands/Tests
Stop payment-service and hit order creation.

## 11. Expected Behavior
Fallback response triggered immediately without waiting for standard HTTP timeout.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Fallback method signature mismatch (must match original method + Throwable).
* **Troubleshooting Guidance:** Check Actuator `/actuator/health` to see Circuit Breaker state.

## 13. Relationship to Curriculum
* **Context:** First resilience lab. Followed by Bulkhead in Lab 3B.
* **Source Evidence:** Official document `session-04-lab-3a.md`.
* **Related Commit(s):** `session-04: add-order-payment-and-circuit-breaker`
