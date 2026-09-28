content = """# Microservices Professional Diploma — Lab Documentation

This directory contains the documentation for every practical lab and task covered by the 24-session curriculum.

## Documentation Classification
Every lab is strictly classified using a two-axis model:

**Source Status**
* **OFFICIAL SOURCE LAB**: A standalone official source/reference lab document exists.
* **NO STANDALONE SOURCE LAB**: No standalone official document exists.

**Training Documentation Status**
* **SOURCE-DERIVED / EXPANDED**: Documentation closely based on the official source lab, possibly expanded with further detail.
* **RECONSTRUCTED**: Documentation reconstructed from lecture slides, reference implementation, commits, and acceptance criteria.

> Lab numbering follows the course/reference curriculum and therefore contains intentional numbering gaps. Absence of a lab number does not indicate missing work.

## Lab Index

| Lab | Session | Topic | Source Status | Training Documentation |
|---|---|---|---|---|
| [Lab 01](lab-01/README.md) | S01 | Foundation & Service Discovery | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 02A](lab-02a/README.md) | S02 | API Gateway Routing | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 02B](lab-02b/README.md) | S03 | API Gateway Security | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 03A](lab-03a/README.md) | S04 | Circuit Breaker & Retry | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 03B](lab-03b/README.md) | S05 | Bulkhead & TimeLimiter | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 04A](lab-04a/README.md) | S06 | OpenFeign & Sync Communication | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 05A](lab-05a/README.md) | S07 | Kafka Choreography Saga | OFFICIAL SOURCE LAB | RECONSTRUCTED |
| [Lab 06A](lab-06a/README.md) | S08 | Postgres & Redis Cache | OFFICIAL SOURCE LAB | SOURCE-DERIVED |
| [Lab 08A](lab-08a/README.md) | S09 | Docker Containerization | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 09A](lab-09a/README.md) | S10 | Integration Testing | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 09B](lab-09b/README.md) | S11 | Contract & Chaos Testing | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 10A](lab-10a/README.md) | S12 | Orchestration Saga | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 11A](lab-11a/README.md) | S13 | CI/CD & Notification Service | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 11B](lab-11b/README.md) | S14 | ArgoCD GitOps | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 12A](lab-12a/README.md) | S15 | K8s Core Objects | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 12B](lab-12b/README.md) | S16 | Helm, HPA & RBAC | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 13](lab-13/README.md) | S17 | Observability Stack | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 14](lab-14/README.md) | S18 | CQRS Pattern | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 15](lab-15/README.md) | S19 | Keycloak IdP | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 16](lab-16/README.md) | S20 | OAuth2 Resource Server | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 17](lab-17/README.md) | S21 | Istio Service Mesh | NO STANDALONE SOURCE LAB | RECONSTRUCTED |
| [Lab 18](lab-18/README.md) | S22 | Transactional Outbox | OFFICIAL SOURCE LAB | SOURCE-DERIVED / EXPANDED |
| [Lab 19](lab-19/README.md) | S23 | K6 Load Testing | OFFICIAL SOURCE LAB | SOURCE-DERIVED / EXPANDED |

"""

with open('docs/labs/README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated docs/labs/README.md")
