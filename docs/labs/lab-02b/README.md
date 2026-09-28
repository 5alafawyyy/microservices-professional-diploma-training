# Lab 02B — Session 3

## 1. Classification
**OFFICIAL SOURCE LAB**

## 2. Objective
Secure the API Gateway and add rate limiting.

## 3. Concepts Taught
JWT Validation, Rate Limiting

## 4. Why the lab exists
To secure endpoints and prevent abuse.

## 5. Prerequisites
Lab 02A

## 6. Tasks
1. Add JwtAuthFilter. 2. Add Redis rate limiter.

## 7. Technologies Introduced
jjwt, Redis

## 8. Files/Components Changed
api-gateway

## 9. Acceptance Criteria
Unauthenticated requests rejected with 401

## 10. How to Verify
Send request without token

## 11. Expected Result
401 Unauthorized

## 12. Troubleshooting Notes
Redis connection refused

## 13. Related Architecture Changes
Security layer

## 14. Related Commit(s)
session-03

## 15. Relationship to Source/Reference Material
Official document session-03-lab-2b.md
