# 2026-06-13 — Project Planning: Adaptive Reasoning Depth Thesis — Validation & Refinement

Course: Research Lab
Topic: Project Planning
Stage: Deep-dive into Priority #1 Thesis
Confidence: 0.0 -> 0.55

## Today's Question

How has the Adaptive ReAct Depth thesis direction (Priority #1 from Week 1) been validated or challenged by the latest research? What should the concrete project plan look like?

## Main Paper

### Metadata

- Title: Think Fast and Slow: Step-Level Cognitive Depth Adaptation for LLM Agents (CogRouter)
- Authors: Ruihan Yang, Fanghua Ye, Xiang We, Ruoqing Zhao, Kang Luo, Xinbo Xu, Bo Zhao, Ruotian Ma, Shanyi Wang, Zhaopeng Tu, Xiaolong Li, Deqing Yang, Linus
- Year: 2026
- Venue: arXiv:2602.12662 (cs.AI, cs.CL)
- Link: https://arxiv.org/abs/2602.12662

### Why this paper?

This paper directly validates the Adaptive ReAct Depth thesis idea from Week 1. The thesis proposed: *"Dynamically decide between Thought and Action at each step based on uncertainty estimation from the LLM's token probabilities."* CogRouter does exactly this — but better — using a 4-level cognitive hierarchy grounded in cognitive science (ACT-R) and a two-stage RL training pipeline. It's the single most relevant paper for refining this thesis direction.

### Core Problem

Current LLM agents use **fixed cognitive patterns**: non-thinking models produce immediate shallow responses, while thinking models apply uniform deep reasoning to every step. This is wasteful for long-horizon tasks where some steps need strategic planning (e.g., decomposing a novel problem) and others need routine execution (e.g., opening a URL).

### Main Idea

**CogRouter** trains agents to dynamically adapt cognitive depth at each step using a hierarchy of 4 cognitive levels inspired by ACT-R theory:

| Level | Name | Description | Token Cost |
|-------|------|-------------|------------|
| 1 | Instinctive | Fast, automatic responses (routine ops) | ~200 tokens |
| 2 | Routine | Simple rule-based execution (familiar patterns) | ~500 tokens |
| 3 | Deliberate | Intermediate reasoning (unfamiliar errors, trade-offs) | ~2,000 tokens |
| 4 | Strategic | Deep multi-hypothesis reasoning (novel problems) | ~8,000 tokens |

Two-stage training:

1. **CoSFT (Cognition-aware SFT):** Fine-tune the model to produce stable, level-specific behavioral patterns for each cognitive depth.
2. **CoPO (Cognition-aware Policy Optimization):** Step-level credit assignment via **confidence-aware advantage reweighting** — the key insight is that *appropriate cognitive depth should maximize the confidence of the resulting action*.

### Technical Details

- **Base model:** Qwen2.5-7B
- **Training pipeline:** CoSFT → CoPO (RL)
- **Benchmarks:** ALFWorld (text-based household tasks), ScienceWorld (scientific reasoning tasks)
- **Confidence-aware advantage:** Instead of standard GRPO/PPO advantage, CogRouter reweights advantage by how much each cognitive level increases the confidence of the selected action. This creates a natural training signal: if level 2 produces low-confidence actions and level 4 produces high-confidence ones, the model learns to use level 4 when confidence matters.

### Research takeaway

**CogRouter proves that adaptive reasoning depth is not just possible — it's better.** A 7B model taught to reason adaptively achieves 82.3% success rate, outperforming GPT-4o (42.0%, +40.3 pp), OpenAI o3 (64.0%, +18.3 pp), and GRPO (68.3%, +14.0 pp), while using **62% fewer tokens**. This is a clean empirical demonstration that smarter allocation of reasoning compute beats uniformly high compute.

### Modern perspective (June 2026)

CogRouter (Feb 2026) and ARES (Mar 2026) form a dual breakthrough. CogRouter takes the harder path — training the agent itself to reason at different depths via RL. ARES takes the easier path — a lightweight router that predicts effort level per step (no agent modification). Both achieve 50-60% token reduction. This means the Adaptive ReAct Depth thesis direction is **highly validated** and the question is now which approach to build on.

## Related Papers

### Paper 1: ARES — Adaptive Reasoning Effort Selection

- **Authors:** Jingbo Yang, Bairu Hou, Wei Wei, Yujia Bao, Shiyu Chang
- **Link:** https://arxiv.org/abs/2603.07915 (Mar 2026)
- **Contribution:**
  - Lightweight router (small LM or MLP) predicts low/medium/high reasoning effort per step
  - Maps to provider `reasoning.effort` parameters (Anthropic, OpenAI)
  - Data generation pipeline: runs multiple trials at different effort levels to label minimal sufficient effort
  - Up to **52.7% reduction** in reasoning tokens across TAU-Bench, BrowseComp-Plus, WebArena
  - Router adds only ~10ms per step — negligible overhead
- **Relation to main paper:** Complementary approach. CogRouter trains the agent itself; ARES adds an external router. ARES is more practical for existing agent deployments (no agent retraining). CogRouter is more elegant but requires full training pipeline.

### Paper 2: DeepControl — Adaptive Information Control

- **Authors:** Siheng Xiong, Oguzhan Gungordu, James C. Kerce, Faramarz Fekri (Georgia Tech)
- **Link:** https://arxiv.org/abs/2602.01672 (Feb 2026)
- **Contribution:**
  - Controls **extent** (whether to continue retrieval) and **resolution** (how much detail to expose) of information acquisition
  - Novel **information utility** metric combining novelty and effectiveness
  - **Annealed control-forcing**: external control signals gradually removed so policy internalizes effective behavior
  - Outperforms Search-R1 by +9.4 points (Qwen2.5-7B) on 7 benchmarks
- **Relation to main paper:** Extends the adaptive allocation idea to *information retrieval* rather than *reasoning depth*. Together, CogRouter (reasoning depth) + DeepControl (information acquisition) + ARES (reasoning effort) form a unified picture: every dimension of agent resource allocation benefits from dynamic adaptation.

## Current Understanding

The Adaptive ReAct Depth thesis direction has been **strongly validated** by two independent papers published within one month of each other (Feb-Mar 2026):

| Dimension | Week 1 Thesis (June 6) | CogRouter (Feb 2026) | ARES (Mar 2026) |
|-----------|----------------------|---------------------|-----------------|
| Core idea | Dynamic Thought/Action based on uncertainty | 4-level cognitive hierarchy | Lightweight effort router |
| Training | Not specified | CoSFT + CoPO (RL) | Data labeling + router SFT |
| Token savings | Not quantified | 62% fewer tokens | Up to 52.7% fewer tokens |
| Performance | Not tested | 82.3% on ALFWorld (beats GPT-4o, o3) | Minimal degradation |
| Practicality | Conceptual | Requires full training | Plug-and-play |

The thesis is no longer speculative — it's now a validated research direction with concrete implementations.

**Revised thesis framing:** Instead of "adaptive Thought vs. Action," the more promising framing is *adaptive cognitive depth* — a continuum from instinctive response to strategic planning. The specific Thought/Action binary is a special case of a broader principle.

## Key Concepts

- **Cognitive depth hierarchy:** 4-level model (instinctive → routine → deliberate → strategic) grounded in ACT-R theory
- **Confidence-aware advantage:** Using action confidence as the signal for optimal reasoning depth — deeper reasoning is valuable only when it increases confidence
- **Anneal control-forcing:** Gradually removing external control signals so the policy internalizes effective behavior (from DeepControl)
- **Information utility:** State-dependent measure combining novelty and effectiveness of retrieved evidence
- **Reasoning token economy:** Hidden cost driver in agent workloads — output tokens inside thinking blocks billed at 4-8× input rates

## Open Questions

1. **Generalizability:** CogRouter was tested on ALFWorld and ScienceWorld (text-based simulated environments). Does it transfer to real-world agent tasks (web browsing, code generation, API orchestration)?
2. **Router vs. trained agent:** Is the ARES router approach (external lightweight classifier) or the CogRouter approach (train the agent itself) more practical for production deployment? This is an empirical question worth testing.
3. **Confidence calibration:** CogRouter's confidence-aware advantage depends on well-calibrated model confidence. How sensitive is the approach to miscalibrated probabilities (common in LLMs)?
4. **Combined adaptation:** Can reasoning depth adaptation (CogRouter/ARES) + information acquisition control (DeepControl) be combined for even greater efficiency?
5. **Multi-agent settings:** How does adaptive reasoning depth work in multi-agent settings where agents have different roles and capabilities?

## Possible Thesis Ideas

### Revised Priority 1: Adaptive Cognitive Depth for Real-World Agent Tasks

**Original:** Adaptive ReAct Depth — dynamic Thought vs. Action decisions.  
**Revised:** Build on CogRouter's cognitive hierarchy but extend to real-world agent environments (web browsing, API orchestration, coding). Key research questions:
- Does the 4-level hierarchy transfer from simulated to real environments?
- Can the lightweight ARES router approach achieve comparable results without agent retraining?
- Which agent steps benefit most from deep reasoning vs. routine execution?

**Novel angle not covered by existing work:** No existing paper studies adaptive reasoning depth in **tool-calling agents with long observation histories** (e.g., web agents that see 100+ page elements). The information overload problem makes adaptive depth especially critical for web agents.

### Priority 2: Unified Resource-Adaptive Agent Framework

Combine CogRouter's reasoning depth adaptation with DeepControl's information acquisition control into a single framework. The idea: an agent should adapt not just *how hard it thinks* but also *how much information it gathers*. Framework would have two control axes:
- **Reasoning depth:** instinctive → strategic (built on CogRouter/ARES)
- **Information budget:** minimal retrieval → exhaustive search (built on DeepControl)

This is a genuinely novel contribution since no existing work combines both dimensions.

### Priority 3: Practical ReAct Agent with Token Budget Control

Build a minimal open-source ReAct agent that implements ARES-style per-step effort routing using provider API controls (Anthropic's thinking budget, OpenAI's reasoning.effort). This would be:
- **Pragmatic:** No model training needed — just a lightweight router
- **Measurable:** Track tokens per task, success rate, cost per task
- **Publishable as a tech report or blog post** demonstrating practical cost optimization

## Next Step

Build the **Priority 3 implementation** (practical ReAct agent with token budget control) as the next research-lab session. This is the highest-velocity path: no model training, immediate measurable results, and directly connects to the open questions about router vs. trained agent approaches. The implementation would use the Hermes agent itself or a lightweight Python framework with DeepSeek API for reasoning effort control.

Also: update the thesis priorities based on today's findings. CogRouter + ARES validate the idea but also shift the research frontier. The most novel remaining contribution is the combined reasoning depth + information budget framework (Priority 2).
