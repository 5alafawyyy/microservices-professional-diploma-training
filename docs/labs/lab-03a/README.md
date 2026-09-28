# Lab 03A — Session 4

## 1. Classification
**OFFICIAL SOURCE LAB**

## 2. Objective
Scaffold Order & Payment, add Circuit Breaker and Retry.

## 3. Concepts Taught
Resilience4j CircuitBreaker/Retry

## 4. Why the lab exists
To handle downstream failures gracefully.

## 5. Prerequisites
Lab 02B

## 6. Tasks
1. Scaffold services. 2. Add CB/Retry.

## 7. Technologies Introduced
Resilience4j

## 8. Files/Components Changed
order-service, payment-service

## 9. Acceptance Criteria
Fallback method invoked on failure

## 10. How to Verify
Stop payment-service and hit order-service

## 11. Expected Result
Fallback response

## 12. Troubleshooting Notes
Fallback signature mismatch

## 13. Related Architecture Changes
Resilience layer

## 14. Related Commit(s)
session-04

## 15. Relationship to Source/Reference Material
Official document session-04-lab-3a.md
