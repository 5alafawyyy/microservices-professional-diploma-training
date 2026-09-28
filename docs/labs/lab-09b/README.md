# Lab 09B — Session 11

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement Contract Testing (Pact) and Chaos Testing (WireMock).

## 2. Problem Being Solved
Microservices break when downstream APIs change formats unexpectedly.

## 3. Architecture
* **Before the lab:** Assumed API compatibility.
* **After the lab:** Consumer-Driven Contracts ensure upstream providers don't break downstream consumers.
* **Architectural Impact:** Prevents integration regressions.

## 4. Concepts Explained
Consumer-Driven Contracts, Pact, WireMock Fault Injection.

## 5. Prerequisites
Lab 09A.

## 6. Precise Implementation Tasks
1. Write Pact consumer test in order-service.
2. Write Pact provider verification in inventory-service.
3. Use WireMock to simulate HTTP 500s.

## 7. Important Configuration
Pact maven plugin, `@PactFolder`.

## 8. Expected Files/Components
`order-service` tests, `inventory-service` tests

## 9. Acceptance Criteria
> *Reconstructed inference — not explicitly documented in the source material. Derived from reference implementation behavior.*

Pact file generated and verified successfully.

## 10. Verification Commands/Tests
Run `mvn test` in both services.

## 11. Expected Behavior
Contracts verified.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** State setup mismatch (`@State`).
* **Troubleshooting Guidance:** Ensure provider state methods correctly mock the required DB state.

## 13. Relationship to Curriculum
* **Context:** Completes Testing phase.
* **Source Evidence:** Reconstructed from reference implementation and S11 deck.
* **Related Commit(s):** `session-11: add-pact-and-wiremock-tests`
