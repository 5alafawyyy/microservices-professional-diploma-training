# Lab 17 — Session 21

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Enable Istio Service Mesh with mTLS.

## 2. Problem Being Solved
Traffic between microservices in K8s is unencrypted and hard to route dynamically.

## 3. Architecture
* **Before the lab:** Standard K8s services.
* **After the lab:** Istio Envoy sidecars intercept all traffic; mTLS enforced.
* **Architectural Impact:** Offloads networking and security to the infrastructure layer.

## 4. Concepts Explained
Service Mesh, Sidecar Pattern, mTLS, Traffic Split/Canary.

## 5. Prerequisites
Lab 16, K8s cluster.

## 6. Precise Implementation Tasks
1. Label namespace for injection.
2. Apply PeerAuthentication STRICT.
3. Apply VirtualService for 80/20 split.

## 7. Important Configuration
`istio-injection=enabled`.

## 8. Expected Files/Components
`k8s/istio/`

## 9. Acceptance Criteria
mTLS enforced between pods.

## 10. Verification Commands/Tests
Curl from un-injected pod to injected pod.

## 11. Expected Behavior
Connection refused (mTLS enforcement).

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** Sidecars not injected.
* **Troubleshooting Guidance:** Ensure namespace label exists before pods are created.

## 13. Relationship to Curriculum
* **Context:** Advanced K8s networking.
* **Source Evidence:** Reconstructed from reference implementation and S21 deck.
* **Related Commit(s):** `session-21: add-istio-mtls-and-weighted-traffic-split`
