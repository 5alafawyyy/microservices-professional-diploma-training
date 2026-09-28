import os

labs_info = [
    ("01", "1", "OFFICIAL SOURCE LAB", "Build the foundation: Config Server, Eureka Server, and Product Service.", "Service Discovery, Centralized Configuration", "To establish the dynamic routing and configuration foundation.", "None", "1. Create Config Server. 2. Create Eureka. 3. Create Product Service.", "Spring Cloud Config, Netflix Eureka", "config-server, eureka-server, product-service", "Services register as UP in Eureka", "Run mvn spring-boot:run and check Eureka dashboard", "All 3 services running", "Port conflicts", "Foundation", "session-01", "Official document session-01-lab-01.md"),
    ("02a", "2", "OFFICIAL SOURCE LAB", "Implement API Gateway for dynamic routing.", "API Gateway, Route Predicates", "To provide a single entrypoint for clients.", "Lab 01", "1. Create API Gateway. 2. Configure routes via Eureka.", "Spring Cloud Gateway", "api-gateway", "Gateway routes requests to product-service", "Test via gateway port 8080", "200 OK from product-service via gateway", "Route matching errors", "Gateway added", "session-02", "Official document session-02-lab-02.md"),
    ("02b", "3", "OFFICIAL SOURCE LAB", "Secure the API Gateway and add rate limiting.", "JWT Validation, Rate Limiting", "To secure endpoints and prevent abuse.", "Lab 02A", "1. Add JwtAuthFilter. 2. Add Redis rate limiter.", "jjwt, Redis", "api-gateway", "Unauthenticated requests rejected with 401", "Send request without token", "401 Unauthorized", "Redis connection refused", "Security layer", "session-03", "Official document session-03-lab-2b.md"),
    ("03a", "4", "OFFICIAL SOURCE LAB", "Scaffold Order & Payment, add Circuit Breaker and Retry.", "Resilience4j CircuitBreaker/Retry", "To handle downstream failures gracefully.", "Lab 02B", "1. Scaffold services. 2. Add CB/Retry.", "Resilience4j", "order-service, payment-service", "Fallback method invoked on failure", "Stop payment-service and hit order-service", "Fallback response", "Fallback signature mismatch", "Resilience layer", "session-04", "Official document session-04-lab-3a.md"),
    ("03b", "5", "OFFICIAL SOURCE LAB", "Add Bulkhead and TimeLimiter to Order Service.", "Resilience4j Bulkhead/TimeLimiter", "To prevent resource exhaustion and hang.", "Lab 03A", "1. Add Bulkhead. 2. Add TimeLimiter (async).", "Resilience4j", "order-service", "Timeout triggers fallback", "Simulate delay in payment-service", "Fallback response", "Async context issues", "Resilience layer", "session-05", "Official document session-05-lab-3b.md"),
    ("04a", "6", "OFFICIAL SOURCE LAB", "Implement Inventory Service and OpenFeign communication.", "OpenFeign, Sync Communication", "To allow inter-service sync calls.", "Lab 03B", "1. Build inventory-service. 2. Add Feign client to order-service.", "Spring Cloud OpenFeign", "inventory-service, order-service", "Order service successfully calls inventory service", "Place an order", "Inventory updated", "Feign configuration", "Inter-service sync", "session-06", "Source evidence unavailable / reconstructed from reference implementation."),
    ("05a", "7", "OFFICIAL SOURCE LAB", "Implement Choreography Saga using Kafka.", "Event-Driven, Choreography Saga", "To manage distributed transactions.", "Lab 04A", "1. Add Kafka. 2. Implement event handlers.", "Spring Kafka", "order, inventory, payment", "Saga completes or compensates", "Place valid and invalid orders", "Correct final state", "Consumer group conflicts", "Async messaging", "session-07", "Official document session-07-lab-5a.md (empty) / reconstructed."),
    ("06a", "8", "OFFICIAL SOURCE LAB", "Add Postgres and Redis caching to Product Service.", "Relational DB, Cache-Aside", "To add persistence and improve read performance.", "Lab 05A", "1. Add Postgres JPA. 2. Add Redis caching.", "Spring Data JPA, Spring Cache", "product-service", "Products cached in Redis", "Fetch product twice", "Second fetch is faster (cache hit)", "Redis serialization", "Data layer", "session-08", "Official document session-08-lab-6a.md"),
    ("08a", "9", "RECONSTRUCTED TRAINING LAB", "Containerize the microservices platform.", "Docker, Multi-stage builds", "To standardize deployment.", "Lab 06A", "1. Write Dockerfiles. 2. Update docker-compose.yml.", "Docker", "All services", "Containers start successfully", "docker compose up", "All healthy", "Network aliases", "Containerization", "session-09", "Source evidence unavailable / reconstructed from reference implementation."),
    ("09a", "10", "RECONSTRUCTED TRAINING LAB", "Implement integration testing for Product Service.", "Testcontainers, @WebMvcTest", "To ensure service reliability.", "Lab 08A", "1. Write tests. 2. Add Testcontainers.", "Testcontainers, Mockito", "product-service", "Tests pass", "mvn test", "Build success", "Docker daemon issues", "Testing", "session-10", "Source evidence unavailable / reconstructed from reference implementation."),
    ("09b", "11", "RECONSTRUCTED TRAINING LAB", "Implement Contract and Chaos testing.", "Pact, WireMock", "To ensure API compatibility and resilience.", "Lab 09A", "1. Add Pact tests. 2. Add WireMock tests.", "Pact, WireMock", "order-service", "Tests pass", "mvn test", "Build success", "Port conflicts", "Testing", "session-11", "Source evidence unavailable / reconstructed from reference implementation."),
    ("10a", "12", "RECONSTRUCTED TRAINING LAB", "Implement Orchestration Saga.", "State Machine, Orchestrator", "To centralize complex saga logic.", "Lab 09B", "1. Add orchestrator to order-service. 2. Update consumers.", "Spring Kafka", "order-service", "Saga orchestrated successfully", "Place order", "Saga completes", "State machine config", "Architecture shift", "session-12", "Source evidence unavailable / reconstructed from reference implementation."),
    ("11a", "13", "RECONSTRUCTED TRAINING LAB", "Implement CI/CD and Notification Service.", "GitHub Actions, Dead Letter Queue", "To automate builds and handle failed events.", "Lab 10A", "1. Add workflows. 2. Build notification-service.", "GitHub Actions, Kafka", ".github, notification-service", "Pipeline passes", "Push commit", "Green build", "Workflow syntax", "CI/CD", "session-13", "Source evidence unavailable / reconstructed from reference implementation."),
    ("11b", "14", "RECONSTRUCTED TRAINING LAB", "Deploy with ArgoCD GitOps.", "GitOps, ArgoCD", "To automate K8s deployment.", "Lab 11A", "1. Write ArgoCD app manifests.", "ArgoCD", "k8s/argocd", "App deployed via Argo", "Check Argo UI", "Synced", "Cluster access", "Deployment", "session-14", "Source evidence unavailable / reconstructed from reference implementation."),
    ("12a", "15", "RECONSTRUCTED TRAINING LAB", "Implement core K8s objects.", "Deployments, Services, Probes", "To run services in K8s.", "Lab 11B", "1. Write Deployment/Service manifests.", "Kubernetes", "k8s/manifests", "Pods running", "kubectl get pods", "Running", "Image pull errors", "Kubernetes", "session-15", "Source evidence unavailable / reconstructed from reference implementation."),
    ("12b", "16", "RECONSTRUCTED TRAINING LAB", "Implement advanced K8s objects.", "Helm, HPA, RBAC", "To manage and scale K8s apps.", "Lab 12A", "1. Create Helm chart. 2. Add HPA.", "Helm", "k8s/helm", "HPA scales pods", "Load test", "Multiple replicas", "Metrics server", "Kubernetes", "session-16", "Source evidence unavailable / reconstructed from reference implementation."),
    ("13", "17", "RECONSTRUCTED TRAINING LAB", "Implement observability stack.", "Micrometer, Zipkin, Grafana", "To trace requests and monitor metrics.", "Lab 12B", "1. Add Micrometer. 2. Configure Zipkin.", "Micrometer", "All services", "Traces appear in Zipkin", "Generate traffic", "Traces visible", "Sampling rate", "Observability", "session-17", "Source evidence unavailable / reconstructed from reference implementation."),
    ("14", "18", "RECONSTRUCTED TRAINING LAB", "Implement CQRS pattern.", "Command/Query Segregation", "To optimize read/write paths.", "Lab 13", "1. Separate read/write models in product-service.", "Spring Data", "product-service", "Read/Write models separate", "Code inspection", "CQRS applied", "Data synchronization", "Architecture", "session-18", "Source evidence unavailable / reconstructed from reference implementation."),
    ("15", "19", "RECONSTRUCTED TRAINING LAB", "Set up Keycloak IdP.", "Keycloak, OAuth2", "To provide centralized auth.", "Lab 14", "1. Run Keycloak. 2. Create realm.", "Keycloak", "docker-compose.yml", "Keycloak running", "Login to Keycloak admin", "Admin access", "Port 8180", "Security", "session-19", "Source evidence unavailable / reconstructed from reference implementation."),
    ("16", "20", "RECONSTRUCTED TRAINING LAB", "Migrate Gateway to OAuth2 Resource Server.", "OAuth2, RBAC", "To integrate with Keycloak.", "Lab 15", "1. Update Gateway. 2. Configure Client Credentials.", "Spring Security", "api-gateway", "Token validated via Keycloak", "Call with valid token", "200 OK", "Issuer URI mismatch", "Security", "session-20", "Source evidence unavailable / reconstructed from reference implementation."),
    ("17", "21", "RECONSTRUCTED TRAINING LAB", "Enable Istio Service Mesh.", "Istio, mTLS", "To enforce mTLS and traffic splitting.", "Lab 16", "1. Apply Istio manifests.", "Istio", "k8s/", "mTLS enforced", "Check mesh", "Traffic split works", "Sidecar injection", "Service Mesh", "session-21", "Source evidence unavailable / reconstructed from reference implementation."),
    ("18", "22", "OFFICIAL SOURCE LAB", "Implement Transactional Outbox and Idempotency.", "Outbox Pattern", "To prevent dual-write bugs.", "Lab 17", "1. Add outbox to order-service. 2. Add idempotency to payment.", "Spring Data, Kafka", "order-service, payment-service", "Outbox events processed exactly once", "Simulate failure", "No duplicates", "Transaction boundaries", "Data Integrity", "session-22", "Official document missing locally / reconstructed from reference implementation."),
    ("19", "23", "OFFICIAL SOURCE LAB", "Perform k6 Load Testing.", "Load Testing", "To identify bottlenecks.", "Lab 18", "1. Run k6 scripts. 2. Document findings.", "k6", "k6/", "Load test runs successfully", "k6 run script.js", "Report generated", "k6 not installed", "Performance", "session-23", "Official document missing locally / reconstructed from reference implementation.")
]

import os

base_dir = "docs/labs"
os.makedirs(base_dir, exist_ok=True)

for lab in labs_info:
    lab_id, session, cls, obj, concepts, why, prereq, tasks, tech, files, acc, verify, expect, ts, arch, commit, source = lab
    folder = os.path.join(base_dir, f"lab-{lab_id.lower()}")
    os.makedirs(folder, exist_ok=True)
    
    readme_path = os.path.join(folder, "README.md")
    
    content = f"""# Lab {lab_id.upper()} — Session {session}

## 1. Classification
**{cls}**

## 2. Objective
{obj}

## 3. Concepts Taught
{concepts}

## 4. Why the lab exists
{why}

## 5. Prerequisites
{prereq}

## 6. Tasks
{tasks}

## 7. Technologies Introduced
{tech}

## 8. Files/Components Changed
{files}

## 9. Acceptance Criteria
{acc}

## 10. How to Verify
{verify}

## 11. Expected Result
{expect}

## 12. Troubleshooting Notes
{ts}

## 13. Related Architecture Changes
{arch}

## 14. Related Commit(s)
{commit}

## 15. Relationship to Source/Reference Material
{source}
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Generated all lab README files.")
