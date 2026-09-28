# Session 0 — Program Kickoff (Course Orientation)

Source files: 00-Course-Kickoff.pdf (13 pages, read in full)

## 1. Why this topic exists

The kickoff deck frames the industry context: Netflix deploys to production "100s of times per day", Amazon "deploys a new version every 11.7 seconds", and Uber "runs 2,000+ microservices in production". The slide's stated conclusion: "The ability to deploy independently, scale selectively, and own bounded domains is now a baseline expectation in any serious engineering organisation." The course "trains you to design, build, and operate systems the way industry leaders do."

The deck lists the concrete problems this course equips you to solve (Problem -> Solution):

| Problem | Solution |
|---|---|
| A deploy in one module breaks the entire system | Independent deployable services |
| One slow service exhausts all threads | Resilience4j: CB + Bulkhead + TimeLimiter |
| Payment fails midway — order is stuck in limbo | Saga Pattern + Compensation |
| 8 services use 8 different configs | Spring Cloud Config Server |
| Order can't find Inventory's address | Eureka Service Discovery |
| 1000 requests/min collapse the database | Redis Caching + Cache-Aside |

## 2. Core concepts

- Program size: "29 Sessions — 80 Hours — 4 Phases".
- Phase 1 "Foundation & Core Patterns", Sessions 1–8, 20h: Config + Eureka; API Gateway + Security; Resilience4j Stack; OpenFeign + Saga + Kafka; Redis Caching.
- Phase 2 "Quality & Deployment", Sessions 9–16, 20h: Docker + Compose; Integration Testing; Kubernetes; CI/CD Pipelines; GitOps + ArgoCD.
- Phase 3 "Advanced & Enterprise", Sessions 17–24, 20h: Observability Stack; CQRS + Event Sourcing; Keycloak + OAuth2; Service Mesh (Istio); HashiCorp Vault.
- Phase 4 "Capstone Project", Sessions 25–29, 20h: Team Build Day; Production Deploy; Security Audit; Load Testing; Final Presentation.
- Delivery format: "4 Offline Anchor Days (5h each) — Sessions 1, 9, 17, 25" and "25 Online Sessions (2.5h each) — Mon/Wed 3:00-5:30 PM".
- Continuous Capstone: "You Build ONE Real Platform — Session 1 to Session 29": the Enterprise E-Commerce Platform — "Not a toy example. Not isolated exercises. One growing system — every session adds a real capability." Three promises: every session has purpose ("Your lab isn't a practice file — it's part of a real product you're building"); architecture decisions persist ("A bad design in Session 3 costs you in Session 7 — just like real engineering"); ready for production ("By Session 29, what you built can actually run in a real cloud environment").
- The same 7-step session loop repeats for all 29 sessions:
  1. Pre-Reading — 15 min before each session. "Targeted material — not optional."
  2. Knowledge Check — 3 questions on the pre-reading, "called by name at session start".
  3. Concept + Problem — "The problem is introduced first. Always. Then the solution."
  4. Live Coding — trainer codes live; you follow and type along; "Real code, real mistakes."
  5. Lab — "You implement independently. 35 minutes of focused building."
  6. Quiz — 8 questions, 10 minutes, immediate feedback.
  7. Checkpoint Commit — "Commit and push your work. No commit = no grade for that lab."
- Assessment model (four components): Daily Quizzes 10% (8 questions, end of every session, 10 minutes, immediate feedback); Lab Grades 40% (Feature 70% + Unit Tests 20% + Code Quality 10%, one lab per session); Mid-Course Exam 15% (Session 9, 2 hours, practical coding, individual, covers Sessions 1–8, supervised at the Offline Anchor Day); Capstone Project 35% (Team 70% + Individual Contribution 30%).
- Grading bands: Distinction 90-100%; Pass with Merit 75-89%; Pass 60-74%; Retake Required < 60%.
- Working agreement (what is expected from the trainee): pre-reading every session (15 min is enough — but it must be done); labs completed between sessions ("Don't wait for the next session to finish"); checkpoint commit pushed ("No commit = no grade, no exceptions"); unit tests with every lab ("Tests are not optional — 20% of your grade"); pre-reading before Knowledge Check ("You will be called on by name, every session").
- What the trainee receives: Full Session Packs (instructor guide + code + labs for every session); Reference branch (instructor implementation to compare against); Architecture Clinics ("Two full reviews (Sessions 8 & 24) of your design decisions"); Assessment Bank ("64 exam questions with explanations — all mapped to traps"); production-grade patterns.
- Anchor-day agenda: deep-dive theory + whiteboard; extended live coding (no rush); full supervised lab (90 min); architecture discussion + quiz.
- Online-session agenda: knowledge check on pre-reading; concept + live coding (60 min); lab work — independent (35 min); quiz + checkpoint commit.

## 3. Architecture

Platform architecture slide (ports and introduction sessions, exactly as printed):

- API Gateway :8080
- Product :8081 (introduced S1), Order :8082 (S4), Payment :8083 (S4), Inventory :8084 (S6), Notification :8085 (S7)
- Infrastructure "running from Day 1, introduced when needed": Eureka (S1) :8761; Config Server (S1) :8888; PostgreSQL (S1) :5432; Kafka (S7) :9092; Redis (S8) :6379; Zipkin (Later) :9411.
- Repository: `microservices-pro-platform`, "Branch: main (your work) + reference (instructor implementation)".

## 4. Technologies

Named in the deck (no versions stated in this deck): Spring Boot, Spring Cloud, Spring Cloud Config Server, Eureka, Resilience4j (CB + Bulkhead + TimeLimiter), OpenFeign, Saga Pattern, Kafka, Redis (Caching + Cache-Aside), PostgreSQL, API Gateway, JWT, Docker + Compose, Kubernetes, CI/CD, GitOps + ArgoCD, Observability stack, CQRS + Event Sourcing, Keycloak + OAuth2, Istio service mesh, HashiCorp Vault, Zipkin.

Exact versions: UNKNOWN — REQUIRES SOURCE REVIEW (this deck states no versions; version facts appear later, e.g. the Session 2 Continued deck states Java 21, Spring Boot 3.3.x, Spring Cloud 2023.x for the gateway project).

## 5. Important terminology

- Offline Anchor Day — 4 sessions (1, 9, 17, 25), Wednesday 10:00 AM – 3:00 PM, 5 hours.
- Online Live Session — 25 sessions, Monday & Wednesday 3:00–5:30 PM, 2.5 hours.
- Knowledge Check — 3 questions on pre-reading, called by name at session start.
- Pre-Reading — 15 min before each session, "not optional".
- Checkpoint Commit — commit and push your work; "No commit = no grade for that lab."
- Continuous Capstone — one evolving Enterprise E-Commerce Platform across all 29 sessions.
- Reference branch — instructor's canonical implementation to compare against when stuck.
- Architecture Clinic — two full reviews of design decisions at Sessions 8 & 24.
- Assessment Bank — 64 exam questions with explanations, "all mapped to traps".

## 6. Code concepts

UNKNOWN — REQUIRES SOURCE REVIEW (the kickoff deck contains no code; the first code appears in the Session 1 deck: Eureka Server, Config Server, Product Service).

## 7. Configuration

The deck does not show configuration files. Repo/branch conventions it does give:

- Working repo: `microservices-pro-platform`, branch `main` = "your work"; branch `reference` = "instructor implementation".
- (Session 1 deck adds that instructor materials live in a separate repo `microservices-pro-course` — "Not for trainee use — session packs, rubrics, slides".)

## 8. Failure scenarios

The six Problem -> Solution pairs in section 1 are the deck's failure scenarios (deploy blast radius, thread exhaustion by one slow service, mid-flow payment failure/limbo state, config drift across 8 services, service discovery failure, DB collapse under 1000 requests/min).

## 9. Trade-offs

The deck's only explicit trade-off table is "Traditional Training vs Continuous Capstone":

| Traditional Training | Continuous Capstone (This Course) |
|---|---|
| New exercise every session — discarded after | One evolving platform — every lab builds on the last |
| Lab 3 has no relation to Lab 7 | A design choice in Session 3 affects Session 7 — by design |
| "I built a circuit breaker demo" | "I added resilience to our Order Service" |
| Capstone starts from scratch in the final sessions | Capstone = completion of what you already built |
| Low motivation — throwaway work | High motivation — real product, real decisions |

## 10. Common mistakes

The working agreement implies the mistakes the course penalises: skipping pre-reading; leaving labs unfinished until the next session; not pushing a checkpoint commit ("No commit = no grade, no exceptions"); omitting unit tests ("Tests are not optional — 20% of your grade"). The deck also warns that architecture decisions persist: "A bad design in Session 3 costs you in Session 7".

## 11. Interview questions

UNKNOWN — REQUIRES SOURCE REVIEW (the kickoff deck lists no interview questions; it only defines the quiz/exam format: daily quiz = 8 questions, mid-course exam covers Sessions 1–8).

## 12. What I must memorize

- 29 sessions / 80 hours / 4 phases; phase session ranges (1–8, 9–16, 17–24, 25–29) and each phase's technologies.
- 4 Offline Anchor Days = Sessions 1, 9, 17, 25 (5h each); 25 Online Sessions (2.5h, Mon/Wed 3:00–5:30 PM).
- The 7-step session loop in order: Pre-Reading -> Knowledge Check -> Concept+Problem -> Live Coding -> Lab -> Quiz -> Checkpoint Commit.
- Assessment weights: Quizzes 10%, Labs 40% (Feature 70 / Unit Tests 20 / Code Quality 10), Mid-Course Exam 15% (Session 9, covers 1–8), Capstone 35% (Team 70 / Individual 30).
- Grade bands: Distinction 90–100, Merit 75–89, Pass 60–74, Retake < 60.
- Port map: Gateway 8080, Product 8081, Order 8082, Payment 8083, Inventory 8084, Notification 8085; Eureka 8761, Config 8888, PostgreSQL 5432, Kafka 9092, Redis 6379, Zipkin 9411.
- The six problem/solution pairs (CB, Saga, Config Server, Eureka, Redis cache-aside, independent deployable services).

## 13. What I must understand

- Why the course is one continuous capstone instead of isolated exercises (design decisions persist; the capstone is the completion of what you already built).
- Why every session starts with the problem before the solution.
- Why "no commit = no grade" and why unit tests are weighted 20% of the lab grade.
- The role of pre-reading + knowledge check as the entry ticket to each session.

## 14. What I should implement from memory

UNKNOWN — REQUIRES SOURCE REVIEW (the kickoff prescribes no coding task; the first implementation task is Lab 1 in Session 1: Eureka Server, Config Server, Product Service with unit tests).

## 15. Relationship to previous sessions

None — this is the program opening. It orients and precedes Session 1 ("Kickoff Complete — Let's Start Session 1: Architecture & Spring Cloud · Service Discovery · Centralized Configuration").

## 16. Relationship to future sessions

The deck defines the whole arc: Phase 1 foundation (S1–8), Phase 2 quality & deployment (S9–16), Phase 3 advanced & enterprise (S17–24), Phase 4 capstone (S25–29). The platform port map states which session introduces each service/infrastructure piece (S1 Eureka/Config/Product, S4 Order/Payment, S6 Inventory, S7 Notification/Kafka, S8 Redis, Zipkin later).

## 17. Lab relationship

Exact terms used by the deck: anchor days include a "Full supervised lab (90 min)"; online sessions include "Lab work — independent (35 min)"; the loop step is "Checkpoint Commit — Commit and push your work. No commit = no grade for that lab." Lab grading is "Feature (70%) + Unit Tests (20%) + Code Quality (10%) · one lab per session". Homework policy: pre-reading of "15 min before each session. Targeted material — not optional", labs completed between sessions, unit tests with every lab. Trainee keeps a "reference branch — Instructor implementation you can compare against". No specific lab name is given for Session 0; the first named lab is "Lab 1" in the Session 1 deck.
