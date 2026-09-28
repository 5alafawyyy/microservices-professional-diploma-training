# Lab 13 — Session 17

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Integrate the Observability Stack (Tracing, Metrics, Logging).

## 2. Problem Being Solved
Cannot trace a request across 4 different microservices.

## 3. Architecture
* **Before the lab:** Scattered logs in different containers.
* **After the lab:** Micrometer tracing propagates Trace IDs; Zipkin aggregates them.
* **Architectural Impact:** Provides critical production visibility.

## 4. Concepts Explained
Distributed Tracing, Span ID, Trace ID, Prometheus Metrics.

## 5. Prerequisites
Phase 2 completion.

## 6. Precise Implementation Tasks
1. Add Micrometer/Zipkin dependencies.
2. Configure sampling rate.

## 7. Important Configuration
`management.tracing.sampling.probability=1.0`.

## 8. Expected Files/Components
All `pom.xml`, `application.yml`

## 9. Acceptance Criteria
> *Reconstructed inference — not explicitly documented in the source material. Derived from reference implementation behavior.*

Single request to Gateway appears as a unified trace graph in Zipkin.

## 10. Verification Commands/Tests
Send request; open Zipkin UI `:9411`.

## 11. Expected Behavior
Trace showing Gateway -> Order -> Inventory.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Missing B3 headers; broken context propagation in async/feign calls.
* **Troubleshooting Guidance:** Ensure Feign/Kafka are instrumented to pass headers.

## 13. Relationship to Curriculum
* **Context:** First lab of Phase 3.
* **Source Evidence:** Reconstructed from reference implementation and S17 deck.
* **Related Commit(s):** `session-17: add-observability-zipkin-micrometer`
