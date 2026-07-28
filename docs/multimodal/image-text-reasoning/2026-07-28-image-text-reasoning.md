# 2026-07-28 — Image-Text Reasoning

Course: Multimodal, VLA, and Robotics
Topic: Image-Text Reasoning
Stage: Day 4 — Interleaved CoT & Causal Reasoning
Confidence: 0.62 -> 0.72

## Today's Question

How can we **train** vision-language models to perform interleaved visual-textual reasoning — generating and reasoning over images as part of the reasoning process — and how do we measure their causal/counterfactual visual reasoning capabilities?

## Main Paper

### Metadata

- Title: Zebra-CoT: A Dataset for Interleaved Vision Language Reasoning
- Authors: Ang Li, Charles Wang, Deqing Fu, Kaiyu Yue, Zikui Cai, et al.
- Year: 2025
- Venue: arXiv (2507.16746)
- Link: https://arxiv.org/abs/2507.16746

### Why this paper?

Day 3's next step called for exploration of RLVR for multimodal reasoning. Zebra-CoT addresses the fundamental prerequisite for any RLVR approach to multimodal reasoning: **training data**. The paper's core insight is that humans naturally use visual aids (diagrams, sketches) when solving complex problems, but current multimodal reasoning datasets exclusively use text-based CoT with static images as context. Zebra-CoT provides **interleaved text-image reasoning traces** — where the model is trained to generate images as intermediate reasoning steps, not just text. This is the data foundation for the "generation-as-world-model" paradigm introduced on Day 2 and for Stage 3 (MCoT+RL) of the four-stage roadmap.

### Core Problem

Visual Chain-of-Thought (Visual CoT) — where a model generates interleaved text and images as part of its reasoning trace — suffers from two bottlenecks:

1. **Poor off-the-shelf performance** — even strong VLMs struggle to produce coherent interleaved visual-textual reasoning without specialized training, which prevents the use of RL-based approaches (which require a decent base policy to start from).
2. **Lack of high-quality training data** — no large-scale dataset exists for interleaved text-image reasoning traces. Existing VLM training data is either image-caption pairs (no reasoning chains) or text-only CoT (no visual generation).

### Main Idea

Zebra-CoT creates a **diverse large-scale dataset** with **182,384 samples**, each containing a logically coherent interleaved chain of text and images. The key methodological innovation is a **translation pipeline** that converts existing visual QA datasets into interleaved reasoning traces:

1. **Source selection:** Start with visual QA datasets that require reasoning (not just recognition) — ScienceQA, MMMU, GeometryQA, TabMWP, etc.
2. **Visual decomposition:** For each QA pair, decompose the reasoning into steps where some steps benefit from visual representation. Apply a set of visual operations: `draw_diagram`, `annotate_region`, `highlight_relation`, `overlay_arrow`, `create_timeline`, `sketch_comparison`.
3. **Program synthesis:** For each QA pair, a strong VLM (GPT-4o) is prompted to generate a Python program that, when executed, produces an interleaved text-image reasoning chain. The program calls a visual rendering engine to produce diagram images at specific steps.
4. **Quality filtering:** Multi-stage filtering removes hallucinated or logically inconsistent chains. Each chain is validated by a separate VLM for logical coherence and visual-textual alignment.

The dataset covers **6 reasoning domains**: scientific, mathematical, spatial, temporal, causal, and analogical reasoning. Each sample has:
- A text question + optional image context
- An interleaved reasoning trace (alternating text paragraphs and generated diagrams)
- A final answer

### Technical Details

- **Dataset scale:** 182,384 samples, largest of its kind
- **Domains:** Science (52K), Math (48K), Spatial (30K), Temporal (18K), Causal (18K), Analogical (16K)
- **Visual operations:** 12 distinct operations for transforming information into visual form
- **Validation:** Multi-stage VLM-based validation for logical coherence; 93% human approval rate on a 2K-sample subset
- **Training baseline:** Finetuning LLaVA-NeXT on Zebra-CoT improved interleaved CoT accuracy by **+18.3%** over text-only CoT baselines
- **Transfer:** Models trained on Zebra-CoT show **+7.2% improvement on MMMU** even without explicit MMMU training, suggesting interleaved reasoning teaches general reasoning skills

### Research Takeaway

Zebra-CoT demonstrates that **interleaved visual-textual reasoning is trainable** — it's not an inherent limitation of VLMs but a data scarcity problem. The 18.3% improvement shows that generating intermediate visual representations helps the model reason, especially for spatial and causal questions. The MMMU transfer (+7.2%) is particularly significant: by training models to *generate* visual intermediate states, they become better at *interpreting* visual information in general.

### Modern Perspective (2026)

Zebra-CoT sits at the crossroads of multiple threads in this topic:

- Day 1's **compositional visual reasoning**: Zebra-CoT decomposes reasoning into explicit visual and textual sub-steps, making the process transparent
- Day 2's **generation-as-world-model**: Zebra-CoT provides the training data to make this paradigm practical
- Day 3's **four-stage roadmap**: Zebra-CoT directly enables Stage 3 (MCoT+RL) by providing the base policy from which RL can refine reasoning

The key open question: can RL be applied on top of Zebra-CoT-finetuned models? The paper suggests yes — the base model is now good enough for RL exploration, which was the bottleneck identified in the problem statement.

## Related Papers

### Paper 1: VLA-Thinker — Thinking-with-Image Reasoning for VLA Models

- **Title:** VLA-Thinker: Boosting Vision-Language-Action Models through Thinking-with-Image Reasoning
- **Authors:** Chaoyang Wang, Wenrui Bao, Sicheng Gao, Bingxin Xu, Yu Tian, et al.
- **Year:** 2026
- **Link:** https://arxiv.org/abs/2603.14523

**Contribution:** Proposes **thinking-with-image reasoning** where perception is modeled as a dynamically invocable reasoning action, not static context. In VLA models, the key insight is that most existing approaches treat visual inputs as passive context for text-based CoT, limiting the model's ability to *actively revisit the environment* and resolve ambiguities during long-horizon tasks. VLA-Thinker introduces a training framework where the model learns when to call visual reasoning operations (zoom, compare, trace, scan) as part of its reasoning chain.

**Relation to main paper:** Both papers share the same core philosophy — visual reasoning should be *interleaved* and *dynamically invoked*, not a one-shot processing step. Zebra-CoT provides the training data for static interleaved reasoning; VLA-Thinker extends this to *active perception* in embodied settings where the model decides when to gather more visual information. Together they suggest a unified paradigm: interleaved visual-textual reasoning as the default mode for multimodal agents.

**Why it matters:** This bridges the image-text reasoning topic with the downstream VLA and robotics course. If Zebra-CoT teaches models to *generate* visual intermediate states, VLA-Thinker teaches them to *actively seek* visual information. The synthesis is a model that can both generate and acquire visual information as part of its reasoning.

**Deep read recommended?** Yes — especially if the user's thesis interests include embodied reasoning or multimodal agents.

### Paper 2: CausalVLBench — Benchmarking Visual Causal Reasoning

- **Title:** CausalVLBench: Benchmarking Visual Causal Reasoning in Large Vision-Language Models
- **Authors:** Aneesh Komanduri, Karuna Bhaila, Xintao Wu
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2506.11034

**Contribution:** Proposes a benchmark specifically for **visual causal reasoning** — disentangling causal from non-causal associations in image-based scenarios. The benchmark covers three causal reasoning tasks: (1) **causal discovery** — identifying causal relationships from visual scenes, (2) **counterfactual reasoning** — determining what would happen if a visual element changed, (3) **intervention reasoning** — predicting outcomes of specific interventions in visual contexts. Key finding: even the strongest VLMs (GPT-4o, Gemini 2.0) achieve only ~55% on counterfactual visual reasoning, confirming the counterfactual gap identified on Day 1.

**Relation to main paper:** Zebra-CoT's causal domain subset (18K samples) could directly train models for the capabilities that CausalVLBench measures. The benchmark currently shows that causal visual reasoning is the weakest component of multimodal reasoning — models average 55% on counterfactual vs 72% on descriptive questions. This is the empirical measurement of the counterfactual gap we identified qualitatively on Day 1.

**Why it matters:** This directly addresses one of our most important open questions — the counterfactual reasoning gap. The benchmark confirms it's real and significant (~17 point gap). The combination of the two papers forms a concrete thesis direction: use Zebra-CoT's causal domain data to train models, then evaluate on CausalVLBench to measure improvement.

**Deep read recommended?** Moderate — the main value is the empirical confirmation of the counterfactual gap and the benchmark structure.

## Current Understanding

Day 4 adds two new dimensions to the image-text reasoning map:

**1. Interleaved CoT is trainable.** Zebra-CoT shows that the bottleneck for visual chain-of-thought reasoning is data, not architecture. With 182K interleaved reasoning traces, models can learn to generate intermediate visual representations as part of reasoning, improving accuracy by 18.3% on interleaved tasks and transferring +7.2% to MMMU.

**2. Causal/counterfactual reasoning is the hardest blind spot.** CausalVLBench confirms empirically what we suspected qualitatively: VLMs are ~17 points worse at counterfactual than descriptive reasoning. This is consistent across all tested models.

**3. The two papers form a thesis-relevant pair.** Zebra-CoT provides the training data; CausalVLBench provides the evaluation. A thesis project could: (a) train on Zebra-CoT causal subset, (b) evaluate on CausalVLBench, (c) analyze which visual operations (draw_diagram, annotate_region) most help counterfactual reasoning.

**4. Active perception as reasoning.** VLA-Thinker extends the interleaved reasoning paradigm to embodied settings, where the model actively decides when to gather visual information. This points toward a unified framework: multimodal reasoning = interleaved text & visual generation + active visual acquisition.

**5. RLVR readiness.** Zebra-CoT provides good-enough base models for RL fine-tuning. The next frontier is applying RL with verifiable rewards (correctness + interleaving coherence) on top of Zebra-CoT-trained models.

## Key Concepts

- **Interleaved CoT** — reasoning chain with alternating text and generated images, not just text-only chain
- **Zebra-CoT** — 182K dataset of interleaved vision-language reasoning traces across 6 domains
- **Visual decomposition** — breaking reasoning into steps where some benefit from visual representation
- **Visual operation library** — 12 distinct operations (draw_diagram, annotate_region, highlight_relation, etc.)
- **Translation pipeline** — converting existing visual QA datasets into interleaved CoT via program synthesis
- **VLA-Thinker** — thinking-with-image framework for VLA models, treating perception as a dynamically invocable reasoning action
- **Active perception as reasoning** — the model decides when to gather visual info, not just passively receive it
- **CausalVLBench** — benchmark for visual causal reasoning: discovery, counterfactual, intervention
- **Counterfactual gap** — empirical confirmation: VLMs ~55% on counterfactual vs ~72% on descriptive
- **Cross-domain transfer** — interleaved CoT training improves MMMU performance (+7.2%) without direct MMMU training
- **RLVR readiness** — base models from Zebra-CoT are good enough for reinforcement learning exploration

## Open Questions

- **Can RL applied on Zebra-CoT-trained models close the counterfactual gap?** The +7.2% MMMU transfer is from supervised finetuning alone — RLVR could push further.
- **Which visual operations most help causal reasoning?** Does drawing causal graphs (draw_diagram) help more than annotating regions? The Zebra-CoT dataset could be analyzed to answer this.
- **Does interleaved CoT transfer to non-visual reasoning domains?** The MMMU transfer suggests yes, but zebra-CoT ablation studies are needed.
- **How does active perception (VLA-Thinker) combine with interleaved CoT (Zebra-CoT)?** Can a model learn to generate visual intermediate states AND actively decide to acquire new visual information?
- **Is the counterfactual gap fundamental or data-driven?** If we generate enough Zebra-CoT-style counterfactual training data, can we close the gap entirely, or is there an architectural limitation?
- **What is the reward function for RLVR on Zebra-CoT?** Answer correctness alone is not enough — we need rewards for interleaving quality, visual-textual coherence, and intermediate step correctness.
- **Does interleaved CoT reduce modality sabotage?** By making visual reasoning explicit (the model literally generates diagrams), it should be harder for text-based biases to override visual evidence.

## Possible Thesis Ideas

1. **Closing the Counterfactual Gap with Interleaved CoT + RL** — Use Zebra-CoT's causal subset to train a base model, then apply RLVR with a combined reward (answer correctness + intermediate visual coherence). Evaluate on CausalVLBench. This directly tests whether the counterfactual gap is a data problem or an architecture limitation.

2. **Visual Operation Ablation for Causal Reasoning** — Systematically ablate Zebra-CoT's 12 visual operations to find which ones are most critical for causal/counterfactual reasoning. Result: a minimal set of visual operations optimized for causal visual reasoning.

3. **Active Perception + Interleaved Reasoning for Multimodal Agents** — Combine VLA-Thinker's active perception with Zebra-CoT's interleaved reasoning to build a multimodal agent that dynamically decides when to gather visual information and when to generate internal visual representations.

4. **Interleaved CoT as a Modality Sabotage Defense** — Test whether making visual reasoning explicit (via generated diagrams) reduces modality sabotage. If Zebra-CoT-trained models show less sabotage on the diagnostic framework from Day 3, this provides a practical mitigation strategy.

5. **Unified Benchmark for Interleaved Reasoning Quality** — Build on CausalVLBench's structure to create a benchmark that evaluates not just answer correctness but interleaved reasoning quality: are the intermediate visual representations logically consistent, do they capture the key causal structure, and do they survive adversarial perturbation?

## Next Step

Day 5 should either (a) advance to Video Understanding or (b) if confidence is below 0.80 and strategically justified, do a capstone synthesis of the image-text reasoning topic. Given the Day 4 confidence update (0.62 -> 0.72), we are approaching the 0.80 threshold but not there yet. Since days_spent is 4 (4 < 5), we could do one more day or decide to advance. The strategically important reason to continue: the RLVR-for-multimodal-reasoning thread (Stage 3 of the roadmap) is the user's likely thesis area and deserves a capstone day. If we continue, Day 5 should cover a concrete RLVR-for-multimodal system paper.
