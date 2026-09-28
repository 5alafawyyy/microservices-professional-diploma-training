# Engineering Log

> One entry per problem that cost real debugging time. This is **capstone evidence** (individual contribution)
> and the raw material for the exam's "explain a debugging story" questions.
> Keep it honest: a bug you caused and fixed is worth more here than a lab that went smoothly.

## Entry template — copy this block

```markdown
### YYYY-MM-DD — Lab NN — one-line title
- **Symptom:** what was observed (exact error / log line / status code).
- **Context:** what I was doing, which versions/ports, what I had just changed.
- **Investigation:** hypotheses tried, commands run, what ruled each out.
- **Root cause:** the actual mechanism (not just "it was wrong").
- **Fix:** the minimal change that fixed it (with file path).
- **Verification:** the command + result proving it is fixed.
- **Lesson:** the generalizable rule (this is what you say out loud in an interview).
- **Prevention:** what in this repo would catch it next time (test, check, note).
```

## Common traps index (pre-loaded from the course material — verify them yourself as they come up)

These are documented traps in the course. When you hit one, write the entry — do not just link this list.

| Trap | Where it bites | Detection | Fix |
|---|---|---|---|
| `spring-boot-starter-web` present in the gateway pom | Gateway (WebFlux) fails to start | startup conflict error | remove `spring-boot-starter-web`; use WebFlux only |
| Missing `spring-boot-starter-aop` | Resilience4j annotations silently do nothing | no CB metrics in `/actuator/circuitbreakers` | add the AOP starter |
| Fallback method signature wrong | Fallback never invoked (or context fails) | 500 instead of fallback response | same parameters + `Throwable` last, same return type |
| Annotation order wrong on `createOrderAsync()` | Bulkhead/Timelimiter not outermost | metrics show unexpected nesting | `@Bulkhead → @TimeLimiter → @CircuitBreaker → @Retry` |
| Duplicate Kafka consumer group id | Messages silently dropped (no error) | one handler never fires | 5 distinct groups (see `docs/labs` for the checklist) |
| `@CacheEvict` only on the individual key | `findAll()` serves stale list | stale data after save/delete | also call `evictAllProductsCache()` |
| `#product.id` in `@CacheEvict` on `save()` | Eviction key evaluates wrong on inserts | key remains in Redis | use `#result.id` |
| Eureka self-preservation in dev | Ghost instances stick around | dashboard shows stale entries | `enable-self-preservation: false` — DEV ONLY |
| Hardcoded secret drift (JWT) | Gateway rejects tool-generated tokens | 401 with valid-looking token | generator and gateway share `JWT_SECRET` |
| `ddl-auto: update` mistaken for production behaviour | unexpected schema changes | schema drift | DEV ONLY; revisit in Session 9+ |

## Entries

### 2026-09-28 — Lab 01 — Two Maven builds against one local repository: "Access is denied"
- **Symptom:** `mvn spring-boot:run` for `eureka-server` failed with
  `java.io.FileNotFoundException: C:\Users\Access\.m2\repository\org\vafer\jdependency\2.8.0\jdependency-2.8.0.pom.lastUpdated (Access is denied)`
  while resolving the `spring-boot-maven-plugin` dependency set — `BUILD FAILURE` before the app started.
- **Context:** Lab 1, first cold build. I launched `config-server` and `eureka-server` as two background
  `mvn spring-boot:run` processes at the same time; both were downloading the same plugin dependencies
  into `~/.m2` for the first time (JDK 21, Maven 3.9.10, Windows).
- **Investigation:** The generic advice is "delete the `.lastUpdated` file / purge the cache" — I did not,
  because the error is a Windows sharing violation, not corrupt content. Checked whether the other Maven
  process was still running: it was (config-server). Hypothesis: both processes were touching the same
  repository paths concurrently. Test: wait for config-server's plugin resolution to finish, then re-run
  eureka-server **alone**.
- **Root cause:** Maven's local repository is not safe for concurrent *resolution* writes. Two JVMs
  resolving the same not-yet-cached artifact race on the same files (`.lastUpdated`, POMs); on Windows the
  loser gets `Access is denied` instead of waiting for the lock.
- **Fix:** serialize the first builds — run one `mvn spring-boot:run` at a time until the plugin classpath
  is cached. Nothing deleted; no repository repair needed.
- **Verification:** re-ran `mvn spring-boot:run` for eureka-server alone → `:: Spring Boot :: (v3.3.4)`
  started on :8761; `curl http://localhost:8761/` → HTTP 200.
- **Lesson:** "Access is denied" inside `.m2` during a build usually means **another Maven process holds the
  file**, not that the cache is broken. Diagnose the concurrency before "repairing" the cache.
- **Prevention:** this repo's run workflow starts modules one at a time; if parallel startup is ever needed,
  warm `~/.m2` first with one `mvn -q dependency:go-offline` per module.

### 2026-09-28 — Lab 01 — Eureka `/eureka/apps` reports an empty registry right after a successful registration
- **Symptom:** seconds after product-service logged its registration, `GET http://localhost:8761/eureka/apps`
  returned `{"applications":{…,"application":[]}}` — no applications, despite the service being up.
- **Context:** Lab 1 acceptance check "product-service registers with Eureka". product-service had just
  started with `eureka.client.service-url.defaultZone=http://localhost:8761/eureka/`.
- **Investigation:** (1) Read the Eureka server log — it contained
  `Registered instance PRODUCT-SERVICE/localhost:product-service:8081 with status UP (replication=false)`,
  so the registration had *happened*. (2) Hypothesis: the REST read path is cached. Test: re-queried after
  `sleep 35`.
- **Root cause:** the Eureka server refreshes its REST response cache every 30 s
  (`eureka.server.response-cache-update-interval-ms`, default 30 000 ms). The authoritative registry is
  updated instantly; only the read model lags.
- **Fix:** none — by design. For verification, poll until `UP` appears instead of asserting on the first read.
- **Verification:** `sleep 35; curl /eureka/apps` → `PRODUCT-SERVICE → localhost:product-service:8081 → UP`.
- **Lesson:** when a discovery check looks broken, separate the **authoritative state** (registry, server log)
  from the **read model** (cached REST view). The same 30 s cache delays `lb://` routing in Session 2 after
  a fresh start — retry before concluding anything.
- **Prevention:** the registration acceptance check uses a wait-for-UP loop; recorded in
  `docs/labs/lab-01/README.md` (observation 3).

### 2026-09-28 — Lab 01 — Mockito "could not self-attach to current VM": a test failure that was really memory exhaustion
- **Symptom:** `mvn test` in `config-server` → `Tests run: 1, Failures: 0, Errors: 1`:
  `IllegalStateException: Could not initialize plugin: interface org.mockito.plugins.MockMaker (alternate: null)`
  → `MockitoInitializationException: Could not initialize inline Byte Buddy mock maker … Java: 21, 21.0.5+9-LTS-239`
  → `Could not self-attach to current VM using external process`. The Spring context itself had started
  fine (`Started ConfigServerApplicationTests in 5.137 seconds`).
- **Context:** Lab 1 acceptance evidence. Three Spring Boot services were live (:8888, :8761, :8081),
  Docker ran postgres, and Maven was resident; ~5.3 GB free of 31.7 GB (24-core Windows 11 host).
  The test class is a plain `@SpringBootTest` with **no mocks** — but Mockito is on the test classpath
  via `spring-boot-starter-test`, and Spring Boot's `ResetMocksTestExecutionListener` initializes it
  for every `@SpringBootTest`.
- **Investigation:** (1) Ruled out a broken test — the failure is Mockito *plugin init*, before any
  assertion. (2) Passed `-Djdk.attach.allowAttachSelf=true` to the fork → `Tests run: 0 … The forked VM
  terminated without properly saying goodbye … Process Exit Code: 1`. (3) Read
  `target/surefire-reports/*.dumpstream`: `insufficient memory for the Java Runtime Environment to continue`.
  (4) Read the fork's `hs_err_pid*.log`: `Native memory allocation (mmap) failed to map 532676608 bytes
  for G1 virtual space` — the fork could not even start. (5) After stopping the services, found their
  child JVMs **still listening** on :8888/:8761/:8081 although the Maven parent tasks were stopped →
  killed them; free RAM rose to 8 GB.
- **Root cause:** oversubscription. Mockito's inline mock maker attaches a Byte Buddy agent; self-attach
  is disabled by default on this JDK, so it spawns an *external* attacher JVM — which could not start on
  the exhausted machine. The "MockMaker init" error was a symptom of memory pressure, not a library defect.
  The diagnostic fork deaths are the same mechanism, observed more directly.
- **Fix:** free memory — stop the Spring Boot services (and their orphaned child JVMs) before running test
  suites. No pom, code, or Mockito changes.
- **Verification:** re-ran all three suites on the unloaded machine (2026-09-28 07:41–07:43):
  config-server `Tests run: 1, Failures: 0, Errors: 0`; eureka-server `1/0/0`; product-service `6/0/0`
  — all `BUILD SUCCESS`. The `WARNING: A Java agent has been loaded dynamically
  (byte-buddy-agent-1.14.19.jar)` line in the passing logs proves the attach that failed before now works.
- **Lesson:** on a loaded machine, "could not self-attach / MockMaker init" almost always means **the test
  harness ran out of memory**, not a Mockito defect — check free RAM and `hs_err_pid*.log` before touching
  build configuration. `mvn test` forks a JVM of its own: count every JVM (services + Maven + forks + Docker)
  before blaming the framework.
- **Prevention:** run the acceptance phase (services up) and the `mvn test` phase at different times,
  or check free RAM first — recorded in `docs/labs/lab-01/README.md` (observation 4). Evidence rule
  adopted: a test result is only written into an acceptance record when the `Tests run: …` summary was
  actually observed. On an unavoidably loaded machine, `-Djdk.attach.allowAttachSelf=true` avoids the
  extra attacher process — a mitigation, not a fix.
