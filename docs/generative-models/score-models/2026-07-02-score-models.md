# 2026-07-02 — Score-Based Models (Day 1)

Course: Generative Models
Topic: Score-Based Models
Stage: Day 1 — Consistency distillation
Confidence: 0.00 → 0.40

## Today's Question

How can score-based models generate samples in a single step?

## Main Paper

**"Consistency Models"**

- **Authors:** Yang Song, Prafulla Dhariwal, Mark Chen, Ilya Sutskever
- **Year:** 2023
- **Venue:** ICML 2023 / arXiv:2303.01469
- **Link:** https://arxiv.org/abs/2303.01469

### Core Problem

Diffusion models require 10-1000 iterative denoising steps for sampling. Each step requires a full model forward pass. Can we learn a model that maps any noisy input directly to the clean data distribution in a single step?

### Main Idea

Train a **consistency model** that maps any point on the diffusion trajectory (x_t at any t) directly to the initial point x_0. This function is called the "consistency function" f(x_t, t) = x_0, and it must satisfy:

1. **Self-consistency**: for any t and t', f(x_t, t) = f(x_{t'}, t') — the output should be the same regardless of which noise level you start from
2. **Boundary condition**: f(x_0, 0) = x_0 — at the clean data point, it's the identity

### Training Methods

Two approaches:

1. **Consistency Distillation (CD)**: distill a pretrained diffusion model into a consistency model. Generate paired samples (x_t, x_{t'}) from the diffusion trajectory, train f to produce the same prediction. Requires a teacher model.

2. **Consistency Training (CT)**: train from scratch without a teacher. Use Monte Carlo estimation of the score function to compute the consistency target. More challenging but more flexible.

### Technical Details

- Architecture: same U-Net as diffusion models, but with different output head
- Sampling: single forward pass (or 2-3 steps for quality improvement)
- Schedule: the number of discretization steps N controls the tradeoff — larger N for better quality, smaller N for faster training
- Connection to probability flow ODE: the consistency function is the solution of the PF-ODE integrated from t to 0

### Results

| Method | CIFAR-10 FID | Steps |
|--------|-------------|-------|
| DDPM | 3.17 | 1000 |
| DDIM | ~6.0 | 50 |
| CT (1 step) | 8.70 | 1 |
| CD (1 step) | 3.55 | 1 |
| CD (2 step) | 2.93 | 2 |

### Research Takeaway

Consistency models show that **single-step generation from a learned diffusion prior is achievable** without adversarial training. The key insight is the self-consistency property: the model must produce consistent predictions across all noise levels, which forces it to learn the true data manifold.

### Modern Perspective (2026)

Consistency models directly led to latent consistency models (LCM), which applied the same idea to latent diffusion (Stable Diffusion). LCM is widely used for real-time text-to-image generation. The main limitation: quality still lags behind multi-step diffusion for complex scenes, but the gap is closing. The approach is now standard for any deployment requiring low latency.

## Key Concepts

- Consistency function f(x_t, t) → x_0
- Self-consistency property across noise levels
- Consistency distillation (teacher-based)
- Consistency training (teacher-free)
- Probability flow ODE integration
- Single-step vs multi-step generation

## Open Questions

- Is the quality ceiling of consistency models fundamental to the single-step constraint, or can it be overcome with larger models?
- Can consistency training match distillation quality without a teacher?
- Does the consistency property impose a capacity bottleneck on the model?
- How does the consistency model handle multimodal distributions — does single-step generation always produce one mode?

## Next Step

Day 2 should explore latent diffusion (LDM) or flow matching as complementary approaches to efficient generative modeling.
