# 2026-07-09 — Score-Based Models (Day 2)

Course: Generative Models
Topic: Score-Based Models
Stage: Day 2 — SDE unification
Confidence: 0.40 → 0.60

## Today's Question

How does the SDE framework unify score matching, Langevin dynamics, and diffusion-based generative models? And what practical training innovations made score-based models viable at scale?

## Main Paper

**"Score-Based Generative Modeling through Stochastic Differential Equations"**

| Field | Detail |
|-------|--------|
| **Authors** | Yang Song, Jascha Sohl-Dickstein, Diederik P. Kingma, Abhishek Kumar, Stefano Ermon, Ben Poole |
| **Year** | 2021 |
| **Venue** | ICLR 2021 |
| **Link** | https://arxiv.org/abs/2011.13456 |

### Why this paper?

This is the **unification paper** — it shows that NCSN (score matching + Langevin dynamics) and DDPM (denoising diffusion) are both special cases of the same continuous-time framework: forward SDE diffusion + reverse SDE generation. For the score-models topic, this paper is essential because it puts score estimation at the center of all generative modeling via diffusion.

### Core Problem

Two separate generative paradigms — score matching with Langevin dynamics (NCSN) and denoising diffusion (DDPM) — were developed independently with different training objectives, different sampling algorithms, and different intuitions. Is there a unified mathematical framework that explains both?

### Main Idea

The paper makes two key contributions:

1. **Unified SDE framework**: Both NCSN and DDPM can be expressed as discretizations of the same continuous process: a forward SDE that adds noise to data and a reverse SDE that generates data. The difference is just which SDE you choose — **Variance Exploding (VE)** SDE for NCSN (noise scale grows unbounded) vs **Variance Preserving (VP)** SDE for DDPM (noise variance saturates at 1).

2. **Probability Flow ODE**: For any SDE, there exists a deterministic ODE (the probability flow ODE) whose trajectories have the same marginal density at every time t. This means you can sample deterministically using the ODE (faster, invertible) or stochastically using the SDE (higher quality, more exploration).

### Technical Details

**Forward SDE:**
```
dx = f(x, t) dt + g(t) dw
```
where f is the drift coefficient and g is the diffusion coefficient.

**Reverse SDE:**
```
dx = [f(x, t) - g(t)² ∇_x log p_t(x)] dt + g(t) dw̄
```
The key term is **∇_x log p_t(x)** — the **score function** of the perturbed data distribution. This is what the neural network learns!

**Probability Flow ODE:**
```
dx/dt = f(x, t) - ½ g(t)² ∇_x log p_t(x)
```
Same score function, but no stochastic term — a deterministic ODE.

**Two specific SDEs:**

| SDE | Type | g(t) | Variance | Origin |
|-----|------|------|----------|--------|
| VE | Exploding | sqrt(dσ²/dt) | σ(t)² → ∞ | NCSN |
| VP | Preserving | sqrt(β(t)) | 1 - e^{-∫β dt} ≤ 1 | DDPM |

**Sub-VP SDE**: A third variant that achieves lower variance than VP by using a different drift.

**Sampling methods:**
- **Predictor-Corrector (PC) sampler**: Alternates between reverse SDE step (predictor) and Langevin dynamics correction step (corrector) at each noise level. Best quality, more compute.
- **Probability Flow ODE sampler**: Pure deterministic ODE solve. Fewer NFEs but can use numerical ODE solvers (e.g., RK45, Euler). Enables likelihood computation.
- **ODE + SDE correction**: Use ODE for efficient trajectory, then add small stochastic corrections.

**Likelihood computation:** The probability flow ODE allows exact likelihood computation via the instantaneous change-of-variables formula (Neural ODE). The paper shows diffusion models achieve log-likelihoods competitive with autoregressive models on CIFAR-10.

### Results

| Method | CIFAR-10 FID | NFE | Likelihood (bits/dim) |
|--------|-------------|-----|----------------------|
| DDPM (baseline) | 3.17 | 1000 | — |
| SDE-PC (VP) | 2.41 | 2000 | 2.99 |
| SDE-PC (VE) | 2.20 | 2000 | — |
| ODE (VP) | 4.46 | 140 | — |
| ODE (VE) | 5.17 | 140 | — |
| SDE-PC + ODE (VE) | **2.17** | 1000+140 | — |

### Limitations

- The PC sampler requires 1000-2000 NFEs for best quality — much more expensive than simple DDPM sampling
- The ODE sampler is faster but quality degrades significantly at low NFE
- The theoretical framework doesn't immediately suggest better SDE designs — VE and VP were discovered empirically
- Likelihood computation via Neural ODE requires differentiable ODE solver, which is memory-intensive

### Research Takeaway

The SDE framework revealed three fundamental insights: (1) score estimation is the core learning objective that unifies all diffusion-like models; (2) the choice of SDE (VE vs VP vs sub-VP) changes the optimization landscape and final sample quality; (3) the probability flow ODE connects diffusion to normalizing flows, enabling likelihood computation.

### Modern Perspective (2026)

The SDE framework is now the standard way to think about diffusion models. The PC sampler has been largely superseded by DPM-Solver and other fast ODE solvers that achieve similar quality in 10-50 steps. The sub-VP SDE is rarely used. But the core insight — that score estimation + SDE/ODE reverse simulation = generative model — remains the foundation of the field. The most impactful recent development, flow matching (Lipman et al. 2023), generalizes the probability flow ODE to arbitrary vector fields, not just score-based ones.

## Related Papers

### Paper 1: "Improved Techniques for Training Score-Based Generative Models"

| Field | Detail |
|-------|--------|
| **Authors** | Yang Song, Stefano Ermon |
| **Year** | 2020 |
| **Venue** | NeurIPS 2020 |
| **Link** | https://arxiv.org/abs/2006.09011 |

**Contribution:** This paper fixes practical training issues in the original NCSN (Score Matching with Langevin Dynamics). Key improvements:

1. **Unified noise conditioning**: Replace the separate noise-conditioned score networks (one per noise scale) with a single noise-conditioned network using a learned noise embedding — like the time embedding in DDPM.
2. **Progressive training**: Anneal the noise levels during training rather than training them all at once.
3. **Improved architecture**: Use more residual blocks, attention, and better up/downsampling.
4. **Stability fixes**: Address the training instability of ANOVA (denoising score matching) at high noise levels.

**Relation to main paper:** This paper is the "engineering" companion to the SDE theory. While the SDE paper provides the unified mathematical framework, this paper provides the practical techniques needed to actually train score models. The noise-conditioned network design and progressive training are what made score models scale beyond 32×32 images.

**Why it matters:** Without these training improvements, the SDE framework would be a beautiful theory that doesn't produce good samples. The improved training was necessary for score-based models to match GAN quality on CIFAR-10 and ImageNet.

### Paper 2: "Maximum Likelihood Training of Score-Based Diffusion Models"

| Field | Detail |
|-------|--------|
| **Authors** | Yang Song, Conor Durkan, Iain Murray, Stefano Ermon |
| **Year** | 2021 |
| **Venue** | NeurIPS 2021 |
| **Link** | https://arxiv.org/abs/2101.09258 |

**Contribution:** This paper analyzes the relationship between the score-matching objective used in training diffusion models and the log-likelihood of the generated data. Key findings:

1. **Weighted score matching = likelihood lower bound**: The standard MSE loss on score prediction at each noise level, when weighted appropriately, corresponds to maximizing a variational lower bound on the data log-likelihood.
2. **Connection to ELBO**: The connection is exact for VP-SDE (DDPM) — the standard DDPM loss is a variational bound. For VE-SDE (NCSN), the connection is approximate.
3. **Improved weighting schemes**: By analyzing the likelihood connection, the paper proposes new weighting schemes that improve log-likelihood without sacrificing sample quality.
4. **Likelihood evaluation**: Uses the probability flow ODE (from the SDE paper) to compute exact test-set log-likelihoods, showing diffusion models achieve competitive likelihoods on par with autoregressive models.

**Relation to main paper:** This paper deepens the theoretical foundation laid by the SDE framework. The SDE paper showed the geometry (score → reverse process); this paper shows the optimization theory (score matching ≈ maximum likelihood). Together they provide a complete picture: why score matching works, what it optimizes, and how to evaluate it.

**Why it matters:** The likelihood connection matters conceptually — it means diffusion models aren't just generating pretty samples; they have a principled probabilistic objective. This is what distinguishes them from GANs (which have no tractable likelihood). It also enables direct comparison to autoregressive models, VAEs, and normalizing flows on the same metric.

## Current Understanding

Score-based models now have a coherent three-layer picture:

**Layer 1 — Unified SDE framework (this paper):** All diffusion-like models are instances of a forward SDE (data → noise) and learned reverse SDE (noise → data). The score function ∇_x log p_t(x) is the only thing the model needs to learn. The probability flow ODE provides a deterministic counterpart that enables likelihood computation and invertible generation.

**Layer 2 — Practical training (Improved Techniques):** Training score models requires careful noise conditioning, progressive noise annealing, and appropriate architecture design. The noise-conditioned network with learned embeddings is the standard approach. Training at high noise levels is the primary source of instability.

**Layer 3 — Likelihood theory (Maximum Likelihood):** The score matching objective is not arbitrary — it corresponds to maximizing a lower bound on log-likelihood. This connects diffusion models to the broader framework of probabilistic generative modeling and allows direct comparison with other generative model classes.

Together with the Consistency Models covered on Day 1, the map now includes:
- The score function as the fundamental object (what to learn)
- The SDE/ODE framework (how to use it for generation)
- Practical training innovations (how to make it work)
- The likelihood connection (why it's principled)
- Consistency distillation (how to accelerate it)

## Key Concepts

- Forward SDE: dx = f(x,t)dt + g(t)dw
- Reverse SDE: dx = [f(x,t) - g(t)²∇log p_t(x)]dt + g(t)dw̄
- Probability flow ODE: dx/dt = f(x,t) - ½g(t)²∇log p_t(x)
- VE SDE (Variance Exploding): noise variance → ∞
- VP SDE (Variance Preserving): noise variance ≤ 1
- Sub-VP SDE: lower-variance alternative to VP
- Predictor-Corrector (PC) sampler: SDE step + Langevin correction
- Noise-conditioned score network
- Progressive noise annealing for training stability
- Score matching loss ≈ likelihood lower bound
- ELBO connection for VP-SDE (exact) and VE-SDE (approximate)
- Probability flow ODE for likelihood computation
- Weighted score matching and optimal weighting schemes

## Open Questions

- Why does VE-SDE empirically produce better sample quality than VP-SDE, even though VP has cleaner likelihood theory?
- Is there an optimal choice of forward SDE, or are VE/VP just the two discovered endpoints of a spectrum?
- Can the PC sampler be replaced entirely by better ODE solvers for all quality regimes?
- Does the likelihood-quality tradeoff (better likelihood ≠ better samples) indicate a fundamental tension in the score matching objective?
- How should the SDE framework be adapted for discrete data (text, code)?

## Possible Thesis Ideas

1. **Learning the forward SDE**: Instead of fixing the forward SDE (VE/VP), learn a data-dependent forward process that adapts to the geometry of the data manifold
2. **Theoretical analysis of the likelihood-sample quality gap**: Understand why better log-likelihood doesn't guarantee better sample quality in diffusion models — could lead to better training objectives
3. **Unified training framework for VE and VP**: Develop a single training recipe that works well for both SDE types, removing the need for SDE-specific hyperparameter tuning
4. **Score-free generative models**: Can we bypass score estimation entirely and learn the reverse SDE directly via optimal transport or adversarial objectives?

## Next Step

Day 3 should explore **score matching methodology more deeply** — specifically, denoising score matching (DSM), sliced score matching (SSM), and their tradeoffs. The current map has the two main score matching approaches covered: DSM (via the diffusion/SDE framework) and the consistency property. Understanding the methodological taxonomy of score matching techniques will fill the gap between theory and practice.
