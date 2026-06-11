# 2026-06-02 — VLM Pretraining

Course: Multimodal, VLA, and Robotics
Topic: VLM Pretraining
Stage: Day 1 — Foundation paper
Confidence: 0.00 → 0.45

## Today's Question

How are image-language models pretrained and aligned?

## Main Paper

**"Learning Transferable Visual Models From Natural Language Supervision" (CLIP)**

- **Authors:** Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, Ilya Sutskever
- **Year:** 2021
- **Venue:** arXiv:2103.00020 / OpenAI
- **Link:** https://arxiv.org/abs/2103.00020

### Why this paper?

CLIP is the canonical foundation paper for modern VLM pretraining. Nearly every subsequent VLM (LLaVA, BLIP, InternVL, etc.) builds on or compares against CLIP's contrastive pretraining paradigm.

### Core Problem

Traditional vision models are trained on fixed labeled categories (e.g., 1000 ImageNet classes). Adding or changing concepts requires expensive re-labeling. The supervision signal is too narrow.

### Main Idea

Train a vision encoder and a text encoder jointly with a contrastive objective: given a batch of N image-text pairs, maximize the cosine similarity of matched pairs while minimizing it for unmatched pairs. This simple objective learns rich, transferable visual representations aligned to natural language.

Key innovations:
- **400M image-text pairs** scraped from the internet (WebImageText dataset)
- **Contrastive loss**: 80% efficiency gain over predictive approaches
- **Zero-shot transfer**: use natural language class descriptions as classifiers
- **Scalability**: linear in batch size, works at web scale

### Technical Details

- Two encoders: ResNet or ViT (vision) + Transformer (text)
- Training: 32k batch size, 592 GPUs for 12 days on 400M pairs
- Loss: symmetric cross-entropy on similarity matrix (N×N)
- Temperature scaling learned during training
- Zero-shot: encode class names → compute similarity with image → argmax

### Research takeaway

The key insight is that **contrastive learning from natural language** is dramatically more sample-efficient than prediction-based approaches (predicting exact caption text). The alignment objective naturally forces representations to capture the shared structure between modalities.

### Modern perspective (2026)

CLIP's architecture has been absorbed as a standard component — nearly every modern VLM uses a CLIP-style vision encoder. Key improvements include: SigLIP (sigmoid loss, more efficient), EVA-CLIP (better training recipes), and multimodal pretraining (adding audio/video). The contrastive paradigm remains dominant, but newer VLM architectures often add generative objectives on top (captioning, VQA).

## Related Papers

### Paper 1: "A Survey of State of the Art Large Vision Language Models"

- **Authors:** Zongxia Li, Xiyang Wu, Hongyang Du, Fuxiao Liu, Huy Nghiem, Guangyao Shi
- **Year:** 2025
- **Venue:** arXiv:2501.02189 / CVPR Workshop 2025
- **Role:** Context and landscape

**Contribution:** Surveys the major VLMs through 2025, covering architecture evolution, alignment methods, benchmarks, and challenges (hallucination, fairness, safety).

**Relation to main paper:** Shows how CLIP's contrastive paradigm evolved into the modern VLM landscape of GPT-4V, Claude, and specialized models. Provides the post-CLIP trajectory.

**Why it matters:** Essential to understand where CLIP fits in the broader VLM ecosystem — it's the pretraining backbone, not the end-to-end vision-language system.

### Paper 2: "Exploring the Frontier of Vision-Language Models: A Survey"

- **Authors:** Akash Ghosh, Arkadeep Acharya, Sriparna Saha, Vinija Jain, Aman Chadha
- **Year:** 2024
- **Venue:** arXiv:2404.07214
- **Role:** Complementary taxonomy

**Contribution:** One of the first VLMs-only surveys. Proposes a three-way taxonomy: vision-language understanding, multimodal→text, and multimodal→multimodal.

**Relation to main paper:** Classifies CLIP as a "vision-language understanding" model — its primary use is representation learning and zero-shot transfer, not generation.

## Current Understanding

VLM pretraining has converged on a two-stage paradigm:

1. **Stage 1 — Contrastive pretraining** (CLIP-style): learn aligned vision-language representations from large-scale noisy image-text pairs
2. **Stage 2 — Generative finetuning** (optional): train a connector + LLM for VQA/captioning

CLIP's contribution is showing that Stage 1 alone produces remarkably transferable representations. The contrastive objective is the critical design choice — it's far more efficient than generative pretraining (predicting captions) because it doesn't need to model all the irrelevant details in either modality.

## Key Concepts

- Contrastive learning with image-text pairs
- Zero-shot transfer via natural language class descriptors
- Symmetric cross-entropy loss (image→text + text→image)
- Web-scale data collection (400M pairs)
- Encoder-decoder vs. dual-encoder architectures
- Vision encoder (ViT or ResNet) + text encoder (Transformer)

## Open Questions

- What is the optimal pretraining data quality vs. quantity tradeoff for VLM encoders?
- How much of CLIP's zero-shot capability comes from data scale vs. the contrastive objective vs. the encoder architecture?
- Can contrastive pretraining be replaced by a unified multimodal objective?
- How do VLM representations degrade under distribution shift?

## Possible Thesis Ideas

- **Unified contrastive-generative VLM pretraining** — combine contrastive alignment with masked image/text modeling to improve both representation quality and generation
- **Resource-efficient VLM alignment** — finding minimal fine-tuning required to adapt a CLIP encoder to a specific downstream domain

## Next Step

Day 2 should explore a modern VLM that builds on CLIP (e.g., LLaVA, BLIP-2, or InternVL) to understand the Stage 2 connector + LLM architecture.
