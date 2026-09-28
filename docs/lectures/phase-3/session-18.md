# Session 18 — CQRS Pattern (Command Query Responsibility Segregation • Read Models • Spring Data Projections • Domain Events)

Source files: `Session_18_CQRS.pdf` (25-page slide deck), `Session_18_CQRS_Pattern_Complete_Student_Tutorial.pdf` (13-page complete student tutorial). File check: the two PDFs differ in size and packaging — the deck is the instructor presentation (May 2026 delivery, "Session 18 of 29"), the tutorial is a self-contained study document. Both were read; where they differ, the difference is noted inline.

Session logistics: ONLINE SESSION — 2.5 hours, Monday 3:00–5:30 PM. Phase 3 — Advanced & Enterprise, Session 18 of 29. Instructor: Dr. ElSayed Mohamed Elsayed Baladoh. Repos: `microservices-pro-course` — `microservices-pro-platform`. Session 18 refactors **product-service — the very first service built in Session 1** — to separate Command (write) and Query (read) responsibilities.

## 1. Why this topic exists

- **One endpoint, two jobs.** product-service has grown since Session 1: it now has a Redis cache (Session 8), and Ops wants a dashboard: "show me every product, its category name, its current stock level from Inventory Service, and how many times it was ordered this week." A developer adds this logic straight into `ProductService.findAll()` — the same method the checkout page calls for a simple product lookup.
- The result: checkout — a write-adjacent, latency-sensitive path — is slowed down by a dashboard query nobody asked it to carry. "One model. Two very different customers. Every change is now a compromise for someone."
- Engineering question posed: "What would you do if a product manager asks for yet another dashboard field next month?" — it keeps piling into the same overloaded model unless something structural changes.
- The problem is **not only performance**: the same model now has two very different **reasons to change** (business rules vs screen/report requirements).
- The tutorial frames the overloaded abstraction: domain writes, simple lookups, joins, aggregations and presentation requirements all change together.
- **Honest trade-off (Instructor Pack P6):** "CQRS is not a synonym for 'good architecture.' It is a specific answer to a specific pain: read and write needs pulling a model in opposite directions." If you don't feel that pain yet, applying CQRS preemptively adds two models to keep mentally in sync plus a synchronization mechanism — for no real benefit.
- Today's refactor is justified: there IS a real, described dashboard requirement pulling against a real, described write-side invariant set. "That is the bar to clear before reaching for this pattern in your own Capstone."

## 2. Core concepts

- **CQRS = Command Query Responsibility Segregation.** Command: changes state, represents intent ("create this product", "update this price"), enforces business invariants, returns little or nothing (success/failure, an ID at most). Query: reads state, never changes anything, shaped entirely around what the caller needs to DISPLAY or DECIDE with — can be denormalized, joined, cached, or precomputed freely.
- Core insight: once one model stops serving both jobs, each side can evolve, be optimized, and be tested independently — **at the cost of an explicit synchronization mechanism between them**.
- Student rule (tutorial): COMMAND = 'Please change something.' QUERY = 'Please tell me something.'
- **CQRS does NOT automatically require two databases, Kafka, Event Sourcing or Axon.** This session uses lightweight **logical CQRS** inside one microservice and one database.
- Write Model vs Read Model: Write = enforce invariants / persist correctly; normalized JPA entity (`Product`); changes rare, driven by domain rules. Read = serve exactly what the consumer needs, fast; flattened Projection/DTO (`ProductSummaryProjection`); changes frequent, driven by UI/reporting needs.
- **Read model** = designed for the consumer: may contain only selected fields, flattened relationships, joins, or calculated values; does not need to mirror the Product entity.
- **Projection** = an interface (or DTO) that Spring Data populates directly from a query. Spring Data generates the implementation — no manual mapping code, no second physical database.
- **Domain event decoupling seam:** the command side announces a change without knowing who reacts (cache eviction today; future: materialized read model, search index, Grafana metric, integration).
- **CQRS ≠ Event Sourcing** (see §9 and §10): CQRS separates read/write responsibilities and can exist alone with one DB; Event Sourcing stores state history as durable events and uses events as the source of truth.

## 3. Architecture

- **Write side (Command):** `ProductCommandService` owns ALL writes: `create() / update() / deleteById()` — the only methods that touch the database for writes. Business invariants live HERE and ONLY here (e.g., price > 0). Publishes a `ProductChangedEvent` after every successful write. Naming discipline: no Command method joins categories, calls Inventory, or computes aggregates — "that temptation is now structurally harder to give in to."
- **Read side (Query):** `ProductQueryService` with `@Transactional(readOnly = true)` (hint to Hibernate: skip dirty-checking). Repository adds projection-returning JPQL queries: `findSummaryById`, `findAllSummaries` (join Product + Category, flattened, denormalized).
- **Event flow (the full loop):** POST/PUT/DELETE → Command Controller → `ProductCommandService` → validate → repository → commit → `ProductChangedEvent` → `ProductCacheEvictionListener` evicts `products::<id>` and `products::all` → next GET served fresh by `ProductQueryService`.
- **Request flow (tutorial):** Client → Command Controller → `ProductCommandService` → validate → repository → commit → `ProductChangedEvent`. GET: Client → Query Controller → `ProductQueryService` → projection/read model → database or cache → response.
- **Why an event at all if the DB is shared?** (deck slide 16) The event is the extension seam — where the pattern would extend to a real separate read store later (cache warm-up, search index, materialized view) without touching `ProductCommandService` again; it keeps the Command side ignorant of who cares (Open/Closed Principle). Today one listener exists (cache eviction). Tomorrow a second listener could update a Grafana metric (Session 17!) without changing a single line of the Command service.
- **URLs stay valid:** CQRS does not require different URLs — it requires separation of responsibilities. Keeping GET and POST/PUT/DELETE under the same REST resource path (`/api/products`) is perfectly valid.
- **Scope boundary (deck):** today = internal Spring events (same JVM) — `ApplicationEventPublisher` + listener stay entirely inside product-service, no network hop, no serialization, no broker. Cross-service Kafka domain events were already built in Session 7 (Choreography Saga) and Session 12 (Orchestration Saga) — this session does not repeat that work.
- The tutorial adds: "The command side knows about the domain change, not the cache implementation" — cache concerns stay out of `ProductCommandService`.

## 4. Technologies

- **Spring Boot / Spring Framework** — `@Service`, `@Transactional`, `@Transactional(readOnly = true)`, `ApplicationEventPublisher`, event listeners.
- **Spring Data JPA** — `JpaRepository`, `@Query` JPQL, interface-based projections (alias-to-getter mapping).
- **Spring events** — `@EventListener` (deck) vs `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)` (tutorial); `@Async` discussed only as an option (with `@EnableAsync`); "async is not durability".
- **Hibernate** — dirty-checking skipped via readOnly.
- **PostgreSQL** — same single database shared by write and read models (logical CQRS). Explicitly NOT a separate read database.
- **Redis cache (from Session 8)** — cache invalidation now triggered by event listener instead of direct `@CacheEvict`; CacheManager eviction of product key + 'all' list key.
- **Mockito** — `@ExtendWith(MockitoExtension.class)`, `@Mock ProductRepository`, `@Mock ApplicationEventPublisher`, `@InjectMocks`.
- **Axon Framework** — explicitly OUT of scope ("evaluate it independently once you understand the pattern it automates"). **Event Sourcing** — explicitly OUT of scope (separate, heavier pattern that often pairs with CQRS but is NOT required by it).
- No version numbers for any tool are given in either S18 PDF.

## 5. Important terminology

- Command — changes state, expresses intent, enforces business rules, transactional write, returns minimal acknowledgement/ID at most; create/update/delete.
- Query — reads state, answers a question, no business mutations, read-only transaction; find/list/search/report.
- Write Model / Command side — normalized JPA entity, invariants, correctness first.
- Read Model / Query side — flattened projection/DTO, denormalized, UI/report driven, read efficiency first.
- Projection — interface or DTO populated by Spring Data from a query; interface projection = minimal mapping code + getter aliases important; DTO/record projection = explicit response construction, explicit constructor fields, useful for deliberate API/read structures.
- Logical CQRS — separation of responsibilities within one microservice and one database (today's design); physical separation is "logical first and physical later only when justified".
- `ProductChangedEvent` — domain event announcing a product wrote/updated/deleted; ChangeType `CREATED, UPDATED, DELETED`.
- `ProductSummaryProjection` — read model: id, name, price, categoryName (flattened — write-side has categoryId only); `getDisplayLabel()` default method = read-side-only convenience.
- AFTER_COMMIT — the safe moment for post-write side effects; a normal listener may execute before the surrounding transaction commits, so a rollback would leave the listener having already done cache/external work.
- Extension seam — the placeholder where a separate read store / search index / metric listener plugs in later without touching the command service.
- `InvalidProductException` ("Price must be positive") — invariant owned by the command side.
- Stale data — cache entries invalidated only after successful writes (evict individual product key AND 'all' list key).
- Event Sourcing — durable state history as events; a different pattern, not required by CQRS.
- Dashboard field — the motivating reporting requirement; changing it must not force changes to the write entity.

## 6. Code concepts

- **`ProductCommandService`** (deck version): `@Service` with `ProductRepository` + `ApplicationEventPublisher`; `@Transactional create(CreateProductRequest)` — validates `price > 0` (throws `InvalidProductException`, comment: "invariant lives HERE only"), saves, publishes `new ProductChangedEvent(saved.getId(), "CREATED")`; `@Transactional update(Product)` — saves + publishes "UPDATED"; `@Transactional deleteById(Long id)` — deletes + publishes "DELETED".
- **`ProductCommandService`** (tutorial version): records `CreateProductRequest(name, description, price, categoryId)` / `UpdateProductRequest(...)`; `create()` returns the new `Long` id; `update(Long id, ...)` loads the entity first (`findById(...).orElseThrow(ProductNotFoundException)`) then sets fields — "The command is changing an existing aggregate. Loading the current state creates a clear place to enforce rules and avoids blindly saving an external detached entity"; `deleteById` checks `existsById` first; private `validatePrice` (null or <= 0 → `InvalidProductException("Price must be positive")`); event carries `ChangeType` enum instead of String.
- **`ProductSummaryProjection`** (interface): `Long getId(); String getName(); BigDecimal getPrice(); String getCategoryName();` + `default String getDisplayLabel() { return getName() + " (" + getCategoryName() + ")"; }`.
- **Repository JPQL:** `@Query("SELECT p.id AS id, p.name AS name, p.price AS price, c.name AS categoryName FROM Product p JOIN Category c ON p.categoryId = c.id WHERE p.id = :id") Optional<ProductSummaryProjection> findSummaryById(@Param("id") Long id);` and the same without WHERE returning `List<ProductSummaryProjection> findAllSummaries();`. Spring Data maps query aliases to projection getters — alias `categoryName` ↔ `getCategoryName()`. JPQL uses entity and Java field names, not table/column names.
- **DTO alternative (tutorial):** `record ProductSummaryResponse(Long id, String name, BigDecimal price, String categoryName) { public String displayLabel() {...} }`. Comparison: interface projection = minimal mapping code, getter aliases important, convenient for simple repository reads; DTO/record = explicit construction, useful for deliberate API/read structures.
- **`ProductQueryService`:** `@Service @RequiredArgsConstructor @Transactional(readOnly = true)` (tutorial puts it on the class; deck puts it per-method) with `findById` (throws `ProductNotFoundException` if empty) and `findAll`. "readOnly = true expresses query intent and can enable persistence-provider read optimizations. It is useful, but it is not a substitute for designing a method as a genuine query."
- **Command controller:** `@RestController @RequestMapping("/api/products")` — POST → 201 CREATED returning `Map.of("id", ...)`; PUT → 204 NO_CONTENT; DELETE → 204 NO_CONTENT.
- **Query controller:** `@GetMapping("/{id}")` → `ProductSummaryProjection`; `@GetMapping` → `List<ProductSummaryProjection>`.
- **`ProductCacheEvictionListener`:** `@Component` with `CacheManager`; deck uses `@EventListener onProductChanged(ProductChangedEvent)` evicting both `products` cache entries (`event.productId()` and `"all"`), with an explicit NOTE: "@EventListener here runs SYNCHRONOUSLY on the same thread as the Command by default. Add @Async (with @EnableAsync) only if the listener does slow work." Tutorial uses `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)` with the same eviction logic — DISCREPANCY between deck and tutorial: post-commit guarantee vs default-sync listener; the tutorial explicitly warns "a normal event listener may execute before the surrounding transaction has successfully committed. If the transaction rolls back, a listener may already have performed cache or external work."
- **Sync vs async listeners (tutorial table):** synchronous default = simple in-process work, easy failure reasoning, good for small local actions, not durable messaging; asynchronous = other thread/executor, needs executor/error-handling design, useful for slow non-critical work, still not durable messaging. "Do not add @Async simply because an event exists. Asynchronous execution and reliable distributed delivery are different concerns."
- **Mockito test example (tutorial):** `@ExtendWith(MockitoExtension.class)`, `@Mock ProductRepository`, `@Mock ApplicationEventPublisher`, `@InjectMocks ProductCommandService`; `create_shouldRejectNonPositivePrice()` asserts `InvalidProductException` thrown and `verifyNoInteractions(productRepository)`.
- **Suggested package structure (tutorial):** `com.example.productservice` → `command` (incl. `dto`), `query` (`ProductQueryService`, `ProductSummaryProjection`, `ProductSummaryResponse`), `event` (`ProductChangedEvent`), plus `controller`, `domain`, `repository`.

## 7. Configuration

- No new application.yml/properties content is shown in the S18 deck for this refactor; the working settings inherited from earlier sessions apply (product-service on port 8081, Redis cache "products" from Session 8).
- `@Transactional` on every command method; `@Transactional(readOnly = true)` on query methods (placement is a known pitfall — must be on the query service method itself, not only on the repository interface).
- Event listener wiring: `@EventListener` (deck) or `@TransactionalEventListener(phase = AFTER_COMMIT)` (tutorial); `@Async` only with `@EnableAsync` and only for slow listener work.
- Invariant: price must be positive — enforced in one place, the command service.
- Cache keys involved: `products::<productId>` and `products::all` — both must be evicted after a write.
- Injected collaborators: `ProductRepository`, `ApplicationEventPublisher`, `CacheManager` — all Spring-managed beans.
- EXACT YAML/property additions for Session 18: not shown in the slides.

## 8. Failure scenarios

The deck's "5 Things That Will Go Wrong Today" + tutorial troubleshooting:

- **Query endpoint returns stale data after a Command** → evict BOTH the individual product key AND the 'all products' list key — same lesson as Session 8, Q4.
- **Event listener never fires** → confirm `eventPublisher.publishEvent()` is actually called, and the listener is a discovered `@Component`.
- **Projection query returns null for `categoryName`** → check the JPQL `@Query` join condition — a typo in the join column silently returns null; also check query alias vs getter name.
- **Unit test fails with NullPointerException on `eventPublisher`** → `@Mock ApplicationEventPublisher` must be included alongside `@Mock ProductRepository`.
- **`@Transactional(readOnly=true)` still shows dirty-checking overhead** → verify the annotation is on the `ProductQueryService` method itself, not only the repository interface.
- Tutorial's common mistakes table: separate databases immediately (start logical instead); returning JPA entities everywhere (use minimal command responses and read models); validating business rules in queries (keep invariants on the command side); adding reporting fields to the Product entity (use a projection/DTO); evicting cache directly from every command (use a decoupled post-commit listener); using in-process events as durable messaging (use a proper broker/outbox design when reliability is required); assuming `@Async` makes delivery reliable ("Async is not durability"); projection field null (check alias/getter); JPQL fails (use entity/Java field names).
- **Rollback hazard (tutorial):** a plain `@EventListener` can perform cache/external work before commit; if the transaction rolls back, the eviction already happened (safe-ish) but external side effects may be wrong — use AFTER_COMMIT for post-commit invalidation.

## 9. Trade-offs

- **How far to go? Decision ladder:** Skip CQRS (no separation — simple CRUD, single model OK) → Projection/DTO (a read needs selected fields/joins/another shape) → CQRS — separate read model (today's build; write invariants and read requirements pull the model apart) → CQRS + Event (read-heavy with complex queries) → CQRS + Event Sourcing (future pattern; read/write scale independently or need different storage; audit trail; state history as durable source of truth). Also: "Team new to the codebase?" → start without CQRS.
- **Costs of CQRS (P6):** two models to keep mentally in sync + a synchronization mechanism to maintain — justified only against a real read/write conflict.
- **Logical vs physical:** one shared PostgreSQL DB today — no synchronization lag at data level, no distributed consistency problem; a separate read store is deferred "until justified" (physical separation later only when justified).
- **Event seam trade-off:** an event is not needed to move data today — it exists for decoupling and future extension (search index, materialized view, metrics); the listener still couples to the CacheManager, but the command service is clean.
- **Sync vs async listeners:** sync = easy reasoning, blocks command thread; async = non-blocking but needs executor/error-handling design and is still not durable messaging.
- **Interface projection vs DTO:** minimal mapping code vs explicit, deliberate read structure.
- **CQRS vs Event Sourcing:** CQRS separates responsibilities, doesn't require events, works with normal relational persistence and one database, can exist alone. Event Sourcing stores state history as durable events (events = source of truth), requires reconstruction/projections, often needs specialized infrastructure; it often pairs well with CQRS but is independent. "CQRS asks: Should reads and writes use different responsibilities/models? Event Sourcing asks: How is domain state and its history stored?"
- Assessment weighting itself as a quality trade-off (tutorial): Feature correctness 70% / Tests 20% / Code quality and CQRS separation 10%.

## 10. Common mistakes

- Placing dashboard logic (joins, Inventory calls, order counts, aggregations, presentation fields) inside the shared `ProductService.findAll()` — one model, two customers, every change a compromise.
- Applying CQRS preemptively without a felt read/write conflict — "CQRS is not a synonym for 'good architecture'." Use the smallest design that solves the real problem.
- Jumping to a physically separate read database or Event Sourcing/Axon when the pattern alone is the lesson.
- Putting invariants anywhere other than the command side; validating business rules in queries.
- Returning JPA entities everywhere instead of read models; adding reporting fields to the write entity.
- Publishing events but forgetting the listener is a `@Component` (or never calling `publishEvent`) — listener silently never fires.
- Evicting only the individual product key and forgetting the 'all' list key — stale list responses.
- Calling the cache directly from `ProductCommandService` (direct `@CacheEvict`) instead of an event-driven listener — defeats the decoupling.
- Not using AFTER_COMMIT semantics for post-write side effects (tutorial) while assuming the default listener timing is safe.
- Treating in-process events / `@Async` as durable messaging.
- Misplacing `@Transactional(readOnly = true)` (repository interface instead of the query service method); JPQL alias/getter mismatches; JPQL using table/column names instead of entity/Java field names.
- Forgetting `@Mock ApplicationEventPublisher` in tests → NPE.

## 11. Interview questions

- What does CQRS stand for and what problem does it solve? ("Command Query Responsibility Segregation"; a specific answer to the pain of read and write needs pulling a model in opposite directions.)
- Must CQRS use two databases? (No — logical CQRS can use one database; today's Read Model shares the same PostgreSQL database.)
- What does a command do vs what does a query do? (Command: expresses intent, validates rules, changes state, returns minimal acknowledgement/ID. Query: returns information without changing business state, shaped for the consumer.)
- Why use a projection instead of returning the entity? (To shape read data/joins/flattened fields without polluting the write entity; Spring Data generates the implementation; no manual mapping, no second database.)
- Why use `@Transactional(readOnly = true)`? (Expresses query intent, hints Hibernate to skip dirty-checking; real performance gain on the read path — but not a substitute for designing a genuine query.)
- Why publish an event when both sides share one database? (Extension seam + Open/Closed: decouples the command side from who reacts — cache today, metrics/search index/materialized view later — without touching the command service.)
- Why use AFTER_COMMIT for cache eviction? (To avoid reacting to a change that later rolls back.)
- Is CQRS the same as Event Sourcing? (No — different patterns, different questions; neither automatically requires the other.)
- When should CQRS be avoided? (When the read/write conflict does not justify the added complexity — small CRUD service, pattern added because it sounds advanced, simple DTO/projection already solves the read problem.)
- How do you decide how far to go? (Ladder: no separation → projection/DTO → logical CQRS → CQRS+Event → CQRS+Event Sourcing; pick the smallest that solves the real problem.)
- Is `@Async` the same as reliable messaging? (No — "async is not durability".)

## 12. What I must memorize

- Command vs Query definition and the student rule: COMMAND = 'Please change something.' QUERY = 'Please tell me something.'
- CQRS does NOT automatically require two databases, Kafka, Event Sourcing or Axon — today is logical CQRS, one database.
- The five core rules: a command changes state, a query does not change business state; commands own business invariants; queries are shaped around consumer needs; read models do not have to mirror JPA entities; separation can be logical first and physical later only when justified.
- "CQRS is not a synonym for good architecture" — apply the smallest design that solves the real problem.
- Write invariants (price > 0) live ONLY in the Command side.
- Read model shape: `ProductSummaryProjection(id, name, price, categoryName)` + `getDisplayLabel()` default method; aliases in JPQL map to getter names.
- After a write, evict BOTH the product key and the 'all' key; tutorial: do it AFTER_COMMIT.
- CQRS ≠ Event Sourcing (two different questions).
- CQRS does not require different URLs — same REST resource path is valid.
- `@Transactional(readOnly = true)` belongs on the query service method; it hints Hibernate to skip dirty-checking.
- The decision ladder: Skip CQRS → Projection/DTO → CQRS (separate read model) → CQRS + Event → CQRS + Event Sourcing.
- Lab 14 essentials: writes+publish; projection+query service; event-driven eviction; minimum 2 unit tests (invalid price rejected, event published on create).

## 13. What I must understand

- Why one model/two jobs is a structural problem (two reasons to change), not just a performance problem.
- Why CQRS here is a **logical** split: the pain is model conflict, not storage scale — a separate read database is deliberately deferred.
- The difference between a projection (a read shape derived from a query) and a second physical database (a distributed synchronization problem) — CQRS proper is about responsibility separation, not storage duplication.
- Why the event exists even with a shared DB: extension seam + Open/Closed Principle — tomorrow a Grafana metric listener (Session 17) can be added without touching the command service.
- Why invariants stay exclusively on the command side ("The Query side never sees invalid data, and never has to know about validation rules at all").
- Why the listener must be post-commit (AFTER_COMMIT) and why `@Async` ≠ durability.
- How Spring Data generates the `ProductSummaryProjection` implementation from the `@Query` — no manual mapping code, no second database.
- Where the internal-event scope boundary is: today in-JVM events; cross-service Kafka events belong to Sessions 7/12, not repeated here.
- The tutorial's why-load-before-update reasoning (existing aggregate; no blindly saved detached entity).
- How to make the judgment call: when a DTO/projection alone is sufficient vs when CQRS earns its complexity.

## 14. What I should implement from memory

- `ProductCommandService` — `create` / `update(Long id, ...)` / `deleteById` (all `@Transactional`), invariant validation (price > 0 → `InvalidProductException`), publish `ProductChangedEvent` after each successful write; command controller: POST 201 with id, PUT/DELETE 204.
- `CreateProductRequest` / `UpdateProductRequest` records; `ProductChangedEvent` (productId + ChangeType CREATED/UPDATED/DELETED, or String in deck form).
- `ProductSummaryProjection` interface with the four getters + `getDisplayLabel()` default method; `ProductSummaryResponse` record alternative with `displayLabel()`.
- Repository JPQL with aliases: `findSummaryById`, `findAllSummaries` (JOIN Category ON `p.categoryId = c.id`).
- `ProductQueryService` with `@Transactional(readOnly = true)`: `findById` (throw when missing), `findAll`; query controller with GET endpoints returning projections on the same URLs.
- `ProductCacheEvictionListener`: after commit, evict productId + "all" from the "products" cache via `CacheManager`; replace direct `@CacheEvict` in the old service.
- Unit tests: positive/zero/negative price, missing product update fails, delete succeeds, correct change event published — with `@Mock ApplicationEventPublisher`; query-side tests (no save/delete calls; alias mapping).
- Integration test flow: create → query projection → update → verify commit + cache eviction → query fresh → delete → verify query behavior.
- Demonstrate: dashboard field change without touching the write entity; invalid price → 400; update → cache eviction log via event.

## 15. Relationship to previous sessions

- **Session 1:** product-service — "the very first service you built" — is the refactor target; builds on its entity/repository.
- **Session 3:** (security context) forward reference — Session 18 leads into Security in Session 19 (slots S19/S20 in the roadmap from this deck).
- **Session 7 (Choreography Saga) and Session 12 (Orchestration Saga):** cross-service Kafka domain events were already built there — this session keeps events in-JVM and does not repeat broker work.
- **Session 8:** the Redis cache is connected back to CQRS — `ProductCacheEvictionListener` replaces direct `@CacheEvict`; "same lesson as Session 8, Q4" (evict both product and list keys).
- **Session 12:** same discipline — "In Session 12 we built Saga Orchestration in plain Spring Boot — no Axon Framework — because the goal was to teach you the PATTERN so you could evaluate any framework independently afterward." CQRS is implemented the same way: pattern, not framework.
- **Session 17:** a second listener could update a Grafana metric (Session 17!) without changing a single line of the Command service — the observability work slots directly into this extension seam.
- **Next session (deck, slide 24):** Session 19 — Security Part 1, Wednesday 3:00–5:30 PM, Online.

## 16. Relationship to future sessions

- **Phase 3 roadmap (deck slide 2):** S19 Security Pt.1 → S20 Security Pt.2 → S21 Service Mesh → S22 Adv. Patterns → S23 Performance → S24 Arch Clinic #2.
- A physically separate read store / search index / materialized view is the natural future extension of today's seam ("cache warm-up, search index, materialized view") — deliberately not built today.
- **CQRS + Event Sourcing** is listed in the decision ladder as a future pattern; Event Sourcing remains intentionally out of scope for this session (tutorial: "Event Sourcing remains intentionally out of scope for this session").
- The Capstone: "Document one justified CQRS case and one unjustified case" (homework) — the pattern is to be applied selectively in Phase 4.
- Platform progress tracker (8 segments): Config+Eureka, Gateway, Resilience, Feign+Saga, K8s Pipeline, Observability, **CQRS (Product) — NEW**, Security.
- The refactor leaves product-service with an explicit command side, a read-optimized query side, decoupled Redis invalidation, and "a seam for future read-store evolution."

## 17. Lab relationship

Exact lab/quiz/homework/assessment content as stated in the slides:

- **LAB 14 — Command/Query Split on product-service** (deck slide 20): product-service — builds on Session 1 entity/repository and Session 8 Redis caching — **25 min**. 4 tasks: (1) `ProductCommandService` — move all write logic + invariant checks here; publish `ProductChangedEvent`. (2) `ProductSummaryProjection` + `ProductQueryService` — `@Transactional(readOnly=true)`, returns the flattened Projection. (3) Event-Driven Cache Eviction — replace direct `@CacheEvict` with `ProductCacheEvictionListener`. (4) Unit Tests — minimum 2 tests: invalid price rejected, event published on create.
- **Hands-on Lab (tutorial, 9 steps):** Goal — refactor product-service into lightweight CQRS without introducing a second database: create `ProductCommandService` for all writes; `ProductQueryService` for all reads; `ProductSummaryProjection` with id, name, price, category name; add projection repository queries; create separate create/update request DTOs; publish `ProductChangedEvent` after writes; evict Redis product cache after successful commit; write command and query tests; demonstrate that a dashboard field can change without changing the write entity.
- **Acceptance criteria (tutorial, 7):** no query changes product state; no command performs dashboard aggregation; read endpoints return projections/read DTOs; write endpoints validate invariants; stale cache entries are invalidated after successful writes; tests pass; the student can explain why a separate database is not required today.
- **Live coding checklist (tutorial, 12 items):** create command/query packages; create request DTOs; create `ProductChangedEvent`; move create/update/delete to `ProductCommandService`; keep validation on the command side; create `ProductSummaryProjection`; add projection repository queries; create `ProductQueryService`; create command/query controllers; add AFTER_COMMIT cache listener; run unit tests; demonstrate create → query → update → cache eviction → query.
- **Demos (deck):** invalid price via curl → 400 Bad Request `InvalidProductException 'Price must be positive'`; valid create → 201 Created + log `[CQRS] ProductChangedEvent published: productId=42, changeType=CREATED`; GET `/api/v1/products/42` returns flattened `categoryName` from the JOIN; full loop demo — call the Command then immediately call the Query endpoint and show the Redis cache log line confirms eviction happened via the event, "not because ProductCommandService called the cache directly."
- **Daily Quiz (deck):** 8 Questions — 10 Minutes — Google Forms or Kahoot. Topics: Command vs Query, Projections, readOnly=true, When NOT to use CQRS. Tutorial quiz: 8 Q&A (what CQRS stands for; two databases?; command/query roles; why a projection; why AFTER_COMMIT; CQRS vs Event Sourcing; when to avoid).
- **Homework (tutorial, 5 items):** add one display-oriented field to the read projection; add product search by name using a read-side projection/DTO; test that invalid prices are rejected; create an integration test for create → query → update → cache eviction → query; document one justified CQRS case and one unjustified case in the capstone.
- **Assessment (tutorial):** Feature correctness 70% / Tests 20% / Code quality and CQRS separation 10%.
- **Session completion checklist (tutorial, 9 items):** distinguish command/query; identify read/write model conflict; know when a projection alone is sufficient; implement command and query services; create interface and DTO projections; understand post-commit event handling; decouple cache invalidation from command logic; explain CQRS vs Event Sourcing; know CQRS is a design choice, not a default requirement.
- **Checkpoint commits in slides:** not shown in either S18 PDF.
