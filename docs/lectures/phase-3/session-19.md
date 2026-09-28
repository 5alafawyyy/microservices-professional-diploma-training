# Session 19 — Security Part 1: Keycloak & OAuth2 (Identity Provider • Authorization Code Flow • Realms, Clients, Users)

Source files: `Session_19_Security_Part1.pdf` (24-page slide deck), `Sessions_19_20_Keycloak & OAuth2 Security.pdf` (71-page combined student tutorial — Part A covers Session 19; Part B covers Session 20 and is written up in `session-20.md`). File check: the two PDFs differ in size and packaging — the deck is the instructor presentation (Session 19 of 29, "Wednesday 3:00–5:30 PM, Online"), the tutorial is the combined self-contained study document. Both were read; differences between them are noted inline (most importantly the Keycloak image version/port and env-var naming — see §7).

## 1. Why this topic exists

- **Session 19 answers the question Session 3 deliberately left open: where do real, trustworthy tokens actually come from?** Session 3 built `JwtAuthFilter` — it validated a JWT signature using a shared secret hardcoded in application.yml — and even left a production note: "In a real system, Keycloak or Auth0 issues the tokens. The Gateway only validates — it does not issue tokens. We cover the full OAuth2 flow in a later session." Today is that session — for the human-login half of the story.
- **3 Questions Session 3's security cannot answer:**
  1. Where do real customers create accounts and set passwords? There is no signup form — only test tokens generated with a Java snippet.
  2. A customer forgets their password — what happens? Nothing — no reset flow was built, because there is no real user store.
  3. A customer's laptop is stolen with an active session — can you revoke JUST their token? No — `JwtAuthFilter` only checks a signature and an expiry timestamp; it has no concept of "this specific token is now invalid."
- **The conceptual shift — from shared secret to trusted issuer:** Session 3 = trust because I know the secret (anyone with the secret can forge a valid token); Session 19 = trust because I trust the issuer (the Gateway trusts tokens signed by Keycloak, a real Identity Provider; complexity of authentication lives in ONE place). This is the same "trust the boundary" principle from Session 3's Gateway-as-trust-boundary lesson — one layer further out: Session 3: services trust the Gateway; today: the Gateway trusts Keycloak.
- Combined deck's framing: replace the hand-written security mechanism with a real Identity Provider (Keycloak); the Gateway no longer needs to know how the password was checked, where the user was created, how password reset works, or whether MFA was used — it only trusts tokens issued by Keycloak.
- **Explicit scope boundary (deck, OBG-001):** today covers human login only (Authorization Code Flow). Session 20 covers service-to-service authentication (Client Credentials) and wiring the Gateway as a real OAuth2 Resource Server. If a machine-to-machine question comes up today, the honest answer is: "great question — that's next session."

## 2. Core concepts

- **Identity Provider (IdP):** a system whose entire job is proving "this really is who they claim to be" and issuing a signed, trustworthy statement of that fact (the token). Everyone else — Gateway, services — trusts tokens signed by the IdP without needing to know HOW the user authenticated (password? social login? multi-factor?). That complexity lives in ONE place: Keycloak.
- **OAuth2 four roles (deck table):** Resource Owner = the customer using the E-Commerce app (owns the data/account; grants or denies access); Client = the API Gateway (requests access on the Resource Owner's behalf); Authorization Server = Keycloak (authenticates the Resource Owner; issues tokens); Resource Server = Order/Product Service via Gateway (accepts tokens; serves protected resources).
- **Keycloak:** open-source Identity and Access Management platform; in this course it is the Identity Provider + Authorization Server + OpenID Connect Provider. Conceptually manages users, passwords, roles, groups, authentication, login, token issuance, Single Sign-On, MFA.
- **Realm:** an isolated security domain in Keycloak — each realm holds its own independent set of users, clients, and roles; two realms never share user accounts or configuration. Ours: `ecommerce-platform`. Never put application users in the `master` realm (used only for Keycloak's own admin).
- **Authorization Code Flow (5 steps, deck):** (1) Customer clicks "Login" in the app. (2) Browser redirected to Keycloak's login page. (3) Customer authenticates DIRECTLY — Client never sees the password. (4) Browser redirected back with a short-lived code. (5) Server-side exchange: code → access_token + id_token + refresh_token. Key message: steps 2–4 happen entirely through browser redirects — the Client application code is not involved until step 5.
- **Why redirects — not a direct API call?** The customer's password is typed only into Keycloak's own page, never into our Gateway or any of our code. If the Client collected the password and sent it via API call, the Client would have full access to raw credentials — a much larger attack surface, and it defeats the purpose of centralizing identity in one trusted place. The core security property: **the Client only ever receives a short-lived authorization code — never the password, never the raw credentials.**
- **Flow selection:** User logs in, human interaction? → Authorization Code (today). Service-to-service, no user? → Client Credentials (Session 20). Mobile/SPA app? → Authorization Code + PKCE. Backend API called by another service? → Client Credentials (Session 20). Today builds ONLY the human-login half.
- **Public vs Confidential clients:** server-side app that can safely store a secret (our Gateway) = Confidential Client — has a client_secret; SPA/mobile app whose code is visible to the end user = Public Client — no secret, use PKCE instead. Strongest guarantee that only the real Client exchanges a code = Confidential Client + client_secret. Our platform: the API Gateway is a Confidential Client — it runs entirely server-side and can safely hold a client_secret.
- **PKCE (combined deck):** Proof Key for Code Exchange — protects the authorization-code exchange against code interception. Simplified idea: Client sends `code_challenge` → Authorization Server returns authorization code → Client sends `code + code_verifier` → server verifies that the client that started the flow is the one completing it. For modern browser/mobile apps, Public Client + PKCE is the normal approach.
- **OAuth2 vs OpenID Connect:** OAuth2 = authorization; OIDC = authentication/identity on top of OAuth2. Our login scenario is better described as: OAuth 2.0 Authorization Code Flow + OpenID Connect.
- **Access Token vs ID Token (combined deck, "extremely important"):** Access Token is used to access protected APIs (`Authorization: Bearer <access-token>` to the Resource Server) — the API should care primarily about the access token. ID Token belongs to OpenID Connect and provides information about the authenticated user to the client (user ID, username, authentication information). "Do not teach students that an ID Token is simply another API access token."
- **Trust-the-issuer improvement (combined deck):** before — "I trust this JWT because I know the signing secret"; after — "I trust this JWT because it was issued by my trusted Identity Provider." This is the key architectural lesson.

## 3. Architecture

- **Before (Session 3):** Client → JWT → API Gateway → verify signature (JwtAuthFilter; the Gateway knew the shared secret, e.g. `jwt.secret: microservices-pro-course-secret-key-2024-minimum-256-bits`) → trusted request → Microservice.
- **After (Session 19 target architecture):** Customer → username/password → Keycloak (users, passwords, roles, token issuing, authentication) → signed JWT (OAuth2/OIDC) → API Gateway (authentication, authorization, routing) → Product Service / Order Service / Inventory Service. The Gateway only validates; it does not issue tokens.
- **Authorization Code Flow sequence (deck slide 8):** Customer → Client ("Login" click); Client → Keycloak (browser redirect to login page); Customer → Keycloak (authenticates DIRECTLY; Client never sees the password); Keycloak → Client (browser redirected back with short-lived code); Client → Keycloak (server-side exchange: code → access_token + id_token + refresh_token).
- **Detailed flow (combined deck §12):** Step 1 user clicks Login → Step 2 browser redirected to `GET /realms/ecommerce-platform/protocol/openid-connect/auth` with `client_id=gateway`, `redirect_uri=http://localhost:8080/login/oauth2/code/keycloak`, `response_type=code`, `scope=openid` → Step 3 Keycloak displays login (username/password submitted to Keycloak; Gateway does not receive the password) → Step 4 Keycloak authenticates customer1 → Step 5 redirect to `http://localhost:8080/login/oauth2/code/keycloak?code=abc123` (code is short-lived, temporary, intended to be exchanged) → Step 6 server-side `POST /realms/ecommerce-platform/protocol/openid-connect/token` with grant_type=authorization_code, client_id, client_secret, code, redirect_uri → Step 7 response contains `access_token`, `id_token`, `refresh_token`, `expires_in`. The client secret must never be exposed to the browser.
- **Alternative architecture noted (combined deck §17):** "The API Gateway does not have to be the OAuth2 Client in every architecture." Another model: Browser → obtains access token from Keycloak → API Gateway validates Bearer token → Microservices. Session 20 focuses strongly on this Resource Server model. For this course, a server-side Gateway/BFF-style example is used so students understand a confidential client.
- **Where the platform stands after today (deck slide 21):** Platform infra: Keycloak container added. Realm `ecommerce-platform` with Gateway (Confidential) client and test customer user. **No service code changes yet — Gateway still runs Session 3's JwtAuthFilter until Session 20.** The 8-segment tracker shows "Keycloak IdP — NEW"; Gateway still shows JwtAuthFilter active — "Keycloak IdP is standing by, not yet wired to the Gateway. Session 20 completes the swap."

## 4. Technologies

- **Keycloak** — open-source Identity and Access Management platform; runs via Docker; image explicitly named in the deck: `quay.io/keycloak/keycloak:24.0` (combined deck instead shows `quay.io/keycloak/keycloak:26.7.3` and instructs: "For course reproducibility, pin the Keycloak image version rather than using `latest`").
- **Docker / docker-compose** — Keycloak as a new compose service on `platform-net`; `docker compose up -d keycloak`.
- **OAuth2** — Authorization Code Flow (today); Client Credentials (Session 20); roles (Resource Owner/Client/Authorization Server/Resource Server); Public vs Confidential clients; PKCE mentioned.
- **OpenID Connect (OIDC)** — identity layer on top of OAuth2; ID token; the Keycloak client is the "OpenID Connect Provider" role.
- **JWT** — inspected on jwt.io; header.payload.signature (`xxxxx.yyyyy.zzzzz`); claims iss, sub, exp, iat, realm_access.roles.
- **Postman and curl** — for the manual token exchange.
- **Spring Boot / Gateway (context)** — no code changes today; Gateway is the OAuth2 Client/Confidential Client conceptually; its Session 3 JwtAuthFilter remains until Session 20.
- The deck compares signing: Session 3 shared HMAC secret vs Session 19 "Keycloak's private key (RSA) — Session 20 covers verification".
- No other version numbers are given in the S19 PDFs.

## 5. Important terminology

- Resource Owner / Client / Authorization Server / Resource Server — the four OAuth2 roles (mapped to customer / Gateway / Keycloak / Order-Product services via Gateway).
- Identity Provider (IdP) — trusted system that authenticates and issues signed tokens; complexity of authentication lives there.
- Realm — isolated space of users, clients, roles; `ecommerce-platform` for the platform; `master` is for Keycloak's own admin only.
- Client (in Keycloak) — a registered application allowed to use Keycloak (here: `gateway`).
- Client ID / Client Secret — confidential client credentials; secret regenerates if "Regenerate" is clicked; needed for token exchange in step 5 and Session 20.
- Authorization Code — short-lived, temporary code exchanged for tokens; the Client never receives the password.
- Authorization endpoint — `/realms/<realm>/protocol/openid-connect/auth`.
- Token endpoint — `/realms/<realm>/protocol/openid-connect/token`.
- Access token / ID token / refresh token — the three tokens returned; `expires_in` their lifetime.
- Public vs Confidential client; PKCE (code_challenge / code_verifier).
- Standard flow = the Authorization Code Flow (name used in the Keycloak client config).
- Valid Redirect URIs — must exactly match (including trailing slashes).
- Temporary password toggle — must be OFF for smoother demo.
- realm_access.roles — user's assigned Keycloak realm roles inside the token.
- iss — issuer's URL (Keycloak realm URL) — the very thing that lets the Gateway trust WHO signed it.
- sub — the user ID; exp — expiration; iat — issued at.
- BONUS preview: `admin` role + separate admin user to preview Session 20's role-based access.

## 6. Code concepts

No application/service code is written today. The concrete "code-ish" artifacts in the slides:

- **docker-compose service for Keycloak (deck version):**
  ```yaml
  keycloak:
    image: quay.io/keycloak/keycloak:24.0
    command: start-dev
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin   # DEV ONLY -- never a real password in prod
    ports: ["8090:8080"]                # 8090 host -- avoids clashing with existing services
    networks: [platform-net]
  ```
  Combined-deck variant (DISCREPANCY — different version, port and env-var names): image `quay.io/keycloak/keycloak:26.7.3`, `command: start-dev`, `KC_BOOTSTRAP_ADMIN_USERNAME: admin`, `KC_BOOTSTRAP_ADMIN_PASSWORD: admin`, ports `8180:8080`, networks `platform-net`. The combined deck warns explicitly: "Never use admin/admin in production" and later (Common Mistake 1) "KEYCLOAK_ADMIN with a current Keycloak image" — "Keycloak container configuration is version-sensitive."
- **Keycloak administration steps (console, not code):** create realm `ecommerce-platform`; create client `gateway` with Client authentication ON (makes it CONFIDENTIAL), Standard flow (this IS the Authorization Code Flow), Valid redirect URIs `http://localhost:8080/login/oauth2/code/keycloak`, then Credentials tab → copy Client Secret; create user `customer1` (email customer1@example.com), Credentials tab → set password with 'Temporary' toggle OFF; BONUS at home: create an `admin` role + separate admin user.
- **Manual flow commands (curl/Postman):**
  - Authorization URL: `http://localhost:8090/realms/ecommerce-platform/protocol/openid-connect/auth?client_id=gateway&redirect_uri=http://localhost:8080/login/oauth2/code/keycloak&response_type=code&scope=openid` (combined deck uses :8180).
  - Token exchange: `curl -X POST http://localhost:8090/realms/ecommerce-platform/protocol/openid-connect/token -d 'grant_type=authorization_code' -d 'client_id=gateway' -d 'client_secret=<paste-from-Credentials>' -d 'code=<paste-from-redirect>' -d 'redirect_uri=http://localhost:8080/login/oauth2/code/keycloak'` → Response: access_token, id_token, refresh_token, expires_in.
- **JWT inspection:** paste the access_token into jwt.io; header.payload.signature; inspect iss (issuer URL), sub (user ID), realm_access.roles, exp; server-to-server character of the exchange (Browser --code--> Application --server-to-server--> Keycloak).
- **Comparison table — Session 3 hand-signed JWT vs Keycloak JWT:** sub: hardcoded test value → real user ID; role: manually inserted → realm_access.roles assigned in Admin Console; iss: does not exist → Keycloak's realm URL (enables trust-the-issuer); signing key: shared HMAC secret → Keycloak's private key (RSA, Session 20 covers verification).

## 7. Configuration

- docker-compose additions as above; `docker compose up -d keycloak`; verify Admin Console at `http://localhost:8090` (deck) / `http://localhost:8180` (combined deck); login admin/admin (dev only).
- Realm `ecommerce-platform`; client `gateway` (confidential, standard flow, redirect URI `http://localhost:8080/login/oauth2/code/keycloak`); user `customer1` with non-temporary password.
- Keycloak dev-mode image can take 30–60s to fully start (common issues table).
- **Discrepancy to carry forward for Session 20 wiring:** deck uses Keycloak on host port 8090 with image 24.0 — and Session 20's deck configures `issuer-uri` pointing at the Keycloak realm accordingly; the combined tutorial uses host port 8180 with image 26.7.3 and `issuer-uri: http://localhost:8180/realms/ecommerce-platform` — which is then contradicted again by the S20 deck's other realm name (`microservices-pro`, port 8090). The slides do not reconcile this; pick one URL scheme for the lab and keep it consistent (see `session-20.md` §7/§8).
- No application.yml changes for services today (Gateway still uses the Session 3 configuration, `jwt.secret` included, until Session 20).
- Never place client_secret in JavaScript/HTML/mobile source/Git/public configuration; hardcoded secrets are acceptable only for classroom demonstration.
- Combined deck instructs: use strong passwords, do not share credentials, enable password policies, consider MFA in production; pin the Keycloak image version.

## 8. Failure scenarios

Deck "5 Things That Will Go Wrong Today":

- **"Invalid redirect_uri" error from Keycloak** → must EXACTLY match a Valid Redirect URI on the Client (including trailing slashes). Copy-paste, don't retype.
- **Token exchange returns 401 invalid_client** → verify client_secret was copied correctly — it regenerates if 'Regenerate' is clicked by accident.
- **Login page shows but credentials are rejected** → verify the user's password was set with 'Temporary' toggled OFF.
- **Cannot reach Keycloak Admin Console at all** → Keycloak dev-mode image can take 30–60s to fully start — wait and retry.
- **Token exchange succeeds but no realm_access.roles** → roles must be explicitly assigned to the user — a freshly created user has none by default.

Combined-deck additional pitfalls relevant to this part:

- **Keycloak container configuration is version-sensitive** — e.g., using `KEYCLOAK_ADMIN` with a current image without checking docs (the 26.x image uses `KC_BOOTSTRAP_ADMIN_*`) — Misconfiguration at startup.
- **localhost inside Docker** — if the Gateway later runs in another container, `localhost:8180` does not mean Keycloak; use the Compose service name (`keycloak:8080`) when both are inside the Compose network (formalized in Session 20's issuer-URI failure).
- **Client secret exposure** — the secret must never reach the browser; the exchange is server-to-server. A stolen access token (e.g., stolen laptop scenario) is exactly what the IdP/central session management is there to eventually address — Session 3's filter "only checks a signature and an expiry timestamp".

## 9. Trade-offs

- **Shared HMAC secret vs trusted issuer:** Session 3 — anyone with the secret can forge valid tokens; every validator must know the secret. Session 19 — trust because you trust WHO signed; Keycloak later verifies via RSA public keys (Session 20), private key stays only with Keycloak. Complexity moves to ONE place (Keycloak): password checks, user creation, password reset, MFA — the Gateway doesn't need to know any of it.
- **Redirects vs direct API call:** redirects are deliberate — the password is typed only into Keycloak's page; collecting the password client-side gives the Client full access to raw credentials (larger attack surface, defeats centralizing identity).
- **Confidential vs Public client + PKCE:** the Gateway (server-side) can hold a client_secret — Confidential; SPA/mobile cannot keep a secret — Public + PKCE. "The API Gateway does not have to be the OAuth2 Client in every architecture" — an alternative is the Browser obtaining tokens and the Gateway only validating Bearer tokens (Session 20's Resource Server model).
- **Access Token vs ID Token:** use the access token for APIs; the ID token is an OIDC identity artifact for the client — treating it as an API token is a mistake.
- **Scope discipline:** today = human login only; Client Credentials deferred to Session 20 — a deliberate split so each half is learned properly.
- **Training vs production security:** admin/admin dev credentials and hardcoded demo secrets are acceptable in class only; production needs env vars / Docker secrets / Kubernetes Secrets / Vault / cloud secret managers, HTTPS, key rotation, etc. (combined deck).

## 10. Common mistakes

- Believing Session 3's hand-rolled JWT is a production identity system (no signup/login UI, no password store/reset, no per-token revocation, shared secret forgeable).
- Typing redirect URIs instead of copy-pasting; forgetting trailing-slash exact match.
- Clicking 'Regenerate' on the client secret and then getting invalid_client; sharing the client_secret with the browser / committing it to Git.
- Leaving the user's password 'Temporary' ON, then thinking the credentials are wrong.
- Expecting realm_access.roles on a fresh user without assigning roles.
- Running Keycloak and immediately assuming it's broken (30–60s startup).
- Using the wrong admin env-var names for the Keycloak image version; using `latest` instead of a pinned image.
- Using `localhost` for Keycloak from inside another container.
- Treating the ID token as the API token.
- Testing with tokens generated by hand instead of the real flow — the whole point of today is a real IdP, real realm, real user, real end-to-end exchange.

## 11. Interview questions

- Why was the Session 3 JWT implementation insufficient for a production identity system? (No user store/signup/reset; shared secret; no per-token revocation; manual token creation.)
- What is the responsibility of Keycloak? (Identity Provider + Authorization Server + OIDC provider — authenticates, issues tokens, manages users/roles; "trust because I trust the issuer.")
- What is the difference between an Authorization Server and a Resource Server? (Issues tokens vs accepts access tokens and serves protected resources.)
- Why does the Authorization Code Flow use browser redirects? (Password typed only into Keycloak; the Client never sees credentials; it only receives a short-lived code.)
- Why should a browser/SPA not contain a client secret? (Code is visible to the user — the "secret" isn't secret; use Public Client + PKCE.)
- What problem does PKCE solve? (Code interception during authorization-code exchange; verifies the client that started the flow completes it.)
- What is the difference between an Access Token and an ID Token? (API authorization vs OIDC identity artifact for the client.)
- What does iss mean? What does sub mean? (Who issued the token — Keycloak realm URL; the user/client identity the token represents.)
- What are the four OAuth2 roles and who plays them here? (Resource Owner=customer, Client=Gateway, Authorization Server=Keycloak, Resource Server=services via Gateway.)
- What is a realm and why not use master? (Isolation boundary of users/clients/roles; master is for Keycloak's own admin.)
- Public vs Confidential client — what decides? (Whether the app can safely store a secret: server-side yes; SPA/mobile no.)
- OAuth2 vs OIDC? (Authorization vs authentication/identity on top of OAuth2.)
- What did the Keycloak JWT have that Session 3's didn't? (Real sub; realm_access.roles; iss; RSA private-key signing.)

## 12. What I must memorize

- The four OAuth2 roles and their platform mapping: Resource Owner=customer, Client=Gateway, Authorization Server=Keycloak, Resource Server=Order/Product Service via Gateway.
- The 5-step Authorization Code Flow: login click → redirect to Keycloak login page → customer authenticates directly → redirect back with short-lived code → server-side exchange for access + id + refresh tokens.
- The core security property: the Client only ever receives a short-lived authorization code — never the password, never the raw credentials.
- Trust shift: "trust because I know the secret" → "trust because I trust the issuer."
- Realm = isolation boundary; use `ecommerce-platform`, never put app users in `master`.
- Gateway client: Client authentication ON = Confidential; Standard flow = Authorization Code Flow; redirect URI `http://localhost:8080/login/oauth2/code/keycloak`.
- Token endpoint: `POST /realms/<realm>/protocol/openid-connect/token` with grant_type=authorization_code + client_id + client_secret + code + redirect_uri; response = access_token, id_token, refresh_token, expires_in.
- JWT claims: iss (issuer — Keycloak realm URL), sub (real user ID), exp, iat, realm_access.roles (assigned in Admin Console).
- Session 3 vs Keycloak token table: sub hardcoded→real; role manual→realm_access.roles; iss absent→present; HMAC shared secret→RSA private key at Keycloak.
- OAuth2 = authorization, OIDC = authentication; access token for APIs, ID token for the client.
- Public vs Confidential + PKCE rule.
- Scope boundary: today human login only; Client Credentials and Resource Server wiring = Session 20.
- Lab 15 deliverables: Keycloak in compose at the chosen port; realm + confidential gateway client + customer1; documented manual flow; 3–4 sentence token comparison note.

## 13. What I must understand

- WHY a real IdP exists: identity is a responsibility of its own (users, passwords, reset, MFA, revocation) and must not live inside each microservice.
- WHY redirects: to keep raw credentials away from the Client application.
- WHY the trust moves outward one layer: services trust the Gateway (S3); the Gateway trusts Keycloak (S19) — same boundary-trust principle, one layer further out; the Gateway then no longer needs to know HOW authentication happened.
- WHY the Gateway is a Confidential client and when you'd choose Public + PKCE instead; and that the Gateway doesn't have to be the OAuth2 client in every architecture (BFF vs browser-token models).
- WHY the authorization code is short-lived and exchanged server-side (secret never exposed to the browser).
- What each token is FOR (access vs id vs refresh) — and why using the ID token as an API token is wrong.
- What remains unresolved after today and why that's deliberate (no service code changes; JwtAuthFilter still active; Client Credentials + Resource Server = Session 20).

## 14. What I should implement from memory

- The docker-compose Keycloak service block (image pinned, start-dev, admin env vars, port mapping avoiding clashes, platform-net).
- Console workflow: create realm `ecommerce-platform` → create confidential client `gateway` (Standard flow, redirect URI) → copy client secret → create user `customer1` with non-temporary password → (bonus) admin role + admin user.
- The authorization URL (auth endpoint with client_id/redirect_uri/response_type=code/scope=openid), capturing the `?code=`, and the curl token exchange (grant_type=authorization_code, client_id, client_secret, code, redirect_uri).
- Inspecting the JWT payload on jwt.io: locate iss, sub, exp, realm_access.roles; explain each.
- The comparison table against Session 3's token (sub/role/iss/signing key).
- Lab 15 tasks 1–4 including the 3–4 sentence written note: "what fields does this JWT have that Session 3's did not?"

## 15. Relationship to previous sessions

- **Session 3 is the direct predecessor:** it built JwtAuthFilter with a shared secret in application.yml and explicitly deferred token issuance — "We cover the full OAuth2 flow in a later session." Session 19 answers that open question for human login. Today's shift extends the Session 3 "Gateway as trust boundary" lesson one layer out.
- The comparison slide is literally "Session 3 Hand-Signed JWT vs Keycloak JWT" (sub/role/iss/signing key).
- **Session 8 / S1–S16 platform pieces** appear only in the 8-segment progress tracker (Config+Eureka, Gateway, Resilience, Feign+Saga, K8s Pipeline, Observability, CQRS) — Keycloak IdP is the NEW segment added today.
- **Session 18 (previous session):** CQRS — no direct dependency; the deck's "where we are" shows S18 CQRS → S19 Security Pt.1.

## 16. Relationship to future sessions

- **Session 20 (next, Monday 3:00–5:30 PM, Online) completes the swap:** "Gateway validation will use Keycloak tokens instead of the custom JwtAuthFilter from Session 3." Session 20 scope: Client Credentials Flow (service-to-service), wiring the Gateway as a real OAuth2 Resource Server, RSA public-key verification (JWKS), role-based authorization, retiring JwtAuthFilter/JwtUtil/JJWT deps/jwt.secret.
- The client secret copied today is needed "for the token exchange in Step 5, and for Session 20."
- The BONUS admin role/user is explicitly to "preview Session 20's role-based access."
- The combined deck's Part B extends this architecture diagram with Client Credentials (Order Service → Keycloak → Inventory Service) — the "no user" half of the security story.
- Phase 3 roadmap (deck slide): S19 Security Pt.1 → S20 Security Pt.2 → S21 Service Mesh → S22 Adv. Patterns → S23 Performance → S24 Arch Clinic #2.

## 17. Lab relationship

Exact lab/quiz content as stated in the slides:

- **LAB 15 — Standing Up Keycloak & Running the Flow** (deck slide 20): Infrastructure + manual flow verification — Embedded across Live Coding blocks — **~55 min**. 4 tasks: (1) Add Keycloak to the Platform — docker-compose.yml + verify Admin Console loads at :8090. (2) Create Realm, Client, User — ecommerce-platform realm, Confidential 'gateway' client, 'customer1' user. (3) Run and Document the Flow — Build the authorization URL, capture the code, exchange for tokens. (4) Compare the Tokens — 3–4 sentence note: what fields does this JWT have that Session 3's did not?
- **Live coding blocks (deck, 4 blocks):** Keycloak in docker-compose; Create the Realm; Create the Gateway Client (Confidential); Create a Test Customer User; then "Run the Flow" with Browser + Postman manual Authorization Code Flow (URL, code capture, curl exchange) and the jwt.io demo.
- **Demo (deck):** Inspecting the Real Keycloak JWT on jwt.io — header/payload/signature, look at the payload: iss, sub, realm_access.roles, exp. Production note repeated: Keycloak or Auth0 issues tokens; the Gateway only validates.
- **Daily Quiz (deck):** 8 Questions — 10 Minutes — Google Forms or Kahoot. Topics: OAuth2 Roles, Authorization Code Flow, Public vs Confidential, Realms.
- **Practical Lab (combined tutorial, Sessions-19 portion of the 12 labs):** Lab 1 — Start Keycloak (`docker compose up -d keycloak`; verify console); Lab 2 — Create Realm `ecommerce-platform`; Lab 3 — Create Gateway Client (authorization-code flow; record Client ID, Client Secret, Redirect URI; do not commit the secret to Git); Lab 4 — Create Customer `customer1` + assign the appropriate user role; Lab 5 — Perform Authorization Code Flow (browser login → Keycloak → authorization code → exchange → inspect JWT: iss, sub, exp, realm_access). Labs 6–12 belong to Session 20.
- **Keycloak / Authorization Code sections of the combined Testing Checklist (shared with Session 20):** Keycloak starts; Admin Console opens; ecommerce-platform realm exists; gateway client exists; customer1 exists. Login redirects to Keycloak; Customer can authenticate; Authorization code is returned; Code can be exchanged for tokens; Access token can be inspected.
- **No homework is assigned in the S19 deck or in the combined tutorial's Session-19 part** (the combined tutorial has no homework section; homework in S18 explicitly; S20 deck homework items are listed in session-20.md). Keycloak bonus task is labeled "BONUS at home" but is not formal homework.
- **Checkpoint commits in slides:** not shown in either S19 PDF.
