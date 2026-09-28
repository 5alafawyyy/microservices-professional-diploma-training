# Lab 12A — Session 15

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Write core Kubernetes manifests (Deployment, Service).

## 2. Problem Being Solved
Docker Compose does not provide self-healing or cluster orchestration.

## 3. Architecture
* **Before the lab:** Docker Compose.
* **After the lab:** Kubernetes cluster running product-service.
* **Architectural Impact:** Moves platform to enterprise container orchestration.

## 4. Concepts Explained
Pods, Deployments, Services, Liveness/Readiness Probes.

## 5. Prerequisites
Lab 11B.

## 6. Precise Implementation Tasks
1. Write `deployment.yaml`.
2. Write `service.yaml`.
3. Add actuator probes.

## 7. Important Configuration
`livenessProbe`, `readinessProbe` paths.

## 8. Expected Files/Components
`k8s/manifests/`

## 9. Acceptance Criteria
Pod schedules and reports healthy via Readiness probe.

## 10. Verification Commands/Tests
`kubectl get pods -w`.

## 11. Expected Behavior
Pod reaches `1/1 Running`.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** CrashLoopBackOff due to missing DB.
* **Troubleshooting Guidance:** `kubectl describe pod` to view probe failures.

## 13. Relationship to Curriculum
* **Context:** First K8s lab. Prepares for Helm.
* **Source Evidence:** Reconstructed from reference implementation and S15 deck.
* **Related Commit(s):** `session-15: add-kubernetes-core-manifests`
