# Video Understanding

Question: **How do models represent temporal information in video?**

🟢 **Active** — Started 2026-08-04

## Notes

| Date | Paper | Paradigm | Link |
|------|-------|----------|------|
| 2026-08-04 | Video Understanding with Large Language Models: A Survey (Tang et al. 2023) | Survey / Landscape | [📄](2026-08-04-video-understanding.md) |

## Connection to Previous Topics

Video understanding builds naturally on image-text reasoning: the same perceptual tools (ViTs, region grounding, interleaved representations) must now handle **temporal sequences**. Key new dimensions:

- **Temporal encoding**: how to aggregate frame-level features into video-level representations
- **Spatiotemporal attention**: self-attention over both space and time
- **Training data**: video-text pairs are scarcer and noisier than image-text pairs
- **Efficiency**: video inference is O(T) more expensive than image inference
