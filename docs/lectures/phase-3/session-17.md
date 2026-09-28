# Session 17 — Observability Deep Dive

Source files: `Session 17 Observability Deep Dive.pdf`, `Session_17_Observability.pdf`

File check: the two files differ in size and page count (61-page detailed session document vs 29-slide instructor deck) — both were read in full. The slide deck adds session logistics, engineering-decision tables, Lab 13, demo scripts, daily quiz and a common-issues table; the deep-dive document adds the full narrative, Checkpoints 1–2, a troubleshooting part and a 7-task student lab.

Session logistics (from slide deck): Offline Anchor Day — 5 hours, Wednesday 10:00–3:00, Phase 3 — Advanced & Enterprise, Session 17 of 29. It is the third Offline Anchor Day (after Sessions 1 and 9).

## 1. Why this topic exists

- In previous sessions the platform gained: Spring Cloud Gateway, Service Discovery, Centralized Configuration, Circuit Breakers, Retries and Fallbacks, Bulkheads, OpenFeign, Kafka, Distributed Sagas, Caching, Testing, Docker. The platform is now distributed — "a major achievement" that "also creates a new problem".
- A request now travels through multiple services: Client -> API Gateway -> Order Service -> {Inventory Service, Kafka -> Payment Service}. "If something fails, where do we look? Which service was slow? Which service generated the error? How do we find every log related to one specific request?"
- The 9-Second Order story: a customer says "I placed an order. It took 9 seconds. I am not even sure whether it worked." Investigating means manually comparing timestamps across Gateway, Order, Inventory, Payment and Kafka consumer logs. "Without observability, you are guessing."
- Monitoring vs Observability: Monitoring answers questions we already know to ask ("Is CPU above 80%?", "Is Order Service UP?") using dashboards, alerts, health checks, metrics; it tells us "Something is wrong." Observability helps answer questions we did not know in advance ("Why did THIS specific order take 9 seconds?"); it tells us "Here is where and why something happened." "You cannot buy Observability as a single dashboard."
- Slide-deck root cause framing: "Resilience Made the System More Robust — and More Opaque." Every retry, fallback and async Saga step (Sessions 4–7, 12) hides the true request path from a flat log file. Class question: "If every service printed its own timestamp and its own request ID, would that solve the problem?" — No: request IDs must be the SAME id, generated once and propagated, not invented independently by each service.
- Why now (OBG-001): Zipkin has been running in docker-compose since Session 1 "doing nothing for you". OBG-001 (Session 1): infrastructure must not be introduced before its teaching session — even if it is technically running. There was nothing worth tracing until real cross-service complexity existed: no Gateway (S2), no resilience (S4–5), no Feign (S6), no Saga (S7).

## 2. Core concepts

- The Three Pillars of Observability — Metrics, Traces, Logs; none replaces the others:
  - Metrics: "How is the system behaving over time?" (CPU, JVM memory, request count, error count, request duration). "Metrics tell you SOMETHING is wrong."
  - Traces: "Where did this specific request spend time?" / "Where in the request path did time go? Which service, which call?" "Traces tell you WHERE."
  - Logs: "What exactly happened, in detail, at one point in the code?" "Logs tell you WHY."
- The complete investigation flow: METRICS (something is wrong) -> TRACES (where is the problem?) -> LOGS (why did it happen?) -> ROOT CAUSE.
- Trace: the complete journey of ONE request (e.g. POST /api/orders through Gateway -> Order -> Inventory -> Kafka -> Payment). Identified by a single Trace ID shared by every span (example id: 7a3f9c2b1e8d4f6a).
- Span: ONE unit of work within that journey (e.g. "Gateway request", "OrderService.createOrder()", "Feign call to Inventory", "Kafka event publishing", "Payment Kafka consumer"). Each span has its own Span ID and a reference to its PARENT span.
- Parent/child spans form a hierarchy (Gateway Span -> Order Service Span -> Inventory Feign Span + Kafka Producer Span -> Payment Consumer Span). This lets tools show the complete request path.
- Trace context propagation: the context must travel with the request. Context contains Trace ID, Current Span ID, parent information. HTTP propagation uses standard headers such as `traceparent` (W3C format). Kafka propagation carries trace context in Kafka message headers so the trace continues across asynchronous boundaries (consumer may run on another thread, in another service, later in time). Micrometer Tracing auto-instruments Feign, RestTemplate, WebClient and Spring Kafka once the bridge dependency is present — "you rarely write propagation code by hand."
- Sampling: tracing every request creates a large amount of data, so tracing systems may sample. 1.0 = 100% (trace every request); 0.1 = 10%. Course setting: `management.tracing.sampling.probability: 1.0`, appropriate for local development, learning, testing. Production must choose by traffic, storage, cost, operational requirements.
- Micrometer: a metrics abstraction layer — analogy "SLF4J for Metrics" (write metrics code once; swap Prometheus/Datadog/CloudWatch underneath). Spring Boot Actuator already includes Micrometer; `/actuator/circuitbreakers` (S4) and `/actuator/bulkheads` (S5) endpoints are also powered by Micrometer underneath.
- Metric types: Counter — "How many times did X happen?" (monotonically increasing; e.g. orders created, payments failed, messages consumed). Gauge — "What is the current value right now?" (moves both directions; e.g. active users, queue size, bulkhead available-concurrent-calls). Timer — "How long did X take?" plus distribution (count, total time, maximum time, distribution; e.g. order creation duration, database query duration, HTTP request duration).
- Metric tags: metrics can have tags (e.g. `service=order-service`, `status=success` / `status=failed`) to filter and group. Rule: do not use highly unique values as tags (high cardinality).
- Prometheus pull model: Prometheus periodically requests ("scrapes") metrics from the service's `/actuator/prometheus` endpoint (e.g. every 15 seconds). "Prometheus = Pull Metrics. Zipkin = Receive Trace Spans (pushed)." Neither model is "better" — they are simply how each tool was designed.
- Grafana: visualization layer on top of Prometheus (or any data source) — dashboards, graphs, alerts. "Grafana does not collect metrics itself; it queries Prometheus."
- Structured logging: plain-text logs are acceptable for one application/one log file, but across many services "searching plain text becomes difficult". Structured logging represents log information as fields (timestamp, level, service, traceId, spanId, message). Trace and log correlation: Micrometer tracing integrates the tracing context with the logging context, commonly represented via MDC (Mapped Diagnostic Context); logs then contain traceId/spanId — the span IDs differ but the trace ID connects the complete request ("Log Correlation").
- Structured logging vs centralized logging: this session covers Structured JSON Logs + Trace Correlation only. A complete centralized logging platform (ELK-based) is explicitly NOT built in this session — it is a production concern with real infrastructure cost; "What you're building today is the PREREQUISITE for ELK, not ELK itself."

## 3. Architecture

- Final observability architecture (deep-dive Part 10):
  - GRAFANA (Dashboards) --Queries--> PROMETHEUS (Time-Series Data) --Scrapes--> Order Service / Product Service / Inventory Service (`/actuator/prometheus`).
  - Client -> API Gateway -> Order Service -> {Inventory Service, Kafka -> Payment Service}; all services push Distributed Trace Spans to ZIPKIN (Distributed Request Map); all services produce JSON Logs with traceId + spanId to Console / File Logs.
- Metrics flow: Application -> Prometheus -> Grafana. Grafana queries Prometheus; it does not normally collect metrics from the Spring Boot service.
- Containers (from compose examples): zipkin (9411), prometheus (9090), grafana (3000), all on `platform-net` (bridge). Example target addresses used in the course: Order Service 8082, Product Service 8081; Gateway on 8080.
- Zipkin flow: services create spans -> send spans -> Zipkin -> Zipkin UI, answering "Which service was slow? How long did every operation take? Where did the request fail?"

## 4. Technologies

(Only what the slides actually mention.)
- Micrometer: `micrometer-tracing-bridge-brave` (maven groupId io.micrometer), `micrometer-registry-prometheus`; `io.micrometer.core.instrument.Counter`, `MeterRegistry`; annotation `io.micrometer.core.annotation.Timed` (requires a `TimedAspect` bean in some configurations — deep-dive Part 10, slide 18).
- Zipkin: image `openzipkin/zipkin:latest`; UI http://localhost:9411; span endpoint http://localhost:9411/api/v2/spans, `io.zipkin.reporter2:zipkin-reporter-brave`.
- Prometheus: image `prom/prometheus:latest`; UI/API http://localhost:9090; config mounted as `prometheus/prometheus.yml`; `global: scrape_interval: 15s`; PromQL.
- Grafana: image `grafana/grafana:latest`; http://localhost:3000; default local Docker login commonly admin/admin (change may be requested); Prometheus data source URL http://prometheus:9090; community dashboard import example ID 12900 ("Spring Boot Statistics") — slide deck.
- Logging: Logback; `net.logstash.logback:logstash-logback-encoder` (slide deck pins version 7.4; the deep-dive says versions should be managed through the project's dependency-management strategy); `logback-spring.xml`; MDC.
- Spring Boot Actuator: must already be present (since Session 1); `spring-boot-starter-actuator`; exposure list includes health, info, prometheus (slide deck also keeps circuitbreakers, bulkheads).
- Docker / Docker Compose; Spring Kafka (already on classpath since Session 7; auto-instrumented for tracing).
- W3C `traceparent` header format for HTTP propagation.
- Not mentioned anywhere in these decks: specific Spring Boot version, Java version, Zipkin/Prometheus/Grafana version pins (images use `:latest`).

## 5. Important terminology

- Monitoring / Observability; Five-Minute style question split: known vs unknown questions.
- Trace, Span; Trace ID (identifies the complete distributed request); Span ID (identifies one operation inside the trace); parent/child span hierarchy.
- Trace context propagation; `traceparent`; Kafka header propagation; auto-instrumentation.
- Sampling (probability); error-based sampling override.
- Micrometer; MeterRegistry; Counter / Gauge / Timer; metric tags (labels); high cardinality; `@Timed`; TimedAspect.
- Scraping; pull model (Prometheus) vs push model (Zipkin); time-series database; PromQL; `rate(...)`.
- Waterfall view (Zipkin); "Distributed Request Map" (deep-dive wording for Zipkin).
- Structured JSON logging; MDC (Mapped Diagnostic Context); Log Correlation; centralized logging (ELK) as out-of-scope.
- Service name (`spring.application.name`) — used by observability tools to identify the service.

## 6. Code concepts

- Dependencies (pom.xml) for every participating service: `micrometer-tracing-bridge-brave`, `zipkin-reporter-brave`, actuator already present; later `micrometer-registry-prometheus`; logging: `logstash-logback-encoder`.
- `OrderMetricsService` — a `@Component` injecting `MeterRegistry`, building a Counter: `Counter.builder("orders.created").description("Number of successfully created orders").register(meterRegistry)`, with `incrementOrdersCreated()` calling `counter.increment()`. Inject into order-processing logic after successful creation.
- `@Timed(value = "order.create.duration", description = "Time required to create an order")` on a `@PostMapping` controller method returning `CompletableFuture<ResponseEntity<OrderResponse>>`; deep-dive note: annotation-based timing may require registering a `TimedAspect` bean in a `@Configuration` (`new TimedAspect(meterRegistry)`) — "Add this only when required by your project's configuration. Always verify the actual metric output."
- Metric tags via builder (e.g. status=success/failed); warning against `.tag("orderId", orderId)`.
- `logback-spring.xml`: `ConsoleAppender` + `net.logstash.logback.encoder.LogstashEncoder` with `<includeMdcKeyName>traceId</includeMdcKeyName>` and `<includeMdcKeyName>spanId</includeMdcKeyName>`; root level INFO. "Micrometer Tracing automatically populates MDC with traceId/spanId — no extra code needed."
- Verification code concepts: `curl -X POST http://localhost:8080/api/orders` with JSON body (productId PROD-001, quantity, amount); Zipkin query by Service Name -> order-service -> Run Query; a 50-iteration curl loop generated Grafana load; grep `'"traceId":"7a3f9c2b1e8d4f6a"'` across all service log files to find every line for one request.

## 7. Configuration

- Tracing (per service, application.yml):
  - `management.tracing.sampling.probability: 1.0`
  - `management.zipkin.tracing.endpoint: http://localhost:9411/api/v2/spans`
  - `spring.application.name: order-service` (already set since Session 1) — "shown as the service name in Zipkin UI".
- Actuator exposure (deep-dive): `management.endpoints.web.exposure.include: health,info,prometheus`; slide-deck version keeps existing endpoints: `health,info,prometheus,circuitbreakers,bulkheads`.
- prometheus.yml: `global.scrape_interval: 15s`; scrape_configs jobs `order-service` (metrics_path `/actuator/prometheus`, target `order-service:8082`) and `product-service` (target `product-service:8081`).
- Docker networking rule (called "extremely important"): inside the Prometheus container, `localhost` means the container itself, not your machine; use the Docker service/container hostname (`order-service:8082`). Same rule for Grafana: do not use `http://localhost:9090`; use `http://prometheus:9090`. Common-issues table also says: from inside a container use `http://zipkin:9411/api/v2/spans` (Docker hostname), not localhost.
- docker-compose additions: prometheus (volume `./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml`, port "9090:9090", network platform-net), grafana (port "3000:3000", network platform-net), zipkin ("9411:9411"); network `platform-net: driver: bridge`. Do not replace existing platform compose config (PostgreSQL, Config Server, Eureka, Kafka, Redis) — add observability services to it.
- Start commands: `docker compose up -d prometheus grafana`; `docker compose ps` to verify; `docker compose ps | grep zipkin` (running since Session 1).

## 8. Failure scenarios

- Zipkin Shows No Traces: check `docker compose ps`, Zipkin UI at :9411, tracing dependencies, sampling probability 1.0, Zipkin endpoint, and that a real request reaches the application.
- Zipkin Shows Only One Service: does the request actually call the second service; are tracing dependencies present in both; is propagation working; is the second service configured and sending spans.
- Trace missing spans from a downstream service (slide deck): that service is missing `micrometer-tracing-bridge-brave` or `sampling.probability` is 0.
- Kafka Saga spans don't share the HTTP request's traceId: both producer AND consumer service need the tracing bridge on the classpath.
- Prometheus Target Is DOWN: check http://localhost:9090/targets; verify `http://SERVICE:PORT/actuator/prometheus`; service running; correct port; Prometheus can reach the service; Docker networking correct; actuator exposure includes prometheus. Slide deck: use the Docker Compose service name (product-service:8081), not localhost. "Do not continue until the target is UP."
- Grafana Cannot Connect to Prometheus: Grafana container's localhost means the Grafana container; use http://prometheus:9090 when both are on the same network; verify both containers running.
- Custom Metric Does Not Appear: did the code execute; did the counter increment; application restarted; checking `/actuator/prometheus`; is Prometheus scraping; generate several requests and check again.
- @Timed metric never appears in /actuator/prometheus: missing the TimedAspect @Bean — "same AOP requirement as Resilience4j (Session 4)".
- Logs Do Not Contain Trace IDs: check Micrometer tracing dependency, active request context, JSON logging configuration, MDC fields in the encoder, application restart. "A trace ID exists during a traced operation. A log created outside a traced context may not have the same correlation information."
- (Checkpoint gating) "Do not continue until this works" after Checkpoint 1 (tracing) and "Do not continue until the target is UP" before Checkpoint 2 (Prometheus targets).

## 9. Trade-offs

- Sampling rate (slide-deck engineering decision): local development/course -> probability 1.0; low-traffic production (<100 req/s) -> 1.0 often still affordable; high-traffic production (thousands req/s) -> 0.05–0.10; need to guarantee every ERROR traced -> error-based sampling override; Zipkin storage/network becoming a bottleneck -> "Lower the sampling probability, not the trace detail per request."
- Structured (JSON) vs plain-text logging: high-traffic production -> structured mandatory; small team reading logs on one machine -> plain text often OK; centralized log aggregation (ELK/Loki) planned -> structured is a mandatory prerequisite; multiple services/cross-service queries -> structured mandatory (grep by traceId). Platform default chosen: structured logging with traceId/spanId correlation.
- Pull (Prometheus) vs push (Zipkin): "Neither model is 'better' — they are simply how each tool was designed."
- Imported Grafana dashboards: never assume an imported dashboard works perfectly with every Spring Boot app — metric names, labels, Micrometer versions and application configuration can differ. "First understand your metrics. Then build a simple dashboard. Then optionally import dashboards."
- Structured logging vs centralized logging: centralized ELK is a production concern with real infrastructure cost — beyond course scope; JSON logs + correlation are the prerequisite.
- Deep-dive framing: tracing every request creates a large amount of data; in high-traffic production the sampling strategy should follow traffic, storage, cost and operational requirements.

## 10. Common mistakes

- Using high-cardinality values as metric labels — orderId, customerId, email, traceId, random UUID — "Prometheus must store a huge number of unique time series. This is called high cardinality." Good tags have a limited number of possible values (status=success/failed).
- Using `localhost` inside containers (Prometheus scrape targets, Grafana data source, Zipkin endpoint from inside a container).
- Assuming an imported community dashboard will just work; skipping the "understand your metrics first" step.
- Forgetting that a running service must be restarted after dependency/config changes before metrics/traces appear.
- Using @Timed without the TimedAspect bean where the project configuration requires it; not verifying actual metric output.
- Expecting a trace ID in every log line — logs created outside a traced operation have no correlation context.
- Inventing per-service request IDs instead of propagating one shared trace ID (class discussion, slide 5).
- Not checking the actual port of a service when verifying `/actuator/prometheus` ("The port depends on your Order Service configuration").
- Replacing the existing Docker Compose platform configuration instead of adding observability services to it.

## 11. Interview questions

(Phrased from what the slides teach.)
- What is the difference between monitoring and observability? Give an example question each can answer.
- Name the Three Pillars of Observability and the main question each answers. Why is one pillar alone not enough?
- What is a trace? What is a span? How are trace ID and span ID related?
- How does trace context propagate over HTTP? Over Kafka? Why does Kafka header propagation matter?
- Why would you lower the sampling probability in production, and what would you lower instead of per-request detail?
- What is Micrometer, and why is the "SLF4J for metrics" analogy useful?
- Difference between Counter, Gauge and Timer — give a platform example of each.
- Why is Prometheus described as pull-based and Zipkin as push-based? Which direction does each data type flow?
- What is high cardinality and why is it dangerous in Prometheus? Which tag values must you avoid?
- What is MDC and how does it connect logs to traces?
- How would you investigate "an order took 9 seconds" end to end using metrics, traces and logs?
- Why does Docker `localhost` not mean what you expect inside a container? What do you use instead?
- Why has Zipkin been running since Session 1 if it was only used in Session 17? (OBG-001 principle.)

## 12. What I must memorize

- Definitions: Trace, Span, Trace ID, Span ID, parent/child spans; sampling probability values 1.0 / 0.1 and the course choice 1.0.
- The pillar-to-question mapping: Metrics = "something is wrong"; Traces = "where (in the request path)"; Logs = "why".
- Dependency names: `micrometer-tracing-bridge-brave`, `zipkin-reporter-brave`, `micrometer-registry-prometheus`, `logstash-logback-encoder`.
- Configuration keys: `management.tracing.sampling.probability`, `management.zipkin.tracing.endpoint` (http://localhost:9411/api/v2/spans), `management.endpoints.web.exposure.include`, `spring.application.name`.
- Default ports/URLs: Zipkin 9411, Prometheus 9090, Grafana 3000; `/actuator/prometheus`.
- Counter = monotonic count; Gauge = current value (up and down); Timer = duration + distribution.
- Pull vs push: Prometheus scrapes (pull) every 15s; services push spans to Zipkin.
- Grafana data source URL inside Docker: http://prometheus:9090.
- The observability workflow order: Metrics -> Traces -> Logs -> Root Cause.
- The three checkpoint-2 items: /actuator/prometheus works, targets UP, PromQL returns metrics.

## 13. What I must understand

- Why distributed tracing only becomes meaningful once real cross-service complexity exists (Gateway S2, resilience S4–5, Feign S6, Saga S7) — and why infrastructure may exist before its teaching session but stay unused.
- Why a request ID invented independently per service does not solve correlation; one ID must be generated once and propagated (HTTP headers, Kafka headers).
- Why Micrometer Tracing needs almost no custom code — how auto-instrumentation of Feign/RestTemplate/WebClient/Spring Kafka works conceptually.
- Why the metrics -> trace -> logs sequence is the operational workflow, and how to read a Zipkin waterfall to identify a slow span.
- Why sampled tracing is a cost/observability trade-off; what error-based sampling means.
- Why high-cardinality labels break Prometheus storage (unique time series explosion).
- Why MDC/traceId correlation is the prerequisite for a later ELK-style platform, and why ELK itself is out of scope in this session.
- How Docker networking makes service-name addressing (order-service, prometheus, zipkin) different from localhost.
- Why service names matter for identifying services in Zipkin.

## 14. What I should implement from memory

(Buildable directly from the slides.)
- Add tracing dependencies + sampling/zipkin config + service name to Gateway, Order, Product, Inventory, Payment services; restart; generate a request; find the trace in Zipkin; read the waterfall.
- Verify Kafka Saga spans join the same trace as the HTTP request.
- Add `micrometer-registry-prometheus`; expose the actuator endpoint; verify `/actuator/prometheus` output shows `jvm_memory_used_bytes`, `http_server_requests_seconds_count`, `http_server_requests_seconds_sum`.
- Create a custom Counter (`orders.created`) via MeterRegistry; verify `orders_created_total` appears.
- Register a TimedAspect bean and apply @Timed to a critical endpoint.
- Write prometheus.yml with two scrape jobs; add Prometheus + Grafana containers to compose on platform-net; verify targets UP.
- PromQL from memory: `orders_created_total`, `rate(http_server_requests_seconds_count[1m])`, `rate(sum[1m]) / rate(count[1m])`.
- Grafana: add Prometheus data source (http://prometheus:9090), Explore, and a dashboard with the 4 panels: request rate, request duration, order count, JVM memory.
- Structured logging: logback-spring.xml with LogstashEncoder + traceId/spanId MDC keys; verify multiple services log the same trace ID and that it matches the Zipkin trace.

## 15. Relationship to previous sessions

- Builds on the whole platform built so far: Gateway (S2–3), resilience stack (S4–5), OpenFeign (S6), Kafka/Sagas (S7, S12), caching (S8), testing (S10), Docker/K8s pipeline (S13–16).
- Actuator existed since Session 1; `/actuator/circuitbreakers` (S4) and `/actuator/bulkheads` (S5) are also Micrometer-powered — today exposes the raw metrics feed underneath.
- Zipkin container has been in docker-compose since Session 1 (OBG-001: infrastructure must not be introduced before its teaching session).
- `spring.application.name` already set since Session 1 — "nothing new here".
- Session 16 lab review (slide 3): Helm chart install verified? ServiceAccount / Role present? session-16 committed before today?
- Tracing demos exercise the S7 Choreography Saga (or S12 Orchestration) across Kafka.

## 16. Relationship to future sessions

- Slide deck: "Next: Session 18 — CQRS Pattern" (Monday, 3:00–5:30 PM, Online).
- Deep-dive deck's "Next Session" preview says "Advanced Patterns — CQRS & Event Sourcing" and lists CQRS, Command/Query models, Event Sourcing, Event Store, Axon concepts, read projections, eventual consistency, when CQRS is useful/avoided. NOTE discrepancy: the actual Session 18 deck implements CQRS with Spring Data and explicitly places Axon Framework and Event Sourcing OUT of scope. Treat the deep-dive preview wording as superseded by the Session 18 material.
- The CQRS session references Session 17 directly: a future listener "could update a Grafana metric (Session 17!) without changing a single line of the Command service".
- Session 23's load tests will exercise the same Timer/P95/P99 shapes first seen here (slide 16).
- Session 24's clinic records "No structured logging -> JSON logs + trace correlation — Session 17" among resolved technical debt, and lists "introducing structured logging (S17) from Session 1 instead of Session 17" as an example of a decision one might revisit.

## 17. Lab relationship

Exactly what the slides say:
- LAB 13 "Tracing, Metrics & Structured Logging" (slide deck): product-service (primary) + order-service (bonus, includes Saga trace verification) — 50 min. Tasks: (1) add tracing deps + config to product-service; verify a trace appears in Zipkin UI; (2) @Timed on a business-critical endpoint; scrape via prometheus.yml; (3) structured JSON logging — Logback JSON console appender; verify traceId matches the Zipkin trace; (4) Verification — existing Session 10 unit tests (@WebMvcTest, TestContainers) must still pass.
- Deep-dive Student Lab (Part 9, sections 61–62), Tasks 1–7: (1) enable distributed tracing for API Gateway, Order Service, Inventory Service (Micrometer tracing, Zipkin reporting, 100% development sampling); (2) generate a distributed trace through Gateway -> Order -> Inventory and verify all services appear in Zipkin; (3) create custom metric `orders.created` via Micrometer, increment after successful order creation, verify through Actuator; (4) configure Prometheus to scrape Order Service and Product Service, verify Status -> Targets -> UP; (5) run at least `orders_created_total` and `rate(http_server_requests_seconds_count[1m])`; (6) create a Grafana dashboard with at least four panels (request rate, request duration, order count, JVM memory); (7) configure structured JSON logging (JSON, traceId, spanId) and verify multiple services log the same trace ID.
- Lab acceptance criteria (deep-dive section 62): send an order request -> find the request in Zipkin -> identify all participating services -> see metrics in Prometheus -> see dashboards in Grafana -> find logs using the trace ID.
- Checkpoints: CHECKPOINT 1 — Zipkin container running, Zipkin UI opens, services start successfully, a request creates a trace, multiple services appear in the trace; "Do not continue until this works." CHECKPOINT 2 — /actuator/prometheus works, Prometheus is running, targets UP, PromQL returns metrics, custom order metrics appear.
- Demos (slide deck): (1) one request -> one connected trace (curl POST /api/orders, Zipkin query serviceName order-service, ~5 spans, waterfall view); (2) async Saga steps share the same trace (order-service, inventory-service, payment-service Kafka Saga; search by traceId); (3) Grafana populating under generated load (50-request loop; watch order.create.duration and http.server.requests).
- Final checklist (deep-dive Part 10): Distributed Tracing (Zipkin running/UI opens/services send traces/multi-service trace/context propagates), Metrics (Prometheus dependency, /actuator/prometheus works, custom metric exists, target UP, PromQL works), Grafana (running, data source, metric in Explore, dashboard created), Logging (JSON logs, trace ID, span ID, same trace ID across services).
- Daily Quiz (slide deck): 8 Questions, 10 Minutes, Google Forms or Kahoot — Traces, Metrics, Structured Logging, Sampling Rate, Pull vs Push.
- Homework: not mentioned in either deck. UNKNOWN — REQUIRES SOURCE REVIEW.
- Checkpoint commit naming for Session 17: not mentioned in either deck (only the slide-3 review question "session-16 committed before today?"). UNKNOWN — REQUIRES SOURCE REVIEW.
