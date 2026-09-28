# Lab 18 — Session 22

## 1. Classification
**OFFICIAL SOURCE LAB**

## 2. Objective
Implement Transactional Outbox and Idempotency.

## 3. Concepts Taught
Outbox Pattern

## 4. Why the lab exists
To prevent dual-write bugs.

## 5. Prerequisites
Lab 17

## 6. Tasks
1. Add outbox to order-service. 2. Add idempotency to payment.

## 7. Technologies Introduced
Spring Data, Kafka

## 8. Files/Components Changed
order-service, payment-service

## 9. Acceptance Criteria
Outbox events processed exactly once

## 10. How to Verify
Simulate failure

## 11. Expected Result
No duplicates

## 12. Troubleshooting Notes
Transaction boundaries

## 13. Related Architecture Changes
Data Integrity

## 14. Related Commit(s)
session-22

## 15. Relationship to Source/Reference Material
Official document missing locally / reconstructed from reference implementation.
