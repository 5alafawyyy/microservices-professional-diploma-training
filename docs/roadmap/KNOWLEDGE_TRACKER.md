# Knowledge Tracker

Tracks the distinction between **repository implementation** and **student independent knowledge readiness**.

**Criteria for Overall Knowledge Status:**
* 🟢 **READY**: Can explain, reproduce independently, troubleshoot, and defend the concept.
* 🟡 **NEEDS PRACTICE**: Understands the concept but needs reference material for implementation/debugging.
* 🔴 **NOT READY**: Cannot explain clearly, cannot reproduce, or only recognizes code from seeing it.

## Phase 1 — Foundations

| Concept | Session | Impl Evidence | Impl Location | Explanation | Reproduction | Troubleshooting | Defense | Overall Knowledge | Assessment Date |
|---|---|---|---|---|---|---|---|---|---|
| Monolith vs microservices trade-offs | S01 | N/A (Theory) | N/A | 🔴 Not Validated | 🔴 Not Validated | N/A | 🔴 Not Validated | 🔴 NOT READY | - |
| Bounded contexts / DDD service decomposition | S01 | N/A (Theory) | N/A | 🔴 Not Validated | 🔴 Not Validated | N/A | 🔴 Not Validated | 🔴 NOT READY | - |
| 12-Factor App (Config, Backing Services) | S01 | Implemented | config-server | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Eureka: registration, discovery, self-preservation | S01 | Implemented | eureka-server | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Spring Cloud Config Server (native profile) | S01 | Implemented | config-server | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| API Gateway (Spring Cloud Gateway, WebFlux) | S02 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Route predicates, lb://, StripPrefix | S02 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| GlobalFilter + Ordered, filter ordering | S02 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| JWT structure + validation (jjwt) | S03 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Token-bucket rate limiting with Redis | S03 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Circuit breaker states + config | S04 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Retry with exponential backoff | S04 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Bulkhead (semaphore) | S05 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| TimeLimiter + async CompletableFuture | S05 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| OpenFeign declarative clients | S06 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| ErrorDecoder → domain exceptions | S06 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Kafka fundamentals (topics, partitions, groups) | S07 | Implemented | docker-compose.yml | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Choreography saga + compensation | S07 | Implemented | order, inventory, payment | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Idempotent compensation | S07 | Implemented | inventory-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Cache-aside + @Cacheable/@CacheEvict | S08 | Implemented | product-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Technical Debt Register discipline | S08 | Implemented | docs/architecture/clinic-2.md | 🔴 Not Validated | 🔴 Not Validated | N/A | 🔴 Not Validated | 🔴 NOT READY | - |

## Phase 2 — Quality & Deployment

| Concept | Session | Impl Evidence | Impl Location | Explanation | Reproduction | Troubleshooting | Defense | Overall Knowledge | Assessment Date |
|---|---|---|---|---|---|---|---|---|---|
| Multi-stage Dockerfiles | S09 | Implemented | Dockerfile (all services) | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Compose networking + service-name DNS | S09 | Implemented | docker-compose.yml | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Test pyramid / FIRST principles | S10 | N/A (Theory) | N/A | 🔴 Not Validated | 🔴 Not Validated | N/A | 🔴 Not Validated | 🔴 NOT READY | - |
| Mockito stubbing & verification | S10 | Implemented | product-service tests | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Testcontainers integration tests | S10 | Implemented | product-service tests | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Consumer-driven contracts (Pact) | S11 | Implemented | order-service tests | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| WireMock fault injection / chaos | S11 | Implemented | order-service tests | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Saga orchestration vs choreography | S12 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| GitHub Actions workflow anatomy | S13 | Implemented | .github/workflows/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| GitOps principles + ArgoCD Application | S14 | Implemented | k8s/argocd/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| K8s core objects (Deployment/Service) | S15 | Implemented | k8s/manifests/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Probes, rolling updates | S15 | Implemented | k8s/manifests/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| HPA autoscaling | S16 | Implemented | k8s/helm/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Helm charts | S16 | Implemented | k8s/helm/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| RBAC (ServiceAccount/Role) | S16 | Implemented | k8s/helm/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |

## Phase 3 — Advanced & Enterprise

| Concept | Session | Impl Evidence | Impl Location | Explanation | Reproduction | Troubleshooting | Defense | Overall Knowledge | Assessment Date |
|---|---|---|---|---|---|---|---|---|---|
| Metrics (Micrometer/Prometheus) | S17 | Implemented | All services | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Distributed tracing (spans, Zipkin) | S17 | Implemented | All services | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| CQRS + read projections | S18 | Implemented | product-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| OAuth2 concepts (grants, tokens, claims) | S19 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Keycloak realms/clients/users/roles | S19 | Implemented | Keycloak | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Resource server + RBAC in the gateway | S20 | Implemented | api-gateway | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Client-credentials service-to-service auth | S20 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Istio: sidecars, VirtualService | S21 | Implemented | k8s/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| mTLS STRICT + verification | S21 | Implemented | k8s/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Dual-write problem + transactional outbox | S22 | Implemented | order-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Idempotency keys | S22 | Implemented | payment-service | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Load/stress/smoke testing (k6) | S23 | Implemented | k6/ | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 Not Validated | 🔴 NOT READY | - |
| Architecture decision defence (ADR practice) | S24 | Implemented | docs/architecture/ | 🔴 Not Validated | 🔴 Not Validated | N/A | 🔴 Not Validated | 🔴 NOT READY | - |

