# 2026-07-18 — Project Planning: Revising P3 from Cycle 1 Failures — Budget-Aware Evaluation & Production Runtime Design

Course: Research Lab
Topic: Project Planning
Stage: Cycle 2 — Revising Priority #3 thesis based on 4 failure patterns from Cycle 1
Confidence: 0.75 -> 0.72

## Today's Question

Cycle 1 built and benchmarked a P3 prototype (Token-Budget-Controlled ReAct Agent) and identified 4 failure patterns through systematic postmortem:
1. **Proxy variable failure** — instruction length ≠ task complexity for routing decisions
2. **Interface incompleteness** — budget signals emitted with no defined consumers or handlers
3. **Simulation overconfidence** — synthetic benchmarks don't survive real API contact
4. **Metric aggregation blindness** — 87.9% headline hides bimodal distribution

Given these findings, how should the P3 thesis be revised? What new evaluation methodology and runtime architecture should the Cycle 2 prototype adopt?

## Main Paper

### Metadata

- Title: Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies
- Authors: Junlin Wang, Siddhartha Jain, Dejiao Zhang, Baishakhi Ray, Varun Kumar, Ben Athiwaratkun
- Year: 2024
- Venue: arXiv:2406.06461
- Link: https://arxiv.org/abs/2406.06461

### Why this paper?

This is the single most critical paper for the P3 revision. It directly identifies and formalizes the fundamental flaw in Cycle 1's evaluation methodology: **traditional evaluations that focus solely on performance metrics overlook the fact that increased effectiveness may come from additional compute, not algorithmic ingenuity.** Our Cycle 1 benchmark was exactly this — it reported impressive 87.9% compression without properly controlling for the compute budget of the routing decisions themselves.

### Core Problem

A diverse array of reasoning strategies (CoT, ToT, self-consistency, multi-agent debate, Reflexion) has been proposed, but evaluations miss a key factor: the increased effectiveness due to additional compute. Without budget-aware evaluation, a skewed view of strategy efficiency is presented — complex strategies appear better simply because they use more compute.

### Main Findings

| Finding | Implication for P3 |
|---------|-------------------|
| Complex strategies often outperform baselines **only because** they consume more compute | P3's routing gains must be measured net of routing overhead |
| Simple baseline (CoT self-consistency) **frequently outperforms** complex strategies given comparable budget | Effort routing must benchmark against simple fixed-budget baselines |
| Some strategies (multi-agent debate, Reflexion) **get worse** with more budget | More budget ≠ better; P3 must find optimal budget per task |
| Budget-aware evaluation reveals different optimal strategies at different budget levels | P3 needs multi-budget-level evaluation, not single-point metrics |

### Research takeaway

**The evaluation methodology itself was a source of metric inflation in Cycle 1.** The "87.9% compression" number only looks at outputs, not at the cost of the routing decisions that achieved it. The Token Economies paper shows that a proper evaluation must compare strategies at **fixed cost levels** and decompose performance by inference spend and tool spend separately.

**Revised evaluation methodology for P3 Cycle 2:**

1. **Fixed-budget baselines:** Always compare against a simple fixed-budget ReAct loop consuming the same total tokens. If P3 with routing doesn't outperform the fixed-budget baseline, the routing overhead isn't justified.
2. **Cost decomposition:** Separate tracking of (a) routing decision costs, (b) observation purification costs, (c) actual task execution costs.
3. **Multi-budget evaluation:** Test at ECONOMY / STANDARD / DEEP budgets independently — report per-budget accuracy, not just "best case."
4. **Diminishing returns curve:** Plot accuracy vs. total tokens consumed to show the efficiency frontier.

### Modern perspective (July 2026)

This paper (June 2024) was among the first to call for budget-aware evaluation. Since then, the field has produced SupervisorAgent (ICLR 2026, 29.68% token reduction), CogRouter (Feb 2026, 62% reduction), and the "Beyond Success Rate" security-agent paper (July 2026, applying cost-success lens to security agents). The token-economics-aware evaluation paradigm is now mainstream. The question is no longer whether budget-aware evaluation matters, but **how to implement it as a standard practice** in agent research — exactly what P3 should contribute.

---

## Related Papers

### Paper 1: Beyond Success Rate — Cost-Aware Evaluation of Offensive and Defensive Security Agents

- **Authors:** Paul Kassianik, Blaine Nelson, Yaron Singer
- **Link:** https://arxiv.org/abs/2607.15263
- **Contribution:**
  - Evaluates security agents through cost-success lens — not just best-case success
  - Compares models at **fixed cost levels** and decomposes performance by inference spend vs tool spend
  - **Key finding:** Performance has different scaling regimes — offensive CTF benefits from more test-time compute, defensive SOC tasks depend more on disciplined tool use than raw reasoning budget
  - Proposes that benchmarks should measure **economic efficiency and operational fit** alongside task success
- **Relation to main paper:** Independent validation of budget-aware evaluation in a different domain (security agents). The finding that different task types have different scaling regimes directly supports P3's core thesis: **effort routing must be task-type-aware, not just budget-level-aware.** The same token budget buys different effectiveness for different task categories.

### Paper 2: A Methodology for Selecting and Composing Runtime Architecture Patterns for Production LLM Agents

- **Authors:** Vasundra Srinivasan
- **Link:** https://arxiv.org/abs/2605.20173
- **Contribution:**
  - Introduces the **Stochastic-Deterministic Boundary (SDB)** as a four-part contract: proposer, verifier, commit step, and reject signal
  - Catalog of 6 runtime patterns for production agent systems
  - Identifies **replay divergence** failure mode (LLM consumers of deterministic event logs produce different outputs under model changes)
  - Provides a reliability decomposition separating per-call model variance from architectural momentum
  - **Directly addresses failure pattern #2 (interface incompleteness):** budget signals need explicit consumers with defined commit/reject semantics
- **Relation to main paper:** The Token Economies paper says "evaluate with budget-awareness"; this paper says "design the runtime so budget signals are first-class architectural objects." Together they complete the picture: proper evaluation methodology + proper runtime architecture = production-ready P3.
- **Specific architectural insight for P3:** The budget signal needs a defined consumer with a **reject path**. When a step goes OVER_BUDGET, the SDB reject signal specifies what happens: fall back to ECONOMY mode, return partial result, or emit a user-facing notification. This is the missing piece in Cycle 1's architecture.

---

## Current Understanding

### What Cycle 1 established (verified findings):

| Component | Status | Key Metric |
|-----------|--------|------------|
| Observation purification | ✅ Works well | 87.9% overall compression, 96.7% for JSON |
| Stateful complexity tracking | ✅ Bug fixed | Always-ECONOMY issue resolved |
| Effort routing (3 levels) | ⚠️ Signal quality poor | Instruction length is bad proxy |
| Real API validation | ❌ Not done | Simulation overconfidence unaddressed |
| Graceful degradation | ❌ Not designed | Budget signals have no consumers |

### Revised P3 thesis for Cycle 2:

**Thesis:** A practical token-budget-controlled ReAct agent can achieve 30-50% cost reduction over naive ReAct, but only if (a) its evaluation methodology accounts for routing overhead costs, and (b) its runtime architecture treats budget signals as first-class architectural objects with defined consumers.

**The key insight from cross-paper analysis:** All three papers converge on a single principle — **the evaluation framework must match the runtime architecture.** If your agent has budget signals but no defined consumers (Cycle 1 failure #2), your evaluation can't measure what matters (Cycle 1 failure #3). If your evaluation doesn't control for compute budget (failure #3), your metrics are inflated (failure #4). If your proxy signals are wrong (failure #1), the routing decisions make everything worse.

### Revised Cycle 2 implementation plan:

1. **Rebuild evaluation methodology first** — before writing any new routing code, implement the Token Economies framework: fixed-budget baselines, cost decomposition, multi-budget evaluation, diminishing-returns curves.
2. **Redesign runtime architecture** — use the SDB contract pattern from the Runtime Architecture paper: budget signal → verifier → commit/reject → fallback.
3. **Replace instruction-length routing** — with multi-signal stateful complexity tracking (accumulated step count + tool output size + tool call count + task type).
4. **Add graceful degradation** — define explicit OVER_BUDGET → ECONOMY fallback with partial result preservation.
5. **Real API gate** — no metric reported as final until validated on real API calls.

## Key Concepts

- **Budget-aware evaluation framework (Token Economies):** Comparing strategies at fixed cost levels, decomposing performance by inference spend vs tool spend
- **Diminishing returns curve of reasoning:** More compute yields less marginal accuracy gain — the fundamental economic argument for budget control
- **Fixed-budget baseline:** Simple chain-of-thought self-consistency at the same budget often outperforms complex strategies — P3 must beat this baseline
- **Stochastic-Deterministic Boundary (SDB):** The four-part contract (proposer, verifier, commit, reject) that governs how LLM outputs become system actions
- **Replay divergence:** LLM consumers of deterministic event logs produce different outputs under model/version changes — a reliability failure mode for agent runtimes
- **Cost decomposition for agents:** Separating routing costs, purification costs, and execution costs in the evaluation
- **Per-budget accuracy reporting:** Reporting accuracy at ECONOMY/STANDARD/DEEP budgets independently, not just a single "best case" number

## Open Questions

1. **Fixed-budget baseline calibration:** What fixed-budget ReAct loop (in tokens) should P3 compare against? The same total tokens consumed by the routed version, or a theoretically optimal fixed allocation?
2. **SDB pattern selection for P3:** Which of the 6 runtime patterns (hierarchical delegation, scatter-gather + saga, event-driven sequencing, shared state machine, supervisor + gate, HITL) best fits a single-agent ReAct loop with budget control? The paper's methodology provides selection criteria, but applying them to P3 is new.
3. **Routing cost break-even point:** At what task complexity does the routing overhead pay for itself? For trivial tasks, routing cost > savings. For complex tasks, routing is essential. Finding this break-even curve empirically is a standalone contribution.
4. **Metric aggregation across budget levels:** If accuracy is higher at DEEP budget but lower at ECONOMY, which number is "the" result? The Token Economies paper doesn't fully address how to aggregate across budget levels into a single comparative score.
5. **Domain-specific scaling regimes:** The security paper shows different tasks scale differently with budget. Does P3's effort routing need a task-type classifier as a prerequisite, or can a single routing policy work across task types?

## Possible Thesis Ideas

### Revised Priority 1: Budget-Aware Evaluation Methodology for Single-Agent ReAct Systems

*(New — emerged from this session)*

**Value:** The Token Economies paper shows how to evaluate reasoning strategies fairly. But no paper applies this methodology specifically to **single-agent ReAct loops with budget control.** A standalone paper demonstrating the correct evaluation methodology (fixed-budget baselines, cost decomposition, per-budget accuracy reporting) for a practical token-budget-controlled agent would be a **methodology contribution** — and a prerequisite for any subsequent P3 publication.

**Novelty:** Applying budget-aware evaluation to ReAct agents specifically (not just reasoning strategies), plus the addition of **routing overhead decomposition** as a distinct cost category.

### Priority 2 (Revised): Practical Token-Budget-Controlled ReAct Agent v2

**Refined from Cycle 1:** The P3 prototype exists but needs:
- Evaluation methodology rewrite (apply Token Economies framework)
- Runtime architecture redesign (apply SDB contract pattern)
- Multi-signal routing (replace instruction-length proxy)
- Graceful degradation (defined consumer for budget signals)
- Real API validation gate

**Novel angle:** No existing paper combines all three: (a) budget-aware evaluation, (b) SDB-runtime architecture, and (c) observation purification + effort routing for single-agent ReAct loops. Each component exists in isolation; combining them with a proper evaluation framework is the contribution.

### Priority 3: Architecture-Driven Reliability for Token-Budgeted Agents

*(From the Runtime Architecture paper's reliability decomposition)*

Separating per-call model variance from architectural momentum suggests that **as model variance decreases, pattern choice becomes the dominant reliability lever.** This could mean that a well-architected budget controller (using SDB contracts) will matter more as models get cheaper and more reliable — counterintuitive but testable.

### Revised Thesis Priority List

1. **[New] Budget-Aware Evaluation Methodology for Single-Agent ReAct** — Highest methodological priority; P3 cannot be published without first solving this
2. **[P3v2] Practical Token-Budget-Controlled ReAct Agent v2** — Core implementation, redesigned with SDB architecture + multi-signal routing
3. **[P1] Adaptive Cognitive Depth for Real-World Agent Tasks** — Validated but requires training pipeline
4. **[New] Architecture-Driven Reliability** — Speculative but provocative angle

---

## Next Step

The next research-lab session should be a **project-planning** continuation (one more day) to produce a concrete implementation plan for the P3v2 architecture. Specifically:

1. **Design the SDB contract** for P3's budget control signals — define proposer, verifier, commit, reject explicitly
2. **Design the evaluation framework** — specify fixed-budget baseline, cost decomposition categories, per-budget reporting format
3. **Specify the multi-signal routing function** — what signals, how weighted, fallback rules
4. **Specify graceful degradation protocol** — what happens at each budget exhaustion level

After this design is complete, advance to **implementation-notes** to build the P3v2 prototype.
