# Session 09 — Docker Containerization

Source files:
- `Session_09 — Docker Containerization.pdf` — full lecture deck (131 slides, Dr. ElSayed Mohamed Elsayed Baladoh; 7 parts: why Docker, install, images & containers, first Dockerfile, multi-stage builds, Docker Compose, production compose + best practices).
- `Session_09_Docker_Containerization.pdf` — course delivery deck (31 slides, "PHASE 2 – SESSION 9 OF 29 – ANCHOR DAY", Wednesday in-person 10:00–15:00 + mid-course exam, 5 hours): roadmap, the three root-cause stories, decision rules, standard Dockerfile, Lab 8A, homework, quiz list, exam logistics.

Source note: the two files are NOT duplicates (131 pages vs 31 pages; different content). Both were read; this note merges them. The underscore deck is the anchor-day deck and is the anchor for labs/homework/exam logistics.

## 1. Why this topic exists

- Docker is the first Phase 2 session; Phase 1 (S1–8) built a working microservices platform on a developer machine, and the class problem is: "works on my machine" — how do we deliver the platform so it runs identically on any machine (colleague laptop, test server, production)?
- Anchor-day framing: three ROOT CAUSES of "works on my machine" class of problems:
  1. JDK version mismatch (developed on 21, server has other version).
  2. Missing environment variables (e.g. `SPRING_PROFILES_ACTIVE`, config/eureka/DB connection env omitted outside the IDE).
  3. `localhost` vs container hostname (`localhost` inside a container is the container itself, not the host and not another service).
- Three PRINCIPLES Docker provides: Isolation (each service in its own environment), Reproducibility (same image -> same behavior anywhere), Portability (build once, run anywhere).
- Container vs VM: container startup 1–5 s vs VM 30–120 s; Spring Boot image 200–300 MB vs VM images of several GBs. Docker vs VM comparison table makes the resource-weight argument.
- Automation/CI argument: from S9 onward the service must be packaged as an image so later sessions (CI/CD, GitOps, Kubernetes) can deploy it without environment hand-crafting.

## 2. Core concepts

- "Build once, run anywhere": an image built on the developer machine runs identically on any Docker host.
- Image vs container: image = read-only template (built from a Dockerfile, layered); container = a running instance created from the image (plus a writable layer).
- Container lifecycle: Created -> Running -> Stopped -> Removed. Commands: `docker run`/`docker stop`/`docker start`/`docker rm`/`docker rmi`.
- Docker architecture components: CLI (what you type), Docker Desktop (GUI/daemon bundle on Windows/macOS), Docker Engine/daemon (builds and runs containers), and the artifacts: Images, Containers, Networks, Volumes.
- Dockerfile: declarative recipe for an image. Instructions covered: `FROM`, `COPY`, `RUN`, `WORKDIR`, `ENTRYPOINT`, `EXPOSE` (documentation only — it does NOT publish a port; `-p` does).
- Build context: the directory sent to the daemon at build time; `.dockerignore` excludes files (target/, .idea/, .git/, *.md, *.log, **/*.class) so context stays small and old JARs / .git history do not leak into the image.
- Layers and layer caching — the anchor-day rule: stable layers go ABOVE (earlier), volatile layers BELOW (later). Putting `pom.xml` in its own layer before copying `src` caches the ~2-minute Maven dependency download; a code-only rebuild then takes ~15 s instead of ~2 min.
- Multi-stage build: Stage 1 (builder) compiles with a full JDK+Maven image; Stage 2 (runtime) copies only the built JAR into a small JRE image. Sizes: single-stage ~600–700 MB vs multi-stage 180–300 MB (~240 MB measured); 60% smaller.
- Base images: `eclipse-temurin:21` (~700 MB full JDK — builder stage only) vs `eclipse-temurin:21-jre` / `eclipse-temurin:21-jre-jammy` (~240 MB JRE — runtime stage). Jammy = Ubuntu 22.04 LTS (patched until 2027). Rule: "Never put a full JDK in a production image."
- Docker Compose: declarative multi-container definition (`docker-compose.yml`): services, networks, volumes, environment variables, health checks, dependencies. Service names act as hostnames on the compose network.
- Named volumes: needed for PostgreSQL data persistence across `docker compose down` / `up`.
- Networks: one user-defined bridge network (platform-net) so containers resolve each other by service name; `container_name` should be avoided (name collisions, scaling).
- Non-root containers: create a system user (`addgroup --system spring && adduser --system --group spring`) and `USER spring` in the runtime stage.
- Health checks: `healthcheck.test: ["CMD","curl","-f","http://localhost:8888/actuator/health"]` with interval 10s, timeout 5s, retries 5; compose dependency on `condition: service_healthy`.
- Ports: `-p 8080:80` maps host port 8080 to container port 80.

## 3. Architecture

- Platform services listed in Part 1 (Phase 1 stack to be containerized): Config Server, Eureka, API Gateway, Product Service, Order Service, Inventory Service, Notification Service, PostgreSQL, Redis, Kafka, Zipkin.
- Production compose (Part 7) brings up, in order: config-server (8888) -> eureka-server (8761) -> api-gateway (8080) + the business services, plus infrastructure (postgres, redis, kafka).
- Startup-order topology (anchor day): Spring services depend on config-server and eureka-server with `condition: service_healthy`; PostgreSQL (healthcheck `pg_isready`) and Redis (`redis-cli ping`) are `service_healthy`; Kafka OSS has no HTTP health endpoint -> `service_started` + Spring's own reconnect/retry handles the rest.
- Network model: every service joins `platform-net` (bridge driver); internal DNS resolves `postgres`, `kafka`, `config-server`, `eureka-server` by service name. Container-to-container traffic uses service names; only front doors are published to the host.
- Per-service container facts (anchor deck compose examples): config-server 8888, eureka-server 8761, product-service 8081 (productdb), order-service 8082 (+kafka `service_started`, orderdb), payment-service 8083 (PAYMENT_FAILURE_RATE=0.0 "DEV ONLY"), inventory-service 8084 (inventorydb), api-gateway 8080.
- Image flow: source -> `docker build -t product-service:local .` -> local image (241 MB measured in demo) -> `docker run` -> container; later sessions move the same image to registries (CI/CD) and Kubernetes.
- CRITICAL limitation stated in the slides: `depends_on` controls STARTUP ORDER only, not runtime monitoring — it will not restart a dependent service if its dependency later dies. `condition: service_healthy` only waits for one-time health at startup.

## 4. Technologies

- Docker (Engine, CLI, Desktop, Hub) — no version numbers are stated for Docker itself in the slides.
- Windows: WSL2 backend for Docker Desktop. Linux: `sudo apt install docker.io`, then `usermod -aG docker $USER` (non-root use of docker). macOS: Docker Desktop.
- Verification commands: `docker --version`, `docker info`; hello-world demo (5 internal steps explained).
- Base/version tags mentioned exactly: `eclipse-temurin:21`, `eclipse-temurin:21-jre`, `eclipse-temurin:21-jre-jammy`, `maven:3.9-eclipse-temurin-21` (builder), `postgres:16`, `redis:7`, `nginx` (practice). (The unit deck's TestContainers demo log alternatively shows postgres:15-alpine — that belongs to Session 10.)
- Docker Compose v2 CLI syntax: `docker compose ...` (subcommand form, not `docker-compose`).
- Alternative base images mentioned: Amazon Corretto, Alpine.
- No other exact tool versions are given in these decks.

## 5. Important terminology

- Image — immutable, read-only template of layered filesystem.
- Container — running (or stopped) instance of an image; thin writable layer on top.
- Dockerfile — text recipe; docker build executes its instructions layer by layer.
- Build context — files sent to the daemon for the build; controlled by `.dockerignore`.
- Layer cache — reuse of unchanged image layers; cache-busting when a copied file changes.
- Multi-stage build — multiple `FROM` stages; `COPY --from=builder` transfers artifacts.
- Registry — image store (Docker Hub etc.); `docker pull`/`docker push`.
- Volume — persistent storage managed by Docker; survives container removal; used for PostgreSQL data.
- Compose service — one container definition in `docker-compose.yml`; its name is its DNS hostname on the compose network.
- Healthcheck — in-container command Docker runs periodically to set healthy/unhealthy state.
- `service_healthy` / `service_started` — `depends_on` conditions for startup ordering.
- Non-root user — container process runs as unprivileged user (`USER spring`).
- `host.docker.internal` — hostname to reach the host from inside a container (Docker Desktop; on Linux requires `--add-host=host.docker.internal:host-gateway`).

## 6. Code concepts

- Simplest Dockerfile (Part 4): `FROM eclipse-temurin:21-jre`, `COPY app.jar app.jar`, `ENTRYPOINT ["java","-jar","app.jar"]`.
- The standard Dockerfile used throughout the course (Part 5, single-stage vs multi-stage form):
```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
ENTRYPOINT ["java","-jar","app.jar"]
```
- `-DskipTests` rationale (slides): tests already run in CI before the image build; image build stays fast. (Anchor day keeps this rule.)
- Standardized Stage 2 (anchor deck): WORKDIR /app, `RUN addgroup --system spring && adduser --system --group spring`, `USER spring`, `COPY --from=builder /build/target/*.jar app.jar`, `EXPOSE 8081`, `ENTRYPOINT ["java","-jar","app.jar"]`. "One Dockerfile pattern covers all 7 core services" — copy the pattern, change only the EXPOSE port.
- Layer-optimized dependency caching pattern (Part 4): `COPY pom.xml` then `RUN mvn dependency:go-offline` then `COPY src` — dependencies cached as their own layer.
- Build & run: `docker build -t product-service .` / `-t product-service:local`; `docker run -d --name nginx-demo -p 8080:80 nginx`; run demo with env vars (see section 7) and `host.docker.internal` when dependencies run on the host.
- Image/container management: `docker images`, `docker pull`, `docker ps`, `docker ps -a`, `docker logs`, `docker logs -f`, `docker exec -it <c> bash`, `docker inspect`, `docker stats`, `docker rm`, `docker rm -f`, `docker rmi`, `docker system prune`.
- Compose commands: `docker compose up`, `up -d`, `ps`, `logs`, `logs -f`, `stop`, `start`, `restart`, `down`; anchor deck verify flow: `docker compose build`, `docker compose up -d`, `docker compose ps` (all healthy), curl through the gateway.

## 7. Configuration

- Compose file basics (Part 6): `services:`, image or build, `ports`, `environment`, `depends_on`, `healthcheck`, `networks`, `volumes`. Environment variables in compose can be literal or `${VAR}` from `.env`/shell.
- JDBC URL inside compose network: `jdbc:postgresql://postgres:5432/productdb` — service name `postgres` is the hostname.
- Anchor-day env-var strategy (avoid hardcoded URLs; `localhost` inside a container = the container itself):
  - `SPRING_PROFILES_ACTIVE: docker`
  - `SPRING_CONFIG_IMPORT: optional:configserver:http://config-server:8888`
  - `CONFIG_SERVER_URL: http://config-server:8888`
  - `EUREKA_SERVER: http://eureka-server:8761/eureka` (client defaultZone)
  - `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USERNAME` / `DB_PASSWORD` per service
  - `EUREKA_CLIENT_SERVICE_URL_DEFAULTZONE` in the run-demo example.
- Rule: environment-varying values go in env vars (compose), constant values stay in `application.yml` (server.port, logging.level).
- Healthchecks: `test: ["CMD","curl","-f","http://localhost:8888/actuator/health"]`, `interval: 10s`, `timeout: 5s`, `retries: 5`. PG: `pg_isready`; Redis: `redis-cli ping`.
- `depends_on` conditions: Spring + Actuator services -> `service_healthy`; PostgreSQL/Redis -> `service_healthy`; Kafka (no HTTP health endpoint) -> `service_started` + Spring reconnect retry.
- Dev vs prod compose: dev uses build paths + volume mounts; prod uses prebuilt images and no dev-only flags (e.g. `PAYMENT_FAILURE_RATE: 0.0` marked "DEV ONLY").
- Secrets: never in compose plaintext. Slides state this is "addressed properly in Session 19 (Security + Keycloak)"; mention of Docker Secrets or Vault as the production mechanisms.
- Avoid `container_name` (breaks scaling / causes collisions); rely on service names.

## 8. Failure scenarios

- Docker Desktop not running -> CLI cannot connect to daemon (Part 2 common mistakes).
- Host port already in use -> `docker run -p` fails (port bind error).
- Closing Docker Desktop stops all running containers (mistake listed in Part 2).
- Code change not reflected in image: stale JAR in the image because `.dockerignore` was missing (target/ included in build context) or layer cache not invalidated correctly.
- Container cannot reach a dependency because the URL is `localhost` instead of the service name (root cause #3 example).
- Service starts before its dependency is ready -> crash; mitigated by healthcheck + `condition: service_healthy`.
- Kafka-dependent service starts before broker is ready -> `service_started` is deliberately used with Spring reconnect retry (accepted risk).
- Image way too large because a full JDK/Maven builder image is kept as the runtime stage (single-stage ~700 MB) — fixed by multi-stage.
- PostgreSQL data lost if no named volume exists.
- Test start with `docker compose down`/`up` used in homework to verify volume persistence.

## 9. Trade-offs

- Containers vs VMs: containers win on startup time (1–5 s vs 30–120 s), image size (hundreds of MB vs GBs), density; VMs win on full OS isolation (not discussed beyond the table).
- Single-stage vs multi-stage: single-stage is simpler but ~600–700 MB and carries build tools; multi-stage is ~2.5x smaller (~240 MB) at the cost of a more complex Dockerfile.
- `-DskipTests` in image build: fast builds and tests already run in CI — trade-off is that a developer can build an unverified image locally.
- `depends_on` + healthcheck: gives deterministic startup order but NO runtime monitoring/restart; slides call this the CRITICAL limitation — orchestration platforms (Kubernetes, later sessions) are what actually solve runtime dependency health.
- Kafka `service_started` vs `service_healthy`: waiting for Kafka health is not practical with plain OSS Kafka; accepting Spring's reconnect retry logic is the pragmatic choice.
- Dev compose convenience (volumes, build-on-up, FAILURE_RATE simulation) vs prod compose determinism (prebuilt images). `PAYMENT_FAILURE_RATE` is DEV ONLY.
- Secrets in env vars vs Docker Secrets/Vault: env vars are simple but visible; real secret management deferred to Session 19.

## 10. Common mistakes

- Forgetting `.dockerignore` -> huge build context, slow builds, old JARs copied in, `.git` history leaked into image.
- Copying all source before `pom.xml`/dependencies -> Maven download re-runs on every code change (destroys layer cache; 2 min vs 15 s rebuild).
- Confusing `EXPOSE` with port publishing: `EXPOSE` documents, `-p` actually maps.
- Using `localhost` inside compose network to reach other services (must use service names).
- Hardcoding URLs/ports instead of env vars.
- Using full JDK in production image ("Never put a full JDK in a production image").
- Using `container_name` (collisions, prevents scaling).
- Assuming `depends_on` guarantees the dependency is healthy forever (it only orders startup).
- Putting secrets in compose plaintext.
- Closing Docker Desktop / not starting it -> everything appears broken.

## 11. Interview questions

UNKNOWN — REQUIRES SOURCE REVIEW (for a slide-authored interview-question list — the deck has no such section). Questions below are derived strictly from slide content (the daily-quiz topic list and the deck's decision points):
- Why Docker over a VM — quantify startup time and image size.
- How does multi-stage build reduce the image from ~700 MB to ~240 MB?
- Why is `pom.xml` copied in its own layer before `src`?
- Dockerfile vs image vs container vs compose service — define each.
- What does `.dockerignore` do and what should be in it here?
- `EXPOSE` vs `-p 8080:80`?
- Why does `jdbc:postgresql://postgres:5432/productdb` work inside compose but `localhost` does not?
- What does `depends_on: condition: service_healthy` guarantee — and what does it NOT guarantee?
- Why can Kafka only use `service_started` here?
- Why run the container as a non-root user?
- Daily Quiz topics (anchor deck lists 8 questions / 5 min): Multi-Stage, Layer Cache, service_healthy, localhost vs service name, Non-root USER, Image size, Volumes.

## 12. What I must memorize

- The standard multi-stage Dockerfile pattern (maven:3.9-eclipse-temurin-21 builder -> eclipse-temurin:21-jre runtime, COPY --from=builder, ENTRYPOINT java -jar).
- Approximate numbers: container start 1–5 s; VM start 30–120 s; single-stage ~600–700 MB; multi-stage ~240 MB (60% smaller); pom layer saves 2 min -> 15 s rebuild; rebuild memo.
- `.dockerignore` contents: target/, .idea/, .git/, *.md, *.log, **/*.class.
- Container lifecycle: Created -> Running -> Stopped -> Removed.
- Compose service names are hostnames; `postgres:5432`, `kafka`, `config-server:8888`, `eureka-server:8761`.
- depends_on condition rules: Spring+Actuator -> service_healthy; PG/Redis -> service_healthy; Kafka -> service_started.
- Ports per service: gateway 8080, product 8081, order 8082, payment 8083, inventory 8084, config 8888, eureka 8761.
- Healthcheck syntax with interval 10s / timeout 5s / retries 5.
- Non-root: addgroup/adduser `spring`, `USER spring`.
- The two Session 09 decks' distinct roles (131-page lecture vs 31-page anchor-day deck).

## 13. What I must understand

- Why "build once, run anywhere" requires image immutability + externalized config, not just packaging.
- How layer caching works mechanically (a changed layer invalidates all layers below it; order layers stable->volatile).
- Why multi-stage separates build-time tools from runtime dependencies.
- Why service-name DNS + one bridge network replaces all localhost URLs.
- Why `depends_on` is a startup-order tool, not a supervisor (no runtime monitoring/restarts).
- Why Kafka-health waiting is impractical with OSS Kafka and how Spring retry compensates.
- Why the platform services must each be reachable only on the right ports and how the compose file expresses that.

## 14. What I should implement from memory

- Write the standard multi-stage Dockerfile for a Spring Boot service and the matching `.dockerignore`.
- Write a `docker-compose.yml` that starts config-server, eureka-server, postgres(+named volume), kafka, and one business service on `platform-net`, with healthchecks and `condition: service_healthy`/`service_started` dependencies and env vars instead of hardcoded URLs.
- Build, run, inspect, exec, log, and clean up a container using the CLI commands listed in section 6.
- Run the sample: build a service image, run it with the docker env vars, and verify through the gateway + Eureka.
- Demonstrate the layer-cache effect: rebuild after a code change and observe the fast rebuild.

## 15. Relationship to previous sessions

- Phase 1 (S1–8) built the platform: config-server, eureka-server, api-gateway, product/order/payment/inventory services, PostgreSQL/Redis/Kafka — Docker packages exactly these artifacts.
- Session 7 (Saga Choreography, referenced in the roadmap S9–S16) built event-driven flows; the containerized platform is the runtime for those services.
- The three root causes (JDK mismatch, missing env vars, localhost vs hostname) are the accumulated Phase 1 "works on my machine" pain that Docker answers.
- Roadmap shown: Phase 1 = S1–8; Phase 2 = S9 Docker, S10–S11 Testing I/II (sessions 10/11), S12 Saga Orchestration, S13 CI/CD, S14 GitOps, S15 K8s Core, S16 K8s Advanced.

## 16. Relationship to future sessions

- S10/S11 (testing): images and `docker compose up -d` are the environment for TestContainers; "TestContainers is our course standard from Lab 9A onwards"; homework must keep `docker compose up -d` working (no port leaks).
- S12 (Saga Orchestration): the order-service container hosts the S7 choreography code that S12's orchestrator complements.
- S13 CI/CD: the Dockerfile written here is what the pipeline builds and pushes to a registry.
- S14 GitOps / S15–16 Kubernetes: "build once, run anywhere" images are the deployable artifact; Kubernetes replaces compose as the orchestrator (runtime dependency health becomes the platform's job).
- S19 (Security + Keycloak): proper secrets management (compose plaintext secrets are explicitly deferred there).

## 17. Lab relationship

- LAB 8A — "Dockerize the Platform" (anchor deck), 60 minutes, 12:45–13:45. Scope: all 7 core Phase 1 services. Grading stated: Feature 70% + Tests 20% + Quality 10%.
  - Step 1 — Write Dockerfiles (20 min): copy the standard pattern to all 7 services, change only EXPOSE, add `.dockerignore`.
  - Step 2 — Update `docker-compose.yml` (20 min): build path, ports, `depends_on` (`service_healthy`; `service_started` for Kafka), environment variables, networks (`platform-net`).
  - Step 3 — Verify End-to-End (15 min): `docker compose build` / `up -d` / `ps` all healthy; `curl /api/products` through the Gateway; Eureka shows 7 services; images <= 300 MB.
  - Step 4 — Unit Test Verification (5 min): run `mvn test` from the host, all pass; update hardcoded localhost to `@Value` injection.
- Lecture-deck lab exercises (Part 2–7, practice, not graded per deck): Part 2 exercises 1–5 (install/verify, hello-world, nginx run, ps/ps -a, port mapping); Part 3 exercises 1–6 (pull nginx, postgres:16, redis:7; run nginx-demo 8080:80; lifecycle commands); Part 4 exercises 1–5 (first Dockerfile, build product-service, .dockerignore effects, layers/cache); Part 5 exercises 1–4 (multi-stage sizes, base image variants); Part 6 lab: write a compose for nginx/redis/postgres; Part 7 lab: compose for Config Server, Eureka, PostgreSQL, Gateway, Product Service; verify 8761/8080/8888.
- Demo (anchor deck): `docker build -t product-service:local .` -> 241 MB; run with `host.docker.internal` (Docker Desktop; on Linux add `--add-host=host.docker.internal:host-gateway`) and env `SPRING_PROFILES_ACTIVE=docker`, `SPRING_CONFIG_IMPORT=optional:configserver:...`, `EUREKA_CLIENT_SERVICE_URL_DEFAULTZONE`.
- HOMEWORK before S10: `docker compose down && docker compose up -d` and verify data persists (PostgreSQL named volume). Pre-reading: `@WebMvcTest`, `@DataJpaTest`, TestContainers guide (links in Session Pack). No commit name is stated for S9 homework in these decks.
- Daily Quiz (anchor deck): 8 questions / 5 minutes, Google Forms.
- MID-COURSE EXAM (anchor day): 120 minutes (~14:25–16:25 / stated as ~3:00–5:30 PM); Part A: 24 MCQ (Sessions 1–8, Analyze/Apply); Part B: practical coding. Tools allowed: course notes, Spring docs, IDE open, internet, AI tools. Submission: `git commit -m "mid-course-exam"` -> git push -> open Eureka on screen for the examiner.
