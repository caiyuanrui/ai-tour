# 2026-07-21 — Image-Text Reasoning

Course: Multimodal, VLA, and Robotics
Topic: Image-Text Reasoning
Stage: Day 3 — Benchmarking & Diagnosis
Confidence: 0.50 -> 0.62

## Today's Question

How do we *measure* genuine multimodal reasoning — and when does one modality override or sabotage the reasoning process?

## Main Paper

### Metadata

- Title: MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI
- Authors: Xiang Yue, Yuansheng Ni, Kai Zhang, Tianyu Zheng, Ruoqi Liu, Ge Zhang, Samuel Stevens, Dongfu Jiang, Weiming Ren, Yuxuan Sun, Cong Wei, Botao Yu, Ruibin Yuan, Renliang Sun, Ming Yin, Boyuan Zheng, Zhenzhu Yang, Yibo Liu, Wenhao Huang, Huan Sun, Yu Su, Wenhu Chen
- Year: 2023
- Venue: arXiv (2311.16502); CVPR 2024
- Link: https://arxiv.org/abs/2311.16502

### Why this paper?

After two days covering compositional reasoning paradigms (module-based, program-based, generation-as-world-model) and the perception bottleneck (BLINK), the next natural question is: **how do we benchmark multimodal reasoning holistically?** MMMU is the most influential benchmark for this purpose — 11.5K college-level multimodal questions across 6 disciplines, covering 30 subjects and 183 subfields. It revealed that even GPT-4V and Gemini Ultra only achieve 56% and 59%, setting the standard for measuring genuine reasoning capability.

### Core Problem

Existing multimodal benchmarks (VQA, GQA, NLVR2, OK-VQA) focus on visual perception tasks with short answer formats. They test whether a model can *see and identify*, not whether it can *reason with deep understanding*. MMMU targets deliberate reasoning with domain-specific knowledge — questions from college exams, textbooks, and quizzes that require both multimodal understanding and expert-level reasoning.

### Main Idea

MMMU collects **11.5K multimodal questions** from college-level materials across six core disciplines:

| Discipline | Description |
|------------|-------------|
| Art & Design | Art history, design principles, visual composition |
| Business | Accounting, economics, management (charts, tables) |
| Science | Physics, chemistry, biology (diagrams, graphs) |
| Health & Medicine | Anatomy, pharmacology, clinical reasoning (medical images) |
| Humanities & Social Science | History, psychology, philosophy (maps, timelines) |
| Tech & Engineering | CS, EE, mechanical engineering (circuits, code, architecture diagrams) |

Each question is open-ended or multiple-choice, accompanied by heterogeneous image types: charts, diagrams, maps, tables, music sheets, chemical structures, circuit diagrams, anatomical images, and more. The key design principle is that **text-only performance is near-random** — the images are integral to the question.

### Technical Details

- **Question sources:** College exams, quizzes, and textbooks curated by experts
- **Quality control:** Multi-round validation by domain experts; ambiguous or answerable-without-image questions filtered out
- **Format:** Multiple-choice (most common) + open-ended
- **Difficulty gradient:** Within each subject, questions span basic recall to complex multi-step reasoning
- **Evaluation metrics:** Accuracy (exact match for MCQ, keyword match for open-ended)

The authors evaluated 14 open-source LMMs + GPT-4V and Gemini:

| Model | Accuracy |
|-------|----------|
| Gemini Ultra | 59.4% |
| GPT-4V | 55.7% |
| Gemini Pro | 47.9% |
| Qwen-VL-Plus | 45.2% |
| LLaVA-1.5 (13B) | 36.4% |
| InstructBLIP (13B) | 33.3% |
| Open-source average | ~35% |

**Key takeaway:** Even the best models are well below expert-level (80%+), and there's a massive gap between proprietary and open-source models.

### Research Takeaway

MMMU established several critical findings:

1. **College-level multimodal reasoning is far from solved** — the 56-59% ceiling is far below human expert performance
2. **Discipline variance is enormous** — models do better on Science (physics formulas, diagram-based) and worse on Humanities (nuanced reasoning, cultural context)
3. **Open-source LMMs lag proprietary by ~15-20 points** — but the gap has been closing with newer models
4. **The benchmark is robust to text-only cheating** — the images are truly necessary

### Modern Perspective (2026)

MMMU has been extended to MMMU-Pro (2024, 2409.02813), which filters out questions that can be answered correctly by random chance too often, making the benchmark more robust. By 2025-2026, top models (GPT-4o, Claude 3.5/4, Gemini 2.0) have pushed MMMU scores past 75-80%, but the hardest disciplines (Art & Design, Humanities) remain challenging. The benchmark successfully identified that **perceptual understanding and deep reasoning are distinct capabilities** — a model can ace one and fail the other.

## Related Papers

### Paper 1: When One Modality Sabotages the Others

- **Title:** When One Modality Sabotages the Others: A Diagnostic Lens on Multimodal Reasoning
- **Authors:** Chenyu Zhang, Minsol Kim, Shohreh Ghorbani, Jingyao Wu, Rosalind Picard, Patricia Maes, Paul Pu Liang
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2511.02794

**Contribution:** Introduces the concept of **modality sabotage** — a diagnostic failure mode in which a high-confidence unimodal error overrides other evidence and misleads the fused result. The paper proposes a lightweight, model-agnostic diagnostic layer that treats each modality as an "agent" producing candidate labels and self-assessments, then aggregates them to identify which modality is the "saboteur."

**Relation to main paper:** MMMU tells us *what* models get wrong (which disciplines, which question types). Modality sabotage tells us *why* — it reveals that a single overconfident visual or textual error can cascade and corrupt the whole reasoning process. Together they form a diagnostic loop: MMMU identifies the failure, modality sabotage explains the mechanism.

**Why it matters:** This directly addresses one of Day 1's open questions: "How much of VLMs' reasoning capability is genuine composition vs. memorized patterns?" The sabotage framework suggests that even when a model gets the right answer, it may be driven by a single modality overwhelming others — the fusion dynamics are opaque and unreliable.

**Deep read recommended?** Yes — the sabotage framework has direct implications for any system that fuses modalities. The agent-as-modality metaphor is especially relevant for multimodal agents.

### Paper 2: LMRM Survey

- **Title:** Perception, Reason, Think, and Plan: A Survey on Large Multimodal Reasoning Models
- **Authors:** Yunxin Li, Zhenyu Liu, Zitao Li, Xuanyu Zhang, Zhenran Xu, Xinyu Chen, Haoyuan Shi, Shenyuan Jiang, Xintong Wang, Jifang Wang, Shouzheng Huang, Xinping Zhao, Borui Jiang, Lanqing Hong, Longyue Wang, Zhuotao Tian, Baoxing Huai, Wenhan Luo, Weihua Luo, Zheng Zhang, Baotian Hu, Min Zhang
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2505.04921

**Contribution:** A comprehensive survey organizing multimodal reasoning research into a **four-stage developmental roadmap**:
1. **Task-specific modules** (2018-2022) — specialized modules per task, reasoning embedded across representation/alignment/fusion
2. **Unified MLLMs** (2022-2024) — single architecture for all tasks (Flamingo, LLaVA, BLIP-2)
3. **Multimodal CoT + RL** (2024-2025) — structured reasoning chains (MCoT) + multimodal reinforcement learning
4. **Native LMRMs** (2025+) — end-to-end reasoning models trained to reason from scratch

**Relation to main paper:** MMMU provides the evaluation substrate against which all four stages are measured. The survey shows how each stage improved MMMU scores: Stage 2 (unified MLLMs) pushed from ~35% to ~50%, Stage 3 (MCoT+RL) pushed further to ~65%, and Stage 4 (native reasoning models) aims for 80%+.

**Why it matters:** This survey maps the exact trajectory we're tracking in this topic. ViperGPT (Day 2) sits at the boundary of Stage 1 and 3 — it's a module-based approach but uses code generation for reasoning. MMMU (today) provides the evaluation framework across all stages. The open question is whether Stage 4 native reasoning models will need to re-incorporate explicit decomposition (ViperGPT-style) or can achieve reasoning purely through scale and RL.

**Deep read recommended?** Yes — the four-stage roadmap is the best organizing framework for the topic so far.

## Current Understanding

After 3 days, the image-text reasoning topic is taking shape:

1. **The perception-reasoning gap** (Day 1, confirmed by BLINK on Day 2): VLMs see well but perceive poorly — they identify objects but lack robust core visual capabilities (depth, correspondence, forensics). This caps all higher-level reasoning.

2. **Three architectural paradigms** (Day 1-2):
   - **Module-based/program-based** (ViperGPT, VisProg) — transparent and compositional, but bottlenecked by underlying perception APIs
   - **End-to-end VLM** (most commercial models) — scalable but opaque, prone to shortcut learning
   - **Generation-as-world-model** (interleaved CoT) — promising but unproven at scale

3. **The measurement problem** (Day 3): MMMU shows that even the best models achieve only 56-59% on college-level multimodal reasoning. But MMMU measures correctness, not the reasoning process — a model could get the right answer for the wrong reason.

4. **Modality sabotage** (Day 3): A new diagnostic concept explaining *how* multimodal reasoning fails — when one modality's overconfident error cascades and dominates the fused result. This complements the BLINK perception gap by showing a failure mechanism at the fusion level, not just the perception level.

5. **The four-stage roadmap** (Day 3): The field is progressing from modular → unified → MCoT+RL → native reasoning models. Each stage improves MMMU scores about 15-20 points.

6. **The counterfactual gap** (Day 1) remains unresolved — no paradigm handles counterfactual/analogical visual reasoning well.

## Key Concepts

- **MMMU benchmark** — 11.5K college-level multimodal questions across 6 disciplines; the standard for expert-level multimodal reasoning evaluation
- **Discipline variance** — large accuracy differences across disciplines (Science > Humanities) in MMMU
- **Modality sabotage** — failure mode where a single overconfident unimodal error corrupts fused multimodal reasoning
- **Diagnostic layer** — treating each modality as an "agent" to audit fusion dynamics
- **Four-stage roadmap** — task-specific modules → unified MLLMs → MCoT+RL → native unimodal reasoning models
- **Benchmark robustness** — MMMU's design prevents text-only cheating (images are integral)
- **MMMU-Pro** — improved version filtering out low-discrimination questions
- **Perception bottleneck overlap** — modality sabotage operates at the fusion level while BLINK operates at the perception level; they interact but are distinct

## Open Questions

- MMMU measures answer correctness, not reasoning quality. **Can we build a benchmark that measures the reasoning process itself** — rewarding correct intermediate steps even if the final answer is wrong?
- **Does modality sabotage get worse or better as models scale?** Larger models have more capacity per modality, which could mean fewer errors per modality — but also more confidence in those errors.
- **Is the modality sabotage framework applicable beyond emotion recognition** (the paper's case study) — to VQA, multimodal agents, video understanding?
- **How do program-based systems (ViperGPT) fare against the sabotage framework?** In principle, explicit program decomposition should make each modality's contribution traceable, reducing sabotage risk.
- **What is the weakest link in current multimodal reasoning: perception (BLINK), fusion (sabotage), or reasoning (CoT quality)?** Different papers blame different bottlenecks.
- **Can RLVR be applied to teach models to resist modality sabotage** — e.g., by training against adversarial unimodal distractor signals?
- **Will native LMRMs (Stage 4) converge back to modular decomposition**, or is pure end-to-end sufficient at sufficient scale?
- **Do MMMU scores correlate with real-world multimodal agent performance?** A model that aces MMMU may still fail in open-ended agent interactions.

## Possible Thesis Ideas

1. **Modality Sabotage in Multimodal Agents** — extend the sabotage diagnostic framework from static VQA to dynamic agent environments where modalities (vision, text, tool outputs) compete for attention over multiple steps. The open-agent setting makes the sabotage problem harder because incorrect early observations cascade.

2. **Benchmark for Reasoning Process Quality** — build on MMMU's question set but add process-level evaluation: scoring the reasoning trace (program correctness if using ViperGPT, chain-of-thought quality if using end-to-end), not just the final answer. This would disentangle "right for the right reason" from "right for the wrong reason."

3. **Adversarial Training Against Modality Sabotage** — design a training procedure where a "saboteur" signal (intentionally corrupted modality) is injected during training, teaching the model to weigh modalities more carefully and detect when one is unreliable.

4. **Cross-Discipline Reasoning Diagnosis** — use MMMU's discipline structure + modality sabotage to create a diagnostic profile per model: "this model is strong on Science+Vision but Humanities over-relies on text priors," enabling targeted training interventions.

## Next Step

Day 4 should explore **RLVR for multimodal reasoning** — how reinforcement learning with verifiable rewards is being applied to improve reasoning in multimodal settings. The LMRM survey identified this as Stage 3, and recent work on MathVista and multimodal math reasoning (e.g., Multimodal RLVR, M3CoT) provides concrete examples. This connects to the open question about whether RL can teach models to resist modality sabotage.
