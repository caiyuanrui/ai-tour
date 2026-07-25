# 2026-07-25 — Project Planning: P3v2 Architecture Design — Token-Budget Reasoning, Production Overruns & RL Efficiency

Course: Research Lab
Topic: Project Planning (Cycle 2, Day 2)
Stage: Designing the P3v2 implementation plan — SDB contract, evaluation framework, multi-signal routing, graceful degradation
Confidence: 0.72 -> 0.78

## Today's Question

Last session (2026-07-18) established the *what* of the P3v2 revision: budget-aware evaluation + SDB runtime architecture + multi-signal routing + graceful degradation. This session's job is the *how* — the concrete design decisions that turn these principles into a buildable implementation plan.

Three specific design questions for today:

1. **Budget control architecture:** Should P3 implement budget control at the prompt level (like Token-Budget-Aware LLM Reasoning), the system level (like Token Budgets' affine type system), or both?
2. **Graceful degradation protocol:** What happens at each budget exhaustion stage, and what signals/consumers are needed?
3. **Implementation priority:** Which component should be built first in the implementation-notes phase?

## Main Paper

### Metadata

- **Title:** Token-Budget-Aware LLM Reasoning
- **Authors:** Tingxu Han, Zhenting Wang, Chunrong Fang, Shiyu Zhao, Shiqing Ma, Zhenyu Chen
- **Year:** 2024
- **Venue:** arXiv:2412.18547
- **Link:** https://arxiv.org/abs/2412.18547

### Why this paper?

This paper directly validates the core premise of the P3 thesis: **that token budgets can be dynamically allocated based on reasoning complexity, and doing so reduces cost with only slight performance loss.** While P3 focuses on agent runtime budget control (ReAct loops with tool calls), this paper shows the same principle works for pure reasoning (CoT chains). If prompt-based token budgets work for reasoning chains, the architecture should be even more impactful for agent loops where observation sizes vary enormously.

### Core Problem

LLMs use unnecessarily lengthy CoT reasoning chains. When prompted to stay within a token budget, LLMs can compress their reasoning — but the choice of budget threshold is critical: too tight degrades accuracy, too loose wastes tokens. The paper asks: can token budgets be dynamically determined per problem?

### Main Idea

A **token-budget-aware reasoning framework** (TALE) that:
1. Uses a lightweight classifier to predict problem difficulty
2. Maps difficulty to an appropriate token budget for CoT reasoning
3. Passes the budget as a prompt instruction ("think within N tokens")

Key results:
- **GSM8K:** 93.0% accuracy at 37.4% of original token cost (prompt-based budget)
- **MATH:** 48.8% accuracy at 51.0% token cost
- Dynamic budgeting outperforms both fixed-budget and no-budget baselines
- The classifier is lightweight — a small LM or even a simple regression model suffices

### Research takeaway

**For P3v2, this paper validates the signal-routing approach from a new angle.** Cycle 1 of P3 used stateful complexity tracking (accumulated step count + tool output size + tool call count). This paper shows that even a simpler signal (predicted problem difficulty → token budget) can work well for pure reasoning. The implication for P3: **routing signals don't need to be perfect — they just need to be better than no routing.** The 93% GSM8K accuracy at 37% cost validates this.

**Critical difference from P3:** This paper operates at the *prompt level* (tell the model to use N tokens), while P3 operates at the *system level* (route to different model tiers/k-budget levels). These are complementary: P3's system-level routing could apply TALE's prompt-level budgets *within* each tier for finer-grained control. The P3v2 architecture should support both layers.

### Core Design Implication

The paper's lightweight classifier approach validates that **single-signal routing can work**, but P3's agent domain requires richer signals because:
- Observation sizes vary by 100x (tool outputs)
- Task complexity isn't known upfront (hidden in instruction)
- Budget overruns compound over multi-step episodes

P3 needs multi-signal routing where TALE's single-signal approach works for reasoning chains. This concretely justifies the P3v2 multi-signal design.

---

## Related Papers

### Paper 1: Token Budgets: An Empirical Catalog of 63 LLM-Agent Budget-Overrun Incidents

- **Authors:** Sajjad Khan
- **Year:** 2026
- **Venue:** arXiv:2606.04056
- **Link:** https://arxiv.org/abs/2606.04056
- **Contribution:**
  - First empirical catalog of production budget-overrun incidents: **63 confirmed incidents from 21 orchestration frameworks (2023–2026)**
  - Taxonomy of 8 failure clusters (inter-rater κ = 0.837, N = 113) + 47 structural entries
  - Builds an **affine-typed Rust crate** (`token-budgets`) that makes cloning, double-spending, or using a delegated budget a **compile error** rather than a runtime hazard
  - Documents dollar losses for individual incidents (some reaching thousands of dollars before detection)
- **Relation to main paper:** The main paper shows *how* to control tokens at the prompt level; this paper shows *why* budget control is necessary at the system/architecture level. Production agents fail catastrophically without proper budget discipline — a single retry loop can spend thousands of dollars. Together, they argue for a **two-layer budget architecture**: prompt-level hints (TALE) + system-level enforcement (Token Budgets).
- **Specific relevance to P3v2 graceful degradation:** The 8-cluster taxonomy provides an empirical checklist for P3's graceful degradation protocol. Each failure cluster maps to a specific architectural gap that P3v2 must address:
  - **Retry loops without budget ceilings** → P3's HARD_STOP + ECONOMY fallback
  - **Observations exceeding cost estimates** → P3's purification + size-based routing
  - **Cross-episode budget leakage** → P3's episode-scoped budget reset
  - **No graceful degradation path** → P3's defined consumer for each budget signal
- **Importance:** **Deep read recommended** before P3v2 implementation. The failure taxonomy should be treated as a requirements document.

### Paper 2: Token-Efficient RL for LLM Reasoning

- **Authors:** Alan Lee, Harry Tong
- **Year:** 2025
- **Venue:** arXiv:2504.20834
- **Contribution:**
  - Proposes RL strategies for token-efficient reasoning under strict compute limits (LoRA-compatible)
  - Introduces **S-GRPO** (stochastic GRPO) and **T-SPMO** (token-level prefix matching for fine-grained credit assignment)
  - Applied to Qwen2-1.5B: accuracy on SVAMP from 46% to 70%+, strong on multi-digit multiplication
  - **Surprising finding:** Full-token GRPO under LoRA fails to improve — selective token-level optimization acts as an implicit regularizer in low-parameter regimes
- **Relation to main paper:** Both papers optimize for token efficiency — the main paper at inference time (prompt-based budgets), this one at training time (RL with token-level credit). They represent complementary approaches that could be combined: TALE for inference-side routing, S-GRPO for training-side optimization. For P3v2, this paper suggests a long-term direction: if the effort router itself could be trained via token-efficient RL rather than heuristic rules, routing decisions might generalize better across task types.
- **Importance:** Not immediately actionable for P3v2's first implementation phase (which focuses on heuristic routing + system architecture), but highly relevant for P3 Phase 2 or P4 when learned routing is on the roadmap.

---

## Current Understanding

### P3v2 Architecture Design (Concrete Specs)

Based on the three papers and prior Cycle 2 work, here is the concrete P3v2 architecture design:

#### 1. Two-Layer Budget Architecture

```
Layer 1: Prompt-Level Budget Hints (from TALE)
  └── Lightweight difficulty classifier → token limit per step
  └── Passed as prompt instruction ("reason in ≤ N tokens")
  └── Soft hint — model may exceed, but tends to comply

Layer 2: System-Level Budget Enforcement (from Token Budgets)
  └── Per-episode token budget (ECONOMY / STANDARD / DEEP)
  └── Accumulated token tracking across steps
  └── HARD_STOP at episode budget ceiling
  └── Fallback: ECONOMY mode on WARNING signal
```

**Why two layers?** TALE shows prompt hints are effective (37-51% cost reduction) but not binding. The Token Budgets catalog shows the system layer must enforce hard ceilings. Together they provide both efficiency *and* safety.

#### 2. SDB Contract for Budget Signals

```
BudgetSignal = {
  proposer:   StatefulEffortRouter (determines budget level)
  verifier:   BudgetTracker (checks remaining budget, rate-limits)
  commit:     Executor (runs step at determined budget level)
  reject:     FallbackHandler (graceful degradation on OVER_BUDGET)
}

Signal flow:
  StatefulEffortRouter.propose(step_context) → budget_level
  BudgetTracker.verify(budget_level) → OK | WARNING | HARD_STOP | OVER_BUDGET
  Case OK → Executor.commit(budget_level)
  Case WARNING → Executor.commit(ECONOMY) [downgrade]
  Case HARD_STOP → FallbackHandler.reject("emit partial result, stop loop")
  Case OVER_BUDGET → FallbackHandler.reject("emit partial result, notify operator")
```

#### 3. Multi-Signal Routing Function

```python
class StatefulEffortRouter:
    def route(self, episode_state: EpisodeState) -> BudgetLevel:
        signals = {
            "accumulated_steps":        episode_state.step_count,
            "instruction_complexity":   self._estimate_complexity(episode_state.instruction),
            "max_observation_size":     episode_state.max_observation_size_history,
            "tool_call_density":        episode_state.tool_call_count / max(1, episode_state.step_count),
            "remaining_budget_pct":     episode_state.remaining_tokens / episode_state.episode_budget,
        }
        score = weighted_sum(signals, weights=[0.3, 0.25, 0.2, 0.15, 0.1])
        return quantize(score)  # ECONOMY / STANDARD / DEEP
```

**Key insight from TALE:** The classifier doesn't need to be perfect. A simple weighted sum with good signals outperforms no routing. The weights can be tuned empirically during the implementation phase.

#### 4. Graceful Degradation Protocol

| Budget Stage | Trigger | Action | Expected Outcome |
|---|---|---|---|
| OK | budget > 80% remaining | Normal routing | Standard operation |
| WARNING | 50-80% remaining | Fall to ECONOMY for remaining steps | Cost preservation |
| HARD_STOP | Budget exhausted mid-step | Complete current step if < 20% over, then stop | Partial result |
| OVER_BUDGET | Budget + margin exceeded | Force stop, emit collected results | Graceful failure |

The Token Budgets catalog (Paper 1) provides the empirical justification: 63 real incidents would have been prevented by this protocol.

#### 5. Evaluation Framework (Updated from 2026-07-18)

Per the Token Economies methodology, P3v2 evaluation reports:

| Metric | Description |
|--------|-------------|
| Gross cost | Total tokens consumed (routing + purification + execution) |
| Net efficiency | Task accuracy ÷ gross cost |
| Routing overhead | % of total tokens used for routing decisions alone |
| Purification savings | Tokens saved by observation purification (with/without) |
| Per-budget accuracy | Accuracy at ECONOMY / STANDARD / DEEP budgets independently |
| Break-even complexity | Task complexity at which routing overhead = routing savings |
| Failure rate | # of OVER_BUDGET incidents per 100 episodes |

### Which component to build first?

**Priority order for the implementation-notes phase:**

1. **Budget tracking + enforcement (Layer 2)** — This is the foundation. Without system-level enforcement, the agent can still overrun. Build as a lightweight wrapper around existing Hermes tool calls. **Estimated effort: 1 session.**

2. **Multi-signal routing function** — The single largest improvement over Cycle 1. Replace the instruction-length proxy with the weighted signal approach above. **Estimated effort: 1 session.**

3. **Graceful degradation protocol** — Depends on #1 (needs budget tracking). Implement the fallback handlers. **Estimated effort: 1 session.**

4. **Evaluation framework** — Instrument everything. Add cost decomposition, per-budget reporting. **Estimated effort: 1 session.**

5. **Prompt-level budget hints (Layer 1)** — Optional enhancement after core is working. **Estimated effort: 1 session.**

### Confidence Update: 0.72 -> 0.78

**What raised confidence:**
- TALE paper validates the core premise (dynamic budgets work) from a completely independent angle (prompt-level for reasoning chains)
- Token Budgets catalog provides strong empirical motivation and an incident-based requirements checklist
- The two-layer architecture clearly addresses both efficiency (TALE) and safety (Token Budgets)
- Concrete design spec is now complete enough to start building

**What keeps confidence below 0.80:**
- No paper yet directly validates **multi-signal routing for agent tool-use scenarios** (TALE validates single-signal for reasoning chains)
- The weighted-sum routing function is heuristic — optimal weights unknown until empirically tested
- Real API validation hasn't started (Cycle 1 failure #3 still unaddressed)
- P3v2 needs to run on real Hermes/HuggingFace API calls before any metric is trustworthy

---

## Key Concepts

- **Two-layer budget architecture:** Prompt-level hints (soft) + system-level enforcement (hard) — from TALE + Token Budgets papers
- **Token-Budget-Aware LLM Reasoning (TALE):** Lightweight classifier → dynamic token budget → prompt-based compression, achieving 37-51% cost reduction
- **Affine-typed budget enforcement:** Making budget ownership a compile-time property (from Token Budgets' Rust crate) — the principle generalizes to any type system
- **8-cluster failure taxonomy:** Empirical catalog of 63 production budget-overrun incidents — actionable requirements checklist for P3v2
- **Stateful multi-signal routing:** Five signals (steps, complexity, obs size, tool density, remaining budget) with weighted sum — heuristic but principled
- **SDB contract for budget signals:** Explicit proposer-verifier-commit-reject protocol for each budget decision
- **Per-budget evaluation:** Reporting accuracy at each budget level independently, plus routing overhead decomposition

## Open Questions

1. **Weight calibration:** What are the optimal weights for the five routing signals? Needs empirical testing against a labeled dataset of agent episodes with known "correct" budget levels.
2. **Prompt-level vs system-level tradeoff:** At what task granularity does prompt-level budget hinting outperform system-level routing (and vice versa)? A prompt hint costs ~0 tokens; a routing decision costs a classifier call + potential model switch.
3. **Failure rate baseline:** What is the "natural" budget-overrun rate of naive ReAct without any budget control? The Token Budgets catalog documents production incidents but doesn't provide a per-episode baseline rate.
4. **Budget granularity:** Are three levels (ECONOMY/STANDARD/DEEP) optimal, or should there be continuous budget allocation? TALE uses a continuous budget parameter in the prompt; P3 uses discrete levels for model-tier routing. Which works better for agents?
5. **Task-type specificity:** Does the multi-signal routing function need different weights for different task types (coding, search, data processing)? The security agents paper (2607.15263) suggests yes.

## Possible Thesis Ideas

### Priority 1 (Refined): Practical Token-Budget-Controlled ReAct Agent v2 — Architecture-Driven Cost Control

**Refined framing:** Demonstrate that a single-agent ReAct system can achieve 40-60% cost reduction over naive ReAct through a combination of (a) system-level budget enforcement, (b) multi-signal stateful routing, and (c) observation purification — validated on real API calls with proper budget-aware evaluation methodology.

**Novelty claim (strengthened by today's papers):** No existing work combines all three components with a proper evaluation methodology that decomposes routing overhead. TALE shows prompt budgets work but doesn't address agent tool-use loops. The Token Budgets catalog shows the problem exists but only proposes a Rust type-system mitigation (not a runtime solution). P3v2 fills the gap between these two extremes.

### Priority 2: Failure Taxonomy for Agent Budget Design

From the Token Budgets paper: a systematic catalog of 63 incidents with proposed mitigations. This could be extended with P3v2's own failure patterns into a practitioner's guide to budget-safe agent design.

### Priority 3: Learned Routing for Token-Budgeted Agents

From the Token-Efficient RL paper: train the routing function itself via selective token optimization rather than heuristic rules. This is the natural next step after P3v2 demonstrates that heuristic routing works.

---

## Next Step

**Advance to implementation-notes.** The project-planning phase for Cycle 2 is complete:
- Design spec is concrete enough to build
- Confidence threshold (0.65) is exceeded (0.78)
- The next topic in the rotation is **implementation-notes** (topic index 1)

First implementation task: **Build the budget tracking + enforcement layer** as a lightweight Python module wrapping Hermes tool calls. Goal: demonstrate that system-level budget enforcement works (no overruns) and measure baseline routing overhead.
