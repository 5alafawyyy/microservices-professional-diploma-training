# Command Reference

> Everything the course needs, copy-paste ready (Windows **Git Bash** shell).
> Prerequisite: `export JAVA_HOME="/c/Program Files/java/jdk-21"` if not already set.

## Git

```bash
git status                          # always before committing / discarding
git add services/product-service    # stage specific paths, not -A
git commit -m "session-01: add-product-service-eureka-config"
git log --oneline -5
git remote -v                       # identity check before every push
git config --local user.name
git config --local user.email
ssh -T git@github-personal          # must greet the personal account
git push -u origin main
```

## Maven

```bash
mvn -v                                   # version + the JDK Maven will use
mvn clean package -DskipTests            # build without tests
mvn test                                 # the lab acceptance gate
mvn test -Dtest=ProductServiceTest       # single test class
mvn spring-boot:run                      # start a service (from its module dir)
mvn dependency:tree                      # capture resolved BOM versions (see TECHNOLOGY_MATRIX)
mvn spring-boot:run -Dspring-boot.run.arguments=--payment.failure-rate=1.0
```

## Docker & Compose

```bash
docker compose up -d                 # start infra (from platform/ecommerce-platform)
docker compose ps                    # check healthy
docker compose logs -f kafka
docker compose down                  # stop (keeps volumes)
docker compose down -v               # stop AND delete volumes (destructive)
docker exec -it <container> bash
```

## PostgreSQL

```bash
docker compose exec postgres psql -U postgres -d products
\dt                                 # list tables
SELECT * FROM product;
```

## Redis

```bash
docker compose exec redis redis-cli
KEYS products*
TTL products::1
GET products::all
FLUSHALL                            # dev only
```

## Kafka

```bash
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic order-events
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic order-events --from-beginning
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group order-service          # check lag / duplicates
```

## HTTP checks

```bash
curl http://localhost:8761                  # Eureka dashboard
curl http://localhost:8888/actuator/health  # Config Server
curl http://localhost:8081/api/v1/products
curl -i http://localhost:8081/api/v1/products            # include headers
curl -X POST http://localhost:8081/api/v1/products \
  -H 'Content-Type: application/json' -d '{"name":"Keyboard","price":49.99,"quantity":10}'
curl -X DELETE http://localhost:8081/api/v1/products/1
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/api/v1/products
```

## JWT (tool: `tools/jwt-generator`, Session 3 → retired Session 20)

```bash
cd platform/ecommerce-platform/tools/jwt-generator
mvn clean package -DskipTests
export JWT_SECRET=microservices-pro-course-dev-secret-key-2026-min-256-bits

java -jar target/jwt-generator-1.0.0.jar --username=ahmed --roles=ROLE_ADMIN
java -jar target/jwt-generator-1.0.0.jar --username=test --roles=ROLE_USER --expiry=1m

curl -X POST http://localhost:8080/api/v1/products \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"name":"x","price":1}'
```

## Resilience4j actuator endpoints

```bash
curl http://localhost:8082/actuator/circuitbreakers
curl http://localhost:8082/actuator/circuitbreakerevents
curl http://localhost:8082/actuator/bulkheads
curl http://localhost:8082/actuator/retries
curl http://localhost:8082/actuator/health
```

## Kubernetes (Phase 2, Session 15+)

```bash
kubectl config get-contexts
kubectl get nodes
kubectl get pods -A
kubectl apply -f k8s/
kubectl get svc,deploy,hpa
kubectl logs -f deploy/product-service
kubectl describe pod <pod>          # events — first tool for any pod stuck in Pending/CrashLoop
kubectl port-forward svc/product-service 8081:8081
kubectl rollout status deploy/product-service
```

## Istio (Phase 3, Session 21)

```bash
istioctl version
istioctl analyze -n default
kubectl get peerauthentications,authorizationpolicies -A
istioctl proxy-status
```

## Load testing (Phase 3, Session 23)

```bash
k6 run k6/load-test.js
k6 run --vus 50 --duration 30s k6/load-test.js
```

## Observability (Phase 3, Session 17)

```bash
curl http://localhost:9411/api/v2/traces?serviceName=order-service
# Prometheus:  http://localhost:9090   Grafana: http://localhost:3000 (admin/admin)
```

## Lab scripts (this repo)

```bash
./scripts/verify-environment.sh          # tool audit — run before Phase 1 starts
./scripts/verify-lab.sh 01               # automated acceptance slice for Lab 1
SKIP_TESTS=1 ./scripts/verify-lab.sh 05  # skip mvn test while iterating
./scripts/reset-lab.sh                   # stop containers, show state (safe)
./scripts/reset-lab.sh --discard         # confirm-discard local edits
./scripts/reset-lab.sh --wipe-data       # confirm-wipe volumes (destructive)
```
