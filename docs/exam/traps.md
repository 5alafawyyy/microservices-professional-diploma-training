# Traps

> Each trap: what it looks like when it bites → how to detect it → the fix.
> Traps marked *(documented)* come from the course material; traps marked *(hit)* are ones you actually hit
> and must be backed by an entry in `docs/ENGINEERING_LOG.md`.

| # | Trap | Looks like | Detection | Fix | Source |
|---|---|---|---|---|---|
| 1 | Gateway pom contains `spring-boot-starter-web` | Gateway won't start (WebFlux/Servlet conflict) | startup error naming the conflict | remove the starter from `infrastructure/api-gateway/pom.xml` | documented |
| 2 | Missing `spring-boot-starter-aop` | Resilience4j annotations silently ignored | `/actuator/circuitbreakers` lists nothing | add the AOP starter to order-service | documented |
| 3 | Fallback signature wrong | 500 instead of fallback response | call a failing path and inspect | same params + `Throwable` last, same return type | documented |
| 4 | Resilience annotation order wrong | wrong component throttles/times out first | bulkhead vs timeout metrics behave oddly | `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry` | documented |
| 5 | Duplicate Kafka consumer group id | one handler silently never fires | `kafka-consumer-groups --describe` shows shared group | use the 5 distinct group ids | documented |
| 6 | `@CacheEvict` only on individual key | `findAll()` returns stale list | POST then GET-all shows old data | also `evictAllProductsCache()` on save/delete | documented (S08-Q04) |
| 7 | `#product.id` instead of `#result.id` on `save()` | eviction key wrong on insert | `KEYS products*` after POST | `@CacheEvict(key = "#result.id")` | documented |
| 8 | Eureka self-preservation left on in dev | stale instances in the dashboard | dashboard after killing a service | `enable-self-preservation: false` (DEV ONLY) | documented |
| 9 | JWT secret mismatch generator ↔ gateway | valid-looking token rejected 401 | compare `JWT_SECRET` on both sides | export the same secret | documented |
| 10 | `optional:` missing on `spring.config.import` | service won't start when Config Server is down | startup failure | `optional:configserver:…` | documented |
| 11 | Redis not running before Lab 2B checks | rate-limit route errors 500 | `docker compose ps redis` | start infra first | operational |
| 12 | Trailing `e` typo in consumer group (`order-service-cancel`) | compensation never runs | consumer-group listing | fix the group string, redeploy | documented (S07) |
| 13 | Keycloak port/realm discrepancy across materials (:8090 `microservices-pro` vs :8180 `ecommerce-platform`) | 404/401 during S19–S20 setup | check the running container's port + realm list | follow the session deck, record the truth in the ADR | documented discrepancy |
| 14 | `ddl-auto: update` treated as production-safe | silent schema drift | compare schema to entity | DEV ONLY; Flyway/managed migrations later | documented |
| 15 | Idempotency key missing on payment retry (Outbox era) | double charge on saga retry | payment table duplicates for one order | idempotency key (Session 22) | documented |

## Log of traps actually hit

| Date | Trap # | Evidence (engineering-log entry) |
|---|---|---|
| — | — | — |
