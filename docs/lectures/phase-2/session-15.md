# Session 15 — Kubernetes Core

Source files:
- `Session_15_Kubernetes_Core.pdf` — course delivery deck (24 slides): pod lifecycle, liveness vs readiness probes, Spring Boot Actuator sub-endpoints, Service types, ConfigMap vs Secret, namespaces, Lab 12A, homework/checkpoint.
- `Session_15_Kubernetes_Fundamentals_Beginner_Tutorial.pdf` — long-form beginner tutorial deck (78 numbered sections): cluster components, kubectl, manifests, probes, Ingress/Gateway API, storage, local clusters (Minikube/kind), Beginner Lab, quick quiz, readiness checklist.

Source note: the two files are NOT duplicates. They are two decks for the same session labels (course delivery deck vs. beginner tutorial). One framing difference must be recorded as stated: the tutorial is titled "Prerequisite for Session 15 — Helm & Kubernetes Packaging" and describes Session 15 as introducing Helm, while the course deck defines Session 15 as "Kubernetes Core" and places Helm in Session 16. Both statements appear in the slides; neither is resolved by invention here. Lab naming also differs (Lab 12A vs "Beginner Lab — Kubernetes From Zero").

## 1. Why this topic exists

- Course deck framing: "Kubernetes has no idea our app is healthy unless we tell it how to ask. That's the whole session." S14 gave us ArgoCD deploying product-service with manifests (Deployment, Service, ConfigMap) — but "K8s has no health signal from our app yet. No probes. DB password sits in plain ConfigMap."
- Problem 1 — "Pod Is 'Running' -- But Not Serving Traffic": the pod is Running; `curl` the product endpoint returns Timeout / 503. The pod is Running but NOT ready: Spring Boot is still loading JPA schemas, connecting to PostgreSQL, registering with Eureka, warming up the cache. Kubernetes sent traffic to the pod before it finished starting — "The first 30 requests fail."
- Problem 2 — "A Silent Deadlock -- Running, But Dead Inside": a pod has been running for 6 hours, silently entered a deadlock (JVM threads all blocked, process still exists, JVM still consuming CPU). `kubectl get pods`: Running. Customers get timeouts; the pod never returns errors, it just hangs forever.
- Root cause of both: "Kubernetes has no health signal from the application. Liveness probe fixes deadlocks. Readiness probe fixes premature traffic. Both are required."
- Beginner tutorial purpose: "Session 14 introduced GitOps and Argo CD and therefore introduced Kubernetes as the deployment target... Before students use Helm, they need a proper Kubernetes foundation. This tutorial fills that gap." Course progression: Docker -> Kubernetes Fundamentals -> Helm -> GitOps/Argo CD + Helm -> Advanced Kubernetes. "The existing Session 15 material assumes students already understand Deployments, Services" (sentence truncated in source).
- "Why We Learn Raw YAML Before Helm" (tutorial section 66): "If students start directly with Helm, the templates can look like magic." Progression: Raw Kubernetes YAML -> Understand Deployment/Service/ConfigMap/Secret -> Repeated YAML becomes obvious -> Helm values + templates -> Rendered Kubernetes YAML.
- Production readiness progression: from "It Deploys" to "It's Production-Ready" — probes give K8s a health signal, Secrets keep the DB password out of ConfigMap.

## 2. Core concepts

- Pod lifecycle (course deck): Pending (scheduled, image pulling, waiting for resources — "K8s waits here": `initialDelaySeconds`) -> Running (container started, JVM starting up, Eureka registering, DB connection pool initializing — liveness starts checks: is JVM alive?) -> Ready (readiness probe passes — pod joins load balancer, traffic can flow; readiness gates checks: is app ready for traffic?) -> Terminating (SIGTERM sent, grace period 30s default, SIGKILL if needed).
- CrashLoopBackOff: "pod keeps crashing. K8s applies exponential backoff (10s, 20s, 40s...) before each restart -- indicates a config/startup error, not a liveness failure."
- Why a Pod, not a container: Docker container = "a running process with its own filesystem and network namespace. The unit Docker manages directly." Kubernetes Pod = "K8s' deployable unit. Wraps one or more containers that share network/storage. You never run containers directly in K8s -- you declare Pods (via Deployments)."
- Liveness probe: "Is this pod still alive?" If it FAILS -> RESTART the pod (kills it and starts a new one). Failure scenario: Deadlock, OOM, Infinite Loops, JVM freeze. Endpoint: `/actuator/health/liveness`. DB connectivity check? No — DB outage does not mean the pod is dead (slide note: a DB outage should not restart the pod).
- Readiness probe: "Is this pod ready to accept traffic?" If it FAILS -> REMOVE from load balancer (pod keeps running). Failure scenario: Spring Boot still starting, warm-up cache loading, DB migration in progress. Endpoint: `/actuator/health/readiness`. DB connectivity check? Yes — "if DB is down, pod should not serve traffic."
- COMMON TRAP: "I only need one probe -- liveness is enough." CORRECT: "They serve different purposes. Configure BOTH. Missing readiness = premature traffic."
- Starter probe (tutorial section 35): Startup probe — "Has the application finished starting?" — "Protect slow-starting applications." Readiness — "Can this Pod receive traffic?" — "Control Service traffic." Liveness — "Is the application still alive?" — "Restart a stuck container."
- "A Pod can be Running but not Ready. That distinction is critical for reliable Services."
- Service concept: "The Service does not track pod IPs directly -- it continuously watches for pods whose labels match its selector. Add a 4th pod with the same label and it automatically joins. Delete one and it's automatically removed. This is why the label selector is the single most important line in a Service manifest."
- Service types: ClusterIP (default; internal only); NodePort (random port 30000–32767; local dev/testing); LoadBalancer (cloud creates L4 load balancer; production external access); ExternalName (tutorial: "DNS alias to an external name for special integration scenarios"); Ingress (HTTP routing with host/path rules — "beyond today's scope" in the course deck, but fully introduced in the tutorial).
- Headless Service — awareness only (tutorial section 27): `spec.clusterIP: None` — "useful for direct Pod discovery, especially in stateful systems. It is not needed for the basic Product Service lab."
- ConfigMap vs Secret (course deck table): ConfigMap = Non-sensitive configuration; plain text in etcd; Safe to commit; examples `datasource.url, redis.host, eureka.url`. Secret = Passwords, tokens, API keys, certificates; base64-encoded in etcd (NOT encrypted by default); never commit — use external secrets manager in prod; examples `DB_PASSWORD, JWT_SECRET, DOCKER_TOKEN`. Rule: "if you would be embarrassed to see it in a git log, it belongs in a Secret, not a ConfigMap."
- Namespace isolation: `ecommerce-dev` (developer testing; lower resource limits), `ecommerce` (integration/staging; what we use in this course), `ecommerce-prod` (production; stricter limits, manual sync policy). "Namespaces provide soft multi-tenancy within a single cluster: resource quotas, RBAC, and network policies per namespace." Tutorial adds: "A namespace is useful isolation, but it is not by itself a complete security boundary."
- Kubernetes fundamentals (tutorial): Kubernetes is "an open-source platform for managing containerized workloads and services using declarative configuration and automation. It continuously works to move the actual cluster state" toward the desired state (sentence truncated in source); provides service discovery/load balancing, automated rollouts and rollbacks, self-healing.
- Desired state and declarative configuration: "Desired: replicas: 3, image: product-service:1.0.0. Kubernetes: continuously works toward that state. This concept becomes the foundation of GitOps in Session 14."
- Manifest anatomy: `apiVersion` (API version), `kind` (object type), `metadata` (name, namespace, labels, annotations), `spec` (desired configuration), `status` ("normally maintained by Kubernetes rather than written by students").
- Beginner resource map (tutorial section 10): Namespace (logical grouping/isolation), Pod (smallest deployable compute unit), Deployment (stateless application rollout and replica management), ReplicaSet (maintains the desired number of matching Pods), Service (stable network endpoint for Pods), ConfigMap (non-sensitive configuration), Secret (sensitive data), Ingress (HTTP/HTTPS routing rules), PersistentVolume/PersistentVolumeClaim (persistent storage abstractions), Job/CronJob (one-time or scheduled work), StatefulSet (stateful workloads with stable identity/storage patterns), DaemonSet (workload intended to run on selected nodes), HorizontalPodAutoscaler (automatic replica scaling).
- Labels and selectors: "Labels identify resources. Selectors find matching resources... A mismatched selector is one of the most common beginner errors."
- Deployment chain: Deployment -> ReplicaSet -> Pods; "provides declarative replicas, rolling updates, and rollback capabilities." "A production Spring Boot service should normally be managed by a Deployment" (not a bare Pod).
- Pods are ephemeral: "Do not design clients around permanent Pod IP addresses." Service gives the stable endpoint; Kubernetes DNS provides stable names (`http://product-service:8080`).
- port vs targetPort vs nodePort: port = port exposed by the Service; targetPort = port on the selected Pod/container; nodePort = port exposed on nodes when using NodePort. Chain: Service port 8080 -> Pod targetPort 8080 -> Spring Boot `server.port=8080`.
- Ingress (tutorial): "a Kubernetes HTTP/HTTPS routing API object. It can route requests by host/path to Services. An Ingress Controller is required to implement the routing." "Ingress does not by itself create an external load balancer or controller. Kubernetes currently recommends Gateway API for new development; Ingress remains stable but its API is frozen."
- Ingress vs Spring Cloud Gateway: SCG is "an application/API gateway used for application-level routing and filters"; Ingress is a Kubernetes traffic-routing API object implemented by an Ingress Controller; "Spring Cloud Gateway may remain the main application gateway while an Ingress/Gateway API layer provides cluster entry."
- Gateway API — awareness: "the modern Kubernetes direction for expressive traffic management... Kubernetes recommends it for new development, but Ingress is still important" to understand.
- Persistent storage (awareness): Pod -> PVC -> PV -> storage backend. "A container filesystem should not be treated as durable database storage." PV = storage resource available to the cluster; PVC = application request for storage; StorageClass = describes dynamic storage provisioning.
- Jobs/CronJobs/StatefulSets/DaemonSets — awareness only: Job (run work until completion, e.g. one-time migration), CronJob (create Jobs on a schedule), StatefulSet (stateful workloads needing stable identity/storage), DaemonSet (run a Pod on each eligible node, common for node agents).
- What Kubernetes does NOT do (tutorial section 68): does not build Spring Boot source code; does not replace Maven; does not replace container images; does not automatically provide your database, Redis, Kafka, or monitoring stack; does not make application code correct; does not remove security responsibilities; does not automatically make every stateful application horizontally scalable; does not replace CI or GitOps.
- Kubernetes vs Docker Compose (tutorial section 67): Compose service ~ Deployment + Service; container ~ container inside a Pod; scale ~ Deployment replicas; environment variables ~ ConfigMap/Secret/env; ports ~ Service; volumes ~ Kubernetes volumes/PVCs; network ~ Kubernetes networking + Services + DNS; `docker compose up` ~ `kubectl apply` / Helm / GitOps; `depends_on` has no direct Kubernetes equivalent — use readiness/health and correct application behavior.
- Spring Boot configuration model (tutorial section 34): Docker Image (Java application + dependencies) + ConfigMap (non-sensitive environment configuration) + Secret (passwords/tokens/keys); "Deployment -- connects the application to configuration."

## 3. Architecture

- Pod lifecycle state diagram (course deck): Pending -> Running -> Ready -> Terminating, with the probe gates annotated: liveness checks start in Running ("is JVM alive?"); readiness gates the transition to Ready ("is app ready for traffic?"); Terminating sends SIGTERM with grace period 30s default, SIGKILL if needed. CrashLoopBackOff backoff 10s/20s/40s annotated below.
- Service-to-pod selection diagram: Service `product-service` with `selector: app: product-service` continuously watches Pod 1/2/3 all labelled `app: product-service`; pods join/leave automatically.
- Namespace layout: `ecommerce-dev` / `ecommerce` / `ecommerce-prod` — one per environment; kubectl defaults to the `default` namespace, "always specify -n ecommerce or set the context."
- Tutorial cluster architecture: Cluster = Control Plane (kube-apiserver, etcd, scheduler, controllers) + Worker Nodes (kubelet, container runtime, Pods).
- Control plane components (tutorial section 7): kube-apiserver — exposes the Kubernetes HTTP API; etcd — stores Kubernetes API data and cluster state; kube-scheduler — selects suitable nodes for unscheduled Pods; kube-controller-manager — runs controllers that reconcile desired and actual state; cloud-controller-manager — optional integration with cloud infrastructure.
- Worker node components (section 8): kubelet — node agent responsible for making sure assigned Pods are running; container runtime — runs containers; networking components — implement the cluster networking model. "Students do not need to administer these components yet. They need to understand that the control plane manages desired state and worker nodes run workloads."
- API-driven model (section 9): kubectl -> kube-apiserver -> ("stores/updates desired state" / "controllers react") -> cluster resources. "Kubernetes objects are persistent records of intent. Most have a desired spec and a system-maintained" status (sentence truncated in source).
- Resource map (section 42): Cluster -> Namespace -> Deployment -> ReplicaSet -> Pods; plus Service (selects Pods), ConfigMap, Secret, Ingress/Gateway resources, PVC, HPA (later).
- Request flow (section 43): Client -> Load Balancer / Ingress / Gateway -> Service -> Pod A/B/C -> Spring Boot.
- Docker image to Kubernetes chain (section 44): Spring Boot source -> Maven tests/build -> Docker/OCI image -> Container Registry -> Deployment -> Pods -> Service -> Ingress/Gateway/LoadBalancer.
- Cloud deployment mental model (section 58): GitHub -> CI (Test, Build, Push image) -> Registry -> GitOps Repository -> Argo CD -> Managed Kubernetes -> (Deployment, Service, ConfigMap, Secret, Ingress/Gateway, HPA).
- Full course mental model (section 75): Source Code -> Maven + Tests -> Docker Image -> Container Registry -> GitOps Repository -> Helm -> Argo CD -> Kubernetes -> (Deployment -> Pods; Service; ConfigMap; Secret; Ingress/Gateway; Storage; HPA).
- S14 -> S15 -> S16 context (course deck): S14 manifests intro (Deployment/Service/ConfigMap) -> S15 probes, service types, Secrets, namespaces make deployment production-ready -> S16 HPA, Resource Limits, Helm Charts, RBAC.
- Demo observation (course deck): `kubectl describe pod` shows "Warning Unhealthy ... Readiness probe failed: HTTP 503"; "the Warning line disappears once Spring Boot finishes startup -- readiness flips to Healthy and the pod joins the Service endpoints."

## 4. Technologies

- Kubernetes (workload manifest API versions mentioned): `apps/v1` (Deployment), `v1` (Service, ConfigMap, Secret, Namespace, ServiceAccount), `networking.k8s.io/v1` (Ingress), `rbac.authorization.k8s.io/v1` (appears in S16).
- kubectl — commands listed in the tutorial (exact): `kubectl version --client`; `kubectl cluster-info`; `kubectl get nodes`; `kubectl get namespaces`; `kubectl get pods -A`; `kubectl get all -n ecommerce`; `kubectl describe pod <pod> -n ecommerce`; `kubectl logs <pod> -n ecommerce`; `kubectl exec -it <pod> -n ecommerce -- sh`; `kubectl apply -f file.yaml`; `kubectl delete -f file.yaml`; `kubectl get svc -n ecommerce`; `kubectl get ingress -n ecommerce`; `kubectl get events -n ecommerce --sort-by=.lastTimestamp`. Plus `kubectl config current-context`, `kubectl config get-contexts`, `kubectl config use-context <context-name>`, `kubectl get endpointslice -n ecommerce`, `kubectl rollout status/history/undo`, `kubectl scale`, `kubectl set image`, `kubectl port-forward service/hello 8080:80`, `kubectl run curl-test --image=curlimages/curl --rm -it -n ecommerce -- sh`, `kubectl logs --previous` (course deck).
- Local clusters (tutorial sections 48–55): Minikube ("beginner-friendly local Kubernetes"; `minikube start --driver=docker`; `minikube status`; `minikube addons enable metrics-server` appears in S16; `minikube service hello -n ecommerce`; `minikube stop/start/delete`); kind ("Kubernetes nodes running as Docker/Podman containers"; `kind create cluster --name microservices`; `kind delete cluster --name microservices`); Docker Desktop Kubernetes ("convenient if Docker Desktop is already installed"); online playground; kubeadm ("advanced cluster creation/administration; not the first learning environment"). Recommended course setup: "use either Minikube with the Docker driver or kind. Minikube is a good primary beginner walkthrough; kind is an excellent alternative."
- Spring Boot side: `spring-boot-starter-actuator` (required in pom.xml); `management.endpoints.web.exposure.include: health,info`; `management.health.livenessstate.enabled: true`; `management.health.readinessstate.enabled: true`; endpoints `/actuator/health/liveness`, `/actuator/health/readiness`. Tutorial variant: `management.endpoint.health.probes.enabled: true` with probes on port 8080.
- Example images in manifests: `nginx:1.27` (first Pod, and `kubectl create deployment hello --image=nginx:1.27`), `curlimages/curl` (in-cluster test), `ghcr.io/OWNER/product-service:1.0.0` / `1.1.0` (tutorial), `ghcr.io/org/product-service:sha-abc1234` (S14 continuity).
- Cloud managed Kubernetes (awareness): AWS EKS, Microsoft Azure AKS, Google Cloud GKE.
- Course deck product-service port: 8081 (probes, Service, Deployment); tutorial uses port 8080 (Product Service examples). Both appear in the slides as written.
- Secret tooling (dev/prod note): base64 `echo -n 'pw' | base64`; production alternatives named: Sealed Secrets / Vault / AWS Secrets Manager. No versions/configurations for these tools are provided — UNKNOWN — REQUIRES SOURCE REVIEW.
- No exact Kubernetes, kubectl, Minikube, or kind version numbers are stated in the slides. UNKNOWN — REQUIRES SOURCE REVIEW.

## 5. Important terminology

- Pod; container; Pod lifecycle (Pending / Running / Ready / Terminating); CrashLoopBackOff; exponential backoff (10s, 20s, 40s).
- Liveness probe; readiness probe; startup probe; `initialDelaySeconds`; `periodSeconds`; `failureThreshold`; `periodSeconds`; probe "gates."
- Spring Boot Actuator; `/actuator/health/liveness`; `/actuator/health/readiness`; `livenessstate`; `readinessstate`; `spring-boot-starter-actuator`; HTTP 200; readiness probe failed: HTTP 503.
- Service; ClusterIP; NodePort (30000–32767); LoadBalancer; ExternalName; headless Service (`clusterIP: None`); port vs targetPort vs nodePort; label selector; endpoints; endpointslice.
- ConfigMap; Secret; Opaque Secret; base64; etcd; "NOT encrypted by default"; `secretKeyRef`; `envFrom` / `configMapRef`.
- Namespace; soft multi-tenancy; `ecommerce-dev` / `ecommerce` / `ecommerce-prod`; `kubectl config set-context --current --namespace=ecommerce`.
- Deployment; ReplicaSet; rolling update; rollback; `kubectl rollout status` / `history` / `undo`; scaling; self-healing.
- Manifest; `apiVersion` / `kind` / `metadata` / `spec` / `status`; desired state; declarative.
- Control plane (kube-apiserver, etcd, kube-scheduler, kube-controller-manager, cloud-controller-manager); worker node (kubelet, container runtime); cluster; context.
- Ingress; Ingress Controller; Gateway API; Spring Cloud Gateway (contrast); PV / PVC / StorageClass; Job / CronJob / StatefulSet / DaemonSet; HPA (awareness).
- Minikube; kind; Docker Desktop Kubernetes; kubeadm; EKS / AKS / GKE.

## 6. Code concepts

- Actuator configuration (course deck application.yml): `management: endpoints: web: exposure: include: health,info`; `management.health.livenessstate.enabled: true`; `management.health.readinessstate.enabled: true`. "Both endpoints require spring-boot-starter-actuator in pom.xml AND the livenessstate/readinessstate flags enabled. Without both, the sub-health endpoints do not exist -- probes will 404. Rule: never add DB or Redis checks to the liveness group -- a DB outage should not restart the pod. DB checks belong in readiness."
- Probe configuration on product-service Deployment (course deck):
  - `livenessProbe.httpGet.path: /actuator/health/liveness`, port 8081; `initialDelaySeconds: 60` ("Spring Boot needs time to start. For DEV inly: reduce to 30 for faster feedback" — slide typo preserved); `periodSeconds: 10`; `failureThreshold: 3` ("restart after 3 consecutive failures").
  - `readinessProbe.httpGet.path: /actuator/health/readiness`, port 8081; `initialDelaySeconds: 30` ("readiness checked earlier -- pod might be alive before ready"); `periodSeconds: 5`; `failureThreshold: 3` ("remove from LB after 3 failures").
- Tutorial probe example (port 8080): readinessProbe `initialDelaySeconds: 10, periodSeconds: 5`; livenessProbe `initialDelaySeconds: 30, periodSeconds: 10`; "Tune timings using real startup/health behavior; do not copy arbitrary production values."
- Secret manifest (course deck): `apiVersion: v1`, `kind: Secret`, `metadata: name: product-secrets, namespace: ecommerce`, `type: Opaque`, `data: DB_PASSWORD: cG9zdGdyZXNwYXNzd29yZA==` (`# base64('postgrespassword')`), "DEV ONLY: hardcoded base64. Prod: Sealed Secrets / Vault / AWS Secrets Manager."
- Secret reference in Deployment (course deck): `env: - name: SPRING_DATASOURCE_PASSWORD` with `valueFrom: secretKeyRef: {name: product-secrets, key: DB_PASSWORD}`.
- Tutorial Secret variant: `kind: Secret`, `type: Opaque`, `stringData: DB_USERNAME: product, DB_PASSWORD: change-me`; reference via `env.valueFrom.secretKeyRef`; "Secret does not mean 'automatically fully secure'... Never commit real production secrets to Git."
- ClusterIP Service (course deck): `apiVersion: v1`, `kind: Service`, `metadata: name: product-service, namespace: ecommerce`, `spec.selector.app: product-service`, `ports: - port: 8081, targetPort: 8081`, `type: ClusterIP` ("# default -- omit type: for same result"). Commented NodePort variant: `nodePort: 30081` ("optional -- K8s assigns random if omitted"), "DEV ONLY: NodePort exposes on every node's IP. Never use in production."
- Tutorial Service: `type: ClusterIP`, `port: 8080`, `targetPort: 8080`; internal call `http://product-service:8080`.
- ConfigMap (tutorial): `kind: ConfigMap`, `metadata.name: product-service-config`, namespace ecommerce; `data: SPRING_PROFILES_ACTIVE: "kubernetes", LOG_LEVEL: "INFO", APP_NAME: "product-service"`; injection via `envFrom: - configMapRef: name: product-service-config` (or mounted as files).
- Tutorial first Pod: `kind: Pod`, `name: hello-pod`, image `nginx:1.27`, `containerPort: 80` — "useful for learning, but a production Spring Boot service should normally be managed by a Deployment."
- Tutorial Deployment: `replicas: 2`, image `ghcr.io/OWNER/product-service:1.0.0`, `containerPort: 8080`; commands: `kubectl apply -f deployment.yaml`, `kubectl get deployment|replicaset|pods -n ecommerce`, `kubectl describe deployment product-service -n ecommerce`, `kubectl rollout status/history deployment/product-service -n ecommerce`.
- Scaling: `kubectl scale deployment/product-service --replicas=4 -n ecommerce`.
- Rolling update/rollback: `kubectl set image deployment/product-service product-service=ghcr.io/OWNER/product-service:1.1.0 -n ecommerce`; `kubectl rollout status deployment/product-service -n ecommerce`; `kubectl rollout undo deployment/product-service -n ecommerce`. "Kubernetes performs the rollout; Helm later provides a higher-level release-management workflow."
- Ingress manifest (tutorial): `apiVersion: networking.k8s.io/v1`, `kind: Ingress`, `metadata.name: ecommerce-ingress`, namespace ecommerce; rule `host: api.example.local`, path `/products`, `pathType: Prefix`, backend service product-service port 8080.
- Complete raw YAML example (tutorial section 59): namespace.yaml + configmap.yaml + deployment.yaml (replicas 2, image `ghcr.io/OWNER/product-service:1.0.0`, containerPort 8080, `envFrom configMapRef`) + service.yaml (ClusterIP, 8080) — applied with `kubectl apply -f` each; verified with `kubectl get all -n ecommerce`, `get pods`, `describe pod`, `logs`, `get svc`, `get endpointslice`.
- In-cluster test: `kubectl run curl-test --image=curlimages/curl --rm -it -n ecommerce -- sh` then `curl http://product-service:8080/actuator/health`.
- Self-healing demo: `kubectl delete pod <pod> -n ecommerce` then `kubectl get pods -n ecommerce -w` — "The Deployment/ReplicaSet creates a replacement because the desired replica count is still two."
- No Helm chart or ArgoCD YAML is repeated in these two decks (S14 artifacts are assumed).

## 7. Configuration

- Actuator: both sub-health endpoints require `spring-boot-starter-actuator` AND the `livenessstate`/`readinessstate` flags; otherwise "probes will 404."
- Probe timing rules from the slides: liveness `initialDelaySeconds: 60` (Spring Boot needs time to start; dev-only 30), `periodSeconds: 10`, `failureThreshold: 3`; readiness `initialDelaySeconds: 30`, `periodSeconds: 5`, `failureThreshold: 3`. Tutorial: "Tune timings using real startup/health behavior; do not copy arbitrary production values."
- Probe placement rule: "never add DB or Redis checks to the liveness group — a DB outage should not restart the pod. DB checks belong in readiness."
- Service port convention: course examples use containerPort/port/targetPort 8081 for product-service; tutorial examples use 8080 (`server.port=8080`).
- Namespace creation and context: `kubectl create namespace ecommerce`; or via ArgoCD `syncOptions: - CreateNamespace=true`; `kubectl get all -n ecommerce`; `kubectl config set-context --current --namespace=ecommerce`.
- Secret dev/prod rule: dev = hardcoded base64 in YAML; prod = "Sealed Secrets / Vault / AWS Secrets Manager"; use `echo -n 'pw' | base64` (the `-n` flag avoids a trailing newline corrupting the decoded value). "Never commit real production secrets to Git."
- Local cluster setup: `minikube start --driver=docker`; `minikube status`; verify `kubectl get nodes`, `kubectl cluster-info`; kind alternative `kind create cluster --name microservices`; `kubectl config get-contexts / current-context / use-context` to manage contexts.
- Tutorial deployment commands: `kubectl create deployment hello --image=nginx:1.27 -n ecommerce`; `kubectl expose deployment hello --type=ClusterIP --port=80 -n ecommerce`; `kubectl port-forward service/hello 8080:80 -n ecommerce`; `minikube service hello -n ecommerce` — "Port-forward is a development/testing technique, not the normal production exposure model."
- No Spring `application.yml` beyond Actuator management keys and tutorial ConfigMap data values appears in these decks.

## 8. Failure scenarios

- "Running but not serving traffic": pod Running, endpoint Timeout/503, first 30 requests fail because traffic was sent before startup finished (JPA schemas, PostgreSQL, Eureka, cache warm-up).
- "Running but dead inside": 6-hour-old pod with blocked JVM threads still reports Running; customers get timeouts; pod never returns errors. Fixed by liveness probe.
- CrashLoopBackOff: pod keeps crashing; exponential backoff 10s/20s/40s before each restart; "indicates a config/startup error, not a liveness failure." Course fix: "Increase initialDelaySeconds -- Spring Boot + JPA needs 60-90s. Check kubectl logs --previous."
- Demo warning seen in `kubectl describe pod`: `Warning Unhealthy ... Readiness probe failed: HTTP 503` — disappears when Spring Boot finishes startup and readiness flips to Healthy; pod joins the Service endpoints.
- Course deck "5 Errors You Will See This Session":
  1. Pod stuck in CrashLoopBackOff -> increase initialDelaySeconds (Spring Boot + JPA needs 60–90s); check `kubectl logs --previous`.
  2. `/actuator/health/liveness` returns 404 -> need BOTH `spring-boot-starter-actuator` AND `management.health.livenessstate.enabled: true`.
  3. Secret values corrupted -> use `echo -n 'pw' | base64` (trailing newline corrupts decoded value).
  4. ReadinessProbe passes but no traffic -> check Service selector labels match Pod labels exactly — "one typo = zero endpoints."
  5. Running but ArgoCD shows Degraded -> "ArgoCD uses readiness for Health. Ensure readiness probe passes before sync completes."
- Tutorial common Pod problems (section 47): Pending (scheduling, resource, storage, or admission problem); CrashLoopBackOff (application starts then repeatedly crashes); ImagePullBackOff (image cannot be pulled); Running but not Ready (readiness probe/configuration problem); Service has no response (selector, ports, readiness, or application-listening-port problem); OOMKilled (container exceeded memory limit or has a memory problem).
- Tutorial debugging checklist (sections 46 and 71, same 8-step "golden sequence"): 1. `kubectl config current-context` (Which cluster?); 2. `kubectl get nodes` (Are nodes healthy?); 3. `kubectl get pods -n ecommerce` (What is the Pod state?); 4. `kubectl describe pod <pod> -n ecommerce` (Why?); 5. `kubectl logs <pod> -n ecommerce` (What does the app say?); 6. `kubectl get events -n ecommerce --sort-by=.lastTimestamp` (What do cluster events say?); 7. `kubectl get endpointslice -n ecommerce` (Is the Service selecting Pods?); 8. back to describe (Are Pods Ready?).
- Namespace trap: "kubectl commands default to the 'default' namespace — always specify -n ecommerce or set the context." (Beginner mistake list also includes "Inspecting the wrong namespace" and "Using the wrong kubectl context".)
- Tutorial common beginner mistakes (14, section 70): calling Pod IPs directly; mismatching Deployment selectors and Pod labels; confusing Service port and targetPort; using NodePort for every microservice; assuming ClusterIP is publicly reachable; creating Ingress without an Ingress Controller; putting passwords in ConfigMaps; committing real Secrets to Git; using `latest` everywhere; inspecting the wrong namespace; using the wrong kubectl context; assuming Running means Ready; treating a Pod as permanent; deleting everything instead of reading describe/logs/events.

## 9. Trade-offs

- Liveness vs readiness (course deck engineering decision): restart vs remove-from-LB; failure scenarios (deadlock/OOM/infinite loops/JVM freeze vs still starting/cache loading/DB migration); DB connectivity belongs to readiness only; the trap of configuring only one probe.
- Service type choice (course deck design choice): internal service-to-service -> ClusterIP (default, no external access); testing externally on dev cluster (minikube) -> NodePort (random port 30000–32767); production external access (cloud provider) -> LoadBalancer (cloud creates L4 load balancer); HTTP routing with host/path rules -> Ingress + ClusterIP ("beyond today's scope" in the course deck); database or internal cache (Redis/Kafka) -> "ClusterIP only -- never expose externally."
- Tutorial Which-Service-Type table: Internal microservice -> ClusterIP; Local simple external test -> NodePort or port-forward/`minikube service`; Cloud external endpoint -> LoadBalancer; HTTP routing for multiple Services -> Ingress/Gateway API + controller/implementation. "Do not expose every microservice publicly just because it has an HTTP endpoint." Course rule: "Product, Inventory, Order, Payment, etc. should normally use ClusterIP. The edge/API gateway should be the externally exposed entry point."
- ConfigMap vs Secret: non-sensitive/plain text/safe to commit vs sensitive/base64/never commit; "base64-encoded in etcd (NOT encrypted by default)"; the git-log embarrassment rule; prod requires external secrets management.
- Probes timing: `initialDelaySeconds` 60 for liveness vs 30 for readiness (course deck); the dev-only reduction note; tutorial warns against copying arbitrary production values.
- NodePort vs port-forward: NodePort exposes on every node's IP (dev only, never production); port-forward is "a development/testing technique, not the normal production exposure model."
- Ingress vs Gateway API: "Kubernetes currently recommends Gateway API for new development; Ingress remains stable but its API is frozen." Students should know Gateway API exists; Ingress remains important to understand.
- Namespace isolation: "soft multi-tenancy within a single cluster" (resource quotas, RBAC, network policies) but "not by itself a complete security boundary."
- Pod vs container: never run containers directly in K8s; declare Pods via Deployments; pods are ephemeral and disposable.
- Raw YAML before Helm (tutorial section 66): if students start with Helm, "the templates can look like magic" — the deliberate progression is raw YAML first, repeated YAML becomes obvious, then Helm.
- Kubernetes does not replace CI/GitOps/Maven; does not automatically provide middleware or security; `depends_on` has no direct Kubernetes equivalent (use readiness/health).

## 10. Common mistakes

- From the course deck "COMMON TRAP": "I only need one probe -- liveness is enough." Correct: configure BOTH; missing readiness = premature traffic.
- Adding DB/Redis checks to the liveness group (course deck rule: DB checks belong in readiness).
- Forgetting that probes 404 without BOTH the actuator starter and the enabled livenessstate/readinessstate flags.
- Corrupting Secret values with a trailing newline (`echo -n` fix).
- Service selector/pod label typos ("one typo = zero endpoints").
- Diagnosing ArgoCD Degraded without checking readiness (ArgoCD uses readiness for Health).
- The 14 beginner mistakes from the tutorial (section 70) — including: assuming Running means Ready; treating a Pod as permanent; creating Ingress without an Ingress Controller; putting passwords in ConfigMaps; committing real Secrets to Git; using `latest` everywhere; using NodePort for every microservice; assuming ClusterIP is publicly reachable; deleting everything instead of reading describe/logs/events.
- From the instructor notes (section 76): beginning with Helm instead of raw YAML; exposing every microservice; forgetting the Ingress Controller requirement.

## 11. Interview questions

The slides contain no labeled interview/exam section. However, the tutorial includes a Quick Quiz (19 Q&A, section 72) and a readiness checklist (section 73); the questions below are derived strictly from the session content:
- What is Kubernetes, and why is Docker alone not enough for a production microservices cluster? (Quiz Q1, Q2)
- What is a Pod? Why not use Pod IPs as stable addresses? (Quiz Q3, Q4)
- What does a Deployment manage? What is a Service? (Quiz Q5, Q6)
- Which Service type is normally used for internal microservices? What is targetPort? (Quiz Q7, Q8)
- What is a ConfigMap? What is a Secret? Does Secret automatically mean the data is completely secure? (Quiz Q9–Q11)
- What is readiness? What is liveness? (Quiz Q12, Q13)
- What is Ingress? What is the modern direction for new Kubernetes traffic management? (Quiz Q14, Q15)
- What is kubectl? What is Minikube? What is kind? (Quiz Q16–Q18)
- Why learn raw YAML before Helm? (Quiz Q19)
- Explain the difference between a liveness and readiness probe and when each should fail.
- Why must a DB connectivity check NOT be part of liveness?
- Walk through the pod lifecycle from Pending to Terminating; where do probes gate it?
- What causes CrashLoopBackOff and what does the exponential backoff sequence look like?
- Why is "Running" not the same as "Ready"?
- How does a Service find its Pods? Why is the label selector "the single most important line in a Service manifest"?
- When should you use ClusterIP vs NodePort vs LoadBalancer, and why is NodePort dev-only?
- Why are secrets base64-encoded in etcd, and why is that not encryption?
- What is the troubleshooting "golden sequence" (context -> nodes -> pods -> describe -> logs -> events -> endpointslice)?
- What is the difference between Ingress and Spring Cloud Gateway?

## 12. What I must memorize

- Both probe definitions and their exact endpoints: liveness = "Is this pod still alive?" -> `/actuator/health/liveness` -> RESTART on failure; readiness = "Is this pod ready to accept traffic?" -> `/actuator/health/readiness` -> REMOVE from load balancer on failure. Configure BOTH.
- Course probe settings: liveness `initialDelaySeconds: 60`, `periodSeconds: 10`, `failureThreshold: 3`; readiness `initialDelaySeconds: 30`, `periodSeconds: 5`, `failureThreshold: 3` (port 8081 in the course deck; 8080 in the tutorial).
- Actuator requirement sentence: "Both endpoints require spring-boot-starter-actuator in pom.xml AND the livenessstate/readinessstate flags enabled. Without both, the sub-health endpoints do not exist -- probes will 404."
- The liveness/readiness DB rule: DB checks belong in readiness; never in liveness.
- Pod lifecycle order and details: Pending (image pulling, waiting for resources) -> Running (JVM starting, Eureka registering, DB pool) -> Ready (readiness passes, joins LB) -> Terminating (SIGTERM, grace period 30s default, SIGKILL if needed).
- CrashLoopBackOff backoff sequence 10s, 20s, 40s; meaning: config/startup error, not a liveness failure.
- Service type selection: ClusterIP (default/internal), NodePort (30000–32767, dev only), LoadBalancer (cloud L4, production), ExternalName (DNS alias), Ingress (host/path routing + Ingress Controller). Databases/caches: ClusterIP only.
- ConfigMap vs Secret: non-sensitive/plain text/safe to commit vs sensitive/base64 in etcd/NOT encrypted/never commit; Secret example `DB_PASSWORD: cG9zdGdyZXNwYXNzd29yZA==` = base64('postgrespassword'); reference via `secretKeyRef`; fix `echo -n 'pw' | base64`.
- Namespaces: ecommerce-dev / ecommerce / ecommerce-prod; soft multi-tenancy; not a complete security boundary; kubectl defaults to `default` namespace.
- Manifest anatomy: apiVersion, kind, metadata, spec (+ system-maintained status).
- The troubleshooting golden sequence (8 steps).
- "Kubernetes has no idea our app is healthy unless we tell it how to ask."

## 13. What I must understand

- Why Kubernetes needs an application health signal at all, and what breaks without each probe.
- Why "Running" is a container-process fact, not a traffic-readiness fact.
- Why liveness restarts are dangerous for dependency checks (a DB outage must not restart every pod) and why readiness is the correct gate for dependencies.
- How the Service selector -> endpoints/endpointslice mechanism works and why one label typo yields zero endpoints.
- Why ClusterIP is the default for internal microservices and why the edge gateway is the only externally exposed entry point.
- Why base64 is encoding, not encryption, and what production secret management requires.
- The desired-state/declarative model and its role as the foundation of GitOps (Session 14) — "This concept becomes the foundation of GitOps."
- Control plane vs worker node responsibilities (desired state management vs workload execution).
- The distinction between Ingress (API object) and Ingress Controller (implementation), and Gateway API as the modern direction.
- Why raw YAML must be learned before Helm ("templates can look like magic").
- The Docker Compose -> Kubernetes mapping, including that `depends_on` has no direct equivalent (use readiness/health).

## 14. What I should implement from memory

- Enable Actuator sub-endpoints in application.yml (livenessstate + readinessstate) and verify both endpoints return HTTP 200.
- Add livenessProbe + readinessProbe to the product-service Deployment with correct paths/delays/thresholds, and verify with `kubectl describe pod` (Liveness and Readiness defined) and that the `Warning Unhealthy` event disappears after startup.
- Create the `product-secrets` Secret (type Opaque, DB_PASSWORD) and wire it into the Deployment via `secretKeyRef` (replacing plaintext ConfigMap usage).
- Create/select the namespace (ecommerce) and set the kubectl context namespace.
- Create a ClusterIP Service and test from inside the cluster (`kubectl run curl-test --image=curlimages/curl ...`; `curl http://product-service:8080/actuator/health`).
- Run the Beginner Lab end-to-end: install kubectl + Minikube, `minikube start --driver=docker`, verify node status, create ecommerce namespace, create NGINX Deployment, scale to 3, create ClusterIP Service, access via port-forward, delete a Pod and observe self-healing, update image and observe rolling update, repeat with Product Service, add a ConfigMap, add a development-only Secret, inspect logs/describe/events, and explain every YAML field before moving to Helm.
- Perform the troubleshooting golden sequence when something fails.
- Commit convention (course deck Lab 12A): `session-15: add-probes-and-secret-product-service`.

## 15. Relationship to previous sessions

- S14 (both decks): "S14 introduced K8s manifests as a light intro for ArgoCD context. S15 goes deeper: probes, service types, Secrets, and namespaces make the deployment production-ready." S14's scope boundary explicitly deferred Ingress, RBAC, Secrets (to S15) and HPA, StatefulSets/PVs (to S16).
- S14's common issue "ArgoCD shows Unknown health status -> Configure readiness/liveness probes -- covered fully in Session 15" is resolved in this session.
- S13/S14 pipeline context: product-service already GitOps-deployed with canary (S14); S15 updates its manifests (deployment.yaml probes, secret.yaml) and commits `session-15: add-probes-and-secret-product-service`, with "ArgoCD synced with production-ready config."
- Phase 2 roadmap (course deck): S9 Docker, S10 Unit+Int Tests, S11 Contract+Chaos, S12 Saga Orch., S13 CI/CD, S14 GitOps, S15 K8s Core, S16 K8s Adv.
- The tutorial's own recap: "Session 14 introduced GitOps and Argo CD and therefore introduced Kubernetes as the deployment target" — and "The existing Session 15 material assumes students already understand Deployments, Services" (this tutorial fills that gap).
- Docker background (S9): Docker image = packaged artifact; container = running instance; the tutorial maps Docker/Compose concepts to Kubernetes equivalents (section 67).

## 16. Relationship to future sessions

- Course deck: "Next: Session 16 -- Kubernetes Advanced: HPA • Resource Limits • Helm Charts • RBAC • Phase 2 Retrospective" — Monday 3:00–5:30 PM, Online — Phase 2 Final Session.
- Carried forward into S16: probes (readiness gates traffic for new pods created by HPA), Secret pattern, namespaces, resources (requests/limits), ServiceClusterIP assumption, ArgoCD sync.
- Course deck BONUS (Lab 12A): "Add startupProbe (failureThreshold: 30) for slow startup + order-service probes (same pattern)" — expands the pattern to more services.
- Tutorial: "How This Leads Into Session 15" — repeating Deployment/Service/ConfigMap/Ingress/HPA YAML for product-service, inventory-service, order-service, payment-service across environments becomes difficult; "Session 15 solves this with Helm: charts, values, templates, releases, environment-specific configuration, and Helm integration with Argo CD." (Recorded as stated; the course deck resolves this into S16 for Helm.)
- Tutorial: "I know what Ingress and an Ingress Controller are. I know Gateway API is the modern direction" are readiness items before the Helm session; HPA is listed as an awareness topic here and becomes the S16 focus.
- Cloud path (tutorial section 57): after learning locally, the same concepts apply to EKS/AKS/GKE; managed Kubernetes reduces control-plane operations but "workload, networking, security, scaling, storage, and application operations still require management."

## 17. Lab relationship

Course deck — "LAB 12A — Production-Ready product-service in Kubernetes": "25 min in-session + homework • Builds on S14 manifests • Grading: Feature 70% + Tests 20% + Quality 10%". Steps (verbatim):
1. "Update Spring Boot Actuator Config — Enable livenessstate + readinessstate in application.yml (3 min)"
2. "Add Probes to Deployment YAML — livenessProbe + readinessProbe with correct delays (8 min)"
3. "Create Secret + Reference It — product-secrets Secret, wire via secretKeyRef (10 min)"
4. "Verify and Commit — kubectl describe pod, test endpoints, git push (4 min)"

Acceptance Criteria (verbatim): "/actuator/health/liveness and /actuator/health/readiness return HTTP 200"; "Deployment YAML has both livenessProbe and readinessProbe configured"; "Secret 'product-secrets' exists in namespace ecommerce"; "Deployment references DB_PASSWORD from secretKeyRef (not ConfigMap)"; "kubectl describe pod shows probe status: Liveness and Readiness defined"; "ArgoCD Application status: Synced + Healthy after probe addition"; "Commit: session-15: add-probes-and-secret-product-service". BONUS: "Add startupProbe (failureThreshold: 30) for slow startup + order-service probes (same pattern)".

Course deck project progress ("Platform Updates"): "k8s/product-service/deployment.yaml -- probes added"; "k8s/product-service/secret.yaml -- new (DEV base64)"; "application.yml -- livenessstate + readinessstate enabled"; "ArgoCD synced with production-ready config."

Course deck wrap-up: "SESSION 15 COMPLETE — Production-Ready K8s Deployment. Next: Session 16 -- Kubernetes Advanced: HPA • Resource Limits • Helm Charts • RBAC • Phase 2 Retrospective." (No "Daily Quiz" or DoD block appears on the S15 course-deck closing slides; only Lab 12A grading, acceptance criteria, and commit convention above.)

Tutorial deck — "Beginner Lab -- Kubernetes From Zero" (15 steps, verbatim list):
1. "Install kubectl and Minikube." 2. "Start Minikube with Docker driver." 3. "Verify node status." 4. "Create ecommerce namespace." 5. "Create an NGINX Deployment." 6. "Scale it to three replicas." 7. "Create a ClusterIP Service." 8. "Access it with kubectl port-forward." 9. "Delete a Pod and observe self-healing." 10. "Update the image and observe a rolling update." 11. "Repeat the exercise with Product Service." 12. "Add a ConfigMap." 13. "Add a development-only Secret." 14. "Inspect logs, describe output, and events." 15. "Explain every YAML field before moving to Helm."

Tutorial also includes a 19-question Quick Quiz (section 72), a Student Readiness Checklist before Session 15 (section 73, 22 items), and Instructor Notes (section 76) — e.g. "Delete a Pod and show self-healing"; "Scale manually before introducing HPA later"; "Show a rolling update before Helm upgrades"; "End by showing the repeated YAML that Session 15 will package with Helm." Neither deck's S15 content mentions a Daily Quiz/homework beyond Lab 12A's "homework" grading note.

Note the lab naming difference between the decks (Lab 12A vs Beginner Lab) — both are recorded above exactly as the slides present them.
