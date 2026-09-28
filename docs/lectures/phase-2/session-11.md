# Session 11 — Testing: Contract & Chaos

Source files:
- `Session_11_Testing_Contract_Chaos.pdf` — 35-slide delivery deck (Wednesday online 15:00–17:30): the Field Rename Incident, consumer-driven contract testing with Pact, WireMock for external HTTP, chaos engineering for circuit breakers, Lab 9B, homework, quiz, Definition of Done.

## 1. Why this topic exists

- Opening story — "The Field Rename Incident": order-service had a mocked InventoryClient in tests, everything green, and both teams shipped. inventory-service renamed the response field `available` → `inStock`. Both services were 100% tested in isolation; in production every order was rejected. Lesson: unit and integration tests inside one service cannot protect the API shape BETWEEN two services.
- Contract testing closes that gap: the consumer's expectations are recorded and automatically verified against the provider, so a rename fails a build instead of production.
- Chaos testing closes the second gap: resilience configuration (Circuit Breaker fallback built earlier) was never verified against real failure — chaos engineering proves that configured behavior actually happens.
- "CS-05 Failure Flow" callback: "we CONFIGURED the fallback then, we VERIFY it here."

## 2. Core concepts

- Consumer-Driven Contracts (Pact): the consumer defines the expected request/response; the generated contract (pact file) is verified by the provider. Choice for this course: order-service (consumer) → inventory-service (provider).
- Provider-driven vs consumer-driven table: who defines expectations, how the contract artifact is produced, which direction verification flows. Both are presented; consumer-driven is the course choice.
- Contract test scope (explicit slide): it is NOT end-to-end testing and NOT business-logic testing — it verifies only that the API SHAPE (paths, methods, query params, status, payload fields/types) matches; it is fast and needs no real running server on the consumer side.
- Pact workflow: consumer test runs Pact DSL → `target/pacts/order-service-inventory-service.json` is generated → provider-side verification runs against that file.
- Roles table: consumer = order-service (calls via Feign); provider = inventory-service (endpoint `/check`); Pact File = generated JSON contract; Pact Broker = the sharing server — "In this course: local file sharing (Broker is optional for teams)" (the file path `../order-service/target/pacts` is used instead).
- WireMock vs Mockito decision rule: HTTP-level dependency → WireMock (real embedded HTTP server); in-process bean → Mockito. "Start with Mockito, add WireMock later" — add WireMock only when the transport/HTTP behavior matters.
- WireMock concept: a REAL HTTP server (unlike Mockito's in-JVM mock), so the HTTP client, serialization, headers, and circuit breaker all behave as in production.
- Chaos Engineering: a formal experiment loop — hypothesis → experiment → result; deliberately inject failure and observe; here: stop the dependency and verify the circuit breaker opens and the fallback returns a graceful PENDING instead of an error.
- Resilience verification follows the configured Circuit Breaker states: CLOSED → (failures) → OPEN → (recovery window ~10 s) → HALF_OPEN → CLOSED.

## 3. Architecture

- Pact topology: order-service consumer test builds a mock server (Pact) and a Feign client pointed at it → interaction recorded → JSON pact file in `target/pacts/` → inventory-service provider verification reads the folder and replays the requests against its real HTTP port.
- Provider verification environment: `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `@LocalServerPort` + HttpTestTarget("localhost", port) — the provider's real endpoints run and are exercised.
- WireMock topology: test-scoped embedded HTTP server replaces the real inventory-service; the order-service code under test still speaks real HTTP; `@AutoConfigureWireMock(port = 0)` random port wired via property.
- Chaos topology: full platform running (docker compose); `docker compose stop inventory-service` removes a real dependency; order-service callers keep calling; the Circuit Breaker tripping is observed through Actuator (`/actuator/circuitbreakers`) and through the API response (PENDING instead of 500/timeout).

## 4. Technologies

- Pact (consumer side): `au.com.dius.pact.consumer:junit5` version 4.6.7 (order-service).
- Pact (provider side): `au.com.dius.pact.provider:junit5spring` version 4.6.7 (inventory-service).
- JUnit 5 Pact extensions/annotations: `@ExtendWith(PactConsumerTestExt.class)` + `@PactTestFor(providerName = "inventory-service", port = "8888")` (consumer); `@Provider("inventory-service")` + `@PactFolder("../order-service/target/pacts")` + `@TestTemplate` + PactVerificationInvocationContextProvider + `@State` (provider).
- OpenFeign (`Feign.builder().decoder(new JacksonDecoder())`) as the consumer's HTTP client; Jackson.
- WireMock via `org.springframework.cloud:spring-cloud-contract-wiremock` (test scope, BOM-managed — no version stated in the slide).
- WireMock annotations/DSL: `@AutoConfigureWireMock(port = 0)`, `stubFor(...)`, matchingJsonPath, verify postRequestedFor, random port injection.
- Spring Boot Actuator endpoints used in chaos: `curl http://localhost:8082/actuator/circuitbreakers` (CircuitBreaker state OPEN/HALF_OPEN/CLOSED); bearer token used in curl: `-H 'Authorization: Bearer <test-jwt>'`.
- Docker Compose as chaos tool: `docker compose stop inventory-service` / start it again.
- No other versions are stated (no WireMock/Spring Cloud version, no Chaos toolkit — the "tool" is compose stop + Actuator observation).

## 5. Important terminology

- Contract — the agreed API shape between a consumer and provider.
- Consumer-driven contract — expectations are authored by the consumer.
- Pact file — generated JSON (`target/pacts/order-service-inventory-service.json`) describing interactions; team-owned artifact.
- Pact Broker — server for sharing/versioning pacts; optional here; local folder sharing is the course mode.
- Provider verification — replaying pact interactions against the real provider.
- `given(...)` — provider state phrase (e.g. "PROD-001 has 100 units in stock").
- `uponReceiving(...)` — consumer-side description of the interaction.
- LambdaDsl / body matchers — `booleanValue("available", true)`, `integerType("remainingStock", 95)` (types + values, not exact-value matching).
- `@State` — provider-side method that sets up the state named by `given`.
- WireMock stub — canned HTTP response for a request matcher.
- Chaos experiment — hypothesis/experiment/result loop; e.g. "if inventory-service dies, orders degrade to PENDING, not 500".
- Circuit Breaker states — CLOSED / OPEN / HALF_OPEN; recovery window ~10 s in the demo.
- Fallback — the graceful alternative result (PENDING) when the dependency fails.

## 6. Code concepts

- Consumer test (order-service): `@ExtendWith(PactConsumerTestExt.class)`, `@PactTestFor(providerName = "inventory-service", port = "8888")`; `@Pact` method building the interaction:
  `.given("PROD-001 has 100 units in stock").uponReceiving(...).path("/api/v1/inventory/check").method("GET").query("productId=PROD-001&quantity=5").willRespondWith().status(200).body(LambdaDsl.newJsonBody(body -> body.booleanValue("available", true).integerType("remainingStock", 95)).build())`;
  the test then builds the Feign client against the Pact mock server (`Feign.builder().decoder(new JacksonDecoder())`) and asserts the returned object.
- Provider verification (inventory-service): `@Provider("inventory-service")`, `@PactFolder("../order-service/target/pacts")`, `@SpringBootTest(webEnvironment = RANDOM_PORT)`; `@LocalServerPort int port;` target `new HttpTestTarget("localhost", port)`; `@TestTemplate` + `PactVerificationInvocationContextProvider`; `@State("PROD-001 has 100 units in stock") void resetStock() { ... }`.
- WireMock test (order-service): happy path APPROVED → CONFIRMED with transactionId TXN-001; failure path: stub 503 → result PENDING (Circuit Breaker fallback from Session 4). Payload verification with `matchingJsonPath("$.amount", equalTo("250.0"))`; demo log lines tagged [WIREMOCK]/[CB]/[FALLBACK].
- Chaos demo flow (commands + observations): `docker compose stop inventory-service` → CB OPEN → API answers PENDING → `docker compose start inventory-service` (implied) wait ~10 s → CB HALF_OPEN → CLOSED → next order APPROVED → CONFIRMED. Wrong outcome would be HTTP 500 or a timeout — that fails the experiment hypothesis.

## 7. Configuration

- Consumer-side pom: Pact consumer junit5 4.6.7.
- Provider-side pom: Pact provider junit5spring 4.6.7.
- Provider `@PactFolder` points at the consumer build output (`../order-service/target/pacts`) — local-file sharing is the configured channel (Broker optional).
- WireMock dependency: `spring-cloud-contract-wiremock`, test scope, version-managed by the Spring Cloud BOM (no explicit version written).
- `@AutoConfigureWireMock(port = 0)` — random port; injected into the client via properties.
- `@PactTestFor(port = "8888")` — fixed port for the consumer's Pact mock server.
- Chaos session: platform running via docker compose; auth header `Authorization: Bearer <test-jwt>` on curl; observe via `/actuator/circuitbreakers`.
- Provider state setup via `@State` methods (e.g. reset stock for "PROD-001 has 100 units in stock").

## 8. Failure scenarios

- The Field Rename Incident — `available` → `inStock`; both suites green; production rejects every order. This is THE failure this session prevents.
- "Rename a field → watch it fail" is a deliberate lab action that must break provider verification — the contract test's job.
- External HTTP dependency down → without proof, the fallback may not work; WireMock 503 test verifies the CB fallback actually returns PENDING.
- Chaos experiment failure would be HTTP 500 or timeout instead of PENDING — the stated "wrong outcome" in the experiment.
- CB stuck OPEN — the ~10 s recovery window transition OPEN → HALF_OPEN → CLOSED is the recovery path that must be observed.
- Provider state missing (`@State`) → verification runs against wrong data.
- Testing business logic or E2E flows in a contract test — out of scope; contract tests only check API shape.

## 9. Trade-offs

- Consumer-driven vs provider-driven contracts — table; consumer-driven chosen because the consumer's requirements drive the recorded expectations (and it is what the course platform needs: order → inventory).
- Pact vs E2E: contract tests are fast and pinpoint the breaking side, but they do NOT prove the whole flow works.
- Pact Broker vs local file sharing: Broker adds versioning/sharing discipline; course uses local files (Broker optional for teams).
- Mockito vs WireMock: Mockito is faster/simpler but never tests HTTP; WireMock is more faithful to production transport at the cost of a server and stubs.
- Chaos engineering: adds deliberate failure into test/demo environments to buy confidence in resilience; must be scoped/hypothesis-driven, not random breakage.
- Contract tests do not test business logic — a complementary layer, not a replacement.

## 10. Common mistakes

- Assuming a green test suite in each service means inter-service integration is safe (the incident itself).
- Writing contract tests as end-to-end tests or business-logic tests (explicit scope slide).
- Forgetting that the consumer test only GENERATES the pact file — someone must run provider verification on it (automation in CI later).
- Breaking provider verification by renaming a field and ignoring it (the lab intentionally shows the failure must surface).
- Using Mockito where HTTP behavior matters (circuit breaker/headers/serialization) — should be WireMock.
- Not defining `@State` for `given(...)` phrases → provider verification failures.
- Chaos: not knowing what the healthy behavior is before injecting failure; treating a 500/timeout as "handled".
- Missing Authorization header on Actuator curls (test-jwt) when security is enabled.

## 11. Interview questions

UNKNOWN — REQUIRES SOURCE REVIEW (for a slide-authored interview-question list — none is printed in the deck). Questions below mirror the deck's quiz topics and knowledge checks:
- What is a consumer-driven contract, and why did both teams pass tests while production failed?
- What exactly is in a pact file, who owns it, and where does it live in this course?
- Why can a provider test pass while the consumer test fails (and vice versa)?
- When do you use WireMock instead of Mockito?
- What does `@AutoConfigureWireMock(port = 0)` do?
- What is a chaos experiment? What hypothesis does the S11 experiment state?
- What are the Circuit Breaker states and what did the ~10 s recovery demonstrate?
- Pre-Session 12 knowledge check (stated in slides): Choreography vs Orchestration; `@StartSaga`; association value.
- Quiz: 8 questions / 10 minutes.
- Bonus question from the pre-S11 knowledge check: WireMock vs Pact — when each?

## 12. What I must memorize

- Pact versions: consumer `au.com.dius.pact.consumer:junit5:4.6.7`; provider `au.com.dius.pact.provider:junit5spring:4.6.7`.
- Pact workflow: consumer test → `target/pacts/order-service-inventory-service.json` → provider verification (@PactFolder ../order-service/target/pacts).
- Consumer annotations: `@ExtendWith(PactConsumerTestExt.class)`, `@PactTestFor(providerName="inventory-service", port="8888")`, `@Pact`, `given`, `uponReceiving`, `willRespondWith`, LambdaDsl body matchers.
- Provider annotations: `@Provider("inventory-service")`, `@PactFolder`, `@SpringBootTest(webEnvironment=RANDOM_PORT)`, `@LocalServerPort`, HttpTestTarget, `@TestTemplate`, `@State`.
- WireMock dependency name: `spring-cloud-contract-wiremock` (BOM-managed, test scope); `@AutoConfigureWireMock(port = 0)`.
- WireMock tests: 200 → APPROVED→CONFIRMED (TXN-001); 503 → PENDING via CB fallback.
- Chaos flow: stop → CB OPEN → PENDING → start → ~10 s → HALF_OPEN → CLOSED → CONFIRMED; wrong outcome = 500/timeout.
- `curl http://localhost:8082/actuator/circuitbreakers` and the Bearer test-jwt header.
- Contract scope: API shape only — not E2E, not business logic.
- Local file sharing in course; Pact Broker optional.

## 13. What I must understand

- Why inter-service API shape is a different risk class than intra-service logic (rename incident mechanics: consumer mock hides provider change).
- How the pact file is generated, what it contains, and how verification consumes it.
- Why consumer-driven was chosen for order-service → inventory-service.
- Why WireMock's real HTTP server is required to exercise circuit-breaker/HTTP-client behavior that Mockito bypasses.
- How a chaos experiment translates a resilience CLAIM into evidence (hypothesis → experiment → result; the ~10 s state machine).
- Why contract tests are fast and stable (no real full-system boot, no network) yet narrow (shape only).

## 14. What I should implement from memory

- Write the Pact consumer test for order-service: @Pact builder with given/uponReceiving/query/willRespondWith + LambdaDsl body, Feign client against the mock server, assert the mapped response; run it and inspect the generated pact JSON.
- Write the provider verification test for inventory-service: @Provider/@PactFolder/@SpringBootTest RANDOM_PORT/@LocalServerPort/HttpTestTarget/@TestTemplate + @State method.
- Demonstrate the rename failure: change `available` to `inStock` in the provider and watch verification fail.
- Write the two WireMock tests (happy path APPROVED→CONFIRMED with TXN-001; 503 → PENDING via fallback).
- Run the chaos experiment with docker compose + Actuator and observe all CB state transitions and the ~10 s recovery.

## 15. Relationship to previous sessions

- Session 4-era configuration: the Circuit Breaker + fallback behavior was BUILT (configured) earlier ("CS-05 Failure Flow") and is now VERIFIED.
- Session 10 (unit/integration): the pyramid's place for these tests — S11 adds the cross-service layer that unit/integration tests cannot cover (the Field Rename Incident is the direct consequence of S10's scope).
- Session 9 (Docker): TestContainers/Docker first; WireMock runs as an in-JVM HTTP server; chaos uses docker compose.
- Phase 1 services: order-service (consumer, port 8082) and inventory-service (provider, port 8084) are the actual platform services.

## 16. Relationship to future sessions

- Session 12 (Saga Orchestration) — announced as the next session ("Next: Session 12 Saga Orchestration; Monday 3:00–5:30 PM"). The pre-S12 check covers Choreography vs Orchestration, @StartSaga, association value.
- CI/CD (S13): contract verification and WireMock tests become pipeline stages (pacts must be generated/verified in automation — Broker helps teams).
- Contract testing protects the inter-service refactors coming with saga orchestration, CI/CD, and Kubernetes-era changes.
- Chaos engineering is the foundation for later production-readiness topics (resilience verification, gradual rollout concerns).

## 17. Lab relationship

- Delivery deck LAB 9B — "Contract Test + WireMock", 20 minutes in-session, intended to be completed as homework; builds on Lab 9A. Steps (as stated):
  1. Pact consumer test → generate `pact.json`.
  2. Provider verification — "Rename a field → watch it fail".
  3. WireMock test — APPROVED → CONFIRMED; 503 → PENDING.
- Quiz: 8 questions / 10 minutes.
- Definition of Done for Session 11 (as stated): the three lab steps above, with the rename failure demonstrated and the WireMock happy/failure paths green.
- Checkpoint commit: `session-11: add-contract-tests-wiremock-order-inventory`.
- Demo/observability evidence used in the lecture: WireMock demo logs [WIREMOCK]/[CB]/[FALLBACK]; chaos commands `docker compose stop inventory-service`, `docker compose start` (recovery), `curl http://localhost:8082/actuator/circuitbreakers` showing OPEN / HALF_OPEN / CLOSED, ~10 s recovery window; authorized curl uses `-H 'Authorization: Bearer <test-jwt>'`.
- Pre-Session 12 knowledge check (given in the deck): Choreography vs Orchestration; `@StartSaga`; association value.
