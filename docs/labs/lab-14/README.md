# Lab 14 — Session 18

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement CQRS (Command Query Responsibility Segregation).

## 2. Problem Being Solved
Read-heavy traffic locks the database while write-heavy operations occur.

## 3. Architecture
* **Before the lab:** Single service model for reads and writes.
* **After the lab:** Product service split into Command paths (writes) and Query paths (reads projections).
* **Architectural Impact:** Prepares architecture for event sourcing and massive read scaling.

## 4. Concepts Explained
CQRS, Read Projections.

## 5. Prerequisites
Lab 13.

## 6. Precise Implementation Tasks
1. Refactor product-service to use separate Command/Query objects.

## 7. Important Configuration
Package structure changes.

## 8. Expected Files/Components
`product-service`

## 9. Acceptance Criteria
> *Reconstructed inference — not explicitly documented in the source material. Derived from reference implementation behavior.*

Code cleanly separates read and write operations.

## 10. Verification Commands/Tests
Inspect code structure.

## 11. Expected Behavior
CQRS enforced at class/package level.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Eventual consistency lag between write and read DBs (if separated).
* **Troubleshooting Guidance:** Verify synchronization mechanism.

## 13. Relationship to Curriculum
* **Context:** Advanced design pattern.
* **Source Evidence:** Reconstructed from reference implementation and S18 deck.
* **Related Commit(s):** `session-18: implement-cqrs-pattern`
