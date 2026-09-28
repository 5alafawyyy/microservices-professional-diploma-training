# Session 13 — CI/CD Pipelines with GitHub Actions

Source files:
- `Session_13 CI-CD with GitHub Actions.pdf` — long-form lecture deck (61 slides, numbered sections 1–90): CI/CD fundamentals, GitHub Actions anatomy, quality gates, Docker build & push, matrix strategy, Lab 13.
- `Session_13_CICD_Pipelines.pdf` — course delivery deck (31 slides): fail-fast decision tables, tagging strategy, Notification Service full implementation, Lab 11A, homework/checkpoint.

Source note: the two files are NOT duplicates. They are two decks for the same session (long-form theory vs. course delivery deck). They use different lab numbers for the same session (Lab 13 vs Lab 11A); both are recorded verbatim in section 17.

## 1. Why this topic exists

- Previous sessions built and containerized microservices: product-service, order-service, config-server, eureka-server, api-gateway. "But there is an important problem. How do we deliver new versions of our services?"
- Manual delivery steps: pull code, run tests, build app, build Docker image, choose tag, log in to registry, push image, tell someone, deploy. Mistakes are easy.
- The Friday 4 PM story (both decks): Ahmed builds with `mvn package -DskipTests` ("The code works on my machine"), SSHes to the server, stops the old app, copies the new JAR, starts it. It fails: server runs Java 17, he developed on Java 21. Rollback, 45 minutes lost; "everyone becomes nervous about deploying."
- Course-deck framing: "The real question: what is the cost of FEAR?" The team stops shipping on Fridays; features pile up; releases grow bigger and scarier.
- Four problems of manual deployment: (1) human error, (2) environment differences, (3) inconsistent process (Developer A: `mvn package`; B: `-DskipTests`; C: forgets push), (4) difficult auditing — CI/CD associates an image with a Git commit (e.g. `sha-a81c92d`), making releases traceable.
- Manual vs CI table: developer performs steps vs pipeline performs steps; developer's machine vs controlled runner; tests may be skipped vs always run; manual tagging vs consistent tagging; "Easy to make mistakes" vs Repeatable; "Fear of deployment" vs "Confidence in deployment."
- Key idea: "Automation is not only about saving time. It is about making the process repeatable and reliable."
- The pipeline is a safety system: "It protects the system from publishing code that has not passed the required checks."

## 2. Core concepts

- CI (Continuous Integration): developers frequently integrate code into a shared repository and automatically validate every change (tests run on each push).
- CD can mean Continuous Delivery (software is always ready to deploy) or Continuous Deployment (deployed automatically after checks). "For this course, we will separate the responsibilities."
- Pipeline: a sequence of automated operations; each stage has a responsibility: Git Push -> Checkout -> Compile -> Test -> Quality Gate -> Docker Build -> Docker Push -> Container Registry.
- Session 13 scope boundary: Code -> Test -> Build Docker Image -> Push Image to Registry. Deployment to Kubernetes belongs to the GitOps process of Session 14.
- GitHub Actions anatomy (course deck): `on:` trigger (push to main, pull_request, schedule, workflow_dispatch); `jobs:` collection of steps on one runner; `steps:` ordered commands; `runs-on:` the runner (VM/container, e.g. `ubuntu-latest`). "Jobs run in parallel by default — use `needs:` to order them." `uses:` = a packaged action; `run:` = a raw shell command.
- Terminology hierarchy: Workflow (complete automation process) > Job (group of related steps, e.g. `test`, `build-and-push`) > Step (one operation, e.g. Checkout code). Runner: the machine that executes the job (`runs-on: ubuntu-latest` = GitHub-hosted Ubuntu machine). Jobs can run independently or depend on each other via `needs`.
- Quality Gate: a condition that must be satisfied before the pipeline is allowed to continue. Tests FAILED -> STOP PIPELINE (fail-fast behavior). Tests PASS -> Docker Build -> Docker Push.
- `continue-on-error: true`: if a step fails, do not necessarily stop the job. Useful for informational checks (Checkstyle, SpotBugs, coverage report) — but NOT for main unit tests. Course rule: "Unit tests = blocking. Test failure -> pipeline failure."
- Blocking vs informational: blocking = unit tests, compilation, security vulnerability above policy threshold. Informational = coverage report, style report, static-analysis report (depending on team policy).
- Triggers: `push`, `pull_request`, manual (`workflow_dispatch:`), scheduled (e.g. nightly security check). Course focus: push + pull_request.
- Path filtering: in a multi-service repo (`services/product-service`, `services/order-service`, `payment-service`, `customer-service`), use `paths: - 'services/product-service/**'` so the Product Service CI does not run for changes to other services. Without paths, every push triggers CI for all services.
- Environment variables: `env:` block with `JAVA_VERSION: '21'`, `REGISTRY: ghcr.io`, `IMAGE_NAME: ${{ github.repository }}/product-service`, referenced as `${{ env.JAVA_VERSION }}` etc.
- Container registry: a service that stores container images (GHCR, Docker Hub, cloud provider registries). Registry acts as central storage: GitHub Actions -> docker push -> GHCR -> Kubernetes.
- Docker image: packaged application (Spring Boot app + JRE/JDK + dependencies + configuration + Dockerfile instructions) used to create containers.
- GHCR = GitHub Container Registry, address `ghcr.io`; image example `ghcr.io/my-company/product-service:sha-a81c92d`. Course uses GHCR because source code is already on GitHub. Docker Hub is conceptually the same purpose.
- Artifact: a produced output of a build process; in this pipeline the important artifact is the Docker image (`ghcr.io/company/product-service:sha-a81c92d`).
- Docker Buildx: Docker's extended build interface; advanced build features, build caching, multi-platform builds. "Buildx provides a modern Docker image building mechanism suitable for CI."
- Image tags: `latest` alone is not enough for reliable release tracking (today version A, tomorrow version B). Prefer Git commit SHA tags (`sha-a81c92d`) for traceability: which source-code commit created this image? Useful for debugging, rollback, auditing, deployment tracking.
- Tagging strategy (course deck): `sha-` prefix (traceable to exact commit — "Rule: tag with sha- for deployment traceability"), `latest` (convenience only; enabled only on push to main; "never deploy from it in production"), branch ref (e.g. `main`; useful for dev/staging).
- GitHub Secrets: protected values stored by GitHub (examples: DOCKER_USERNAME, DOCKER_TOKEN, AWS_ACCESS_KEY, API_KEY). Reference via `${{ secrets.MY_SECRET }}`. Security rule: "Never put passwords, tokens, or access keys directly inside the workflow YAML."
- `GITHUB_TOKEN`: a special token GitHub automatically provides for workflows; usable for GHCR when the workflow has the required package permissions; no manual Docker password needed for the GHCR example. For Docker Hub: store `DOCKER_USERNAME` / `DOCKER_TOKEN` as secrets instead.
- Matrix strategy: run the same job against multiple versions, e.g. `strategy: matrix: java: ['17','21']`; GitHub creates the combinations. Do not always use a matrix: "A matrix increases CI cost and execution time"; use it only when you intentionally support multiple versions. `fail-fast: true` can cancel in-progress matrix jobs when one fails.
- Notification Service (course deck, closing the S7 bonus loop): S7 bonus homework had `@KafkaListener` + `log.info("Email sent")`, no retry, no dead-letter queue, "Failure = silent event loss". S13 full implementation adds `@RetryableTopic` (3 attempts, exponential backoff), Dead Letter Topic (`.DLT`), Actuator health endpoint with Kafka status, and registration in Eureka + docker-compose + CI.

## 3. Architecture

- Session 13 pipeline (long deck ASCII):
  Developer -> git push -> GitHub Repository -> GitHub Actions (Checkout -> Build -> Test -> Quality Gate -> Docker Build -> Docker Push) -> Container Registry. "For this session, the pipeline stops here."
- Session 14 takes over: Container Registry -> GitOps Repository -> Argo CD -> Kubernetes Cluster. "This separation is extremely important."
- Two-job structure: `test` (Test & Quality Gate) -> PASS -> `build-and-push` -> GHCR. If test FAILS: build job SKIPPED -> no Docker image -> no push.
- CI vs GitOps responsibilities (long deck table): CI = build source code, run tests, build Docker image, push image, produce artifact, GitHub Actions. GitOps = manage desired deployment state, synchronize cluster, detect drift, apply manifests, deploy artifact, Argo CD. GitHub Actions answers "Can we build a valid artifact?"; Argo CD answers "Does the Kubernetes cluster match what Git says?"
- Engineering decision — should CI deploy directly?
  - Option A Push-based: CI -> Build -> Test -> Docker Push -> `kubectl apply` -> Kubernetes. Advantages: simple to understand, easy for small systems, fewer tools. Disadvantages: CI needs Kubernetes credentials; deployment logic coupled to CI; no natural drift detection; Git may not represent actual cluster state.
  - Option B GitOps: CI -> Test -> Build -> Push Image -> Registry; Git Manifest -> Argo CD -> Kubernetes. Advantages: Git becomes the desired-state source; strong audit trail; drift detection; deployment responsibility separated from CI; CI does not need direct cluster credentials. Disadvantages: more concepts, additional tooling, requires understanding GitOps and Argo CD.
  - "For our course: We choose GitOps because Kubernetes is our deployment platform and we want a professional deployment architecture."
- Why no `kubectl apply` here: "This is technically possible in a push-based CI/CD design. However, our course deliberately uses GitOps." CI: build image, push image, does NOT directly control Kubernetes. GitOps: watches Git, detects desired state, deploys to Kubernetes.
- Where S13 stops (course deck): "Code -> Test (Quality Gate) -> Build Image -> Push to Registry" — STOPS HERE. Then Session 14 GitOps: "Registry Image -> Update Git Manifest -> ArgoCD Sync -> Kubernetes Cluster."
- Most important mental model (long deck): Developer -> git push -> GitHub Repository -> GitHub Actions -> Checkout -> Build/Compile -> Tests (FAIL -> STOP; PASS ->) -> Docker Build -> Docker Image -> Container Registry.
- Full target architecture (cross-session): Developer -> GitHub Application Repository -> GitHub Actions (Test -> Quality Gate -> Docker Build -> Push Image) -> Container Registry; GitOps side: Git Manifest -> Argo CD -> Kubernetes -> Pods -> Microservices.

## 4. Technologies

- GitHub Actions (workflow YAML in `.github/workflows/`); GitHub-hosted Ubuntu runner (`runs-on: ubuntu-latest`).
- Actions and versions mentioned exactly as written in the slides:
  - `actions/checkout@v4`
  - `actions/setup-java@v4` (with `java-version: '21'`, `distribution: 'temurin'`, `cache: maven`)
  - `docker/setup-buildx-action@v3`
  - `docker/login-action@v3`
  - `docker/metadata-action@v5`
  - `docker/build-push-action@v5`
- GitHub Container Registry (GHCR, `ghcr.io`); `secrets.GITHUB_TOKEN`; GitHub Secrets; `github.actor`; workflow `permissions: contents: read, packages: write`.
- Docker Hub as the alternative registry (secrets DOCKER_USERNAME / DOCKER_TOKEN).
- Maven build commands: `mvn test -pl services/product-service -B` (`-pl` = build/test a specific Maven project in a multi-module repository; `-B` = batch mode, useful in CI, no interactive output).
- Java 21 (Temurin distribution) is the project baseline; Java 17 and 21 appear in the matrix example; the Friday story contrasts local Java 21 vs server Java 17.
- Docker Buildx; GitHub Actions build cache via `cache-from: type=gha` / `cache-to: type=gha,mode=max`; Maven dependency cache via `cache: maven` (~/.m2 between runs).
- Notification Service stack (course deck): `spring-boot-starter-web`, `spring-kafka`, `spring-cloud-starter-netflix-eureka-client`, `spring-boot-starter-actuator`; Spring Kafka `@RetryableTopic` / `@Backoff` / `@DltHandler` / `@KafkaListener`; Kafka topic `payment-events` (group `notification-service`), `inventory-events` (group `notification-service-cancel`); service port 8085; Config Server `http://localhost:8888`; Eureka `http://localhost:8761/eureka/`; docker-compose on `platform-net`.
- No other version numbers are stated in the slides (e.g. no Kafka/Spring Boot/Argo CD versions).

## 5. Important terminology

- Workflow, Job, Step, Runner (long deck: "Before writing YAML, learn these four terms.")
- Quality Gate; fail-fast; `continue-on-error`; `needs` (job dependency: "Do not start this job until the test job has successfully completed.")
- Trigger; path filtering; `env`; `uses` vs `run`; GitHub-hosted vs self-hosted runner.
- Container registry; GHCR; Docker Hub; registry authentication (`registry`, `github.actor`, `secrets.GITHUB_TOKEN`).
- Docker image; artifact; image tag; SHA tag (`sha-a81c92d`); `latest`; branch ref tag.
- `GITHUB_TOKEN`; GitHub Secrets; permissions (`contents: read`, `packages: write`).
- Matrix strategy; fail-fast matrix; blocking check; informational check.
- `@RetryableTopic`; exponential backoff (1s -> 2s -> 4s); Dead Letter Topic (`.DLT`); `@DltHandler`; `autoCreateTopics = "false"`.
- CI; Continuous Integration; Continuous Delivery; Continuous Deployment; GitOps (contrast); traceability (image <-> Git commit).

## 6. Code concepts

- Minimal first workflow: `name: Product Service CI`; `on: push: branches: [main]`; `jobs: test:`; `runs-on: ubuntu-latest`; steps Checkout code -> Set up Java -> Run tests.
- Pull request trigger added alongside push (`pull_request: branches: [main]`) — "detect problems before merging."
- Path filtering example for a specific service; multi-service repo layout (`services/product-service/` with `Dockerfile`, `pom.xml`, `src/`).
- `needs: test` on `build-and-push` — dependency between jobs; if test fails, build-and-push does not run: "TEST = QUALITY GATE."
- GHCR login step: `registry: ${{ env.REGISTRY }}`, `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}`.
- `docker/metadata-action` with `id: meta` generating tags: `type=ref,event=branch`, `type=sha,prefix=sha-`, `type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}`.
- `docker/build-push-action`: `context: services/product-service`, `push: true`, `tags: ${{ steps.meta.outputs.tags }}`, `labels: ${{ steps.meta.outputs.labels }}`, `cache-from: type=gha`, `cache-to: type=gha,mode=max`. Without `push: true` the image only exists on the temporary runner and disappears.
- Image naming structure: registry (`ghcr.io`) / repository image (`my-company/my-repository/product-service`) / tag (`sha-a81c92d`).
- Exercise 2 failing test: `void shouldFail() { assertEquals(1, 2); }` -> pipeline FAILED -> pipeline stops.
- Notification Service code: two `@KafkaListener` methods with `@RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000, multiplier = 2.0), dltTopicSuffix = ".DLT")`; a `@DltHandler` receiving `@Header(KafkaHeaders.RECEIVED_TOPIC) String topic` logging "exhausted all retries. Manual intervention required."; simulated email sending via logs (`sendConfirmationEmail`, `sendCancellationNotification`).
- Full complete workflow YAML is given in the long deck (section 61) and assembled across slides 8, 12, 14 of the course deck. Course guidance: "Do not memorize the YAML. Understand the flow."

## 7. Configuration

- Workflow file location: `.github/workflows/product-service-ci.yml` at the REPOSITORY ROOT. "It does NOT belong inside: services/product-service/.github/."
- Workflow-level `env`: JAVA_VERSION '21', REGISTRY `ghcr.io`, IMAGE_NAME `${{ github.repository }}/product-service`.
- Job-level `permissions` on build-and-push: `contents: read`, `packages: write` (required to push to GHCR).
- `runs-on: ubuntu-latest`; `cache: maven`; Java version from env.
- Course deck optimization notes: `cache: maven` caches `~/.m2` between runs; ensure `cache: maven` is set AND `pom.xml` is committed, otherwise the cache does not work.
- DEV-ONLY production note (course deck): "In production: add `--platform linux/amd64,linux/arm64` for multi-arch."
- Docker Hub alternative authentication via `secrets.DOCKER_USERNAME` / `secrets.DOCKER_TOKEN`.
- Notification Service `application.yml`: `server.port: 8085`; `spring.application.name: notification-service`; `spring.config.import: optional:configserver:http://localhost:8888`; `spring.kafka.bootstrap-servers: localhost:9092`; consumer `group-id: notification-service`, `auto-offset-reset: earliest`, String key/value deserializers; `eureka.client.service-url.defaultZone: http://localhost:8761/eureka/`; `management.endpoints.web.exposure.include: health,info,kafka`; `management.health.kafka.enabled: true` ("shows Kafka consumer status in /actuator/health").
- `docker-compose.yml` entry for notification-service: `build: ./services/notification-service`, `image: notification-service:local`, ports `["8085:8085"]`, `depends_on` eureka-server `service_healthy` and kafka `service_started`, environment `SPRING_CONFIG_IMPORT` / `EUREKA_CLIENT_SERVICEURL_DEFAULTZONE` / `SPRING_KAFKA_BOOTSTRAP_SERVERS`, `networks: [platform-net]`, healthcheck `curl -f http://localhost:8085/actuator/health` interval 10s, timeout 5s, retries 5.

## 8. Failure scenarios

- Test failure: 10 tests, 9 passed, 1 failed -> `mvn test` FAILED -> step fails -> job fails -> pipeline stops; "The Docker image should not be built. This is our Quality Gate."
- Tests fail and pipeline continues (if `continue-on-error` used wrongly): broken code reaches Docker build -> "We have created a deployable artifact from broken code. That defeats the purpose of automated testing."
- Friday incident pattern: skipped tests + JDK mismatch (laptop 21 vs server 17) -> ClassCastException -> rollback; cost = 45 minutes plus fear of deploying.
- DLT / retry exhaustion: attempt 1 fails -> wait 1s -> attempt 2 fails -> wait 2s -> attempt 3 fails -> wait 4s -> `@DltHandler` -> `payment-events.DLT` -> `log.error("Manual intervention required")`. "Failed events are never silently dropped."
- Common issues & solutions (course deck): "permission denied" pushing to GHCR (add `packages: write`); Maven cache not working (ensure `cache: maven` AND pom.xml committed); paths filter ignores all pushes (use `**` recursive matching); "No method annotated with @DltHandler found" (@DltHandler must be in the SAME class as @KafkaListener); DLT messages not appearing after 3 retries (verify `autoCreateTopics='false'` and the `.DLT` topic exists).
- Troubleshooting guide (long deck): workflow does not start (check `.github/workflows/`, YAML committed and pushed, are you actually pushing to main); Maven cannot find the project (path must match actual project structure, run from repository root); Java version mismatch (compare `java-version: '21'` with project); GHCR permission denied (check permissions block and GITHUB_TOKEN); Dockerfile not found (check `context: services/product-service` and Dockerfile location).

## 9. Trade-offs

- Matrix strategy: supports multiple Java versions automatically vs increases CI cost and execution time; "Use a matrix when: We intentionally support multiple versions. Do not use it just because the feature exists." Course example: production standardized on Java 21 -> testing only Java 21 may be sufficient.
- fail-fast matrix (`strategy: fail-fast: true`): with Java 17 FAIL / Java 21 PASS, GitHub can cancel in-progress matrix jobs when one fails; acceptable trade-off depends on whether both results matter.
- fail-fast vs allow-failure in Quality Gates (course deck): Option A `fail-fast: true` (default, recommended) — fastest feedback (developer knows within 3 minutes), no broken Docker image pushed, but a matrix sibling run may be cancelled. Option B `continue-on-error: true` — for quality REPORTS, not gates; if used on unit tests, broken code reaches the Docker build.
- Decision table (course deck): critical service / failure must block -> fail-fast; optional check reviewed manually -> allow-failure; coverage threshold breached -> fail-fast; experimental linting rule still tuning -> allow-failure. "Never use continue-on-error on the test step — 'tests passing' must mean what it says."
- Blocking vs informational checks: "Is this check a release requirement or an informational report?"
- Push-based deployment vs GitOps (full comparison in section 3). Course chooses GitOps despite "more concepts / additional tooling."
- Docker Hub vs GHCR: conceptually same main purpose; course uses GHCR because source code is already hosted on GitHub.
- SHA tag vs latest: `latest` is convenient but not traceable; immutable/traceable SHA tag is important; may still publish `latest` for convenience.
- Manual vs automated table: reproducible runner, tests always run, consistent tagging, Git + pipeline history, confidence — at the cost of adopting and maintaining a pipeline.

## 10. Common mistakes

From "Common Beginner Mistakes" (long deck):
1. Putting the workflow in the wrong location: `services/product-service/.github/workflows/` instead of repo-root `.github/workflows/`.
2. Forgetting `needs` — jobs may run independently when build must wait for tests.
3. Allowing tests to fail — using `continue-on-error: true` on the main test step; then "Tests fail -> Pipeline continues -> Docker image created."
4. Hardcoding secrets (`password: MyPassword123` instead of `${{ secrets.DOCKER_TOKEN }}`).
5. Using only `latest` — does not tell which Git commit produced the image.
6. Building before testing — "Code -> Docker Build -> Test" instead of "Code -> Test -> Docker Build." There is no reason to build and publish an image for code that failed its Quality Gate.

From "5 Errors You Will Hit" (course deck): GHCR permission denied; Maven cache not working; paths filter with wrong glob; @DltHandler in a different class than @KafkaListener; DLT topic missing.

## 11. Interview questions

The slides contain no labeled interview/exam section. The questions below are derived strictly from this session's learning objectives, "Important Concepts to Remember," and exercises:
- What is CI, and what is CD? What is the difference between Continuous Delivery and Continuous Deployment?
- Why is manual deployment risky? Name the four problem categories.
- Explain Workflow / Job / Step / Runner in GitHub Actions.
- What is a Quality Gate, and why must tests stop the pipeline (fail-fast)?
- What does `needs: test` do? What happens to `build-and-push` when tests fail?
- When is `continue-on-error: true` appropriate, and when is it dangerous?
- Why tag images with a Git SHA instead of only `latest`? What does that enable (traceability, rollback, auditing)?
- What is a container registry? Why does this course use GHCR over Docker Hub?
- Why does Session 13 stop at the container registry instead of running `kubectl apply`?
- Compare push-based deployment vs GitOps — advantages and disadvantages of each.
- How do you authenticate a workflow to GHCR without hardcoding a password? What is `GITHUB_TOKEN` and what permissions are required?
- What is a matrix strategy and when should you NOT use one?
- What is `@RetryableTopic` with a DLT, and why is silent event loss unacceptable? (Notification Service)

## 12. What I must memorize

- The exact definitions from "Important Concepts to Remember": GitHub Actions (GitHub's automation platform for executing workflows), Workflow (complete automation process defined in YAML), Job (group of steps executed together on a runner), Step (individual operation inside a job), Runner (machine that executes a job), Quality Gate (condition that must pass before the pipeline continues), Container Registry (service that stores and distributes container images), GHCR, Docker Image, SHA tag, `needs` (dependency between jobs).
- The pipeline order: Checkout -> Build/Compile -> Tests -> Quality Gate -> Docker Build -> Docker Image -> Container Registry; FAIL branches to STOP.
- The 6 beginner mistakes.
- The action names and major versions used: checkout@v4, setup-java@v4, setup-buildx-action@v3, login-action@v3, metadata-action@v5, build-push-action@v5.
- Workflow location rule: `.github/workflows/` at the REPOSITORY ROOT.
- Blocking vs informational classification (unit tests = blocking).
- "Do not memorize the YAML. Understand the flow." (slide instruction — memorize the flow, not the YAML text.)

## 13. What I must understand

- Why each pipeline stage exists and what fails when it is skipped.
- Why tests are a Quality Gate and why fail-fast gives the fastest feedback.
- The difference between `needs` (job ordering) and `continue-on-error` (step failure policy).
- Why jobs run in parallel by default and why that matters in a multi-job workflow.
- Trigger semantics (push vs pull_request vs workflow_dispatch vs schedule) and path filtering in a monorepo of services.
- Why traceability (image <-> commit) matters for debugging, rollback, auditing, deployment tracking.
- Why the registry is the boundary between CI (Session 13) and GitOps (Session 14); why CI should not hold cluster credentials.
- The full DLT flow: retries with exponential backoff, then the dead letter topic.
- That "automation is about repeatability and reliability," not only saving time.

## 14. What I should implement from memory

- Create `.github/workflows/product-service-ci.yml` with push + pull_request triggers, path filtering, env block.
- A `test` job: checkout, set up JDK 21 (temurin, maven cache), run `mvn test -pl services/product-service -B`.
- Demonstrate the Quality Gate: break a test, push, verify the pipeline stops; fix, push, verify PASS.
- Add the `build-and-push` job with `needs: test`, `permissions: contents: read / packages: write`, Buildx setup, GHCR login with `github.actor` + `secrets.GITHUB_TOKEN`.
- Configure `docker/metadata-action` (branch tag, sha tag, latest on main) and `docker/build-push-action` with context, push, tags, cache.
- Verify the image in GitHub Packages and match the SHA tag to the triggering commit.
- Implement the Notification Service from memory: `@RetryableTopic` (3 attempts, exponential backoff), `@KafkaListener` on payment/inventory events, `@DltHandler` in the same class, application.yml, docker-compose entry, Eureka registration.

## 15. Relationship to previous sessions

- S9 Docker: every core service has a multi-stage Dockerfile; `docker compose up -d` starts the platform reproducibly. This session automates the JAR -> image -> registry path that was manual.
- S10 + S11: unit, slice, integration (TestContainers), contract (Pact) and chaos-validated resilience tests — these are the tests that become the Quality Gate in CI.
- Recap used in both decks: "Sessions 9-12 shipped a containerized, tested, orchestration-ready platform. Session 13 automates the path from commit to registry." S12 introduced Saga Orchestration (OrderSagaOrchestrator), naming the services (order, payment, inventory) that appear in the notification examples.
- S7 bonus: the Notification Service existed only as bonus homework (@KafkaListener + log.info, no retry, no DLT). Session 13 turns it into a full production implementation ("Closing the S7 bonus loop").
- The multi-service repo structure (services/product-service, order-service, payment-service, customer-service) and the polyrepo/module layout from earlier sessions is assumed by the path-filtering discussion.

## 16. Relationship to future sessions

- Session 14 (next, Monday 3:00–5:30 PM, Online): "GitOps & Deployments: ArgoCD + Deployment Strategies". Pre-Session 14 reading topic: "GitOps with ArgoCD + Kubernetes Deployment basics" with questions: Push-based vs pull-based deployment? What is `drift` in Kubernetes? What does a Deployment control?
- The registry artifact produced here is the input to Session 14: "Registry Image -> Update Git Manifest -> ArgoCD Sync -> Kubernetes Cluster."
- Lab challenge note: two SHA tags become useful later for "Deployment, Rollback, GitOps".
- Course deck closing: "Next: Session 14 — GitOps & Deployments: ArgoCD + Deployment Strategies."

## 17. Lab relationship

Long-form deck — "Lab 13 — Automate Product Service CI":
- Goal: create a complete CI pipeline for product-service that: (1) runs on changes to Product Service, (2) checks out the repository, (3) installs Java 21, (4) runs Maven tests, (5) stops when tests fail, (6) builds the Docker image, (7) tags the image using the Git SHA, (8) authenticates with GHCR, (9) pushes the image to GHCR.
- Lab Task 1: create `.github/workflows/product-service-ci.yml` with the trigger and `jobs: test:`.
- Lab Task 2: configure Java 21, Temurin, Maven cache.
- Lab Task 3: add `mvn test -pl services/product-service -B`, push, check GitHub Actions (expected: Checkout -> Setup Java -> Run tests all succeed).
- Lab Task 4: break a test on purpose, push, expect Test FAIL -> Pipeline stops, Docker build should not run; then fix and push, expect Test PASS.
- Lab Task 5: add `build-and-push:` job with `needs: test`, `runs-on: ubuntu-latest`, configure Docker Buildx.
- Lab Task 6: add permissions (contents: read, packages: write) and GHCR login.
- Lab Task 7: configure `docker/metadata-action` and `docker/build-push-action`; push to `ghcr.io` with SHA-based tag.
- Verify the image in the GitHub package/container section (`product-service`, tag `sha-a81c92d` style) and verify traceability (commit a81c92d -> image `product-service:sha-a81c92d`).
- Lab Challenge: modify product-service and push a second change; second tag appears (e.g. sha-a81c92d / sha-b72f410) — "two identifiable versions."
- Exercises before the lab: Exercise 1 — Create the CI Workflow (commit `"Add product service CI workflow"`, push, observe the Actions tab); Exercise 2 — Make a Test Fail (failing assert, then fix).

Course deck — "Lab 11A — CI Pipeline for Platform Services":
- Step 1: Create `.github/workflows/product-service-ci.yml` — test + build-and-push jobs.
- Step 2: Implement notification-service: `@RetryableTopic` + `@DltHandler` + docker-compose entry.
- Step 3: Register NOTIFICATION-SERVICE in Eureka; verify it appears in the dashboard.
- Acceptance Criteria: broken test push -> pipeline shows failure, build-and-push does NOT run; fixed code -> image appears in GHCR tagged `sha-` and `latest`; `@RetryableTopic`: 3 attempts, exponential backoff configured; `@DltHandler` present and logs DLT events.
- Demos in the deck: (a) "Push Broken Code -> Quality Gate Fails" (build-and-push SKIPPED because needs: test failed); (b) "Quality Gate Passes -> Image Pushed to GHCR" (images `ghcr.io/org/product-service:sha-abc1234` and `:latest` visible in GitHub Packages).
- Homework / closing items: Daily Quiz — 8 questions, 10 minutes. Definition of Done — Session 13: `product-service-ci.yml` triggers on push + PR; broken test -> pipeline stops (Quality Gate working); image pushed to GHCR with sha- tag; notification-service @RetryableTopic + DLT; Commit: `session-13: add-ci-pipeline...` (message truncated in the slide). Pre-Session 14 reading (see section 16).
- Checkpoint commit convention shown: `session-13: add-ci-pipeline...` (the slide truncates the remainder with "...").
- Project progress: "Enterprise E-Commerce Platform — After Session 13: CI pipeline (GitHub Actions) + Notification Service officially complete. All 8 services now complete." New: notification-service (port 8085): @RetryableTopic + @DltHandler + `.github/workflows/*.yml` added.
