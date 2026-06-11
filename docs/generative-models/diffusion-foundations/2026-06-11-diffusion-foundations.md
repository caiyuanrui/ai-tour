# 2026-06-11 — Diffusion Foundations (Day 2)

Course: Generative Models
Topic: Diffusion Foundations
Stage: Day 2 — Score-Based Perspective
Confidence: 0.45 → 0.65

## Today's Question

How do score-based models connect to diffusion, and what is the unified SDE framework?

## Main Paper

**"Generative Modeling by Estimating Gradients of the Data Distribution" (NCSN)**

- **Authors:** Yang Song, Stefano Ermon
- **Year:** 2019
- **Venue:** NeurIPS 2019 (Oral) / arXiv:1907.05600
- **Link:** https://arxiv.org/abs/1907.05600

### Why this paper?

This paper introduced the score-based perspective (NCSN) which is the complement to DDPM's variational-bound perspective. Understanding both is essential for a complete picture of diffusion-based generation.

### Core Problem

GANs produce high-quality samples but are unstable to train. VAEs are stable but produce blurry samples. Is there a stable training procedure that produces sharp samples without adversarial training?

### Main Idea

Instead of learning to generate data directly, learn the **score function** — the gradient of the log-probability density ∇_x log p(x). Then use **Langevin dynamics** to sample: iteratively move toward higher density regions guided by the score.

Key challenges:
1. **The manifold problem**: data lies on low-dimensional manifolds where gradients are undefined
2. **Low-density regions**: score estimates are poor where data is scarce

### Solution: Score Matching with Multiple Noise Levels

Add Gaussian noise at multiple scales to "diffuse" the data off its manifold. Learn a single neural network (NCSN — Noise Conditional Score Network) that estimates the score at all noise levels simultaneously. For sampling, use **annealed Langevin dynamics**: start with high noise (well-behaved scores) and gradually reduce noise.

### Technical Details

- Training objective: denoising score matching loss at multiple noise levels
- Architecture: U-Net conditioned on noise level σ (via FiLM or concatenation)
- Sampling: annealed Langevin dynamics with T = 100-1000 steps, noise levels decreasing by geometric progression
- Key difference from DDPM: NCSN directly models the score (gradient), while DDPM models the noise prediction ε. These are equivalent: ε ∝ -σ · ∇_x log p(x|σ)

### Research takeaway

Score matching provides a **principled probabilistic objective** for generative modeling that avoids adversarial training. The multi-scale noise perturbation makes score estimation tractable. The deep connection to diffusion is that score matching and DDPM are estimating the same quantity — just from different theoretical perspectives.

### Modern perspective (2026)

Score matching + Langevin dynamics and DDPM are now understood as two views of the same underlying framework. The SDE formulation (Song et al., 2021) unified them. Practical implementations overwhelmingly use DDPM's simpler training objective (predict noise ε) but study it through the score lens for theoretical insights.

## Related Papers

### Paper 1: "Score-Based Generative Modeling through Stochastic Differential Equations"

- **Authors:** Yang Song, Jascha Sohl-Dickstein, Diederik P. Kingma, Abhishek Kumar, Stefano Ermon, Ben Poole
- **Year:** 2021
- **Venue:** ICLR 2021 (Oral) / arXiv:2011.13456
- **Role:** Unification framework

**Contribution:** Unifies score-based models (NCSN) and diffusion models (DDPM) under a single SDE framework. Forward SDE adds noise; reverse SDE removes noise. The score function is the only required component for the reverse SDE. Introduces predictor-corrector sampling and probability flow ODE.

**Relation to main paper:** Shows NCSN's discrete noise levels are a discretization of a continuous SDE. DDPM's discrete diffusion steps are another discretization of the same SDE. This unified view explains why both approaches work equally well.

**Why it matters:** The SDE framework is now the standard theoretical lens for understanding diffusion models. The probability flow ODE enables exact likelihood computation and faster sampling via ODE solvers.

### Paper 2: "Improved Techniques for Training Score-Based Generative Models"

- **Authors:** Yang Song, Stefano Ermon
- **Year:** 2020
- **Venue:** NeurIPS 2020 / arXiv:2006.09011
- **Role:** Practical improvements

**Contribution:** Addresses NCSN training instability. Key improvements: (1) use a U-Net with residual blocks instead of simple architectures, (2) improve noise conditioning, (3) use EMA (exponential moving average) of model parameters, (4) better noise distribution design.

**Relation to main paper:** Transforms NCSN from a proof-of-concept to a practical generative model. Many of these improvements (EMA, U-Net architecture, noise schedule design) were later adopted by DDPM and remain standard.

## Current Understanding

The relationship between the three foundational papers:

| Paper | Perspective | Training | Sampling | Key Insight |
|-------|------------|----------|----------|-------------|
| NCSN (Song 2019) | Score matching | ∇_x log p_σ(x) | Annealed Langevin | Score matches noise prediction |
| DDPM (Ho 2020) | Variational bound | ε_θ(x_t, t) | Reverse Markov chain | Reweighted ELBO |
| SDE (Song 2021) | Continuous diffusion | Score of p(x(t)) | Reverse SDE / PF ODE | Both are SDE discretizations |

The unified picture: all three estimate the same score function ∇ log p(x) at multiple noise levels. The choice of training objective (noise prediction vs. score prediction) and sampling method (Langevin vs. reverse diffusion vs. ODE) are implementation details.

## Key Concepts

- Score function: ∇_x log p(x)
- Denoising score matching
- Langevin dynamics sampling
- Annealed Langevin dynamics
- Noise Conditional Score Network (NCSN)
- SDE unification (VP-SDE, VE-SDE, sub-VP SDE)
- Probability flow ODE
- Predictor-corrector sampling

## Open Questions

- Why does noise prediction (DDPM objective) work better empirically than direct score prediction?
- Is the probability flow ODE truly equivalent to the SDE, or are there discretization artifacts?
- What is the optimal noise schedule for the SDE formulation?
- Can score-based understanding lead to fundamentally new sampling algorithms beyond Langevin/reverse diffusion?

## Possible Thesis Ideas

- **Unified noise schedule optimizer** — learn a noise schedule that simultaneously optimizes the SDE forward process for both score estimation accuracy and sampling efficiency
- **Score-conditioned sampling** — use the learned score function to guide existing samplers (DPM-solver, DDIM) adaptively based on estimated score magnitude

## Next Step

Day 3 should explore the practical consequences of the diffusion/score unification — specifically, improved samplers (DPM-Solver, consistency models) that leverage the ODE/SDE understanding.
