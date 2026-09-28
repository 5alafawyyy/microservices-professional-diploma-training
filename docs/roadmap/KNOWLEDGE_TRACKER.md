# Knowledge Tracker

> Tracks real competency, not just "code compiles". A topic is only **EXAM READY** when it can be explained, reproduced from memory, and troubleshot without AI assistance.
> Update after every lab, quiz, clinic and recall session. Statuses: `NOT STARTED` → `INTRODUCED` → `UNDERSTOOD` → `PRACTICED` → `CONFIDENT` → `EXAM READY`.

## How to update

After each lab, set the columns that actually happened:

- **Introduced** — covered in the lecture/study note.
- **Practiced** — implemented with guidance or followed along.
- **Explained** — can explain it verbally/in writing without notes (proven in a recall session).
- **Implemented** — built it from scratch with minimal/no assistance.
- **Troubleshot** — diagnosed a real failure involving it (see `ENGINEERING_LOG.md`).
- **Exam Ready** — all of the above + can answer Level 5–6 recall questions (see `EXAM_PREPARATION_ROADMAP.md`).

## Phase 1 — Foundations

| Topic | Src | Practiced | Explained | Implemented | Troubleshot | Exam Ready |
| --- | --- | --- | --- | --- | --- | --- |
| Monolith vs microservices trade-offs | S01 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Bounded contexts / DDD service decomposition | S01 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| 12-Factor App (Config, Backing Services) | S01 | PRACTICED | NOT STARTED | IMPLEMENTED | — | NOT STARTED |
| Eureka: registration, discovery, self-preservation | S01 | PRACTICED | NOT STARTED | IMPLEMENTED | TROUBLESHOT | NOT STARTED |
| Spring Cloud Config Server (native profile) | S01 | PRACTICED | NOT STARTED | IMPLEMENTED | NOT STARTED | NOT STARTED |
| Actuator health endpoints | S01 | PRACTICED | NOT STARTED | IMPLEMENTED | — | NOT STARTED |
| API Gateway (Spring Cloud Gateway, WebFlux) | S02 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Route predicates, `lb://`, StripPrefix | S02 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| GlobalFilter + Ordered, filter ordering | S02 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| JWT structure + validation (jjwt) | S03 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Public-route whitelisting / header propagation | S03 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Token-bucket rate limiting with Redis | S03 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Circuit breaker states + config | S04 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Retry with exponential backoff | S04 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Fallback methods (signature rules) | S04 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Bulkhead (semaphore) | S05 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| TimeLimiter + async `CompletableFuture` | S05 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Annotation stacking order (why outermost-first) | S05 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| OpenFeign declarative clients | S06 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| `ErrorDecoder` → domain exceptions | S06 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| JWT propagation between services | S06 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Kafka fundamentals (topics, partitions, groups) | S07 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Choreography saga + compensation | S07 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Consumer-group design (the 5-group trap) | S07 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Idempotent compensation | S07 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Cache-aside + `@Cacheable`/`@CacheEvict` | S08 | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| Stale-list trap / cache invalidation | S08 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Technical Debt Register discipline | S08 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |

## Phase 2 — Quality & Deployment

| Topic | Src | Practiced | Explained | Implemented | Troubleshot | Exam Ready |
| --- | --- | --- | --- | --- | --- | --- |
| Multi-stage Dockerfiles, non-root, HEALTHCHECK | S09 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Compose networking + service-name DNS | S09 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Test pyramid / FIRST principles | S10 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Mockito stubbing & verification | S10 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Testcontainers integration tests | S10 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Consumer-driven contracts (Pact) | S11 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| WireMock fault injection / chaos | S11 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Saga orchestration vs choreography | S12 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Commands vs events; saga state machine | S12 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| GitHub Actions workflow anatomy | S13 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| `@RetryableTopic` retry topics + DLT | S13 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| GitOps principles + ArgoCD Application | S14 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| K8s core objects (Deployment/Service/ConfigMap/Secret) | S15 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Probes, rolling updates | S15 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| HPA autoscaling | S16 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Helm charts (templates, values, rollback) | S16 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| RBAC (ServiceAccount/Role/RoleBinding) | S16 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |

## Phase 3 — Advanced & Enterprise

| Topic | Src | Practiced | Explained | Implemented | Troubleshot | Exam Ready |
| --- | --- | --- | --- | --- | --- | --- |
| Metrics (Micrometer/Prometheus) | S17 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Distributed tracing (spans, Zipkin) | S17 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Structured JSON logging + traceId correlation | S17 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Grafana dashboards | S17 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| CQRS + read projections | S18 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Event-driven cache eviction | S18 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| OAuth2 concepts (grants, tokens, claims) | S19 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Keycloak realms/clients/users/roles | S19 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Resource server + RBAC in the gateway | S20 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Client-credentials service-to-service auth | S20 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Istio: sidecars, VirtualService, DestinationRule | S21 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| mTLS STRICT + verification | S21 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Dual-write problem + transactional outbox | S22 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Polling publisher vs CDC/Debezium | S22 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Idempotency keys | S22 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| API versioning strategies | S22 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Load/stress/smoke testing (k6) | S23 | NOT STARTED | NOT STARTED | NOT STARTED | — | NOT STARTED |
| Bottleneck analysis via metrics/traces | S23 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |
| Architecture decision defence (ADR practice) | S24 | NOT STARTED | NOT STARTED | — | — | NOT STARTED |

## Weak-area log

Record topics where recall sessions (see `EXAM_PREPARATION_ROADMAP.md`) exposed gaps. Format: date · topic · what was weak · remediation · re-test result.

| Date | Topic | Weakness observed | Remediation | Re-test |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |
