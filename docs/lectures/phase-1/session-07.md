# Session 7 — Distributed Transactions (Saga Pattern · Choreography · Kafka · Compensation)

Source files: Session_07_Part 0_ Asynchronous Communication with Kafka.pdf; Session_07_Saga_Kafka.pdf

Coverage map (two decks, one note):
- Session_07_Part 0_ Asynchronous Communication with Kafka.pdf — the pre-saga foundations deck, containing "Session 7 – Part 0: Asynchronous Communication with Kafka" (from OpenFeign to event-driven communication; Producer/Topic/Consumer; first Order Service producer and Notification Service consumer; the sync-vs-async decision question) and "Session 7 – Part 0.5: Why Not Use One Distributed Transaction?" (business inconsistency; ACID in a monolith; 2PC with its two phases and five problems; local transactions; compensating actions; 2PC vs Saga comparison; check-your-understanding questions).
- Session_07_Saga_Kafka.pdf — the live-session deck ("Session 7 of 29"): recap and framing, business inconsistency story, what a Saga is, happy path and compensation path, COMPENSATE ≠ ROLLBACK, mandatory workshop "Draw the Saga on Paper", choreography vs orchestration, Kafka as event transport, live coding of the order/inventory/payment saga handlers, consumer group design, full-saga demo, DoD, common issues.

Deck identity (live deck): "MICROSERVICES COURSE • PHASE 1 • SESSION 7 OF 29 — Distributed Transactions — Saga Pattern • Choreography • Kafka • Compensation", Dr. ElSayed Mohamed Elsayed Baladoh, Wednesday, 2.5 Hours – Online, Phase 1 – Foundation. Slide: "Today: the most architecturally important session in Phase 1 -- where partial failure becomes business inconsistency, and Choreography Sagas restore it."

## 1. Why this topic exists

- Part 0 goal (verbatim): "Before implementing the Saga Pattern, we first learn how two microservices communicate asynchronously using Apache Kafka."
- New requirement after S6: "After an order is created, send a confirmation notification to the customer." But: "Does Order Service need to wait for the email to be sent before completing the request?" Usually No — the order is valid even if the email provider is unavailable, sending takes seconds, or Notification Service restarts. "The notification is a reaction to an event that already happened."
- The bigger problem (Part 0.5 / live deck): "Create Order → Reserve Inventory → Process Payment → Confirm Order" — these are "no longer independent reactions. These steps participate in one larger business process." If payment fails after the first two steps: Order DB = CREATED, Inventory DB = 3 units RESERVED, Payment DB = nothing charged. "The system is now technically running, but the business state is inconsistent."
- Business Inconsistency defined (live deck): "A distributed state problem: each service did its own job correctly, but the SYSTEM as a whole is left in a state that violates a business rule." It is NOT a code bug, NOT a network error, NOT something try/catch was supposed to fix.
- Story told in the live deck: a customer orders 3 units of PROD-001 — order CREATED, stock RESERVED, payment throws an exception. "Next customer tries to buy PROD-001 -- shows out of stock -- but nothing was sold!"
- "Resilience4j (CB/Retry) handles THIS call's failure -- but who fixes the order and the reservation that already happened?"
- Why the monolith answer does not transfer: ACID works because of one database and one connection; microservices have three separate databases — "Each service owns its own data", so no service can roll back another's committed transaction.
- Positioning: S6 = "How do I call another service and wait for the answer?" (OpenFeign); S7 = "How do I publish an event without waiting for every interested service?" (Kafka) and then "How do I maintain business consistency when multiple independent services participate in one distributed business process?" (Saga). "These are not competing technologies. They solve different problems."

## 2. Core concepts

- Synchronous (S6 recap): caller knows the receiver, waits, gets an immediate response; "temporal coupling"; failure affects the current call. Asynchronous (S7): producer publishes an event, does not wait for the consumer, consumers react independently, "Services are more temporally decoupled", multiple consumers can subscribe.
- Sync-or-async decision question (Part 0, verbatim): "Does the caller need the result immediately to continue the current business operation?" YES → consider synchronous (OpenFeign); NO → consider asynchronous (Kafka event). Platform decision table: Order→Inventory stock check Sync ("The answer is needed now"); Order→Product details Sync; Order→Notification Async ("The order should not wait for email"); Payment→Analytics Async ("Analytics does not control payment success"); Order→Audit Async. "Do not make the decision based on: Kafka is more modern. or: REST is easier." "What communication semantics does this business interaction require?"
- Kafka mental model (only three concepts for today): Producer → Topic → Consumer. Platform mapping: Producer = Order Service; Topic = order-created; Consumer = Notification Service. Flow: `KafkaTemplate.send(...)` → `order-created` topic → `@KafkaListener`.
- Command thinking vs Event thinking: sync REST thinks in commands ("Check inventory", "Send notification") — "The caller knows exactly which service it is calling." Event-driven thinks in facts: `OrderCreated` — "Something already happened in the domain." "The producer does not necessarily need to know every service interested in that event." One publish, many independent consumers.
- Naming rule: `OrderCreated`, not `CreateOrder` — "A command asks for something to happen. An event describes something that already happened." Past-tense domain facts: OrderCreated, PaymentCompleted, InventoryReserved, OrderCancelled.
- "This is not a Saga yet" — the OrderCreated → Notification flow is Async Event-Driven Communication only. "Kafka ≠ Saga" and "Async Messaging ≠ Distributed Transaction". If Notification fails: order is still valid; the notification can be retried later.
- ACID in a monolith: BEGIN TRANSACTION → INSERT order / UPDATE inventory / UPDATE payment → COMMIT; if payment fails → ROLLBACK; "Everything succeeds together or everything fails together."
- Two-Phase Commit (2PC): a distributed transaction protocol coordinating one logical transaction across multiple transactional resources. Central `Transaction Coordinator`; participating systems = `Participants`. Phase 1 PREPARE: coordinator asks "Can you successfully commit this transaction?" → participants answer YES/READY or NO. Phase 2: if all YES → COMMIT to all; if one fails → ROLLBACK to all. Gives "All succeed OR All fail".
- Five 2PC problems: (1) the coordinator becomes critical — if it crashes after participants are PREPARED they do not know the final decision and resources stay locked; (2) participants hold resources while waiting — network latency, timeouts, partial failures, restarts, network partitions; (3) availability becomes coupled — if one participant is down, "Final transaction → CANNOT COMPLETE"; (4) network latency becomes part of the transaction — duration depends on network, slow participants, timeouts, retries, coordinator availability; (5) tight runtime coordination — conflicts with independent deploy/scale/fail/recover.
- 2PC is not always wrong: appropriate where "strong consistency is mandatory; all participants support compatible transactional protocols; the infrastructure is tightly controlled; reduced availability or higher coordination cost is acceptable." Better question: "Does the consistency guarantee justify the coordination, availability, and scalability cost?" Live deck conclusion: "2PC is a theoretical solution that does not work at scale" (single point of failure; all services must be UP to commit; locks held across network = slow; does not scale horizontally — "Coordination overhead grows polynomially as services are added").
- Local transactions: each service performs its own local transaction and commits its own data. If a later step fails after earlier services committed: "We cannot perform a global database rollback. Instead, we perform: Compensating Actions."
- COMPENSATE ≠ ROLLBACK (golden concept): ROLLBACK "Means it never happened. Reverts to the original state -- only possible inside a single ACID transaction." COMPENSATE "Acknowledges what happened and takes corrective action. The Payment Service does not undo the charge -- it issues a refund." Part 0.5: "A database rollback says: Pretend the transaction never happened. A compensation says: The operation happened, but another business operation corrected its effect."
- Saga definition (live deck, verbatim): "A sequence of local transactions, coordinated through events." "Each step updates its own service's database, then publishes an event to trigger the next step." If any step fails: the Saga publishes a failure event; all COMPLETED previous steps execute their compensation transaction; "The system reaches a NEW consistent state -- not the original state." "There is no global ROLLBACK." "Each service is responsible for undoing its own work if the Saga fails."
- Happy path: OrderPlaced → InventoryReserved → PaymentCompleted → OrderConfirmed. Failure path: PaymentFailed → ReleaseInventory → OrderCancelled; final state Order = CANCELLED, Inventory = AVAILABLE, Payment = FAILED.
- Eventual Consistency (Part 0.5): "In a distributed system, the entire business operation may not become consistent at exactly the same instant. Instead, the system moves through valid intermediate states until it reaches a final consistent state."
- Kafka as event transport: "Kafka is the transport mechanism. Saga is the distributed business transaction pattern." Kafka gives event transport, durable messages, producer/consumer communication, asynchronous delivery; the Saga defines "Which business step happens next; Which event represents success; Which event represents failure; Which compensation must execute." "Kafka does not automatically implement a Saga."
- Kafka capabilities used by the Saga (live deck): Durability ("Events persisted to disk -- if Inventory is down, OrderPlaced waits"), Decoupling ("Order Service doesn't know if Inventory is up -- just publishes and continues"), Replay ("A crashed consumer re-reads from the last committed offset"), Fan-out ("Multiple services can consume the same event (Notification + Inventory)").
- Topics (live deck, "WHAT WE USE IN S7"): `order-events` (Order Service publishes), `inventory-events` (Inventory Service publishes), `payment-events` (Payment Service publishes). "WHAT WE DO NOT COVER": Kafka Partitions internals, Exactly-Once Semantics, Consumer Group rebalancing, Kafka Streams, Schema Registry.
- Choreography vs Orchestration: choreography = "No central coordinator -- events drive the flow"; services only know about events (loosely coupled); debugging harder ("must trace events across services"); scalability high ("no bottleneck"). Orchestration = "Central Saga orchestrator service"; services know about the orchestrator; easier debugging ("one place to see the full flow"); lower scalability ("orchestrator can become a bottleneck"). "Today's use: We implement CHOREOGRAPHY"; "Orchestration is discussed in Session 12."
- Consumer group design — "Two Consumer Groups, One Service": `inventory-service` listens to `order-events` ("Reserve stock when a new order arrives"); `inventory-compensation` listens to `payment-events` ("Release stock when payment fails (compensation only)"). Rationale: one group for both would make "one logical consumer ... handle two unrelated jobs on the same offset stream"; separate groups isolate reservation from compensation with "independent scaling, independent failure handling". "Real bug we guard against: mixing these up makes one consumer process both events and causes duplicate or skipped compensation."
- Final platform decision (Part 0.5 section 16): we will use — Local transaction inside each service; Kafka for asynchronous event transport; Saga Pattern for the distributed business workflow; Compensation when a later business step fails; Eventual consistency across services. (One global ACID transaction and 2PC as the default are rejected.) Core rule: "Inside one service and one database: use a local ACID transaction. Across multiple independently owned service databases: coordinate the business process using a Saga."
- Order status: `createOrder()` creates the order in `PENDING` and returns immediately — "client gets PENDING, not final state".

## 3. Architecture

- Part 0 platform after this section: SYNCHRONOUS Order Service → (OpenFeign) → Inventory Service; ASYNCHRONOUS OrderCreatedEvent → Kafka → Notification Service → "Sending confirmation email...". "This is our first asynchronous communication flow."
- Part 0.5 domain layout: Order Service → Order Database; Inventory Service → Inventory Database; Payment Service → Payment Database — one local transaction per service, no shared connection.
- 2PC topology: Transaction Coordinator → Order DB / Inventory DB / Payment DB (participants); PREPARE fan-out, then COMMIT-OR-ROLLBACK fan-out.
- Saga happy path (live deck): Order Service `createOrder()` publishes `OrderPlaced`; Inventory Service `reserveStock()` [stock OK] publishes `InventoryReserved`; Payment Service `processPayment()` [OK] publishes `PaymentCompleted`; Order Service status CONFIRMED; Notification `sendConfirmation()`. "each arrow is a Kafka event. Each service handles only its own local DB transaction."
- Saga compensation path: Payment Service `processPayment()` fails → `PaymentFailed` published; Inventory Service `releaseStock()` COMPENSATION [stock released] publishes `InventoryReleased`; Order Service status CANCELLED. "No ROLLBACK. Each service executes a compensation transaction -- a new consistent state."
- Listener wiring:
  - Order Service — publishes `OrderPlaced` to `order-events`; `OrderSagaEventHandler.handlePaymentEvent` @KafkaListener(topics = "payment-events", groupId = "order-service") → PaymentCompleted → CONFIRMED; PaymentFailed → status PAYMENT_FAILED ("waiting for inventory release..."); `OrderSagaEventHandler.handleInventoryReleased` @KafkaListener(topics = "inventory-events", groupId = "order-service-cancel") → InventoryReleased → CANCELLED.
  - Inventory Service — `InventorySagaHandler.handleOrderPlaced` @KafkaListener(topics = "order-events", groupId = "inventory-service") → reserveStock → publish InventoryReserved, or on InsufficientStockException publish InventoryReservationFailed; `InventorySagaHandler.handlePaymentFailed` @KafkaListener(topics = "payment-events", groupId = "inventory-compensation") → releaseStock → publish InventoryReleased ("COMPENSATION").
  - Payment Service — `PaymentSagaHandler.handleInventoryReserved` @KafkaListener(topics = "inventory-events", groupId = "payment-service") → processPayment → PaymentCompleted or PaymentFailed ("-- triggering compensation").
- Project progress after S7: NEW — "Kafka event bus -- order/inventory/payment-events"; UPDATED — "Order, Inventory, Payment Services -- Saga handlers". "A payment failure no longer leaves the system inconsistent -- inventory is released and the order is cancelled automatically." Platform bar shows: Config+Eureka, Gateway Secured, Product Svc, Resilience Full, Feign Sync, Order Svc Saga, Kafka Running, Notif. Svc.

## 4. Technologies

- Apache Kafka — "Kafka will run as infrastructure for our microservices platform"; KRaft mode ("does not require ZooKeeper"). Docker Compose: `image: apache/kafka:latest` (KRaft env: KAFKA_NODE_ID, KAFKA_PROCESS_ROLES: broker,controller, listeners 9092/9093, replication factors 1, KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0); start `docker compose up -d kafka`; verify `docker compose ps`. Course Note (verbatim): "The exact Docker image version should be pinned in the course repository rather than using latest. The repository version is the source of truth for the lab."
- Spring for Apache Kafka: `org.springframework.kafka:spring-kafka` — "Spring Boot manages the compatible Spring Kafka version. Do not manually add a version unless the project explicitly requires one." Used via `KafkaTemplate<String, Object>`, `@KafkaListener`, `@Payload`, `@Header(KafkaHeaders.RECEIVED_TOPIC)`; serializers `StringSerializer`/`JsonSerializer`; deserializers `StringSerializer`→`StringDeserializer`/`JsonDeserializer`; `spring.json.trusted.packages`.
- Notification Service stack (Part 0): Spring Boot application from Spring Initializr, "Java: 21", artifact/name `notification-service`; dependencies "Spring for Apache Kafka", "Spring Boot Actuator"; optional "Eureka Discovery Client", "Config Client" ("The exact dependency set should remain consistent with the current platform architecture").
- Java records for all events; `BigDecimal` for money; JSON message format (event contract "Producer Contract = Consumer Contract").
- Versions stated: Java 21 (notification-service creation). Kafka Docker image is `apache/kafka:latest` but the deck says the pinned repository version is "the source of truth for the lab". Spring Boot / Spring Cloud / Spring Kafka version numbers → UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- Synchronous / Asynchronous; temporal coupling; Producer, Topic, Consumer; consumer group; offset; `auto-offset-reset: earliest`; `bootstrap-servers`.
- Command vs Event; domain event; past-tense facts; event contract; fan-out; durability; decoupling; replay.
- Business Inconsistency; ACID transaction; distributed transaction; Two-Phase Commit (2PC); Transaction Coordinator; Participants; PREPARE; COMMIT; ROLLBACK.
- Local transaction; compensating action / compensation; Saga; choreography; orchestration; Eventual Consistency.
- Topics: `order-created` (Part 0), `order-events`, `inventory-events`, `payment-events` (Saga).
- Consumer groups: `notification-service`, `order-service`, `order-service-cancel`, `inventory-service`, `inventory-compensation`, `payment-service`.
- Order statuses: PENDING, CONFIRMED, PAYMENT_FAILED, CANCELLED (compensation path); inventory "released".
- Idempotency (duplicate compensation guard); InsufficientStockException; PaymentException; `[SAGA]` log prefix.

## 6. Code concepts

- `OrderCreatedEvent` record (Part 0): `public record OrderCreatedEvent(Long orderId, Long customerId, BigDecimal totalAmount) {}`
- Producer: `OrderEventPublisher` — `KafkaTemplate<String, Object> kafkaTemplate`; `public static final String ORDER_CREATED_TOPIC = "order-created";` `kafkaTemplate.send(ORDER_CREATED_TOPIC, event.orderId().toString(), event);` + log "Published OrderCreatedEvent for order: ...". "It does not call notificationService.sendEmail(...) ... It publishes a domain fact: OrderCreated."
- Consumer (Part 0): `OrderCreatedEventListener` — `@KafkaListener(topics = "order-created", groupId = "notification-service")` `public void handle(OrderCreatedEvent event)` printing the "NOTIFICATION SERVICE / Sending order confirmation email..." block.
- Wiring the producer: `OrderService.createOrder` keeps existing S6 logic ("1. Validate request  2. Check inventory using OpenFeign  3. Create and save the order") then `eventPublisher.publishOrderCreated(event);` after save — "Order saved successfully → OrderCreatedEvent published".
- Saga Order Service: `Order order = new Order(UUID.randomUUID().toString(), request.getProductId(), request.getQuantity(), request.getAmount(), OrderStatus.PENDING); orderRepository.save(order); kafkaTemplate.send("order-events", order.getOrderId(), new OrderPlacedEvent(order.getOrderId(), request.getProductId(), request.getQuantity(), request.getAmount(), request.getCustomerId())); return new OrderResponse(order.getOrderId(), OrderStatus.PENDING, "Order received...");`
- `OrderSagaEventHandler` (two methods):
  - `handlePaymentEvent(@Payload String rawEvent, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic)` — `rawEvent.contains("PaymentCompleted")` → CONFIRMED log `[SAGA] Order {} CONFIRMED`; `rawEvent.contains("PaymentFailed")` → PAYMENT_FAILED log "waiting for inventory release...". Comment: "In production: use proper JSON deserialization with type discriminator".
  - `handleInventoryReleased(String rawEvent)` — contains "InventoryReleased" → CANCELLED log `[SAGA] Order {} CANCELLED -- inventory released`.
- `InventorySagaHandler.handleOrderPlaced(OrderPlacedEvent event)` — try `inventoryService.reserveStock(event.productId(), event.quantity(), event.orderId())` → send `InventoryReservedEvent` to `inventory-events`; catch `InsufficientStockException` → send `InventoryReservationFailedEvent(event.orderId(), e.getMessage())`.
- `InventorySagaHandler.handlePaymentFailed(String rawEvent)` (compensation) — contains "PaymentFailed" → `inventoryService.releaseStock(event.orderId())` → send `InventoryReleasedEvent`; log `[SAGA] COMPENSATION: Inventory released for order: {}`.
- `PaymentSagaHandler.handleInventoryReserved(String rawEvent)` — `if (!rawEvent.contains("InventoryReserved")) return;` → `paymentService.processPayment(event.orderId())` → send `PaymentCompletedEvent(event.orderId(), txId)`; catch `PaymentException` → send `PaymentFailedEvent(event.orderId(), e.getMessage())`; log `[SAGA] Payment FAILED for order: {}  -- triggering compensation`.
- All 8 saga event records (defined "on the board AND in code -- before any service logic"; "In production: shared library or events module. In this course: duplicated per service (shared libs discussed Session 14)"):
  - `OrderPlacedEvent(String orderId, String productId, int quantity, BigDecimal amount, String customerId)`
  - `InventoryReservedEvent(String orderId, String productId, int quantity)`
  - `InventoryReservationFailedEvent(String orderId, String reason)`
  - `PaymentCompletedEvent(String orderId, String transactionId)`
  - `PaymentFailedEvent(String orderId, String reason)`
  - `InventoryReleasedEvent(String orderId)`
  - `OrderConfirmedEvent(String orderId, String transactionId)`
  - `OrderCancelledEvent(String orderId, String reason)`
- Demo request: `curl -X POST http://localhost:8082/api/orders -d '{"productId":"PROD-001","quantity":3,...}'` → response `{ "orderId": "a1b2c3", "status": "PENDING", "message": "Order received -- processing..." }`.

## 7. Configuration

- pom.xml (each saga service, verbatim): `<dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka</artifactId></dependency>`.
- application.yml (each saga service):
  ```
  spring:
    kafka:
      bootstrap-servers: localhost:9092
      producer:
        key-serializer: ...StringSerializer
        value-serializer: ...JsonSerializer
      consumer:
        group-id: ${spring.application.name}
        key-deserializer: ...StringDeserializer
        value-deserializer: ...JsonDeserializer
        properties:
          spring.json.trusted.packages: "com.microservices.pro.*"
        auto-offset-reset: earliest
  ```
- Configuration notes (verbatim): "group-id = own consumer group per service -- each tracks its own offset"; "auto-offset-reset: earliest -- new consumers read from the beginning"; "trusted.packages required, or JSON deserializer rejects unknown classes"; "Kafka already running (Docker Compose since S1) -- no setup needed".
- Part 0 notification-service yml: `server.port: 8084`; `spring.application.name: notification-service`; `spring.kafka.consumer.group-id: notification-service`; `auto-offset-reset: earliest`; `spring.json.trusted.packages: "*"` with the production caveat: "trusted.packages: "*" is convenient for a controlled training environment. In a production system, restrict trusted packages rather than accepting every package."
- Recorded deck inconsistencies (as-is): (a) notification-service port 8084 in Part 0 conflicts with Inventory Service's port 8084 from Session 6; (b) Part 0 instructs "Add Kafka to the existing docker-compose.yml" while the live deck says "Kafka already running (Docker Compose since S1) -- no setup needed".

## 8. Failure scenarios

- Core failure the session solves: payment fails after order saved and stock reserved → compensation: PaymentFailed → release stock → order CANCELLED; "A payment failure no longer leaves the system inconsistent."
- Stock failure inside the saga: InsufficientStockException in inventory handler → `InventoryReservationFailed` published ("starts compensation").
- Notification failure (Part 0): order remains valid; notification is an independent reaction and "can be retried later".
- Coordinator crash during 2PC: participants PREPARED but nobody knows COMMIT or ROLLBACK; "resources may remain unavailable or locked".
- Participant unavailable during 2PC: order READY, inventory READY, payment UNAVAILABLE → "Final transaction → CANNOT COMPLETE".
- Common issues table (live deck, 5 rows):
  1. "Consumer never receives events" → "Check spring.kafka.consumer.group-id is unique per service. Verify auto-offset-reset: earliest."
  2. "ClassCastException deserializing events" → "Add spring.json.trusted.packages: "com.microservices.pro.*" to consumer config."
  3. "Compensation fires but stock not released" → "inventory-compensation must be a DIFFERENT consumer group from inventory-service."
  4. "Order stays PENDING indefinitely" → "Kafka consumer not running -- check startup logs. Verify topic names match exactly."
  5. "Duplicate compensation (released twice)" → "Add idempotency check: if order is already CANCELLED, skip compensation."
- Kafka durability/replay act as safety nets: if a service is down, the event waits (persisted to disk); a crashed consumer "re-reads from the last committed offset".

## 9. Trade-offs

- Sync vs async (Part 0 comparison slide): sync — caller knows receiver, waits, immediate response, temporal coupling, failure affects the current call; async — producer publishes, does not wait, consumers react independently, more temporally decoupled, multiple consumers can subscribe.
- When to choose each (the decision question + platform table, section 2). Decisions must follow communication semantics, not fashion ("Do not make the decision based on: Kafka is more modern / REST is easier").
- 2PC vs Saga (Part 0.5 comparison table, 7 rows):
  - One distributed transaction ↔ Sequence of local transactions
  - Central commit decision ↔ Business steps coordinated through events or commands
  - Participants wait for transaction outcome ↔ Services commit locally
  - Strong coordination ↔ Looser service coordination
  - Global rollback semantics ↔ Compensating actions
  - Strong consistency focus ↔ Eventual consistency
  - Infrastructure transaction protocol ↔ Business transaction pattern
- 2PC is a legitimate protocol in specific environments (strong consistency mandatory; compatible protocols; tightly controlled infrastructure; reduced availability acceptable) but "usually not the preferred default" for independently deployable, horizontally scaled, fault-isolated, event-driven microservices.
- Choreography vs orchestration (4 comparison rows, section 2) — choreography chosen today for loose coupling and high scalability; pays with harder debugging.
- Compensation vs rollback: rollback is "free" inside one ACID transaction but impossible across services; compensation is a real business operation (e.g. refund, not undo) and requires idempotency care.
- Kafka as transport (durability, replay, fan-out) vs the business logic of the Saga (which the developer must design).
- Global client experience trade-off: `POST /api/orders` returns PENDING immediately; confirmation arrives later via events (async Saga).

## 10. Common mistakes

- Treating the first Kafka example as a Saga: "This is not a Saga yet"; "Kafka ≠ Saga"; "Async Messaging ≠ Distributed Transaction".
- Trying to roll back across services: "We cannot simply leave it reserved" / no global ROLLBACK — each service compensates its own work.
- Confusing compensation with rollback semantics ("COMPENSATE ≠ ROLLBACK"; a refund is not an undo).
- Choosing communication style by preference, not semantics (see decision question).
- Using one consumer group for both inventory jobs (causes "duplicate or skipped compensation"; `inventory-compensation` must differ from `inventory-service`).
- Forgetting `spring.json.trusted.packages` (ClassCastException on deserialization) or using `"*"` in production.
- Forgetting `auto-offset-reset: earliest` / non-unique group-id (consumer never receives events); consumer not running (order stays PENDING); topic-name typos.
- Missing idempotency: "Duplicate compensation (released twice)" → skip if order already CANCELLED.
- Assuming 2PC is "always wrong" — the deck explicitly says "No. That would be an oversimplification" — but also rejecting it as the platform default (coordination/availability/scalability cost).

## 11. Interview questions

- Live deck Daily Quiz: "8 Questions -- 10 Minutes" — topics "Business Inconsistency • 2PC • Saga • Choreography • Compensation • Kafka Durability • Consumer Groups".
- Part 0 "Key Takeaways" framing questions (verbatim): OpenFeign — "How do I call another service and wait for the answer?"; Kafka — "How do I publish an event without waiting for every interested service?"; Saga — "How do I maintain business consistency when multiple independent services participate in one distributed business process?"
- Part 0.5 "Check Your Understanding" (6 questions, verbatim):
  1. "Why can the Payment Service not simply roll back the Order Database?"
  2. "Why can the Inventory Database not remain locked while waiting indefinitely for the Payment Service?"
  3. "What would 2PC require all participants to do before the final commit?"
  4. "What happens if the transaction coordinator fails during a distributed transaction?"
  5. "In a Saga, what should happen to the reserved inventory after PaymentFailed?"
  6. "Is Kafka itself the Saga, or is Kafka only the communication mechanism used by the Saga?"
- Pre-Session 8 Knowledge Check (verbatim, 3 questions — caching): "What is the difference between Cache-Aside and Write-Through caching?"; "When would you invalidate a cache entry in a microservices system?"; "What is a TTL (Time-To-Live) and what problem does it solve?"
- Questions derived from the slides: Define a Saga; why is there no global rollback; choreography vs orchestration trade-offs; why two consumer groups for Inventory; what Kafka gives a Saga (transport, durability, replay, fan-out); when is compensation triggered; what state does the customer see immediately after POST /api/orders and why.

## 12. What I must memorize

- Saga definition: "A sequence of local transactions, coordinated through events"; no global ROLLBACK; each service compensates its own work.
- COMPENSATE ≠ ROLLBACK: rollback = "it never happened"; compensation = "the operation happened, but another business operation corrected its effect" (refund example).
- Happy path: OrderPlaced → InventoryReserved → PaymentCompleted → OrderConfirmed. Failure: PaymentFailed → ReleaseInventory → OrderCancelled; final states CANCELLED / AVAILABLE / FAILED.
- Topics: `order-events`, `inventory-events`, `payment-events` (Part 0 example topic `order-created`).
- Consumer groups: order-service (payment-events), order-service-cancel (inventory-events), inventory-service (order-events), inventory-compensation (payment-events), payment-service (inventory-events).
- The 8 saga event record names and fields.
- 2PC phases: Phase 1 PREPARE (READY/YES or NO), Phase 2 COMMIT or ROLLBACK; the five problems; the "better question" quote.
- Decision question: "Does the caller need the result immediately to continue the current business operation?"; platform table (stock check sync, notification async).
- "Kafka is the transport mechanism. Saga is the distributed business transaction pattern."
- PENDING order + immediate return; `[SAGA]` log lines; commit tag `session-07: add-choreography-saga`.

## 13. What I must understand

- Why business inconsistency is a system-level state problem, not a bug/exception/network issue (every service did its job correctly).
- Why ACID cannot span services: "Each service owns its own data" — no service may touch another's database; local transactions only.
- Why 2PC is theoretically correct but operationally costly at microservices scale (coordinator criticality, held resources/locks, coupled availability, latency inside the transaction, tight runtime coordination).
- Why compensation is a NEW business operation with new semantics (refund), and why idempotency is required (duplicate compensation issue).
- Why choreography now and orchestration later (S12): loose coupling and no bottleneck vs traceability and central visibility.
- Why the two Inventory consumer groups exist — isolation of reservation from compensation on the same service.
- Why Kafka alone is not the solution: Saga logic = which step next, which event = success/failure, which compensation.
- Why the client receives PENDING immediately (the wait chain was broken by design; final state arrives via events) and what that implies for the API.
- Why "sync vs async" is a design decision per interaction, not a technology preference.

## 14. What I should implement from memory

- Add `spring-kafka` to each saga service; add the Kafka consumer/producer yml (bootstrap-servers, serializers, group-id per service, trusted packages, earliest offset).
- Define all 8 saga event records before service logic (board + code practice).
- Order Service: `createOrder()` saves PENDING order + publishes `OrderPlaced` to `order-events` + returns immediately; `OrderSagaEventHandler` with the two listeners (CONFIRMED / PAYMENT_FAILED / CANCELLED transitions).
- Inventory Service: `InventorySagaHandler` — reserve on order-events (publish InventoryReserved, or InventoryReservationFailed on InsufficientStockException) and compensate on payment-events (release + InventoryReleased, log "[SAGA] COMPENSATION").
- Payment Service: `PaymentSagaHandler` — process on inventory-events; publish PaymentCompleted or PaymentFailed.
- Part 0 first exercise: OrderCreatedEvent producer in Order Service + Notification Service consumer (log-only "email").
- Reproduce the demos: POST orders → PENDING; happy path logs; set payment failure rate to 100% → compensation logs.
- Do the mandatory paper workshop before coding (see section 17).

## 15. Relationship to previous sessions

- Builds on S6 OpenFeign directly: "We begin with order-service because it already exists from Session 6"; `createOrder` keeps S6 logic (validate, Feign inventory check, save) and adds the publish step; Session 6 sync characteristics are the contrast baseline for the async comparison.
- Builds on S5 resilience: "Resilience4j (CB/Retry) handles THIS call's failure -- but who fixes the order and the reservation that already happened?" — resilience protects a call, not a business process.
- Builds on S1–S3 infrastructure: Kafka runs via the existing Docker Compose ("since S1"); events use the existing platform (Eureka/Config optional for notification-service).
- Assumes S1–S6 recap (live deck): "Gateway secured with JWT + Rate Limiting; Order Service: full Resilience4j stack (CB, Retry, Bulkhead, TimeLimiter); Inventory Service added -- Order calls it synchronously via OpenFeign; Every call so far: Order waits, gets an answer, decides."

## 16. Relationship to future sessions

- Kafka mechanics are now in place; the deck's learning ladder: Session 6 Synchronous → OpenFeign → Session 7 Part 0 Asynchronous → Kafka Producer/Consumer → Part 0.5 distributed business problem → 2PC → Saga Pattern (local transactions + domain events + compensating actions); "Saga Choreography → Session 12 Saga Orchestration".
- Session 12: "When Choreography Becomes Complex" → Saga Orchestration ("Orchestration is discussed in Session 12 -- keep this badge in mind for that day too").
- Shared event libraries / events module discussed in Session 14 ("shared libs discussed Session 14") — today events are duplicated per service.
- Bonus homework bridges to notification: "build the bonus Notification Service -- consumes PaymentCompleted, logs 'Email sent'" (also part of the platform's future Notification service).
- Knowledge check before Session 8: caching topics — Cache-Aside vs Write-Through, cache invalidation, TTL (see section 11).
- Next session: "Session 8 -- Caching Strategies + Architecture Clinic #1", Monday, 3:00–5:30 PM, Online.

## 17. Lab relationship

- MANDATORY WORKSHOP slide: "Draw the Saga on Paper" — verbatim quote: "Do not skip or rush this. If trainees cannot draw the Saga, they cannot implement it. (10 min work + 5 min debrief)". Prompts: "1 Happy Path — Draw the event sequence from 'Order placed' to 'Order confirmed.' Label each event. Show which service publishes and which consumes."; "2 Compensation Path — What happens after PaymentFailed? Which service compensates? What does compensation look like? Final DB state of each service?"; "3 Bonus: Inventory Down — Draw what happens if Inventory Service is DOWN when OrderPlaced is published. How long does the message wait?"
- Live coding segments (no "Lab N" label): "Spring Boot Kafka Configuration" (pom + application.yml per saga service); "Define All Domain Events First"; Order Service `createOrder()` publishes OrderPlaced; Order Service listens for Saga outcomes (2 handlers); Inventory Service reserve + compensate; Payment Service process & fail.
- Demos: "Test It Live: POST /api/orders" — response `{ "orderId": "a1b2c3", "status": "PENDING", "message": "Order received -- processing..." }`; "Watch the Response: status is PENDING immediately -- not CONFIRMED"; "Watch the Log Sequence Across All 3 Services" — happy path (Inventory reserved → Payment COMPLETED → Order CONFIRMED) and compensation ("set failure rate to 100%": Payment FAILED → COMPENSATION: Inventory released → Order CANCELLED).
- Part 0 run instructions: `docker compose up -d kafka`; start Order Service + Notification Service; POST `/api/v1/orders`; expected logs — Order Service: "Published OrderCreatedEvent for order: 1001"; Notification Service: "NOTIFICATION SERVICE / Sending order confirmation email... / Order ID: 1001 / Customer ID: 501 / Total Amount: 1499.99".
- DEFINITION OF DONE — SESSION 7 (7 items, quoted): "POST /api/orders returns PENDING + orderId"; "GET /api/orders/{id}/status returns CONFIRMED (happy path)"; "Compensation: failure rate 100% → order CANCELLED"; "All 3 Kafka topics receiving events (check logs)"; "[SAGA] COMPENSATION log visible on payment failure"; "5 unit tests passing: mvn test green"; "Commit: session-07: add-choreography-saga".
- KNOWLEDGE CHECK — BEFORE SESSION 8: topic "Redis Caching Strategies" with the 3 questions quoted in section 11; "Also: build the bonus Notification Service -- consumes PaymentCompleted, logs 'Email sent'".
- Daily Quiz: "8 Questions -- 10 Minutes" (topics in section 11).
- Common Issues & Solutions: "5 Real Errors, 5 Real Fixes" (table quoted in section 8).
- The live deck's setup note conflicts with Part 0 (section 7, inconsistency b): live deck says no Docker setup is needed today; Part 0 shows adding Kafka to docker-compose.
