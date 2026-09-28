# Lab 02A — Session 2

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Implement Spring Cloud Gateway for dynamic routing.

## 2. Problem Being Solved
Clients shouldn't need to know the IPs or ports of individual microservices.

## 3. Architecture
* **Before the lab:** Direct connections to product-service.
* **After the lab:** API Gateway acts as the single entrypoint and routes to product-service via Eureka `lb://`.
* **Architectural Impact:** Hides internal network topology from clients.

## 4. Concepts Explained
API Gateway Pattern, Route Predicates, Filters, Load Balancing.

## 5. Prerequisites
Lab 01.

## 6. Precise Implementation Tasks
1. Initialize api-gateway.
2. Configure Eureka client.
3. Configure route to product-service.

## 7. Important Configuration
`spring.cloud.gateway.routes`, `lb://PRODUCT-SERVICE`.

## 8. Expected Files/Components
`api-gateway/src/main/resources/application.yml`

## 9. Acceptance Criteria
Gateway routes `/api/products/**` to `product-service`.

## 10. Verification Commands/Tests
Hit `http://localhost:8080/api/products`.

## 11. Expected Behavior
200 OK from Product Service, routed via Gateway.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Route 404s due to missing `StripPrefix`.
* **Troubleshooting Guidance:** Check Eureka dashboard to ensure Gateway and Product are both registered.

## 13. Relationship to Curriculum
* **Context:** Builds on Lab 1. Prepared for Security in Lab 2B.
* **Source Evidence:** Official document `session-02-lab-02.md`.
* **Related Commit(s):** `session-02: add-api-gateway`
