# 2026-07-23 — Score-Based Models

Course: Generative Models
Topic: Score-Based Models
Stage: Day 4 — Manifold structure, convergence theory, and weighting analysis
Confidence: 0.72 → 0.78

## Today's Question

How do score-based generative models learn data distributions supported on low-dimensional manifolds, and what theoretical guarantees govern score estimation and loss weighting?

## Main Paper

### Metadata

- Title: Score-based generative models learn manifold-like structures with constrained mixing
- Authors: Li Kevin Wenliang, Ben Moran
- Year: 2023
- Venue: NeurIPS 2022 Workshop on Score-Based Methods
- Link: https://arxiv.org/abs/2311.09952

### Why this paper?

Days 1–3 covered consistency distillation, the unified SDE framework (Song 2021), and practical/high-order score matching. But a fundamental question remains: **how does score estimation actually work when data lies on a low-dimensional manifold?** This is not a niche concern — real data (images, text, audio) all concentrate near low-dimensional manifolds. Understanding how SBMs handle this geometry is essential for the next topic (Sampling) and for diagnosing failure modes.

### Core Problem

Standard score matching theory assumes the data distribution has full-dimensional support in ambient space. However, real-world data typically lies on or near a low-dimensional manifold embedded in a high-dimensional ambient space. When the noise level is low, the score function becomes approximately normal to the manifold (pointing toward the manifold), but parallel to the manifold, the score should mix samples. How do trained SBMs actually handle these two regimes?

### Main Idea

The authors analyze a trained score model through its **local linear approximations** — specifically, the subspace spanned by the Jacobian of the score function (the local feature vectors). They study how this subspace evolves during the reverse diffusion process:

1. **Off-manifold direction (denoising):** The score field behaves as if there's an energy function — it has normal projections that point toward the manifold. This is consistent with the standard intuition that score matching learns the gradient of the log-density.

2. **In-manifold direction (mixing):** The score field has a **non-conservative component within the manifold**. This is surprising — it means the learned score field is **not simply the gradient of a potential energy** restricted to the manifold. The non-conservative component actively mixes samples, enabling the model to generate diverse samples from the same mode.

### Key Technical Details

- **Local dimensionality:** As noise decreases, the local dimensionality of the score's feature subspace increases and becomes more variable across different sample sequences. This suggests the model adaptively allocates representation capacity.
- **Subspace overlap:** At each noise level, the subspace spanned by local features overlaps with an effective density function — the score model encodes density information in its feature geometry.
- **Constrained mixing:** The non-conservative in-manifold component is constrained — it cannot be arbitrarily large because the off-manifold denoising component dominates at low noise.

### Research Takeaway

This paper provides a geometric picture of what score models actually learn: they learn a **constrained mixing field** that can flexibly transport samples within the data manifold while maintaining the denoising structure in off-manifold directions. This explains why score models are simultaneously good at denoising (off-manifold) and at generating diverse samples (in-manifold mixing).

### Modern perspective (2026)

This line of analysis has since been extended in multiple directions. The Burgers equation analysis (covered Day 3) connects the shock fronts in the score field to mode boundaries — the "speciation transitions" align with the manifold structure boundaries. The constrained mixing observation also foreshadows more recent work on score-conditioning and flow matching, where the vector field's non-conservative component is made explicit through optimal transport formulations.

## Related Papers

### Paper 1: Implicit Score Matching Meets Denoising Score Matching

- Title: Implicit score matching meets denoising score matching: improved rates of convergence and log-density Hessian estimation
- Authors: Konstantin Yakovlev, Anna Markovich, Nikita Puchkin
- Year: 2025
- Link: https://arxiv.org/abs/2512.24378
- arXiv ID: 2512.24378

**Contribution:** Provides the first unified convergence analysis of both implicit score matching (ISM) and denoising score matching (DSM) under the low-dimensional manifold assumption. Proves that ISM adapts to intrinsic dimension and achieves the same rates as DSM. Crucially, shows that both methods allow **log-density Hessian estimation without the curse of dimensionality** via simple differentiation — justifying ODE-based sampler convergence.

**Relation to main paper:** Where Wenliang & Moran provide an empirical/geometric picture of manifold learning in SBMs, Yakovlev et al. provide the complementary **theoretical convergence guarantees** under manifold assumptions. The Hessian estimation result is especially relevant — it justifies why ODE-based samplers (probability flow ODE) work well in practice despite the manifold structure.

**Why it matters:** Bridges the gap between empirical observations of manifold learning and rigorous convergence theory. The dimension-free Hessian estimation result is a strong theoretical foundation for the practical success of score-based diffusion ODEs.

### Paper 2: Why Heuristic Weighting Works

- Title: Why Heuristic Weighting Works: A Theoretical Analysis of Denoising Score Matching
- Authors: Juyan Zhang, Rhys Newbury, Xinyang Zhang, Tin Tran, Dana Kulic, Michael Burke
- Year: 2025
- Link: https://arxiv.org/abs/2508.01597
- arXiv ID: 2508.01597

**Contribution:** Identifies that **heteroskedasticity** is an inherent property of the denoising score matching objective. Derives optimal weighting functions for generalized, arbitrary-order DSM losses. Shows that the widely used heuristic weighting function (from DDPM/EDM) arises as a **first-order Taylor approximation** to the trace of the expected optimal weighting. Demonstrates that the heuristic weighting, despite its simplicity, can achieve **lower variance** than the optimal weighting with respect to parameter gradients, explaining its empirical effectiveness.

**Relation to main paper:** Both papers address fundamental questions about the score matching objective. Wenliang & Moran ask what geometry the learned score induces; Zhang et al. ask what loss weighting produces the best score estimates. The finding that heuristic weighting's lower variance helps training connects directly to the question of how score models can reliably learn manifold structure despite noise.

**Should be deep-read later?** Yes, for anyone designing new diffusion training procedures or trying to understand the connection between loss weighting and sample quality.

## Current Understanding

Score-based models now have a **five-layer understanding**:

1. **Training objective:** Denoising score matching (DSM) trains a neural network to predict the score (gradient of log-density) at varying noise levels. The weighting function in the DSM loss, long treated as heuristic, has a principled foundation connected to heteroskedasticity and variance minimization (Zhang et al., 2025).

2. **Unified SDE framework:** All score-based models can be described as learning a reverse SDE that reverses a forward diffusion process (Song et al., 2021). The probability flow ODE connects score estimation to likelihood computation and deterministic sampling.

3. **Practical training methods:** Sliced score matching (Song et al., 2019) makes deep score models feasible by reducing Hessian trace estimation from O(d²) to O(d) via random projections. High-order denoising score matching (Lu et al., 2022) is needed for maximum likelihood of the ODE.

4. **Geometric structure (new — Day 4):** The learned score field has a two-component structure — a conservative denoising component in off-manifold directions, and a non-conservative mixing component within the data manifold (Wenliang & Moran, 2023). This explains how score models simultaneously denoise and generate diverse samples.

5. **Theoretical guarantees (new — Day 4):** Both ISM and DSM adapt to intrinsic data dimension with the same convergence rates, and enable dimension-free log-density Hessian estimation (Yakovlev et al., 2025), providing theoretical justification for ODE-based sampler quality.

## Key Concepts

- **Local feature subspaces:** The Jacobian of the score function spans different subspaces at different noise levels and spatial locations; these subspaces encode geometric information about the data manifold
- **Constrained mixing:** The non-conservative in-manifold component of the learned score field that mixes samples while maintaining denoising structure off-manifold
- **DSM heteroskedasticity:** The inherent property that DSM loss variance varies across noise levels, motivating noise-level-specific weighting
- **Optimal weighting function:** Principled weight that minimizes DSM loss variance, derived from the heteroskedastic formulation
- **Dimension-free Hessian estimation:** Both ISM and DSM estimate log-density Hessians without exponential dependence on ambient dimension under manifold assumptions

## Open Questions

- How does the constrained mixing mechanism interact with classifier-free guidance (CFG)? CFG scales up the score, but does it amplify the conservative or non-conservative component?
- Can the non-conservative mixing component be explicitly parameterized and controlled for downstream tasks like interpolation or style mixing?
- Does the heuristic weighting function's lower variance property hold for very large models (billions of parameters)?
- How does the manifold learning capability of score models depend on network architecture (U-Net vs Transformer)?
- Can the dimensional adaptation (local dimensionality increasing with decreasing noise) be used as a diagnostic for underfitting?

## Possible Thesis Ideas

1. **Manifold-aware score training** — explicitly regularize the non-conservative in-manifold component to improve sample diversity or denoising quality
2. **Hessian-guided sampler design** — use the dimension-free Hessian estimation result (Yakovlev et al.) to design adaptive ODE solvers that adjust step size based on local curvature
3. **Weighting function search** — extend the DSM weighting analysis to flow matching and consistency models, potentially discovering better loss weighting for each framework
4. **Geometric measure of model quality** — use the local dimensionality of the score's feature subspace as a training quality metric (analogous to intrinsic dimension estimation)

## Next Step

Day 5 will focus on a representative application or extension of score-based models — possibly conditional score modeling, or score-based models for inverse problems. The confidence (0.78) is approaching the 0.80 threshold for advancing to the next topic (Sampling).
