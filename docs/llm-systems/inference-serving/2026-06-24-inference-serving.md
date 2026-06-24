# 2026-06-24 — Inference Serving

Course: LLM Systems
Topic: Inference Serving
Stage: Day 3 — Speculative Decoding family
Confidence: 0.60 -> 0.68

## Today's Question

Beyond architectural innovations in scheduling (disaggregation, chunked prefill), how can **model-level techniques** further reduce latency and improve throughput of LLM inference?

## Main Paper

### Metadata

- **Title:** Fast Inference from Transformers via Speculative Decoding
- **Authors:** Yaniv Leviathan, Matan Kalman, Yossi Matias
- **Year:** 2023
- **Venue:** ICML 2023
- **Link:** https://arxiv.org/abs/2211.17192

### Why this paper?

Speculative decoding is one of the most impactful inference optimization techniques post-2022. It fundamentally changes the assumption that autoregressive decoding must be sequential. After covering system-level optimizations (vLLM, DistServe, Sarathi) it's time to understand how model-level parallelism can complement system-level scheduling.

### Core Problem

Standard autoregressive decoding generates one token at a time, each requiring a full forward pass. For large models (70B+), this means memory bandwidth dominates — each token generation reads the entire model weights (~140GB for 70B FP16) from HBM to compute units, produces only one token, and repeats. The arithmetic intensity is terrible: transformers are memory-bound during decode.

The core insight: **a single forward pass on a batch of K tokens costs roughly the same as a single token** (amortized batch processing). So if we can somehow generate K candidate tokens in parallel and verify them in one pass, we can get K× speedup.

### Main Idea

Speculative decoding uses a **small, fast draft model** (e.g., a 125M-parameter model) to propose a sequence of candidate tokens greedily. Then the **large target model** verifies ALL K candidates in a *single* parallel forward pass (using an attention mask that treats the sequence as a batch). The verification uses a rejection sampling scheme — tokens that pass are kept; the first token that fails is discarded and the process restarts from there — guaranteeing that the *output distribution is identical* to the target model's greedy decoding (or even sampling distribution, with appropriate rejection).

Key theoretical guarantee: the method introduces **zero quality degradation** — it produces exactly the same distribution as the target model would, because the rejection sampling corrects any distributional mismatch.

### Technical Details

- **Draft model** (`M_q`): Small, fast model used to generate candidate tokens autoregressively (cheap).
- **Target model** (`M_p`): Large model that verifies candidates in parallel.
- **Speculation length** `K`: Number of tokens to draft. Longer K provides more parallelism but risks lower acceptance rate.
- **Acceptance rate** `β`: Probability that a drafted token is accepted. Depends on the alignment between `M_q` and `M_p`.
- **Walltime speedup** ≈ `(average accepted tokens) × (single token latency of M_p) / (draft latency + one forward pass of M_p)`.
- **Rejection sampling correction**: If `M_q(x) > M_p(x)` for a token, it's accepted with probability `M_p(x)/M_q(x)`; if rejected, a corrected sample is drawn from `(M_p(x) - M_q(x))_+`. This ensures the output distribution exactly matches `M_p`.

### Experiments / Results

- With a 125M draft model + LaMDA target, achieved **2–3× walltime speedup** in standard settings.
- Speedup increases for larger models (more memory-bound → more benefit from batching).
- Speedup degrades when the draft model and target model are poorly aligned (creative/divergent tasks).
- The method is **hardware-agnostic** — works on any GPU, TPU, or CPU setup.

### Limitations

- Requires maintaining and serving a separate draft model (extra memory, deployment complexity).
- Speedup is limited by the draft-target alignment: if the draft model is too weak, acceptance rate drops; if too strong, it's nearly as expensive as the target.
- Effective speculation length `K` is hard to tune dynamically.
- Does not help for **prefill** (first few tokens) — only decode phase.
- Greedy decoding variant is simpler; sampling variant requires more careful rejection correction.

### Connection to Previous Days

Day 1 covered PagedAttention (memory management) and Orca (iteration-level batching). Day 2 covered disaggregation (DistServe) and chunked prefill (Sarathi-Serve). Speculative decoding is orthogonal — it changes *what the model does* during decode rather than *where or when* decode runs. All three optimizations can be combined: speculative decode + PagedAttention + chunked prefill all target different bottlenecks.

### What Changed in the Topic Map

We now have **three axes** of inference optimization:

| Axis | Technique | Bottleneck | Day |
|------|-----------|------------|-----|
| Memory | PagedAttention, KV cache quantization | HBM fragmentation, capacity | 1 |
| Scheduling | Iteration-level batching, disaggregation, chunked prefill | GPU utilization, prefill-decode interference | 1, 2 |
| **Model-level** | **Speculative decoding** | **Sequential decode bottleneck** | **3** |

## Related Papers

### Paper 1: Medusa — Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

- **Authors:** Tianle Cai, Yuhong Li, Zhengyang Geng, et al.
- **Year:** 2024
- **Venue:** arXiv / NeurIPS 2024
- **Link:** https://arxiv.org/abs/2401.04589

**Contribution:** Medusa eliminates the need for a separate draft model by adding **multiple decoding heads** on top of the target model's last hidden state. Each head predicts tokens at different positions (head 1 predicts the next token, head 2 predicts the token-after-next, etc.). The heads are lightweight (MLP layers) and can be trained in a few hours on a single GPU.

**Relation to main paper:** Medusa is a **draft model-free** variant of speculative decoding. Instead of `M_q` being a separate model, it's a few extra parameters on `M_p`. This addresses the main paper's limitation of needing a separate draft model. However, it requires fine-tuning (which not all practitioners want) and doesn't have the same distribution-preserving guarantee.

**Why it matters:** Medusa shows speculative decoding can be practical without serving two models. Combined with vLLM's speculative decoding support, it's becoming production-ready.

**Deep read later?** Only if designing a speculative decoding system. Otherwise, knowing the concept is sufficient.

### Paper 2: Break the Sequential Dependency of LLM Inference Using Lookahead Decoding

- **Authors:** Fu et al.
- **Year:** 2024
- **Venue:** ICML 2024
- **Link:** https://arxiv.org/abs/2402.02057

**Contribution:** Lookahead Decoding uses **Jacobian iteration** to break the autoregressive dependency entirely. Instead of a draft model or extra heads, it generates candidates by **looking ahead** using n-gram pools built from the model's own predictions during a warm-up phase. It maintains a lookahead branch parallel to the main branch and uses n-gram matching to generate candidate continuations.

**Relation to main paper:** Same goal (parallel token generation) but **no draft model** AND **no fine-tuning**. The trade-off is higher memory usage during inference (maintaining n-gram pools) and potentially lower acceptance rates for highly creative generation.

**Why it matters:** Lookahead represents the third family of speculative decoding approaches: draft-model-free AND training-free. It's the most practical for black-box models where you cannot add heads or train a draft model.

**Deep read later?** Yes — the Jacobi iteration approach is conceptually interesting and may combine well with other techniques.

## Current Understanding

Speculative decoding represents a **third axis** of inference optimization, orthogonal to memory management (PagedAttention) and scheduling (disaggregation, chunked prefill). The core insight is elegant: one parallel forward pass on a batch of K tokens costs only marginally more than a single-token forward pass (amortized weight reading), so if we can generate plausible candidates cheaply, we can "batch" the decode step.

The three branches of the approach form a clear trade-off space:

| Approach | Quality guarantee | Extra serving cost | Adoption |
|----------|------------------|-------------------|----------|
| Draft model | Lossless (exact distribution) | Two models to serve | Highest (GPT-4, Gemini) |
| Extra heads (Medusa) | Approximate | Single model + fine-tune | Growing (vLLM) |
| Training-free (Lookahead) | Approximate | N-gram memory overhead | Experimental |

For production systems, the draft model approach (original speculative decoding) is most mature — vLLM and TensorRT-LLM both support it natively. Medusa is attractive for teams that can afford a fine-tuning step. Lookahead is best for scenarios where neither fine-tuning nor a second model is feasible.

The key open question: **can speculative decoding techniques be combined with disaggregated architectures?** In a prefill-disaggregated system, the decode phase runs on dedicated GPUs — speculative decoding could further improve decode GPU efficiency. But the draft model's forward passes also need scheduling, and the KV cache interaction between draft and verification passes needs careful management.

## Key Concepts

- **Speculative decoding:** Using a small model to propose tokens and a large model to verify in parallel
- **Rejection sampling correction:** Mathematically guarantees output distribution match
- **Speculation length (K):** Number of tokens to propose per round
- **Acceptance rate (β):** Fraction of proposed tokens accepted by target model
- **Draft model alignment:** How closely the draft model's distribution matches the target model
- **Medusa heads:** Multiple prediction heads on the last hidden state for draft-free speculation
- **Jacobian iteration:** Breaking autoregressive dependency via fixed-point iteration (Lookahead)
- **N-gram pool:** Cache of frequently occurring continuations used in Lookahead Decoding

## Open Questions

- How does speculative decoding interact with disaggregated inference? If prefill and decode are on separate GPUs, where does the draft model run?
- Can the draft model be dynamically selected per request or per task to maximize acceptance rate?
- Is there a theoretical limit on the acceptance rate given a fixed draft-target compute budget ratio?
- For agent workloads (short, tool-interleaved generations), does the prefill overhead of speculative decoding outweigh the decode savings?
- Can speculative decoding be combined with chunked prefill — or do they compete for the same parallel compute?
- How do MoE models (DeepSeek-V3, Mixtral) change the draft-target trade-off?

## Possible Thesis Ideas

- **Speculative decoding for agent runtimes:** Design a draft model specifically for tool-calling patterns (short, structured generations) and measure the acceptance rate improvement over generic draft models.
- **Unified speculative + disaggregated scheduler:** Extend DistServe's scheduler to assign draft model inference and target verification to different GPU types (e.g., draft on smaller GPUs, verification on H100s).
- **Adaptive speculation length:** Learn to predict optimal K per request based on task difficulty, draft acceptance rate, and system load — then dynamically tune K.
- **Speculative KV cache reuse:** Can the KV cache computed during the draft phase be partially reused during verification to reduce redundant computation?

## Next Step

Continue on Inference Serving. Next direction should be **quantization for serving** (AWQ, GPTQ, FP8) — how quantization affects serving throughput and quality, and how it interacts with the three axes covered so far. Alternatively, explore **continuous batching improvements** in vLLM (v1 updates, scheduler optimizations).

Confidence update: 0.60 → 0.68. Speculative decoding adds a useful third axis but I need to see it in practice (vLLM integration, production benchmarks) before reaching 0.75+.
