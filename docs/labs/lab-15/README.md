# Lab 15 — Session 19

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Deploy and configure Keycloak as an Identity Provider.

## 2. Problem Being Solved
Custom JWT generation is insecure and difficult to rotate.

## 3. Architecture
* **Before the lab:** Custom `jwt-generator` tool.
* **After the lab:** Keycloak provides standard OAuth2 / OIDC token issuance.
* **Architectural Impact:** Offloads identity management to an enterprise IdP.

## 4. Concepts Explained
Identity Provider, OAuth2, OpenID Connect.

## 5. Prerequisites
Lab 14.

## 6. Precise Implementation Tasks
1. Run Keycloak in Compose.
2. Create Realm, Client, User, Role.

## 7. Important Configuration
Keycloak realm export JSON.

## 8. Expected Files/Components
`docker-compose.yml`, `keycloak-realm.json`

## 9. Acceptance Criteria
Can fetch a JWT from Keycloak token endpoint.

## 10. Verification Commands/Tests
cURL Keycloak `/protocol/openid-connect/token`.

## 11. Expected Behavior
Valid JWT token returned.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Keycloak admin console inaccessible.
* **Troubleshooting Guidance:** Check port 8180 mapping.

## 13. Relationship to Curriculum
* **Context:** Prepares for Lab 16 Gateway integration.
* **Source Evidence:** Reconstructed from reference implementation and S19 deck.
* **Related Commit(s):** `session-19: add-keycloak-realm-client-and-manual-oauth2-flow`
