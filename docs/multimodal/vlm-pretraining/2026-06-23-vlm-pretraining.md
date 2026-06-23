# 2026-06-23 — VLM Pretraining

Course: Multimodal, VLA, and Robotics
Topic: VLM Pretraining
Stage: Day 4 — Architecture ablations and design space exploration
Confidence: 0.68 -> 0.74

## Today's Question

Beyond contrastive pretraining and instruction tuning, what architectural and data choices actually matter when building modern VLMs from scratch? How should we systematically think about the VLM design space?

## Main Paper

### Metadata

- Title: MM1: Methods, Analysis & Insights from Multimodal LLM Pre-training
- Authors: Brandon McKinzie, Zhe Gan, Jean-Philippe Fauconnier et al. (Apple — 31 authors)
- Year: 2024
- Venue: arXiv (2403.09611)
- Link: https://arxiv.org/abs/2403.09611

### Why this paper?

After understanding CLIP's contrastive foundations (Day 1), LLaVA's instruction tuning paradigm (Day 2), and pretraining optimization (SigLIP/DataComp/EVA-CLIP, Day 3), the natural next question is: *how do all these components fit together in a modern VLM?* MM1 is the most comprehensive ablation study of VLM pretraining choices — it systematically isolates what matters and what doesn't.

### Core Problem

When building a multimodal LLM (image encoder → connector → LLM decoder), there are many design choices: image encoder architecture and size, image resolution and token count, connector design (simple MLP vs. resampler vs. Q-Former), and data mixture (image-caption only vs. interleaved text+images vs. text-only). The field lacked a systematic understanding of which choices dominate performance.

### Main Idea

MM1 trains a large number of VLM variants at 1B–3B scale while ablating one variable at a time, then scales the best configuration to 7B/30B/30B-MoE. The key findings are:

1. **Data mixture is the most critical factor.** A careful combination of image-caption data + interleaved image-text data + text-only data achieves dramatically better few-shot and multi-image reasoning performance than any single data type. Image-caption data teaches visual grounding; interleaved data teaches in-context learning; text-only data prevents LLM degradation.

2. **Image encoder capacity dominates vision performance.** Larger image encoders, higher resolution, and more visual tokens all substantially improve downstream results. The choice of image encoder (ViT-L vs ViT-H) has a much larger effect than the connector design.

3. **Vision-language connector design has negligible impact.** After controlling for visual token count, simple MLP connectors perform about as well as transformer-based resamplers or Q-Former-style cross-attention. The connector's role is primarily to map visual tokens to the LLM's embedding space — any reasonable linear/MLP projection works once it has enough capacity for the token count.

4. **Text-only data is crucial for LLM competency.** Without text-only data during pretraining, the LLM backbone's language capabilities degrade significantly, especially on reasoning-heavy tasks.

### Technical Details

- **Architecture**: SigLIP ViT (image encoder) → MLP connector → pre-trained LLM decoder (based on a Chrome-style architecture).
- **Data mixture**: ~70% image-caption pairs (for visual grounding) + ~25% interleaved image-text data (for in-context few-shot learning) + ~5% text-only data (for language competency preservation). The exact ratios are ablated.
- **Training**: Two-stage — (1) pretraining on the mixture above, (2) supervised fine-tuning on instruction-following data.
- **Scaling**: Dense 7B and 30B models, plus a Mixture-of-Experts (MoE) variant of the 30B model. MoE improves efficiency-quality tradeoff.
- **Evaluation**: Few-shot learning, multi-image reasoning, and standard VLM benchmarks. The model shows strong in-context learning and chain-of-thought abilities.

### Research takeaway

MM1 reframes VLM building from "which connector architecture wins?" to "what data mixture and image encoder should I use?" — a more hardware- and data-centric view. The null result on connector design is both surprising and liberating: practitioners can use the simplest MLP connector and focus engineering effort on data curation and image processing.

### Modern perspective

MM1's findings have been validated by subsequent models (Idefics2, PaliGemma, Llama 3.2 Vision, Qwen2-VL). The field converged on:
- Simple MLP connectors (or direct pixel injection for native multimodal models)
- Higher-resolution image encoders (384+ px, 576+ tokens)
- Mixed data strategies with substantial interleaved data
- Text-only data preservation

The connector null result also explains why the field moved toward native multimodal models (Chameleon, Gemini) that train everything jointly rather than post-hoc connector designs.

## Related Papers

### Paper 1: Flamingo — a Visual Language Model for Few-Shot Learning

- **Authors**: Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc et al. (DeepMind, 26 authors)
- **Year**: 2022
- **Venue**: NeurIPS 2022
- **Link**: https://arxiv.org/abs/2204.14198

**Contribution:** Flamingo introduced interleaved visual-language pretraining at scale, using a Perceiver Resampler to compress variable numbers of visual features into fixed-length tokens that condition a frozen LLM via gated cross-attention layers. A single model achieves SOTA few-shot results across VQA and captioning benchmarks without task-specific fine-tuning.

**Relation to MM1:** Flamingo is the precursor architecture that MM1 builds on conceptually. Where Flamingo showed *that* interleaved training works, MM1 systematically ablates *why* and *which components matter*. Flamingo's Perceiver Resampler is an example of a complex connector that MM1 finds unnecessary — simple MLPs match it after controlling for token count.

**Why it matters:** Flamingo established the interleaved training paradigm that most modern VLMs (including MM1) inherit. Its approach of freezing pretrained components and training only the bridge/connector is still a common practical recipe.

**Should deep-read?:** Yes, especially the Perceiver Resampler and gated cross-attention details. It's a canonical architecture paper.

### Paper 2: Qwen2.5-VL Technical Report

- **Authors**: Shuai Bai, Keqin Chen, et al. (Alibaba, ~30 authors)
- **Year**: 2025
- **Venue**: arXiv (2502.13923)
- **Link**: https://arxiv.org/abs/2502.13923

**Contribution:** Qwen2.5-VL pushes VLM architecture further by training a **native dynamic-resolution Vision Transformer** from scratch with Window Attention, eliminating the need for image resizing/normalization. It introduces **absolute time encoding** for hour-long video understanding. The 72B model matches GPT-4o and Claude 3.5 Sonnet on document/diagram understanding.

**Relation to MM1:** Qwen2.5-VL validates and extends MM1's findings. Its dynamic-resolution ViT is a direct upgrade to the "image encoder resolution matters" lesson from MM1. The simple connector design (after MM1's null result confirmation) uses a straightforward MLP projection. Its strong performance confirms that data mixture and encoder capacity dominate.

**Why it matters:** Qwen2.5-VL represents the current SOTA in open-source VLMs and shows how the field has evolved:
- From fixed-resolution ViT → dynamic-resolution ViT trained from scratch
- From separate vision/language pretraining → joint optimization
- From shallow understanding → document parsing, structured extraction, agent capabilities

**Should deep-read?:** Yes, especially the dynamic-resolution ViT training recipe and Window Attention efficiency analysis. It's a good system-level paper.

## Current Understanding

VLM pretraining can now be understood as a **three-layer problem**:

1. **Representation layer** (image encoder): ViT trained with contrastive (SigLIP) or generative objectives. Encoder capacity, resolution (≥384px), and token count (≥576) dominate performance. Dynamic-resolution ViTs (Qwen2.5-VL) remove the fixed-resolution bottleneck — the ViT is no longer a separately pretrained frozen module but part of an end-to-end trained system.

2. **Bridge layer** (connector): Despite early complexity (Q-Former in BLIP-2, Perceiver Resampler in Flamingo, gated cross-attention), the connector is now understood to be a solved problem — simple MLP projection of visual tokens to the LLM's embedding space suffices. The real work is in token count, not connector architecture.

3. **Reasoning layer** (LLM + data mixture): The LLM decoder provides reasoning, and the data mixture determines what multimodal capabilities emerge. Image-caption data → visual grounding. Interleaved data → in-context few-shot learning. Text-only data → preserved language reasoning. The balance between these three data types is the highest-leverage design decision.

This three-layer view clarifies why the field is moving toward end-to-end native multimodal training (Chameleon, Gemini, GPT-4o): when the connector doesn't matter much, you might as well train everything jointly and let the model learn its own visual representations.

## Key Concepts

- **VLM design space**: Image encoder + connector + LLM + data mixture
- **Connector null result**: After controlling for visual token count, connector architecture is negligibly important
- **Three-way data mixture**: Image-caption + interleaved + text-only
- **Dynamic-resolution ViT**: ViT trained from scratch without fixed image size, using Window Attention
- **Perceiver Resampler**: Compresses variable visual features to fixed-length latent tokens (Flamingo)
- **Interleaved pretraining**: Training on naturally co-occurring text-image sequences (web pages, documents)
- **Token count vs. connector complexity**: Higher token count dominates better connector design
- **Absolute time encoding**: Native temporal encoding for hour-long video (Qwen2.5-VL)

## Open Questions

1. **What is the optimal dynamic-resolution ViT training recipe?** Qwen2.5-VL shows it works, but training a ViT from scratch at multiple resolutions is expensive. Is there a cheaper fine-tuning path?

2. **Does the connector null result hold at extreme scales (200B+)?** MM1 tested up to 30B. At much larger LLM scales, does a more sophisticated connector become necessary to bridge modality gaps effectively?

3. **Can end-to-end native multimodal training outperform connector-based VLMs at all scales?** Or is the connector approach a practical Pareto-optimal solution below a certain scale?

4. **What is the optimal data mixture ratio?** MM1 found a specific ratio, but this likely depends on the target tasks. Is the mixture a function of the LLM's pretraining data distribution?

5. **How does dynamic-resolution ViT interact with contrastive pretraining?** Current dynamic-resolution ViTs are trained from scratch. Can SigLIP/DINOv2-style contrastive encoders be adapted to variable-resolution inputs?

6. **Does text-only data proportion scale with model size?** The text-only data is needed to preserve LLM competency — does a 200B LLM need more or less text-only data during VLM training than a 7B model?

## Possible Thesis Ideas

1. **Connector-free multimodal pretraining at scale** — Train an LLM from scratch with interleaved text and image tokens (no separate encoder/connector), systematically measuring the data efficiency vs. connector-based approaches across model scales.

2. **Dynamic-resolution ViT adapters** — Instead of training a ViT from scratch, adapt fixed-resolution contrastive ViTs (SigLIP, DINOv2) to variable-resolution inputs with lightweight modules (positional embedding interpolation + resolution-aware routing).

3. **Task-aware data mixture optimization** — Learn to dynamically sample from image-caption / interleaved / text-only data during VLM training based on a meta-learning curriculum, rather than using a fixed ratio.

4. **VLM pretraining at the model-collapse frontier** — As web data becomes increasingly AI-generated, how does the three-way data mixture need to change to maintain VLM capabilities?

## Next Step

Day 5 should cover **post-pretraining alignment** for VLMs — how RLHF, DPO, and preference optimization work for multimodal models. This would round out the full VLM pipeline: pretraining → fine-tuning → alignment. Good options include LLaVA-RLHF (2024), Silkie (RLHF for VLM), or DRESS.

After Day 5, we'll have 5 days on VLM Pretraining with confidence likely reaching ~0.80, enabling a natural transition to the next topic (Image-Text Reasoning).
