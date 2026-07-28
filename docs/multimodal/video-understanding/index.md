# Video Understanding

Question: **How do models represent temporal information in video?**

This directory contains daily research-map notes for this topic.

🟢 **Active** — Starting July 28, 2026

## Connection to Previous Topics

Video understanding builds naturally on image-text reasoning: the same perceptual tools (ViTs, region grounding, interleaved representations) must now handle **temporal sequences**. Key new dimensions:

- **Temporal encoding**: how to aggregate frame-level features into video-level representations
- **Spatiotemporal attention**: self-attention over both space and time
- **Training data**: video-text pairs are scarcer and noisier than image-text pairs
- **Efficiency**: video inference is O(T) more expensive than image inference
