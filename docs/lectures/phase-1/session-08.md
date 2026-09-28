# Session 8 — Caching Strategies (Redis · Cache-Aside · @Cacheable · Architecture Clinic #1)

Source files: Session_08_Caching_ArchClinic1.pdf; Session_08_Spring Boot Caching with Redis.pdf

Coverage map (two decks, one note — two clearly separate parts):
- Session_08_Caching_ArchClinic1.pdf — the live-session deck ("Session 8 of 29 (FINAL)"): Phase-1 transition point, database-read bottleneck problem, caching decision framework, Cache-Aside pattern and invalidation, caching candidates, live coding in Product Service, demo, then "ARCHITECTURE CLINIC #1" (Q1–Q5 with expected answers and red flags), clinic debrief, technical debt checkpoint (8 items), Phase 1 completion, DoD, Session 9 prep, common issues. In this note its content is tagged "(ArchClinic1/main deck)".
- Session_08_Spring Boot Caching with Redis.pdf — the seminar/tutorial deck ("Spring Boot & Spring Cloud • Professional Edition — Spring Boot Caching with Redis — Complete Guide to Caching Strategies in Microservices", 12 sections): introduction to caching, cache layers (CPU / application / Hibernate L1–L2 / Spring Cache), local vs distributed caching, cache technologies compared (HashMap / Caffeine / EhCache / Hazelcast / Redis), caching patterns (Cache-Aside / Read-Through / Write-Through / Write-Behind), Spring Cache abstraction, implementing @Cacheable (attributes incl. condition/unless/sync), cache invalidation strategies, advanced Redis configuration (per-cache TTL, serialization, redis-cli, production), live coding workshop phases 1–8, common pitfalls, quick reference with Interview Questions Q1–Q8 and a final checklist. In this note its content is tagged "(seminar deck/Redis seminar)".

Deck identity (live deck): "MICROSERVICES COURSE • PHASE 1 • SESSION 8 OF 29 (FINAL) — Caching Strategies — Redis • Cache-Aside • @Cacheable • Architecture Clinic #1", Dr. ElSayed Mohamed Elsayed Baladoh, Monday, 2.5 Hours – Online, "Phase 1 -- Final Session". Slide: "Today is the last session of Phase 1 -- and it's different. We don't add a feature. We make the platform faster, then turn around and review every decision we've made since Session 1."

## 1. Why this topic exists

- Performance problem (main deck): "Database Reads Become a Bottleneck at Scale." WITHOUT CACHE: GET /api/products/1 → Product Service → `SELECT * FROM products WHERE id=1` → "PostgreSQL responds in 50ms"; "At 1000 requests/minute: 1000 queries/min hit the database directly"; "PostgreSQL CPU climbs to 90%"; "Every single request pays the full 50ms". WITH CACHE-ASIDE (REDIS): "GET product:1 from Redis (1ms)"; "At 1000 requests/minute: 999 hits (1ms each), 1 miss (first time only)"; "PostgreSQL CPU stays under 5%"; "Response time: 1ms on a cache hit".
- Phase transition (main deck): Sessions 1–7 "Every session added a feature... Every session ended with something new working." Session 8 asks: "Is our system fast enough? Did we make the right architectural decisions?" — "No new service. No new annotation type."
- Architecture Clinic purpose: "Be the Harshest Critic of Your Own Work. Imagine you're a senior engineer reviewing a colleague's code for the first time -- you are not here to praise it, you're here to make it better." A lazy answer: "It works, so it's fine." A good answer: "It works, but if I were to do it again, I would..." An excellent answer: "I see a specific risk in this design: ..."
- Seminar framing: "A cache is a temporary storage that keeps frequently accessed data in fast memory. Instead of computing or loading data repeatedly, a cache stores the result so it can be retrieved quickly." "Key Insight: Caching trades memory for speed." Scenario: Product Service receives 100,000 requests/hour; "The database does unnecessary work answering the same queries repeatedly." "Caching is a design technique, not a technology. Redis is a technology that implements caching. Spring Cache is an abstraction over caching technologies."
- Why caches work — access time table (seminar): CPU Cache < 1 ns; RAM 50–100 ns; SSD 50–150 µs; HDD 5–100 ms; Network 50–1000 ms. "The farther data is from the CPU, the slower it becomes. Caching brings data closer."

## 2. Core concepts

Caching core (main deck):
- Decision framework — 3 questions: (1) "Is this data read much more than it's written?" (Products read 10,000x/day, updated 2x/day → GOOD candidate; "Order status changes constantly → BAD candidate"). (2) "Is occasional stale data acceptable?" (Product name/price: a short window is OK with short TTL; "Account balance: must be current → do not cache"). (3) "Is the cost of a cache miss acceptable?" ("Simple product lookup: DB query is cheap → fine either way"; "Complex 10-table join report (500ms) → definitely cache").
- Cache-Aside flow: check Redis `GET product:{id}` → CACHE HIT → "Return cached value (1ms)"; CACHE MISS → "Query PostgreSQL: SELECT * FROM products WHERE id=? (50ms)" → "Store in Redis: SET product:{id} {value} EX {ttl}" → return (50ms this time; "subsequent calls: 1ms"). Invalidation: "when product is UPDATED or DELETED → DELETE product:{id} from Redis (@CacheEvict)"; "Next GET will be a CACHE MISS → reads fresh data from DB". "Cache Invalidation -- the hard part."
- Caching candidates — GOOD: "Product catalogue -- names, descriptions, categories"; "Pricing -- with a short TTL (5 min)"; "Configuration data -- rarely changes, read constantly"; "Expensive computed reports -- aggregate calculations". NEVER CACHE: "Order status -- changes on every Saga step"; "Payment information -- must be real-time accurate"; "Inventory stock levels -- customer might order out-of-stock"; "Authentication tokens -- stale tokens are a security risk".
- Invalidation strategy (main deck): "@CacheEvict on every write operation -- this is your PRIMARY invalidation strategy"; "TTL (Time-to-Live) -- automatic expiry after N seconds -- use as a SAFETY NET (e.g. 5–10 minutes) -- even if a write path is missed, stale data eventually expires". "COMBINED STRATEGY, EVERY TIME: @CacheEvict on every write + TTL as safety net (e.g. 10 minutes). Never rely on TTL alone -- 'it'll expire eventually' is not a consistency guarantee for anything that matters." Quote: "There are only two hard things in Computer Science: cache invalidation and naming things." -- Phil Karlton.
- Two annotations, two jobs: @Cacheable "On a READ method. Checks Redis first. On a hit, returns immediately. On a miss, runs the method and stores the result."; @CacheEvict "On a WRITE method. Removes a key from Redis so the next read is forced to go back to the database." "findById() and findAll() get @Cacheable -- they're reads; update() and deleteById() get @CacheEvict -- they're writes that must invalidate stale data." "One more rule: evicting the single-product cache is not enough -- the all-products LIST cache must be evicted too."
- @EnableCaching (main deck): "REQUIRED -- activates the Spring Cache abstraction." "Without @EnableCaching, every @Cacheable and @CacheEvict annotation is silently ignored -- the method always executes, Redis is never checked."

Caching layers (seminar deck):
- Layer 1 CPU Cache (tiny memory inside the processor; "Who manages: Operating system and hardware (automatic)"). Layer 2 Application Cache (HashMap, Caffeine, EhCache; "Store objects in memory instead of querying databases"). Layer 3 Hibernate First-Level Cache (L1) — "Built-in cache in every EntityManager", "Scope: Single transaction only", "Auto-enabled: Yes"; `entityManager.find(...)` twice in one transaction = one query. Layer 4 Hibernate Second-Level Cache (L2) — "survives beyond one transaction"; providers EhCache, Infinispan, Hazelcast; "Why less common in Microservices: Multiple pods would have inconsistent caches; Synchronization becomes difficult." Layer 5 Spring Cache — "Abstraction layer for caching... Not: An actual cache implementation."
- Local vs distributed (seminar): local = "Cache stored inside the application's own memory (JVM Heap)" — extremely fast, no network call, simple; but "Cache disappears if application restarts", "Every application instance has its own copy", "Difficult to keep multiple instances synchronized". Distributed = "Cache stored in a dedicated cache server shared by all instances" — shared, "Consistent across pods", "Works perfectly with Kubernetes", "Independent of application lifecycle"; costs "Small network latency", "Extra infrastructure", "Requires monitoring". Comparison table: Storage JVM Memory vs External Server; Network Call No vs Yes; Speed Extremely Fast vs Very Fast; Shared No vs Yes; Kubernetes Ready No vs Yes.

Caching patterns (seminar deck):
- "A cache is only a storage mechanism. The more important question is: How does an application interact with that cache?"
- Pattern 1 — Cache-Aside (Lazy Loading), "The most popular caching strategy": the application reads from cache and updates the cache; "The cache itself is passive"; step-by-step first request (NOT FOUND → DB query → store `products::1` → return) and second request (FOUND → return; "Database is never contacted"); "Why 'Lazy Loading'? Data is not cached until someone requests it. No request → No cache." Advantages: very simple, excellent read performance, "Only caches data that is actually used", supported directly by Spring Cache. Disadvantages: "First request is slower", "Application must remember to invalidate cache", "Cache consistency is the application's responsibility".
- Pattern 2 — Read-Through: "Application never queries the database directly. It asks the cache, which loads missing data." "Why Not Used in Spring Boot? Redis doesn't know your repositories, entities, or business logic."
- Pattern 3 — Write-Through: "Every write goes to cache first, then immediately to database"; advantage "Cache always contains latest data"; disadvantages "Every write becomes slower", "Write latency increases"; usage: financial systems.
- Pattern 4 — Write-Behind (Write-Back): "Application writes only to cache. Database updates happen later in background"; "Very fast writes"; "Risk of losing data before it reaches database"; more complex; usage: analytics, logging, metrics, IoT.
- Pattern comparison table: Cache-Aside (Excellent / Normal / Low / Most Common); Read-Through (Excellent / Normal / Medium / Rare); Write-Through (Excellent / Slower / Medium / Rare); Write-Behind (Excellent / Very Fast / High / Specialized). "In this course, we use Cache-Aside exclusively."

Spring Cache abstraction (seminar deck):
- "Important: Your service never communicates directly with Redis. It communicates with Spring Cache, which decides which cache implementation to use." Analogies: "Spring Data JPA → Hibernate; SLF4J → Logback; Spring Cache → Redis/Caffeine/EhCache."
- Annotations: @Cacheable ("Read from cache or store result"), @CacheEvict ("Remove cache entries"), @CachePut ("Update cache without skipping method"), @Caching ("Combine multiple cache operations"), @CacheConfig ("Define common cache configuration").
- Why not RedisTemplate everywhere: doing it manually means handling "Key generation, Serialization, Cache lookup, Cache insertion, Cache eviction, TTL handling" — "For 90% of business applications, Spring Cache is cleaner, safer, and easier to maintain." Use RedisTemplate only for Redis-specific capabilities: custom data structures, counters, distributed locks, Pub/Sub, Streams, Lua scripts, Transactions.

@Cacheable attributes (seminar deck):
- Key basics: `@Cacheable("products")` ≡ `@Cacheable(cacheNames = "products")`; Redis keys like `products::1`; "The cache name acts like a namespace"; multiple caches `@Cacheable({"products", "catalog"})`; default key = method parameter; `key = "#id"` (SpEL — "The # symbol means 'method parameter'"); multiple params `key = "#categoryId + '-' + #productId"` → `products::10-3`; nested `key = "#product.id"`; method call `key = "#name.toLowerCase()"`; static text `key = "'product-' + #id"` → `products::product-15`.
- `condition` vs `unless` table: condition — "Before method / Uses parameters / Decides whether caching should start" (`condition = "#id > 0"` "Caches only when ID is positive"); unless — "After method / Uses returned object / Decides whether result should be stored" (`unless = "#result.price < 100"` "Doesn't cache products priced below $100").
- Cache stampede and `sync = true`: "500 requests arrive simultaneously. None finds data in Redis. All 500 execute repository.findById(). Database receives 500 identical queries." `sync = true`: "First request loads data; Other requests wait; Everyone receives same cached value; Only one database query executes." Use for "Expensive reports, Large computations, Frequently requested data"; "Not necessary for: Cheap database queries".
- Attributes summary table: value/cacheNames, key, condition, keyGenerator, cacheManager, cacheResolver evaluated "Before"; unless "After"; sync "During execution".
- Best practices: "Use meaningful cache names; Keep keys readable; Use SpEL instead of manual string building; Use condition for request-based decisions; Use unless for response-based decisions; Use sync=true only when duplicate database work is expensive; Avoid caching null values unless explicitly needed."

Invalidation (seminar deck):
- "The Real Problem: Keeping cache synchronized with database is difficult. This process is called Cache Invalidation."
- Strategy 1 — Cache Eviction (Recommended): "Delete the cache entry when data changes"; flow "Update database → Remove from Redis → Next request → Cache miss → Database → Fresh cache"; "Why Eviction is Usually Better": rebuilding the cached object (name, description, images, reviews, categories, price, inventory, discount, rating) in Redis is complex; "Removing it is much simpler."
- Strategy 2 — @CachePut (Update Cache): "Always executes the method, then updates the cache"; vs @Cacheable: "Skip method on cache hit" vs "Always execute"; "Read optimization" vs "Write synchronization"; "Recommendation: Use @CacheEvict for most CRUD services. It's simpler and less error-prone."
- Strategy 3 — TTL as Safety Net: "Even if a developer forgets cache eviction, Redis automatically removes stale entries." "Important: TTL is NOT your primary strategy. Eviction is primary. TTL is backup."
- Multiple cache entries: updating one product must also remove the list cache — solution `@Caching(evict = { @CacheEvict(value="products", key="#product.id"), @CacheEvict(value="products", key="'all'") })`; "Removing Everything" — `@CacheEvict(value = "products", allEntries = true)` for configuration cache, small lookup tables, reference data; "Not suitable for: Large caches with millions of entries."
- "Before or After Invocation?": default `beforeInvocation = false` ("evict after method success"); `true` removes cache before calling the method; "Recommendation: Default behavior is safer. If database update fails, cache is still valid."
- TTL decision table: Product Catalog 5–15 min; Categories 1 hour; Countries 24 hours; Currency Rates 5–30 min; Dashboard Reports 15–60 min; User Profile 5 min; Feature Flags 30 sec–2 min; Inventory Stock "Very short TTL or no cache"; Account Balance "No cache".
- What should NOT be cached (seminar): inventory stock levels ("Changes with every order/return. Stale data allows customers to buy unavailable items"); payment information ("Must reflect latest state"); authentication decisions ("Roles/permissions may change immediately. Creates security risks"); shopping carts ("Highly user-specific, frequently updated"); saga state ("Depends on current workflow. Stale data causes incorrect decisions"). Note: "This doesn't mean Redis is never used in authentication. It's commonly used for session storage, token blacklists, and rate limiting. Just avoid blindly caching authorization results with long-lived @Cacheable entries."
- Decision framework (seminar, 4 questions): read much more often than written? tolerate slightly stale data? retrieval expensive? "Will caching significantly reduce database load?" "If you answer No to most of these questions, don't cache it."

Advanced Redis (seminar deck):
- "Why One TTL Is Usually Wrong": Products 10 minutes; Categories 1 hour; Countries 24 hours; Reports 15 minutes; Session data 2 hours; Feature flags 30 seconds — "A single TTL for everything rarely makes sense in production." Per-cache TTL via custom `RedisCacheManager` bean (`RedisCacheConfiguration.defaultCacheConfig().entryTtl(Duration.ofMinutes(10))` + `withInitialCacheConfigurations`); "Key Insight: Business logic stays in @Service. Infrastructure stays in @Configuration."
- Serialization: "Redis stores bytes, not Java objects." Option 1 Java Serialization (Legacy) — "Not human readable; Large payload; Java only; Version compatibility issues". Option 2 JSON Serialization (Recommended) — "Human readable; Smaller size; Language independent; Easy debugging"; configured with `GenericJackson2JsonRedisSerializer`. "Why JSON for Microservices: Imagine later you have services in Python, Node.js, and Go reading the same Redis cache."
- redis-cli: `docker exec -it redis redis-cli`; `KEYS *`; `GET "products::1"`; `TTL "products::1"`; `DEL "products::1"`; "WARNING: Flush all (never use in production!) FLUSHALL".
- Production: "Never hardcode. Use: Spring Cloud Config for configuration; Vault for passwords; Different environments use different Redis clusters." Redis persistence: RDB snapshots, AOF, both — "Should Cache Be Persistent? Usually No... If cache disappears, the application simply rebuilds it from the database." Monitoring: "Cache Hits, Cache Misses, Hit Ratio, Evictions, Memory Usage, Latency" via "Spring Boot Actuator, Micrometer, Prometheus, Grafana".

Architecture Clinic #1 (main deck — review exercise, separate from the caching material):
- Q1–Q5 with expected answers and red flags (full text in section 11). Debrief insights: boundaries "confirmed the current split is justifiable on business domain lines"; "Saga was the right choice for Order→Payment -- not just because Kafka is trendy"; "Circuit Breaker on the outgoing call is correct, not scattered everywhere"; "Most Common Debt: in-memory stores, no idempotency, hardcoded config values"; "Key Takeaway: architecture is not a one-time decision -- it evolves with the system." "Architecture Clinic #2 is Session 24 -- after Kubernetes, Observability, and Security. Same list, more context."

## 3. Architecture

- Runtime topology (both decks): Client → Gateway → Product Service → Spring Cache → Redis Cache; Product Service → Postgres (persistent storage). "Who Does What?" — ProductService: business logic; Spring Cache: cache abstraction; Redis: cache storage; PostgreSQL: persistent storage.
- Cache-Aside read/write paths and eviction flow (main deck diagrams, section 2): miss → DB 50ms → populate with TTL; hit → 1ms; update/delete → DELETE key so next read misses.
- Annotation-to-method map (Product Service): findById + findAll = @Cacheable (reads); update + deleteById = @CacheEvict (writes) plus the shared `evictAllProductsCache()` for `key = "'all'"`.
- Seminar request lifecycle: "GET /products/1 → Spring intercepts @Cacheable method → Spring generates cache key: products::1 → Spring asks Redis for value → Found: Return immediately (cache hit) / Not Found: Execute method → Store result → Return (cache miss)."
- Architecture Clinic as a formal review of the platform built in S1–S7: service boundaries (Product vs Inventory), communication choice (Saga for Order→Payment), resilience placement (Circuit Breaker on the outgoing call), rushed decisions (in-memory store, hardcoded routes, no idempotency), boundary redesign options (Notification as part of Order; Product+Inventory shared DB) — see sections 11 and 14.
- Platform progress after S8 (main deck): "Product Service -- @Cacheable + @CacheEvict, 5 min TTL"; "Platform -- boundaries reviewed, tech debt logged"; "Product reads now served from Redis in ~1ms."

## 4. Technologies

- Spring Boot starters (both decks): `spring-boot-starter-cache` ("Provides annotations and abstraction") and `spring-boot-starter-data-redis` ("Provides Redis client and implementation") — "Why both?" requires both.
- Redis — distributed cache server (host localhost, port 6379); "Redis is already running (Docker Compose since Session 1). No infrastructure setup needed today."; redis-cli inspection; persistence options RDB/AOF; described in the seminar as "An in-memory data platform" (strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog, Pub/Sub, Streams, transactions, Lua scripts, distributed locks, replication, clustering, persistence).
- Spring Cache abstraction — @EnableCaching, @Cacheable, @CacheEvict, @CachePut, @Caching, @CacheConfig; SpEL keys.
- Redis-specific config/classes (seminar): `RedisCacheManager`, `RedisCacheConfiguration`, `entryTtl`, `cacheDefaults`, `withInitialCacheConfigurations`, `GenericJackson2JsonRedisSerializer`, `RedisTemplate` (only for Redis-specific capabilities).
- Alternative cache technologies compared in the seminar (not used in-course): HashMap (learning only), Caffeine (`CaffeineCacheManager`, `expireAfterWrite`, `maximumSize`), EhCache (legacy enterprise), Hazelcast (distributed data grid).
- Hibernate L1/L2 cache layers (seminar concept).
- Observability for cache metrics (seminar): Spring Boot Actuator, Micrometer, Prometheus, Grafana.
- Production externalization (seminar): Spring Cloud Config, Vault.
- Versions: NO version numbers appear in either deck (no Spring Boot, Java, Spring Cloud, Redis, or starter versions) → UNKNOWN — REQUIRES SOURCE REVIEW. Concrete numbers stated: TTL `300000` ms (= 5 min, main deck yml), `5m` (seminar yml), `10s` (workshop experiment), `10m` (safety-net example); ports 6379 (Redis), 8081 (main-deck demo API), 8080 (seminar workshop API).

## 5. Important terminology

- Cache; cache hit; cache miss; hit ratio; TTL (Time-to-Live); eviction / eviction policy; invalidation; stale data; "keeping the cache warm" (seminar Q5 answer).
- Cache-Aside (Lazy Loading); Read-Through; Write-Through; Write-Behind (Write-Back).
- Local cache vs distributed cache; JVM heap; Hibernate L1 / L2.
- Cache stampede; cache avalanche; cache penetration; cache breakdown (hot key); negative caching; Bloom filter; randomized TTL.
- SpEL; `condition`; `unless`; `sync`; `keyGenerator`; `cacheManager`; `cacheResolver`; `allEntries`; `beforeInvocation`.
- RDB snapshot; AOF (Append Only File); `KEYS` vs `SCAN`; `FLUSHALL`.
- Java serialization vs JSON serialization (`GenericJackson2JsonRedisSerializer`).
- Technical debt; architecture clinic; "red flag"; MISSHIT (deck shorthand for "MISS/HIT logs"); Phase 1 complete.

## 6. Code concepts

- ProductServiceApplication (main deck): `@SpringBootApplication @EnableCaching // REQUIRED -- activates the Spring Cache abstraction`.
- ProductService (main deck, exact annotations):
  - `@Cacheable(value = "products", key = "#id")` on `findById(Long id)` — log `[CACHE MISS] Loading product {} from database`; comment "Cache individual product lookups. Key: "products::1", "products::2", etc."
  - `@Cacheable(value = "products", key = "'all'")` on `findAll()` — log `[CACHE MISS] Loading all products from database`; comment "NOTE: @CacheEvict on any product change must also evict "all-products""
  - `@CacheEvict(value = "products", key = "#product.id")` on `update(Product product)` — log `[CACHE EVICT] Invalidating cache for product {}`; calls `evictAllProductsCache()` ("also evict the list cache").
  - `@CacheEvict(value = "products", key = "#id")` on `deleteById(Long id)` — same log + `evictAllProductsCache()`.
  - `@CacheEvict(value = "products", key = "'all'")` on `evictAllProductsCache()` — "called internally on any write operation".
- Seminar code: simplest `@Cacheable("products")`; complete example `@Cacheable(value = "products", key = "'product-' + #id", condition = "#id > 0", unless = "#result.discontinued", sync = true)`; `@CachePut(value = "products", key = "#product.id")` on update; `@Caching(evict = {...})`; `@CacheEvict(value = "products", key = "#product.id", beforeInvocation = true)`; Caffeine `@Bean CacheManager` with `expireAfterWrite(Duration.ofMinutes(5)).maximumSize(1000)`; custom `RedisCacheManager` bean; `@Bean RedisCacheConfiguration` with `GenericJackson2JsonRedisSerializer`; manual RedisTemplate example (`redisTemplate.opsForValue().get/set(key, product, 10, TimeUnit.MINUTES)`).
- Demo commands (main deck): `curl http://localhost:8081/api/products/1` (first → `[CACHE MISS] Loading product 1 from database`; second → "nothing logged -- served from Redis"); `docker exec -it redis redis-cli` → `KEYS products*`, `GET "products::1"`, `TTL "products::1"` ("shows remaining seconds before expiry"); `curl -X PUT .../products/1` → `[CACHE EVICT] Invalidating cache for product 1`; then GET → `[CACHE MISS]` again.
- Randomized-TTL example (seminar, cache avalanche solution): `Duration.ofMinutes(10).plusSeconds(new Random().nextInt(120))` ("Random TTL between 8-12 minutes").

## 7. Configuration

- pom.xml — both starters (verbatim in both decks): `org.springframework.boot:spring-boot-starter-data-redis` and `org.springframework.boot:spring-boot-starter-cache`.
- application.yml (main deck, Product Service):
  ```
  spring:
    data:
      redis:
        host: localhost
        port: 6379
    cache:
      type: redis
      redis:
        time-to-live: 300000 # 5 min TTL(milliseconds)
        cache-null-values: false # do not cache null responses
  ```
- application.yml (seminar): `spring.cache.type: redis`; `spring.cache.redis.time-to-live: 5m`; `cache-null-values: false`; workshop Phase 6 uses `time-to-live: 10s` ("Very short TTL") to watch expiry.
- TTL notation differs between decks (`300000` ms vs `5m`) — same 5-minute value; recorded as-is.
- "Redis is already running (Docker Compose since Session 1). No infrastructure setup needed today."
- Per-cache TTL configuration class (seminar): `@Configuration class CacheConfig` with `@Bean RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory)` — default 10 minutes; `products` 10 min, `categories` 1 hour, `countries` 24 hours, `reports` 15 min.
- Production config note (seminar): "Never hardcode. Use: Spring Cloud Config for configuration; Vault for passwords; Different environments use different Redis clusters."
- Critical yml gotcha (main deck common issues): "Check spring.cache.type=redis in yml. Without it, Spring defaults to in-memory cache, not Redis."

## 8. Failure scenarios

- Common issues table (main deck, 5 rows — 5 Real Errors, 5 Real Fixes):
  1. ""No cache manager found" at startup" → "Missing @EnableCaching on ProductServiceApplication -- this annotation activates Spring's Cache abstraction."
  2. "@CacheEvict not evicting -- MISS every call" → "Key expression must match @Cacheable exactly. products::1 vs products:1 are different keys -- use key="#id"."
  3. "Cache always MISS, never hits Redis" → "Check spring.cache.type=redis in yml. Without it, Spring defaults to in-memory cache, not Redis."
  4. "Cannot connect to Redis (ConnectionRefused)" → "Redis must be running: docker compose ps | grep redis. Verify host=localhost and port=6379."
  5. ""Serialization failed" when caching" → "Product entity must implement Serializable, or configure a Jackson serializer for Redis."
- Seminar pitfalls 1–8 (problem → solution):
  1. Cache stampede (concurrent misses hit DB) → `sync = true`.
  2. Cache avalanche ("All keys expire at the same time, causing database overload") → "Randomize TTL."
  3. Cache penetration ("Requests for non-existent data (e.g., Product 999999) hit database every time") → "Short-lived negative caching (when appropriate); Bloom Filter (advanced systems); Rate limiting."
  4. Cache breakdown (hot key — "One extremely popular product expires, causing millions of requests to hit the database") → "sync=true; Background refresh; Longer TTL for hot keys."
  5. Redis unavailable → "Degrade gracefully: Redis Down → Go to Database → Application still works"; "Configure timeout and fallback."
  6. Inconsistent caches ("Multiple service instances have different cached values") → "Use Redis (distributed cache) instead of local cache."
  7. Memory exhaustion ("Unlimited cache growth consumes all memory") → "Set maximum size and eviction policies" (`maximumSize(1000)` example).
  8. Too much caching → use the 4-question decision framework.
- Redis restart question (seminar): "If Redis restarts, is everything lost? Answer: Depends on configuration" (RDB/AOF); "Should Cache Be Persistent? Usually No... the application simply rebuilds it from the database."
- Stale-data scenario used to introduce invalidation (seminar): cached Laptop $1000, DB updated to $900, "Redis still contains: Laptop $1000"; "Some users see $900, others see $1000."

## 9. Trade-offs

- Local vs distributed caching (seminar): local is "Extremely Fast" but per-instance, restart-losing, sync-hard, "Kubernetes Ready: No"; distributed adds network latency + infrastructure + monitoring but is shared, consistent across pods, Kubernetes-ready.
- Technology choice (seminar): HashMap (learning only) / Caffeine (single instance, monolith) / EhCache (legacy) / Hazelcast (distributed computing grid) / Redis (multiple instances, Kubernetes, Spring Cloud microservices). Decision tree: multiple application instances? No → local (Caffeine recommended); Yes → Redis; advanced distributed computing needed → Hazelcast.
- Pattern choice (seminar comparison table): Cache-Aside is the most common with low complexity; Read-Through transfers loading to the cache but "Redis doesn't know your repositories"; Write-Through keeps cache fresh at the cost of write latency; Write-Behind gives fastest writes with data-loss risk. "In this course, we use Cache-Aside exclusively."
- Cache-Aside trade-offs: simple and read-optimized; "First request is slower"; "Application must remember to invalidate cache"; "Cache consistency is the application's responsibility."
- Eviction vs @CachePut vs TTL (seminar): "Use @CacheEvict for most CRUD services. It's simpler and less error-prone"; @CachePut keeps cache warm but "Always execute"; TTL "is NOT your primary strategy. Eviction is primary. TTL is backup."
- condition vs unless vs sync (evaluated before / after / during) and cost of `sync=true` ("reduces throughput unnecessarily" if everywhere).
- beforeInvocation=true trade-off: risk that the DB update fails after the cache was already removed — "Default behavior is safer."
- allEntries=true fine for small reference caches, "Not suitable for: Large caches with millions of entries."
- Java vs JSON serialization (seminar): JSON smaller, readable, language independent vs Java serialization legacy problems.
- Single TTL vs per-cache TTL (seminar): "A single TTL for everything rarely makes sense in production."
- Caching vs consistency (main deck): candidate/never-cache decisions explicitly trade staleness vs performance/security; "Cache-Aside Solves Performance -- Not Every Problem" (invalidation is "the hard part").
- Measured impact: 50ms (DB) vs 1ms (Redis) per read (main deck demo); workshop: 150ms vs 5ms/4ms (seminar Phase 7).

## 10. Common mistakes

- Main deck: forgetting @EnableCaching ("every @Cacheable and @CacheEvict annotation is silently ignored"); forgetting that the list cache must also be evicted; relying on TTL alone; caching order status/payment/inventory/auth tokens; the 5 common issues (section 8).
- Seminar @Cacheable mistakes (5): "Using default key when multiple parameters require a clearer key"; "Building cache keys inconsistently across services"; "Caching every method without considering read frequency"; "Forgetting that unless is evaluated after method returns"; "Enabling sync=true everywhere (reduces throughput unnecessarily)."
- Seminar invalidation mistakes (5): "Forgetting to evict the list cache after updating a single entity"; "Assuming TTL alone guarantees fresh data"; "Using allEntries=true for very large caches"; "Choosing arbitrary TTL values ('5 minutes sounds good')"; "Using @CachePut when simple eviction is easier and less error-prone."
- Seminar production mistakes (6): "One TTL for every cache"; "Java serialization in modern distributed systems"; "Using KEYS * on production systems (blocks Redis; use SCAN instead)"; "Forgetting memory limits and eviction policies"; "Treating Redis as the primary database"; "Hardcoding Redis credentials."
- Seminar workshop mistakes to reproduce (Phase 8): "Mistake 1: Missing @EnableCaching → Result: Nothing is cached"; "Mistake 2: Missing @CacheEvict → Result: Stale data remains in cache"; "Mistake 3: Wrong Key (`key = "#productId"` — Wrong parameter name) → Result: Duplicate cache entries or cache misses."
- Clinic red flags (main deck): "Because we were told to separate them"; "Because Kafka is better than REST"; "We put it everywhere to be safe"; "Nothing -- we designed it perfectly"; "I would not change anything."

## 11. Interview questions

- Seminar explicit "Interview Questions" (Q1–Q8, with answers):
  - Q1 "What is the difference between condition and unless?" → condition evaluated before method execution, uses parameters; unless evaluated after, can inspect `#result` to decide whether it should be cached.
  - Q2 "Why would you use sync=true?" → "To prevent a cache stampede. When multiple concurrent requests miss the cache for the same key, only one request loads the data while others wait."
  - Q3 "Why use a custom cache key?" → "To create readable, consistent, and collision-free keys, especially for methods with multiple parameters or when sharing cache conventions across services."
  - Q4 "Why is cache invalidation considered difficult?" → "Once data is cached, every database change must be reflected in the cache at the correct time. Missing an invalidation causes stale data, while unnecessary invalidation reduces cache effectiveness."
  - Q5 "When would you choose @CachePut instead of @CacheEvict?" → "When the updated object returned by the method is exactly what should be stored in the cache, and keeping the cache warm is more beneficial than forcing the next request to reload."
  - Q6 "Why is TTL considered a safety net?" → "TTL eventually removes stale entries even if a write path forgot to evict them. However, it cannot guarantee immediate consistency after updates, so it should complement--not replace--explicit cache eviction."
  - Q7 "Why shouldn't every cache have the same TTL?" → "Different business data changes at different frequencies..."
  - Q8 "Why is JSON preferred over Java serialization?" → "JSON is human-readable, has smaller payload, is language independent, and easier to debug. Java serialization is not readable, has larger payload, and only works with Java."
- Seminar mid-deck "Important Interview Question": "Q: Why doesn't the second request execute repository.findById()? A: Spring's cache proxy intercepts the method before the method body executes. If a cached value exists, Spring returns it immediately and skips invoking the method entirely."
- ARCHITECTURE CLINIC #1 (main deck) — questions, expected answers, red flags:
  - Q1 "Why is Product Service separate from Inventory Service?" — Expected: "Different team ownership, different change rate, different scaling needs. Products rarely change; inventory changes on every order." Red flag: "Because we were told to separate them" -- no business justification.
  - Q2 "Why did we use Saga instead of REST for Order → Payment?" — Expected: "Payment is a write operation -- if it fails mid-flow, we need compensation. REST is request-reply with no built-in compensation mechanism." Red flag: "Because Kafka is better than REST" -- wrong comparison entirely.
  - Q3 "Where Did We Put the Circuit Breaker -- and Why There?" — Expected: "On the Order Service's outgoing call to Payment Service. Order Service cannot afford to wait for a broken Payment Service -- it needs to fail fast and return a degraded response instead of hanging." Red flag: "We put it everywhere to be safe" -- shows no design intent. Probe deeper: "What would go wrong if we changed that?" -- "the learning is in the reasoning, not the answer."
  - Q4 "What is the most rushed architectural decision we made?" — Expected: "Open discussion. Good answers: in-memory store for Inventory, hardcoded public routes in JWT filter, no idempotency on payment retry." Red flag: "Nothing -- we designed it perfectly." "No engineer, ever."
  - Q5 "If we had to redesign one service boundary, which one?" — Expected: "Open discussion. Examples: should Notification be part of Order? Should Product and Inventory share a DB for simplicity?" Red flag: "I would not change anything." "No critical thinking applied."
- Main deck Daily Quiz: "8 Questions -- 10 Minutes" — topics "Cache-Aside • TTL • @CacheEvict • Caching Candidates • Architecture Trade-offs • Technical Debt".
- Pre-Session 9 knowledge check (2 questions, quoted in section 17).

## 12. What I must memorize

- Both starters; @EnableCaching is REQUIRED (otherwise annotations are silently ignored).
- Two annotations, two jobs: @Cacheable on reads (findById, findAll incl. `key = "'all'"`); @CacheEvict on writes (update, deleteById) + also evict the list cache.
- Config values: `spring.cache.type: redis`; `time-to-live: 300000 # 5 min TTL(milliseconds)`; `cache-null-values: false`; Redis host localhost port 6379.
- Keys: `products::1`, `key = "#id"`, `key = "'all'"`.
- "Caching is a design technique, not a technology." / "In this course, we use Cache-Aside exclusively."
- Eviction is PRIMARY, TTL is a SAFETY NET (5–10 minutes); "Never rely on TTL alone -- 'it'll expire eventually' is not a consistency guarantee for anything that matters."
- Never cache: order status (changes on every Saga step), payment info, inventory stock levels, authentication tokens.
- Phil Karlton quote ("cache invalidation and naming things").
- condition = before/parameters; unless = after/#result; sync=true stops stampede.
- Clinic expected answers Q1–Q3 and the technical debt list (8 items, section 17).
- DoD 6 items; NO commit message is stated (only "Commit all Session 8 work before Session 9 starts").
- Latencies: DB 50ms vs Redis 1ms (live demo); 150ms vs 5ms/4ms (workshop).

## 13. What I must understand

- Why the read-heavy/stale-tolerance/miss-cost questions decide caching candidates; why order status ("changes on every Saga step", S7 link) and inventory stock (out-of-stock risk) are never cached.
- Why two annotations are needed (read optimization vs write invalidation) and why one product update must invalidate the list cache too.
- Why TTL alone is not consistency ("it'll expire eventually" argument) and why eviction is the primary strategy.
- Why local caches fail behind multiple instances/Kubernetes (inconsistent copies) and why Redis is the standard distributed answer.
- Why Spring Cache is an abstraction (SLF4J/Logback, Spring Data JPA/Hibernate analogies) and why RedisTemplate is reserved for Redis-specific capabilities.
- Why Cache-Aside is preferred over Read-Through/Write-Through/Write-Behind in Spring (application controls loading; cache is passive) and why Spring uses it "exclusively" in this course.
- Why JSON serialization is preferred in microservices (future polyglot services reading the same cache).
- Why per-cache TTL matches business change rates.
- Stampede/avalanche/penetration/breakdown: what each is and its mitigation.
- Clinic reasoning: why boundaries exist (team ownership, change rate, scaling), why Saga + compensation for write flows, why a Circuit Breaker goes on the specific outgoing call, and why "architecture is not a one-time decision -- it evolves with the system."
- The technical debt list is "not a confession -- it's an engineering decision log" (revisited Session 24).

## 14. What I should implement from memory

- Add both starters to Product Service; write the yml (data.redis host/port, cache type redis, TTL, cache-null-values).
- `@EnableCaching` on the main application class.
- Annotate ProductService: @Cacheable findById/findAll; @CacheEvict update/deleteById; `evictAllProductsCache()` with `key = "'all'"` called on any write.
- Verify: curl twice (MISS → silent HIT); redis-cli `KEYS products*`, `GET "products::1"`, `TTL "products::1"` (< 300 s); PUT → evict → next GET MISS.
- 3 unit tests passing (`mvn test green`).
- Write the technical debt list in team notes.
- Be able to defend Q1–Q5 of the clinic from memory, including red-flag avoidance and the "most rushed decision" list.
- Seminar workshop: run phases 1–8; reproduce the 3 mistakes (remove @EnableCaching; remove @CacheEvict; wrong key `#productId`); observe 10s TTL expiry; observe 150ms vs 5/4ms.
- Seminar advanced (from memory): per-cache TTL `RedisCacheManager` bean; JSON serialization bean; CSS: `condition`/`unless`/`sync` usage decisions; note what to do when Redis is down (fallback to DB, no hard failure).

## 15. Relationship to previous sessions

- Pulls all of Phase 1 together for review: service boundaries and Product Service (S1/S6), Order→Payment Saga decision (S7), Circuit Breaker placement (S4/S5), hardcoded `PUBLIC_ROUTES` in JwtAuthFilter and gateway security (S2/S3), in-memory Inventory stock (S6), `payment.failure-rate 0.5` leftover (S5 demos), missing idempotency (S7), missing DLQ on Kafka consumers (S7).
- Infrastructure reuse: "Redis is already running (Docker Compose since Session 1). No infrastructure setup needed today." (Same pattern as S7's "Kafka already running".)
- Where-we-are row: "S7 Saga + Kafka" → "S8 Caching (LIVE)"; project bar adds "Product Cached" and "Arch Reviewed".
- Not-a-new-feature framing: "No new service. No new annotation type." — performance + architectural review instead of new capability.

## 16. Relationship to future sessions

- Phase 1 COMPLETE: "PHASE 1 COMPLETE -- Foundation & Core Patterns. 8 Sessions • 20 Hours • Discovery + Gateway + Resilience + Communication + Saga + Caching, all reviewed and validated."
- Next: "Session 9 -- Docker + Mid-Course Exam (5h Offline Anchor Day)", Wednesday, 10:00 AM–3:00 PM. Prep (verbatim): "Have ALL services runnable locally before arriving"; "Docker Desktop installed and running"; "docker compose up -d works without errors"; "Commit all Session 8 work before Session 9 starts."
- Knowledge check before Session 9: "What is a multi-stage Docker build and why does it produce smaller images?"; "Why should production Docker images NOT run as root?"
- Architecture Clinic #2 is Session 24 ("after Kubernetes, Observability, and Security. Same list, more context.") — the technical debt list is revisited there.
- "NEXT: PHASE 2 BEGINS"; platform bar foreshadows "Docker (S9)".

## 17. Lab relationship

- LAB NAMED IN SLIDES: NO numbered lab in the main deck (no "Lab N" label). Hands-on = "LIVE CODING" slides + "DEMO — RESULT" + "ARCHITECTURE CLINIC #1". The seminar deck has a "Live Coding Workshop" (phases 1–8) plus a "Final Checklist".
- DEFINITION OF DONE — SESSION 8 (6 items, quoted): "@Cacheable on findById() -- MISS/HIT logs verified"; "@Cacheable on findAll() -- list cached in Redis"; "@CacheEvict on update() and deleteById()"; "TTL: redis-cli TTL shows < 300 seconds"; "3 unit tests passing: mvn test green"; "Technical debt list written in team notes".
- Checkpoint commit: the wrap-up states only "Commit all Session 8 work before Session 9 starts" — NO commit message/tag is given (unlike session-05/06/07 DoD items) → commit tag UNKNOWN — REQUIRES SOURCE REVIEW.
- SESSION 9 PREP block (verbatim header): "S E S S I O N 9 I S A 5 - H O U R O F F L I N E D A Y"; items quoted in section 16.
- Architecture Clinic #1 (in-session exercise): "Be the Harshest Critic of Your Own Work"; Q1–Q5 expected answers + red flags (section 11); debrief insights (section 2); "Architecture Clinic #2 is Session 24."
- Seminar "Live Coding Workshop" phases: Phase 1 "Verify Redis is Running" (`docker ps`); Phase 2 "Enable Spring Cache" (before/after @EnableCaching); Phase 3 "Add @Cacheable" (first request log "Loading Product 1 from DB", second request "(No DB log)"; "First request: CACHE MISS / Second request: CACHE HIT"); Phase 4 "Inspect Redis" (`KEYS "*"`, `GET "products::1"`, `TTL "products::1"`); Phase 5 "Update Product" (@CacheEvict → "Cache removed; Database updated; Next request reloads cache"); Phase 6 "Change TTL" (`time-to-live: 10s` → "Request → Cache miss → Load from DB; Wait 10 seconds; Request again → Cache miss again"); Phase 7 "Performance Comparison" (without cache 150ms/145ms/148ms vs with cache 150ms/5ms/4ms); Phase 8 "Common Mistakes" (the 3 mistakes quoted in section 10).
- Demos: main deck "Watch the Cache Behavior Live" against `http://localhost:8081/api/products/1` with redis-cli checks and PUT eviction; seminar workshop steps against `http://localhost:8080/products/1`.
- Daily Quiz: "8 Questions -- 10 Minutes" (topics in section 11).
- Technical debt checkpoint — "What We're Choosing to Fix Later -- On the Record" (8 items, quoted): "In-memory stock map in Inventory Service -- no persistence across restarts"; "No idempotency on payment retry -- duplicate charges possible"; "PUBLIC_ROUTES list hardcoded in JwtAuthFilter -- should be in config"; "No dead-letter queue on Kafka consumers -- failed events silently lost"; "payment.failure-rate still set to 0.5 -- leftover test configuration"; "No structured logging -- plain text log lines, hard to search at scale"; "No API versioning strategy -- /api/products with no version prefix"; "Missing database migrations (Flyway/Liquibase) -- schema deployed manually". "This is not a confession -- it's an engineering decision log. We revisit this exact list at Architecture Clinic #2 (Session 24)."
- No other homework beyond the DoD + Session 9 prep + knowledge check is stated in the deck.
