# Prerequisites & Tooling Audit

> Full inventory of everything the course needs, organised by the session that first requires it.
> Environment status verified on **2026-09-28** on this machine (Windows 11, Git Bash).

## Status summary

| # | Tool | Needed from | Status |
| --- | --- | --- | --- |
| 1 | JDK 21 (LTS) | Session 01 | **PASS** — JDK 21.0.5 installed (`C:\Program Files\java\jdk-21`, `JAVA_HOME` set). Note: bare `java` on PATH resolves to JDK 17; Maven correctly uses 21. Cosmetic only. |
| 2 | Maven 3.9+ | Session 01 | **PASS** — 3.9.10 |
| 3 | Git 2.x+ | Session 01 | **PASS** — 2.48.1 (Git Bash) |
| 4 | Docker Engine + Compose | Session 01 | **PASS** — Docker 29.7.2, Compose v5.4.0, daemon running |
| 5 | curl | Session 01 | **PASS** — 8.12.1 |
| 6 | jq | Session 03 (nice), Session 23 (real) | **MISSING** |
| 7 | K8s cluster (Docker Desktop K8s / minikube / kind) | Session 15 | **MISSING** — kubectl installed (v1.36.1) but no cluster/context configured (`~/.kube` absent) |
| 8 | Helm | Session 16 | **MISSING** |
| 9 | Istio + istioctl | Session 21 | **MISSING** |
| 10 | k6 | Session 23 | **MISSING** |
| 11 | gh CLI (optional) | PR flow | MISSING — not required; git + SSH works |
| 12 | Postman / Insomnia (optional) | Session 01 | NOT VERIFIED (GUI app, manual check) |
| 13 | IntelliJ IDEA (recommended) | Session 01 | NOT VERIFIED (GUI app, manual check) |

Nothing missing blocks **Lab 1**. `jq` is convenient from Session 3 (rate-limit header inspection) and required in practice by Session 23's `watch … | jq` commands — install before Session 23 at the latest. Helm/k8s/Istio/k6 block Phases 2–3 only.

## Core

### JDK 21 — PASS
- **Why:** every module targets Java 21 (`pom.xml` `java.version` 21); CI uses temurin 21.
- **Verify:** `java -version` (expect `21.x`) and `mvn -version` (expect `Java version: 21.x`).
- **Note:** if a terminal shows Java 17, check `JAVA_HOME`; Maven honors `JAVA_HOME`, not PATH.

### Maven 3.9+ — PASS
- **Why:** build/test tool for every module (`mvn test`, `mvn spring-boot:run`).
- **Verify:** `mvn -version`.

### Git — PASS
- **Why:** checkpoint commits every session; "no commit = no grade".
- **Verify:** `git --version`.

### Docker Desktop — PASS
- **Why:** all infrastructure (Postgres, Redis, Kafka, Zipkin, Prometheus, Grafana, Keycloak) and later all application services run as containers. The daemon must be **running** before `docker compose up -d`.
- **Verify:** `docker --version && docker compose version && docker info --format '{{.ServerVersion}}'`.

### curl — PASS
- **Why:** every lab's acceptance criteria are curl commands.
- **Verify:** `curl --version`.

## Spring ecosystem (Maven-managed — no install)

All pulled via `pom.xml` from the Spring BOMs: Spring Boot 3.3.4, Spring Cloud 2023.0.3, Spring Cloud Gateway, Eureka Server/Client, Spring Cloud Config Server (native profile), OpenFeign, Resilience4j (`spring-boot3` starter), Spring Kafka. Nothing to install manually; versions resolved from the BOMs (see `TECHNOLOGY_MATRIX.md`).

## Messaging

### Kafka + ZooKeeper — via Docker (PASS)
- **Images:** `confluentinc/cp-kafka:7.6.1`, `confluentinc/cp-zookeeper:7.6.1` (from compose).
- **Why:** Session 07 (saga), Session 12 (orchestration), Session 13 (retry topics/DLT), Session 22 (outbox).
- **Verify:** `docker compose ps` shows kafka healthy; `docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list`.

## Databases / storage

### PostgreSQL — via Docker (PASS)
- **Image:** `postgres:16-alpine` (db `microservices_pro`).
- **Why:** Session 01 (infra up), Session 08 (JPA + cache).
- **Verify:** `docker exec -it postgres psql -U postgres -d microservices_pro -c 'select 1'`.

### Redis — via Docker (PASS)
- **Image:** `redis:7-alpine`.
- **Why:** Session 03 (rate-limiter counters), Session 08 (`@Cacheable`).
- **Verify:** `docker exec -it redis redis-cli ping` → `PONG`.

## Observability

### Zipkin, Prometheus, Grafana — via Docker (PASS at S17)
- **Images:** `openzipkin/zipkin:3` (:9411), `prom/prometheus:v2.51.0` (:9090), `grafana/grafana:10.4.2` (:3000, admin/admin).
- **Why:** Session 17; Zipkin also used by Session 23 (trace ↔ k6 error correlation).
- **Verify:** `curl -s localhost:9411/health`, `curl -s localhost:9090/-/healthy`, Grafana login.

## Security

### Keycloak — via Docker (PASS at S19)
- **Image:** `quay.io/keycloak/keycloak:24.0.4` (`start-dev`, host port 8180 → container 8080, admin/admin DEV ONLY).
- **Why:** Sessions 19–20 (replaces `tools/jwt-generator`), Session 23 (`TEST_JWT` via client-credentials).
- **Verify:** `curl -s http://localhost:8180/realms/master` returns realm JSON; admin console loads.
- **Discrepancy to resolve at S19:** earlier course material states `:8090` with realm `microservices-pro`, the S22/23 lab docs state `:8180` with realm `ecommerce-platform`. Decide at implementation time from the deck.

## Kubernetes

### kubectl — PASS (installed)
### Kubernetes cluster — MISSING
- **Why:** Sessions 15–16 (deployments, HPA, Helm), Session 21 (Istio).
- **Choose one:**
  - **Docker Desktop Kubernetes** (simplest; matches course): Docker Desktop → Settings → Kubernetes → Enable Kubernetes → Apply & Restart. Verify: `kubectl version` (server version appears), `kubectl get nodes` → one node `Ready`.
  - **minikube:** `winget install Kubernetes.minikube` then `minikube start --driver=docker`. Verify `kubectl get nodes`.
  - **kind:** `winget install Kubernetes.kind` then `kind create cluster`.
- **Verify:** `kubectl get nodes` shows a Ready node.

### Helm — MISSING
- **Why:** Session 16 (chart authoring, install/upgrade/rollback).
- **Install:** `winget install Helm.Helm` (or `choco install kubernetes-helm`).
- **Verify:** `helm version` (v3.x) and `helm list`.

### Istio + istioctl — MISSING
- **Why:** Session 21 (sidecar injection, VirtualService, DestinationRule, PeerAuthentication mTLS).
- **Install (Windows):** download the Istio release zip and add `istioctl` to PATH — see the official getting-started guide (https://istio.io/latest/docs/setup/getting-started/). WSL alternative: `curl -L https://istio.io/downloadIstio | sh -`.
- **Verify:** `istioctl version --remote=false`.
- **Note:** resource-heavy alongside Docker Desktop; can be exercised with a smaller demo namespace.

## CI/CD

### GitHub account + repo — see identity section below
- **Why:** Session 13 (Actions workflows), Session 14 (GitOps). The course mandates a personal repository where the trainee pushes each checkpoint commit.
- **Verify:** `git remote -v` inside this repo shows the personal remote.

### gh CLI (optional) — MISSING
- Not required; git over SSH is sufficient. Install `winget install GitHub.cli` if PR automation is wanted.

## Performance

### k6 — MISSING
- **Why:** Session 23 (smoke/load/stress).
- **Install:** `winget install k6.k6` (or `choco install k6`).
- **Verify:** `k6 version`.

### jq — MISSING
- **Why:** Session 23 `watch -n1 curl … | jq …` monitoring commands; handy for gateway/CB output throughout.
- **Install:** `winget install jqlang.jq` (or `choco install jq`).
- **Verify:** `jq --version`.

## Identity / GitHub configuration (from the master prompt — non-negotiable)

- Use **only** the personal GitHub account `5alafawyyy` via the SSH alias `github-personal`.
- Remotes must be `git@github-personal:5alafawyyy/<repo>.git`.
- **Never** use the work account (`ahmedemad1998` / `github-work` / `id_ed25519_work`).
- Before every push: run `git remote -v`, `git config --local user.name`, `git config --local user.email`, `ssh -T git@github-personal` — stop if anything indicates the work account.
- No global git config changes; repository-local settings only.
- **Open item:** `user.email` for the training repo is not yet set (awaiting the trainee's personal email).

## Installation backlog (not blocking Lab 1)

| Order | Tool | Command | When needed |
| --- | --- | --- | --- |
| 1 | jq | `winget install jqlang.jq` | before S03 (nice-to-have) / S23 (required) |
| 2 | cluster | Docker Desktop → Enable Kubernetes | before S15 |
| 3 | Helm | `winget install Helm.Helm` | before S16 |
| 4 | Istio | istioctl per official docs | before S21 |
| 5 | k6 | `winget install k6.k6` | before S23 |

Each will be re-verified with the `PREREQUISITE CHECK` block (per master prompt §7) immediately before the session that needs it — nothing gets installed without explicit approval.

## Port conflicts discovered on this machine (2026-09-28)

A **separate Docker project** is currently running on this machine — containers named `iiq-*` (IdentityIQ:
tomcat, mysql, openldap, phpldapadmin, phpmyadmin, mailslurper). **These belong to other work — they must not
be stopped, modified, or deleted by this training.** They occupy course-relevant ports:

| Port | Occupied by | Course use | Blocks |
| --- | --- | --- | --- |
| **8080** | `iiq-tomcat` | API Gateway (S2+) | Lab 2 onward |
| **8085** | `iiq-mailslurper` | Notification Service (S7 homework / map) | notification work |
| **8090** | `iiq-mailslurper` | Keycloak dev port (S19–S20, one of the two documented variants) | S19–S20 |
| **6443** | `iiq-ldapadmin` (host port) | Kubernetes API server default | S15 (Phase 2) |

Not conflicting: 3306 (course uses PostgreSQL 5432), 389/636 (LDAP, unused by the course).

### Resolution options (decision deferred to the user — nothing changed yet)

1. **Stop the iiq stack only while a conflicting lab runs** (`docker compose -f <iiq-compose> stop` in *that*
   project) and restart it afterwards. Cleanest for the gateway; requires access to that project's compose file.
2. **Remap the course ports** in the course's own `docker-compose.yml` / service `application.yml`
   (e.g. gateway 18080). Cheap, but diverges from the lab documents' acceptance criteria (which hardcode 8080)
   and from the exam expectations — only acceptable if documented as an explicit ADR.
3. **Leave as-is for Phase 1 Lab 1** — Lab 1 only needs 8081 (product), 8761 (eureka), 8888 (config),
   5432 (postgres). **None of these conflict.** The conflict only starts at Lab 2 (gateway :8080).

Current status: **Lab 1 is unblocked.** The 8080/8085/8090/6443 conflicts must be resolved (option 1 or 2,
user's call) before Lab 2 / S15 / S19. Recorded in the reconnaissance report as open question #5.
