# 2026-07-28 — Image-Text Reasoning Capstone

Course: Multimodal, VLA, and Robotics
Topic: Image-Text Reasoning
Stage: Capstone (Day 5)
Confidence: 0.72 → 0.82

## Topic Map

```
VLM Pretraining (completed)
└── Image-Text Reasoning (completed, 5d / 15 papers / conf 0.82)
    └── Video Understanding (NEXT →)
```

## Journey Recap

Over 5 days, we built a map of image-text reasoning across 15 papers:

### Day 1 — Framing the Landscape
**Survey**: Compositional Visual Reasoning (explain-before-answer philosophy)
**Papers**: GQA, LogicVista
**Insight**: Three paradigms — module-based (transparent), end-to-end (scalable but opaque), neuro-symbolic (powerful but brittle)

### Day 2 — Program-Based Reasoning
**Main**: ViperGPT (visual inference via Python execution)
**Related**: Visual Generation as World Model, BLINK (perception bottleneck)
**Insight**: API-as-perception-interface — encapsulate vision behind typed function signatures; the real bottleneck is perception quality, not reasoning logic

### Day 3 — Measurement & Diagnosis
**Main**: MMMU (massive multi-discipline benchmark)
**Related**: Modality Sabotage diagnostic framework, Multimodal Reasoning survey
**Insight**: Even advanced VLMs are at ~60% on college-level questions; modality sabotage is a real systemic failure mode where overconfident unimodal errors corrupt fused reasoning

### Day 4 — Interleaved CoT + Empirical Gaps
**Main**: Zebra-CoT (182K interleaved VLM reasoning dataset)
**Related**: VLA-Thinker (active perception), CausalVLBench (counterfactual benchmark)
**Insight**: Interleaved CoT is **trainable** — bottleneck is data, not architecture; counterfactual gap empirically confirmed at ~17 points (55% vs 72%)

### Day 5 — Capstone Synthesis (Today)
Synthesizing all four days into a coherent picture, identifying cross-cutting patterns, and mapping the frontier for thesis-level work.

---

## Cross-Cutting Patterns

### 1. The Three-Paradigm Tradeoff Hasn't Converged

| Paradigm | Strength | Weakness | Representative |
|----------|----------|----------|----------------|
| Module-based / Program | Transparent, verifiable | Brittle, hard to scale | ViperGPT, VisProg |
| End-to-end VLM | Scalable, emergent | Opaque, shortcut-prone | LLaVA, Qwen-VL |
| Interleaved / World Model | Eloquent, human-like | Data-hungry, unproven at scale | Zebra-CoT, Visual Gen World Model |

**Key insight**: These are not competitors — they operate at different points on the transparency-scalability frontier. The most promising direction is a **hybrid** that uses program-based decomposition for the reasoning skeleton and end-to-end VLM + interleaved generation for the perception and world-model layers.

### 2. The Perception Bottleneck is Real and Capstone-Limiting

BLINK (Fu et al. 2024) showed that VLMs are systematically weak at "simple" perception tasks: depth estimation, correspondence matching, forensic image analysis. This perception gap caps all downstream reasoning accuracy. **The bottleneck is not reasoning — it's seeing.**

Implication: Improving the perceptual backbone (resolution, fine-grained features, temporal coherence) may have a larger impact on reasoning accuracy than any reasoning-specific architectural innovation.

### 3. Counterfactual Reasoning is the Hardest Subproblem

Across all benchmarks:
- Descriptive reasoning: ~72% on VLMs
- Spatial reasoning: ~65%
- Counterfactual reasoning: ~55%

The ~17 point counterfactual gap is persistent and does not shrink at scale. Two competing hypotheses:
1. **Data-driven**: counterfactual training data is scarce and synthetically generated counterfactuals don't capture real-world causal structure
2. **Fundamental**: the VLM architecture (joint embedding of vision + language) cannot truly represent causal counterfactuals — they require a world model, not just pattern matching

These can be tested: if RLVR on Zebra-CoT (interleaved with causal visual generation) closes the gap, hypothesis 1 wins.

### 4. The Modality Sabotage Framework Generalizes

Modality sabotage (Zhang et al. 2025) was demonstrated on emotion recognition but the mechanism is general: any time a confident unimodal error enters the fusion layer, it can corrupt the multimodal result. This maps to:
- **VQA**: visual hallucination overrides correct text reasoning
- **Multimodal agents**: vision misperception causes wrong tool selection
- **Video understanding**: single-frame misclassification corrupts temporal reasoning

The diagnostic framework (treating each modality as an agent) is a useful design pattern for any multimodal system.

---

## Frontier Directions

### Near-term (1-2 years, high certainty)

1. **RLVR for Multimodal Reasoning**
   - Zebra-CoT provides the base model
   - CausalVLBench provides the evaluation
   - The reward function problem is open but tractable
   - Expected impact: +8-12 points on counterfactual reasoning

2. **Active Perception for Reasoning**
   - VLA-Thinker showed dynamic perception invocation improves VLA performance
   - Extending to general multimodal reasoning: the model decides when to zoom, re-read, or generate auxiliary visual information

3. **Unified Benchmark for Reasoning Process**
   - Current benchmarks (MMMU, CausalVLBench, GQA) measure answer correctness
   - Missing: benchmark that rewards intermediate reasoning quality, not just final accuracy
   - Needed for: distinguishing genuine reasoning from memorized patterns

### Medium-term (2-4 years, moderately certain)

4. **End-to-End Interleaved Reasoning**
   - Train a model from scratch on interleaved text+image sequences
   - Not just generating images mid-chain, but treating visual generation as a differentiable reasoning step
   - This would unify the three paradigms into one

5. **Causal World Models for Reasoning**
   - Move from pattern-based VLM reasoning to actual causal reasoning using learned world models
   - World model provides the "what if" capability that counterfactual questions demand
   - Intersection: multimodal reasoning + world models + RL

### Long-term (5+ years, speculative)

6. **Native Spatiotemporal Reasoning**
   - Models trained on continuous video streams (not discrete frames)
   - Reasoning happens in a unified space-time embedding, not post-hoc text
   - This may require fundamentally new architectures beyond transformers

---

## Key Concepts Accumulated

- Compositional visual reasoning
- Neural Module Networks
- Scene graphs and GQA
- Shortcut learning / language priors
- Counterfactual reasoning gap (~17 points)
- Explain-before-answer
- Program-based visual reasoning (ViperGPT)
- API-as-perception-interface
- Perception bottleneck (BLINK)
- Interleaved CoT (Zebra-CoT)
- Visual superiority hypothesis
- MMMU benchmark
- Discipline variance in multimodal reasoning
- Modality sabotage diagnostic framework
- Active perception (VLA-Thinker)
- CausalVLBench
- Visual operation library (12 operations)
- RLVR readiness for multimodal reasoning
- Three-way paradigm comparison

## Open Questions Remaining

- Is the counterfactual gap fundamental or data-driven? (the single most important open question)
- Can a single architecture handle all reasoning types?
- Does interleaved CoT reduce modality sabotage by making visual reasoning explicit?
- What is the weak link: perception (BLINK), fusion (sabotage), or reasoning (CoT quality)?
- Can RLVR on Zebra-CoT + CausalVLBench close the counterfactual gap?

## Possible Thesis Ideas (Refined)

1. **RLVR for Closing the Counterfactual Gap** — Train on Zebra-CoT causal subset with a process-aware reward, evaluate on CausalVLBench. Most concrete and high-impact near-term thesis.

2. **Unified Visual Reasoning Router** — Meta-system that classifies a query by reasoning type (descriptive, spatial, causal, counterfactual) and routes to the optimal paradigm. Addresses the three-paradigm tradeoff directly.

3. **Modality Sabotage Defense via Interleaved CoT** — Hypothesis: explicit visual generation in the reasoning chain makes modality contributions traceable, reducing sabotage risk. Testable: compare sabotage rate with vs. without interleaved generation.

## Next Step

**Topic completed.** 🎉

Transitioning to **Video Understanding** — next Tuesday's multimodal slot.

Video understanding connects naturally: static image-text reasoning tools (per-region grounding, interleaved CoT) should extend to temporal sequences. The first question: what new representations does time introduce?
