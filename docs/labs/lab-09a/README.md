# Lab 09A — Session 10

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement Spring Boot integration tests with Testcontainers.

## 2. Problem Being Solved
Mocking databases hides actual SQL and serialization errors.

## 3. Architecture
* **Before the lab:** Unit tests only.
* **After the lab:** Integration tests spin up real Postgres/Redis containers during the test phase.
* **Architectural Impact:** Increases confidence in data layer.

## 4. Concepts Explained
Test Pyramid, Testcontainers, `@WebMvcTest`, `@SpringBootTest`.

## 5. Prerequisites
Lab 08A.

## 6. Precise Implementation Tasks
1. Add Testcontainers dependencies.
2. Write ProductService integration tests.

## 7. Important Configuration
`@Testcontainers`, `@Container`.

## 8. Expected Files/Components
`product-service/src/test/...`

## 9. Acceptance Criteria
`mvn test` spins up Docker containers, runs tests against them, and tears them down.

## 10. Verification Commands/Tests
Run `mvn clean test` on product-service.

## 11. Expected Behavior
Tests pass against a real ephemeral Postgres instance.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Docker daemon not running; port conflicts.
* **Troubleshooting Guidance:** Ensure Docker Desktop is running before Maven.

## 13. Relationship to Curriculum
* **Context:** Part 1 of Testing phase. Followed by Contract Testing.
* **Source Evidence:** Reconstructed from reference implementation and S10 deck.
* **Related Commit(s):** `session-10: add-testcontainers-integration-tests`
