# Lab 10A — Session 12

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Migrate from Choreography to Orchestration Saga.

## 2. Problem Being Solved
Choreography becomes impossible to trace and maintain as the number of services grows.

## 3. Architecture
* **Before the lab:** Peer-to-peer event listening (Choreography).
* **After the lab:** Order Service acts as the centralized Orchestrator (State Machine) dispatching commands.
* **Architectural Impact:** Shifts complexity from network back to the orchestrator service.

## 4. Concepts Explained
Orchestration Saga, State Machine, Command/Reply Messaging.

## 5. Prerequisites
Lab 09B.

## 6. Precise Implementation Tasks
1. Add Orchestrator to order-service.
2. Change Payment/Inventory to listen for Commands and emit Replies.

## 7. Important Configuration
State machine state transitions.

## 8. Expected Files/Components
`order-service` saga package.

## 9. Acceptance Criteria
Orders flow through the Orchestrator state machine successfully.

## 10. Verification Commands/Tests
Place order and observe state machine logs.

## 11. Expected Behavior
Centralized control flow.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Deadlocks; missing reply topics.
* **Troubleshooting Guidance:** Ensure every command has exactly one correlating reply.

## 13. Relationship to Curriculum
* **Context:** Major architectural refactoring of Lab 05A.
* **Source Evidence:** Reconstructed from reference implementation and S12 deck.
* **Related Commit(s):** `session-12: migrate-to-saga-orchestration`
