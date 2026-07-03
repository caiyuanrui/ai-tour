# 2026-06-30 — VLM Pretraining (Day 5 — Topic Capstone)

Course: Multimodal, VLA, and Robotics
Topic: VLM Pretraining
Stage: Day 5 — Topic summary and advance
Confidence: 0.74 → 0.82

## Today's Question

What is the unified picture of VLM pretraining after studying five generations of methods?

## Topic Map: VLM Pretraining

Over 5 days, we traced VLM pretraining from its foundation to the modern frontier:

| Day | Date | Paper | Focus | Conf After |
|-----|------|-------|-------|------------|
| 1 | Jun 2 | **CLIP** (Radford 2021) | Contrastive pretraining, zero-shot transfer | 0.45 |
| 2 | Jun 9 | **LLaVA** (Liu 2023) | Visual instruction tuning, connector architecture | 0.60 |
| 3 | Jun 16 | **SigLIP** (Zhai 2023) | Sigmoid loss, data curation, training recipes | 0.68 |
| 4 | Jun 23 | **MM1** (McKinzie 2024) | Design space: encoder + connector + LLM + data mix | 0.74 |
| 5 | Jun 30 | **Topic Synthesis** | Unified picture and open problems | **0.82** |

## Unified Understanding

VLM pretraining decomposes into three decoupled layers:

```
┌─────────────────────────────────────┐
│  Reasoning Layer: LLM + Data Mix    │ ← interleaved + caption + text-only
├─────────────────────────────────────┤
│  Bridge Layer: Connector            │ ← simple MLP suffices (null result)
├─────────────────────────────────────┤
│  Representation Layer: Image Encoder│ ← SigLIP ViT, dynamic-resolution
└─────────────────────────────────────┘
```

**Key findings across the topic:**

1. **Image encoder dominates** — scaling encoder capacity and resolution has the highest ROI of any single change
2. **Data mixture is the second lever** — image-caption + interleaved + text-only ratio significantly impacts downstream performance
3. **Connector is a solved problem** — simple MLP matches complex Q-Former after controlling for visual token count
4. **Contrastive pretraining is not yet replaceable** — generative objectives still lag behind on zero-shot transfer

## Key Concepts (consolidated)

- Contrastive learning with sigmoid pairwise loss
- Two-stage paradigm: contrastive pretrain → generative finetune
- Three-way data mixture: caption + interleaved + text-only
- Dynamic-resolution ViT with window attention + Perceiver Resampler
- Connector null result: MLP matches complex designs
- SigLIP decouples batch size from loss computation
- EVA-CLIP: training technique as a systematic improvement axis
- DataComp: data curation as a systematic research dimension
- MM1 design space methodology: isolate one variable while controlling others

## Open Questions (most important)

- **Can loss unification happen?** — is there a single objective that achieves both CLIP-level zero-shot and generative VQA performance?
- **Is the three-layer separation fundamental or an artifact of current architectures?**
- **At what model scale does end-to-end native multimodal training outperform connector-based VLMs?**

## Next Step

Advancing to **Image-Text Reasoning** — exploring how VLMs reason over visual and textual information jointly (VQA, visual dialogue, chain-of-thought with images).
