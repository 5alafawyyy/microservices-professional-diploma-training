# Lab 18 — Session 22

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED / EXPANDED

## 1. Exact Objective
Implement Transactional Outbox and Idempotency Keys.

## 2. Problem Being Solved
Saving to DB and sending to Kafka in the same method risks Dual-Write inconsistency if Kafka fails.

## 3. Architecture
* **Before the lab:** Dual-write risk in Order Service.
* **After the lab:** Order saved with Outbox event in same DB transaction. Idempotency enforced in Payment.
* **Architectural Impact:** Guarantees reliable messaging.

## 4. Concepts Explained
Transactional Outbox, Idempotent Consumer, Dual-Write Problem.

## 5. Prerequisites
Lab 17.

## 6. Precise Implementation Tasks
1. Add Outbox table.
2. Save event to DB.
3. Add scheduler to poll Outbox.
4. Add idempotency check in Payment.

## 7. Important Configuration
`@Scheduled` for outbox polling.

## 8. Expected Files/Components
`order-service`, `payment-service`

## 9. Acceptance Criteria
Kafka messages reliably delivered exactly-once (effectively) without dual-write risk.

## 10. Verification Commands/Tests
Simulate Kafka crash during order creation.

## 11. Expected Behavior
Order saved, Outbox event stored, polled when Kafka returns.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Polling race conditions in multi-instance setup.
* **Troubleshooting Guidance:** Use ShedLock or Debezium for production outbox implementations.

## 13. Relationship to Curriculum
* **Context:** Fixes design flaw in Lab 10A.
* **Source Evidence:** Official document missing locally; reconstructed and expanded from curriculum map / reference implementation.
* **Related Commit(s):** `session-22: add-outbox-pattern-and-idempotency-keys`
