# Phase 2 Roadmap — Quality & Deployment (Sessions 09–16)

> Goal: make the platform deployable and trustworthy: containerization, automated testing at every level, saga orchestration, CI/CD, GitOps, Kubernetes.
> Source framing: kickoff deck ("Phase 2 — Quality & Deployment, S9–16") + deck folders `Phase2/`. The course `COURSE-ROADMAP.md` splits these topics differently; the decks win (see digest §7).

## Phase outcome

```
                     ┌──────────────────────────── GitHub Actions ───────────────────────────┐
                     │  per-service CI: build → test → docker build → push (ghcr/dev registry)│
                     └───────────────────────────────┬───────────────────────────────────────┘
                                                     ▼
   docker compose (local)                     Kubernetes cluster (Docker Desktop / minikube)
   postgres · redis · kafka · zipkin              k8s/*.yaml  +  helm/product-service-chart
   config · eureka · gateway · 5 services         ArgoCD watches git → syncs manifests
   (+ notification-service :8085)                 HPA scales product-service
```

Test architecture by end of phase: unit (JUnit5/Mockito) + integration (Testcontainers, real Postgres) + contract (Pact consumer/provider) + chaos (WireMock fault injection).

## Session-by-session

### Session 09 — Docker Containerization

- **Concepts:** multi-stage builds (build with Maven image, run with JRE image), layer caching, non-root containers, HEALTHCHECK, `.dockerignore`, compose service discovery by name.
- **Build:** Dockerfile + `.dockerignore` for all 7 modules; compose file gains `config-server`, `eureka-server`, `api-gateway`, `product-service`, `inventory-service`, `payment-service`, `order-service` containers on `platform-net`.
- **Lab:** Lab 8A (slide-only; no lab doc — reconstruct from deck + reference diff).
- **Acceptance (reconstructed):** `docker compose up -d` brings up infra + all services healthy; gateway reachable on 8080 from host; identical behaviour to the Maven-run stack.
- **Checkpoint commit:** `session-09: docker-containerization` (reference wording; commit format must stay `session-NN: …`).
- **Mid-Course Exam anchor day** — practical coding exam covering Sessions 1–8 (15% of grade).

### Session 10 — Testing Essentials + Unit & Integration Testing

- **Concepts:** test pyramid, FIRST principles, JUnit 5 lifecycle/parameterized tests, Mockito stubbing/verification, `@SpringBootTest` vs slice tests, integration testing against real infrastructure (Testcontainers) vs mocks.
- **Build:** expand test suites; `ProductServiceIntegrationTest` (Testcontainers Postgres), `ProductControllerTest`, parameterized tests.
- **Lab:** Lab 9A (slide-only).
- **Acceptance (reconstructed):** Testcontainers test boots a real `postgres:16` container; suite green including the S1–S9 tests.
- **Checkpoint commit:** `session-10: testing` (reference wording).

### Session 11 — Testing: Contract & Chaos

- **Concepts:** consumer-driven contracts, pact files, provider verification, contract versioning; chaos testing by fault injection (latency, errors) with WireMock; difference between mocking and simulating failure.
- **Build:** `OrderServiceInventoryContractTest` (Pact consumer), `InventoryServicePactVerificationTest` (provider), `OrderServicePaymentWireMockTest` (fault injection: timeouts, 500s).
- **Lab:** Lab 9B (slide-only).
- **Acceptance (reconstructed):** pact contract generated and verified in both modules; WireMock test proves the client handles 500/timeout paths.
- **Checkpoint commit:** `session-11: contract-and-chaos-testing` (verify wording against deck at lab time).

### Session 12 — Saga Orchestration

- **Concepts:** orchestration vs choreography (central coordinator + state machine vs event chain), commands vs events, when to prefer each, compensations driven by the orchestrator, DLQ for stuck sagas.
- **Build:** `OrderSagaOrchestrator` + `SagaState`; command/result events (`ProcessPaymentCommand`, `ReserveInventoryCommand`, `ReleaseInventoryCommand` / `PaymentResultEvent`, `InventoryResultEvent`, `InventoryReleasedEvent`); handlers in payment/inventory services. The S7 choreography handlers remain in the tree.
- **Lab:** Lab 10A (slide-only).
- **Acceptance (reconstructed):** happy path completes via orchestrator; forced payment failure triggers `ReleaseInventoryCommand`; saga state reaches terminal state; no stuck `PENDING`.
- **Checkpoint commit:** `session-12: saga-Orchestration` (reference wording; keep `session-12: …` format).

### Session 13 — CI/CD Pipelines with GitHub Actions

- **Concepts:** workflow anatomy (triggers, jobs, steps, matrix), building/testing per service, caching Maven deps, artifact publishing, container image build + push, why one pipeline per service.
- **Build:** `notification-service` (:8085) consuming `payment-events` with `@RetryableTopic` (retry topics `payment-events-retry-0/1`, then `payment-events-dlt`); per-service CI workflows (`product-service-ci.yml`, `notification-service-ci.yml`).
- **Lab:** Lab 11A (slide-only).
- **Acceptance (reconstructed):** CI workflow green on push; retry topic + DLT exist after a forced consumer failure; notification-service logs consumed payment events.
- **Checkpoint commit:** `session-13: cicd` (reference wording).

### Session 14 — GitOps & Deployments

- **Concepts:** GitOps principles (git = single source of truth, pull-based deploy, drift detection), ArgoCD Application CRD, sync policies, separating app repo from deploy state.
- **Build:** `k8s/argocd/product-service-app.yaml`; `k8s/product-service/{configmap,deployment,deployment-canary,service}.yaml`.
- **Lab:** Lab 11B (slide-only).
- **Acceptance (reconstructed):** ArgoCD Application manifest valid (declarative); canary deployment described; drift-detection discussion documented.
- **Checkpoint commit:** `session-14: gitops` (reference wording).
- **UNKNOWN — REQUIRES SOURCE REVIEW:** whether a live cluster + ArgoCD install is expected in-session or the manifests are only authored.

### Session 15 — Kubernetes Core

- **Concepts:** Pods/Deployments/Services, ConfigMaps vs Secrets, liveness/readiness probes, `kubectl` workflow, namespaces, resource requests/limits, service discovery in K8s (as an alternative to Eureka — links back to S1).
- **Build:** `k8s/product-service/{deployment,hpa,secret}.yaml`; deployment runs the containerized service with config from ConfigMap/Secret.
- **Lab:** Lab 12A (slide-only).
- **Acceptance (reconstructed):** `kubectl apply` brings up product-service; pod Ready; logs clean; service reachable inside cluster; rolling update demonstrated.
- **Checkpoint commit:** `session-15: kubernetes` (reference wording).
- **Prerequisites:** cluster available locally (Docker Desktop Kubernetes or minikube — see `PREREQUISITES.md`), images built and loadable into the cluster.

### Session 16 — Kubernetes Advanced

- **Concepts:** HPA (CPU-based autoscaling), Helm (chart structure, templates, `values.yaml`, releases, rollback), ServiceAccount + Role/RoleBinding (least privilege), probes tuning.
- **Build:** `helm/product-service-chart` (Chart.yaml apiVersion v2, deployment/hpa/role/rolebinding/service/serviceaccount templates, `values.yaml`); `hpa.yaml` with CPU target.
- **Lab:** Lab 12B (slide-only).
- **Acceptance (reconstructed):** `helm install` deploys the chart; `helm upgrade`/`rollback` works; HPA scales replicas under load (`kubectl get hpa` shows target metrics).
- **Checkpoint commit:** `session-16: kubernetes-advanced` (verify wording against deck at lab time).

## Phase 2 completion criteria

- [ ] All 8 checkpoint commits present (`session-09` … `session-16`).
- [ ] `docker compose up -d` runs the full platform from a clean machine.
- [ ] Test architecture: unit + integration (Testcontainers) + contract (Pact) + chaos (WireMock) all green.
- [ ] At least one CI workflow runs on push and passes.
- [ ] `helm install` succeeds against a local cluster; HPA demonstrated.
- [ ] `docs/architecture/CURRENT_ARCHITECTURE.md` matches the deployed platform.
