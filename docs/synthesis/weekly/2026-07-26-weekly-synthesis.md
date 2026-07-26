# 2026-07-26 — Weekly Synthesis

## This Week's Readings

- Agents / Planning: Two Distinct Planning Abilities (Operational Reasoning vs Structural Enumeration)
- Multimodal / Image-Text Reasoning: MMMU Benchmark & Modality Sabotage Diagnosis
- LLM Systems / KV Cache: Make Each Token Count — KV Cache Eviction with Attention Redistribution
- Generative Models / Score-Based Models: Score Models Learn Manifold-Like Structures with Constrained Mixing
- Agents / Memory: Are We Ready For An Agent-Native Memory System?
- Research Lab / Project Planning: TALE, Token Budgets Catalog, Token-Efficient RL — P3v2 Architecture Design

## Major Themes

- Structural enumeration bottleneck — Huang (2026) reveals that LLM planning has two separable competencies; structural enumeration (goal reachability) resists scaling and CoT, while operational reasoning (local action choice) improves normally. This is the most impactful paper of the week — it reframes the planning debate and suggests targeted interventions for the hard part.
- Two-component score field theory matures — Wenliang & Moran (2023) shows score models learn a conservative off-manifold denoising component + a non-conservative in-manifold mixing component. Convergent theoretical guarantees (Yakovlev 2025) and weighting function analysis (Zhang 2025) now provide a complete five-layer picture of score-based models.
- Agent memory as a systems stack — The Zhou (2026) survey decomposes memory into 4 modules (representation, extraction, retrieval, maintenance), showing that no single architecture dominates and that workload-memory alignment is the central design principle. This provides the framework for the newly-started Memory topic.
- KV cache eviction joins quantization as a mature pillar — Make Each Token Count shifts eviction from selection-centric to training-centric (eviction-aware finetuning). EVICPRESS shows compression and eviction must be jointly optimized. StreamingLLM's attention sink phenomenon provides foundation.
- Two-layer budget architecture for P3v2 — TALE (prompt-level budgets, 93% GSM8K at 37% cost) + Token Budgets catalog (63 production incidents) validate P3's direction. The architecture now has both prompt-level hints and system-level enforcement.
- Modality sabotage as diagnostic failure mode — Zhang (2025) introduces the concept of one modality's error overriding others in multimodal reasoning. Combined with MMMU's benchmark framework, this provides a two-layer diagnosis: what models get wrong (MMMU) and why (modality sabotage).

## Cross-Course Connections

- Structural enumeration bottleneck (Agents/Planning) ↔ Attention redistribution in KV cache (LLM Systems) — both involve structural dependencies that resist easy optimization. The planning bottleneck is about reasoning about goal structures; the KV cache redistribution is about attention structures after token removal. Both require training-level intervention, not just architecture changes.
- Two-component score field (Generative/Score Models) ↔ Modality sabotage diagnostic (Multimodal) — both reveal that generative/reasoning processes have hidden internal structure (conservative vs non-conservative components; dominant vs suppressed modalities) that standard metrics (likelihood, accuracy) fail to capture.
- TALE validation (Research Lab) ↔ Agent memory architecture (Agents/Memory) — TALE's lightweight classifier for token budgets could be integrated with memory's retrieval/routing module: routing decisions can use budget predictions from a classifier, and memory maintenance could be budget-aware.
- Eviction-aware training (LLM Systems/KV Cache) ↔ Agent-native memory maintenance (Agents/Memory) — both deal with the problem of what to keep and what to discard. KV cache eviction retrains the model to work with sparse attention; agent memory maintenance needs similar robustness — the agent should work well when memory is partially consolidated or pruned.
- Structural enumeration ↔ Score-based model mixing — The non-conservative in-manifold mixing of score models is analogous to structural operations: both operate on the 'inner space' of the data/task and resist standard optimization approaches.

## Contradictions and Tensions

- Implicit vs explicit planning: Dong (2025) found LLMs encode future outputs in hidden representations (implicit planning), but Huang (2026) found LLMs are structurally enumeration-blind even at 671B scale. If implicit structural awareness exists, why doesn't it surface in explicit structural enumeration tasks?
- Memory generalization vs specialization: The Zhou (2026) survey argues for task-adaptive memory design, while Pink (2025) argues episodic memory is the universal missing piece. Is the answer a family of specialized architectures or a single episodic-first architecture?
- Score model likelihood-quality gap: Zhang (2025) shows heuristic weighting's lower variance helps training, but the gap between likelihood and sample quality remains unexplained — suggesting the training objective itself may be insufficient despite optimal weighting.

## Open Problems

- Structural enumeration in LLMs — the single hardest open problem identified this week. How to train or architect LLMs to reason about global goal reachability, not just local action applicability? Possible approaches: process reward models for structural properties, explicit verifier modules, or probing-to-explicit transfer.
- Modality sabotage measurement at scale — the diagnostic framework exists for emotion recognition but hasn't been extended to agent environments, video understanding, or large-scale VQA. The interaction between sabotage and scaling is unknown.
- Three-way KV cache management — jointly optimizing quantization, eviction, and offloading is unsolved. Each interaction (quantization-eviction, eviction-offloading, quantization-offloading) changes the cost structure of the others.
- Workload-memory alignment as a learning problem — can a system learn which memory architecture to use based on task description and run-time signals, rather than being manually configured?
- Budget-aware agent evaluation methodology — most agent papers report a single accuracy number. The field needs cost-decomposed, per-budget, per-competency evaluation that separates routing, reasoning, and tool costs.

## Possible Thesis Ideas

### 1. Structural Enumeration via Process Reward Models

- **Problem:** LLMs cannot reliably reason about goal reachability (structural enumeration), even at 671B scale
- **Why it matters:** This is the single biggest bottleneck to reliable long-horizon planning
- **Method:** Train a PRM specifically to score structural properties of partial plans, then use as verifier during CoT or as RL training signal
- **Background:** Huang 2026 (two planning abilities), Chasing Progress 2024, PRM literature
- **Evaluation:** ACPBench-Hard structural enumeration subset, PlanBench, structural validity metrics
- **Risk:** Medium — structural enumeration may be fundamentally harder for transformer architectures
- **Next step:** Deep-read Huang 2026, replicate IRT analysis, design a PRM for structural planning
- **Confidence:** 3/5

### 2. Modality Sabotage in Multi-Step Agent Environments

- **Problem:** Modality sabotage diagnosis only exists for static VQA; agents with multiple modalities over multiple steps have far more sabotage surfaces
- **Why it matters:** Multimodal agents are the next frontier; undiagnosed sabotage cascades over agent steps
- **Method:** Extend diagnostic-layer framework to agent trajectories — treat each tool output type as a "modality"
- **Background:** Zhang 2025 (modality sabotage), MMMU, ViperGPT
- **Evaluation:** Web agent benchmarks with visual perception; compare models with/without sabotage-aware routing
- **Risk:** Low-Medium — proven concept, naturally defined extension
- **Next step:** Deep-read sabotage paper, design web agent experiment with instrumented tool outputs
- **Confidence:** 4/5

### 3. Three-Way Unified KV Cache Manager

- **Problem:** Quantization, eviction, and offloading studied separately but interactions dominate practical trade-offs
- **Why it matters:** 1M+ token contexts are becoming common; joint management essential
- **Method:** Learned policy jointly deciding: which tokens to quantize (bit-width), evict, or offload — optimizing SLO-constrained goodput
- **Background:** KIVI, Make Each Token Count, EVICPRESS, KVSwap
- **Evaluation:** Simulate across workload types (long-doc, multi-turn agent, streaming) and GPU tiers
- **Risk:** High — large optimization space; may not generalize across models/hardware
- **Next step:** Build offline simulation environment for evaluating arbitrary mechanism combinations
- **Confidence:** 2/5

## What To Read Next

- Deep-read Huang 2026 (ACPBench-Hard IRT analysis) to understand structural enumeration metrics
- Read the full Wenliang & Moran 2023 paper on score-based manifold learning for the geometic analysis details
- Read Zhou 2026 agent memory survey full paper — the 4-module framework is useful for mapping the topic
- Explore offloading literature (KVSwap, FlexGen, InfiniGen) as Day 3 of KV Cache topic
- For multimodal — Day 4 should be RLVR for multimodal reasoning (Stage 3 of the 4-stage roadmap)

## Next Week Adjustments

- Memory topic on Monday (agents) — continue with topic-structured memory (Infini Memory) and episodic vs semantic memory systems
- Generative Models — Score-Based Models confidence at 0.78, one more day may advance to 0.80+ to complete the topic. Plan Day 5 (capstone/synthesis)
- LLM Systems / KV Cache — Day 3 on offloading completes the tripartite view; consider advancing or capstoning
- Multimodal / Image-Text Reasoning — Day 4 on RLVR for multimodal reasoning
- Research Lab — implementation-notes topic is now active (for P3v2 coding)
