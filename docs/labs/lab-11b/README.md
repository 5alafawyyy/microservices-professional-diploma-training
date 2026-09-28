# Lab 11B — Session 14

## Documentation Classification
* **Source Status:** NO STANDALONE SOURCE LAB
* **Training Documentation:** RECONSTRUCTED

## 1. Exact Objective
Implement ArgoCD for GitOps deployment.

## 2. Problem Being Solved
Manual `kubectl apply` leads to configuration drift between cluster and git.

## 3. Architecture
* **Before the lab:** Push-based or manual deployments.
* **After the lab:** ArgoCD continuously syncs cluster state with Git.
* **Architectural Impact:** Changes deployment paradigm to Pull-based.

## 4. Concepts Explained
GitOps, ArgoCD Application CRD.

## 5. Prerequisites
Lab 11A.

## 6. Precise Implementation Tasks
1. Create ArgoCD manifest for product-service.

## 7. Important Configuration
`Application` spec pointing to repo URL.

## 8. Expected Files/Components
`k8s/argocd/`

## 9. Acceptance Criteria
ArgoCD detects changes in Git and syncs to cluster.

## 10. Verification Commands/Tests
Apply ArgoCD app, check UI.

## 11. Expected Behavior
Sync status: Synced.

## 12. Common Failure Modes & Troubleshooting
* **Failure Mode:** ArgoCD cannot reach private GitHub repo.
* **Troubleshooting Guidance:** Check repository credentials in ArgoCD.

## 13. Relationship to Curriculum
* **Context:** Follows CI pipeline.
* **Source Evidence:** Reconstructed from reference implementation and S14 deck.
* **Related Commit(s):** `session-14: add-argocd-gitops-manifests`
