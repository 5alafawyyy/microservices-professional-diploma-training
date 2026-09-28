content = """# Microservices Professional Diploma — Lab Documentation

This directory contains the documentation for every practical lab and task covered by the 24-session curriculum.

## Documentation Classification
Every lab is strictly classified as one of the following:
* **OFFICIAL SOURCE LAB**: A standalone lab document exists in the course/reference material (mostly Labs 1–6A).
* **RECONSTRUCTED TRAINING LAB**: Practical work reconstructed from the session lecture/deck lab instructions, reference implementation, commit history, and acceptance criteria.

**Note:** We are not saying that every lab has an official source Markdown file. We are saying that every practical lab/task in our training curriculum has a usable training document here.

## Lab Index

| Lab | Session | Topic | Classification |
|---|---|---|---|
| [Lab 01](lab-01/README.md) | S01 | Foundation & Service Discovery | OFFICIAL SOURCE LAB |
| [Lab 02A](lab-02a/README.md) | S02 | API Gateway Routing | OFFICIAL SOURCE LAB |
| [Lab 02B](lab-02b/README.md) | S03 | API Gateway Security | OFFICIAL SOURCE LAB |
| [Lab 03A](lab-03a/README.md) | S04 | Circuit Breaker & Retry | OFFICIAL SOURCE LAB |
| [Lab 03B](lab-03b/README.md) | S05 | Bulkhead & TimeLimiter | OFFICIAL SOURCE LAB |
| [Lab 04A](lab-04a/README.md) | S06 | OpenFeign & Sync Communication | OFFICIAL SOURCE LAB |
| [Lab 05A](lab-05a/README.md) | S07 | Kafka Choreography Saga | OFFICIAL SOURCE LAB |
| [Lab 06A](lab-06a/README.md) | S08 | Postgres & Redis Cache | OFFICIAL SOURCE LAB |
| [Lab 08A](lab-08a/README.md) | S09 | Docker Containerization | RECONSTRUCTED TRAINING LAB |
| [Lab 09A](lab-09a/README.md) | S10 | Integration Testing | RECONSTRUCTED TRAINING LAB |
| [Lab 09B](lab-09b/README.md) | S11 | Contract & Chaos Testing | RECONSTRUCTED TRAINING LAB |
| [Lab 10A](lab-10a/README.md) | S12 | Orchestration Saga | RECONSTRUCTED TRAINING LAB |
| [Lab 11A](lab-11a/README.md) | S13 | CI/CD & Notification Service | RECONSTRUCTED TRAINING LAB |
| [Lab 11B](lab-11b/README.md) | S14 | ArgoCD GitOps | RECONSTRUCTED TRAINING LAB |
| [Lab 12A](lab-12a/README.md) | S15 | K8s Core Objects | RECONSTRUCTED TRAINING LAB |
| [Lab 12B](lab-12b/README.md) | S16 | Helm, HPA & RBAC | RECONSTRUCTED TRAINING LAB |
| [Lab 13](lab-13/README.md) | S17 | Observability Stack | RECONSTRUCTED TRAINING LAB |
| [Lab 14](lab-14/README.md) | S18 | CQRS Pattern | RECONSTRUCTED TRAINING LAB |
| [Lab 15](lab-15/README.md) | S19 | Keycloak IdP | RECONSTRUCTED TRAINING LAB |
| [Lab 16](lab-16/README.md) | S20 | OAuth2 Resource Server | RECONSTRUCTED TRAINING LAB |
| [Lab 17](lab-17/README.md) | S21 | Istio Service Mesh | RECONSTRUCTED TRAINING LAB |
| [Lab 18](lab-18/README.md) | S22 | Transactional Outbox | OFFICIAL SOURCE LAB |
| [Lab 19](lab-19/README.md) | S23 | K6 Load Testing | OFFICIAL SOURCE LAB |

"""

with open('docs/labs/README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated docs/labs/README.md")
