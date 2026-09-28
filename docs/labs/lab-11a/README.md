# Lab 11A — Session 13

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement GitHub Actions CI/CD and build Notification Service.

## 2. Problem Being Solved
Manual builds are error-prone; failed events disappear into the void.

## 3. Architecture
* **Before the lab:** Manual `mvn package`.
* **After the lab:** Automated pipeline; Notification Service uses `@RetryableTopic` and DLQ.
* **Architectural Impact:** Automates verification; adds event failure safety net.

## 4. Concepts Explained
CI/CD Pipelines, Kafka Dead Letter Queue (DLQ), @RetryableTopic.

## 5. Prerequisites
Lab 10A.

## 6. Precise Implementation Tasks
1. Write `.github/workflows/build.yml`.
2. Build `notification-service` with DLQ.

## 7. Important Configuration
`@RetryableTopic(attempts = 3)`.

## 8. Expected Files/Components
`.github/workflows`, `notification-service`

## 9. Acceptance Criteria
Pipeline passes on commit; Notification service routes failures to DLQ.

## 10. Verification Commands/Tests
Push to branch; trigger Kafka failure in notification.

## 11. Expected Behavior
Event lands in `notification-events-dlt`.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Pipeline YAML syntax errors.
* **Troubleshooting Guidance:** Use GitHub Actions UI to trace pipeline steps.

## 13. Relationship to Curriculum
* **Context:** Prepares CD flow for GitOps.
* **Source Evidence:** Reconstructed from reference implementation and S13 deck.
* **Related Commit(s):** `session-13: add-ci-pipeline-and-notification-service`
