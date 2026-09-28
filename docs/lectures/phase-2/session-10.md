# Session 10 — Testing Essentials (Part 0) + Unit & Integration Testing

Source files:
- `Session_10_Part_0_Testing Essentials for Microservices.pdf` — 94-slide essentials deck (7 sub-parts: 0.1 why testing, 0.2 SDLC/continuous testing, 0.3 test types, 0.4 monolith vs microservices testing, 0.5 effective tests + pyramid, 0.6 tool map + progression, 0.7 first JUnit/Mockito examples).
- `Session_10_Testing_Unit_Integration.pdf` — 27-slide delivery deck (Monday online 15:00–17:30, 2.5 h): H2-vs-PostgreSQL incident, testing pyramid for microservices, live coding (JUnit 5 parameterized tests, Mockito, @WebMvcTest, TestContainers), Lab 9A, homework, quiz, Definition of Done.

Source note: both decks belong to the same session (Part 0 = fundamentals, second deck = hands-on unit/integration). Both were read; this note merges them.

## 1. Why this topic exists

- Testing = verifying AND validating software: verification ("Are we building the product correctly?") vs validation ("Are we building the correct product?"). Testing vs debugging distinguished.
- Cost of defects grows over the lifecycle (defect cost timeline: cheapest at design/unit stage, most expensive in production).
- Automation argument: CI/CD deployments would be impossible manually — slides compute 5 deployments/day × 2 h manual verification = 10 h/day. Automated tests are what make CI/CD possible.
- Second-deck opening story: 47 unit tests green, yet `POST /api/orders` returns 500 in real runtime — the bug is the PostgreSQL `TIMESTAMPTZ` vs `TIMESTAMP` column, ignored by H2, rejected by PostgreSQL. Teaches: green unit tests do not verify wiring; you need tests at the right layer.
- "A field rename → contract preview" (0.3) and the H2 story set up Sessions 11 (contract/chaos) and 23.
- "A feature is not considered complete until it has been tested" (0.2); "quality is everyone's responsibility".

## 2. Core concepts

- Verification vs validation; testing vs debugging; defect cost timeline.
- SDLC, Continuous Testing, Shift-Left testing (move quality activities earlier); CI vs CD vs Continuous Deployment (table distinguishing integrate / deliver / deploy).
- Test types (0.3 + delivery deck): Unit, Integration, System, End-to-End, Acceptance, Contract. How each fits the platform, with examples and a decision table. Contract type preview: field rename scenario (payoff in Session 11).
- Testing Pyramid (both decks): 70% unit (~70 tests, milliseconds, plain Java + Mockito), 20% integration (~20 tests, seconds, @WebMvcTest/@DataJpaTest/TestContainers), 10% E2E (~5 tests, minutes, RestAssured/Playwright). "@SpringBootTest is ~10× slower than @WebMvcTest". E2E is deferred to Phase 3 / Session 23 (load testing).
- Microservices-specific failure modes (0.4): Network Failure; Service Unavailable (handled by Circuit Breakers/Retry/Bulkhead); Slow Response (15 s example); Incorrect API Response ({productId:5} vs {id:5} — shape mismatch); Database Differences (H2 vs PostgreSQL → TestContainers); Kafka broker problems (event never arrives, wrong format, deserialization failure, duplicates, out-of-order). "A collection of perfectly tested services does not guarantee a perfectly working system."
- Microservices need MORE integration tests than a monolith — because of JSON (de)serialization contract boundaries between services.
- Good test characteristics (0.5): Fast, Reliable, Valuable (flaky tests destroy value); Simple, Independent, Repeatable, Readable, Maintainable; confidence vs cost table; the trade-off triangle.
- 5 testing principles (0.5): including "test behavior, not implementation" and "tests are production code". Mistakes list includes "80% meaningful coverage better than 100% meaningless".
- AAA pattern (Arrange-Act-Assert) for every test.
- JUnit 5 basics: `@Test`, `@ParameterizedTest`, `@CsvSource`; assertions assertEquals/assertNotEquals/assertTrue/assertFalse/assertNull/assertNotNull/assertThrows.
- Mockito: `mock()`, `when(...).thenReturn(...)`, `verify(...)`; deeper: `@Mock` (complete fake — all methods stubbed null/do-nothing), `@Spy` (real object, real methods unless stubbed), `ArgumentCaptor`, `InOrder`. Never `@Spy` an interface; abstract class spying needs a no-arg constructor.
- Spring Boot Test slices: `@WebMvcTest` (controller layer + MockMvc; dependencies via `@MockBean`), `@DataJpaTest` (JPA/repository layer), `@JsonTest` (JSON serialization), full `@SpringBootTest` (whole context, slowest).
- TestContainers: real Docker-based dependencies in tests — `PostgreSQLContainer<>("postgres:16")`, `@Container` static field, `@DynamicPropertySource` to inject `spring.datasource.url/username/password`. Container starts ONCE per test class ("static").
- Database test strategy: H2 (~100 ms boot) fine for simple CRUD; TestContainers REQUIRED for PostgreSQL-specific features (JSON operators, arrays, TIMESTAMPTZ). "TestContainers is our course standard from Lab 9A onwards."
- Spring Boot starter: `spring-boot-starter-test` includes JUnit 5, Mockito, Spring Test, MockMvc, AssertJ, Hamcrest — no extra test deps needed for unit/@WebMvcTest/@DataJpaTest.

## 3. Architecture

- Test layout: `src/test/java` mirrors `src/main/java` package structure; tests are compiled/run by `mvn test` or the IDE.
- Progression ladder (0.6): Simple Java Method → JUnit → Mockito → @WebMvcTest → @DataJpaTest → @SpringBootTest → TestContainers; Session 11 adds Pact, WireMock, Chaos (decision matrix in 0.6).
- Layer-per-test-type mapping (platform examples): service logic → unit tests with Mockito; controllers/HTTP → @WebMvcTest + MockMvc; repositories/DB → @DataJpaTest (+TestContainers when PG-specific); cross-service API shape → Pact (S11); external HTTP dependency → WireMock (S11).
- The 500-incident teaches layer correctness: H2 (embedded) hid a PostgreSQL TIMESTAMPTZ problem that only a TestContainers integration test would catch.
- TestContainers architecture: a real ephemeral Docker container started by the test JVM, random host port (demo: 52341), Spring `@DynamicPropertySource` rewires the DataSource; container lifecycle bound to test class.

## 4. Technologies

- JUnit 5 (`@Test`, `@ParameterizedTest`, `@CsvSource`), Mockito (`@Mock`, `@Spy`, `ArgumentCaptor`, `InOrder`, `when/thenReturn`, `verify`), Spring Boot Test slices (`@WebMvcTest`, `@DataJpaTest`, `@JsonTest`, `@SpringBootTest`, `@MockBean`), MockMvc (jsonPath), AssertJ, Hamcrest — via `spring-boot-starter-test`.
- TestContainers: `org.testcontainers:junit-jupiter` + `org.testcontainers:postgresql`; BOM `testcontainers-bom` version stated as 1.19.3 (in a comment in the slide's pom snippet). Database image used: `postgres:16`. (One demo log in the deck shows `postgres:15-alpine`; the code and lab say postgres:16 — slide inconsistency, recorded as-is.)
- Precise measurements stated in the decks: @WebMvcTest run 2.341 s / 3 tests; TestContainers demo total 4.812 s, random port 52341; H2 boot ~100 ms; "@SpringBootTest is ~10× slower than @WebMvcTest".
- Session 11 preview tools (0.6): Pact, WireMock, Chaos engineering.
- No other exact version numbers are stated (no explicit JUnit/Mockito/Spring Boot version numbers).

## 5. Important terminology

- Verification — building the product correctly (specs, requirements).
- Validation — building the correct product (user needs).
- Shift-Left — moving testing earlier in the lifecycle.
- CI vs CD vs Continuous Deployment — continuous integration / always-deployable (Delivery) / automatic production deploy (Deployment).
- Unit / Integration / System / E2E / Acceptance / Contract test — six types taught with platform examples.
- Testing Pyramid — 70/20/10 distribution and why.
- Test slice — context-limited Spring test (@WebMvcTest, @DataJpaTest, @JsonTest).
- @MockBean — replaces a bean in the Spring test context with a Mockito mock.
- ArgumentCaptor — captures the argument passed to a verified call for later assertions.
- @Mock vs @Spy — full fake vs real-object-with-stubbing.
- Flaky test — passes/fails without code change (kills trust).
- TestContainers / `@Container` / `@DynamicPropertySource` — real dependency containers wired into the test context.
- `@AutoConfigureTestDatabase(replace = NONE)` — stop Spring from swapping the real DB for an embedded one (required with TestContainers).
- AAA — Arrange, Act, Assert.

## 6. Code concepts

- First tests (0.7): Calculator JUnit example with AAA; assertion family; reading failures (Expected: 8 / Actual: 7); running via IntelliJ or `mvn test`; first Mockito example with `mock()`, `when().thenReturn()`, `verify()`.
- Parameterized unit test (delivery deck, live coding): `@ParameterizedTest` + `@CsvSource({"SILVER, 5", "GOLD, 10", "PLATINUM, 15"})` for `calcDiscount`.
- ArgumentCaptor example: `verify(orderRepository).save(orderCaptor.capture())`, then assert `captor.getValue()` has PENDING status. (capture() must be called INSIDE verify() — common-issue list.)
- @WebMvcTest example: `@MockBean ProductService`; tests GET 200 with jsonPath, GET 404, POST 400; context is web-only and fast (2.341 s, 3 tests).
- TestContainers example:
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)
@Testcontainers
class ProductRepositoryIntegrationTest {
  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
      .withDatabaseName("testdb") /* ... */;
  @DynamicPropertySource
  static void props(DynamicPropertyRegistry registry) { /* url/username/password */ }
  // tests: save_andFindById_roundTrip, findByPriceLessThan
}
```
- pom test dependencies (slide snippet): `spring-boot-starter-test`; `org.testcontainers:junit-jupiter`; `org.testcontainers:postgresql`; TestContainers BOM 1.19.3.

## 7. Configuration

- `mvn test` runs the whole test suite from the host; also runnable from the IDE.
- `@DynamicPropertySource` is the configuration bridge that points Spring at the ephemeral container (`spring.datasource.url/username/password`).
- `@AutoConfigureTestDatabase(replace = NONE)` configuration step required so TestContainers' PostgreSQL is really used, not replaced by H2.
- `@MockBean` configures the Spring test context with mocks for collaborators (replaces real bean).
- No properties files/env changes beyond these are described in the decks.

## 8. Failure scenarios

- H2 vs PostgreSQL divergence (TIMESTAMPTZ vs TIMESTAMP) — 47 green unit tests, production 500 (opening story). Fix: right test at the right layer, TestContainers for PG-specific features.
- Flaky tests — pass/fail without code change; destroy confidence; called out under Fast/Reliable/Valuable.
- Testing at the wrong layer (unit test where integration is needed; over-mocked tests that only verify implementation).
- `Could not find a valid Docker environment` (TestContainers) — fix per common-issues list: check `DOCKER_HOST` / start Docker Desktop.
- `@DataJpaTest` "No qualifying bean" — fix: `@Import` the missing configuration.
- MockMvc import/scope mistakes listed in common issues; H2→TestContainers swap mistakes.
- 100%-coverage-with-meaningless-tests anti-pattern ("80% meaningful coverage better than 100% meaningless").
- Kafka-side test blind spots listed in 0.4: event never arrives, wrong format, deserialization failure, duplicates, out-of-order — integration concerns.

## 9. Trade-offs

- Unit vs integration vs E2E: speed/confidence trade-off (ms vs seconds vs minutes) captured by the pyramid and the confidence/cost table.
- H2 (fast ~100 ms, no Docker) vs TestContainers (real PG behavior, slower, needs Docker) — use H2 for simple CRUD, TestContainers when PostgreSQL-specific behavior matters.
- @SpringBootTest (full context, ~10× slower than @WebMvcTest) — use only when wiring itself is under test.
- Mocking everywhere vs integration tests — over-mocking tests implementation, not behavior ("test behavior not implementation").
- Microservices: more integration tests needed than in a monolith (contract boundaries) — accepted cost.
- E2E coverage deliberately small (10%) and deferred to Phase 3/Session 23.

## 10. Common mistakes

- Testing implementation details instead of behavior.
- Writing only unit tests and believing the system works (H2 story; "a collection of perfectly tested services does not guarantee a perfectly working system").
- Using H2 for tests that depend on PostgreSQL-specific features.
- @Spy on an interface; spying an abstract class without a no-arg constructor.
- ArgumentCaptor: calling `capture()` outside `verify()`.
- `@AutoConfigureTestDatabase(replace = NONE)` omitted → tests silently run on H2 again.
- Chasing 100% coverage instead of meaningful coverage.
- Flaky tests left in the suite.
- MockMvc import/scope mistakes (wrong MockMvc/MockMvcRequestBuilders import).
- "Could not find a valid Docker environment" → forgetting Docker Desktop / DOCKER_HOST.
- `@DataJpaTest` missing bean → forgetting `@Import`.

## 11. Interview questions

UNKNOWN — REQUIRES SOURCE REVIEW (for a slide-authored interview-question list — none is printed in the decks). Questions below mirror the decks' quizzes, knowledge checks, and decision tables:
- Verification vs validation?
- Why does the Testing Pyramid put 70% at unit level? How many tests / how long per layer in this course?
- Why do microservices need MORE integration tests than a monolith?
- @SpringBootTest vs @WebMvcTest — what loads, what speed difference did the slides state?
- @Mock vs @Spy; when can you not use @Spy?
- What does @MockBean do in a @WebMvcTest?
- Why did 47 green unit tests miss the TIMESTAMPTZ bug? What test would have caught it?
- When H2 and when TestContainers? What does `replace = NONE` do?
- What is a flaky test and why are they worse than failing tests?
- Pre-Session 11 knowledge check (stated in slides): Pact consumer vs provider; why a provider test can pass while the consumer fails; what a pact file is and who owns it; bonus: WireMock vs Pact.
- Quiz: 8 questions / 10 minutes (delivery deck).

## 12. What I must memorize

- Pyramid numbers: 70% unit / 20% integration / 10% E2E; ~70/~20/~5 tests; ms/seconds/minutes.
- "@SpringBootTest is ~10× slower than @WebMvcTest"; @WebMvcTest demo 2.341 s; TestContainers demo 4.812 s, random port.
- H2 ~100 ms boot; H2 vs PostgreSQL comparison (JSON operators, arrays, TIMESTAMPTZ are the PG-specific triggers).
- TestContainers recipe: `@DataJpaTest` + `@Testcontainers` + `@Container static PostgreSQLContainer<>("postgres:16")` + `@DynamicPropertySource` + `@AutoConfigureTestDatabase(replace = NONE)`.
- Mockito rules: @Mock = fake, @Spy = real object; capture() inside verify(); never @Spy an interface.
- pom test deps: spring-boot-starter-test; testcontainers junit-jupiter + postgresql; BOM 1.19.3.
- The six test types and which tool/annotation serves each layer.
- Good test characteristics: Fast, Reliable, Valuable + Simple, Independent, Repeatable, Readable, Maintainable.
- The 5 principles: incl. "test behavior not implementation" and "tests are production code".
- "TestContainers is our course standard from Lab 9A onwards."

## 13. What I must understand

- Why testing is both verification and validation, and how defect cost drives shift-left.
- Why automated testing is a prerequisite for CI/CD (10 h/day manual math).
- Why each layer of the pyramid buys a different kind of confidence and why the pyramid is narrow at the top.
- Why green unit tests cannot prove wiring/serialization/DB compatibility (the 500 story).
- How spring-boot-starter-test, slices, and MockMvc fit together in a fast test.
- How TestContainers + @DynamicPropertySource actually wire the real DB into the Spring context.
- When mocking is appropriate (isolating a unit) vs when it lies (mocking across service boundaries).

## 14. What I should implement from memory

- ProductServiceTest: `@ParameterizedTest` + `@CsvSource` over SILVER/GOLD/PLATINUM `calcDiscount` plus one ArgumentCaptor test (save captured with PENDING status).
- ProductControllerTest: `@WebMvcTest` with `@MockBean ProductService`; GET 200 (jsonPath), GET 404, POST 201, POST 400.
- ProductRepositoryIntegrationTest: `@DataJpaTest` + TestContainers `postgres:16` (save-and-find round-trip, findByPriceLessThan) with `replace = NONE` and `@DynamicPropertySource`.
- Run all of it with `mvn test` from the host and read failures (Expected/Actual).
- Set up the pom test dependencies (starter-test + TestContainers junit-jupiter/postgresql, BOM 1.19.3).

## 15. Relationship to previous sessions

- Session 9 (Docker): TestContainers depends on Docker being installed/running; `docker compose up -d` must keep working (no port leaks) per the Definition of Done.
- Phase 1 services (product-service etc.) are the subject under test (calcDiscount, ProductController, ProductRepository).
- Circuit-breaker fallback and retry concepts (Session 4-era build, referenced in S11 chaos) are the failure-handling this session only unit-tests around; fallback verification with WireMock comes in Session 11.
- Roadmap position: Testing I of II (S10 of 29), between Docker (S9) and Contract & Chaos (S11).

## 16. Relationship to future sessions

- Session 11 (Contract & Chaos): contract tests (Pact), WireMock for external HTTP, and chaos experiments (Circuit Breaker hypothesis testing) — pre-read Pact consumer-driven contract testing.
- Session 12 (Saga Orchestration): orchestrator unit tests mock KafkaTemplate (stated in S12 lab); the mocking skills here are the prerequisite.
- Session 23 (Phase 3): E2E / load testing gets its own session — that is where the deferred 10% pyramid layer is covered.
- CI/CD (S13): `mvn test` green is the blocking quality gate in the pipeline.
- Kafka testing story (duplicates, out-of-order, deserialization) will recur when saga/topic flows are tested (S12 forward).

## 17. Lab relationship

- Delivery deck LAB 9A — "Write Tests for Product Service", 50 minutes, on product-service. Grading stated: Feature 70% + Tests 20% + Quality 10%.
  - Step 1 — Unit tests, ~12 min: ProductServiceTest; `calcDiscount` for SILVER/GOLD/PLATINUM via `@ParameterizedTest` + `@CsvSource`; plus an ArgumentCaptor test.
  - Step 2 — `@WebMvcTest`, ~18 min: ProductControllerTest; GET 200, GET 404, POST 201, POST 400; `@MockBean` + jsonPath.
  - Step 3 — TestContainers, ~20 min: ProductRepositoryIntegrationTest with postgres:16; save-and-find round-trip; findByPriceLessThan; `@AutoConfigureTestDatabase(replace = NONE)`.
- HOMEWORK before Session 11: `mvn test` — all 3 test classes green. Pre-reading: Consumer-Driven Contract Testing (Pact) link in the Session Pack.
- Daily Quiz: 8 questions / 10 minutes (Google Forms).
- Definition of Done for Session 10 (as stated): ProductServiceTest with @ParameterizedTest + ArgumentCaptor green; ProductControllerTest with 4 @WebMvcTest cases; ProductRepositoryIntegrationTest with 2 TestContainers tests; `mvn test` with zero failures/skipped; `docker compose up -d` still works (no port leaks).
- Checkpoint commit: `session-10: add-unit-and-integration-tests`.
- Demo logs (Part of the lecture): @WebMvcTest run 2.341 s / 3 tests; TestContainers run 4.812 s, container port 52341 mapped; TestContainers "Container starts ONCE per test class ('static')".
- Common issues & fixes table (slide): MockMvc import/scope; H2→TestContainers swap; "Could not find a valid Docker environment" → DOCKER_HOST/Docker Desktop; ArgumentCaptor capture() inside verify(); @DataJpaTest no qualifying bean → @Import.
- Note: the Part 0 deck states Session 10 (including the deeper @Mock/@Spy/ArgumentCaptor/InOrder treatment) as the follow-through of the 0.7 section; the delivery deck is the delivery vehicle of that promise.
