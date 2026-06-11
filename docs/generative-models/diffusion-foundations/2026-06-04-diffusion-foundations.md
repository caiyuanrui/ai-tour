# 2026-06-04 — Diffusion Foundations

Course: Generative Models
Topic: Diffusion Foundations
Stage: Day 1 — Foundation paper
Confidence: 0.00 → 0.45

## Today's Question

What are the core ideas behind denoising diffusion models?

## Main Paper

**"Denoising Diffusion Probabilistic Models" (DDPM)**

- **Authors:** Jonathan Ho, Ajay Jain, Pieter Abbeel
- **Year:** 2020
- **Venue:** NeurIPS 2020 / arXiv:2006.11239
- **Link:** https://arxiv.org/abs/2006.11239

### Why this paper?

DDPM is the paper that made diffusion models practical for high-quality image generation. It established the connection between diffusion probabilistic models and denoising score matching, and showed that a carefully weighted variational bound produces state-of-the-art results.

### Core Problem

Generative models face a tension between sample quality (GANs are good but unstable) and tractable likelihood (VAEs are stable but blurry). Prior diffusion models (Sohl-Dickstein 2015) existed but produced poor results.

### Main Idea

Define a forward Markov chain that gradually adds Gaussian noise to data (destroying structure), and learn a reverse Markov chain that denoises step by step. The key insight: when each forward step adds a small amount of noise, the reverse distribution becomes a simple Gaussian that is easy to learn.

### Technical Details

- **Forward process**: q(x_t | x_{t-1}) = N(√(1-β_t) x_{t-1}, β_t I). Closed form: q(x_t | x_0) = N(√(α̅_t) x_0, (1-α̅_t)I)
- **Reverse process**: p_θ(x_{t-1} | x_t) modeled as N(μ_θ, σ_t^2 I)
- **Training objective**: minimize variational bound. Simplified to L_simple = E_{t,x_0,ε}[||ε - ε_θ(√(α̅_t)x_0 + √(1-α̅_t)ε, t)||^2]
- **Key connection**: This is equivalent to denoising score matching over multiple noise levels, connecting diffusion models to score-based generative models
- **Architecture**: U-Net with attention layers, sinusoidal position embeddings for timestep t

### Results

- CIFAR10: FID 3.17 (state-of-the-art for likelihood-based models)
- LSUN 256×256: comparable to ProgressiveGAN quality

### Research takeaway

The critical innovation is the **weighted variational bound** — standard ELBO assigns equal weight to all timesteps, but DDPM reweights to emphasize the high-noise regime (coarse structure) over low-noise (fine detail). This subtle change is what makes diffusion models work well.

### Modern perspective (2026)

DDPM's architecture has been almost entirely superseded (large-scale U-Nets → latent diffusion → DiT transformers). But its training objective (simple MSE on noise) remains standard. The main limitations are: (1) 1000-step sampling is slow, (2) the Markov assumption limits architectural flexibility, (3) the Gaussian noise schedule is not optimal for all data types.

## Related Papers

### Paper 1: "Deep Unsupervised Learning using Nonequilibrium Thermodynamics"

- **Authors:** Jascha Sohl-Dickstein, Eric A. Weiss, Niru Maheswaranathan, Surya Ganguli
- **Year:** 2015
- **Venue:** ICML 2015 / arXiv:1503.03585
- **Role:** Original idea

**Contribution:** Introduced the concept of diffusion probabilistic models — forward diffusion destroys structure, reverse diffusion restores it. Provided the variational bound training framework.

**Relation to main paper:** DDPM is a practical instantiation of Sohl-Dickstein's framework. Key differences: DDPM removes the "diffusion rate β_t as learnable parameter" and directly predicts noise ε rather than μ.

**Should deep-read later?** Yes — the theoretical framing (nonequilibrium thermodynamics, tractable reverse process) is essential for deep understanding.

### Paper 2: "Denoising Diffusion Implicit Models" (DDIM)

- **Authors:** Jiaming Song, Chenlin Meng, Stefano Ermon
- **Year:** 2021
- **Venue:** ICLR 2021 / arXiv:2010.02502
- **Role:** Key extension

**Contribution:** Shows that DDPM's training objective depends only on the marginals q(x_t|x_0), allowing a non-Markovian forward process with same marginals → deterministic reverse process → 10-50× faster sampling without retraining.

**Why it matters:** DDIM makes diffusion models practical for real applications by enabling 10-50 step sampling instead of 1000, and provides a structured latent space for interpolation.

## Current Understanding

Diffusion models work by learning to reverse a gradual noising process. The forward process adds noise in T steps (typically 1000), and the model learns to predict the noise added at each step, conditioned on the timestep. The training is simple (MSE on noise prediction), but sampling requires iterative denoising.

The connection between diffusion and score matching is crucial: the model implicitly learns the score (gradient of the log-density) at multiple noise levels, and the reverse process implements annealed Langevin dynamics.

Key limitations of the DDPM formulation:
- Slow sampling (1000 steps)
- No explicit latent representation (unlike VAEs)
- The Markovian forward process is restrictive

## Key Concepts

- Forward diffusion (gradual Gaussian noise addition)
- Reverse denoising Markov chain
- Variational bound on log-likelihood
- Connection to denoising score matching
- Noise schedule (linear β_t)
- U-Net with attention for noise prediction
- Importance of the reweighted variational bound

## Open Questions

- What is the optimal noise schedule — is the linear schedule actually best, or does it depend on the data distribution?
- Why does predicting noise ε work better than predicting the original data x_0?
- How does the choice of T (number of diffusion steps) interact with model capacity?
- Is there a unified theory connecting diffusion, score matching, and flow-based models?

## Possible Thesis Ideas

- **Adaptive noise schedules** — learn a data-dependent diffusion schedule that accelerates training and improves sample quality simultaneously
- **Bridging diffusion and discrete token models** — adapting the continuous diffusion framework to discrete data (text, code, structured outputs)

## Next Step

Day 2 should explore score-based models (Song & Ermon, NCSN / SDE) to understand the reverse direction from score matching to diffusion.
