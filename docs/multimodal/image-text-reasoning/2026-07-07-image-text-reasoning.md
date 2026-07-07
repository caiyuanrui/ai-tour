# 2026-07-07 — Image-Text Reasoning

Course: Multimodal, VLA, and Robotics
Topic: Image-Text Reasoning
Stage: Day 1 — Survey
Confidence: 0.00 -> 0.38

## Today's Question

How do models reason over visual and textual information? What are the main paradigms, benchmarks, and open problems in compositional visual reasoning?

## Main Paper

### Metadata

- Title: Explain Before You Answer: A Survey on Compositional Visual Reasoning
- Authors: Fucai Ke, Joy Hsu, Zhixi Cai, Zixian Ma, Xin Zheng, Xindi Wu, Sukai Huang, Weiqing Wang, Pari Delir Haghighi, Gholamreza Haffari, Ranjay Krishna, Jiajun Wu, Hamid Rezatofighi
- Year: 2025
- Venue: arXiv
- Link: https://arxiv.org/abs/2508.17298

### Why this paper?

This is a comprehensive modern survey on compositional visual reasoning — the exact core of today's topic. For Day 1, a survey gives the map before the territory, identifying paradigms, benchmarks, and open problems. It is recent (August 2025), covers both classical and modern approaches, and explicitly categorizes the field.

### Core Problem

Compositional visual reasoning asks models to **decompose visual scenes, ground intermediate concepts, and perform multi-step logical inference** — going beyond surface-level pattern matching. Unlike standard VQA (which can be solved by exploiting dataset biases or using purely textual shortcuts), compositional reasoning requires systematic understanding of objects, relations, spatial arrangements, and their interplay with natural language questions.

### Main Idea

The survey organizes the field into four major axes:

1. **Module-Based Architectures** — decompose the reasoning task into interpretable sub-tasks (e.g., Neural Module Networks, NMNs), each handled by a dedicated, differentiable module. The question is parsed into a program, which is then executed step-by-step over visual representations. This line is characterized by explicit compositionality and transparency.

2. **End-to-End Transformers** — large pretrained models (VLMs like LLaVA, Qwen2.5-VL, InternVL) that perform reasoning implicitly within the transformer's autoregressive decoding. No explicit decomposition; reasoning emerges from pretraining at scale. The trade-off is opaque reasoning but strong performance on standard benchmarks.

3. **Neuro-Symbolic Approaches** — hybrid systems combining neural perception (object detection, segmentation) with symbolic reasoning (logical inference, constraint solving, probabilistic programming). These aim for the best of both worlds: neural flexibility for perception + symbolic rigor for reasoning.

4. **Benchmarks and Evaluation** — the survey catalogs 15+ benchmarks (GQA, CLEVR, NLVR, VCR, SNLI-VE, LogicVista, etc.), categorizing them by reasoning type (spatial, logical, causal, analogical, numerical) and the specific compositional skills they test.

The survey also identifies a crucial **trustworthiness gap**: most VLMs claim to "reason" but their reasoning processes are opaque. The **"Explain Before You Answer"** philosophy argues that models should produce intermediate explanations before final answers — a property that module-based and neuro-symbolic approaches can guarantee.

### Technical Details

The survey introduces a taxonomy distinguishing:

- **Architectural compositionality** — built into model design (NMNs, ViLT, ALBEF)
- **Functional compositionality** — achieved via modular training objectives (CLIP, BLIP-2)
- **In-context compositionality** — emergent via CoT prompting or visual program induction (ViperGPT, VisProg)
- **Causal compositionality** — models that learn causal structure from visual-linguistic data (CausalVLR)

For each axis, it provides:
- Representative papers with performance tables
- Key failure modes (shortcut learning, language priors, visual grounding confounds)
- Cross-benchmark comparison showing that no single approach dominates all reasoning types

### Research takeaway

Image-text reasoning is not a monolithic capability. The survey reveals **at least 6 distinct reasoning types** (spatial, relational, logical, causal, numerical, analogical) that require different architectural choices. Module-based approaches remain the gold standard for transparency and interpretability, while end-to-end VLMs dominate raw benchmark performance but are near-impossible to debug.

The most active research direction combines **neural scene representation** (e.g., slot attention, object-centric learning) with **symbolic program execution** — a route that neither "pure end-to-end" nor "pure symbolic" camps can fully claim.

### Modern perspective

Since this survey's publication (Aug 2025), several developments are reshaping the field:

1. **Multi-step CoT for VLMs** — newer work on multimodal chain-of-thought (e.g., MMCoT, multimodal ReAct) shows that even end-to-end models benefit from explicit intermediate reasoning steps, partially closing the transparency gap.
2. **Visual generation as reasoning** — a surprising new paradigm where models "generate to reason" (e.g., Visual Generation Unlocks Human-Like Reasoning, Wu et al. 2026), using image generation as an internal world model.
3. **RLVR for multimodal reasoning** — reinforcement learning with verifiable rewards is being applied to visual reasoning tasks, potentially enabling self-improving multimodal reasoners.

## Related Papers

### Paper 1

- Title: GQA: A New Dataset for Real-World Visual Reasoning and Compositional Question Answering
- Authors: Drew A. Hudson, Christopher D. Manning
- Year: 2019
- Venue: CVPR 2019
- Link: https://arxiv.org/abs/1902.09506

**Contribution:** GQA addresses key shortcomings of previous VQA datasets (VQA v2, CLEVR) by using **scene graph structures** to generate 22M diverse, balanced, and compositional questions. Questions are generated via functional programs, enabling precise control over reasoning type (e.g., "what color is the cat?" → filter(attribute) + locate(object)).

**Relation to main paper:** GQA is a foundational benchmark extensively analyzed in the survey. It embodies the **module-based** evaluation paradigm — each question can be decomposed into a program, making it the ideal testbed for evaluating compositional reasoning.

**Why it matters:** GQA revealed that standard VQA models (2017-era) struggled dramatically when dataset biases were removed — accuracy dropped from ~65% to ~45% on balanced questions. This directly motivated the "Explain Before You Answer" philosophy. GQA's program-based question generation remains the gold standard for controlled reasoning evaluation.

**Deep read later:** Yes — especially the scene graph construction methodology and the specific failure modes GQA exposes.

### Paper 2

- Title: LogicVista: Multimodal LLM Logical Reasoning Benchmark in Visual Contexts
- Authors: Yijia Xiao, Edward Sun, Tianyu Liu, Wei Wang
- Year: 2024
- Venue: arXiv
- Link: https://arxiv.org/abs/2407.04973

**Contribution:** LogicVista introduces a unified multimodal benchmark covering **5 logical reasoning types**: deductive, inductive, abductive, analogical, and counterfactual. It evaluates MLLMs across 448 manually curated visual-logical problems. Key finding: even GPT-4V achieves only ~65% accuracy, with counterfactual and analogical reasoning being particularly weak (~45-50%).

**Relation to main paper:** LogicVista operationalizes the survey's call for **fine-grained reasoning evaluation**. While the survey catalogs benchmarks, LogicVista specifically targets the gap the survey identifies — current benchmarks test too few distinct reasoning types.

**Why it matters:** The finding that deductive reasoning is strongest (often >70%) while counterfactual and analogical reasoning is near-chance (~50%) reveals a fundamental asymmetry in VLMs' reasoning capabilities. This suggests current pretraining (mostly on descriptive image-text data) does not build robust counterfactual understanding.

**Deep read later:** Yes — especially the counterfactual/analogical results and the test data construction methodology.

## Current Understanding

Image-text reasoning spans multiple distinct capabilities that current models address unevenly. The field is organized around three architectural paradigms:

1. **Module-based (transparent, explicit)** — decomposes reasoning into interpretable sub-steps; strong on controlled benchmarks (CLEVR, GQA) but harder to scale to real-world images.
2. **End-to-end VLM (opaque, scalable)** — dominates raw performance but cannot explain its reasoning; prone to shortcut learning and language-prior exploitation.
3. **Neuro-symbolic (hybrid, brittle)** — strongest in principle (neural perception + symbolic logic) but difficult to train end-to-end and sensitive to perception errors.

Evaluation is similarly fragmented — no single benchmark tests all reasoning types. The field lacks:
- A unified reasoning taxonomy with standardized evaluation
- Methods to verify that models genuinely "reason" rather than pattern-match
- Training paradigms that explicitly target reasoning weaknesses (especially counterfactual and analogical)

## Key Concepts

- **Compositional visual reasoning** — decomposing a visual-linguistic problem into sub-problems and combining intermediate results
- **Module-based reasoning** — NMNs, ViperGPT, VisProg where question is parsed into executable program
- **Neural Module Networks (NMNs)** — differentiable modules that perform specific operations (attend, compare, count, filter) over visual features
- **Scene graphs** — structured representation of objects, attributes, and relations in an image; used for controlled question generation (GQA)
- **Shortcut learning / language priors** — models using text-only patterns (e.g., "Is there a ... → yes") instead of genuine visual reasoning
- **Counterfactual reasoning gap** — VLMs' systematic weakness in "what if" scenarios vs. descriptive or spatial reasoning
- **Explain-before-answer philosophy** — intermediate explanations should be required, not optional, for trustworthy multimodal reasoning

## Open Questions

1. Can a single architecture handle all reasoning types (spatial, logical, causal, analogical, counterfactual), or do these require fundamentally different approaches?
2. How much of VLMs' reasoning capability is genuine composition vs. memorized patterns from pretraining data?
3. What training data would improve counterfactual and analogical reasoning — do we need synthetic program-generated data, or can it emerge from scale?
4. Can RLVR (reinforcement learning with verifiable rewards) be effectively applied to multimodal reasoning, and what reward functions capture compositional correctness?
5. How do we measure reasoning - the gap between "getting the right answer" and "getting it for the right reasons" remains unsolved.
6. Is "generation-as-reasoning" (using image generation as a world model) a separate paradigm or a special case of neuro-symbolic approaches?

## Possible Thesis Ideas

1. **Reasoning-Aware VLM Training** — design a training objective that explicitly rewards intermediate reasoning consistency (not just final answer accuracy) using program-synthetic question-answer pairs. Extend the GQA methodology to modern VLM training.

2. **Unified Visual Reasoning Benchmark** — build a benchmark that normalizes across reasoning types with controllable difficulty, enabling apples-to-apples comparison of module-based, end-to-end, and neuro-symbolic approaches. Could extend LogicVista with program-grounded ground truth for every reasoning step.

3. **Counterfactual Visual Training** — develop a data generation pipeline (using scene graph manipulation + image editing) that produces counterfactual visual reasoning examples, then evaluate whether training on these data closes the counterfactual reasoning gap.

4. **Multimodal RLVR for Compositional Reasoning** — apply reinforcement learning with verifiable rewards where the reward is not just answer correctness but program-step correctness, directly incentivizing compositional reasoning chains.

## Next Step

Day 1 complete — the survey has built the map. Day 2 should dive into a specific paradigm (likely module-based reasoning: ViperGPT or VisProg) to understand the technical execution of explicit visual reasoning programs.
