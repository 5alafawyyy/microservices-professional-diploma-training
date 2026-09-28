# Lab 01 — Acceptance Record

> Session 1 · Date: 2026-09-28
> Status vocabulary: **PASS** (verified with evidence) · **NOT VERIFIED** · **BLOCKED** · **NOT APPLICABLE**
> Rule: nothing is marked PASS without the evidence below it.

## Acceptance criteria (from the official lab document)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `docker compose up -d` starts postgres and it reports healthy | **PASS** | `docker compose ps` → `postgres  Up 8 seconds (healthy)  0.0.0.0:5432->5432/tcp` |
| 2 | Config Server runs and serves configuration | **PASS** | `curl :8888/actuator/health` → `{"status":"UP"}`; `curl :8888/product-service/default` → `propertySources[0].source = {"app.source":"config-server"}` |
| 3 | Eureka Server dashboard reachable at `localhost:8761` | **PASS** | `curl -o /dev/null -w "%{http_code}" http://localhost:8761/` → `200`; dashboard HTML contains `PRODUCT-SERVICE` |
| 4 | Product Service registered in Eureka | **PASS** | server log: `Registered instance PRODUCT-SERVICE/localhost:product-service:8081 with status UP (replication=false)`; `/eureka/apps` after cache refresh → `PRODUCT-SERVICE → UP` |
| 5 | All 4 REST endpoints work | **PASS** | see the endpoint transcript below |
| 6 | Minimum 3 unit tests, `mvn test` green | **PASS** | re-verified 2026-09-28 07:41–07:43 with the machine unloaded: product-service `6/0/0`, config-server `1/0/0`, eureka-server `1/0/0` (8 total) — first run errored on memory exhaustion; see incident note under the evidence block |
| 7 | Commit with message `session-01: add-product-service-eureka-config` | **PASS** | see commit section |

## Endpoint transcript (criterion 5)

```
$ curl -s -w "  <- HTTP %{http_code}\n" http://localhost:8081/api/v1/products
[]  <- HTTP 200
$ curl -s -w "  <- HTTP %{http_code}\n" -X POST http://localhost:8081/api/v1/products \
       -H 'Content-Type: application/json' \
       -d '{"name":"Laptop","description":"15-inch laptop","price":999.99,"category":"Electronics"}'
{"id":1,"name":"Laptop","description":"15-inch laptop","price":999.99,"category":"Electronics"}  <- HTTP 201
$ curl -s -w "  <- HTTP %{http_code}\n" http://localhost:8081/api/v1/products/1
{"id":1,"name":"Laptop","description":"15-inch laptop","price":999.99,"category":"Electronics"}  <- HTTP 200
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8081/api/v1/products/999
HTTP 404
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE http://localhost:8081/api/v1/products/1
HTTP 204
$ curl -s -w "  <- HTTP %{http_code}\n" http://localhost:8081/api/v1/products
[]  <- HTTP 200
```

Interpretation of the assertions that matter:
- `POST` returns **201**, not 200, and the response body carries the server-assigned id.
- `GET /{id}` for a missing id returns **404 with an empty body**, not `200 null`.
- `DELETE` returns **204** and is idempotent (deleting a missing id is not an error).

## Config-client evidence (criterion 2, client side)

```
product-service.log:
  ConfigServerConfigDataLoader : Fetching config from server at : http://localhost:8888
  ConfigServerConfigDataLoader : Located environment: name=product-service, profiles=[default], …
```

This proves the JVM **pulled** configuration from the server at startup — the server-side
`curl` alone would not.

## Unit test evidence (criterion 6)

```
config-server   (07:41): Tests run: 1, Failures: 0, Errors: 0, Skipped: 0   BUILD SUCCESS
eureka-server   (07:42): Tests run: 1, Failures: 0, Errors: 0, Skipped: 0   BUILD SUCCESS
product-service (07:43): Tests run: 6, Failures: 0, Errors: 0, Skipped: 0   BUILD SUCCESS
```

The 6 service tests cover: empty list · save assigns id + round-trip · save keeps a
client-supplied id · `findById` empty for unknown id · `deleteById` removes ·
`findAll` returns an immutable snapshot (encapsulation, not a live view).

> **Incident note (2026-09-28).** The first config-server run was briefly recorded above as
> green from a `mvn -q` invocation whose summary was never observed. The true first result was
> `Errors: 1` — Mockito's inline Byte Buddy mock maker could not attach to the forked test JVM
> (`Could not self-attach to current VM using external process`). Root cause was machine memory
> exhaustion — three Spring Boot services + Docker + Maven forks resident, 5.3 GB free of 31.7 GB:
> the external agent-attach JVM failed to spawn, and diagnostic forks died with
> `hs_err_pid*.log: failed to map 532676608 bytes for G1 virtual space`. After stopping the
> services, the **unmodified** code passes on all three modules. Full story:
> `docs/ENGINEERING_LOG.md` entry 3.

## Commit (criterion 7)

```
session-01: add-product-service-eureka-config
```

## Differences from the reference implementation

Noting these explicitly rather than hiding them. The reference was used **only** to
compare after the lab was built — no code was copied.

| # | Difference | Source A (course/reference) | Source B (this build) | Impact | Decision & reason |
|---|---|---|---|---|---|
| 1 | `ProductServiceTest` style | 4 tests, `@ExtendWith(MockitoExtension.class)` + `@InjectMocks` although the service has no collaborators | 6 tests, plain instantiation in `@BeforeEach` | None functional; mocking a class with nothing to mock adds noise | Kept mine: Mockito is introduced properly in Session 10; using it here would imply a collaborator that does not exist |
| 2 | Extra tests | — | `save_keepsClientSuppliedId`, `findAll_returnsImmutableSnapshot_notTheLiveStore` | Adds coverage for the two "shallow-pass" patterns the trainer checklist warns about | Kept mine |
| 3 | Infra module tests | No test classes shipped for config-server / eureka-server | One `contextLoads()` `@SpringBootTest` each | +~10 s build time; catches "module no longer boots" immediately | Kept mine |
| 4 | `management` block in product-service `application.yml` | Not present in the reference file read during STEP A | `include: health,info` | None (`health` is exposed by default anyway) | Kept mine: consistent with the other two modules |
| 5 | Comments/doc style | Course-style explanatory comments | Rewritten in my own words, referencing ADR-001 | None | Kept mine |

## Deviations from the lab document

None. All 4 tasks (T1–T4) and the 7 acceptance criteria were performed as written.
The optional homework (JPA + PostgreSQL) was deliberately **not** done — it belongs to
the Session 6–8 JPA block under the Historical State Rule; see ADR-001.

## Open items

- None blocking. Port 8080 remains occupied by the unrelated IdentityIQ stack; it is
  first needed in Session 2 (gateway) → must be resolved before that lab.
