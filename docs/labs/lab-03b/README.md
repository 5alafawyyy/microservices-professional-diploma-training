# Lab 03B — Session 5

## 1. Classification
**OFFICIAL SOURCE LAB**

## 2. Objective
Add Bulkhead and TimeLimiter to Order Service.

## 3. Concepts Taught
Resilience4j Bulkhead/TimeLimiter

## 4. Why the lab exists
To prevent resource exhaustion and hang.

## 5. Prerequisites
Lab 03A

## 6. Tasks
1. Add Bulkhead. 2. Add TimeLimiter (async).

## 7. Technologies Introduced
Resilience4j

## 8. Files/Components Changed
order-service

## 9. Acceptance Criteria
Timeout triggers fallback

## 10. How to Verify
Simulate delay in payment-service

## 11. Expected Result
Fallback response

## 12. Troubleshooting Notes
Async context issues

## 13. Related Architecture Changes
Resilience layer

## 14. Related Commit(s)
session-05

## 15. Relationship to Source/Reference Material
Official document session-05-lab-3b.md
