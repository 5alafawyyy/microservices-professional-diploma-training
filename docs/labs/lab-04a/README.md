# Lab 04A — Session 6

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED / RECONSTRUCTED (LOCAL SOURCE FILE ABSENT)

## 1. Exact Objective
Build Inventory Service and implement sync communication via OpenFeign.

## 2. Problem Being Solved
Manual RestTemplate calls are verbose and hard to maintain.

## 3. Architecture
* **Before the lab:** Hardcoded RestTemplate or WebClient usage.
* **After the lab:** Declarative Feign interfaces used for synchronous inter-service communication.
* **Architectural Impact:** Standardizes synchronous HTTP calls.

## 4. Concepts Explained
Spring Cloud OpenFeign, ErrorDecoder, Declarative REST Clients.

## 5. Prerequisites
Lab 03B.

## 6. Precise Implementation Tasks
1. Scaffold inventory-service.
2. Create Feign client in order-service.
3. Map Feign exceptions.

## 7. Important Configuration
`@EnableFeignClients`, `spring.cloud.openfeign.client.config.*`

## 8. Expected Files/Components
`inventory-service`, `order-service`

## 9. Acceptance Criteria
Order service seamlessly fetches stock from inventory via Feign.

## 10. Verification Commands/Tests
Place order requiring stock check.

## 11. Expected Behavior
Successful stock validation across service boundaries.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Feign URL mapping errors; unhandled FeignExceptions.
* **Troubleshooting Guidance:** Verify Eureka registration. Implement Custom ErrorDecoder to unwrap exceptions.

## 13. Relationship to Curriculum
* **Context:** Prepares the sync baseline before Kafka async is introduced in Session 7.
* **Source Evidence:** Official document missing locally; reconstructed from curriculum map and reference implementation.
* **Related Commit(s):** `session-06: add-inventory-and-feign-clients`
