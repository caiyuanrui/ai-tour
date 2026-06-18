# 2026-06-18 — Diffusion Foundations (Day 3)

Course: Generative Models
Topic: Diffusion Foundations
Stage: Day 3 — Design Space Unification
Confidence: 0.65 → 0.78

## Today's Question

How can we systematically understand and improve diffusion model design choices (noise schedule, preconditioning, sampling) — and what are the key architectural innovations that made diffusion models surpass GANs?

## Main Paper

### Metadata

- **Title:** Elucidating the Design Space of Diffusion-Based Generative Models (EDM)
- **Authors:** Tero Karras, Miika Aittala, Timo Aila, Samuli Laine
- **Year:** 2022
- **Venue:** NeurIPS 2022
- **Link:** https://arxiv.org/abs/2206.00364

### Why this paper?

We've covered DDPM (variational bound / noise prediction) and NCSN (score matching). EDM is the essential third pillar: it systematically analyzes the *entire design space* of diffusion models — noise schedule, sampling, preconditioning, and architecture — and provides a unified practical framework. This is critical for understanding why later models (Stable Diffusion, DALL·E 3, etc.) use the design choices they do.

### Core Problem

Diffusion model theory and practice had become "unnecessarily convoluted." Different papers used different:

- Noise schedules (linear, cosine, geometric)
- Training objectives (ε-prediction, v-prediction, score prediction)
- Preconditioning strategies
- Sampling algorithms (DDIM, DPM-Solver, SDE solvers)
- Network preconditioning

No one had systematically separated these choices or understood their interactions.

### Main Idea

Decompose the diffusion design space into **independent choices** and evaluate each one experimentally. Key components:

1. **Deterministic ODE formulation** — Start from the probability flow ODE (Song 2021) as the foundation, parameterize it with clear design variables.

2. **Preconditioning redesign** — The network input/output must be scaled so that the network operates on unit-variance signals regardless of noise level. EDM introduces explicit preconditioning:

   ```
   F_θ = c_skip(σ) · x + c_out(σ) · D_θ(c_in(σ) · x, c_noise(σ))
   ```

   Where each `c_*(σ)` is analytically designed so that D_θ always gets well-scaled inputs and produces well-scaled outputs.

3. **Improved noise schedule** — Instead of linear β_t, use a schedule based on the effective signal-to-noise ratio: `σ(t) ∝ t`. This aligns with the ODE formulation naturally.

4. **Heun 2nd-order sampler** — Use a predictor-corrector style 2nd-order ODE solver instead of Euler, achieving far better quality in few steps.

### Technical Details

- **Training objective:** The preconditioning makes MSE training converge faster and be less sensitive to hyperparameters.
- **SDE vs ODE:** EDM focuses on the ODE formulation (probability flow), enabling high-quality sampling in 35 steps (vs 1000 for DDPM).
- **Architecture:** Uses StyleGAN-like backbone modifications (ResNet blocks with grouped convolutions, attention at resolution 32×32).
- **Noise schedule redesign:** σ(t) ∝ t (where t ∈ [0.002, 80]), leading to a much simpler and mathematically cleaner schedule.

### Key Results

| Setting | FID (prior SOTA) | FID (EDM) | Steps |
|---------|-----------------|-----------|-------|
| CIFAR-10 unconditional | ~2.56 | **1.97** | 35 |
| CIFAR-10 class-conditional | — | **1.79** | 35 |
| ImageNet-64 (re-trained) | 2.07 | **1.36** | 35 |

Importantly, just applying EDM's *sampling* changes to a pre-trained ImageNet-64 model improved FID from 2.07 to 1.55 — no retraining needed.

### Research takeaway

EDM showed that diffusion models' performance is largely determined by **design choices in the data representation and solver**, not just the model architecture. The explicit preconditioning and deterministic ODE formulation systematically removed training/sampling fragility. This modular analysis became the gold standard for all subsequent diffusion work.

### Modern perspective (2026)

EDM's preconditioning formulation is now standard in most diffusion training codebases (Stable Diffusion 3 uses variations of it). The Heun sampler remains one of the best deterministic samplers. The key limitation is that EDM was designed for pixel-space models — latent diffusion (Rombach 2022) required adapting these ideas to the VAE latent space, where noise statistics differ.

## Related Papers

### Paper 1: "Improved Denoising Diffusion Probabilistic Models" (IDDPM)

- **Authors:** Alex Nichol, Prafulla Dhariwal
- **Year:** 2021
- **Venue:** ICML 2021 / arXiv:2102.09672
- **Role:** Predecessor — practical improvements to DDPM

**Contribution:** Three key improvements to DDPM: (1) **Cosine noise schedule** replacing the linear β_t schedule — cosine schedule adds noise more gradually at both ends, improving log-likelihood. (2) **Learning the reverse process variance** σ_θ(x_t, t) instead of fixing it — this enables high-quality sampling with 10× fewer steps. (3) **Importance sampling** for the variational bound, reducing training variance.

**Relation to main paper (EDM):** IDDPM identified the noise schedule as a critical but poorly understood design choice — EDM later formalized this into a principled framework. IDDPM's learned variance was a practical hack that EDM's preconditioning and deterministic ODE made unnecessary (EDM achieves better results with fixed variance using 2nd-order solvers).

**Why it matters:** IDDPM showed diffusion could achieve competitive log-likelihoods (not just sample quality). The cosine schedule remains widely used in latent diffusion models (Stable Diffusion 1.x).

### Paper 2: "Diffusion Models Beat GANs on Image Synthesis"

- **Authors:** Prafulla Dhariwal, Alex Nichol
- **Year:** 2021
- **Venue:** NeurIPS 2021 / arXiv:2105.05233
- **Role:** Application — demonstrating diffusion superiority with architectural improvements

**Contribution:** (1) Systematic architecture ablation for diffusion models — found that widening ResNet blocks, adding more attention heads, and using BigGAN-style modifications significantly improved quality. (2) **Classifier guidance** — during sampling, add the classifier gradient ∇_x log p(y|x) to the noise prediction, enabling a controllable trade-off between diversity and fidelity. (3) Achieved FID 2.97 on ImageNet 128×128, surpassing BigGAN-deep.

**Relation to main paper (EDM):** Dhariwal & Nichol's architectural improvements were the starting point for EDM's architecture analysis. EDM further refined these by showing that many of the improvements attributed to architecture were actually due to better training dynamics from proper preconditioning. EDM also showed classifier guidance can be replaced by classifier-free guidance (Ho & Salimans 2022) for the same benefit without an extra classifier.

**Why it matters:** This was the landmark paper that convincingly showed diffusion models could surpass GANs — a psychological turning point for the field. Classifier guidance became the standard conditioning method until classifier-free guidance supplanted it.

## Current Understanding

The diffusion foundations topic now has a coherent three-layer map:

| Layer | Core Paper | Key Function | Contribution |
|-------|-----------|-------------|--------------|
| **Training objective** | DDPM (Ho 2020) | ε_θ(x_t, t) | MSE on noise prediction, reweighted ELBO |
| **Theoretical lens** | NCSN + SDE (Song 2019/2021) | ∇ log p_σ(x) | Unification, score matching, probability flow ODE |
| **Practical design** | EDM (Karras 2022) | Preconditioned D_θ | Design space decomposition, 2nd-order sampling |

The landscape is now clear: diffusion models succeed because they provide a **stable, principled training procedure** (score matching / noise prediction MSE) with a **flexible sampling process** (any ODE/SDE solver). The practical secrets are proper preconditioning and high-order ODE solvers — not the specific architecture.

EDM's key insight: most prior "improvements" weren't caused by what their authors thought they were. Architecture improvements only help when paired with proper preconditioning; the noise schedule only matters relative to the ODE parameterization.

## Key Concepts

- EDM design space decomposition
- Preconditioning functions (c_skip, c_out, c_in, c_noise)
- Heun 2nd-order ODE solver
- Inverse noise schedule σ(t) ∝ t
- Classifier guidance vs classifier-free guidance
- Cosine noise schedule (IDDPM)
- Learned reverse process variance
- Deterministic sampling via probability flow ODE
- Ablation study methodology for generative models

## Open Questions

- **Latent space generalization:** EDM's preconditioning was designed for pixel-space. How should it be adapted for latent diffusion (VAE latents have different statistics than pixels)?
- **Optimal solver order:** Heun (2nd-order) is standard, but do higher-order solvers (like DPM-Solver++'s 3rd-order) provide meaningful gains for deterministic sampling?
- **Text conditioning:** How does EDM's design space change for text-conditioned generation? The preconditioning assumes unconditional or class-conditional; text embeddings require different scaling.
- **Architecture vs preconditioning:** EDM suggested architecture matters less than previously thought. Is this still true for large-scale (billion-parameter) diffusion models?

## Possible Thesis Ideas

- **Latent-space preconditioning theory** — Extend EDM's analytic preconditioning to the latent space of VQ-VAE / VAE, enabling principled latent diffusion training without hyperparameter search
- **Dynamic solver selection** — Learn a controller that picks between deterministic (ODE) and stochastic (SDE) sampling depending on the estimated score magnitude, combining EDM's ODE efficiency with SDE mode coverage
- **Design space mapping for video diffusion** — Apply EDM's systematic ablation methodology to video diffusion (which has an additional temporal dimension), identifying which design choices transfer and which don't

## Next Step

Day 4 should connect diffusion foundations to **sampling algorithms** — specifically DPM-Solver, the current standard fast sampler. This bridges EDM's deterministic ODE framework to the practical solvers used in every modern diffusion pipeline.
