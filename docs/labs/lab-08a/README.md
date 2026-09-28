# Lab 08A — Session 9

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Containerize the platform using Docker multi-stage builds.

## 2. Problem Being Solved
Inconsistent environments between dev and prod ('It works on my machine').

## 3. Architecture
* **Before the lab:** Services run manually via `mvn spring-boot:run`.
* **After the lab:** All 7 services packaged into Docker images and orchestrated via Docker Compose.
* **Architectural Impact:** Standardizes deployment artifact.

## 4. Concepts Explained
Multi-stage Dockerfiles, Docker Compose networking.

## 5. Prerequisites
Phase 1 completion.

## 6. Precise Implementation Tasks
1. Write Dockerfile for each service.
2. Update docker-compose.yml to include app services.

## 7. Important Configuration
`docker-compose.yml` networks, environment variables.

## 8. Expected Files/Components
`Dockerfile` (in every service), root `docker-compose.yml`

## 9. Acceptance Criteria
> *Reconstructed inference — not explicitly documented in the source material. Derived from reference implementation behavior.*

`docker compose up` brings up the entire platform successfully.

## 10. Verification Commands/Tests
Run `docker compose up -d`.

## 11. Expected Behavior
All containers healthy and inter-communicating via Docker DNS.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Services fail to start because Config/Eureka are not ready.
* **Troubleshooting Guidance:** Use `depends_on: condition: service_healthy` in compose.

## 13. Relationship to Curriculum
* **Context:** Prerequisite for K8s deployment in Session 15.
* **Source Evidence:** Reconstructed from reference implementation, git history, and S09 deck.
* **Related Commit(s):** `session-09: add-multi-stage-dockerfiles`
