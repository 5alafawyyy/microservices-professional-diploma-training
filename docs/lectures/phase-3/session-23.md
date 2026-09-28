# Session 23 — Performance & Load Testing

Source files: `Session_23_Performance & Load Testing.pdf` (50 pages, full student-tutorial edition, sections 1–55, header "Spring Boot & Spring Cloud — Professional Edition"); `Session_23_Performance_Load_Testing.pdf` (21 pages, DIFFERENT instructor deck — header: "k6 · Load Test Design · Watching Resilience Patterns Trigger for Real · Bottleneck Analysis", Wednesday, 3:00–5:30 PM, 2.5 hours, Phase 3 · Advanced & Enterprise). The two files are different documents (different page counts and content) and both were read in full.

## 1. Why this topic exists

- Until now everything was tested with `curl`, Postman, unit tests, integration tests, small shell loops — useful, but they do not answer: "What happens when many clients access the system concurrently?"
- The system may work perfectly with 1 request and still fail under 100 concurrent requests.
- Every resilience pattern since Session 4 (Circuit Breaker, Bulkhead, TimeLimiter, Retry) had only been exercised with a handful of manual curl calls or a 15-request shell loop. Every observability tool since Session 17 was tested similarly. "Configuration written in application.yml is a HYPOTHESIS about how the system will behave."
- Today the hypothesis is tested for real: it is the first time the platform runs under genuine concurrent load; patterns nobody has actually seen fire are observed live ("not a unit test mock, not 15 sequential curls, but genuine simultaneous traffic like a real Black Friday spike").
- Prediction exercise (instructor deck): before any code runs, write on the board which resilience pattern YOU predict will show visible effects first and at what request rate — revisited after the stress test demo.
- Performance testing helps discover: latency problems, throughput limits, connection pool exhaustion, CPU saturation, database bottlenecks, downstream failures, queue buildup, timeout problems, retry amplification, Circuit Breaker activation, Bulkhead rejection, capacity limits.
- Professional framing: "Performance testing is not simply: 'Send as many requests as possible.' A professional performance test asks a specific question."

## 2. Core concepts

- Virtual User (VU): one simulated client executing the test script in a continuous loop for the test's duration. A VU is a workload-generation abstraction, NOT a literal count of human users (a k6 VU may do request → sleep 1 second → request...; a real user opens pages, thinks, reads, clicks, waits, scrolls).
- Iteration: one complete execution of the `export default function () {...}` by one VU; e.g. 10 VUs × 20 iterations ≈ 200 iterations (actual number depends on the workload model and execution time).
- VUs and throughput: 10 VUs × ~1s iteration ≈ 10 iterations/sec; same 10 VUs at 5s per iteration ≈ 2 iterations/sec — "More VUs does not automatically mean a specific requests-per-second rate."
- Checks vs thresholds: `check()` verifies an assertion (a failed check is recorded by k6) but "a check alone does not necessarily fail the entire test"; thresholds turn performance requirements into automated pass/fail conditions — if violated, k6 marks the test failed and returns a non-zero exit code (same "fail the build" philosophy as Session 13's Quality Gate).
- Percentiles: do not rely only on average latency (example: avg = 300 ms, P95 = 1200 ms, P99 = 3000 ms — average looks acceptable but tail latency is poor). P50/P95/P99 definitions: "95% of requests are faster than this value" (so P95 = 500 ms means ~95% ≤ 500 ms, 5% > 500 ms; the remaining 1% at P99 can represent a significant number of requests in a large system).
- Test types (four important types + extensions): Smoke (does the test work at all — e.g. 1 VU, 10 seconds; checks endpoint available, authentication works, response correct, script works, thresholds work); Load (can the system handle expected traffic — example 10 → 20 → 20 sustained → 0 VUs; interested in latency, throughput, errors, stability); Stress (where does the system stop behaving acceptably — intentionally exceed expected traffic, e.g. 20 → 50 → 100 → 150 → 200; observe latency degradation, failures, resource saturation, resilience patterns, recovery behavior); Spike (can the system survive a sudden traffic increase — e.g. 10 VUs → sudden jump → 150 VUs → hold → 10 VUs — different from gradually increasing traffic).
- Test type decision table: Does the script work? → Smoke · Can normal expected traffic be handled? → Load · Where does the system break? → Stress · Can the system survive sudden traffic? → Spike · Will a particular Bulkhead threshold activate? → Targeted stress · Where is the bottleneck? → Load + monitoring + tracing.
- Staged workload design: ramp-up → expected traffic → stable/steady-state period → ramp-down. "A steady-state period is important because we want stable measurements rather than measuring only startup behavior." (Grafana's k6 guidance likewise recommends ramp-up, steady-state, ramp-down for baseline testing.)
- Baseline: before a stress test, establish a baseline with 1 VU, then 5 VUs, then 10 VUs; record VUs, requests/sec, P95, P99, errors — "This gives us something to compare against."
- Workload models: VU-based workload = closed-model style (VU sends request → waits for response → continues); arrival-rate workload = open model (requests start at a controlled rate; the system's response time does not determine the desired arrival rate). This distinction matters for serious capacity testing.
- Retry amplification / retry storm: if k6 sends 100 requests and the service retries failed downstream calls 3 attempts/request, the downstream receives substantially more attempts than the original client traffic — "the resilience mechanism itself may be contributing to the load."
- Bottleneck analysis: "P95 = 2.5 seconds" is a symptom, not yet the root cause; ask "Where did the 2.5 seconds go?" — trace the request with Zipkin to get evidence, then say exactly which service/span holds the majority of the latency. "Performance engineering is evidence-based diagnosis."
- Resilience under real load (instructor deck): the observed sequence — traffic increases → latency increases → downstream becomes slow → timeouts/failures appear → Bulkhead saturation/rejections → Circuit Breaker records failures → Circuit Breaker may OPEN → requests rejected/fallbacks. Explicitly "a hypothesis, not a guaranteed universal execution order."
- Bulkhead visibility: with `maxConcurrentCalls: 10`, once the protected operation becomes slow, Request 11/12/13 may encounter a saturated Bulkhead — increasing VUs alone is not enough; you need "high concurrency + slow enough protected operation".
- Circuit Breaker visibility: with `minimumNumberOfCalls = 10` and `failureRateThreshold = 50%`, the breaker cannot open after one failed request; e.g. 10 calls with 8 failures → 80% > 50% → CLOSED → OPEN (assuming other conditions are satisfied). The Circuit Breaker is a state machine: CLOSED → (failure threshold exceeded) → OPEN → (wait duration) → HALF_OPEN → (healthy → CLOSED / failing → OPEN).
- Session 5 execution order confirmed live (instructor deck): Bulkhead → TimeLimiter → CircuitBreaker → Retry; with the demo showing Bulkhead dropping to 0 available calls BEFORE the Circuit Breaker flips to OPEN — "This is exactly Session 5's documented execution order, happening for real." Bulkhead is OUTERMOST — the first gate a request passes through.
- Bottleneck investigation workflow: 1 Detect → 2 Measure → 3 Locate → 4 Explain → 5 Change → 6 Re-test (example: P95 increased → Zipkin shows Payment slow → Payment DB connection pool saturated → increase pool? optimize query? → run test again → compare results).
- Performance testing is experimental: record your prediction, execute, and if the Circuit Breaker changed state first instead of the Bulkhead, "That is not a failed experiment. It is a useful result. Ask: Why?"
- The most important principle: never conclude "The application is slow" — ask which request, which service, which operation, which dependency, which resource, which threshold, which trace, which metric.
- Why a load test can lie: if the k6 machine CPU = 100% while the microservices CPU = 40%, the bottleneck may be the load generator, not the application — "Can my load generator generate the requested workload without becoming the bottleneck?" (larger tests may need distributed/cloud load generation).

## 3. Architecture

- Test topology (student deck, section 2):

```
                +---------------+
                |      k6       |
                | Load Generator|
                +-------+-------+
                        |
                        v
                +---------------+
                | API Gateway   |
                +-------+-------+
                        |
                        v
                +---------------+
                | Order Service |
                +-------+-------+
                        |
           +------------+------------+
           v            v            v
      Inventory      Payment       Kafka
       Service       Service
           |            |
           +------+-----+
                  v
              Database
```

- The load test must NOT bypass: API Gateway, Security, Service discovery, Resilience, Downstream calls, Database, Kafka — "We want to test the real architecture."
- Therefore the test uses a valid JWT: `TEST_JWT=<valid-token>`; `k6 run -e TEST_JWT="$TEST_JWT" load-test.js`. Never hard-code real credentials into a committed k6 script.
- Instructor deck stack strip for the demo: k6 → full secured chain; results correlated with Session 17 tracing: "k6 tells you WHAT failed (aggregate: '12% of requests exceeded 800ms in this stage'); Zipkin tells you WHERE (precise: 'THIS trace, THIS span — the Feign call to Inventory — took 780ms')."
- Live demo reading k6 summary output (instructor deck): `http_req_duration: avg=42ms p(95)=61ms p(99)=88ms`; `http_req_failed: 0.00% ✓500 ✗0`; `http_reqs: 500 50.02/s`; "✓ THRESHOLDS PASSED: p(95)<500, rate<0.01".
- Two-terminal live demo (instructor deck):

```
/actuator/bulkheads                     /actuator/circuitbreakers
t=0s:  available-concurrent-calls: 10   t=0s:  state: CLOSED
t=8s:  available-concurrent-calls: 3    t=12s: state: CLOSED
t=12s: available-concurrent-calls: 0    t=17s: state: OPEN
Bulkhead full — rejecting calls FIRST   A few seconds LATER — failure rate crosses threshold
```

  Conclusion shown: "Bulkhead drops to 0 available calls BEFORE Circuit Breaker flips to OPEN."
- Docker networking: if k6 runs on your machine, `http://localhost:8080` may be correct; if k6 runs inside Docker, `localhost` means the k6 container, not the API Gateway container — use the Docker service name, e.g. `http://api-gateway:8080` (exact hostname depends on the Docker Compose service name); all services on `platform-net` in the example.
- Safety boundary: `POST /api/orders` changes system state — "Do not run this against production." Use test database, test customer, test products, test payment environment, test Kafka topics; also consider the Session 22 Idempotency mechanism so the test does not accidentally create uncontrolled duplicate business operations.
- Controlled slow-down experiment (for Bulkhead demonstration): if the platform contains a test-only endpoint or controlled downstream delay mechanism, introduce a safe delay (e.g. Payment Service artificial 2-second delay), then run 10 / 20 / 50 / 100 VUs so concurrency accumulates more easily — "Do this only in a dedicated development/test environment."
- Project progress after Session 23 (instructor deck): new `k6/` directory (smoke, load, stress tests); "No application code changes"; baseline documented (req/s, P95/P99 latency); capability "Verified Resilience Under Real Load."

## 4. Technologies

- Grafana k6 — the load-testing tool; workloads described in JavaScript. Commands shown: `k6 version`, `k6 run <script>.js`, `k6 run -e KEY=value <script>`; environment variables via `__ENV`. Executors/workloads used in slides: `stages` (shortcut for the `ramping-vus` workload) and `constant-arrival-rate` (arrival-rate executor; open workload model; `rate: 50`, `timeUnit: '1s'`, `duration: '1m'`, `preAllocatedVUs: 50`). k6 RELEASE version: UNKNOWN — REQUIRES SOURCE REVIEW (slides only say "k6 version" prints the installed version; install according to your OS).
- Zipkin — tracing tool from Session 17, used to locate WHERE latency lives (find a representative slow/failed request, identify slowest service and slowest span).
- Resilience4j Actuator endpoints used live (port 8082 in the demo): `/actuator/bulkheads` (available-concurrent-calls), `/actuator/circuitbreakers` (state), `/actuator/circuitbreakerevents` (event endpoints). "Resilience4j exposes Actuator endpoints for Circuit Breaker and Bulkhead information, as well as event endpoints."
- Security stack exercised (not bypassed): JWT — valid token required; instructor deck: "either a cached Keycloak Client Credentials token (S20) or a pre-obtained customer token (S19)"; test operates against the FULL secured platform.
- Surrounding platform components named: API Gateway, Order Service, Payment Service, Inventory Service, PostgreSQL database, Kafka (consumer lag), Docker (Compose networking), Hikari connection pool (Hikari active connections = maximum as a bottleneck pattern).
- NOT mentioned in either Session 23 deck: Jaeger, Kiali, Istio (Session 21 material is not referenced here), gatling/JMeter/Locust. Tool versions: UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- VU (Virtual User); iteration; `sleep()`; workload-generation abstraction vs real human users.
- `options` object; `vus`; `duration`; `stages`; ramp-up / expected load / sustained load / ramp-down; steady-state.
- check() (assertion recorded by k6, does not fail the test by itself); threshold (pass/fail condition; non-zero exit code on violation).
- Metrics: `http_req_duration` (avg, p(90), p(95), p(99)), `http_req_failed` (rate), `http_reqs`, `http_reqs/s`, `iterations`, `vus`, `data_received`, `data_sent`.
- Percentiles P50 / P95 / P99; tail latency; "average is not enough".
- Test types: smoke, load, stress, spike, targeted stress; bottleneck analysis; baseline test/table.
- Closed model (VU-based) vs open model (arrival-rate); arrival-rate executors; `constant-arrival-rate`; `preAllocatedVUs`.
- Retry amplification / retry storm.
- Bulkhead: `maxConcurrentCalls: 10`, available-concurrent-calls, saturation/rejections.
- Circuit Breaker: `minimumNumberOfCalls = 10`, `failureRateThreshold = 50%`, states CLOSED / OPEN / HALF_OPEN, wait duration, CLOSED → OPEN transition.
- Session 5 documented execution order: Bulkhead → TimeLimiter → CircuitBreaker → Retry (Bulkhead outermost).
- Bottleneck patterns: CPU bottleneck; database bottleneck; connection-pool bottleneck; downstream bottleneck; retry amplification.
- Load generator as bottleneck; distributed/cloud load generation.
- Slow trace; span; "k6 tells you WHAT failed, Zipkin tells you WHERE".
- Performance test results table; lab report fields (see §17).

## 6. Code concepts

- Minimal k6 script (smoke):

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],     // less than 1% may fail
  },
};

export default function () {
  const res = http.get('http://localhost:8080/api/v1/products');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

- Imports: `import http from 'k6/http'` gives `http.get()`, `http.post()`, `http.put()`, `http.delete()`; `import { check, sleep } from 'k6'` — `check()` verifies an assertion, `sleep()` pauses the VU.
- Staged load test (with JWT-authenticated POST; also shows environment variables):

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp-up
    { duration: '30s', target: 20 },   // Expected load
    { duration: '2m',  target: 20 },   // Sustained load
    { duration: '30s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<800', 'p(99)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const token = __ENV.TEST_JWT;
  const payload = JSON.stringify({ productId: 'PROD-001', quantity: 1, amount: 100.00 });
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
  const res = http.post(`${BASE_URL}/api/orders`, payload, params);
  check(res, { 'status is successful': (r) => [200, 202].includes(r.status) });
  sleep(1);
}
```

- Stress test — same request function, only `options` changes (student deck): stages 20s→20, 30s→50, 30s→100, 30s→150, 30s→200, 30s→0 with deliberately loose threshold `http_req_duration: ['p(95)<5000']`. Instructor deck variant: stages 20s→50, 20s→150 ("well beyond S5's Bulkhead max-concurrent-calls: 10"), 20s→0 with `http_req_failed: ['rate<0.5']` ("deliberately loose — we EXPECT failures"). Why loose? "This test is not primarily asking 'Does the system meet the normal SLA?' It is asking 'What happens as we push the system toward its limits?'"
- Arrival-rate executor (professional extension):

```javascript
export const options = {
  scenarios: {
    api_load: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 50,
    },
  },
};
```

  "For today's core lab, use ramping-vus first. Treat arrival-rate testing as the professional extension."
- Environment variables: `const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';` → `k6 run -e BASE_URL=http://localhost:8080 load-test.js`; for the JWT `const token = __ENV.TEST_JWT;` → `k6 run -e TEST_JWT="$TEST_JWT" load-test.js` (instructor variant: `TEST_JWT=<paste-a-valid-token> k6 run order-load-test.js`).
- File layout created: `session23/` containing `smoke-test.js`, `load-test.js`, `stress-test.js` (student deck); instructor deck uses `order-load-test.js`, `stress-test.js`, and the lab expects `k6/checkout-stress-test.js`.
- No Java code is written in this session — instructor deck states explicitly: "No application code changes."

## 7. Configuration

- Smoke: `vus: 1`, `duration: '10s'`, thresholds `http_req_duration: ['p(95)<500']`, `http_req_failed: ['rate<0.01']`.
- Load: stages `30s → 10`, `30s → 20`, `2m → 20`, `30s → 0`; thresholds `p(95)<800`, `p(99)<2000`, `rate<0.05`.
- Stress (student variant): `20s→20`, `30s→50`, `30s→100`, `30s→150`, `30s→200`, `30s→0`; threshold `p(95)<5000` (intentionally looser).
- Stress (instructor variant): `20s→50`, `20s→150`, `20s→0`; threshold `rate<0.5`.
- Threshold semantics: `p(95)<800` = 95% of HTTP requests must complete in under 800 ms; `rate<0.05` = less than 5% may fail; violating a threshold marks the test failed and returns a non-zero exit code.
- Environment/jogging configuration: `-e BASE_URL=...`, `-e TEST_JWT=...`; Docker service name for the gateway (`http://api-gateway:8080` on network `platform-net`).
- Resilience configuration referenced during the test (existing from S4–5): Bulkhead `maxConcurrentCalls: 10`; Circuit Breaker `minimumNumberOfCalls = 10`, `failureRateThreshold = 50%`; Actuator endpoints on port 8082: `curl http://localhost:8082/actuator/bulkheads`, `.../actuator/circuitbreakers`, `.../actuator/circuitbreakerevents`.
- Results interpretation example: `avg=320ms, p(90)=500ms, p(95)=700ms, p(99)=1.5s`, `http_req_failed: 1.2%` → 1.2% < 5% so the error-rate threshold passes.
- Throughput reading: look at `http_reqs` and `http_reqs/s`; 150 req/s is very different from 20 req/s even if both tests used 50 VUs — "VU count alone is not a performance requirement."

## 8. Failure scenarios

- One request works; 100 concurrent requests fail — the gap this session closes.
- Discoverable problems (slide list): latency problems, throughput limits, connection pool exhaustion, CPU saturation, database bottlenecks, downstream failures, queue buildup, timeout problems, retry amplification, Circuit Breaker activation, Bulkhead rejection, capacity limits.
- Degradation under stress is the observation target, not "make everything crash": example progression 20 VUs → P95 400 ms / 0% errors; 50 VUs → 600 ms / 0%; 100 VUs → 1.2 s / 1%; 150 VUs → 3.5 s / 8%; 200 VUs → 8 s / 25%.
- Bulkhead may not fire even at high VU counts: "Why might 150 VUs fail to trigger a Bulkhead?" — the protected operation may not be slow enough; you need high concurrency AND a slow enough protected operation.
- Circuit Breaker cannot open without enough calls: with `minimumNumberOfCalls = 10`, even 9 failed calls may not be enough; 10 calls with 8 failures (80% > 50%) may cause CLOSED → OPEN assuming other conditions are satisfied.
- Retry amplification: retries multiply downstream traffic during failure (100 client requests → 100 primary calls → failures → retries → additional calls).
- Load generator as the hidden bottleneck: k6 machine CPU = 100% while microservices CPU = 40% → the load generator, not the application, is the bottleneck.
- Accidentally testing production: `POST /api/orders` changes system state — do not run against production; use test database/customer/products/payment environment/Kafka topics.
- Uncontrolled duplicate business operations in load tests: consider Session 22's `Idempotency-Key` support so the test does not accidentally create duplicates.
- Low realism from bypassing security: a test that skips Gateway/JWT would not reflect real production behavior — the test must use a real JWT.
- Slow tests due to missing warm-up: Rule 4 — warm up the application.
- Misleading conclusions from single runs: Rule 10 — repeat tests before drawing conclusions.

## 9. Trade-offs

- Closed vs open workload models: VU-based (closed — response time feeds back into the achieved rate) vs arrival-rate (open — start requests at a controlled rate independently of response time); "This distinction becomes important when doing serious capacity testing."
- Strict vs loose thresholds: the stress test deliberately uses loose thresholds because it is exploratory ("What happens as we push the system toward its limits?"), not an SLA validation.
- ramping-vus first (core lab) vs arrival-rate executors as the professional extension.
- Local load generation vs distributed/cloud load generation when the generator cannot produce the required workload.
- Zipkin-style tracing over aggregate metrics: k6 gives WHAT failed (aggregate), Zipkin gives WHERE (specific trace/span) — you need both aggregate and precise views.
- Average vs percentiles: averages hide tail latency problems.
- Controlled slow-down experiments (e.g. artificial 2-second delay) to make resilience visible — only in a dedicated development/test environment (realism vs observability of the pattern).
- The uncertainty trade-off: configured resilience behavior under load is a hypothesis; observed firing order may differ from predictions — that difference is itself the valuable result ("A hypothesis that survives contact with real load is worth more than a hypothesis nobody tested.")

## 10. Common mistakes

- Relying only on average latency instead of percentiles (avg = 300 ms while P95 = 1200 ms, P99 = 3000 ms).
- Assuming 10 VUs = 10 real human users; assuming VU count maps one-to-one to concurrent users.
- Assuming more VUs automatically means a specific requests-per-second rate (iteration duration changes throughput).
- Assuming "VU count" is itself a performance requirement (150 req/s vs 20 req/s at the same 50 VUs).
- Skipping the baseline; jumping immediately to a huge number during stress ("Do not jump immediately to a huge number").
- Treating a stress test as "make everything crash" instead of studying how the system degrades.
- Assuming the predicted resilience firing order, instead of measuring it ("Do not assume the answer").
- Concluding "the application is slow" without identifying request/service/operation/dependency/resource/threshold/trace/metric.
- Hard-coding real credentials into a committed k6 script.
- Accidentally running the state-changing test against production.
- Running the load test, but not monitoring the load generator, the database, or the downstream services (Design Rules 6–8).
- Testing a bypassed path (skipping Gateway/security) so results do not reflect the real architecture.
- Recording only PASS/FAIL in the results table instead of what happened (VUs, req/s, P50/P95/P99, error %, main observation).

## 11. Interview questions

- Session 23 question set (student deck, Q1–Q10): Q1 What is a VU? · Q2 Why is 100 VUs not equivalent to 100 real human users? · Q3 Difference between `check()` and a threshold? · Q4 What does `p(95)<800` mean? · Q5 Difference between load and stress testing? · Q6 Why do we need a baseline? · Q7 Why might 150 VUs fail to trigger a Bulkhead? · Q8 What conditions are required before a Circuit Breaker can open? · Q9 Why should we inspect Zipkin when P95 increases? · Q10 How can the load generator itself become the bottleneck?
- Instructor deck prediction exercise: "Which pattern do YOU predict will show visible effects first, at what request rate?" — compared against the two live terminals after the stress demo ("Bulkhead fired first — was this what the group expected, or a surprise?").
- Professional takeaway phrasing to replace "The service can handle 200 users": "Under the tested workload profile, the platform sustained approximately X requests/sec at Y VUs, with P95 latency of Z ms and an error rate of N%. Beyond this level, latency/error behavior changed and the evidence pointed to ______ as the primary bottleneck." — "That is the difference between 'I tested it.' and 'I have evidence about its capacity and failure behavior.'"
- Daily quiz in class: 8 questions · 10 minutes · Google Forms or Kahoot.

## 12. What I must memorize

- Definitions: VU (simulated client running the script in a loop; an abstraction, not a person count); iteration (one full execution of the default function by one VU); check (assertion; does not fail the test by itself); threshold (pass/fail condition; failed test + non-zero exit code); `p(95)<500` = 95% of requests under 500 ms; `rate<0.01` = less than 1% may fail.
- The four test types + decision table: Smoke (does the script work?), Load (normal expected traffic), Stress (where does it break?), Spike (sudden jump); extensions: Targeted stress (specific Bulkhead threshold), Load + monitoring + tracing (bottleneck location).
- Session 5 documented execution order: Bulkhead → TimeLimiter → CircuitBreaker → Retry (Bulkhead outermost, first gate).
- Circuit Breaker state machine: CLOSED → (failure threshold exceeded) → OPEN → (wait duration) → HALF_OPEN → (healthy → CLOSED / failing → OPEN); opening needs `minimumNumberOfCalls` + violation of `failureRateThreshold` (example: 10 calls, 8 failures = 80% > 50%).
- Key numbers from the decks: smoke 1 VU / 10s; load stages 30s→10, 30s→20, 2m→20, 30s→0; stress progression 50/100/150/200; thresholds examples p(95)<500, p(95)<800, p(99)<2000, rate<0.01/0.05/0.5, p(95)<5000; Bulkhead maxConcurrentCalls: 10; CB minimumNumberOfCalls = 10, failureRateThreshold = 50%.
- The 10 Performance Test Design Rules: 1 Always establish a baseline · 2 Change one important variable at a time · 3 Use realistic data · 4 Warm up the application · 5 Do not test production accidentally · 6 Monitor the load generator · 7 Monitor the database · 8 Monitor downstream services · 9 Use traces to investigate latency · 10 Repeat tests before drawing conclusions.
- The workflow: Detect → Measure → Locate → Explain → Change → Re-test; and the question ladder: which request / service / operation / dependency / resource / threshold / trace / metric.
- The mental model diagram: PERFORMANCE TEST → Workload (VUs, Rate, Duration) + Metrics (P95, P99, Errors) → Microservices (Gateway, Order, Inventory, Payment, Database, Kafka) → Resilience (Bulkhead, Timeout, Circuit Breaker) → Zipkin → Bottleneck Analysis.

## 13. What I must understand

- Why manual curl/Postman/small loops cannot answer the concurrency question; why configuration is a hypothesis until tested under real load.
- Why a VU is an abstraction and why the VU-to-real-user mapping is never one-to-one.
- Why the number of VUs alone does not determine throughput (10 VUs × 1s ≈ 10 iter/s; 10 VUs × 5s ≈ 2 iter/s) and why k6 offers arrival-rate executors when you want to control the rate independently.
- When to use which test type (smoke/load/stress/spike/targeted stress) and why stress thresholds are deliberately loose.
- Why percentiles matter more than averages for tail latency.
- Why the test must run against the full secured platform (Gateway, security, discovery, resilience, downstream, DB, Kafka) with a real JWT.
- Why a baseline is needed and what to record (VUs, req/s, P50, P95, P99, error rate).
- The mechanics that make resilience visible: Bulkhead needs concurrency + slow operation; Circuit Breaker needs enough calls in its evaluation window before it can open.
- Why the observed firing order is a hypothesis that must be measured; why a different result (Circuit Breaker first) is still useful.
- How retry amplification works and why it means observing the whole chain, not only the gateway.
- How to do bottleneck analysis with evidence: trace a slow request in Zipkin, find the slowest span, then name the bottleneck and record evidence.
- Why the load generator itself can be the bottleneck, and what the five bottleneck patterns look like (CPU, database, connection pool, downstream, retry amplification).
- Why open vs closed workload models matter for serious capacity testing.
- The connection to earlier sessions (S4–5 resilience, S13 quality gates, S16 autoscaling, S17 tracing, S20 security, S22 idempotency).

## 14. What I should implement from memory

- Create the `session23/` directory with `smoke-test.js`, `load-test.js`, `stress-test.js` (instructor deck lab path: `k6/checkout-stress-test.js`).
- Write the smoke test from memory: `vus: 1`, `duration: '10s'`, threshold `p(95)<500` and `rate<0.01`, `http.get` the products endpoint, `check` status 200, `sleep(1)`.
- Write the staged load test from memory: env-driven `BASE_URL`/`TEST_JWT`, stages ramp-up/expected/sustain/ramp-down, thresholds `p(95)<800`, `p(99)<2000`, `rate<0.05`, JWT-authenticated `http.post('/api/orders', payload, params)` with `[200, 202]` check.
- Write the stress test from memory by changing only `options` (progressive stages through 50/100/150/200 or 50→150, loose thresholds).
- Run tests with environment variables (`k6 run -e TEST_JWT=... load-test.js`); never hard-code credentials.
- Build the baseline table (VUs, Req/s, P95, P99, Errors for 1/5/10 VUs) and the performance results table per run.
- Run the resilience experiment: open terminals tailing `/actuator/bulkheads`, `/actuator/circuitbreakers`, `/actuator/circuitbreakerevents` while the stress test runs; record the ACTUAL order and timestamps of pattern activations.
- Correlate one slow/failed request from k6 to a Zipkin trace; identify the slowest service and slowest span.
- Write the bottleneck statement: "The primary bottleneck appears to be ________. Evidence: 1. ___ 2. ___ 3. ___".
- Fill the Lab Report table fields: Baseline VUs; Maximum tested VUs; Maximum sustainable throughput; Baseline P95; Stress P95; Baseline error rate; Stress error rate; First visible resilience behavior; Circuit Breaker state; Bulkhead observation; Slowest service; Suspected bottleneck; Evidence.
- Optionally demonstrate arrival-rate usage (`constant-arrival-rate`, rate 50/s, 1m, preAllocatedVUs 50) as the extension.
- Implement the controlled slow-down experiment only in a dedicated dev/test environment (if a test-only endpoint exists).

## 15. Relationship to previous sessions

- Session 4–5 — Resilience4j patterns configured (Bulkhead, TimeLimiter, Circuit Breaker, Retry); their documented execution order (Bulkhead → TimeLimiter → CircuitBreaker → Retry) is CONFIRMED LIVE in this session's demo; the exercise is to compare actual vs theoretical order.
- Session 13 — Quality Gates: thresholds use the same "fail the build" philosophy.
- Session 16 — Autoscaling.
- Session 17 — Distributed tracing / Zipkin: used to investigate slow requests; instructor deck: "k6 tells you WHAT failed; Zipkin tells you WHERE."
- Session 19–20 — Security: the load test must use a real JWT (cached Keycloak Client Credentials token from S20 or pre-obtained customer token from S19); load testing operates against the FULL secured platform, no bypass.
- Session 22 — Idempotency: consider the Idempotency-Key mechanism for the `POST /api/orders` load test to avoid uncontrolled duplicate business operations.
- Closing-the-loop diagram (student deck, section 54): Session 4–5 Resilience → Session 13 Quality Gates → Session 16 Autoscaling → Session 17 Distributed Tracing → Session 20 Security → Session 22 Idempotency → Session 23 PERFORMANCE TESTING → "Real evidence about how the architecture behaves. The architecture is no longer only something we configured."
- Observed platform status strip: prior sessions tested with curl / Postman / unit tests / integration tests / small shell loops; observability tools tested with 15-request shell loops (instructor deck).
- Phase 3 roadmap strip: S17 Observ. → S18 CQRS → S19 Sec. Pt1 → S20 Sec. Pt2 → S21 Svc Mesh → S22 Adv. Pat. → S23 Perf. (LIVE) → S24 Arch. Cl. 2.

## 16. Relationship to future sessions

- Next session (instructor deck closing slide): "Next: Session 24 — Architecture Clinic #2 + Phase 3 Wrap-Up" (Monday, 3:00–5:30 PM, Online).
- The bottleneck findings, baseline numbers, and resilience firing record produced today are the performance evidence the platform carries into the Session 24 clinic (instructor deck: "Resilience Verified Under Real Load"; baseline documented).
- Course repositories named on closing slides: `microservices-pro-course`, `microservices-pro-platform`, ITSharks.

## 17. Lab relationship

- Instructor deck — **Lab 19 — Find the Platform's Actual Bottleneck**. Three steps: (1) Write a Stress Test — `k6/checkout-stress-test.js` targeting the full chain; exceed both Bulkhead AND Circuit Breaker thresholds; (2) Document the Firing Order — record with timestamps; compare against Session 5's documented theoretical order; (3) Correlate to a Zipkin Trace — find one failed request; identify exactly which span shows the failure.
  - Duration: "15 min in-session + complete as homework" · "Builds on: S4-5 Resilience, S17 Observability, S20 Security".
  - Acceptance criteria (exact): a k6 stress test script exists in `k6/checkout-stress-test.js` targeting the full chain; the test run demonstrably exceeds at least one Session 4–5 resilience threshold; a written record documents the ACTUAL order patterns activated, with rough timestamps; this actual order is compared against Session 5's documented theoretical order; at least one failed request is correlated to a specific Zipkin trace and span.
  - Checkpoint commit named in slides: `session-23: add-k6-stress-test-and-bottleneck-findings`.
- Student-tutorial deck — "49. Lab Exercise: **Lab 23 — Find the Performance Limit**". Objective: determine how the platform behaves as traffic increases. Steps: 1) Verify the platform (API Gateway UP, Order Service UP, Payment Service UP, Inventory Service UP, Database UP, Kafka UP, Zipkin UP); 2) Run smoke test (`k6 run smoke-test.js`, expected no major errors); 3) Run baseline with 5 VUs, record requests/sec, P50, P95, P99, error rate; 4) Run normal load with 20 VUs for approximately 2 minutes, record results; 5) Run stress test, increasing gradually 50 → 100 → 150 → 200 ("Do not jump immediately to a huge number"), recording at each stage P95, P99, error rate, throughput, CPU, memory, database, Bulkhead, Circuit Breaker; 6) Observe resilience — "Determine: Which resilience mechanism showed evidence first? Do not assume the answer"; 7) Find a slow trace with Zipkin from the period where latency increased — identify slowest service, slowest span; 8) Identify the bottleneck using the fill-in statement ("The primary bottleneck appears to be ______. Evidence: 1. ___ 2. ___ 3. ___").
- Student-tutorial "50. Lab Report" to submit (exact table fields): Baseline VUs; Maximum tested VUs; Maximum sustainable throughput; Baseline P95; Stress P95; Baseline error rate; Stress error rate; First visible resilience behavior; Circuit Breaker state; Bulkhead observation; Slowest service; Suspected bottleneck; Evidence.
- Note the two deck versions name different labs: "Lab 19" (instructor, `k6/checkout-stress-test.js`, 15 min in-session + homework) vs "Lab 23" (student tutorial, smoke→baseline→load→stress→observe→trace→bottleneck). Both are recorded as found; which name the course actually assigns: UNKNOWN — REQUIRES SOURCE REVIEW.
- Demo in slides (instructor deck): reading k6's summary output; and the two-terminal live demo showing Bulkhead rejecting first (t=12s, 0 available calls) followed by Circuit Breaker OPEN at t=17s.
