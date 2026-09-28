# Session 12 — Saga Orchestration

Source files:
- `Session_12_Saga_Orchestration.pdf` — 28-slide delivery deck (Monday online 15:00–17:30): why orchestration after Session 7 choreography, orchestrator design, SagaState state machine, code walkthrough, demo logs, Lab 10A, tech debt, homework, Definition of Done.

## 1. Why this topic exists

- Session 7 built the Saga pattern as CHOREOGRAPHY: each service reacts independently to events; no central coordinator.
- Real pilot flow outgrew it — the 5-step order flow: Reserve Inventory → Fraud Check → Loyalty Points → Process Payment → Schedule Delivery, with the rule "if fraud risk > 0.7 AND order total > 500 EGP, skip loyalty" — choreography needs every participant to know such conditional rules (or implicit conventions), which does not scale.
- Three failure modes of choreography named in the deck:
  1. Invisible State — nobody can answer "where is this order in the saga right now?"
  2. Conditional Logic Sprawl — branching business rules are scattered across services.
  3. Compensation Ambiguity — it is unclear who triggers compensating actions (e.g. releasing stock when payment fails).
- Session 12 adds ORCHESTRATION: a single OrderSagaOrchestrator owns the decision tree. Explicitly stated: the Session 7 code is NOT deleted — choreography and orchestration coexist; "a real team picks one per flow".
- "The Orchestrator is the BRAIN. Services are the HANDS."

## 2. Core concepts

- Saga orchestration: one coordinator sends COMMANDS to participants and listens for RESULT events, maintaining the saga's state.
- Orchestrator's two roles: Command Sender (`kafkaTemplate.send(...)`, asynchronous — unlike synchronous OpenFeign calls) and Result Listener (`@KafkaListener` methods).
- Command vs event: the orchestrator sends commands (`ReserveInventoryCommand`, `ProcessPaymentCommand`, `ReleaseInventoryCommand`); services reply with result events.
- SagaState enum — the explicit state machine (9 states): STARTED, INVENTORY_RESERVING, INVENTORY_RESERVED, PAYMENT_PROCESSING, COMPLETED (+ failure/compensation states) INVENTORY_RESERVE_FAILED, PAYMENT_FAILED, INVENTORY_RELEASING, CANCELLED.
- Idempotency guards: every result handler begins with "if current state is not the expected state, return" — prevents double-processing of duplicate events.
- Compensation decided by the orchestrator: on payment failure the orchestrator itself sends `ReleaseInventoryCommand` and moves to INVENTORY_RELEASING (choreography left this ambiguous). On inventory reserve failure no compensation is needed (nothing was reserved).
- Distinct Kafka consumer groupIds per handler: `orchestrator-inventory`, `orchestrator-payment`, `orchestrator-compensation` — each handler consumes its topic independently.
- In-memory state store: `Map<String, SagaState> sagaStates = new ConcurrentHashMap<>()` — documented DEV ONLY, lost on restart; "Production: persist SagaState to DB (see Homework §8)".
- CS-09 course slide: "The State Diagram IS the Design" — draw the transitions on paper first; "prevents half the bugs".
- CS-09 comparison callback: S7 configured the saga flow, S12 makes a single component own decisions; compensation logic comparison shown side-by-side (choreography: inventory-service listens and self-releases; orchestration: orchestrator sends ReleaseInventoryCommand).

## 3. Architecture

- Components: order-service hosts OrderSagaOrchestrator (@Service @Slf4j) + the existing S7 createOrder flow; inventory-service and payment-service are command consumers / event producers on Kafka.
- Command topic flow: orchestrator → `kafkaTemplate.send("saga-commands", orderId, new ReserveInventoryCommand(...))` (message key = orderId); results arrive on listener methods grouped by dedicated groupIds.
- Per-listener topics (from handler code): inventory result listener (groupId `orchestrator-inventory`), payment result listener (groupId `orchestrator-payment`), inventory-released compensation listener (groupId `orchestrator-compensation`).
- State flow (happy path): STARTED → INVENTORY_RESERVING → (INVENTORY_RESERVED) → PAYMENT_PROCESSING → COMPLETED, Order saved/updated to CONFIRMED (demo: ORD-789 CONFIRMED).
- State flow (compensation path): STARTED → INVENTORY_RESERVING → INVENTORY_RESERVED → PAYMENT_PROCESSING → PAYMENT_FAILED → INVENTORY_RELEASING → CANCELLED (demo: ORD-790 CANCELLED).
- State flow (inventory failure): INVENTORY_RESERVING → INVENTORY_RESERVE_FAILED → CANCELLED (no compensation needed; saga state removed).
- Both sagas coexist: `createOrder()` (S7 choreography) and `startSaga()` (S12 orchestration) both exist in order-service.
- In-memory sagaStates map is the weak point: orchestrator crash = in-memory state lost (side-by-side table calls this out explicitly).

## 4. Technologies

- Apache Kafka via Spring Kafka: `KafkaTemplate.send`, `@KafkaListener` with `groupId` per handler; topics referenced: `saga-commands` (commands) plus result/compensation topics consumed by the three listeners.
- Spring Boot service layer annotations: `@Service`, `@Slf4j`.
- `ConcurrentHashMap` for the dev-only saga state.
- Testing: unit tests mock `KafkaTemplate` (per Lab 10A step 3); alternative mentioned: `@EmbeddedKafka` for Spring Kafka consumers.
- External API style comparison (side-by-side table): Kafka commands are async vs OpenFeign synchronous.
- Advanced reference (explicitly "not taught" — listed for further study): Axon Framework.
- No version numbers for Kafka/Spring Kafka/Axon are stated in this deck.

## 5. Important terminology

- Saga — a sequence of local transactions coordinated either by events (choreography) or a coordinator (orchestration).
- Orchestrator — the component that owns the saga decision tree and state.
- Command — an instruction to a participant (ReserveInventoryCommand, ProcessPaymentCommand, ReleaseInventoryCommand).
- Result event — a participant's reply consumed by @KafkaListener handlers.
- SagaState — the enum modeling saga progress (9 values listed above).
- Transition — the `transition()` helper that moves state and logs with a `[SAGA]` prefix.
- Idempotency guard — state check at the top of a handler so duplicate events are ignored.
- Compensation — the corrective action (release inventory) triggered by the orchestrator on failure.
- Invisible state — the choreography failure mode where no one knows the current status.
- Tech debt (documented): in-memory sagaStates map; proper fix = persistent saga state (DB); the "full fix pattern" named: Event Sourcing (Phase 3, Session 19).

## 6. Code concepts

- `startSaga()`: generate UUID orderId; save Order with PENDING status; `sagaStates.put(orderId, STARTED)`; `kafkaTemplate.send("saga-commands", orderId, new ReserveInventoryCommand(...))` (a COMMAND — deliberately not a domain event); transition to INVENTORY_RESERVING; return a PENDING response.
- `transition()` helper: updates the map and logs with `[SAGA]` prefix (observability of state changes).
- `handleInventoryResult(...)`— groupId "orchestrator-inventory": guard `if (current != INVENTORY_RESERVING) return;` (idempotency); success → send ProcessPaymentCommand + PAYMENT_PROCESSING; failure → INVENTORY_RESERVE_FAILED + CANCELLED + remove from map (no compensation needed).
- `handlePaymentResult(...)` — groupId "orchestrator-payment": guard PAYMENT_PROCESSING; success → COMPLETED + Order CONFIRMED; failure → PAYMENT_FAILED + send ReleaseInventoryCommand + INVENTORY_RELEASING (orchestrator decides compensation).
- `handleInventoryReleased(...)` — groupId "orchestrator-compensation": → CANCELLED + remove saga state.
- Demo logs: happy saga ORD-789 CONFIRMED; compensation saga ORD-790 CANCELLED.
- S7 vs S12 comparison snippet shown side by side: choreography compensation is implemented inside the participant; orchestration compensation is a command emitted by the orchestrator.

## 7. Configuration

- Kafka producers/consumers via Spring Kafka defaults (KafkaTemplate injection; @KafkaListener with explicit groupId per handler).
- WARNING stated for tests: mock `KafkaTemplate` so @KafkaListener beans do not start real consumers during unit tests; `@EmbeddedKafka` is the alternative when a broker is needed.
- Message key = orderId for command correlation on `saga-commands`.
- State persistence: currently in-memory (dev only); production = persist SagaState to DB (homework), full pattern Event Sourcing in Phase 3 / Session 19.
- No exact Spring Boot / Kafka configuration values (brokers, serializers) are stated in this deck beyond the above.

## 8. Failure scenarios

- Choreography failure modes motivating the session: Invisible State, Conditional Logic Sprawl, Compensation Ambiguity.
- Orchestrator crash → in-memory saga state lost (side-by-side table; tech debt; homework to persist).
- Duplicate delivery of result events → idempotency guard rejects stale transitions (tested rationale).
- Payment failure → must trigger inventory release; the orchestrator owns it (PAYMENT_FAILED → ReleaseInventoryCommand → INVENTORY_RELEASING → CANCELLED).
- Inventory reserve failure → CANCELLED with no compensation (nothing to undo).
- Duplicate @KafkaListener consumers starting during unit tests → mitigated by mocking KafkaTemplate (common issues).
- Multiple listeners sharing one groupId would steal each other's messages — hence the three distinct groupIds (orchestrator-inventory / orchestrator-payment / orchestrator-compensation).
- Wrong-state events (late/duplicate) must not corrupt state — guard returns early.

## 9. Trade-offs

- Orchestration vs choreography (side-by-side comparison table includes): who decides, where business logic lives, how inventory releases stock, where state lives, and the orchestrator crash = in-memory state lost.
- Decision table (deck) lists the selection factors: 3 services/simple flow; complex conditional logic (4+ branching); full audit trail; avoiding a single point of failure; a team new to event-driven; multiple teams on different schedules; frequently changing business rules — conclusion: "Many production systems use BOTH". (Note: the extracted two-column table was partially scrambled in text extraction; recordings above preserve the factor list — re-verify exact column mapping against the PDF before quoting a pairing.)
- Orchestrator as SPOF (state + decision ownership) vs choreography's distributed resilience but invisible state.
- Async commands (KafkaTemplate) vs sync calls (OpenFeign) — no blocking, but eventual consistency and harder tracing.
- In-memory state (fast, simple, dev-only) vs persistent state (homework; durable, more code).
- Both flows coexist in order-service: richer platform vs duplicated order-entry paths (createOrder vs startSaga).

## 10. Common mistakes

- Using one Kafka groupId for multiple orchestrator listeners.
- Omitting idempotency guards — duplicate results corrupt the saga.
- Forgetting that in-memory sagaStates is lost on restart (and not marking it dev-only).
- Sending domain events instead of commands from the orchestrator (the slide underlines COMMAND).
- Starting real Kafka consumers in unit tests (real @KafkaListener beans) — mock KafkaTemplate instead.
- Not drawing/documenting the state diagram first ("The State Diagram IS the Design" — CS-09).
- Assuming choreography must be deleted when orchestration is added — the slides say both coexist.
- Testing saga logic via internals only: expose a package-private getSagaState test helper, or use an ArgumentCaptor on KafkaTemplate per the lab/known-issues guidance.

## 11. Interview questions

UNKNOWN — REQUIRES SOURCE REVIEW (for a slide-authored interview-question list — none is printed in the deck). Questions below mirror the deck's decision table, comparison tables, and quizzes:
- Choreography vs Orchestration: trade-offs and when each wins (decision factors in section 9).
- Why does orchestration make state visible, and what does the orchestrator own?
- Why commands instead of events from the orchestrator?
- Walk the 9 SagaState values and the happy/compensation transitions.
- Where is compensation decided in choreography vs orchestration (S7 vs S12 code comparison)?
- What happens to in-flight sagas if the orchestrator crashes (today and with the homework fix)?
- How do you make result handlers idempotent?
- Why does each handler need its own consumer groupId?
- How would you unit-test an orchestrator without a Kafka broker (mock KafkaTemplate / @EmbeddedKafka)?
- Pre-Session 13 check (stated in slides): GitHub Actions job vs step; `on: push: branches: [main]`; the Docker build-and-push step.

## 12. What I must memorize

- The 9 SagaState values and the valid transitions (draw the diagram).
- startSaga steps: UUID orderId → save Order PENDING → sagaStates.put(STARTED) → send ReserveInventoryCommand to "saga-commands" keyed by orderId → INVENTORY_RESERVING.
- The three groupIds: orchestrator-inventory, orchestrator-payment, orchestrator-compensation.
- The three commands: ReserveInventoryCommand, ProcessPaymentCommand, ReleaseInventoryCommand.
- The guard line pattern: `if (current != EXPECTED_STATE) return;`.
- Compensation ownership: orchestrator sends ReleaseInventoryCommand on payment failure; no compensation when the reserve itself fails.
- In-memory ConcurrentHashMap = tech debt; production fix = persist saga state (DB); full fix pattern = Event Sourcing (Phase 3 / Session 19).
- Demo results: ORD-789 CONFIRMED / ORD-790 CANCELLED.
- "The Orchestrator is the BRAIN. Services are the HANDS."
- "The State Diagram IS the Design." (CS-09)

## 13. What I must understand

- Why the 5-step conditional flow ("fraud risk > 0.7 AND total > 500 EGP → skip loyalty") breaks choreography and why centralizing the decision tree fixes it.
- Why state visibility and compensation clarity are the core wins (interview-grade answer).
- How the async command/reply loop via KafkaTemplate + @KafkaListener implements the coordinator without blocking.
- Why commands are directed (one recipient) while events are broadcast — and what that means for coupling.
- Why idempotency guards are mandatory in event-driven systems (duplicate delivery is normal).
- Why both patterns can coexist in one codebase and how a team chooses per flow.

## 14. What I should implement from memory

- Define the commands + result events + 9-value SagaState enum (Lab 10A step 1: 3 commands + result events, all 9 states).
- Build OrderSagaOrchestrator from scratch: startSaga, handleInventoryResult, handlePaymentResult, handleInventoryReleased, transition() helper with [SAGA] logging, three distinct groupIds, idempotency guards.
- Unit tests: mock KafkaTemplate; verify startSaga → INVENTORY_RESERVING and that payment failure sends ReleaseInventoryCommand (compensation test).
- Draw (on paper/markdown) the complete state diagram with all transitions before coding (CS-09 discipline).
- Reproduce the demo: happy saga → CONFIRMED, compensation saga → CANCELLED.

## 15. Relationship to previous sessions

- Session 7 — Choreography saga (createOrder + event reactions) is the direct predecessor; S12 explicitly does NOT delete it; side-by-side compensation comparison given.
- Session 4-era resilience (OpenFeign, circuit breaker fallback) contrasts with async Kafka commands (the deck contrasts sync OpenFeign vs async kafkaTemplate.send).
- Session 11 (contract/chaos): the pre-S12 check and the verification habits carry over; Kafka is also how order/inventory/payment already communicate in the platform.
- Phase 1 services (order/inventory/payment, Kafka infra) are the runtime of the saga.

## 16. Relationship to future sessions

- Phase 3, Session 19 — named twice: proper secrets/security reference in S9 aside here ("Session 19" appears as the Event Sourcing fix pattern reference in this deck's tech-debt slide) and persistent-state hardening.
- Pre-Session 13 check states the immediate next topic: CI/CD with GitHub Actions (job vs step; `on: push: branches: [main]`; Docker build-and-push step).
- Saga orchestration is the business-flow layer that CI/CD, GitOps, and Kubernetes sessions will build/ship/recover around.
- Axon Framework named as the advanced (not-taught) reference for production saga/orchestration frameworks.

## 17. Lab relationship

- LAB 10A — "Build OrderSagaOrchestrator", 20 minutes in-session, to be completed as homework; builds on Session 7 (which remains unchanged). Steps (as stated):
  1. Define Events & Commands + SagaState enum — 3 commands + result events, all 9 states.
  2. Build the orchestrator — startSaga, handleInventoryResult, handlePaymentResult, handleInventoryReleased, transition.
  3. Unit tests — mock KafkaTemplate; verify startSaga → INVENTORY_RESERVING; verify compensation sends ReleaseInventoryCommand.
- Tech Debt documented in the deck: in-memory ConcurrentHashMap saga state is lost on restart; homework/bonus fix = persistent Saga state; the full fix pattern named = Event Sourcing (Phase 3, Session 19).
- Definition of Done for Session 12 (as stated): the three Lab 10A steps completed — all 9 states defined, orchestrator with all four handlers + transition, unit tests proving happy-path transition and compensation command, and the demo paths (ORD-789 CONFIRMED / ORD-790 CANCELLED) reproduced.
- Checkpoint commit: `session-12: add-orchestration-saga-order-service`.
- Common issues & fixes guidance (lab support): distinct groupIds (orchestrator-inventory/payment/compensation); idempotency guards; package-private getSagaState test helper or KafkaTemplate ArgumentCaptor; mock KafkaTemplate so @KafkaListener beans do not start real consumers; @EmbeddedKafka as alternative.
- Advanced Reference (explicitly not taught in this session): Axon Framework.
- Pre-Session 13 knowledge check (in deck): GitHub Actions job vs step; `on: push: branches: [main]`; Docker build-and-push step.
