# Enterprise E-Commerce Platform

The running artifact of the training programme: a Spring Boot / Spring Cloud
microservices platform grown lab by lab from the course materials.

**Current milestone: Lab 1 (Session 1) — foundation.**

```
                ┌──────────────┐                         ┌────────────────┐
  client ─────▶ │  product-    │ ──── config import ───▶ │  config-server │
                │  service     │                         │      :8888     │
                │   :8081      │ ──── register ────────▶ │  (native)      │
                └──────────────┘                         └────────────────┘
                       │
                       ▼
                ┌────────────────┐        docker-compose
                │  eureka-server │        ┌──────────────────────────┐
                │     :8761      │        │ postgres:16-alpine :5432 │
                └────────────────┘        └──────────────────────────┘
```

## Modules

| Module | Port | Purpose |
| --- | --- | --- |
| `infrastructure/config-server` | 8888 | Centralized configuration, native backend (`classpath:/configs`) |
| `infrastructure/eureka-server` | 8761 | Service registry (client-side discovery) |
| `services/product-service` | 8081 | Product bounded context — CRUD over an in-memory store |

Each module is a **standalone Maven project** (no aggregator pom): build and
run from inside the module directory.

**Historical State Rule:** a later session's technology never appears early.
`api-gateway` (:8080) arrives in Session 2, Redis in Session 3, Kafka in
Session 7, Dockerfiles in Session 9.

## Run it

```bash
docker compose up -d                     # postgres (unused until Session 6-8)

cd infrastructure/config-server && mvn spring-boot:run    # :8888
cd infrastructure/eureka-server && mvn spring-boot:run    # :8761
cd services/product-service     && mvn spring-boot:run    # :8081
```

## Smoke test

```bash
curl http://localhost:8888/actuator/health                        # {"status":"UP"}
curl http://localhost:8888/product-service/default                # app.source = config-server
curl http://localhost:8761/                                       # Eureka dashboard
curl -X POST http://localhost:8081/api/v1/products \
     -H 'Content-Type: application/json' \
     -d '{"name":"Laptop","description":"15-inch laptop","price":999.99,"category":"Electronics"}'
curl http://localhost:8081/api/v1/products                        # list with the new product
```

## Tests

```bash
cd infrastructure/config-server && mvn test
cd infrastructure/eureka-server && mvn test
cd services/product-service     && mvn test
```
