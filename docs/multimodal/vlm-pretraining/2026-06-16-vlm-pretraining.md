# 2026-06-16 — VLM Pretraining

Course: Multimodal, VLA, and Robotics
Topic: VLM Pretraining
Stage: Day 3 — Beyond Contrastive Softmax: Alternative Objectives and Data Curation
Confidence: 0.60 -> 0.68

## Today's Question

Beyond the standard softmax-based contrastive loss (CLIP), what alternative training objectives and data curation strategies improve VLM pretraining efficiency and quality?

## Main Paper

### Metadata

- Title: Sigmoid Loss for Language Image Pre-Training (SigLIP)
- Authors: Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, Lucas Beyer
- Year: 2023
- Venue: ICCV 2023 Oral
- Link: https://arxiv.org/abs/2303.15343

### Why this paper?

We now understand CLIP's contrastive paradigm (Day 1) and the generative finetune stage (Day 2, LLaVA). But the pretraining objective itself is worth questioning. SigLIP proposes a fundamentally different loss function — pairwise sigmoid instead of softmax — that decouples batch size from loss computation. This directly addresses our open question: "Can contrastive pretraining be replaced by a unified multimodal objective?"

### Core Problem

CLIP's contrastive loss uses softmax normalization across all image-text pairs in a batch. This means every training example must see every other example's similarity score — a global operation that couples batch size to both memory and communication cost. Large-batch training becomes expensive because all-pairs softmax requires gathering logits from all devices.

### Main Idea

Replace the softmax-based contrastive loss with a **pairwise sigmoid loss** that operates independently on each image-text pair. Instead of normalizing across all negatives, each positive pair is trained to have a high similarity score, and each negative pair (implicitly sampled from other pairs in the batch) is trained to have a low score — each via independent sigmoid cross-entropy.

**Pseudocode (corrected):**
```
for each image i, text j in batch:
    logit = cos(embed_i, embed_j) * t + b
    if i == j:   # positive pair
        loss_i += -log(sigmoid(logit))
    else:        # negative pair
        loss_i += -log(sigmoid(-logit))
```

Key difference from CLIP: No softmax normalization across the row. Each logit is independently pushed toward 0 or 1 via the sigmoid.

### Key Technical Details

- **Batch size independence:** Since each pair is treated independently, the loss computation no longer requires a global similarity matrix normalization. This means SigLIP works well at **both small and large batch sizes**.
- **LiT (Locked-image Tuning):** When combined with a frozen pretrained image encoder, training converges extremely fast — 84.5% ImageNet zero-shot in 2 days on just 4 TPUv4 chips.
- **Extreme batch size study:** Tested up to 1M, found diminishing returns beyond 32k. This is novel — CLIP's softmax loss makes 1M-batch training practically impossible due to all-pairs memory.
- **Negative-to-positive ratio:** The sigmoid formulation allows independent study of how many negatives per positive are needed.

### Experiments/Results

| Method | Batch Size | Hardware | ImageNet Zero-Shot |
|--------|-----------|----------|-------------------|
| CLIP ViT-L/14 | 32k | 592 TPUv4 | ~75.5% |
| SigLIP (standard) | 32k | Moderate | ~83% |
| SigLiT (SigLIP+LiT) | 32k | 4 TPUv4 | **84.5%** |

### Limitations

1. The sigmoid loss requires tuning the `t` (temperature) and `b` (bias) parameters carefully — the paper had to correct typos and initialization details across 4 versions.
2. While efficient for pretraining, the final model still follows the same dual-encoder architecture as CLIP — the loss improvement doesn't change the fundamental representation structure.
3. The paper mainly studies zero-shot ImageNet; broader cross-modal transfer benchmarks are less explored.
4. LiT requires a good frozen image encoder — it's not a from-scratch method.

### Relation to Topic

SigLIP answers our core topic question ("How are image-language models pretrained and aligned?") by showing that the **loss function matters at least as much as scale or architecture**. The switch from softmax to sigmoid is mathematically simple but operationally significant — it democratizes VLM training by reducing hardware requirements while maintaining or improving quality.

### What changed in the topic map

Before SigLIP, the literature treated "contrastive loss" as monolithic (softmax-based). SigLIP opens a new dimension: **loss function design** as an independent axis alongside architecture, data, and scale. This also connects to the broader question of whether alignment objectives need to be contrastive at all.

## Related Papers

### Paper 1: DataComp — In Search of the Next Generation of Multimodal Datasets

- **Authors:** Gadre, Ilharco, Fang, et al. (34 authors)
- **Year:** 2023
- **Venue:** NeurIPS 2023 Datasets & Benchmarks
- **Link:** https://arxiv.org/abs/2304.14108

**Contribution:** DataComp is a benchmark for dataset curation, not model design. It provides a 12.8B image-text candidate pool from Common Crawl, standardized CLIP training code, and 38 downstream evaluation tasks. The key finding: **better data, not better models, drives performance** — DataComp-1B (their best curated dataset) trains a ViT-L/14 to 79.2% zero-shot ImageNet, beating OpenAI's CLIP ViT-L/14 (75.5%) with identical training code.

**Relation to main paper:** While SigLIP improves the loss function, DataComp improves the data — these are orthogonal axes of improvement. Together they suggest a combined approach (SigLIP on well-curated data) would be even more effective. DataComp directly addresses our open question about data quality vs. quantity tradeoffs.

**Why it matters:** Established the "dataset engineering" research direction as a rigorous field. Shows that data curation is not a solved problem even for well-studied tasks like CLIP training.

**Deep-read later?** Yes — the filtering strategies (CLIP score filtering, text quality filtering, deduplication) deserve specific study.

### Paper 2: EVA-CLIP — Improved Training Techniques for CLIP at Scale

- **Authors:** Quan Sun, Yuxin Fang, Ledell Wu, Xinlong Wang, Yue Cao
- **Year:** 2023
- **Venue:** arXiv / BAAI
- **Link:** https://arxiv.org/abs/2303.15389

**Contribution:** EVA-CLIP introduces improved training techniques (representation learning, optimization, augmentation) that significantly reduce training cost while improving quality. Their largest model (EVA-02-CLIP-E/14+, 5.0B params) achieves 82.0% ImageNet zero-shot with only 9B seen samples — far fewer than CLIP's 13B seen samples. The smaller EVA-02-CLIP-L/14+ (430M params) achieves 80.4% with 6B seen samples.

**Relation to main paper:** Where SigLIP changes the loss function, EVA-CLIP changes training infrastructure (optimizer, augmentation, model architecture). Both reduce the compute needed for CLIP-class models but approach from different angles. EVA-CLIP shows that **where you allocate compute in training matters more than raw scale**.

**Why it matters:** Opensource CLIP-class model weights that practitioners can actually use. The "EVA" family also connects to masked image modeling, suggesting pretrained visual representations can transfer to contrastive objectives.

**Deep-read later?** Yes — the specific augmentation and optimization tricks could be important for any CLIP reimplementation.

## Current Understanding

VLM pretraining is no longer just "scale up CLIP." We now have three independent axes of improvement:

1. **Loss function** (SigLIP): Replacing softmax with sigmoid enables batch-size-independent training, reducing hardware requirements.
2. **Data curation** (DataComp): The dataset itself is a major design dimension — filtering quality > raw scale.
3. **Training techniques** (EVA-CLIP): Better optimizers, augmentations, and initialization strategies significantly reduce training compute.

These three directions are **complementary** — you could combine SigLIP loss with DataComp-curated data and EVA-CLIP training tricks. A key open question is whether these improvements compound, overlap, or have diminishing returns when combined.

The VLM pretraining landscape has evolved from "one architecture + one loss + large data" to a multidimensional design space where each component is independently optimizable. This is a sign of field maturity — but also means the right combination for specific domains/constraints isn't yet known.

## Key Concepts

- **Pairwise sigmoid loss:** Per-pair sigmoid cross-entropy instead of softmax normalization over a batch
- **Batch-size-independent training:** The loss no longer requires global similarity normalization, decoupling batch size from hardware requirements
- **LiT (Locked-image Tuning):** Freezing the image encoder and only training the text encoder for efficient alignment
- **Data curation as research direction:** Systematic study of filtering, deduplication, and quality assessment for multimodal datasets
- **Compute allocation over raw scale:** EVA-CLIP shows that better training infrastructure beats simply scaling data or parameters
- **Three-axis VLM improvement:** Loss function × Data × Training techniques — each independently optimizable

## Open Questions

1. **Do SigLIP, DataComp-level data, and EVA-CLIP training tricks compound?** If their benefits are additive, the combined improvement could be dramatic. If overlapping, the field may be approaching diminishing returns.
2. **What is the optimal loss for VLM pretraining?** SigLIP improves on softmax contrastive, but is sigmoid itself optimal? Could we move to non-contrastive objectives entirely (e.g., generative objectives during pretraining)?
3. **Does LiT-style frozen encoders limit downstream flexibility?** Locked image encoders are efficient, but what if the downstream task needs vision features that differ from the frozen encoder's pre-training objective?
4. **How does data curation interact with loss function choice?** Are certain curation strategies (e.g., CLIP-based filtering) biased toward certain loss functions?

## Possible Thesis Ideas

1. **Combined effect of SigLIP + DataComp + EVA-CLIP:** Empirically measure whether these three orthogonal improvements are additive, multiplicative, or overlapping in combined CLIP training. If additive, the results would exceed any single improvement direction.
2. **Unified loss-data-training benchmark for VLM pretraining:** Extend the DataComp framework to vary loss function (softmax vs sigmoid vs other) and training techniques (EVA tricks) simultaneously, creating a comprehensive design space map.
3. **Non-contrastive VLM pretraining at scale:** Can we replace the contrastive/sigmoid objective entirely with a generative pretraining objective (e.g., masked image-text modeling) and match CLIP-level zero-shot transfer? If yes, the VLM pretraining paradigm fundamentally changes.
4. **Domain-specific VLM data curation:** Apply DataComp-style systematic curation to niche domains (medical, satellite, robotics) and measure whether curation recipes transfer or need re-discovery per domain.

## Next Step

Confidence increased from 0.60 to 0.68 — we now understand that VLM pretraining improvement happens along three independent axes. Day 4 should pick one of these axes and go deeper: either deeper into loss function variants, or deeper into data curation strategies. DataComp's filtering methodology would be the most useful next exploration since it connects directly to practical deployment decisions.
