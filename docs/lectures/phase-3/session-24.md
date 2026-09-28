# Session 24 — Architecture Clinic #2 + Phase 3 Wrap-Up (Reviewing Every Decision Since Session 1 • Phase 3 Complete • Phase 4 Capstone Preview)

Source files: `Session_24_Architecture_Clinic2.pdf` (24-page instructor deck), `Session_24_Architecture_Clinic_2_Phase_3.pdf` (11-page student tutorial). File check: the two PDFs differ in size and packaging — the deck is the instructor presentation (ITSharks, Monday 3:00–5:30 PM, 2.5 hours, Phase 3 Final Session), the tutorial is the student working document ("Use this document during the Architecture Clinic, group discussion, retrospective, and Capstone hand-off"). Both were read; the tutorial adds the rules, worksheets, templates and checklists noted below.

This is a clinIC session, not a coding session: "Today we do not add a new feature. We ask, with 23 sessions of real context behind us: were our decisions right, and would we make them again?"

## 1. Why this topic exists

- **The transition point:** Session 8 held the first Architecture Clinic, after 8 sessions. Today, after 24 sessions — Observability, CQRS, real Identity, a Service Mesh, closed technical debt, and verified resilience under real load — the clinic repeats at a very different scale of maturity.
- **The standard:** "It works, so it's fine" is not acceptable. "It works, but here is the specific trade-off we accepted, and here is what would make us reconsider it" is what we are after.
- **Be the Harsh Critic — raised stakes:** "Imagine a new senior engineer joins the team today, reads the entire codebase and every session pack, and is asked to write an honest architecture review memo before their first week ends." A lazy answer: "We added Istio because service meshes are industry standard." A good answer: "We added Istio to eliminate cross-cutting duplication, but for our platform's size, the mesh's operational cost may exceed its benefit — a real team our size might reasonably have waited."
- **Core skill (tutorial):** Think like a senior engineer — do not stop at "It works"; stronger: "It works for this workload and requirement, we accepted these costs, and we would reconsider the decision if these conditions changed."
- The central question is not "Which technology is best?" but "For this problem, at this scale, with these constraints, what trade-off are we intentionally accepting?"
- **Pattern-vs-Need:** every Phase 3 addition (CQRS, Mesh, Outbox) was introduced with an explicit justifying problem — this is the standard for EVERY future architectural choice, including the Capstone. Honest trade-offs, not fairy tales (Instructor Pack P6).
- One-line recap of Phase 3 (deck): S17 Observability — enough cross-service complexity finally existed; S18 CQRS split on product-service — a concrete, described read/write conflict existed; S19 Keycloak Identity Provider — answered the question Session 3 explicitly deferred; S20 Client Credentials + Resource Server — closed the loop, JwtAuthFilter formally retired; S21 Istio: mTLS, weighted traffic, mesh resilience — named, cross-cutting duplication across services; S22 Outbox, Idempotency Keys, API Versioning — directly closed 3 named debt items; S23 k6 load/stress testing, resilience verified — turned config into a tested, observed result.

## 2. Core concepts

- **The Simple Decision Model (tutorial table):** 1. Problem — What concrete problem or requirement are we solving? 2. Context — What scale, workload, team, constraints, and existing architecture matter? 3. Options — What realistic alternatives existed? 4. Trade-off — What did we gain, and what complexity or cost did we introduce? 5. Evidence — What tests, observations, failures, metrics, or code support the decision? 6. Reconsideration — What future condition would make us change the decision?
- **Architecture Clinic Rules (tutorial, 9):** (1) Do not defend a decision merely because it was taught or because it is common in industry. (2) Do not reject a technology merely because it adds complexity. (3) State the problem before defending the solution. (4) Name at least one benefit and one cost for important architectural decisions. (5) Use evidence where possible: test results, load-test observations, logs, traces, code complexity, operational steps, or failure behavior. (6) Distinguish valuable to learn from necessary to deploy. (7) If you propose changing a decision, explain what would replace it and what new risks the replacement creates. (8) If you would keep a decision, explain what evidence justifies keeping it. (9) Do not claim that all technical debt is gone.
- **The five Architecture Questions** (see §3 for exact content — each deck slide has Expected Discussion + Red Flag Answer; tutorial adds Discuss/Avoid/Evidence prompts).
- **Growth in judgement debrief:** compare the SHAPE of today's answers to Session 8's Clinic #1 notes. Instructor Pack's Layer 3 (Judgement) explicitly predicted richer answers here. Session 8: "It works, so it's fine" answers common; trade-offs named less specifically. Session 24: "This was probably premature" willingly said; richer trade-off language, real costs named.
- **Technical Debt definition (tutorial):** not simply bad code — a known limitation, shortcut, missing capability, or architectural compromise that may create future cost or risk. Register v2's purpose: make those decisions visible to the Capstone team.
- **Technical Debt Register v2** with three categories: Resolved (to verify), Still Open (carried into Phase 4), Newly Surfaced (populated live from class discussion).
- **ADR mini-template:** capture an important decision as a short record so the reasoning is reusable during the Capstone.
- **Individual reflection:** three questions from Session 23's homework, shared aloud during Part 4 of today's session.
- **Phase 3 complete:** 8 sessions, 20 hours, enterprise-grade capabilities.
- **Takeaway (tutorial):** "Architecture is not a collection of technologies. Architecture is a set of decisions, trade-offs, evidence, and consequences."

## 3. Architecture

This section records the clinic's discussion topics and decision criteria (per the task instruction, the clinic content belongs in §3/§8/§17). The deck gives, per question, an EXPECTED DISCUSSION and a RED FLAG ANSWER; the tutorial gives Discuss / Avoid / Useful evidence per question. Groups work in small groups, approximately eight minutes per question, rotating the facilitator so every participant practices architectural reasoning.

- **Question 1 — Did Session 18's CQRS split earn its complexity?** Expected discussion (deck): justified given the DESCRIBED dashboard-vs-checkout conflict, but honestly marginal for a training platform without real production read/write load. A real production team should re-verify the pain still exists before copying this pattern elsewhere. Red flag: "CQRS should be applied everywhere for good architecture" — no scale/pain justification. Tutorial: discuss whether the described dashboard-versus-checkout conflict justified the additional model and flow; avoid answering "CQRS is good"/"CQRS is over-engineering" — explain the actual problem, scale, benefit, cost; evidence to seek: read/write paths, model separation, query behavior, complexity added to code and operations.
- **Question 2 — Was Session 21's Service Mesh (Istio) the right call?** Expected discussion: powerful pattern, honestly named trade-off in the session itself — real operational cost (sidecar per pod, control plane, learning curve) for a small, single-language platform. Strong answer: valuable to LEARN, debatable to actually NEED here. Red flag: "Istio is industry standard so every platform should use it" — no cost/benefit weighing. Tutorial: separate the value of learning service-mesh concepts from whether this particular platform requires a mesh; evidence to seek: number of services, operational overhead, configuration complexity, mTLS/traffic-management needs, resilience duplication.
- **Question 3 — Clean cutover or parallel run for retiring JwtAuthFilter (Sessions 19–20)?** Expected discussion: correct as taught for a fully-controlled training environment; a real production system with live traffic and external consumers would need to weigh the parallel-run alternative (Session 20's own Engineering Decision) much more seriously. Red flag: "There was only one right way to do this" — ignores the session's own stated trade-off. Tutorial: for a controlled training environment a clean cutover may be reasonable; for a live system with external consumers, migration and compatibility concerns could change the decision; evidence to seek: token issuer, audience/claims, gateway behavior, service-to-service flow, client migration requirements.
- **Question 4 — Which original S8/S12 debt items were NOT addressed?** Expected discussion: open discussion — expect answers referencing in-memory SagaState (S12), dead-letter queue handling maturity, or database migration tooling (Flyway/Liquibase, named since S8 and never implemented). Good answer names a SPECIFIC remaining item and argues its priority. Red flag: "All our technical debt is resolved now" — no engineer's platform is ever fully debt-free. Tutorial: compare the earlier Technical Debt Register with the work completed by Session 22; candidate areas: persistent Saga state, database migrations, dead-letter replay/alerting, older hardcoded route/config patterns.
- **Question 5 — The ONE decision from Sessions 1–16 you'd make differently?** Expected discussion: open discussion. Strong answers reference something concrete — e.g., introducing structured logging (S17) from Session 1 instead of Session 17, or considering CQRS/Outbox needs earlier given how naturally S7's Saga led to S22's Outbox gap. Red flag: "I wouldn't change anything" — no engineer ever, especially not with 23 sessions of hindsight. Tutorial: imagine rebuilding the platform today with all knowledge through Session 23; a strong answer identifies a concrete change, explains the original trade-off, and describes the cost/risk of changing it; possible discussion areas: when observability should begin, how resilience and messaging decisions evolved, when reliability patterns become necessary.
- **Strong answer structure (tutorial, 8 parts):** Decision ("We chose X for Y.") → Problem → Benefit → Cost → Evidence → Alternative → Reconsideration → Conclusion ("Given the current context, we would keep/change/defer it because…"). Example of reasoning: instead of "Istio is industry standard", a stronger answer discusses the cross-cutting problem it solves, the operational overhead it introduces, the scale of the platform, and the conditions under which the team would or would not adopt it.
- **Technical Debt Register v2 content (the "architecture artifact" produced today):** see §8 for the exact item lists.
- **Phase 4 Capstone Preview — the hand-off structure:** what is inherited as-is vs what remains open to team judgement (see §16).
- **Deck-level architecture narrative:** everything reviewed today becomes the foundation the Capstone builds on — or deliberately rebuilds — starting Session 25.

## 4. Technologies

Named in this session's slides (review context — no new tools introduced today):

- **CQRS** (Session 18) — read/write separation on product-service; event-driven cache eviction.
- **Istio / Service Mesh** (Session 21) — mTLS, weighted traffic, mesh-level resilience; sidecar per pod, control plane, learning curve as costs.
- **Keycloak + OAuth2/OIDC** (Sessions 19–20) — Identity Provider; Client Credentials; Gateway as OAuth2 Resource Server; hand-rolled JWT validation (`JwtAuthFilter`) retired.
- **Zipkin, Prometheus/Grafana, structured logs** (Session 17) — named in the Phase 3 recap table as the Observability additions.
- **Transactional Outbox, Idempotency Keys, API Versioning** (Session 22) — closed named debt items.
- **k6** (Session 23) — load/stress testing, bottleneck/resilience analysis.
- **Resilience4j stack** (Sessions 4–5) — inherited foundation.
- **OpenFeign** (Session 6) — inherited communication.
- **Choreography Saga** (Session 7) — inherited; S7 Saga → S22 Outbox gap referenced in Q5.
- **Docker, Kubernetes, CI/CD, GitOps** (Sessions 9–16) — inherited.
- **Config Server / Eureka / Gateway** (Sessions 1–3) — inherited foundations.
- **Flyway/Liquibase** — named as never-implemented migration tooling (open debt).
- No version numbers are stated in either S24 PDF.

## 5. Important terminology

- Architecture Clinic — structured review of accumulated decisions (Clinic #1 = Session 8; Clinic #2 = Session 24).
- Pattern-vs-Need — the standard: every addition must be justified by an explicit problem.
- Trade-off statement — "It works, but here is the specific trade-off we accepted, and here is what would make us reconsider it."
- Red flag answer — the kind of unjustified answer the clinic is designed to expose (e.g., "industry standard", "wouldn't change anything", "all debt resolved").
- Expected discussion — the instructor's calibration of a strong answer per question.
- Technical Debt Register v2 — Resolved / Still Open / Newly Surfaced items, with priorities.
- Debt prioritization factors (tutorial, 6): Impact (what happens if left unresolved?), Likelihood (how likely to occur?), Scope (one service or whole platform?), Cost of delay (will fixing later become substantially harder?), Capstone dependency (will new features depend on this area?), Learning value (does resolving it demonstrate an important engineering capability?).
- ADR (Architecture Decision Record) mini-template fields: Title; Status (Accepted / Reconsider / Deferred); Context; Decision; Alternatives; Benefits; Costs / risks; Evidence; Reconsider when.
- Inherited vs owned decisions — inherited does not mean untouchable; the team starts from an established baseline; any change must be justified by a concrete requirement, problem, evidence, or risk.
- Core Scope vs Advanced Scope — Instructor Pack Section 3.5; reviewed before Session 25.
- Offline Anchor Day #4 — Session 25 Capstone Build Day, Wednesday 10:00 AM, 5 hours.
- Phase 3 Checkpoint — the pre-Session 25 readiness list.
- Student Technical Debt Register — TD-01..TD-06 worksheet (ID / Debt or limitation / Evidence / Impact / Priority / Proposed action & owner).
- Capstone Handoff Summary (Appendix B) — areas to mark Keep / Change / Defer with reasons.

## 6. Code concepts

No code is written or taught in this session; it is a judgement/retrospective clinic. The "code-related" content consists of:

- Referencing enacted code decisions: the CQRS split on product-service (S18), event-driven cache eviction, the retired `JwtAuthFilter`, the Order Service Resource Server configuration (S19–20), Istio configuration (S21), Outbox/Idempotency/API versioning code (S22), k6 test scripts (S23).
- Named code-level debt items to be examined: in-memory `SagaState` in `OrderSagaOrchestrator` (S12) — state lost on restart; hardcoded `PUBLIC_ROUTES`-style config patterns that may still exist in older session code; no database migrations (schema managed manually since Session 1); DLT events logged (S13) but no automated replay/alerting.
- Evidence sources the clinic asks students to use: tests, load-test observations, logs, traces, code complexity, operational steps, failure behavior.
- Exact code snippets teaching: none in this session.

## 7. Configuration

- No configuration is changed in this session.
- Configuration-level debt references: `PUBLIC_ROUTES`-style hardcoded config patterns (still open item); hardcoded JWT secret (resolved in S19–20); no Flyway/Liquibase migration tooling (open).
- Environment readiness requirement before Session 25 (Phase 3 Checkpoint): full local environment verified working — Docker, Kubernetes, Istio, Keycloak all reachable.
- Secret-management theme from S19–20 recalled in the clinic via the resolved debt item "Hardcoded JWT secret / no real Identity Provider → Keycloak + OAuth2".
- EXACT config content for this session: none (configuration not covered in the S24 PDFs beyond these references).

## 8. Failure scenarios

The clinic's "failure scenarios" are the red-flag answers and unresolved risks the session is designed to surface (per the task instruction, clinic content belongs here):

- **Red flag answers to guard against:** "CQRS should be applied everywhere for good architecture" (no scale/pain justification); "Istio is industry standard so every platform should use it" (no cost/benefit weighing); "There was only one right way to do this" (ignores S20's own clean-cutover-vs-parallel-run trade-off); "All our technical debt is resolved now" (no platform is ever fully debt-free); "I wouldn't change anything" (no hindsight applied).
- **Weak-answer table (tutorial):** "It works." vs "It works for the current context; here is the evidence and trade-off." / "X is industry standard. We should use it everywhere." vs "X solves this concrete problem; these are its costs for our context. We should use it where this problem exists and justify each extension." / "All debt is resolved." vs "These items are resolved; these remain open; these are newly discovered." / "I would change everything." / "I would change nothing." vs "I would change this specific decision because of this evidence or trade-off." / vs "I reviewed the alternatives and identified why the current choices still fit."
- **STILL OPEN debt (carried into Phase 4) — the concrete risks:**
  - In-memory `SagaState` in `OrderSagaOrchestrator` (Session 12) — lost on restart.
  - No database migrations (Flyway/Liquibase) — schema managed manually since Session 1.
  - Dead-letter queue handling maturity — DLT events logged (S13) but no automated replay/alerting.
  - `PUBLIC_ROUTES`-style hardcoded config patterns that may still exist in older session code.
- **NEWLY SURFACED debt:** this deck slide is intentionally a blank template — filled in from the actual class discussion during Questions 1 and 2 (CQRS, Istio); each group documents at least one NEWLY SURFACED debt item plus a one-sentence priority justification.
- **Capstone risk of not doing this session properly:** teams would re-litigate settled decisions (or blindly preserve everything); the tutorial: the goal is not to blindly preserve every previous decision and not to rewrite everything.

## 9. Trade-offs

The session is entirely about trade-off reasoning; the trade-off content of the five questions:

- **CQRS (S18):** justified given the described dashboard-vs-checkout conflict; marginal for a training platform without production read/write load; two models + synchronization mechanism as cost; re-verify the pain before copying the pattern elsewhere.
- **Service Mesh / Istio (S21):** powerful pattern with honestly named operational cost — sidecar per pod, control plane, learning curve, for a small single-language platform; valuable to LEARN, debatable to NEED.
- **Clean cutover vs parallel run (S19–20):** clean cutover correct for a fully-controlled training environment; a production system with live traffic and external consumers would weigh the parallel-run alternative much more seriously (Session 20's own Engineering Decision).
- **Debt resolution honesty:** resolved items verified (payment retry without idempotency → S22 Idempotency Keys; no API versioning → `/api/v1/` + deprecation window S22; hardcoded JWT secret → Keycloak + OAuth2 S19–20; no structured logging → JSON logs + trace correlation S17); open items carried; new items surfaced — the trade-off is explicit *what you fix now vs what you accept and carry*.
- **Hindsight trade-off (Q5):** e.g., structured logging from Session 1 instead of S17; considering CQRS/Outbox earlier given how naturally S7's Saga led to S22's Outbox gap — each with the cost/risk of changing it.
- **Inherited vs open decisions:** inherited baseline (not untouchable) vs team-owned choices (CQRS elsewhere; mesh partial vs full; debt prioritization) — changes must be justified by concrete requirement/problem/evidence/risk.
- **Judgement growth itself as the trade-off metric:** Session 8 answers ("It works, so it's fine" common; trade-offs less specific) → Session 24 answers ("this was probably premature" said willingly; richer trade-off language, real costs named).

## 10. Common mistakes

- Answering "It works, so it's fine" — the central anti-pattern the clinic exists to break.
- Defending a decision because it was taught or is industry standard; rejecting a technology purely because it adds complexity.
- Stating the solution before the problem; omitting costs; claiming benefits without evidence.
- Thinking the platform is debt-free; failing to distinguish resolved vs deferred debt.
- "I wouldn't change anything" — refusing to apply hindsight.
- Treating inherited decisions as untouchable (or rewriting everything) instead of a baseline with justified changes.
- Not recording newly surfaced debt; not defining what evidence would trigger reconsideration.
- Confusing "valuable to learn" with "necessary to deploy".
- Entering the Capstone without: finalized team, Core vs Advanced Scope reviewed, TD v2 priorities agreed, environment verified (Docker/Kubernetes/Istio/Keycloak reachable).

## 11. Interview questions

- Why was CQRS introduced, and would you introduce it the same way again? (Describe the read/write conflict, scale, benefit, cost, reconsideration criteria.)
- Why was Istio introduced, and does this platform actually need a service mesh? (Valuable to learn vs necessary to deploy; sidecar/control-plane/learning-curve costs.)
- Why was the hand-rolled JWT validation retired, and was a clean cutover right? (Training vs production with external consumers; parallel-run alternative.)
- What technical debt remains, and how would you prioritize it? (Specific item + priority argument; 6 prioritization factors.)
- What ONE decision from the first 16 sessions would you make differently, and why? (Concrete change + original trade-off + cost/risk of changing.)
- What evidence would make you reconsider a decision? (Strong-answer structure requires a Reconsideration statement.)
- What is the difference between inherited and owned architecture? (Inherited baseline; owned choices; changes justified by requirement/problem/evidence/risk.)
- How do you give a strong architecture answer? (8-part structure: Decision, Problem, Benefit, Cost, Evidence, Alternative, Reconsideration, Conclusion.)
- What does "Be the Harsh Critic" mean? (The new-senior-engineer memo test; honest trade-offs, not fairy tales.)

## 12. What I must memorize

- The clinic's standard sentence: "It works, but here is the specific trade-off we accepted, and here is what would make us reconsider it."
- The Simple Decision Model, 6 steps: Problem, Context, Options, Trade-off, Evidence, Reconsideration.
- The five Architecture Questions and their core positions: CQRS justified-but-marginal; Istio valuable-to-learn-debatable-to-need; clean cutover right for training but parallel-run weighs heavily in production; specific debt remains open; one earlier decision would be changed with concrete reasoning.
- Technical Debt Register v2 categories: RESOLVED (idempotency keys S22; API versioning S22; Keycloak S19–20; structured logging S17), STILL OPEN (in-memory SagaState S12; no Flyway/Liquibase; DLQ replay/alerting immature; PUBLIC_ROUTES hardcoded config), NEWLY SURFACED (filled live; ≥1 item per group + priority justification).
- The 6 debt prioritization factors: Impact, Likelihood, Scope, Cost of delay, Capstone dependency, Learning value.
- ADR mini-template fields: Title, Status (Accepted/Reconsider/Deferred), Context, Decision, Alternatives, Benefits, Costs/risks, Evidence, Reconsider when.
- Phase 3 = 8 sessions, 20 hours; Phase 4 = S25–S29; S25 Capstone Build Day = Offline Anchor Day #4, Wed 10AM–3PM, 5 hours.
- Phase 3 Checkpoint before S25: team finalized; Core vs Advanced Scope reviewed (Instructor Pack 3.5); TD v2 priorities agreed; Docker/Kubernetes/Istio/Keycloak all reachable.
- Inherited-as-is list: Config/Eureka/Gateway (S1–3); Resilience4j (S4–5); OpenFeign (S6); Choreography Saga (S7); Docker+K8s+CI/CD+GitOps (S9–16); Observability (S17); full security stack (S19–20).
- Open-for-team: CQRS elsewhere; mesh partial vs full; debt prioritization vs new feature work.
- Takeaway: "Architecture is not a collection of technologies. Architecture is a set of decisions, trade-offs, evidence, and consequences."

## 13. What I must understand

- Why a clinic (judgement exercise) is needed at all after 24 sessions: the answers about *why* matter more than the catalog of *what*.
- How to distinguish a justified decision from a premature/over-engineered one using problem → context → options → trade-off → evidence → reconsideration.
- Why "was it needed?" is a legitimate question, not a criticism — it is exactly the judgement the clinic builds ("Some of you will genuinely ask: did our training platform actually NEED this?").
- Why each Phase 3 technology was introduced at that particular point (connect each addition to its justifying problem; the recap table is the starting point of the retrospective).
- Why debt honesty matters: resolved vs deferred vs newly discovered — and why "all resolved" is a red flag.
- Why evidence (tests, logs, traces, load tests, code complexity, operational steps, failure behavior) is what separates a strong answer from an opinion.
- What "inherited does not mean untouchable" implies for the Capstone: understand, then justify keep/modify/replace.
- The exam-like discipline of the strong-answer 8-part structure.

## 14. What I should implement from memory

This is a non-coding session; "from memory" means reproducing the clinic artifacts:

- Run the decision model on any decision: state Problem/Context/Options/Trade-off/Evidence/Reconsideration.
- Answer all five architecture questions using the 8-part strong-answer structure, naming at least one benefit and one cost each.
- Build Technical Debt Register v2: verify the 4 resolved items; list the 4 open items; add ≥1 newly surfaced item from the CQRS/Istio discussions with a one-sentence priority justification; fill the TD-01..TD-06 worksheet (ID, debt/limitation, evidence, impact, priority, proposed action/owner).
- Apply the 6 debt prioritization factors to rank items (Impact, Likelihood, Scope, Cost of delay, Capstone dependency, Learning value).
- Write at least one short ADR using the mini-template for a seriously debated decision.
- Complete the Capstone Architecture Review Checklist (11 questions) and the individual reflection (from Session 23's homework: decision you'd defend, decision you're unsure about, what you'd do differently).
- Produce the Capstone Handoff Summary (Appendix B): mark Keep/Change/Defer per area (Infrastructure/discovery, Gateway/routing, Resilience, Communication/Saga, Observability, Security, CQRS/read models, Service mesh, Messaging reliability, API evolution, Performance, Technical debt) with reasons.

## 15. Relationship to previous sessions

- **Session 8:** the first Architecture Clinic — today is Clinic #2; the debrief explicitly compares the SHAPE of today's answers to Session 8's Clinic #1 notes.
- **Session 1–16 decisions are directly in scope** of Question 5 ("The ONE decision from Sessions 1–16 you'd make differently"); the inherited list spans S1–S16 (Config/Eureka/Gateway, Resilience4j, Feign, Choreography Saga, Docker/K8s/CI-CD/GitOps).
- **Sessions 17–23 are the recap table** of today: S17 Observability; S18 CQRS; S19–20 Security; S21 Service Mesh; S22 Advanced Patterns (Outbox/Idempotency/API Versioning); S23 Performance (k6).
- **Specific cross-session threads named:** in-memory SagaState in OrderSagaOrchestrator (S12); DLT events logged (S13); Flyway/Liquibase named since S8 and never implemented; PUBLIC_ROUTES hardcoded config from "older session code"; Session 20's own Engineering Decision (clean cutover vs parallel run) referenced in Q3; "how naturally S7's Saga led to S22's Outbox gap" in Q5.
- **Session 23's homework** provides the three individual-reflection questions shared aloud in Part 4 today.
- The resolved-debt table is a map of earlier sessions: S22 idempotency keys and API versioning; S19–20 Keycloak; S17 structured logging.

## 16. Relationship to future sessions

- **Phase 4 (S25–S29):** S25 Capstone — Build Day (Offline Anchor Day #4) Wed 10AM–3PM; S26 Capstone — Deployment (Online); S27 Capstone — Observability & Security (Online); S28 Capstone — Testing & Polish (Online); S29 Final Presentations & Evaluation.
- "Phase 4 begins Session 25 — everything from today's Technical Debt Register v2 is now YOUR call to make, as a team, with a real justification either way."
- **Inherited as-is foundation (deck + tutorial §9.1):** Config/Eureka/Gateway (S1–3); full Resilience4j stack (S4–5); OpenFeign (S6); Choreography Saga (S7); Docker + K8s + CI/CD + GitOps (S9–16); Observability (S17); full security stack (S19–20).
- **Open to the team's own judgement (§9.2):** whether to adopt CQRS elsewhere; whether to extend the Service Mesh to every service or leave it partial; how to prioritize the STILL OPEN TD v2 items against new Capstone feature work; whether a new Capstone feature creates new architectural requirements; whether an inherited decision should be retained, modified, or replaced — and why.
- "Inherited does not mean untouchable. It means the team starts from an established baseline."
- Phase 4 is "Building the Capstone — your own decisions now; applying judgement, not following a script; presenting and defending architecture choices." Bring Tech Debt Register v2, architecture notes, and decision rationale to the Build Day.
- Next: Session 25 — Capstone Build Day (Phase 4 begins) — 5-Hour OFFLINE Anchor Day, Wednesday 10:00 AM.

## 17. Lab relationship

Session 24 has no coding lab. What the slides say about labs / exercises / discussion work / deliverables / checkpoint (exact):

- **No lab, exercise, demo, or homework is named as such in either S24 PDF.** The session's structured activities are the clinic discussions and deliverables below.
- **The clinic itself is the "exercise":** work in small groups; approximately eight minutes per question; rotate the facilitator so every participant practices architectural reasoning (5 questions — see §3).
- **Final student deliverables (tutorial, 7):** (1) Completed discussion notes for the five Architecture Clinic questions. (2) Technical Debt Register v2, including resolved, open, and newly surfaced items. (3) At least one short ADR for a decision the team debated seriously. (4) A clear list of inherited platform components. (5) A clear list of architectural choices the Capstone team owns. (6) A prioritized list of technical-debt candidates for Phase 4. (7) An individual reflection from each team member.
- **Individual reflection (deck + tutorial):** three questions from Session 23's homework — (1) one architectural decision from Sessions 1–23 you would defend confidently under questioning; (2) one decision you are genuinely UNSURE was correct, and why; (3) one thing you would do differently if starting the platform over today — shared aloud during Part 4 of today's session; tutorial adds written prompts (decision understood differently now; decision to reconsider first; most important trade-off learned; debt the Capstone should address; decision you'd keep and its evidence; one condition that would make you change your mind).
- **Capstone Architecture Review Checklist (tutorial, 11 questions):** purpose of every major Phase 3 addition; ≥1 trade-off for CQRS; ≥1 trade-off for Istio/service mesh; why Keycloak/OAuth2 replaced the earlier approach; identify remaining technical debt; distinguish resolved from deferred debt; recorded new debt from the clinic; which inherited components must keep working; which decisions are explicitly open to Capstone judgement; every team member can explain ≥1 architectural decision without slides; state what evidence would cause reconsideration.
- **Phase 3 Checkpoint — required before Session 25 (Capstone Build Day) (deck):** Capstone team finalized; Core Scope vs Advanced Scope reviewed (Instructor Pack Section 3.5); Technical Debt Register v2 priorities agreed upon as a team; full local environment verified working — Docker, Kubernetes, Istio, Keycloak — all reachable.
- **Daily Quiz (deck):** 8 questions — 10 minutes — "Reflective, not purely technical."
- **Appendix A — One-Page Architecture Review Worksheet** (decision/problem/context/alternatives/gain/complexity-cost/evidence/reconsider prompts) and **Appendix B — Capstone Handoff Summary** (areas: Infrastructure/discovery, Gateway/routing, Resilience, Communication/Saga, Observability, Security, CQRS/read models, Service mesh, Messaging reliability, API evolution, Performance, Technical debt — each marked Keep/Change/Defer with reason).
- **Checkpoint commits in slides:** none shown for Session 24 (no commit message, no code checkpoint).
