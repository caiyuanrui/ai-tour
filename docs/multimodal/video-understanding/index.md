# Video Understanding

Question: **How do models represent temporal information in video?**

✅ **Completed** — 5 days · 15 papers · conf 0.80 (2026-09-01)

## Notes

| Date | Paper | Paradigm | Link |
|------|-------|----------|------|
| 2026-08-04 | Video Understanding with Large Language Models: A Survey (Tang et al. 2023) | Survey / Landscape | [📄](2026-08-04-video-understanding.md) |
| 2026-08-11 | LLaVA-Video: An Image is Worth 1,024 Tokens (Zhang et al. 2024) | Method / Data Recipe | [📄](2026-08-11-video-understanding.md) |
| 2026-08-18 | ReTaKe: Reducing Temporal and Knowledge Redundancy for Long Video Understanding (Wang et al. 2024) | Training-free KV Compression | [📄](2026-08-18-video-understanding.md) |
| 2026-08-25 | HourVideo: 1-Hour Video-Language Understanding (Chandrasegaran et al. 2024) | Benchmark / Hour-scale Temporal Reasoning | [📄](2026-08-25-video-understanding.md) |
| 2026-09-01 | Topic Capstone — Budget Allocation & Temporal-Detail Preservation | Day 5 — Capstone / Synthesis | [📄](2026-09-01-video-understanding-capstone.md) |

## Topic Summary

Video understanding in the LLM era is a **budget-allocation problem at every layer** of the
stack — ingestion → efficiency → measurement:

1. **Ingestion**: sampling/tokenization (LLaVA-Video's uniform 1 fps, 1,024 tokens/frame) and
   position encoding (Qwen2.5-VL's M-RoPE absolute time). F-16 proved "sample more, compress
   locally" beats "sample sparsely" for fine-grained tasks.
2. **Efficiency**: the O(T) token wall attacked from three corners — input selection
   (VideoTree), training-free KV pruning (ReTaKe: DPSelect + PivotKV), external memory
   (Flash-VStream).
3. **Measurement**: the temporal-detail bottleneck is real — HourVideo humans 85.0% vs Gemini
   37.3%; TemporalBench GPT-4o 38.5% vs human ~70%; MBA corrects multi-choice gaming.

**Central thesis target**: temporal-detail-preserving compression evaluated on TemporalBench +
HourVideo subtasks — the question no paper has answered yet. Cross-domain pattern: the
counterfactual weakness is shared with image-text reasoning, suggesting a common data-driven
limitation.

## Connection to Previous Topics

Video understanding builds naturally on image-text reasoning: the same perceptual tools (ViTs,
region grounding, interleaved representations) must now handle **temporal sequences**. Key new
dimensions:

- **Temporal encoding**: how to aggregate frame-level features into video-level representations
- **Spatiotemporal attention**: self-attention over both space and time
- **Training data**: video-text pairs are scarcer and noisier than image-text pairs
- **Efficiency**: video inference is O(T) more expensive than image inference
