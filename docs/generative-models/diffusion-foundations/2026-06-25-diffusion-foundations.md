# 2026-06-25 — Diffusion Foundations (Day 4)

Course: Generative Models
Topic: Diffusion Foundations
Stage: Day 4 — From Theory to Practice: Latent Diffusion
Confidence: 0.78 → 0.82

## Today's Question

How do diffusion foundations translate into a practical text-to-image system — and what structural innovations (latent space, conditioning, cross-attention) were needed to make diffusion models useful at scale?

## Main Paper

### Metadata

- **Title:** High-Resolution Image Synthesis with Latent Diffusion Models (LDM / Stable Diffusion)
- **Authors:** Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn Ommer
- **Year:** 2022
- **Venue:** CVPR 2022
- **Link:** https://arxiv.org/abs/2112.10752

### Why this paper?

We've covered the three theoretical pillars: DDPM (training objective), NCSN/SDE (score matching), and EDM (design space). LDM is the bridge from theory to the real world — the paper that made diffusion models practical for text-to-image generation at scale. It directly addresses the central open question from Day 3: how to adapt diffusion to a compressed latent space where noise statistics differ from pixel space. Understanding LDM is essential for modeling where modern generative AI actually operates.

### Core Problem

Diffusion models in pixel space are computationally prohibitive for high-resolution images:
- Generating a 1024×1024 image requires processing millions of pixels through a large U-Net per step
- Each denoising step is O(N) where N = pixels × channels
- 1000 steps × millions of pixels is infeasible for interactive use
- Previous approaches (DALL·E, VQ-VAE-2) used autoregressive models in latent space, but these have different failure modes (accumulated error, limited diversity)

### Main Idea

Two-stage generation:

1. **Perceptual compression** (stage 1): Train a VQ-VAE or VAE that compresses the image by a factor of ~48 (256×256 → 64×64 latent), preserving perceptual quality but discarding high-frequency details.
2. **Diffusion in latent space** (stage 2): Train a diffusion model in the compressed latent space, where it can operate efficiently with 1000× less computation per step.

The second stage uses a U-Net architecture augmented with **cross-attention layers** for conditioning on text (via CLIP text encoder), layout, or other modalities.

### Technical Details

**VAE vs VQ-VAE:**
- They found VQ-VAE (discrete latent) produced reconstructions with poor perceptual quality
- A VAE with KL regularization (similar to β-VAE, β ≈ 0.1) preserved texture and high-frequency detail much better
- The VAE downsampling factor f = 2^m is the key hyperparameter: f=4 (4× compression) for fine-grained generation, f=32 for extremely efficient generation
- Perceptual loss (LPIPS) + discriminator (GAN) loss in VAE training — critical for reconstruction quality

**Cross-Attention Conditioning:**
- Standard U-Net layers remain feed-forward (conv + attention)
- Between the main U-Net layers, inserted cross-attention layers attend to the conditioning signal

```
Q = W_Q · φ(z_t),   K = W_K · c,   V = W_V · c
Attention(Q, K, V) = softmax(QK^T / √d) · V
```

- c is the conditioning vector (CLIP text embedding, segmentation mask, edge map)
- Cross-attention is inserted at multiple resolution levels
- Classifier-free guidance (CFG) is used during sampling: unconditional and conditional score are combined
- CFG is trained by randomly dropping the conditioning signal (10% probability)

**Architecture diagram:**
```
Text: "a photo of a cat" → CLIP Text Encoder → τ_θ (transformer)
                                              ↓
Latent z_t (64×64) → U-Net (with cross-attn) → ε_θ(z_t, t, τ_θ)
                                         ↑
                                  Noise schedule σ(t)
```

**Training:**
- Same ε-prediction MSE loss as DDPM, but operating on latent space
- Noise is added to latents, not pixels (the VAE handles perceptual compression)
- The loss is not weighted in the latent space differently — standard MSE works

**Sampling:**
- Uses DDIM or PNDM (pseudo-numerical) samplers, not the Heun 2nd-order from EDM
- The latent space changes the noise dynamics enough that EDM's preconditioning doesn't transfer directly
- CFG scale (usually 3-7) controls conditioning strength: higher → more aligned with text but less diverse

**Architecture specifics:**
- U-Net backbone similar to pixel-space models but adapted for latent dimension (typically 4 or 8 channels)
- Self-attention at 32×32 and 16×16 resolution in latent space
- Cross-attention to conditioning at 64×64 to 8×8 (multi-scale)
- Parameters: ~860M for U-Net, much smaller than Imagen's 3B

**Limitations:**
- The VAE reconstruction bottleneck limits fine details (fingers, text, faces at small scale)
- Two-stage training is complex: VAE must be trained first, then diffusion
- The latent space is not a metric space — interpolations in the latent correspond to smooth image transitions but aren't linear
- Cross-attention adds parameters proportional to conditioning length, limiting extremely long prompts

### Key Results

| Dataset | Setup | FID | IS |
|---------|-------|-----|----|
| MS-COCO 256×256 | LDM-8 (f=8) | 8.44 | — |
| MS-COCO 256×256 | LDM-4 (f=4) | 9.62 | — |
| ImageNet 256×256 class-cond | LDM-4 | 5.33 | — |
| LAION text-to-image | Stable Diffusion (LDM) | — | — |

More importantly, LDM demonstrated:
- **Super-resolution** in latent space
- **Inpainting** with masked conditioning
- **Semantic synthesis** from segmentation maps
- All from the same model architecture with different conditioning signals

### Research takeaway

LDM's key insight is that **perceptual compression and semantic generation are separable problems**. A VAE can handle the lossy compression of perceptual details; the diffusion model only needs to learn the underlying semantic distribution. This modular separation makes diffusion models practical at scale. Cross-attention provides a universal conditioning interface that generalizes across modalities.

### Modern perspective (2026)

Stable Diffusion (SD 1.x / 2.x) was directly based on LDM. SD 3 and Flux moved to MM-DiT (dual-stream transformers) and flow matching, but the two-stage architecture (VAE + latent generator) remains standard. LDM's innovations — especially cross-attention conditioning — are now universal across all image generation models. The key limitation (VAE bottleneck for fine details) is still actively researched; newer VAE/VQ-VAE architectures (SD3's 16-channel latent, consistency decoders) address it.

## Related Papers

### Paper 1: "Hierarchical Text-Conditional Image Generation with CLIP Latents" (DALL·E 2)

- **Authors:** Aditya Ramesh, Prafulla Dhariwal, Alex Nichol, Casey Chu, Mark Chen
- **Year:** 2022
- **Venue:** arXiv:2204.06125
- **Role:** Competing approach — uses diffusion in image space, not latent space

**Contribution:** DALL·E 2 (unCLIP) uses a completely different architecture:
1. A prior model (autoregressive or diffusion) maps CLIP text embeddings → CLIP image embeddings
2. A diffusion decoder (similar to GLIDE) generates images conditioned on the CLIP image embeddings
3. No explicit text encoder — all conditioning flows through CLIP's shared embedding space

**Relation to main paper (LDM):** Both solve the same problem (text-to-image generation) but with opposite philosophies. LDM compresses pixels first (VAE), then generates in latent space. DALL·E 2 generates in pixel space but compresses semantic information first (CLIP prior). LDM's cross-attention is more flexible (any conditioning signal); DALL·E 2's CLIP embedding is more semantically structured.

**Why it matters:** DALL·E 2 demonstrated that text-to-image was viable at production quality. Its unCLIP approach influenced later methods (e.g., Parti). The CLIP prior idea (separating semantics from pixels) is related to LDM's separation insight but achieved through different means.

### Paper 2: "Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding" (Imagen)

- **Authors:** Chitwan Saharia, William Chan, Saurabh Saxena, Lala Li, Jay Whang, Emily Denton, et al.
- **Year:** 2022
- **Venue:** NeurIPS 2022 / arXiv:2205.11487
- **Role:** Competitor — pixel-space diffusion + large LM text encoder

**Contribution:** Imagen uses pure pixel-space diffusion (no VAE bottleneck) but with a critical twist:
1. **Massive text encoder**: Uses a frozen T5-XXL (11B parameters) for text understanding — argues that the text encoder matters more than the image generation architecture
2. **Cascaded generation**: Three U-Nets at increasing resolutions — base model (64×64) → super-resolution 1 (256×256) → super-resolution 2 (1024×1024)
3. **Dynamic thresholding**: Clips high-variance samples during conditioning to prevent artifacts

**Relation to main paper (LDM):** LDM and Imagen reach opposite conclusions about the right approach. LDM says "compress pixels, use small text encoder." Imagen says "use large text encoder, keep pixels." In practice, LDM's approach won — Stable Diffusion based on LDM is used far more than any Imagen successor — because the computational efficiency of latent space outweighed Imagen's better text understanding.

**Why it matters:** Imagen's key lesson is that text understanding quality constrains generation quality. The T5-XXL encoder gave Imagen superior compositional ability (rare objects, complex scenes). But the cascaded generation approach proved too expensive and hard to train. Modern models (SDXL, SD3) combine LDM's latent space with improved text encoders.

## Current Understanding

The diffusion foundations map now has a complete four-layer structure:

| Layer | Core Paper | Key Function |
|-------|-----------|-------------|
| **Training objective** | DDPM (Ho 2020) | ε-prediction MSE, reweighted ELBO |
| **Theoretical lens** | NCSN + SDE (Song 2019/2021) | Score matching, probability flow ODE |
| **Design principles** | EDM (Karras 2022) | Preconditioning, design space, ODE solver |
| **Practical architecture** | LDM (Rombach 2022) | VAE compression + cross-attention conditioning |

The core insight connecting all four layers: diffusion models succeed because they separate **where** learning happens (training = simple denoising MSE) from **how** generation proceeds (sampling = any ODE/SDE solver). LDM added the crucial third separation: perceptual compression and semantic generation are independent. This modularity explains why diffusion models became the dominant generative paradigm.

Standing on this foundation, the next steps are clear: score-based models (connecting score matching to denoising more formally), flow matching (the successor to diffusion), and faster samplers (DPM-Solver, consistency models).

## Key Concepts

- Latent diffusion: two-stage generation (VAE + diffusion generator)
- Perceptual compression factor (downsampling f = 2^m)
- Cross-attention conditioning: Q = W_Q · φ(z_t), K = W_K · c, V = W_V · c
- Classifier-free guidance (CFG): combine unconditional and conditional score
- VAE with perceptual loss + discriminator for high-quality reconstruction
- Modular separation: perceptual vs semantic generation
- Cascaded generation vs single-stage latent generation
- T5-XXL text encoder vs CLIP text encoder

## Open Questions

- **Latent space preconditioning:** EDM's systematic preconditioning doesn't transfer to latent space. How should c_skip, c_out, c_in, c_noise be redesigned for VAE latents with different noise statistics?
- **Optimal downsampling factor:** What is the theoretically optimal compression rate f? It depends on dataset, but there's no principled way to determine it.
- **Cross-attention scaling:** Cross-attention's O(L · T) complexity (L=latent tokens, T=text tokens) limits both context length and image resolution. Can it be replaced or augmented?
- **VAE bottleneck:** Is the VAE reconstruction error the fundamental limit on image quality, or can it be overcome with better generators?
- **Text understanding vs latent space:** Imagen's T5-XXL gave better text comprehension. Modern latent models (SDXL, SD3) use dual encoders. What's the right trade-off?

## Possible Thesis Ideas

- **Latent-space preconditioning theory** — Extend EDM's analytic preconditioning from pixel space to VAE latent space, deriving principled noise schedules and conditioning functions for latent diffusion training
- **Cross-attention-free conditioning** — Replace cross-attention with adapter-style conditioning (ControlNet-like) for better scalability to long prompts and high resolutions
- **Unified model for all conditioning types** — A single diffusion backbone that handles text, layout, segmentation, and image conditioning through a unified interface, using cross-attention as the universal connector
- **End-to-end latent diffusion** — Train the VAE and diffusion generator jointly end-to-end, removing the reconstruction bottleneck

## Next Step

This completes the **Diffusion Foundations** topic. The next topic in progression is **Score-Based Models**, which formalizes the connection between denoising and score estimation. From the foundations covered, score-based models provide the theoretical lens that unifies diffusion, denoising, and energy-based models.
