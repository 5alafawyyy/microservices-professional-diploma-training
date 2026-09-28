# Lab 05A — Session 7

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement an Event-Driven Choreography Saga.

## 2. Problem Being Solved
Distributed transactions spanning multiple databases cannot use traditional ACID COMMIT/ROLLBACK.

## 3. Architecture
* **Before the lab:** Synchronous HTTP calls acting as pseudo-transactions.
* **After the lab:** Asynchronous Kafka events drive state changes across Order, Inventory, and Payment.
* **Architectural Impact:** Removes temporal coupling but introduces eventual consistency complexity.

## 4. Concepts Explained
Saga Pattern, Choreography, Event-Driven Architecture, Kafka Topics/Consumers.

## 5. Prerequisites
Lab 04A, Kafka cluster.

## 6. Precise Implementation Tasks
1. Deploy Kafka.
2. Produce `OrderCreatedEvent`.
3. Consume in Inventory/Payment.
4. Produce success/failure events to complete or compensate.

## 7. Important Configuration
`spring.kafka.bootstrap-servers`, consumer group IDs.

## 8. Expected Files/Components
`docker-compose.yml`, `order`, `inventory`, `payment` event listeners

## 9. Acceptance Criteria
> *Reconstructed inference — not explicitly documented in the source material. Derived from reference implementation behavior.*

Order flows from PENDING to COMPLETED (or CANCELLED) via Kafka events.

## 10. Verification Commands/Tests
Place an order; watch logs for Kafka message consumption.

## 11. Expected Behavior
Eventual consistency achieved across 3 databases.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Serialization errors; incorrect topic names; consumer group conflicts.
* **Troubleshooting Guidance:** Ensure `JsonSerializer`/`JsonDeserializer` is configured. Check Kafka tool/logs.

## 13. Relationship to Curriculum
* **Context:** Crucial pattern. Later refactored to Orchestration in Session 12.
* **Source Evidence:** Official document exists (`session-07-lab-5a.md`) but is empty. Reconstructed from reference implementation and S07 deck.
* **Related Commit(s):** `session-07: add-kafka-and-choreography-saga`
