# ADR-001: In-memory product store instead of JPA in Lab 1

- **Date:** 2026-09-28
- **Session / Lab:** Session 1 / Lab 1
- **Status:** accepted

## Context

`product-service` needs a place to keep products. Three constraints apply:

1. **The official lab document specifies an in-memory store.** Persistence is listed as *optional homework*.
2. **Historical State Rule** — JPA/PostgreSQL is taught in the Session 6–8 block. Introducing `@Entity`,
   repositories and datasource configuration now would put technology in the platform before the course
   teaches it, and would hide the fact that a microservice can start with no database at all.
3. `docker-compose.yml` already runs PostgreSQL from Lab 1, so the temptation to "just wire it up" exists.

A fourth, non-course constraint: the store must survive concurrent HTTP requests, because Tomcat serves
requests on many threads.

## Options considered

1. **In-memory `Map`** — zero configuration, nothing to install, no schema; state dies with the process,
   ids restart at 1, and it cannot be scaled horizontally (each instance has its own copy).
2. **JPA + PostgreSQL now** — durable and closer to the final platform; but pulls forward 3 sessions of
   teaching, requires entity/repository/datasource config, and makes Lab 1 unbuildable for anyone without
   Postgres running.
3. **Embedded H2 with JPA** — durable-ish and self-contained; but introduces JPA *and* a second database
   technology that the course never uses, and still violates the Historical State Rule.

## Decision

Use an in-memory `ConcurrentHashMap<Long, Product>` guarded by an `AtomicLong` id sequence, exposed
through `ProductService` behind the same method signatures a JPA-backed implementation will later have.

## Consequences

- **Easier:** the lab runs with three `mvn spring-boot:run` commands and no database; the service contract
  (`findAll` / `findById` → `Optional` / `save` / `deleteById`) is exactly the shape a Spring Data
  repository will satisfy, so the controller does not change when persistence lands.
- **Harder / owed:**
  - State is volatile — a restart wipes products and restarts ids at 1.
  - Not horizontally scalable: two instances would hold two different catalogues. This is precisely the
    problem the platform's later Redis cache and JPA layers exist to address.
  - `findAll()` returns `List.copyOf(...)` so callers cannot mutate the internal map; this is a deliberate
    encapsulation choice, tested.
- **Revisit:** when the Session 6–8 block introduces Spring Data JPA, replace the map with
  `ProductRepository extends JpaRepository<Product, Long>` and re-run the same service tests; if the tests
  still pass unchanged, this ADR's "same shape" claim is verified.

## Evidence

- `platform/ecommerce-platform/services/product-service/src/main/java/com/microservices/pro/productservice/ProductService.java`
- `ProductServiceTest` — 6 tests, `Tests run: 6, Failures: 0, Errors: 0`
- Acceptance record: `docs/labs/lab-01/acceptance.md`
