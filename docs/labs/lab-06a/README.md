# Lab 06A — Session 8

## Documentation Classification
* **Source Status:** OFFICIAL SOURCE LAB
* **Training Documentation:** SOURCE-DERIVED

## 1. Exact Objective
Add PostgreSQL persistence and Redis Cache-Aside to Product Service.

## 2. Problem Being Solved
In-memory stores lose data on restart. Repeated DB reads for static products degrade performance.

## 3. Architecture
* **Before the lab:** In-memory lists inside service classes.
* **After the lab:** Postgres JPA repository with `@Cacheable` Redis layer in front.
* **Architectural Impact:** Establishes standard data layer.

## 4. Concepts Explained
Spring Data JPA, Cache-Aside Pattern, Cache Eviction.

## 5. Prerequisites
Lab 05A.

## 6. Precise Implementation Tasks
1. Configure Postgres.
2. Migrate Product to JPA Entity.
3. Add `@EnableCaching`.
4. Annotate methods.

## 7. Important Configuration
`spring.datasource.url`, `spring.cache.type=redis`.

## 8. Expected Files/Components
`product-service` Entity, Repository, Service classes.

## 9. Acceptance Criteria
Products persist across restarts. Fetching same product twice hits Redis.

## 10. Verification Commands/Tests
Restart service, data remains. Check Redis CLI `KEYS *`.

## 11. Expected Behavior
Fast reads from Redis, writes update Postgres and evict cache.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Object serialization failures in Redis.
* **Troubleshooting Guidance:** Ensure Product entity implements `Serializable` or configure JSON serializer for RedisTemplate.

## 13. Relationship to Curriculum
* **Context:** Closes out Phase 1 foundation.
* **Source Evidence:** Official document `session-08-lab-6a.md`.
* **Related Commit(s):** `session-08: add-postgres-and-redis-caching`
