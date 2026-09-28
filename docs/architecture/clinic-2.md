# Architecture Clinic #2: Final Wrap-up

This clinic reviews the technical debt identified in Clinic #1 (Session 8) and documents the final state of the architecture as we transition into the Capstone project.

## 1. Technical Debt Register Review

We carried forward 8 items from Clinic #1. Here is their current status at the end of Phase 3 (Session 24):

| Item | Status | Resolution / Carry Over |
|---|---|---|
| **1. In-memory stock map** | **CARRY OVER** | The inventory service still uses a `ConcurrentHashMap` for stock. Postgres migration is deferred to Capstone. |
| **2. No idempotency on payment** | **RESOLVED** | Implemented Idempotency Keys in Lab 18 (Session 22). |
| **3. Hardcoded PUBLIC_ROUTES** | **CARRY OVER** | Security routes are still largely hardcoded in SecurityConfig. Needs externalized configuration or centralized auth rules. |
| **4. No Kafka DLQ** | **CARRY OVER** | We added a transactional outbox in Lab 18, but a proper Dead Letter Queue for poison messages in consumer groups remains a Capstone item. |
| **5. payment.failure-rate=0.5** | **CARRY OVER** | Circuit breaker thresholds are still default. Should be tuned based on the k6 stress test findings from Lab 19. |
| **6. No API versioning** | **CARRY OVER** | Only product-service has /api/v1/. The rest still lack strict path or header versioning. |
| **7. No Flyway/Liquibase** | **CARRY OVER** | We still rely on Hibernate ddl-auto: update (DEV ONLY). Database migrations must be added in the Capstone. |
| **8. S6 Feign pre-check unprotected** | **CARRY OVER** | The direct OpenFeign stock pre-check in OrderService lacks Resilience4j fallbacks. Recommended for Capstone. |

## 2. Architecture Decisions Defended

- **Saga Orchestration vs Choreography**: We transitioned from Choreography to Orchestration with a State Machine (Lab 10A). This centralizes the logic and simplifies the rollback tracking, though it introduced a single point of failure (the orchestrator database).
- **Service Mesh (Istio)**: Introduced in Lab 17 (Session 21). Offloads mTLS and traffic splitting (canary releases) from the application layer to the infrastructure layer, reducing code bloat.
- **Transactional Outbox**: Added in Lab 18 to fix the dual-write problem. Ensures the database and Kafka events are always eventually consistent, protecting against JVM crashes.

## 3. Capstone Preview

Going into Phase 4 (Capstone), the primary focus will be closing out the remaining "CARRY OVER" technical debt items, tuning the resilience stack based on real metrics, and preparing the infrastructure for production deployment (Flyway, DLQs, strict API versioning).
