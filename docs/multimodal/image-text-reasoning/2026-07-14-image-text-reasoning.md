# 2026-07-14 — Image-Text Reasoning (Day 2)

Course: Multimodal, VLA, and Robotics
Topic: Image-Text Reasoning
Stage: Day 2 — Program-Based Visual Reasoning Paradigm
Confidence: 0.38 -> 0.50

## Today's Question

Beyond end-to-end VLMs, how can program synthesis and code generation enable explicit, interpretable visual reasoning? And what are the key limitations — both perceptual and architectural — that bound current visual reasoning?

## Main Paper

### Metadata

- **Title:** ViperGPT: Visual Inference via Python Execution for Reasoning
- **Authors:** Dídac Surís, Sachit Menon, Carl Vondrick
- **Year:** 2023
- **Venue:** arXiv (2303.08128) / CVPR 2023
- **Link:** https://arxiv.org/abs/2303.08128

### Why this paper?

Last week's survey identified three main paradigms for visual reasoning: module-based (transparent, explicit), end-to-end VLM (opaque, scalable), and neuro-symbolic (hybrid, brittle). ViperGPT is the most impactful representative of the neuro-symbolic/program-based paradigm — it directly operationalizes the "explain-before-answer" philosophy by generating executable Python code. Understanding ViperGPT is essential for mapping this paradigm's strengths and weaknesses.

### Core Problem

Answering complex visual queries requires both visual perception (detecting objects, attributes, spatial relations) and reasoning (compositional, multi-step inference). End-to-end models fuse these two into a single black box, losing interpretability and struggling with compositional generalization. Prior program-based approaches (e.g., Neural Module Networks) required training both the program structure and the modules simultaneously, which was brittle and hard to scale.

### Main Idea

ViperGPT sidesteps the joint-learning problem entirely: use a pre-trained code-generation LLM (e.g., Codex) to synthesize Python code that composes pre-trained vision-and-language API functions into a complete program for answering a given query. The generated code is then executed deterministically — no additional training needed.

The key insight: **code generation replaces program learning**. The LLM doesn't learn to reason about images — it learns to reason about *code*, which is a much more structured domain. The visual modules (object detection, VQA, image captioning, etc.) are treated as black-box API functions that the code orchestrates.

### Technical Details

- **API design:** ViperGPT defines a typed API with functions like `find(object_name, image) -> List[Region]`, `is_true_condition(region_list, condition) -> bool`, `describe(region) -> str`. These functions encapsulate visual processing (pre-trained models like DETR, CLIP, BLIP).
- **Code generation:** Given a query + API spec, the LLM generates a Python function body. The prompt includes the API documentation with type signatures and examples.
- **Execution:** The generated code is executed with standard Python semantics — loops, conditionals, function calls, arithmetic, string operations.
- **Error recovery:** If execution raises an exception, ViperGPT re-prompts the LLM with the error message to auto-correct the program (zero-shot debugging).

### Experiments/Results

- **State-of-the-art on compositional VQA:** ViperGPT achieved SOTA on GQA (96.3% accuracy), outperforming both end-to-end models and earlier NMN approaches.
- **Out-of-distribution generalization:** Because the API modules are trained independently, ViperGPT generalizes to novel compositions better than end-to-end models that memorize training distributions.
- **Interpretability:** The generated Python code is a complete, human-readable reasoning trace — you can read the steps and see exactly which visual module was called with which arguments.

### Limitations

- **Bottlenecked by API quality:** If the underlying perception modules fail (e.g., object detector misses an object), the program logic is correct but the answer is wrong. ViperGPT inherits all limitations of its visual API components.
- **Limited to queries the API can express:** If a query requires a visual operation not in the API (e.g., optical flow, depth estimation), ViperGPT cannot answer it unless the API is extended.
- **Latency overhead:** LLM code generation + code execution + multiple API calls is slower than a single end-to-end forward pass.
- **No learning from execution feedback:** The code generator doesn't improve over time — each query is a fresh generation without learning from past successes/failures.

### Modern perspective (2026)

ViperGPT established a paradigm that later systems like **VisProg** (Gupta & Kembhavi, 2023) extended by adding step-by-step program generation with intermediate visualization. The program-based approach has since been incorporated into agent frameworks (e.g., multimodal agents that write and execute code to answer visual questions). However, the rise of strong end-to-end VLMs (GPT-4V, Gemini, Qwen2.5-VL) has closed the raw accuracy gap on many benchmarks. Today, the program-based approach's main value is in **interpretability**, **debugging capability**, and **guaranteed compositional correctness** — not raw benchmark numbers.

## Related Papers

### Paper 1 — Visual Generation Unlocks Human-Like Reasoning through Multimodal World Models (Wu et al., 2026)

- **Link:** https://arxiv.org/abs/2601.19834
- **Contribution:** Proposes a complementary reasoning paradigm: instead of decomposing reasoning into program steps (ViperGPT), use visual *generation* as a world model for reasoning. The model alternates between verbal reasoning and image generation — "interleaved CoT."
- **Relation to main paper:** Where ViperGPT excels at symbolic, compositional reasoning (count, compare, filter), the world-model approach targets *physical* and *spatial* reasoning where symbolic operations are insufficient (e.g., "what would happen if I moved this object here?"). They are complementary: ViperGPT for analytic reasoning, world-model generation for intuitive/physical reasoning.
- **Key finding:** On tasks that require physical world knowledge (VisWorld-Eval), interleaved CoT significantly outperforms purely verbal CoT. On formal/logical tasks, there's no advantage — consistent with the view that different reasoning types need different architectures.
- **Should deep-read later?** Yes — this paper represents an important third paradigm alongside module-based and end-to-end approaches.

### Paper 2 — BLINK: Multimodal Large Language Models Can See but Not Perceive (Fu et al., 2024)

- **Link:** https://arxiv.org/abs/2404.12390
- **Contribution:** A benchmark that exposes a critical bottleneck: even the best VLMs fail at core visual perception tasks that humans solve "within a blink." The benchmark covers 14 tasks (relative depth, visual correspondence, forensics detection, multi-view reasoning) with 3,807 multiple-choice questions.
- **Relation to main paper:** ViperGPT (and all program-based approaches) inherit the limitations of their underlying perception modules. BLINK quantifies this gap: humans achieve 95.7% accuracy, GPT-4V only 51.3% (barely above random at 38.1%). This means that even with flawless program logic, a ViperGPT-style system would be capped by the perception ceiling BLINK measures.
- **Why it matters:** It reveals that "perception" and "reasoning" are separate bottlenecks. Improving benchmarks by scaling VLMs alone won't solve the perception gap — specialized vision models (depth estimators, correspondences) still outperform multimodal LLMs on vision-specific tasks.
- **Should deep-read later?** Yes — the perception bottleneck is a critical research direction with direct thesis potential.

## Current Understanding

Image-text reasoning is not a single capability but a spectrum that spans at least three dimensions:

1. **Reasoning mode:** Analytic/compositional (count, filter, compare) vs. physical/intuitive (spatial, causal, counterfactual). Different architectures suit different modes — ViperGPT (program-based) excels at the former, world-model generation excels at the latter.

2. **Perception bottleneck:** Before any reasoning can happen, the model must perceive correctly. BLINK shows that even the most advanced VLMs have severe perception blind spots — they can "see" but not "perceive" in the human sense. This is a fundamental limitation that improvement in reasoning alone cannot fix.

3. **Interpretability-realism tradeoff:** Program-based approaches (ViperGPT) offer full interpretability but are bottlenecked by API completeness and perception module quality. End-to-end VLMs offer better raw perception but provide opaque reasoning traces. The world-model approach offers a middle ground — visual generation provides an interpretable intermediate representation.

The three paradigms align as follows:
- **Symbolic/program-based** (ViperGPT, VisProg, NMNs) → best for analytic, compositional tasks; interpretable; perception-bottlenecked
- **End-to-end VLM** (GPT-4V, Gemini, LLaVA-NeXT) → best raw performance; opaque; perception-bottlenecked but improving
- **Generation-as-world-model** (Wu et al., 2026) → best for physical/spatial reasoning; partially interpretable; depends on generative model quality

## Key Concepts

- **Program-based visual reasoning** — decomposing a visual query into executable code that orchestrates API calls to pre-trained vision modules
- **API-as-perception-interface** — encapsulating visual capabilities behind typed function signatures, so reasoning is done in code space, not visual space
- **Perception bottleneck** — the gap between human-level and VLM-level core visual perception (depth, correspondence, forensics) that caps reasoning accuracy
- **Interleaved CoT** — alternating between verbal reasoning tokens and generated images as intermediate world-model states
- **Visual superiority hypothesis** — for physical-world tasks, visual generation is a more natural world model than purely textual reasoning

## Open Questions

1. Can program-based reasoning (ViperGPT style) be made adaptive — can the system learn from execution traces to improve future code generation, or is it fundamentally stateless?
2. How do we integrate the three paradigms: can a single system dynamically choose between program-based, VLM-end-to-end, and generation-as-world-model depending on the query type?
3. Does the BLINK perception gap diminish at extreme VLM scales (e.g., 1T+ parameters) or is it a fundamental architectural limitation of language-augmented vision?
4. Can interleaved CoT be trained end-to-end, or does it require separate generation and reasoning modules?
5. What is the right interface between perception modules and reasoning modules — typed API functions (ViperGPT), latent embeddings (end-to-end VLM), or generated visual states (world-model)?

## Possible Thesis Ideas

1. **Unified Visual Reasoning Router** — a meta-system that classifies a visual query into reasoning type (analytic, physical, spatial, counterfactual) and routes to the optimal paradigm (program-based, end-to-end, or world-model), combining results where appropriate
2. **Perception-Aware Program Synthesis** — extend ViperGPT-style code generation to explicitly model perception module uncertainty (e.g., use confidence thresholds to decide when to defer or ask for clarification), making the system robust to the BLINK perception gap
3. **Interleaved CoT for Embodied Reasoning** — apply the world-model generation paradigm to robotics/VLA tasks where physical understanding is essential but current models rely on purely textual action reasoning
4. **Benchmark for Reasoning Paradigm Comparison** — a controlled benchmark that varies reasoning type (analytic, physical, spatial, counterfactual, analogical) and measures which paradigm works best, enabling systematic comparison beyond single-benchmark evaluations

## Next Step

Stay on image-text reasoning for Day 3. Next focus: end-to-end VLM reasoning capabilities in modern VLMs — specifically how GPT-4V, Gemini, and LLaVA-NeXT handle multi-step visual reasoning, and the emerging "visual reasoning with RL" direction (multimodal RLVR).

---
*Generated by AI Tour v3 — 2026-07-14*
