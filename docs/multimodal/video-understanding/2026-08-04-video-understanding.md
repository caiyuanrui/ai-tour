# 2026-08-04 — Video Understanding: The Vid-LLM Landscape

Course: Multimodal, VLA, and Robotics
Topic: Video Understanding
Stage: Day 1 — Survey / Landscape
Confidence: 0.00 -> 0.40

## Today's Question

How do LLM-era video understanding systems represent temporal information, and what are the main architectural families for building them?

## Main Paper

### Metadata

- Title: Video Understanding with Large Language Models: A Survey
- Authors: Yolo Y. Tang, Jing Bi, Siting Xu, Luchuan Song, Susan Liang, Teng Wang, Daoan Zhang, Jie An, Jingyang Lin, Rongyi Zhu, et al.
- Year: 2023 (v8 updated 2025-11-25)
- Venue: arXiv
- Link: https://arxiv.org/abs/2312.17432

### Why this paper?

Day 1 of a new topic needs the map first. This is the canonical survey of Vid-LLMs (video + LLM systems), continuously updated through late 2025 — it defines the vocabulary, taxonomy, task landscape, and benchmark ecosystem that every later paper in this topic will reference. It also directly answers the topic question at the system level: how temporal information enters an LLM.

### Core Problem

Video understanding demands more than image understanding: models must perceive change over time — motion, order, causality, speed, event boundaries — and reason about it in open-ended language. The explosion of LLM-based video systems (Vid-LLMs) had outpaced any organizing framework, making it hard to compare approaches or identify what "temporal representation" actually means across systems.

### Main Idea

A two-axis taxonomy of Vid-LLMs:

**Architecture axis — how the video gets into the LLM:**
- **Video Analyzer × LLM**: a video analyzer extracts features (e.g., per-frame CLIP embeddings), which the LLM consumes. LLM is the "brain" over precomputed descriptions/features.
- **Video Embedder × LLM**: a learnable embedder maps the video into tokens/embeddings that are fed directly into the LLM's input space (the dominant family today — Video-LLaVA, VideoChat2, Qwen-VL all live here).
- **(Analyzer + Embedder) × LLM**: hybrids that combine both.

**Function axis — what the LLM does:**
- LLM as **Summarizer** (video → text summary)
- LLM as **Manager** (routes/coordinates downstream modules)
- LLM as **Text Decoder** (video tokens → language generation)
- LLM as **Regressor** (predicts values/timestamps from video features)
- LLM as **Hidden Layer** (video features pass through as intermediate representations)

The survey then maps tasks (captioning, video QA, temporal/spatiotemporal reasoning, video grounding, multimodal chat), datasets, and benchmarks, and catalogs the emergent capability of open-ended **multi-granularity reasoning** (general → temporal → spatiotemporal) with commonsense.

### Technical Details

- Typical pipeline: video encoder (CLIP-style ViT, VideoMAE, TimeSformer-style backbone) → temporal modeling (frame sampling, token merging, Q-Former-style resamplers) → connector/projection → LLM → instruction-tuned on video-text instruction data.
- Training is two-stage: (1) video-text alignment pretraining, (2) video instruction tuning (datasets like VideoChatGPT's instruction set, LLaVA-Video).
- Evaluation ecosystem: classic QA benchmarks (MSRVTT-QA, MSVD-QA, ActivityNet-QA, TGIF-QA) plus harder modern ones (Video-MME, MVBench, LongVideoBench) that stress temporal granularity and long context.
- The survey's recurring design axes: temporal granularity of encoding, number of sampled frames, whether image and video share a token space, and how temporal position is injected.

### Research takeaway

The field's central representation question is **how to compress a video into a token sequence without destroying temporal information**. The taxonomy makes clear that "video understanding" is really a stack: encoder choice × temporal compression strategy × connector × LLM × instruction data. Benchmarks are the weak link — classic QA sets are near-saturated and reward captioning-level understanding more than true temporal precision.

### Modern perspective

Read against what we already know from this course: video understanding inherits VLM pretraining's lessons (encoder capacity and data mixture dominate, connector choice is nearly a null result — MM1) and image-text reasoning's lessons (perception bottleneck, counterfactual gaps, interleaved reasoning). The survey's own listed limitations — long-video modeling, fine-grained temporal reasoning, hallucination — are exactly where this topic should focus its deep dives.

## Related Papers

### Paper 1

- **Title**: Is Space-Time Attention All You Need for Video Understanding? (TimeSformer)
- **Authors**: Gedas Bertasius, Heng Wang, Lorenzo Torresani
- **Year**: 2021 (ICML 2021)
- **Link**: https://arxiv.org/abs/2102.05095

**Contribution**: The canonical convolution-free video backbone — pure self-attention over space and time. Frame patches are embedded and fed to a Transformer; within each block, **divided attention** applies temporal attention first, then spatial attention. Systematic comparison of attention schemes (joint space-time, divided, sparse-local) found divided attention best.

**Relation to main paper**: TimeSformer is the architectural answer to the topic question at the backbone level — it defines the design space (how temporal attention is organized) that the survey's "Video Embedder" family assumes underneath. It grounds the survey's abstraction in a concrete mechanism.

**Why it matters**: SOTA on Kinetics-400/600 at publication; dramatically faster test-time than 3D CNNs; handles 1-minute+ clips. Nearly every modern video encoder (VideoMAE, Video Swin, MViT) is a descendant of this spatiotemporal-attention design space.

**Deep-read later**: Yes — this is the foundation of temporal representation; Day 2 should go deep here (or on VideoMAE/Swin3D).

### Paper 2

- **Title**: Video-LLaVA: Learning United Visual Representation by Alignment Before Projection
- **Authors**: Bin Lin, Yang Ye, Bin Zhu, Jiaxi Cui, Munan Ning, Peng Jin, Li Yuan
- **Year**: 2023
- **Link**: https://arxiv.org/abs/2311.10122

**Contribution**: A representative modern "Video Embedder × LLM" system. Unifies image and video in **one token space** by aligning visual features to the language feature space *before* projection (using LanguageBind as the shared encoder) — solving the "misalignment before projection" problem that separate image/video feature spaces create. Trained on mixed image + video data, showing mutual enhancement.

**Relation to main paper**: The concrete embodiment of the survey's Embedder × LLM family, and a direct probe of one of its central design questions — should image and video share a token space?

**Why it matters**: Outperforms Video-ChatGPT by +5.8 / +9.9 / +18.6 / +10.1 on MSRVTT, MSVD, TGIF, ActivityNet — evidence that unified tokenization plus mixed training beats video-only systems. It also connects to the course's VLM pretraining thread (shared representation, data-mixture effects).

**Deep-read later**: Maybe — as a baseline system; its "alignment before projection" claim is worth verifying against Qwen2-VL-style designs.

## Current Understanding

Video understanding in the LLM era decomposes into a stack: **temporal backbone → tokenization/compression → connector → LLM → instruction tuning**. The survey gives two organizing axes: how video enters the LLM (Analyzer vs Embedder vs hybrid) and what role the LLM plays (Summarizer/Manager/Text Decoder/Regressor/Hidden Layer). The dominant family today is Embedder × LLM, which compresses video into tokens the LLM can reason over.

Two representation questions structure the whole topic:
1. **Temporal encoding**: how to organize attention over time (TimeSformer's divided attention is the canonical answer at the backbone level) and how to sample/compress frames into tokens without losing order, motion, and causality.
2. **Unified vs separate token spaces**: whether images and videos should share one representation (Video-LLaVA argues yes, via alignment before projection).

Weaknesses are concentrated in long-video modeling (token explosion, O(T) cost), fine-grained temporal reasoning (order, speed, causality), and hallucination — and current benchmarks only partially measure these.

## Key Concepts

- Vid-LLM taxonomy: Video Analyzer × LLM / Video Embedder × LLM / (Analyzer + Embedder) × LLM
- LLM functional roles: Summarizer, Manager, Text Decoder, Regressor, Hidden Layer
- Multi-granularity reasoning: general → temporal → spatiotemporal
- Divided space-time attention (TimeSformer): temporal attention then spatial attention per block
- Spatiotemporal attention design space: joint vs divided vs sparse-local attention
- Alignment before projection — unified image/video token space (LanguageBind, Video-LLaVA)
- Two-stage training: video-text alignment pretraining → video instruction tuning
- Frame sampling / token merging / Q-Former-style resampling as temporal compression
- Video QA benchmark ecosystem: MSRVTT-QA, MSVD-QA, ActivityNet-QA, TGIF-QA → Video-MME, MVBench, LongVideoBench
- Benchmark saturation: classic video QA rewards captioning-level understanding, not temporal precision

## Open Questions

- What is the right granularity of temporal representation: per-frame tokens with cross-frame attention, explicit temporal attention, or learned temporal embeddings?
- How much temporal information is destroyed by sparse frame sampling (8–32 frames) — and does it cap fine-grained reasoning (order, speed, causality)?
- Is a unified image-video token space optimal, or do video tokens need extra temporal structure (temporal position embeddings, stride)?
- How do long-video models cope with O(T) token explosion — token merging, memory banks, hierarchical temporal abstraction?
- How much does video-text pretraining contribute vs. instruction tuning to downstream reasoning performance?
- Are classic video QA benchmarks saturated, and do Video-MME/MVBench/LongVideoBench genuinely measure temporal precision?
- How does generative video prediction ("video as world model") connect to temporal reasoning — the interleaved-CoT idea from the image-text-reasoning topic?
- Do temporal encoders trained on action recognition transfer to open-ended video-language reasoning?

## Possible Thesis Ideas

- Temporal token compression for long-video LLMs — adaptive frame/token selection that preserves event boundaries (crosses into LLM-systems efficiency).
- Unified image-video tokenization with an explicit temporal inductive bias — test whether "alignment before projection" scales to hour-long video.
- A fine-grained temporal reasoning benchmark (order/speed/causality) that current QA sets fail to measure — extends the image-text-reasoning capstone's "benchmark for reasoning process quality" idea.
- Video world-model reasoning — using generative video prediction as an interleaved reasoning state for temporal questions (builds on Zebra-CoT interleaved CoT).

## Next Step

Day 2: go deep on temporal backbones — TimeSformer (divided attention) vs VideoMAE (masked video pretraining) vs Video Swin/MViT (hierarchical temporal) — to pin down how each represents time and what the modern encoders (VideoMAE V2, ViT-Adapter) chose. This directly serves the topic question: "how do models represent temporal information."

## Search Notes

No web_search tool in this session; used arXiv API (relevance sort) + full-abstract fetch for verification. All three abstracts verified from arXiv directly.
