# Lab 01 — Session 1

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Build the foundational Service Discovery and Centralized Configuration infrastructure, and connect the first microservice.

## 2. Problem Being Solved
Hardcoded IPs make microservices brittle. Distributed configurations lead to configuration drift.

## 3. Architecture
* **Before the lab:** Empty repository.
* **After the lab:** Config Server (:8888), Eureka Server (:8761), and Product Service (:8081) communicating with each other.
* **Architectural Impact:** Establishes the foundation for all future service discovery.

## 4. Concepts Explained
Service Registry Pattern, Centralized Configuration (12-Factor App III), Spring Cloud Netflix Eureka.

## 5. Prerequisites
Java 21, Maven.

## 6. Precise Implementation Tasks
1. Initialize config-server.
2. Initialize eureka-server.
3. Initialize product-service.
4. Connect product-service to both servers.

## 7. Important Configuration
`eureka.client.register-with-eureka=false` (server)
`spring.config.import=optional:configserver:...`

## 8. Expected Files/Components
`config-server`, `eureka-server`, `product-service`

## 9. Acceptance Criteria
Eureka dashboard shows `PRODUCT-SERVICE` as `UP`.

## 10. Verification Commands/Tests
Run all three applications. Hit `http://localhost:8761`.

## 11. Expected Behavior
Product service registers successfully.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Config server not running before product service starts; port conflicts.
* **Troubleshooting Guidance:** Ensure Config Server starts first. Check `optional:` prefix in application.yml.

## 13. Relationship to Curriculum
* **Context:** First foundational lab. Sets up routing for Session 2 (Lab 2A).
* **Source Evidence:** Official document `session-01-lab-01.md`.
* **Related Commit(s):** `session-01: add-product-service-eureka-config`
