# Session 14 — GitOps & Deployments

Source files:
- `Session_14_GitOps_Deployments.pdf` — course delivery deck (25 slides): push vs pull-based decision tables, ArgoCD reconciliation loop, Application CRD, canary 80/20, deployment strategies, Lab 11B, homework/checkpoint.
- `Session_14_GitOps_Deployments_more.pdf` — long-form lecture deck (49 slides, numbered sections 1–50): GitOps fundamentals, desired vs actual state, drift, sync modes, reconciliation, Lab 1–7 flow, final mental model.

Source note: the two files are NOT duplicates. They are two decks for the same session (long-form theory vs. course delivery deck). They use different lab numbering (Lab 11B vs Lab 1–7) and different repository layouts (see section 17); both are recorded verbatim in section 17. One framing difference must be recorded as stated: the long deck ends by naming the next session "Session 15 — Helm & Kubernetes Packaging", while the course deck defines Session 15 as "Kubernetes Core" and places Helm in Session 16. Both statements appear in the slides.

## 1. Why this topic exists

- Session 13 answered: "How do we automatically turn source code into a tested Docker image?" The result: Developer -> Git Push -> GitHub Actions -> Build + Test -> Docker Image -> Container Registry. "But we stopped there." New problem: "How do we reliably deploy that image to Kubernetes?"
- Course-deck continuity: "Session 13 taught the pipeline to build and push. Session 14 teaches the cluster to pull and deploy." Together: "every push to main is automatically tested, packaged, and deployed. No manual steps."
- The drift story (course deck): the S13 pipeline builds the image, pushes it, then runs `kubectl apply -f k8s/` to deploy. Month 2: production incident; Ops SSHs into the cluster and edits a ConfigMap directly; they forget to commit the fix. Git now says something different than the cluster — this is DRIFT. Next CI run: `kubectl apply` overwrites the manual fix; the incident returns. Two questions the team cannot answer: who changed the cluster? And when did it drift? "GitOps solves both: Git is the audit trail. ArgoCD is the drift detector."
- Long-deck framing of push-based coupling: CI knows about Kubernetes, needs Kubernetes credentials, changes the cluster directly. GitOps takes a different approach: Git contains the desired state; an agent inside the cluster applies it.
- Key insight (course deck): "GitOps does NOT replace CI. It replaces the deployment step. S13 still tests and builds."
- Why drift detection matters (long deck): without GitOps, someone runs `kubectl edit deployment product-service`; six months later: "Why is production configured this way?" Nobody knows. With GitOps the intended configuration is stored in Git: who changed it? When? What changed? Why? Which commit introduced it? This improves auditing, reproducibility, troubleshooting, collaboration.
- The Golden Rule: "Do not manually modify Kubernetes resources that are managed by GitOps." Need to change replicas? Change Git -> Commit -> Argo CD -> Kubernetes. Not `kubectl edit` — "The second approach creates drift."

## 2. Core concepts

- GitOps (student definition, long deck): "a deployment approach where Git stores the desired state of the system, and an automated agent continuously makes the running environment match that desired state." In our course: Git -> Desired Kubernetes State -> Argo CD -> Kubernetes.
- Desired state vs actual state: desired = what the manifests say should exist (3 Product Service replicas); actual = what is really running (Pod 1 Running, Pod 2 Running, Pod 3 CrashLoopBackOff -> 2 healthy). "Kubernetes controllers continuously work to move Actual State toward Desired State."
- Argo CD: a Kubernetes-focused continuous delivery tool ("GitOps controller"). Job: Watch Git -> Read desired state -> Compare with Kubernetes -> Synchronize when necessary. Mental model: "GitHub Actions = Build & Test; Argo CD = Deploy & Reconcile." Do not think "Argo CD is another CI server."
- Reconciliation: repeatedly comparing desired state with actual state and taking action when they differ. If they match: Desired = Actual -> synchronized. If they differ, Argo CD can take action to bring the cluster back toward the desired state.
- Drift: Git says `replicas: 3` but someone runs `kubectl scale deployment product-service --replicas=5`; the cluster has drifted from the desired state. Argo CD detects OutOfSync (long deck: within the reconciliation loop; course deck: "detects and alerts within seconds"). With `selfHeal: true`, it reverts manual kubectl changes.
- Sync: synchronization = compare Git desired state with Kubernetes actual state -> apply necessary changes. Example: Git image sha-222222 vs cluster sha-111111 -> after sync, cluster sha-222222.
- Manual Sync: Argo CD detects OutOfSync but waits for an operator to synchronize (Git change -> Argo CD detects -> Human approves/syncs -> Kubernetes). Automatic Sync: Git change -> Argo CD detects -> automatic synchronization -> Kubernetes.
- Synced vs OutOfSync (sync status): Synced = running cluster corresponds to the desired configuration ArgoCD is tracking (Git = Cluster); OutOfSync = there is a difference (e.g. Git replicas 3, cluster replicas 2).
- Healthy vs Unhealthy (health status): an application can be Synced but Unhealthy — "Kubernetes may have applied the desired Deployment, but the Pods may be failing." SYNC STATUS and HEALTH STATUS are not the same thing: Synced = configuration matches desired state; Healthy = resources are functioning as expected. "This distinction is extremely important when troubleshooting."
- Push-based vs pull-based: push-based = CI pipeline applies changes, external, needs cluster credentials; pull-based GitOps = ArgoCD agent inside the cluster, no external credentials.
- Declarative vs imperative: imperative = "Tell the system exactly what command to execute" (`kubectl scale deployment product-service --replicas=3`); declarative = "Describe the state you want" (`spec: replicas: 3`). "Kubernetes determines what actions are necessary to achieve that state. GitOps strongly favors the declarative model."
- Desired-state source (ArgoCD Application CRD key fields, course deck): Source (Git repo + path + revision to watch), Destination (cluster + namespace to deploy to), Sync Policy (automated vs manual), Health Status (Healthy / Progressing / Degraded), Sync Status (Synced / OutOfSync).
- Image vs deployment configuration: "The registry stores the artifact. Git stores the desired deployment state." The registry contains `product-service:sha-a81c92d`; the GitOps repository declares which image Kubernetes SHOULD run (`image: repository: ghcr.io/company/product-service, tag: sha-a81c92d`).
- Deployment strategies: Rolling Update (default; pods replaced gradually v1 v1 v1 -> v2 v1 v1 -> v2 v2 v1 -> v2 v2 v2); Blue-Green; Canary.
- Canary: introducing a new version to a small portion of traffic or capacity first (95/5 -> 90/10 -> 50/50 -> 0/100). "Expose the new version gradually and observe it before sending all traffic to it."
- Replica canary vs traffic canary: 9 replicas v1 + 1 replica v2 is a capacity/replica approximation (~90/10 by pod count), "not necessarily a precise traffic split" of users. Traffic distribution depends on Service load balancing, connection behavior, request patterns, clients, networking layer. "A true traffic canary requires traffic-management capabilities."
- Kubernetes Service limitation: "Kubernetes Service itself is not a sophisticated percentage-based canary controller." For precise traffic control: Ingress controllers, Service mesh, Gateway/API routing, Progressive delivery tools "may be used. This becomes important later in the course."
- Deployment = GitOps-managed resources; the two governance rules: Git is the single source of truth; do not edit managed resources manually.
- Argo CD is not replacing Kubernetes ("Kubernetes = Runs and manages workloads; Argo CD = Synchronizes Kubernetes with Git; Git = Stores desired configuration") and not replacing GitHub Actions ("GitHub Actions = Build, Test, Package, Publish; Argo CD = Deploy, Synchronize, Detect drift, Reconcile").

## 3. Architecture

- Session 13 + 14 complete flow (course deck): SESSION 13 — CI (done): Code -> mvn test -> Docker build -> Push image to GHCR. SESSION 14 — GITOPS (today): Registry Image -> Update Git Manifest -> ArgoCD Sync -> Kubernetes Cluster.
- Long-deck complete flow: APPLICATION SIDE: Developer -> git push -> Application Repository -> GitHub Actions (Compile, Test, Quality Gate, Docker Build, Docker Push) -> Container Registry. GITOPS SIDE: GitOps Repository -> desired state -> Argo CD -> reconcile -> Kubernetes -> Pods. Missing connection, stated explicitly: "Something has to update the GitOps repository with the new image version" (sha-OLD -> sha-NEW; "That update can be automated").
- Reconciliation loop diagram (course deck): Developer -> git push manifest -> Git Repository (desired state) -> ArgoCD polls every 3 min -> Cluster kubectl apply (actual state). CI pushes new image SHA; ArgoCD detects change; if `syncPolicy: automated` -> applies immediately; if `manual` -> shows as OutOfSync, waits for approval. Drift scenario: someone runs kubectl apply manually -> ArgoCD detects OutOfSync -> alerts + reverts (if `selfHeal: true`).
- Complete GitOps lifecycle (long deck, 14 steps): 1. Developer changes code -> 2. GitHub Actions runs -> 3. Tests pass -> 4. Docker image is built -> 5. Image pushed to GHCR -> 6. GitOps manifest is updated -> 7. Git commit is created -> 8. Argo CD detects change -> 9. Application becomes OutOfSync -> 10. Argo CD synchronizes -> 11. Kubernetes updates resources -> 12. Pods start -> 13. Argo CD observes health -> 14. Application becomes Synced/Healthy. "That is the heart of Session 14."
- Will Argo CD correct drift? Section 36 (long deck): "If automated self-healing is configured, Argo CD can restore the desired state" (Git desired sha-222222 -> Argo CD sees drift -> Kubernetes currently sha-333333 -> Reconcile -> sha-222222).
- Kubernetes manifests in scope today (course deck scope boundary): "Today we cover exactly enough K8s to read a Deployment and connect it to ArgoCD: Deployment, Service, ConfigMap." Explicitly deferred: Ingress (external HTTP routing) -> Session 15; RBAC, Secrets -> Session 15; HPA (autoscaling) -> Session 16; StatefulSets, PersistentVolumes -> Session 16.
- Trainer guidance — what to say when questions go beyond scope: "How do users access this from outside the cluster?" -> Ingress — Session 15; "How do we store passwords securely?" -> Kubernetes Secrets — Session 15; "Can Kubernetes scale this automatically?" -> HPA — Session 16; "What about stateful databases in Kubernetes?" -> StatefulSets + PVs — Session 16. "Pattern: validate the question, name the session, move on. Never improvise K8s depth."
- Repository structure for GitOps (course deck): microservices-pro-platform/k8s/product-service/ containing deployment.yaml, service.yaml, configmap.yaml. "ArgoCD watches this path in Git and syncs it to the cluster. When CI pushes a new image SHA, update deployment.yaml image field here. ArgoCD detects the change -> syncs the new image to the cluster automatically."
- Long-deck repository model (section 6): TWO repositories. Application Repository (microservices-pro-platform; services/product-service, order-service, payment-service; responsibility: Source Code, Build, Tests, Dockerfile) and GitOps Repository (microservices-pro-gitops; k8s/product-service/{deployment.yaml, service.yaml, kustomization.yaml}, order-service/{deployment.yaml, service.yaml}; responsibility: Deployment Configuration, Desired State, Environment Configuration). Argo CD is configured to watch Repository + Path (example: repo microservices-pro-gitops, path environments/production/product-service).
- Canary architecture 80/20 (course deck): STABLE 8 pods sha-OLD + CANARY 2 pods sha-NEW, same Service selector `app=product-service`. "Kubernetes load-balances by pod count: 8 stable + 2 canary = 10 total -> ~80% stable, ~20% canary by probability." Both Deployments visible under one ArgoCD Application; "Git remains the single source of truth."
- Canary promotion/rollback (course deck): "To promote: increase canary replicas to 10, reduce stable to 0. To rollback: delete canary."
- Workflow diagram students must be able to explain (long deck section 48): SOURCE CODE -> GitHub Actions -> (Tests / Docker Build -> Container Registry) -> GitOps Repository -> Argo CD -> (Kubernetes / Drift Detection) -> Deployment -> Pods. And roles: GitHub Actions = CI/artifact production; GitOps Repository = desired deployment state; Argo CD = reconciliation/deployment; Kubernetes = runtime platform.
- End-to-end pipeline stages used in the demo (course deck project progress): Code (S13 CI) test+build+push -> Update Git manifest -> (S14 GitOps) ArgoCD syncs -> Pods updated.

## 4. Technologies

- Argo CD — exact identifiers stated in the slides: `apiVersion: argoproj.io/v1alpha1`, `kind: Application`; metadata namespace `argocd` ("ArgoCD's own namespace"); `spec.project: default`; `source.repoURL`, `source.path`, `source.targetRevision`; `destination.server: https://kubernetes.default.svc` ("in-cluster (ArgoCD runs in the same cluster)"); `syncPolicy.automated` with `prune: true` and `selfHeal: true`; `syncOptions: - CreateNamespace=true`.
- Argo CD polling: "polls every 3 min" (course deck reconciliation diagram). Drift alerting: "ArgoCD detects and alerts within seconds."
- Kubernetes (Deployment, Service, ConfigMap) — manifests as code; used here at intro level only.
- Container registry: GHCR (`ghcr.io`) — images like `ghcr.io/org/product-service:sha-abc1234`, `ghcr.io/company/product-service:sha-a81c92d`; Git commit SHA image tags.
- GitHub Actions — referenced as the CI tool from Session 13 (Compile, Test, Quality Gate, Docker Build, Docker Push; "GitHub Actions | update image tag" to the GitOps Repository).
- Kubernetes CLI: `kubectl apply`, `kubectl scale deployment product-service --replicas=5`, `kubectl get pods` (acceptance criteria); `kubectl edit deployment product-service` (anti-pattern example).
- `imagePullSecret` — mentioned in common issues ("GHCR private images need an imagePullSecret in the namespace"); no further details.
- Helm — mentioned only as a note: "ArgoCD also supports Helm charts as a deployment source -- covered in Session 16 (Kubernetes Advanced)."
- No exact tool versions (Argo CD version, kubectl version) are stated anywhere in the slides. UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- GitOps; desired state; actual state; reconciliation; drift; drift detection; self-healing (`selfHeal`).
- Push-based CI/CD; pull-based GitOps; source of truth; audit trail.
- Argo CD; Argo CD Application; Application CRD; GitOps controller; sync; synchronize; syncPolicy (`automated` / `manual`); `prune`; `CreateNamespace`.
- Sync Status: Synced / OutOfSync. Health Status: Healthy / Progressing / Degraded (course deck wording; long deck uses "Healthy / Unhealthy").
- Manifest (declarative description of a Kubernetes resource); Declarative vs Imperative.
- Deployment; Service (ClusterIP); ConfigMap; replica; pod count vs traffic split.
- Deployment strategies: Rolling Update; Blue-Green; Canary; "weight-based" canary (course deck strategy table); replica canary vs traffic canary.
- Canary monitoring signals: error rate (HTTP 5xx); latency (p95, p99); resource usage (CPU, memory); application metrics (orders failed, payments failed, product searches failed); logs (exceptions, timeouts, connection failures).
- GitOps Repository; Application Repository; environment configuration ("environments/production/product-service" example).
- Golden Rule (do not manually modify GitOps-managed resources).

## 6. Code concepts

- Deployment manifest for product-service (course deck live coding): `apiVersion: apps/v1`, `kind: Deployment`, `metadata: name: product-service, namespace: ecommerce`; `spec.replicas: 2`; `selector.matchLabels: { app: product-service }`; container `image: ghcr.io/org/product-service:sha-abc1234`, `ports: [{ containerPort: 8081 }]`, `resources.requests: { cpu: 100m, memory: 256Mi }`, `resources.limits: { cpu: 500m, memory: 512Mi }`.
- Long-deck Deployment variant: `image: ghcr.io/company/product-service:sha-a81c92d`, `containerPort: 8080`, `replicas: 3` (both variants are in the slides; ports/images differ between decks).
- Service (ClusterIP): `apiVersion: v1`, `kind: Service`, `metadata: { name: product-service, namespace: ecommerce }`, `spec.selector: { app: product-service }`, `ports: [{ port: 8081, targetPort: 8081 }]`, `type: ClusterIP` (# internal only — not exposed externally).
- ConfigMap: `metadata.name: product-config`, namespace ecommerce; `data`: `datasource.url: jdbc:postgresql://postgres:5432/productdb`, `redis.host: redis`, `eureka.url: http://eureka-server:8761/eureka/`. "NOTE: passwords never in ConfigMap -- use Secrets (S15)."
- ArgoCD Application CRD (course deck): `k8s/argocd/product-service-app.yaml` — `apiVersion: argoproj.io/v1alpha1`; `kind: Application`; `metadata: name: product-service, namespace: argocd`; `spec.project: default`; `source.repoURL: https://github.com/org/microservices-pro-platform`; `source.targetRevision: main`; `source.path: k8s/product-service`; `destination.server: https://kubernetes.default.svc`; `destination.namespace: ecommerce`; `syncPolicy.automated: { prune: true, selfHeal: true }`; `syncOptions: [CreateNamespace=true]`. Comment in slides: "DEV ONLY: automated sync. Production: remove 'automated:' block and approve manually."
- Long-deck Application CRD variant: repoURL `https://github.com/company/microservices-pro-gitops.git`, path `environments/production/product-service`, targetRevision main, destination namespace production; "Don't memorize it yet. Understand what it says."
- Reading the Application YAML like English (long deck): `repoURL` = Where is the desired configuration stored?; `path` = Which directory contains the configuration?; `targetRevision` = Which Git revision should be used?; `destination.server` = Which Kubernetes cluster should receive the resources?; `namespace` = Which namespace should be used as the destination.
- Canary Deployment manifest (course deck): `k8s/product-service/deployment-canary.yaml` — `name: product-service-canary`, namespace ecommerce, `replicas: 2` ("2 out of 10 total = 20%"), `selector.matchLabels: { app: product-service, track: canary }`. "Service selector 'app: product-service' routes to BOTH stable (8 pods) and canary (2 pods)."
- GitOps commit example (long deck): `- image: ...sha-111111` becomes `+ image: ...sha-222222`; CI commit message example "Update product-service image to sha-222222".
- Long-deck declarative commit example: `git add deployment.yaml; git commit -m "Scale product service to three replicas"; git push`.
- No CI workflow YAML is shown in either S14 deck (the CI side is referenced from Session 13).

## 7. Configuration

- Argo CD Application file location (course deck): `k8s/argocd/product-service-app.yaml`.
- Argo CD watches a Git repo + path; revision `main`; destination in-cluster (`https://kubernetes.default.svc`) and namespace `ecommerce` (dev) / `production` (long deck).
- Sync policy convention (course deck): "Dev: automated — Prod: manual." Comment: "DEV ONLY: automated sync. Production: remove 'automated:' block and approve manually."
- `prune: true` — "delete resources removed from Git"; `selfHeal: true` — "revert manual kubectl changes (drift correction)"; both sit under `syncPolicy.automated` (common issue: "Confirm selfHeal: true sits under syncPolicy.automated").
- `CreateNamespace=true` — "create 'ecommerce' namespace if it doesn't exist."
- GitOps repo layout conventions: course deck `microservices-pro-platform/k8s/product-service/` (deployment.yaml, service.yaml, configmap.yaml); long deck `microservices-pro-gitops` with `environments/dev/product-service/` and `environments/production/product-service/` (deployment.yaml, service.yaml; kustomization.yaml mentioned in the repo listing).
- Namespace used in all examples: `ecommerce` (course deck) / `production` (long deck Application example).
- Image reference convention: `ghcr.io/org/product-service:sha-abc1234` — CI pushes new image SHA; the GitOps manifest's image field is updated (README-style comment in slides).
- No configuration for Argo CD installation itself is given beyond: Lab 3 "Install Argo CD — Deploy Argo CD into the Kubernetes cluster. Conceptually: Kubernetes → argocd namespace → Argo CD server, controllers, supporting components." (long deck).
- UNKNOWN — REQUIRES SOURCE REVIEW: exact Argo CD install command/manifest URL, polling interval configuration, and any ArgoCD RBAC/SSO config are not in the slides.

## 8. Failure scenarios

- The drift incident (course deck problem story): Ops edits ConfigMap directly -> fix not committed -> Git and cluster diverge -> next CI run `kubectl apply` overwrites the fix -> incident returns. Two questions answered by GitOps: who changed the cluster; when did it drift.
- Drift scenario in the reconciliation loop: someone runs kubectl apply manually -> ArgoCD detects OutOfSync -> alerts + reverts (if selfHeal: true). Long deck: without GitOps "someone may manually change production... Six months later: 'Why is production configured this way?' Nobody knows."
- CI-only (`kubectl set image`) pitfall (long deck section 34): cluster changed but Git still says sha-111111 while cluster runs sha-222222 — "Now Git no longer represents reality."
- Course deck "5 Errors You Will Hit":
  1. ArgoCD Application shows OutOfSync right after creation -> "Commit k8s manifests to Git BEFORE applying the Application."
  2. Pods stuck in ImagePullBackOff -> "GHCR private images need an imagePullSecret in the namespace."
  3. Canary pods not receiving traffic -> "Verify canary selector matchLabels includes app: product-service."
  4. ArgoCD selfHeal not reverting manual changes -> "Confirm selfHeal: true sits under syncPolicy.automated."
  5. ArgoCD shows Unknown health status -> "Configure readiness/liveness probes — covered fully in Session 15."
- Long-deck example actual state with failure: "Pod 3 -> CrashLoopBackOff" so actual = 2 healthy replicas out of 3 desired.
- Synced-but-Unhealthy situation: "Kubernetes may have applied the desired Deployment, but the Pods may be failing" — sync status and health status must be checked separately when troubleshooting.

## 9. Trade-offs

- Push-based vs pull-based (course deck table):
  - Who applies changes: CI pipeline — external, needs cluster credentials vs ArgoCD agent — inside cluster, no external credentials.
  - Source of truth: CI pipeline state (may differ from Git) vs Git repository — always.
  - Drift detection: None — cluster can silently diverge vs ArgoCD detects and alerts within seconds.
  - Audit trail: CI logs, if retained vs Git history — every change has author + timestamp.
  - Rollback: re-run old pipeline vs `git revert` -> ArgoCD auto-syncs previous state.
  - Manual changes: silently overridden by next CI run vs ArgoCD marks cluster OutOfSync immediately.
- When to choose which (course deck design choice):
  - Simple deploy, small team, one environment -> Push-based (simpler).
  - Multiple environments (dev/staging/prod) -> Pull-based GitOps.
  - Need audit trail of who changed what, when -> GitOps — every change is a commit.
  - Drift detection: cluster must always match Git -> GitOps — ArgoCD syncs constantly.
  - Kubernetes is the deployment target -> GitOps is the natural fit.
  - Team prefers no cluster credentials in CI server -> GitOps — agent inside cluster pulls.
- "Key insight: GitOps does NOT replace CI. It replaces the deployment step. S13 still tests and builds." (Reinforced by long deck sections 37–38: Argo CD does not replace Kubernetes nor GitHub Actions.)
- Deployment strategies (course deck design choice + comparison table):
  - Zero downtime, instant rollback needed? -> Blue-Green. Test new version with real production traffic? -> Canary (weight-based). Simple replacement, small downtime acceptable? -> Rolling Update (default). Stateful service with database schema changes? -> Blue-Green — switch after migration. Limited resources, can't run two full envs? -> Rolling Update or Canary.
  - Rolling Update: rollback slow — "pods roll back one by one"; resource cost low — no extra infra; "Default, simple deployments."
  - Blue-Green: rollback instant — "switch back to Blue"; resource cost high — "2x infra during switch"; "Zero-downtime, DB migration."
  - Canary: rollback fast — "reduce canary % to 0"; resource cost medium — "controlled ratio"; "Risk mitigation, real users."
- Platform recommendation (course deck): "Rolling Update for non-critical services (product-service read API). Canary for order-service (new payment flow). Blue-Green for config-server/eureka (infrastructure changes)."
- Replica canary vs traffic canary (long deck): "9 replicas v1 / 1 replica v2 is a capacity/replica approximation, not necessarily a precise traffic split... A true traffic canary requires traffic-management capabilities." Don't give students the false impression that `replicas: 9` means exactly 90% of requests.
- Two repositories vs one (long deck section 7): putting everything in one repo is possible; separation gives a cleaner responsibility model ("What is the application?" vs "What should be deployed?"), useful when different teams own app code and infrastructure; production deployment needs additional approval; infrastructure changes need a separate audit trail; multiple environments need different configurations.
- Manual sync vs automatic sync (long deck section 28): "For students, manual synchronization is useful initially because they can observe: Git changed -> Argo CD detects -> Application becomes OutOfSync -> Sync -> Application becomes Synced. It makes the GitOps lifecycle visible. Later, automatic synchronization can be enabled."
- Canary monitoring cost/consequence (long deck section 46): "A canary is useful only if we observe the system" — error rate, latency (p95/p99), resource usage, application metrics, logs. "This connects Session 14 to the observability topics later in the course."

## 10. Common mistakes

- From the course deck "5 Errors You Will Hit" (see section 8 for the fixes): OutOfSync right after creation; ImagePullBackOff for GHCR private images; canary pods not receiving traffic (selector mismatch); selfHeal not reverting (wrong nesting under syncPolicy.automated); Unknown health status (no probes).
- Manual modification of GitOps-managed resources (the Golden Rule violation, long deck section 17).
- Forgetting to commit k8s manifests to Git before applying the ArgoCD Application (course deck).
- Believing replica ratio equals exact traffic percentage (long deck sections 42–44): "We should not give students the false impression that replicas: 9 means exactly 90% of requests."
- Thinking GitOps replaces CI or Kubernetes (long deck sections 37–38): separate tools, different responsibilities.
- Thinking Argo CD is "another CI server" (long deck section 10).
- Running `kubectl set image` from CI instead of updating the Git manifest (long deck sections 34–35): Git stops representing reality.
- Forgetting that sync status and health status are different: "Synced but Unhealthy" is possible.
- Attempting HPA/Secrets/Ingress discussion in this session — the slides explicitly scope them to Sessions 15–16.

## 11. Interview questions

The slides contain no labeled interview/exam section. The questions below are derived strictly from this session's learning objectives and content:
- What is GitOps? Give the student definition and the Git -> Argo CD -> Kubernetes chain.
- Why does drift happen, and how does GitOps detect and correct it?
- Compare push-based CI/CD vs pull-based GitOps across: who applies changes, source of truth, drift detection, audit trail, rollback, manual changes.
- What are the two Git repositories in this course, and what is each responsible for? Why separate them?
- What is reconciliation? What is the difference between Synced/OutOfSync and Healthy/Unhealthy?
- What does the ArgoCD Application CRD connect (source, destination, syncPolicy)? Read each field in plain English.
- What does `selfHeal: true` do? What does `prune: true` do? Where must they sit in the YAML?
- Why did the course choose manual sync for production and automated sync for dev?
- What is the Golden Rule for GitOps-managed resources?
- Compare Rolling Update, Blue-Green, and Canary: rollback speed, resource cost, and when to use each.
- Why is 8 stable + 2 canary only approximately 80/20 traffic? What would a true traffic canary require?
- What signals should you monitor during a canary rollout?
- How does the new image version get from the registry into the GitOps repository? Why not let CI run `kubectl set image` directly?

## 12. What I must memorize

- "Git = Desired State"; "CI produces the application artifact. GitOps declares what should run. Argo CD reconciles that declaration with Kubernetes."
- The complete flow endpoints: Developer -> git push -> Application Repository -> GitHub Actions (Compile/Test/Quality Gate/Docker Build/Docker Push) -> Container Registry -> (update Git manifest) -> GitOps Repository -> Argo CD -> Kubernetes -> Pods.
- Reconciliation loop diagram: ArgoCD polls every 3 min; automated -> applies immediately; manual -> OutOfSync + wait for approval; drift -> OutOfSync -> alerts + reverts (selfHeal: true).
- ArgoCD Application CRD key fields table (Source / Destination / Sync Policy / Health Status / Sync Status) and the exact `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, namespace `argocd`.
- Sync status values (Synced / OutOfSync) vs health status values (Healthy / Progressing / Degraded; long deck also teaches Healthy / Unhealthy) — and that they are NOT the same thing.
- Deployment strategy comparison: Rolling Update (slow rollback, low cost, default), Blue-Green (instant rollback, 2x infra, zero-downtime + DB migration), Canary (fast rollback, controlled ratio, real users).
- Course canary split: 8 stable + 2 canary = ~80/20 by pod count; promote = canary 10, stable 0; rollback = delete canary.
- Canary monitoring signals: 5xx error rate, p95/p99 latency, CPU/memory, business metrics, logs (exceptions, timeouts, connection failures).
- The Golden Rule and the drift incident story (who changed the cluster? when did it drift?).
- The course scope boundary: Deployment/Service/ConfigMap today; Ingress/Secrets -> S15; HPA/StatefulSets/PVs -> S16.

## 13. What I must understand

- Why a deployment step that edits the cluster directly (push-based) breaks the audit trail, and how pull-based GitOps keeps Git authoritative.
- The difference between desired state and actual state, and how "controllers continuously move actual toward desired."
- Why sync status and health status are independent dimensions and how that changes troubleshooting.
- Why `git revert` + auto-sync is a better rollback mechanism than re-running an old pipeline.
- Why the update of the GitOps repository's image tag can be automated by CI (CI -> update image tag -> GitOps Repository -> commit).
- Why replica-ratio canary is an approximation (Service load balancing, connection behavior, request patterns, clients, networking layer).
- Why the course starts with manual sync for learning then enables automatic sync.
- Why the course defers Ingress, RBAC, Secrets, HPA, StatefulSets and PVs to later sessions, and how to handle out-of-scope questions ("validate the question, name the session, move on").
- How the two decks differ in repository layout (single platform repo `k8s/` folder vs separate `microservices-pro-gitops` repo with environments) and why both support the same GitOps principle.

## 14. What I should implement from memory

- Create the k8s manifests for product-service: Deployment (replicas, selector, image with SHA tag, resources requests/limits), Service (ClusterIP), ConfigMap (datasource.url, redis.host, eureka.url — no passwords).
- Commit the manifests to Git BEFORE creating the ArgoCD Application.
- Write the ArgoCD Application CRD: source (repoURL, targetRevision: main, path), destination (in-cluster server, namespace ecommerce), syncPolicy automated with prune + selfHeal, syncOptions CreateNamespace=true; explain production as manual sync.
- Create `deployment-canary.yaml` with `replicas: 2`, labels `{ app: product-service, track: canary }`, new image SHA; verify the Service routes to both stable and canary pods.
- Verify in the ArgoCD UI: Synced + Healthy; kubectl get pods shows 8 stable + 2 canary; test selfHeal by deleting a pod and confirming ArgoCD recreates it within 30s.
- Demonstrate drift: `kubectl scale` or `kubectl edit` a managed resource, observe OutOfSync, then revert by changing Git (not by another kubectl command).
- Practice the promotion/rollback procedure for the canary: increase canary replicas to 10 and reduce stable to 0 (promote); delete canary (rollback).
- Run the long-deck lab flow from memory: create GitOps repo, Deployment manifest, install Argo CD, create Application, sync (OutOfSync -> Synced/Healthy), change replicas 3 -> 4 in Git, create drift with `kubectl scale --replicas=5`.

## 15. Relationship to previous sessions

- Session 13 (CI/CD): builds and pushes the image to GHCR, produces the artifact and the SHA tag that the GitOps manifest references. "Session 13 taught the pipeline to build and push. Session 14 teaches the cluster to pull and deploy." The S13 push-based `kubectl apply` approach is deliberately replaced here (course deck problem story; long deck section 1).
- Session 9 (Docker) and the whole platform: services such as product-service, order-service, payment-service, config-server, eureka-server appear as the deployment targets; the ConfigMap example externalizes `eureka.url` and the datasource URL.
- Phase 2 context (course deck roadmap): S9 Docker, S10 Unit+Int Tests, S11 Contract+Chaos, S12 Saga Orch., S13 CI/CD, S14 GitOps, S15 K8s Core, S16 K8s Adv.
- The course's S13 -> S14 chain: "Code -> (S13 CI) test+build+push -> Update Git manifest -> (S14 GitOps) ArgoCD syncs -> Pods updated."

## 16. Relationship to future sessions

- Session 15 (course deck): "Kubernetes Core: Deployments, Services, Ingress, Probes" — probes fix "ArgoCD shows Unknown health status" (readiness/liveness are fully covered there); Secrets replace the plaintext ConfigMap password pattern; namespaces/ingress/service types deepen the K8s foundation.
- Session 15 (long-deck framing): the closing question — "How do we package these Kubernetes manifests so that managing many microservices and multiple environments does not become a huge YAML-maintenance problem?" — is answered by "Session 15 — Helm & Kubernetes Packaging." (Recorded as stated; the course deck instead places Helm in Session 16.)
- Session 16 (course deck): HPA, Resource Limits, Helm Charts, RBAC, Phase 2 Retrospective; "ArgoCD also supports Helm charts as a deployment source -- covered in Session 16."
- Observability (long deck section 46): canary monitoring (p95/p99 latency, 5xx, business metrics, logs) "connects Session 14 to the observability topics later in the course."
- Traffic management (long deck sections 42–43): Ingress controllers, Service mesh, Gateway/API routing, progressive delivery tools — "This becomes important later in the course."

## 17. Lab relationship

Course deck — "HANDS-ON LAB — Lab 11B — ArgoCD Application + Canary Deployment":
1. "Create k8s/product-service/ -- Deployment + Service + ConfigMap manifests"
2. "Create the ArgoCD Application CRD pointing to your Git repo"
3. "Add deployment-canary.yaml (2 replicas = 20%) and verify traffic split"

Acceptance Criteria (verbatim): "ArgoCD UI shows product-service as Synced + Healthy"; "kubectl get pods shows at least 2 product-service pods"; "2 pods labelled track:canary visible"; "selfHeal test: delete a pod -> ArgoCD recreates it within 30s".

Homework/checkpoint (course deck wrap-up): "Daily Quiz -- 8 questions, 10 minutes." Definition of Done — Session 14: "k8s/product-service/ manifests in Git"; "ArgoCD Application: Synced + Healthy"; "Canary: 2 pods with track:canary label"; "selfHeal verified: deleted pod recreated"; "Commit: session-14: add-k8s-manifests..." Pre-Session 15 Reading — Topic: "Kubernetes Core -- Pods, Deployments, Services, Probes"; questions: "Pod vs Docker container?", "What does a liveness probe check?", "Why does readiness matter in rolling updates?" Next: "Session 15 -- Kubernetes Core: Deployments, Services, Ingress, Probes", Wednesday 3:00–5:30 PM, Online.

Long deck — "Session 14 Practical Lab Flow" (7 labs):
- "Lab 1 -- Create the GitOps Repository": create `microservices-pro-gitops` with `environments/dev/product-service/` containing deployment.yaml and service.yaml.
- "Lab 2 -- Create the Deployment Manifest": "Define: Product Service, 3 replicas, container port 8080, and the appropriate image."
- "Lab 3 -- Install Argo CD": "Deploy Argo CD into the Kubernetes cluster. Conceptually: Kubernetes -> argocd -> Argo CD server, controllers, supporting components."
- "Lab 4 -- Create an Argo CD Application": create `product-service-dev` pointing to the GitOps repository + `dev/product-service`.
- "Lab 5 -- Synchronize": "Observe: OutOfSync. Then synchronize. Observe: Synced and: Healthy."
- "Lab 6 -- Change Git": change `replicas: 3` to `replicas: 4`, commit and push, observe: "Git changed -> Argo CD detects difference -> OutOfSync -> Sync -> 4 replicas."
- "Lab 7 -- Create Drift": "Manually change the Kubernetes deployment: kubectl scale deployment product-service --replicas=5. Git still says: replicas: 4. Observe the difference in Argo CD. This demonstrates drift."

Note the lab numbering difference between the decks (Lab 11B vs Lab 1–7) — both are recorded above exactly as the slides present them. The course deck defines a DoD commit convention (`session-14: add-k8s-manifests...`); the long deck lab flow does not mention a commit convention.
