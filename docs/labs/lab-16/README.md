# Lab 16 — Session 20

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Migrate Gateway to OAuth2 Resource Server.

## 2. Problem Being Solved
Custom `JwtAuthFilter` must be manually maintained.

## 3. Architecture
* **Before the lab:** Custom `JwtAuthFilter` parsing tokens.
* **After the lab:** Spring Security OAuth2 Resource Server validates tokens via Keycloak JWKS.
* **Architectural Impact:** Standardizes security.

## 4. Concepts Explained
OAuth2 Resource Server, JWKS, Role-Based Access Control.

## 5. Prerequisites
Lab 15.

## 6. Precise Implementation Tasks
1. Remove JwtAuthFilter.
2. Add `spring-boot-starter-oauth2-resource-server`.
3. Configure JWKS URI.

## 7. Important Configuration
`spring.security.oauth2.resourceserver.jwt.issuer-uri`

## 8. Expected Files/Components
`api-gateway`

## 9. Acceptance Criteria
Gateway automatically validates Keycloak tokens.

## 10. Verification Commands/Tests
Send request with Keycloak token.

## 11. Expected Behavior
200 OK.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Issuer mismatch; missing ROLE_ prefix in authorities mapping.
* **Troubleshooting Guidance:** Ensure custom JwtAuthenticationConverter maps Keycloak realm roles correctly.

## 13. Relationship to Curriculum
* **Context:** Replaces Lab 02B security.
* **Source Evidence:** Reconstructed from reference implementation and S20 deck.
* **Related Commit(s):** `session-20: retire-jwtauthfilter-add-oauth2-resource-server`
