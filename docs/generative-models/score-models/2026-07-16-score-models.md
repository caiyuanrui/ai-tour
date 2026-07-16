# 2026-07-16 — Score-Based Models

Course: Generative Models
Topic: Score-Based Models
Stage: Day 3 — Practical Score Estimation & Theoretical Structure
Confidence: 0.60 -> 0.72

## Today's Question

How do we actually estimate the score function in practice, and what theoretical structure does the learned score field exhibit?

## Main Paper

### Metadata

- **Title:** Sliced Score Matching: A Scalable Approach to Density and Score Estimation
- **Authors:** Yang Song, Sahaj Garg, Jiaxin Shi, Stefano Ermon
- **Year:** 2019
- **Venue:** UAI 2019
- **Link:** https://arxiv.org/abs/1905.07088

### Why this paper?

The previous two days established **what** score matching is (Day 2 — SDE framework) and **why** consistency is possible (Day 1 — Consistency Models). But neither addressed the core practical question: how do we actually train a neural network to estimate ∇log p(x)? The original score matching objective requires computing the trace of the Hessian of log p(x; θ), which is O(d²) per data point — prohibitive for high-dimensional data like images. This paper provides the solution that made deep score-based models feasible.

### Core Problem

Implicit (explicit) score matching requires minimizing:

```
J(θ) = 𝔼_{p_data}[ ½‖s_θ(x) - ∇log p_data(x)‖² ]
```

But ∇log p_data(x) is unknown (we only have samples). The equivalent **Fisher divergence** formulation avoids this:

```
J_ISM(θ) = 𝔼_{p_data}[ tr(∇_x s_θ(x)) + ½‖s_θ(x)‖² ]
```

The trace term tr(∇_x s_θ(x)) requires computing the full Jacobian of s_θ (a vector field) — that's O(d²) computation where d is the data dimensionality. For a 256×256 image (d=196,608), this is intractable.

Denoising score matching (Vincent 2011) avoids the trace via a Parzen-window approximation, but introduces bias and only approximates the true score.

### Main Idea

**Sliced Score Matching (SSM):** Instead of matching the full score vector, project the score difference onto random directions v ~ p_v (e.g., standard Gaussian) and match the **projected** scores:

```
J_SSM(θ) = 𝔼_{p_data} 𝔼_v[ ½‖v^T s_θ(x) - v^T ∇log p_data(x)‖² ]
```

This simplifies to:

```
J_SSM(θ) = 𝔼_{p_data} 𝔼_v[ v^T ∇_x s_θ(x) v + ½(v^T s_θ(x))² ]
```

The key term v^T ∇_x s_θ(x) v is a **Hessian-vector product** — computable in O(d) time using reverse-mode automatic differentiation (forward of backward, or double backward). This is the same technique used in curvature estimation for optimization (e.g., Hessian-free optimization).

### Technical Details

1. **Random projections:** Sample v ~ N(0, I_d) — one random direction per data point per training step. The expectation over v means each gradient step averages over random projections.

2. **Hessian-vector products:** v^T ∇_x s_θ(x) v = v^T H_{s_θ}(x) v where H is the Hessian of each output component. Computed efficiently as ∇_x(v^T s_θ(x))·v — first compute the inner product, then take its gradient w.r.t. x and dot with v.

3. **Consistency and asymptotic normality:** The paper proves that the SSM estimator is consistent and asymptotically normal as n → ∞, under standard regularity conditions. The Fisher information matrix of the SSM estimator is a sliced version of the full Fisher information.

4. **Connection to implicit distributions:** SSM can estimate scores for implicit distributions (distributions defined only by a sampling process, not a density). This enables score-based training of models like Wasserstein Auto-Encoders and variational inference with implicit posteriors.

5. **Deep energy-based models:** The paper demonstrates learning deep EBMs (energy-based models) using SSM, showing that score estimation enables unnormalized density estimation for complex, high-dimensional distributions.

### Research takeaway

Sliced score matching transformed score matching from a theoretically elegant but computationally impractical technique into a practical tool. Every subsequent score-based generative model — including the NCSN paper published the same month (Song & Ermon 2019) — uses SSM or denoising score matching in practice. The random-projection insight is surprisingly simple: you don't need the full Hessian trace; random directional derivatives suffice. This is reminiscent of random projection methods throughout ML (JL lemma, randomized SVD, sketch-based optimization).

### Modern perspective

SSM remains the standard approach for training score-based models in continuous state spaces. The key open question: does the random-projection approximation introduce bias in certain regimes (e.g., near zero-score regions, or at very high noise levels)? Recent theoretical work (2025-2026) on implicit vs. denoising score matching suggests the gap between these objectives matters more than previously thought — see the related paper on high-order score matching below.

---

## Related Papers

### Paper 1: High-Order Denoising Score Matching (Maximum Likelihood Training for Score-Based Diffusion ODEs)

- **Authors:** Cheng Lu, Kaiwen Zheng, Fan Bao, Jianfei Chen, Chongxuan Li, Jun Zhu
- **Year:** 2022 (ICML 2022)
- **Link:** https://arxiv.org/abs/2206.08265

**Contribution:** Proves that matching the **first-order score** alone is insufficient to maximize the likelihood of the probability flow ODE. There is a gap between the score-matching objective and the maximum likelihood objective for the ODE. The paper shows this gap can be closed by controlling **first, second, and third-order score matching errors**, and presents a practical high-order denoising score matching method.

**Relation to main paper:** While SSM addresses the computational challenge of **first-order** score matching (trace estimation), this paper addresses the **fundamental statistical limitation** of first-order matching — even with perfect first-order score estimates, the ODE likelihood is suboptimal because the ODE's likelihood depends on the score's Jacobian (divergence). High-order matching fills this gap.

**Why it matters:** This paper connects two previously separate objectives — score matching and maximum likelihood — and explains why models trained with score matching sometimes have poor likelihood despite excellent sample quality. It also provides practical high-order training methods.

**Should deep-read later?** Yes — the theoretical connection between score matching order and ODE likelihood is directly relevant to understanding the fundamental capabilities and limits of score-based models.

### Paper 2: Score Shocks — The Burgers Equation Structure of Diffusion Generative Models

- **Author:** Krisanu Sarkar
- **Year:** 2026 (arXiv)
- **Link:** https://arxiv.org/abs/2604.07404

**Contribution:** Provides a completely new analytical lens on the score field in diffusion models. For Variance-Exploding (VE) diffusion, the score obeys a **viscous Burgers equation** — a canonical PDE from fluid dynamics describing shock formation. This reveals that **speciation transitions** (the separation of modes during reverse diffusion) correspond to shock fronts in the score field. The paper derives a local tanh profile for the score near binary mode boundaries, and proves that score errors are **exponentially amplified** across these layers.

**Relation to main paper:** SSM shows how to compute the score; this paper shows what the learned score field **looks like** from a PDE perspective. The Burgers equation framework explains why score estimation is so critical near inter-mode boundaries — small errors in the score are amplified exponentially, leading to mode dropping or spurious modes.

**Why it matters:** This offers a fundamentally different way to understand diffusion models — not as a probabilistic model with forward/reverse SDEs, but as a PDE system where generation is the time-reversal of a shock-forming process. This could lead to new algorithms that exploit the Burgers structure (e.g., using shock-capturing numerical methods for sampling).

**Should deep-read later?** Conditionally yes — if pursuing theoretical work on diffusion model dynamics, this is essential. For practical modeling, the key insight (exponential error amplification at mode boundaries) is already actionable.

---

## Current Understanding

The score-models map now has three complementary layers:

1. **Practical score estimation** (today — SSM): Score matching is made tractable via random projections, reducing the O(d²) Hessian trace to O(d) Hessian-vector products. This is the computational workhorse behind all score-based models.

2. **Statistical limitations** (related paper 1): First-order score matching has a fundamental gap to maximum likelihood for ODE-based sampling. High-order matching (second and third derivatives) is needed to close this gap — but is more computationally expensive and may not improve sample quality, only likelihood.

3. **Physical/PDE structure** (related paper 2): The score field is not arbitrary — it obeys Burgers equation dynamics, with shock-like structures at mode boundaries. This explains the phenomenon of "speciation" (modes separating during generation) and why score errors near these boundaries are so damaging.

Together with the previous days, the picture is:

| Layer | Paper | Key Insight |
|-------|-------|-------------|
| Unification | Score-Based SDE (Day 2) | All diffusion IS score estimation |
| Single-step limit | Consistency Models (Day 1) | Learn a direct x_T → x_0 map |
| Computation | Sliced Score Matching (Day 3) | Random projections make O(d) feasible |
| Theory bound | High-Order DSM (Rel 1) | 1st order insufficient for MLE |
| Physical structure | Score Shocks (Rel 2) | Score field = Burgers PDE, shock fronts at mode boundaries |

**Confidence update: 0.60 → 0.72** (+0.12)

The increase reflects understanding the practical estimation machinery and its limitations. The remaining gap (0.28) is mainly: (a) precise understanding of score matching convergence rates under various noise schedules, (b) how score estimation quality degrades in very high dimensions, and (c) whether there exist alternative objectives that avoid the likelihood-quality tradeoff entirely.

## Open Questions

1. **SSM bias:** Does the random-projection approximation in SSM introduce systematic bias for certain data distributions (e.g., sparse or highly multimodal)? The expectation over v is unbiased only in expectation per sample — but with finite v per step, what is the convergence rate?

2. **High-order practical cost:** High-order score matching (2nd/3rd order) is theoretically appealing but requires expensive higher-order gradients. Are there efficient approximations (e.g., Hutchinson-style trace estimators for the Hessian) that make it practical?

3. **Burgers ↔ score matching:** If the score field satisfies Burgers dynamics, can we train models to directly predict the shock structure (mode interfaces) rather than the full score? This would efficiently allocate model capacity to the most critical regions.

4. **Quality vs. likelihood revisited:** High-order matching improves likelihood but may not improve sample quality. Conversely, low-order matching produces good samples with poor likelihood. Is this a fundamental property of score-based models, or is there a unified objective that achieves both?

5. **How does score estimation scale with dimensionality?** The SSM projection works in O(d), but the number of random projections needed for a good estimate might grow with d. Is there a dimension-free bound?

## Possible Thesis Ideas

1. **Efficient high-order score matching via randomized trace estimation** — extend SSM's random-projection idea from the Hessian-vector product to the full Hessian trace, enabling practical 2nd-order score matching at near-1st-order cost. Use Hutchinson's trace estimator with Rademacher random vectors to approximate the divergence of the score Jacobian (tr(J_s)) instead of computing it explicitly.

2. **Burgers-constrained score models** — if the score field obeys a known PDE (Burgers equation), impose this as a physics-informed loss during training. This would regularize the score to satisfy the known PDE structure, potentially reducing the required model capacity and improving out-of-distribution generalization.

3. **Spectral analysis of score estimation** — analyze score matching convergence in the eigenbasis of the score's Jacobian. The Burgers equation viewpoint suggests that the score's behavior is dominated by a low-dimensional set of modes (those that will form shocks). Perhaps score estimation can be decomposed into "important" and "unimportant" directions, enabling adaptive computation allocation.

## Next Step

Next session on score-models: explore the theoretical foundations of convergence rates for score matching — "Score-based generative models learn manifold-like structures with constrained mixing" (Li & Moran 2023) or the 2025-2026 work on implicit vs. denoising score matching rates. Also consider whether to advance to the "Sampling" topic next (current days_spent = 3, confidence = 0.72 — need 0.80 or 5 days to advance; one more day likely needed).
