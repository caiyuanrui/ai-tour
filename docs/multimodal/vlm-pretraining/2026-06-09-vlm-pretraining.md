# 2026-06-09 — VLM Pretraining (Day 2)

Course: Multimodal, VLA, and Robotics
Topic: VLM Pretraining
Stage: Day 2 — Modern VLM architecture
Confidence: 0.45 → 0.60

## Today's Question

How do modern VLMs connect a CLIP-style vision encoder to a large language model?

## Main Paper

**"Visual Instruction Tuning" (LLaVA)**

- **Authors:** Haotian Liu, Chunyuan Li, Qingyang Wu, Yong Jae Lee
- **Year:** 2023
- **Venue:** NeurIPS 2023 (Oral) / arXiv:2304.08485
- **Link:** https://arxiv.org/abs/2304.08485

### Why this paper?

LLaVA is the canonical "CLIP + connector + LLM" architecture that defined the modern VLM paradigm. It's simple, effective, and almost all subsequent VLMs (LLaVA-1.5, LLaVA-NeXT, InternVL, etc.) build on its approach.

### Core Problem

CLIP provides aligned vision-language representations, but cannot generate text. End-to-end VLMs (like Flamingo) are expensive to train. How can we build a visual chat model that inherits both CLIP's visual understanding and an LLM's language ability?

### Main Idea

Three-component architecture:
1. **Vision encoder** (CLIP ViT-L/14) — frozen, provides visual features
2. **Projection layer** (simple linear layer) — trainable, maps vision features to LLM's embedding space
3. **LLM** (Vicuna-7B/13B) — frozen for initial training, finetuned for chat

The key innovation is using **GPT-4 to generate visual instruction data** from COCO images — the first work to use a language-only LLM to create multimodal training data.

### Technical Details

- **Data**: 158K multimodal instruction-following samples from COCO images + GPT-4 generated questions
- **Training**: Two stages:
  1. Pre-training: train only the projection layer on image-caption pairs
  2. Instruction tuning: finetune projection + LLM on visual instruction data
- **Architecture**: CLIP ViT-L → linear projection → Vicuna (LLM). Only the projection (0.1% of parameters) + LLM are trainable
- **Results**: 85.1% relative score vs GPT-4 on multimodal instruction following. 92.53% on Science QA (SOTA)

### Research takeaway

LLaVA shows that **the connector doesn't need to be complex** — a simple learned linear projection from CLIP's [CLS] token to the LLM's first embedding is sufficient for good multimodal chat. The real bottleneck is **data quality**, not architecture complexity. GPT-4 generated visual instruction data was the key unlock.

### Modern perspective (2026)

LLaVA's architecture has been refined (LLaVA-1.5 adds MLP connector, higher resolution, cleaner data), but the fundamental pattern is unchanged. The main developments since: high-resolution vision encoders (AnyRes, S2), dynamic resolution, and native-resolution VLMs. LLaVA's data generation pipeline (using strong LLMs to create training data) is now standard practice.

## Related Papers

### Paper 1: "BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models"

- **Authors:** Junnan Li, Dongxu Li, Silvio Savarese, Steven Hoi
- **Year:** 2023
- **Venue:** arXiv:2301.12597
- **Role:** Alternative connector design

**Contribution:** Introduces the Querying Transformer (Q-Former) — a lightweight transformer that learns to query visual features from a frozen image encoder and feed them to a frozen LLM. Two-stage pretraining: (1) vision-language representation learning, (2) generative learning from frozen LLM.

**Relation to main paper:** Where LLaVA uses a simple linear projection, BLIP-2 uses a learned query mechanism. BLIP-2's Q-Former is more parameter-efficient (54× fewer trainable params than Flamingo80B) but doesn't finetune the LLM, limiting instruction-following ability.

**Why it matters:** BLIP-2 and LLaVA define the two poles of VLM connector design — simple projection vs. learned queries. Most modern VLMs follow LLaVA's approach (finetune LLM) but borrow BLIP-2's data curation ideas.

### Paper 2: "LLaVA-1.5: Improved Baselines with Visual Instruction Tuning"

- **Authors:** Haotian Liu, Chunyuan Li, Yuheng Li, Yong Jae Lee
- **Year:** 2024
- **Venue:** arXiv:2310.03744
- **Role:** Practical improvements

**Contribution:** Systematic improvements to LLaVA: MLP projection (instead of linear), academic-task-oriented data mixture (VQA + OCR + region-level), higher resolution (336px). Achieves SOTA on 11 benchmarks with simple changes.

**Relation to main paper:** Shows that the original LLaVA architecture is the right foundation — improvements come from data quality, resolution, and the simple switch from linear to MLP projection.

## Current Understanding

Modern VLM architecture is now standardized as:

```
Vision Encoder (CLIP ViT) → Connector (MLP) → LLM
                              ↑ trainable     ↑ finetuned
```

The connector is tiny (0.1-1% of parameters). The LLM does most of the work. Data quality matters more than architecture complexity for VLM performance.

Key design decisions:
1. **Vision encoder**: CLIP ViT-L remains standard, but higher resolution (336px → 384px → dynamic) is the main axis of improvement
2. **Connector**: simple MLP dominates over Q-Former in practice (LLaVA-1.5 > BLIP-2 for chat)
3. **LLM**: smaller models (7B-13B) work well; scaling the LLM helps predictably
4. **Data**: GPT-4 generated instruction data → higher quality curated datasets (ShareGPT4V, LVIS-Instruct-4V)

## Key Concepts

- Connector architecture (projection layer vs. Q-Former)
- Visual instruction tuning from LLM-generated data
- Two-stage training: alignment pretrain → instruction finetune
- Frozen encoder + trainable connector + finetuned LLM
- Data quality over architecture complexity

## Open Questions

- Why does a simple linear/MLP projection work so well? Is the alignment really that good, or does the LLM compensate?
- Is the CLIP vision encoder the bottleneck for VLM performance, or is it the LLM?
- What is the optimal visual token count for vision-language tasks?
- Can the connector be eliminated entirely (direct visual token injection)?

## Possible Thesis Ideas

- **Adaptive visual tokens** — dynamically allocate more/fewer visual tokens based on image complexity, reducing cost for simple images and improving detail for complex ones
- **Connector-free VLM** — train a vision encoder that produces tokens directly consumable by an LLM, eliminating the connector entirely

## Next Step

Day 3 should move to Image-Text Reasoning (next topic) or continue with video understanding if still on VLM Pretraining.
