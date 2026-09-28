# Session 3 — API Gateway Advanced (JWT Authentication · Rate Limiting · Redis · Security Boundary)

Source files: Session_03_Gateway_Advanced.pdf (31 pages) and Session_03_Gateway_Advanced_Continued.pdf (43 pages, Arabic-language supplemental deck). Both read in full.

File coverage:
- Session_03_Gateway_Advanced.pdf — the course-session deck: recap, filter types + execution order, JWT structure/flow, live coding (JwtUtil, JwtAuthFilter, secret config), security boundary, rate limiting problem, token bucket, Redis KeyResolver, RequestRateLimiter config, demo, Lab 2B, quiz, homework, troubleshooting.
- Session_03_Gateway_Advanced_Continued.pdf — supplemental deck in Arabic with three parts: (1) "JWT Authentication in API Gateway" (why the gateway, Security Boundary, public/protected routes, Method+Path, full filter code, header enrichment, why removing spoofed headers), (2) "Rate Limiting with Redis" — token bucket deep dive (replenishRate, burstCapacity, Steady State, Burst, full timeline), (3) "Why Redis?" (per client key, KeyResolver, fail open vs fail closed, Redis CLI inspection, Lua Scripts note).

## 1. Why this topic exists

Recap of Session 2: the gateway exists — single entry point :8080, routes /api/products/**, global logging filter, load balancing. "What's Missing": "Anyone can call any endpoint — no authentication"; "No protection against abuse — 10,000 req/sec breaks Product Service"; "No way to know WHO is calling". Today's goal: "Making the Gateway smart — adding a Security & Protection layer with JWT validation and Rate Limiting."

Supplemental deck — why validate JWT at the gateway: without a gateway, every service must read the Authorization header, validate the signature, check expiration, extract claims, reject invalid tokens; with 10 microservices "we duplicate the exact same authentication code: 10 Times" — violating DRY ("Don't Repeat Yourself"). With a gateway, "only one component is responsible for authentication."

Rate limiting problem (course deck): "A bot sends 10,000 requests/second to GET /api/products". Without rate limiting: Product Service is overwhelmed, database crashes, ALL users affected. With rate limiting at the Gateway: bot gets 429 after 100 req/s, Product Service stays healthy. Key insight: "Rate limiting is a cross-cutting concern → belongs at the Gateway, not in services. Services should NOT implement their own rate limiting — that defeats the purpose of the Gateway."

## 2. Core concepts

- Filter types revisited: GatewayFilterFactory — "Creates configurable filters for routes"; used in application.yml as "- name: ..."; examples RequestRateLimiter, StripPrefix; "Parameterized — same filter, different args per route". GlobalFilter (today's focus) — "Implemented as @Component, applies to ALL routes"; no configuration needed, always active; examples LoggingFilter (S2), JwtAuthFilter (today); "Best for cross-cutting concerns: auth, logging".
- Filter execution order (why it matters): 1 LoggingFilter (order = HIGHEST_PRECEDENCE) "Logs every request first — even rejected ones"; 2 JwtAuthFilter (order = HIGHEST_PRECEDENCE + 1) "Validates token — runs after logging, before routing"; 3 Routing (predicate match, forwarded to the matched service); 4 RequestRateLimiter (filter factory on route, applied per-route, checked alongside routing).
- JWT structure — Header . Payload . Signature: HEADER `{"alg":"HS256","typ":"JWT"}` ("Algorithm + token type"); PAYLOAD `{"sub":"user123","role":"ADMIN"}` ("Claims — user data, expiry, role"); SIGNATURE `HMACSHA256(header+payload, secret)` ("Proves the token wasn't tampered with"). "The Gateway can verify the signature LOCALLY using the shared secret — no network call to an auth server needed for every request."
- JWT validation flow — 7 steps (course deck): 1 Check if route is whitelisted (public routes skip validation). 2 Extract Authorization header — look for "Bearer <token>". 3 If missing → return 401 immediately (do not forward). 4 Validate JWT signature using the secret/public key. 5 If expired or invalid → return 401 with error message. 6 If valid → extract claims, add as headers (X-User-Id, X-User-Role). 7 Forward the request with enriched headers to the upstream service.
- Security Boundary (Continued deck, "the most important concept of this session"): "The Gateway validates the JWT. Downstream services trust the Gateway. The services no longer care about JWT. Instead they trust the Gateway. The Gateway becomes the Security Boundary of the system." Course deck: "The Gateway is the trust boundary. Everything inside the network trusts the Gateway's validation — re-validating in every service duplicates work and adds latency. This is THE core security principle of API Gateways."
- Public vs Protected routes (Continued deck): Public examples — GET /api/products, POST /api/auth/login, POST /api/auth/register, GET /actuator/health. Protected examples — POST /api/products, PUT /api/products/5, DELETE /api/products/5, GET /api/orders.
- Why Method + Path (Continued deck): naive `isPublicRoute` using `path.startsWith("/api/products")` looks correct, but GET /api/products is public while POST /api/products must NOT be — "The path is identical. The HTTP Method is different." Therefore validate HTTP Method + URL Path.
- Header enrichment: gateway converts claims into trusted headers — e.g. JWT `{"sub":"25","role":"ADMIN"}` becomes `X-User-Id: 25`, `X-User-Role: ADMIN`, forwarded to the service. Course deck example: `{"sub":"user123","role":"ADMIN"}` → X-User-Id: user123 / X-User-Role: ADMIN; Product Service "Trusts the headers — no re-validation".
- Why remove existing headers (Continued deck): "Imagine a malicious client sends: X-User-Role: ADMIN. If the Gateway simply forwards it, the attacker may gain unauthorized access." Therefore the gateway ALWAYS removes X-User-Id / X-User-Role then adds trusted values from the validated JWT, guaranteeing "downstream services only receive trusted identity information."
- Token Bucket algorithm (course deck): "The Bucket — 14 / 20 tokens remaining; replenishRate = 10 — Add 10 tokens per second to the bucket; burstCapacity = 20 — Bucket holds max 20 tokens; Each request = 1 token; If bucket is empty → 429 Too Many Requests; Steady: 10 req/s allowed · Burst: up to 20 at once · Redis stores token count per client."
- Continued-deck clarifications: a bucket token "is NOT a JWT" — "لدينا نوعان مختلفان تمامًا" (two completely different things): JWT Token = Authentication; Bucket Token = Rate Limiting; token bucket is "just a counter". replenishRate = how many tokens are added per second (bucket 5 + 10 = 15; 18 + 10 would be 28 but stays at 20 = burstCapacity ceiling). burstCapacity "does NOT mean requests per second — this is one of the most common mistakes"; it is the maximum tokens that can be stored; if the bucket is full, all tokens can be consumed in a fraction of a second.
- Steady State = the rate supportable continuously, approximately the replenishRate value "as long as no extra stored tokens" (example: replenishRate=10 → 10 Requests/Second sustained, second by second). Burst = a sudden surge absorbed using stored tokens up to burstCapacity (example: bucket full with 20 → 20 requests at once → 0 tokens; after a second +10 → only 10 of the next 20 allowed, rest 429).
- Full timeline example (Continued deck): replenishRate 10, burstCapacity 20. Second 0: bucket 20; client sends 15 → 5 left. Second 1: +10 → 15; client sends 12 → 3 left. Second 2: +10 → 13; client sends 25 → only 13 allowed, 12 rejected with 429 Too Many Requests.
- Easy rules to memorize (Continued deck): replenishRate = refill speed (Tokens/Second); burstCapacity = bucket size (Maximum Tokens Stored); Steady State = the long-term sustainable rate; Burst = using the stored balance to allow many requests in a short time.
- Why Redis (Continued deck, Part 3): "How does the Gateway know that this user already consumed 15 Tokens? Where will it store the count?" Without Redis every request is independent — each request would see 20 tokens, the counter resets every time, "and the Rate Limiter would never work at all." Redis stores only the remaining token count per client — not requests, not JWT, not responses. Example keys: Ali 192.168.1.5 → 7 remaining; Ahmed 192.168.1.20 → 19; Sara 192.168.1.40 → 13 — "Redis is like a table: Key → Remaining Tokens." "Redis stores the token count per client key" — "Note the word per client key, not per server and not per application."
- Why Redis and not memory (Continued deck): with one gateway, memory works; with Gateway 1/2/3 each keeping its own memory, "Gateway1: Ali = 5 Tokens while Gateway2: Ali = 20 Tokens — and this is wrong"; with Redis "all of them see the same data."
- What is the Client Key: `key-resolver: "#{@ipKeyResolver}"` — decides how clients are distinguished; per-IP example makes each IP its own bucket. KeyResolver determines how the client key used by the rate limiter is created (lesson summary).
- Fail Open (Continued deck): "What happens if Redis stops? The default behavior in Spring Cloud Gateway is Fail Open": Redis Down → Disable Rate Limiting → Allow Requests. Rationale (bank example): better the site keeps working for a minute without rate limiting than fully stopping — "Spring chose Availability instead of Strict Rate Limiting". The alternative is Fail Closed: Redis Down → Reject Everything — "more secure but may block all real clients".
- Redis CLI inspection (Continued deck): with docker compose (image `redis:7`, ports "6379:6379"), `docker ps`, then `docker exec -it redis redis-cli`; `KEYS *` or preferably `SCAN 0`; you will see keys like `request_rate_limiter.{192.168.1.5}` (format may vary slightly by Spring Cloud Gateway version). IMPORTANT note: "In reality Spring Cloud Gateway does not store values as a readable string you can read with GET. It uses Lua Scripts and stores the Bucket data in more than one Key (and sometimes different data types or internal keys)" — so you will not find "Remaining Tokens = 7" directly; Redis keeps the Token Bucket state per Client Key while internal storage details are managed by Spring Cloud Gateway using Lua Scripts "to achieve atomic operations and be safe even with multiple Gateways running in parallel."
- Public routes configuration pattern (course deck): today's simple implementation is an in-code list ("fine for today's lab, but rigid"); production pattern (bonus) is `@ConfigurationProperties("gateway.public-routes")` loaded from application.yml — "change without recompiling". "Bonus opportunity: implement the production pattern for +5 points in Lab 2B." The Continued deck shows the same idea under `security.public-routes` with `@ConfigurationProperties(prefix = "security")` — "closer to what is applied in real projects".
- StripPrefix closing-the-loop slide (course deck): scenario needing stripping — client GET /gateway/products/123, StripPrefix=1 removes 1 segment /gateway, service receives /products/123; "Our platform: no stripping needed" — client GET /api/products/123, StripPrefix=0 removes nothing, service receives /api/products/123.

## 3. Architecture

Request path: Client -> API Gateway -> [LoggingFilter -> JwtAuthFilter -> Routing -> RequestRateLimiter] -> downstream service (reads X-User-Id / X-User-Role only). Supplemental flow diagram: Gateway branches into "Is Public Route? YES / NO"; NO → Read Authorization -> Validate JWT -> Extract Claims -> Header Enrichment -> Product Service ("Read X-User-Id, Read X-User-Role, Execute Business Logic") -> Response.

Rate limiting path (Continued deck diagram): Client -> API Gateway (IP = 192.168.1.5) -> Redis (Key: 192.168.1.5, Remaining Tokens = 7) -> Product Service. Multiple gateways share one Redis so "all of them see the same data."

## 4. Technologies

- JJWT (io.jsonwebtoken) — jjwt-api 0.11.5; jjwt-impl 0.11.5 (runtime scope); jjwt-jackson 0.11.5 (runtime scope).
- Spring Cloud Gateway GlobalFilter / GatewayFilterFactory; AntPathMatcher (course deck), PathPattern + PathPatternParser + PathContainer (Continued deck variant).
- Spring Session/Spring Data Redis reactive: `spring-boot-starter-data-redis-reactive`; Redis at localhost:6379; Redis Docker image `redis:7` (Continued deck).
- Spring Cloud Gateway RequestRateLimiter with redis-rate-limiter args.
- Project package naming: `com.microservices.pro.apigateway.filter`, `com.microservices.pro.apigateway.security` (JwtUtil import); Lombok `@RequiredArgsConstructor`.
- jwt.io website for generating a test JWT (live demo option 1).
- HashiCorp Vault referenced for production (Session 21): JWT secret and Redis password.
- Versions: jjwt 0.11.5 (the only pinned version in these decks); Spring Boot/Cloud versions not restated here (they appear in the Session 2 Continued deck: Java 21 / Spring Boot 3.3.x / Spring Cloud 2023.x).

## 5. Important terminology

- Security Boundary — the gateway is the single place JWT is validated; services trust its headers.
- Trust boundary / header enrichment — adding X-User-Id and X-User-Role from validated claims.
- Public Route / Protected Route — defined by HTTP Method + Path, not path alone.
- whitelist — public routes skip validation (step 1 of the JWT flow).
- Bearer token — `Authorization: Bearer <token>`; token extracted via `authHeader.substring(7)`.
- Claims — payload data such as `sub` (user id) and `role`; `Claims.getSubject()`, `claims.get("role", String.class)`.
- Token Bucket — counter-based limiter: replenishRate (tokens added per second), burstCapacity (max tokens stored), requestedTokens (tokens consumed per request).
- Steady State — sustained rate; Burst — temporary surge absorbed by stored tokens.
- 429 Too Many Requests — returned when no token is available.
- KeyResolver / client key — strategy that identifies the client (IP or user id); "per client key, not per server".
- Fail Open — Redis down → rate limiting disabled, requests allowed (Spring Cloud Gateway default).
- Fail Closed — Redis down → reject everything (alternative style).
- X-RateLimit-Remaining — header observed decreasing to 0 during the demo.
- Lua Scripts — used by Spring Cloud Gateway for atomic bucket updates across multiple gateway instances.
- DRY — "Don't Repeat Yourself" — the violation caused by duplicating JWT validation in every service.

## 6. Code concepts

JJWT dependencies (course deck Step 1):

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.11.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
```

JwtUtil (course deck Step 2):

```java
@Component
public class JwtUtil {
    @Value("${jwt.secret}")
    private String secret;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(UTF_8));
    }

    public Claims validateToken(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(getSigningKey())
            .build()
            .parseClaimsJws(token)
            .getBody();  // throws if invalid or expired
    }
}
```

JwtAuthFilter (course deck Step 3): `@Component public class JwtAuthFilter implements GlobalFilter, Ordered`; `AntPathMatcher pathMatcher`; injected `JwtUtil`; `private record PublicRoute(HttpMethod method, String pathPattern)`; `PUBLIC_ROUTES` list as printed in the course deck — `GET /api/v1/products/**`, `GET /actuator/health`, `POST /actuator/info`. The filter: `isPublicRoute` check → `chain.filter`; else read `HttpHeaders.AUTHORIZATION`, require `Bearer ` prefix; `jwtUtil.validateToken(authHeader.substring(7))`; `claims.getSubject()` and `claims.get("role", String.class)` (401 "Token does not contain role claim" if blank); mutate headers — `remove("X-User-Id")`, `remove("X-User-Role")`, then `add("X-User-Id", userId)`, `add("X-User-Role", role)`; forward mutated exchange; `catch (JwtException e)` → "Invalid or expired token". `unauthorizedResponse` sets `HttpStatus.UNAUTHORIZED`, JSON content type, body `{"status":401,"error":"Unauthorized","message":"%s"}` written via `DataBuffer`. `getOrder()` returns `Ordered.HIGHEST_PRECEDENCE + 1` ("runs after LoggingFilter").

Continued-deck variant (slightly different implementation also printed in the slides): imports `com.microservices.pro.apigateway.security.JwtUtil`, `PathPatternParser PARSER`, `private record PublicRoute(HttpMethod method, PathPattern pattern)`, and `PUBLIC_ROUTES` = `GET /api/products`, `POST /api/auth/login`, `POST /api/auth/register`, `GET /actuator/health`; `isPublicRoute` uses `PathContainer.parsePath(path)` + `route.pattern().matches(pathContainer)`. Note: the two decks' public-route lists and matchers differ — implementers should pick one consistently (Lab 2B intent is "public route bypass, header enrichment").

Downstream service (Continued deck): Product Service never validates JWT; it reads headers:

```java
@GetMapping("/{id}")
public ResponseEntity<Product> getProduct(
        @PathVariable Long id,
        @RequestHeader("X-User-Id") String userId,
        @RequestHeader("X-User-Role") String role) {
    log.info("User ID : {}", userId);
    log.info("Role : {}", role);
    return ResponseEntity.ok(...);
}
```

Also shown: `HttpServletRequest request` with `request.getHeader("X-User-Id")` / `("X-User-Role")`, and `@RequestHeader HttpHeaders headers` with `headers.getFirst(...)`.

Test JWT generation (course deck Step 4 of live coding): Option 1 — jwt.io (Header `{"alg":"HS256","typ":"JWT"}`, Payload `{"sub":"user123","role":"CUSTOMER","exp":<future timestamp>}`, Secret = the shared secret); Option 2 — Java:

```java
String token = Jwts.builder()
    .setSubject("user123")
    .claim("role", "CUSTOMER")
    .setExpiration(new Date(System.currentTimeMillis() + 3600000)) // 1 hour
    .signWith(Keys.hmacShaKeyFor(secret.getBytes()))
    .compact();
```

RateLimitConfig (course deck Step 3):

```java
@Configuration
public class RateLimitConfig {
    @Bean @Primary  // Option A: rate limit per IP address
    public KeyResolver ipKeyResolver() {
        return exchange -> Mono.justOrEmpty(
            exchange.getRequest().getRemoteAddress()
        ).map(addr -> addr.getAddress().getHostAddress());
    }

    @Bean  // Option B: rate limit per authenticated user
    public KeyResolver userKeyResolver() {
        return exchange -> Mono.justOrEmpty(
            exchange.getRequest().getHeaders().getFirst("X-User-Id")
        ).defaultIfEmpty("anonymous");
    }
}
```

## 7. Configuration

JWT secret (course deck Step 4):

```yaml
jwt:
  secret: microservices-pro-course-secret-key-2024-minimum-256-bits

# NOTE: In production, this comes from HashiCorp Vault (Session 21)
# NEVER commit real secrets to Git — this is a dev placeholder only
```

Redis connection (course deck Step 2):

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      # In production: host from Config Server, password from Vault (Session 21)
```

RequestRateLimiter on the product route (course deck Step 4):

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: product-service
          uri: lb://PRODUCT-SERVICE
          predicates:
            - Path=/api/products/**
          filters:
            - AddResponseHeader=X-Platform, microservices-pro
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
                redis-rate-limiter.requestedTokens: 1
                key-resolver: "#{@ipKeyResolver}"
```

Continued-deck: same filter block; `requestedTokens` explanation — each request consumes requestedTokens (default 1); it can be set to 5 meaning each request consumes 5 tokens, "sometimes used for very costly operations". Public-routes-in-YAML pattern example:

```yaml
security:
  public-routes:
    - method: GET
      path: /api/v1/products/**
    - method: GET
      path: /actuator/health
    - method: GET
      path: /actuator/info
```

## 8. Failure scenarios

- Anything unauthenticated calling protected endpoints (recap: 10,000 req/sec breaks Product Service; no way to know WHO is calling).
- Missing/malformed token: no Authorization header or no "Bearer " prefix → 401 immediately; request never reaches the service.
- Expired / invalid / tampered JWT → 401 Unauthorized (covered by `catch (JwtException)`).
- Token without role claim → 401 "Token does not contain role claim".
- Header spoofing: malicious client sends X-User-Role: ADMIN — mitigated by remove-then-add before forwarding.
- Public route mis-detected: checking only path (not method) would make POST /api/products public — "Public ❌ (Wrong!)".
- Redis down: default Fail Open — rate limiting disabled and requests allowed; Fail Closed alternative would reject everything (more secure but may block all real clients).
- Redis not running: rate limiter not triggering (always 200) — "Check Redis is running: docker compose ps".
- "No KeyResolver bean" error — add @Primary to the main KeyResolver bean.
- JWT 401 on a valid token — check `jwt.secret` matches the signing secret; minimum 256 bits (32 characters).
- "JWT strings must contain exactly 2 periods" — malformed token; ensure the Bearer prefix is stripped: `authHeader.substring(7)`.
- Public route returning 401 — use `path.startsWith()`, not `path.equals()` — "path may include trailing segments".
- After burst exhaustion every additional request is a 429 until replenishment.

## 9. Trade-offs

- Validate at gateway vs in every service: one validation point, less duplication and latency, services focus on business logic — but everything inside the network must be trusted (gateway becomes the trust boundary).
- In-code public-route list vs `@ConfigurationProperties` from YAML: simple but rigid vs "change without recompiling" (and closer to real projects) — the deck offers +5 bonus points for the production pattern.
- Rate limiting at gateway vs per service: cross-cutting concern belongs at the gateway; "Services should NOT implement their own rate limiting — that defeats the purpose of the Gateway."
- replenishRate vs burstCapacity: steady throughput vs short-term burst absorption ("can absorb 20 requests at once"); burst is not a second "requests per second" limit (common misunderstanding).
- Fail Open vs Fail Closed when Redis dies: availability (degraded protection) vs strictness (may block all real clients). "Spring chose Availability instead of Strict Rate Limiting."
- Single gateway memory vs Redis: memory works for one instance; with multiple gateways each memory diverges (Ali 5 vs 20 tokens) — Redis is shared state, with atomic Lua script updates.
- requestedTokens 1 vs higher values: allows charging more tokens for expensive operations.

## 10. Common mistakes

- Implementing isPublicRoute via `path.startsWith(...)` only, ignoring the HTTP Method (POST /api/products becomes public by mistake).
- Not removing attacker-supplied X-User-Id / X-User-Role before adding trusted values.
- Confusing the two token types — "Token here is not JWT": bucket tokens are just counters for rate limiting, unrelated to authentication.
- Believing burstCapacity means "requests per second" — the deck names this "one of the most common mistakes"; it is the max stored tokens.
- Reading Weight-style intuition into the limiter: 80/20 percentages vs token arithmetic — (Weight example belongs to Session 2; here the equivalent trap is assuming burstCapacity controls per-second throughput).
- Forgetting @Primary on the chosen KeyResolver bean.
- Committing real secrets — "NEVER commit real secrets to Git — this is a dev placeholder only"; production secrets come from Vault (Session 21).
- Forgetting `.substring(7)` when stripping "Bearer " ("JWT strings must contain exactly 2 periods").
- Expecting to read simple values from Redis with GET — Spring Cloud Gateway stores bucket data via Lua Scripts across internal keys.
- Building rate limiting into individual services instead of the gateway.

## 11. Interview questions

Deck-labeled quiz topics: "JWT Validation · Rate Limiting · Token Bucket · Filter Order · Security Boundary" (Daily Quiz, 8 questions, 10 minutes). Homework (pre-Session 4) knowledge-check questions: "What is a cascading failure? What are the 3 Circuit Breaker states? What is a fallback method?" (those belong to Session 4's topic). The Continued deck's stated learning objectives double as self-test questions: why validate JWT in the gateway; what is the Security Boundary; how to configure public routes by HTTP Method + Path; why downstream services do NOT validate JWT again; why Redis is needed; what is stored in Redis; meaning of per client key; role of KeyResolver; what happens if Redis stops. An explicit dedicated interview-question list: UNKNOWN — REQUIRES SOURCE REVIEW.

## 12. What I must memorize

- Filter order: LoggingFilter = HIGHEST_PRECEDENCE, JwtAuthFilter = HIGHEST_PRECEDENCE + 1, then routing; RequestRateLimiter is per-route.
- JWT = Header.Payload.Signature with example values; gateway verifies signature locally with the shared secret (no auth-server call per request).
- The 7-step JWT validation flow; the 401 responses ("Missing token", "Invalid or expired token", "Token does not contain role claim", missing Authorization header).
- Header contract downstream: X-User-Id, X-User-Role; remove-then-add to defeat spoofing.
- Public routes = HTTP Method + Path (GET /api/products public, POST /api/products protected, /api/auth/login, /api/auth/register, /actuator/health public in the printed lists).
- jjwt coordinates and version 0.11.5 (api / impl runtime / jackson runtime).
- jwt.secret minimum 256 bits (32 characters); dev placeholder secret; production via Vault (Session 21).
- Token bucket parameters and arithmetic: replenishRate=10, burstCapacity=20, requestedTokens=1; Steady State ≈ replenishRate; burst up to burstCapacity; 429 when empty.
- Redis stores token count per client key; KeyResolver = "#{@ipKeyResolver}"; Fail Open default when Redis is down.
- Demo expectations: 25 rapid requests → roughly 20×200 then 429s; X-RateLimit-Remaining decreasing to 0.
- Lab 2B: JwtUtil + JwtAuthFilter + public route bypass + header enrichment; RequestRateLimiter with IP-based KeyResolver; minimum 5 unit tests. Checkpoint: GET (no token) 200; POST (no token) 401; valid JWT 201; 25 rapid requests → some 429; commit `session-03: ...`.

## 13. What I must understand

- Why authentication is validated once at the gateway (DRY; 10 services → 10× duplication otherwise) and why services trust the enriched headers instead of re-validating.
- Why method+path (not path alone) defines a public route.
- Why claims must be re-injected with a remove-first step (spoofed X-User-Role scenario).
- How the token bucket behaves over time: sustained rate, burst absorption, refill, ceiling, exhaustion → 429; the full second-by-second timeline example.
- Why distributed rate limiting state must live in Redis (multi-gateway consistency; per client key not per server) and why updates use Lua scripts (atomic, safe with parallel gateways).
- Why Spring Cloud Gateway defaults to Fail Open and what Fail Closed would mean.
- Why the rate limiter belongs at the gateway layer as a cross-cutting concern.

## 14. What I should implement from memory

Lab 2B ("JWT Authentication Filter & Rate Limiting"):
1. Implement JWT Authentication Filter — "JwtUtil + JwtAuthFilter, public route bypass, header enrichment".
2. Add Rate Limiting to Product Route — "RequestRateLimiter with IP-based KeyResolver".
3. Write Unit Tests — "Minimum 5 tests covering auth + rate limit behaviour".

From memory: write JwtUtil (`Jwts.parserBuilder().setSigningKey(...).parseClaimsJws(token).getBody()`), JwtAuthFilter (public-route check by method+path, Bearer extraction with substring(7), try/catch JwtException, header remove+add, order HIGHEST_PRECEDENCE + 1, JSON 401 body), the RateLimitConfig KeyResolvers (@Primary on the chosen one), the RequestRateLimiter YAML block, and optionally the bonus production pattern with @ConfigurationProperties for public routes (+5 points in Lab 2B).

## 15. Relationship to previous sessions

Direct continuation of Session 2: recap slide lists what exists (single entry point :8080, routes /api/products/**, Global LoggingFilter, load balancing) and what is missing (auth, abuse protection, caller identity). It closes Session 2's StripPrefix loop ("StripPrefix — Why We Set It to 0"). The filter-order slide builds on Session 2's LoggingFilter (`HIGHEST_PRECEDENCE` → today's JwtAuthFilter runs right after). The Continued deck's DRY argument extends Session 2's "no single place to add authentication" problem statement. Platform progress: S2 = gateway single entry point; S3 = "Gateway secured — JWT + Rate Limiting".

## 16. Relationship to future sessions

- Production secrets: "In production, this comes from HashiCorp Vault (Session 21)" (JWT secret and Redis password).
- Session 4 preview via homework: Resilience4j Circuit Breaker Basics (resilience4j.readme.io); knowledge-check questions about cascading failure, the 3 CB states, fallback.
- Observability was flagged "SESSION 3+" on the Session 2 responsibilities slide; the gateway remains the single place to log/trace traffic.
- Order and Payment services arrive in Session 4 (platform map), giving the JWT-enriched identity that later services consume.

## 17. Lab relationship

Exact slide content — "HANDS-ON: Lab 2B — JWT Authentication Filter & Rate Limiting" with the 3 steps quoted in section 14. Checkpoint / Definition of Done (course deck): "GET /api/products (no token) → 200"; "POST /api/products (no token) → 401"; "Valid JWT → 201 Created"; "25 rapid requests → some return 429"; "Pushed: session-03: ...". Demo evidence (course deck): the 3 JWT scenarios (200 / 401 / 201) and the 25-request shell loop `for i in {1..25}; do curl -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/products; done` with expected "200 ... 429" output and "Notice X-RateLimit-Remaining decreasing to 0. The Gateway protects Product Service — it never even sees the rejected requests." Bonus task explicitly tied to the lab: "Bonus opportunity: implement the production pattern for +5 points in Lab 2B" (@ConfigurationProperties for public routes). Homework: "Pre-Session 4 Reading (15 min) — Resilience4j — Circuit Breaker Basics", with knowledge-check questions listed in section 11. The Continued deck lists no lab of its own; it supplies the theory deep-dive (security boundary, token bucket, Redis) plus the Redis CLI exercise (`docker exec -it redis redis-cli`, `SCAN 0`) as "practical viewing of stored values". Platform progress slide lists what was added: JwtUtil, JwtAuthFilter (GlobalFilter, order 1), RateLimitConfig (IP + User KeyResolvers), RequestRateLimiter on product-service route.
