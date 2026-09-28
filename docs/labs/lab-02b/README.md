# Lab 02B — Session 3

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Secure the Gateway with JWT and add Redis rate limiting.

## 2. Problem Being Solved
APIs are exposed without authentication and vulnerable to DoS attacks.

## 3. Architecture
* **Before the lab:** Open, unprotected Gateway.
* **After the lab:** Gateway with `JwtAuthFilter` and Redis Token-Bucket `RequestRateLimiter`.
* **Architectural Impact:** Moves security to the edge.

## 4. Concepts Explained
JWT structure, Global/Route Filters, Token-Bucket Rate Limiting.

## 5. Prerequisites
Lab 02A, Redis.

## 6. Precise Implementation Tasks
1. Add jjwt.
2. Implement JwtAuthFilter.
3. Add Redis RequestRateLimiter config.

## 7. Important Configuration
`spring.cloud.gateway.default-filters`, `redis-rate-limiter.replenishRate`.

## 8. Expected Files/Components
`api-gateway/.../JwtAuthFilter.java`

## 9. Acceptance Criteria
Unauthenticated requests yield 401; excessive requests yield 429.

## 10. Verification Commands/Tests
Send request without Authorization header.

## 11. Expected Behavior
401 Unauthorized.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Redis connection refused; JWT signature mismatch.
* **Troubleshooting Guidance:** Ensure Redis is running. Check JWT secret consistency.

## 13. Relationship to Curriculum
* **Context:** Builds on Lab 2A. Security logic later migrated to OAuth2 in Session 20.
* **Source Evidence:** Official document `session-03-lab-2b.md`.
* **Related Commit(s):** `session-03: add-jwt-auth-and-rate-limiting`
