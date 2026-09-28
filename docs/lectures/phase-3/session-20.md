# Session 20 — Security Part 2: Client Credentials, Resource Server & Role-Based Authorization (Retiring JwtAuthFilter)

Source files: `Session_20_Security_Part2.pdf` (24-page slide deck), `Sessions_19_20_Keycloak & OAuth2 Security.pdf` (71-page combined student tutorial — Part B covers Session 20; Part A is written up in `session-19.md`). File check: the two PDFs differ in size and packaging — the deck is the instructor presentation (Monday 3:00–5:30 PM, Online, 2.5 hours), the tutorial is the combined self-contained study document. Both were read; differences between them are noted inline (most importantly the issuer-URI/realm/port discrepancy — see §7/§8).

## 1. Why this topic exists

- Session 19 solved human login (Authorization Code Flow). Session 20 covers the OTHER half: **service-to-service authentication (Client Credentials Flow) and actually wiring the Gateway as a real OAuth2 Resource Server, replacing JwtAuthFilter for good** (deck, explicit scope boundary OBG-001).
- **Before/after table (deck):** Before — custom `JwtAuthFilter` + hardcoded secret + no revocation + no login UI. After — JWKS-based RSA public-key validation, real users + service accounts, standards-based tokens. "DELETED TODAY": the hand-written mechanism is retired.
- **The "no user" problem (combined deck §30):** a scheduled job runs every night ("find products with low stock") — Scheduler → Order Service → Inventory Service. There is no customer, therefore no customer JWT exists. Who is making the request? Not customer1 — it is `order-service`. "The service itself needs an identity."
- The old shared-secret model means every component that verifies tokens must know the secret — a security problem (JWKS/asymmetric signing fixes it). The Gateway never receives Keycloak's private signing key.
- Design/architecture decision drilled in the deck: **"Gateway validates first + Resource Server on sensitive services" (defense in depth)** — not trusting the Gateway blindly, and not validating everywhere twice.
- Duplicate-validation vs no-validation reasoning: stateless JWT vs opaque token → the course chose JWT.

## 2. Core concepts

- **Client Credentials Flow:** the OAuth2 flow for when there is no user. Authorization Code = client acts on behalf of a user; Client Credentials = **client acts as itself**. No user, no browser, no redirect — direct call Order Service → Keycloak → `access_token` → `Authorization: Bearer ...` → Inventory Service.
- **Flow comparison (combined deck table):** Authorization Code — user involved Yes; browser Usually yes; redirect Yes; authentication subject User; typical use customer login; example Customer → Gateway. Client Credentials — user No; browser No; redirect No; subject Service/client; typical use service-to-service; example Order → Inventory.
- **`sub` semantics:** for a customer, `sub` = customer identity; for Client Credentials, `sub` = service/client identity. Conceptually: Customer Token = "I am customer1"; Service Token = "I am order-service."
- **JWKS = JSON Web Key Set:** a set of public keys published by the authorization server; Keycloak exposes them via OpenID Connect metadata at the realm's `/protocol/openid-connect/certs` endpoint. Spring Security can discover this automatically when configured with the issuer URI.
- **Asymmetric signing rule:** Keycloak holds the private key (only Keycloak signs); the public key is distributed to validators (Gateway, Order Service, Inventory Service). "Private key: ONLY Keycloak. Public key: Can be distributed to token validators."
- **Issuer URI configuration:** `spring.security.oauth2.resourceserver.jwt.issuer-uri` — Spring Security uses it to discover the authorization-server metadata and public keys and then validates the token's issuer and timestamps. Acceptability rule: **Valid signature + Trusted issuer + Valid timestamps = acceptable token** (an attacker's own well-formed JWT lacks the trusted `iss`).
- **Issuer vs Audience:** `iss` answers "Who issued this token?" (`iss = Keycloak`); `aud` answers "Who is this token intended for?" (`aud = my-api`). In production, audience validation can provide an additional protection layer; Spring Security supports configuring audiences in addition to the issuer.
- **Resource Server:** an application that protects resources and accepts access tokens — Product Service, Order Service, Inventory Service, API Gateway can all act as Resource Servers (Client/Bearer Token → validate → Allow/Reject).
- **Authentication vs Authorization:** Authentication = "Who are you?" (customer1) — solved by Keycloak + JWT; Authorization = "Are you allowed to perform this operation?" — e.g., customer1 might not be allowed to DELETE /api/products/10 while admin1 may be. 401 Unauthorized = authentication problem (you have not successfully authenticated); 403 Forbidden = authenticated but not authorized.
- **Keycloak roles → Spring authorities:** token contains `realm_access.roles` (e.g., USER, ADMIN); Spring Security needs `ROLE_USER` / `ROLE_ADMIN` — a converter translates. "realm_access.roles mapped automatically once 'roles' scope is present" (deck live-coding note; combined deck shows the explicit converter).
- **Stateless JWT vs opaque token:** the course chose JWT (implied by the comparison slide title in the deck); token revocation/refresh-rotation is delegated to Keycloak (scope boundary).
- **Gateway validates first + Resource Server on sensitive services** (defense in depth): two independent layers — demo shows two independent 401s.
- **Why not keep both filters:** "half-retired security code is a liability"; two competing JWT validation mechanisms increase complexity and may create inconsistent security behavior. For the training platform a clean cutover is appropriate; in a real production migration with existing clients and tokens, a temporary parallel-run migration strategy may be appropriate.

## 3. Architecture

- **Service-to-service (Client Credentials):** Order Service → (client_id + client_secret) → Keycloak → access_token → Order Service → `Authorization: Bearer ...` → Inventory Service (which validates signature, issuer, expiration and applies authorization rules). No browser, no user.
- **Customer vs service token paths (combined deck §62):** Customer → Keycloak → Customer Access Token → Gateway → Order Service (token represents customer1). Scheduler → Order Service → Keycloak → Service Access Token → Inventory Service (token represents order-service, no customer).
- **Feign & service tokens (combined deck §63):** the earlier `FeignJwtInterceptor` propagated the incoming customer's JWT — correct when there is a user request (Customer → Gateway → Order → Inventory). For Scheduler → Order → Inventory there is no incoming user JWT, so: if a user token exists → propagate appropriate user context/token; otherwise → authenticate Order Service itself using Client Credentials.
- **Complete security architecture after Sessions 19–20 (combined deck §64):** Keycloak `ecommerce-platform` realm (users, clients, roles) with two paths: Authorization Code → Customer → API Gateway; Client Credentials → Order Service. Bearer JWT flows to Product/Order/Inventory Services.
- **Gateway (WebFlux) as Resource Server** and **sensitive services (Order Service) as Resource Servers** — two independent validation layers; the demo shows each layer returning 401 on its own.
- **User-context headers preserved but re-sourced:** earlier `JwtAuthFilter` manually parsed the JWT to set `X-User-Id` / `X-User-Role`; now Spring Security's validated `Jwt` is the source. A `UserContextEnrichmentFilter` (GlobalFilter, Ordered) uses `ReactiveSecurityContextHolder` → authentication principal → cast to `Jwt` → `X-User-Id = jwt.getSubject()`, order `Ordered.LOWEST_PRECEDENCE - 1`.
- **Header security warning (combined deck §56):** if downstream services trust X-User-Id/X-User-Role, clients must not be able to inject them. The Gateway should: (1) remove untrusted incoming identity headers, (2) authenticate the token, (3) generate the trusted headers itself, (4) forward them downstream; even better, downstream services should also have their own security boundary where appropriate.
- **Alternative architecture acknowledged (S19 part, relevant here):** the API Gateway does not have to be the OAuth2 client in every architecture — Browser obtains access token from Keycloak; Gateway validates Bearer token. "In Session 20, we will focus strongly on this Resource Server model."

## 4. Technologies

- **Keycloak** — Identity Provider / Authorization Server; the realm and clients from Session 19 (deck S20 flow references Keycloak realm `microservices-pro`; combined tutorial uses `ecommerce-platform` — discrepancy, see §7).
- **OAuth2 Client Credentials Flow** — service accounts, `grant_type=client_credentials`.
- **JWT** — access tokens; JWKS; RSA asymmetric signing; claims iss/sub/exp; audience validation mentioned.
- **Google OAuth2 / OIDC** — not mentioned; the only IdPs named: Keycloak (and Auth0 mentioned in Session 19's production note).
- **Spring Security OAuth2 Resource Server** — `spring-boot-starter-oauth2-resource-server`; `JwtAuthenticationConverter`; `ReactiveJwtAuthenticationConverterAdapter`; `SecurityWebFilterChain` (WebFlux, Gateway); `ServerHttpSecurity`; `authorizeExchange`, `oauth2ResourceServer(oauth2 -> oauth2.jwt(...))`; `Jwt` principal.
- **Spring Boot WebFlux / Spring Cloud Gateway** — `@EnableWebFluxSecurity` for the Gateway (NOT `@EnableWebSecurity`); GlobalFilter for UserContextEnrichmentFilter.
- **Spring MVC service side (Order Service)** — `@EnableWebSecurity` + `SecurityFilterChain` (servlet-style), `permitAll` for `/actuator/health`, `anyRequest().authenticated()`, `oauth2ResourceServer(jwt defaults)`.
- **JJWT (io.jsonwebtoken: jjwt-api / jjwt-impl / jjwt-jackson)** — the Session 3 dependencies to be DELETED.
- **OpenFeign** — FeignJwtInterceptor context (propagating tokens vs client credentials fallback).
- **Feign/caching concepts:** token caching, refresh 30 seconds before expiry, synchronous refresh to avoid token-refresh stampede.
- **Docker / Kubernetes secrets** — named as production secret storage (env vars, Docker secrets, Kubernetes Secrets, Vault, cloud secret managers).
- No numeric version numbers for these tools appear in the S20 deck (only the Keycloak image tag from the combined deck: `quay.io/keycloak/keycloak:26.7.3`; the S19 deck used `24.0`).

## 5. Important terminology

- Client Credentials Flow — service's own identity; no user/browser/redirect.
- Service account — the Keycloak-side identity for the `order-service` client.
- Service token vs customer token — "I am order-service" vs "I am customer1"; different security principals.
- JWKS — JSON Web Key Set; public keys published by Keycloak; discovered via issuer-uri.
- Asymmetric signing — private key only Keycloak; public key distributed to validators.
- issuer-uri — the configured trusted issuer; drives metadata + JWKS discovery; validated against the token's `iss`.
- iss vs aud — issuer ("who issued") vs audience ("who it is for"); audience validation is an additional production layer.
- Resource Server — validates tokens and serves protected resources.
- `keycloakRoleConverter()` — maps realm_access.roles → `ROLE_` + uppercase authorities (`ADMIN` → `ROLE_ADMIN`, `USER` → `ROLE_USER`).
- Defense in depth — Gateway validates first + Resource Server on sensitive services.
- Clean cutover vs parallel run — training platform uses clean cutover; production migration may weigh parallel-run.
- X-User-Id / X-User-Role — downstream user-context headers; source changes from manual parse to validated Jwt; must be stripped from untrusted incoming requests.
- Token caching / refresh before expiry / token refresh stampede — client-side service-token handling.
- FeignJwtInterceptor — propagates user JWT when present; Client Credentials fallback when absent.
- 401 vs 403 — authentication problem vs authenticated-but-not-authorized.
- Token revocation / refresh token rotation — "handled by Keycloak automatically" (deck scope boundary).
- KEYCLOAK_ADMIN vs KC_BOOTSTRAP_ADMIN_* — version-sensitive admin env vars (see §8).

## 6. Code concepts

- **Order Service (servlet, Spring MVC) as Resource Server (deck):**
  - Add dependency `spring-boot-starter-oauth2-resource-server` (no JJWT; security libs come transitively).
  - `SecurityConfig`: `@EnableWebSecurity` + `SecurityFilterChain` — `permitAll` for `/actuator/health`, `anyRequest().authenticated()`, `oauth2ResourceServer(jwt defaults)`.
  - `application.yml`: `issuer-uri: http://keycloak:8090/realms/microservices-pro` (deck) — auto-discovers JWKS; DELETE `jwt.secret`.
- **Gateway (WebFlux) as Resource Server:**
  - Same starter; **DELETE `JwtAuthFilter.java` and `JwtUtil.java` entirely** — "half-retired security code is a liability"; drop JJWT deps and `jwt.secret`.
  - Combined deck code: `@Configuration @EnableWebFluxSecurity` (explicitly NOT `@EnableWebSecurity` — "Our Gateway uses WebFlux"), `SecurityWebFilterChain` via `ServerHttpSecurity`: `.authorizeExchange(exchanges -> exchanges.pathMatchers(HttpMethod.GET, "/api/products").permitAll().pathMatchers("/api/admin/**").hasRole("ADMIN").anyExchange().authenticated()).oauth2ResourceServer(oauth2 -> oauth2.jwt(jwt -> jwt.jwtAuthenticationConverter(keycloakRoleConverter()))).build()`.
  - `keycloakRoleConverter()` (combined deck): returns `Converter<Jwt, Mono<AbstractAuthenticationToken>>` wrapping a `JwtAuthenticationConverter` whose `setJwtGrantedAuthoritiesConverter` reads claim `realm_access.roles` (null-safe; instanceof Collection check), maps each role string to `new SimpleGrantedAuthority("ROLE_" + role.toUpperCase())`, wrapped in `ReactiveJwtAuthenticationConverterAdapter`.
  - `UserContextEnrichmentFilter` (combined deck): `@Component implements GlobalFilter, Ordered`; `ReactiveSecurityContextHolder.getContext().map(ctx -> ctx.getAuthentication().getPrincipal()).cast(Jwt.class).map(jwt -> exchange.mutate().request(exchange.getRequest().mutate().header("X-User-Id", jwt.getSubject()).build()).build()).defaultIfEmpty(exchange).flatMap(chain::filter)`; `getOrder()` returns `Ordered.LOWEST_PRECEDENCE - 1`. "The important concept is not the exact filter code" — Spring Security validates identity → Gateway derives trusted user context → downstream request.
- **Service token client (combined deck §58–§60):** conceptual algorithm — `getToken()`: IF cached token still valid → return it; ELSE request new token from Keycloak (`grant_type=client_credentials`, client_id, client_secret), cache it, return. Cache and refresh shortly before expiration: `expiresAt = Instant.now().plusSeconds(expiresIn - 30)` (refresh 30 seconds before expiry); use appropriate synchronization to avoid a token refresh stampede.
- **Token request has NO username, NO password, NO redirect_uri, NO authorization code** — only grant_type=client_credentials + client_id + client_secret to `POST /realms/<realm>/protocol/openid-connect/token`.
- **Order-service Keycloak client setup:** Client ID `order-service`, Client authentication ON, enable the service-account/client-credentials capability appropriate to the Keycloak version; no interactive browser login flow needed; copy its client secret.
- **Demo commands (deck):** order-service 401 without token / 200 with token; gateway demo shows two independent layers both returning 401; client-credentials call with no user succeeds (acceptance criterion).
- **Expected HTTP results (combined deck):** no authentication → 401 Unauthorized; authenticated but insufficient role → 403 Forbidden; valid authN+authZ → 200 OK.

## 7. Configuration

- **Order Service application.yml (deck):** `spring.security.oauth2.resourceserver.jwt.issuer-uri: http://keycloak:8090/realms/microservices-pro` — DELETE `jwt.secret` after switching.
- **Combined tutorial application.yml:** `issuer-uri: http://localhost:8180/realms/ecommerce-platform` (Session 19 combined-deck Keycloak on port 8180, image 26.7.3). **DISCREPANCY between the two S20 PDFs:** deck realm `microservices-pro` on `keycloak:8090` vs tutorial realm `ecommerce-platform` and port `8180`/`localhost` — also inconsistent with the S19 deck's Keycloak on host `:8090`. The slides do not reconcile this; decide one URL scheme in the lab and use it consistently (issuer-uri must match `iss` EXACTLY: protocol/host/port/realm).
- **Docker networking rule:** when Gateway runs inside Compose, `localhost:8180` points at the Gateway container itself, not Keycloak — use the Compose service name (`keycloak:8080` internally) and carefully design external URL vs internal URL vs issuer configuration vs DNS/service names (this becomes especially important in production deployments and was repeated in the deck's common issues: "Unable to resolve issuer → Keycloak up BEFORE Gateway").
- **Keycloak client config for service accounts:** `order-service` client with Client authentication ON and service account enabled; the client secret goes into Order Service server-side config (env vars in production — never Git/browser).
- **Env-var naming is version-sensitive:** Keycloak 24.0 deck used `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`; combined deck's pinned 26.7.3 uses `KC_BOOTSTRAP_ADMIN_USERNAME` / `KC_BOOTSTRAP_ADMIN_PASSWORD`. Check image/version documentation (Common Mistake 1).
- **Scope/discovery config on the Keycloak side:** client scopes must include 'roles' (deck common issues: "roles missing → client scopes 'roles' + assignment") for realm_access.roles to appear.
- **Token lifetimes:** `expires_in = 300 seconds` example used for the caching/refresh strategy; production guidance: "appropriate token lifetimes, key rotation" (Professional Rule 10).
- **Secrets management:** classroom `client-secret: demo-secret` acceptable only for demo; production → environment variables, Docker secrets, Kubernetes Secrets, Vault, cloud secret managers.

## 8. Failure scenarios

Deck "5 Things That Will Go Wrong Today":

- **"Unable to resolve issuer" / connection failure** → Keycloak must be up BEFORE Gateway (bring it up first).
- **401 after cutover** → `issuer-uri` must match the token's `iss` EXACTLY — protocol, host, port, realm (see the discrepancy in §7; Docker internal vs external URL issue).
- **Roles missing from authorities** → ensure the client scopes include 'roles' AND the user actually has role assignments.
- **Client Credentials call rejected by Inventory** → Inventory must trust the same issuer (same Keycloak realm in its own issuer-uri/trust configuration).
- **New token requested on every call** → implement expiry caching and persist the token until shortly before expiry (refresh 30s before expiry; watch for refresh stampede).

Combined-deck common mistakes (8):

- KEYCLOAK_ADMIN with a current Keycloak image without checking version docs — container configuration is version-sensitive (KEYCLOAK_ADMIN vs KC_BOOTSTRAP_ADMIN_*).
- Using `localhost` inside Docker — from another container it is that container itself; use `keycloak:8080` inside the Compose network.
- Issuer URI vs Docker — Gateway inside Docker resolving `http://localhost:8180` hits itself; design external/internal URL, issuer config, DNS/service names carefully.
- Trusting the ID token as an API token — the access token is intended for API authorization; the ID token is an OIDC identity artifact for the client.
- Keeping the old JwtAuthFilter after configuring Resource Server — do not leave two competing JWT validation mechanisms.
- Sharing the client secret — never in JavaScript, HTML, mobile source, Git, public configuration.
- Hardcoding secrets (`client-secret: demo-secret`) — classroom-only; use secure secret storage in production.
- "JWT means secure" — JWT is a token format; security depends on who issued it, signature verified, issuer trusted, expiration, intended audience, user authorization, secret protection, key rotation.
- Also: audience — "Do not confuse iss with aud"; and do not perform the token exchange client-side where the secret would be exposed.

## 9. Trade-offs

- **Authorization Code vs Client Credentials:** human interaction vs machine identity; user token vs service token — "A user's token and a service's token represent different security principals" (Professional Rule 6).
- **Shared HMAC secret vs asymmetric/JWKS:** old model required every verifier to know the secret (and anyone with it could forge); new model distributes only the public key — "The Gateway never receives Keycloak's private signing key." Rotation/distribution becomes operationally tractable.
- **Clean cutover vs parallel run:** controlled training platform → clean cutover (delete JwtAuthFilter/JwtUtil/JJWT/jwt.secret; "half-retired security code is a liability"); a real production migration with existing clients and tokens may warrant a temporary parallel-run strategy — echoes the S24 clinic question about this same decision.
- **Validate at Gateway vs at every service:** Gateway-first keeps one policy point; adding Resource Server on sensitive services = defense in depth. Two layers mean two 401 sources to understand — the demo shows both independently.
- **Where the Gateway sits / who is the OAuth2 client:** BFF-style confidential client (course) vs Browser obtaining tokens and Gateway only validating — the S19 deck notes the Gateway doesn't have to be the client in every architecture; S20 leans into the Resource Server model.
- **Issuer-only validation vs issuer + audience:** audience validation ("Who is this token intended for?") is an additional protection layer supported by Spring Security; the course configures the issuer.
- **Token caching trade-off:** caching avoids per-call token requests but introduces expiry management, refresh timing (30s before expiry) and stampede risk; no caching multiplies latency and load on Keycloak.
- **Propagate user token vs service token in Feign:** propagate when a user request exists; Client Credentials when it doesn't — "This distinction is essential."
- **401 vs 403 semantics:** 401 = authentication problem; 403 = authenticated but not authorized — important for correct API behavior and tests.

## 10. Common mistakes

- Leaving JwtAuthFilter/JwtUtil/JJWT/jwt.secret in place after Resource Server cutover ("half-retired security code is a liability"; "Do not leave two competing JWT validation mechanisms").
- Configuring the wrong security adapter: `@EnableWebSecurity` on the WebFlux Gateway instead of `@EnableWebFluxSecurity` (and `SecurityWebFilterChain` instead of the servlet `SecurityFilterChain`).
- issuer-uri not matching `iss` exactly (protocol/host/port/realm) → 401s after cutover; using `localhost` where the Compose service name is needed.
- Starting the Gateway before Keycloak ("Unable to resolve issuer" at startup).
- Missing 'roles' client scope or no role assignment → no realm_access.roles → no ROLE_* authorities.
- Rejecting Client Credentials calls because Inventory doesn't trust the same issuer.
- Obtaining a new service token on every call; ignoring refresh stampede; refreshing at the exact expiry second instead of 30s before.
- Using the ID token as the API bearer token.
- Forwarding client-injected X-User-Id/X-User-Role headers instead of stripping + regenerating them; assuming header trust makes downstream services safe.
- Exposing/committing the client secret; hardcoding secrets; believing "JWT means secure"; ignoring audience; confusing iss with aud.
- Migration assumption: expecting a clean cutover to be risk-free in production without a parallel-run plan.

## 11. Interview questions

- What is the Client Credentials Flow and when is it used? (Machine-to-machine; no user; client acts as itself; nightly scheduler → Order → Inventory example.)
- Who does a Client Credentials access token represent? (The service itself — `sub = order-service`, not customer1.)
- What is JWKS and why is it better than a shared secret? (JSON Web Key Set of public keys; verifiers only need the public key; the private signing key never leaves Keycloak.)
- Why configure issuer-uri? (Discover metadata/JWKS automatically; verify the token came from the trusted issuer — valid signature + trusted issuer + valid timestamps = acceptable.)
- Issuer vs audience? (Who issued it vs who it is intended for; audience is an extra production protection layer.)
- Why remove JwtAuthFilter after migrating to Spring Security Resource Server? (Avoid two competing validation mechanisms/complexity; clean cutover; production may parallel-run temporarily.)
- Authentication vs authorization, and 401 vs 403? (Who are you / what may you do; 401 = not authenticated, 403 = authenticated but not authorized.)
- Why does the Gateway use `@EnableWebFluxSecurity` while Order Service uses `@EnableWebSecurity`? (WebFlux reactive stack — SecurityWebFilterChain/ServerHttpSecurity vs servlet stack.)
- How do Keycloak roles become Spring authorities? (realm_access.roles → ROLE_ + uppercase via converter; hasRole("ADMIN") checks ROLE_ADMIN.)
- How should the Gateway handle X-User-Id/X-User-Role? (Strip untrusted incoming identity headers, authenticate, generate trusted headers from the validated Jwt, forward; downstream should still have its own boundary.)
- Why not call Keycloak for a new token on every request? (Latency/load; cache and refresh ~30s before expiry; avoid stampede with synchronization.)
- What does the service do when there is no user token in a Feign chain? (Client Credentials fallback; otherwise propagate the user token.)
- How does this fit the "why not keep both" question? (Complexity/inconsistent behavior vs controlled migration strategy.)
- What is defense in depth here? (Gateway validates first + sensitive services are Resource Servers themselves.)

## 12. What I must memorize

- Authorization Code = client acts on behalf of a user; Client Credentials = client acts as itself. No user, no browser, no redirect.
- Client Credentials token request: `POST /realms/<realm>/protocol/openid-connect/token` with `grant_type=client_credentials` + client_id + client_secret — NO username, NO password, NO redirect_uri, NO code.
- `sub` for Client Credentials = the service/client identity ("I am order-service").
- JWKS = JSON Web Key Set; endpoint `/realms/<realm>/protocol/openid-connect/certs`; discovered via issuer-uri.
- Asymmetric rule: private key ONLY Keycloak; public key distributed to validators.
- Acceptability: valid signature + trusted issuer + valid timestamps = acceptable token.
- iss = who issued (Keycloak); aud = who it is for (my-api); don't confuse them.
- The dependency: `spring-boot-starter-oauth2-resource-server`; config `issuer-uri`.
- Gateway WebFlux: `@EnableWebFluxSecurity` + `SecurityWebFilterChain`; servlet services: `@EnableWebSecurity` + `SecurityFilterChain`.
- DELETE list: JwtAuthFilter.java, JwtUtil.java, JJWT deps (jjwt-api/impl/jackson), jwt.secret.
- `keycloakRoleConverter`: realm_access.roles → ROLE_ + uppercase; hasRole("ADMIN") → ROLE_ADMIN.
- 401 = authentication problem; 403 = authenticated but not authorized.
- Token caching: reuse while valid, refresh 30 seconds before expiry; avoid refresh stampede (synchronization); `expiresAt = Instant.now().plusSeconds(expiresIn - 30)`.
- Feign rule: propagate user token if present; otherwise Client Credentials.
- Header rule: strip untrusted incoming X-User-Id/X-User-Role; generate from the validated Jwt; downstream keeps its own boundary.
- Exact commit message (deck WRAP-UP): `session-20: retire-jwtauthfilter-add-oauth2-resource-server-and-client-credentials`.
- Pre-Session 21 reading: Service Mesh fundamentals + Istio, with 3 knowledge-check questions (why a sidecar proxy; mTLS vs HTTPS TLS; mesh-level resilience vs Resilience4j from S4).

## 13. What I must understand

- Why a service needs its own identity (no user in scheduled flows) and why that identity is a different security principal from a user token.
- Why asymmetric signing + JWKS is operationally superior: the private key never leaves Keycloak; verifiers get public keys; key rotation is feasible.
- Why issuer validation alone is not enough in the abstract (an attacker's own token can have a valid signature) — and why audience validation is an additional production layer.
- How Spring Security's Resource Server plugin performs validation (decode + verify JWT, discover metadata via issuer-uri) so no hand-written filter is needed; why `@EnableWebFluxSecurity` for the reactive Gateway vs `@EnableWebSecurity` for servlet services.
- Why the role converter exists (Keycloak realm roles are not Spring authorities) and where the 'roles' scope matters.
- Why the old filter must die (two competing mechanisms; inconsistent security behavior) and when production would instead parallel-run.
- Why header enrichment survives architecture-wise but its source changes (validated Jwt), and the trust rules for those headers.
- Why token caching + pre-expiry refresh is engineering (stampede, synchronization, persistence between restarts implied by "expiry-caching persist" acceptance item).
- Why 401 and 403 are distinct results worth testing and naming.
- The definition of done: the platform now has two layers of real token validation and a machine identity path.

## 14. What I should implement from memory

- Order Service: add the Resource Server starter; write `SecurityConfig` (`@EnableWebSecurity`, `SecurityFilterChain`: `/actuator/health` permitAll, `anyRequest().authenticated()`, `oauth2ResourceServer(jwt defaults)`); configure `issuer-uri`; delete `jwt.secret`.
- Gateway: switch to `@EnableWebFluxSecurity` + `SecurityWebFilterChain` (`GET /api/products` permitAll, `/api/admin/**` hasRole ADMIN, anyExchange authenticated, oauth2ResourceServer jwt with the Keycloak role converter); write `keycloakRoleConverter()` (realm_access.roles → `ROLE_` + uppercase, reactive adapter) and `UserContextEnrichmentFilter` (GlobalFilter; ReactiveSecurityContextHolder; cast Jwt; X-User-Id from `jwt.getSubject()`; order LOWEST_PRECEDENCE-1);
- Gateway cleanup: delete `JwtAuthFilter.java`, `JwtUtil.java`, JJWT dependencies, `jwt.secret`.
- Keycloak: create the `order-service` client (Client authentication ON, service account enabled), copy the secret into server-side config.
- Service token client: `getToken()` with caching + refresh 30s before expiry (+ synchronization against stampede).
- Feign: propagate customer JWT when present; fall back to Client Credentials when there is no user.
- Tests/demos: 401 without token; 200 with customer token on protected route; X-User-Id/X-User-Role still arrive (now from the real JWT); Client Credentials call succeeds with no user; customer 403 on ADMIN route vs admin 200.
- Commit with the exact message: `session-20: retire-jwtauthfilter-add-oauth2-resource-server-and-client-credentials`.

## 15. Relationship to previous sessions

- **Session 3 is being retired:** the custom `JwtAuthFilter`, `JwtUtil`, JJWT dependencies (`jjwt-api/impl/jackson`) and `jwt.secret` all come from Session 3 and are DELETED today. The S20 deck's before/after table is literally the before/after of Session 3's security.
- **Session 19 (previous session):** provided the IdP, realm, `gateway` client + secret (needed "for Session 20"), `customer1` user; the BONUS admin role/user previews today's role-based access. Deck slide 2 recap: "Session 19 answers the question Session 3 deliberately left open"; S20 completes the swap.
- **Session 4 (Resilience4j context):** referenced in the Pre-Session 21 reading question — "mesh-level resilience vs Resilience4j from S4".
- **Earlier Feign sessions:** `FeignJwtInterceptor` propagated the incoming customer JWT — today's extension adds the no-user Client Credentials fallback.
- **Session 17/18 (platform context):** tracker segments (Observability, CQRS) unchanged; security segment completed today.
- The two-layer decision (Gateway + Resource Server on sensitive services) formally closes the "trust the boundary" arc started in Session 3 (services trust the Gateway) and continued in Session 19 (the Gateway trusts Keycloak).

## 16. Relationship to future sessions

- **Session 21 = Service Mesh (next):** WRAP-UP DEFINITION OF DONE includes PRE-SESSION 21 READING: Service Mesh fundamentals + Istio, with 3 knowledge check questions: (1) why a sidecar proxy approach, (2) mTLS vs HTTPS/TLS, (3) mesh-level resilience vs Resilience4j from S4. Monday (next after this session) at 3:00–5:30 PM per deck rhythm.
- The security stack built in Sessions 19–20 (Keycloak + OAuth2/OIDC + Resource Server + role-based authorization) is part of the Phase 3 platform that later sessions and the Phase 4 capstone inherit (per Session 24's clinic: security stack inherited as-is).
- Token revocation / refresh rotation explicitly left to Keycloak ("handled automatically — scope boundary") — a deferred production concern (Professional Rule 10: logout/revocation strategy for production).
- The issuer-vs-audience point and key rotation remain production hardening topics (audience validation "in production architectures").

## 17. Lab relationship

Exact lab/commit/homework content as stated in the slides:

- **LAB 16 (deck):** timing — wire Gateway as Resource Server / **12 min**; preserve X-User-Id/X-User-Role header enrichment / **5 min**; Client Credentials Order→Inventory / **10 min**; + **3 min** + homework role-based route + unit tests.
- **Lab 16 acceptance criteria (deck, 6):** filter/util gone; GET /api/products with no token returns 200; customer token authenticates a protected route; X-User-Id/X-User-Role headers still arrive (derived from the real JWT); client credentials call with no user succeeds; customer 403 vs admin 200 on an ADMIN route.
- **Demos (deck):** Order Service 401 without token → 200 with token; gateway demo of two independent layers both returning 401; refresh token rotation handled by Keycloak automatically (scope boundary note).
- **WRAP-UP / Definition of Done (deck):** the DEFINITION OF DONE list + PRE-SESSION 21 READING (Service Mesh fundamentals + Istio; 3 knowledge check questions as in §16).
- **EXACT commit message (deck):** `session-20: retire-jwtauthfilter-add-oauth2-resource-server-and-client-credentials`.
- **Practical labs 12 (combined tutorial):** Labs 1–5 belong to Session 19 (Keycloak/realm/gateway client/customer/Authorization Code); Labs 6–12 here: Lab 6 — Configure Resource Server (starter dependency + issuer-uri); Lab 7 — Remove Old Security (JwtAuthFilter, JwtUtil, JJWT dependencies, jwt.secret); Lab 8 — Add Role-Based Authorization (`/api/products` public; `/api/admin/**` ADMIN only); Lab 9 — Test USER as customer1 on `/api/admin/...` → expected 403 Forbidden; Lab 10 — Test ADMIN (create administrator, assign ADMIN, login, same endpoint → 200 OK); Lab 11 — Client Credentials (create `order-service`, configure service account, request grant_type=client_credentials, inspect token — confirm it represents order-service, not customer1); Lab 12 — Service-to-Service Call (Order Service → Inventory Service using `Authorization: Bearer <service-token>`; verify Inventory accepts it).
- **Testing checklist (combined deck) relevant here:** Resource Server — dependency exists; issuer-uri configured; JwtAuthFilter removed; JwtUtil removed; old JJWT dependencies removed; jwt.secret removed. Authorization — public product endpoint works; authenticated endpoint rejects missing token; USER cannot access ADMIN endpoint; ADMIN can access ADMIN endpoint. Client Credentials — order-service client exists; service account enabled; client credentials token can be obtained; token represents order-service; service can call Inventory.
- **Knowledge check (combined deck, 15 Q):** including why S3 JWT was insufficient; Keycloak's responsibility; Authorization vs Resource Server; why redirects; why no client secret in browsers; PKCE; access vs ID token; iss; sub; JWKS; why asymmetric is operationally better; authentication vs authorization; why Client Credentials needs no browser; who the CC token represents; why remove JwtAuthFilter.
- **Professional engineering rules (combined deck, 10):** never hardcode production secrets; never put confidential client secrets in browser apps; don't implement your own JWT validation when a mature framework can; validate signature/issuer/expiration (+audience where appropriate); authentication ≠ authorization; user token ≠ service token; don't trust client-supplied identity headers; understand localhost vs service-name in Docker; keep Keycloak version-pinned; production needs secure secret storage, HTTPS, token lifetimes, key rotation, logging, monitoring, logout/revocation strategy.
- **Session completion checklist (combined deck):** Keycloak running in Docker; ecommerce-platform realm; gateway client; customer; Authorization Code Flow understood; access token inspected; ID token understood; Client Credentials understood; order-service client; service token obtained; JWKS understood; Spring Resource Server configured; issuer-uri configured; JwtAuthFilter/JwtUtil/JJWT removed; Keycloak roles mapped; USER route tested; ADMIN route tested; 401 vs 403 understood; service-to-service authentication tested.
- **Checkpoint commits in slides:** only the single exact commit message above appears; no other checkpoint naming shown.
