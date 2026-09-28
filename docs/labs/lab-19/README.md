# Lab 19 — Session 23

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED / EXPANDED

## 1. Exact Objective
Perform Load and Stress Testing using k6.

## 2. Problem Being Solved
System performance under extreme load is unknown.

## 3. Architecture
* **Before the lab:** Untested scaling limits.
* **After the lab:** k6 scripts establish baseline performance metrics.
* **Architectural Impact:** Validates system non-functional requirements.

## 4. Concepts Explained
Load Testing, Stress Testing, Smoke Testing, Virtual Users (VUs).

## 5. Prerequisites
Lab 18.

## 6. Precise Implementation Tasks
1. Write smoke-test.js.
2. Write stress-test.js.
3. Document bottleneck findings.

## 7. Important Configuration
k6 VU and duration thresholds.

## 8. Expected Files/Components
`k6/`

## 9. Acceptance Criteria
k6 executes and generates performance report.

## 10. Verification Commands/Tests
`k6 run stress-test.js`.

## 11. Expected Behavior
Metrics output to console.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** k6 crashes host machine due to excessive VUs.
* **Troubleshooting Guidance:** Scale down VUs or run k6 from a dedicated testing machine.

## 13. Relationship to Curriculum
* **Context:** Final implementation lab.
* **Source Evidence:** Official document missing locally; reconstructed and expanded from curriculum map / reference implementation.
* **Related Commit(s):** `session-23: add-k6-stress-test-and-bottleneck-findings`
