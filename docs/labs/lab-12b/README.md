# Lab 12B — Session 16

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement Helm charts, HPA, and RBAC.

## 2. Problem Being Solved
Raw YAML files are hard to template. Manual scaling cannot handle sudden load spikes.

## 3. Architecture
* **Before the lab:** Static replicas in raw YAML.
* **After the lab:** Templated Helm chart with Horizontal Pod Autoscaling based on CPU.
* **Architectural Impact:** Enables dynamic elasticity and secure templating.

## 4. Concepts Explained
Helm, HPA, RBAC (ServiceAccounts, Roles).

## 5. Prerequisites
Lab 12A.

## 6. Precise Implementation Tasks
1. Create Helm chart.
2. Add HPA resource.
3. Configure RBAC.

## 7. Important Configuration
`targetCPUUtilizationPercentage`.

## 8. Expected Files/Components
`k8s/helm/`

## 9. Acceptance Criteria
HPA dynamically creates pods when CPU spikes.

## 10. Verification Commands/Tests
`helm install`, run load generator, `kubectl get hpa`.

## 11. Expected Behavior
Replica count increases under load.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Metrics server not installed (HPA shows `<unknown>/50%`).
* **Troubleshooting Guidance:** Ensure K8s cluster has metrics-server enabled.

## 13. Relationship to Curriculum
* **Context:** Completes K8s phase.
* **Source Evidence:** Reconstructed from reference implementation and S16 deck.
* **Related Commit(s):** `session-16: add-helm-hpa-and-rbac`
