# 2026-08-12 — KV Cache Capstone

Course: LLM Systems
Topic: KV Cache
Stage: Capstone (Day 5)
Confidence: 0.70 → 0.80

## Topic Map

```
Inference Serving (completed)
└── KV Cache (completed, 5d / 15 papers / conf 0.80)
    └── Batching and Scheduling (NEXT →)
```

## Journey Recap

Over 5 days, we built a map of KV cache management across 15 papers, organized around four solution families:

### Day 1 — Quantization (Post-hoc, per-entry)
**Main**: KIVI (2-bit asymmetric quantization — per-channel keys, per-token values, tuning-free)
**Related**: KVSink (attention-sink-aware precision), Fractal KV-Cache (symbolic storage layout)
**Insight**: The KV cache is the dominant memory bottleneck in LLM inference; it grows linearly with sequence length × batch size. Quantization reduces the per-entry bit-width (~5×) with <0.1 PPL degradation. Keys and values have *different* compressibility structures — per-channel for K, per-token for V.

### Day 2 — Eviction (Post-hoc, per-entry removal)
**Main**: Make Each Token Count (learned importance-aware eviction + eviction-aware training)
**Related**: EVICPRESS (joint compression + eviction), StreamingLLM (attention sinks + sliding window)
**Insight**: Eviction is not a monolithic problem — it splits into *what to evict* (importance scoring), *how to make models robust to missing tokens* (eviction-aware training — a selection-centric → training-centric shift), and *how to combine with compression* (EVICPRESS). Attention sinks (first tokens) must always be preserved.

### Day 3 — Offloading (Post-hoc, tier movement)
**Main**: ShadowKV (low-rank key SVD + value cache offload + on-the-fly sparse reconstruction)
**Related**: FlexGen (LP-based multi-tier placement), KVDrive (holistic GPU→DRAM→SSD orchestration)
**Insight**: Offloading doesn't have to mean "move everything and pay PCIe latency." The key cache is low-rank (SVD-compressible to rank 64), so the essential attention info stays GPU-resident while only the *selected* value entries cross the bus. Multi-tier orchestration (GPU → DRAM → SSD) with pipeline scheduling is the systems direction.

### Day 4 — Architectural Redesign (Upstream)
**Main**: DeepSeek-V2 / Multi-head Latent Attention (MLA)
**Related**: GEAR (quantization + low-rank residual + sparse outliers), Palu (post-hoc weight low-rank decomposition)
**Insight**: The frontier labs moved the problem *upstream*: cache one latent per token (d_c=512) instead of per-head K/V — 93.3% KV reduction vs MHA, 5.76× generation throughput. Decoupled RoPE (position-independent shared latent + tiny per-head RoPE key) is the subtle trick that makes latent caches viable. Post-hoc methods become second-order once the cache is 14× smaller by construction.

### Day 5 — Capstone Synthesis (Today)
Synthesizing all four days into a coherent picture, identifying the cross-cutting principle, and refining the frontier for thesis-level work.

---

## Cross-Cutting Patterns

### 1. The Four Pillars Are Complementary, Not Competing

| Pillar | Representative | Compression | When it wins | Cost |
|--------|---------------|-------------|--------------|------|
| Quantization | KIVI, GEAR | 2–8× | Any trained model, drop-in | Approximation error, precision floor |
| Eviction | StreamingLLM, Make Each Token Count | 4–10× | Streaming, long context, importance-skewed | Information loss (permanent) |
| Offloading | FlexGen, ShadowKV, KVDrive | Enables 1M+ ctx on modest GPUs | Memory-exhausted single GPU | PCIe bandwidth, latency |
| Architectural | MLA (DeepSeek-V2) | ~14× (93.3%) | New model training | Requires retraining |

A production system should compose all four: MLA shrinks the cache by design → quantize the remaining latents → evict unimportant tokens → offload the rest. **No existing system composes all four with a learned, adaptive policy** — that is the open systems gap.

### 2. Low-Rankness Is the Unifying Principle

Every strong method exploits the same underlying fact — the KV tensor is low-rank:

- **MLA**: learns the low-rank latent during pretraining (upstream)
- **Palu**: decomposes K/V projection *weights* post-training (data-independent)
- **ShadowKV**: SVD-compresses the key cache *data* at runtime (data-dependent)
- **GEAR**: uses a low-rank matrix as *error correction* for quantization

Four different places to find the same structure. The decision-theoretic question — when to exploit low-rankness in the architecture vs. the weights vs. the runtime data — is itself a research map.

### 3. Key-Value Asymmetry Is Structural, Not Accidental

KIVI quantizes keys per-channel and values per-token. ShadowKV compresses keys via SVD but offloads values. MLA caches a joint latent. Three independent lines of work converge on the same observation: **keys have channel-level/low-rank structure; values are token-dependent content**. Any unified KV manager should treat K and V differently — a principle that transfers directly to MLA latents (position-independent shared part vs. per-head RoPE part).

### 4. Attention Sinks Constrain Every Post-Hoc Method

StreamingLLM showed initial tokens absorb disproportionate attention. KVSink showed they need higher precision under quantization. Make Each Token Count must preserve them under eviction. The open question that survives: **is the attention sink a necessary consequence of Softmax attention, or can it be designed away?** If eliminated, every post-hoc policy gets simpler.

---

## Key Concepts Accumulated

- KV cache: the dominant memory bottleneck; linear in sequence length × batch size
- Asymmetric quantization (per-channel K / per-token V) — KIVI
- Attention sinks: first tokens that must always be preserved (StreamingLLM, KVSink)
- Eviction-aware training: making the model robust to missing tokens
- Attention redistribution: eviction changes the attention distribution of survivors
- Joint compression-eviction (EVICPRESS)
- Low-rank key cache / SVD compression (ShadowKV, rank 64)
- On-the-fly sparse KV reconstruction
- PCIe bandwidth as the offloading bottleneck
- Multi-tier cache hierarchy: GPU HBM → CPU DRAM → SSD
- Multi-head Latent Attention (MLA): one latent per token (d_c=512), 93.3% KV reduction
- Decoupled RoPE: position-independent shared latent + per-head RoPE key
- Post-hoc vs. architectural compression regimes (~2–8× vs. ~14×)
- Low-rankness as the unifying principle (learned latent / weight decomp / data SVD / error correction)
- MHA → MQA → GQA → MLA progression
- MLA retrofit (MHA2MLA line of work)

## Open Questions (Top)

- Can post-hoc low-rank compression close the gap to MLA's ~93% without retraining? (Palu's ~50% suggests training-time adaptation matters)
- Can quantization + eviction + offloading stack *on MLA's latent* — quantize d_c, evict unimportant latents, offload latents to CPU? What are the combined savings?
- Does MLA's latent cache change eviction dynamics — are sink/importance signals computed on the latent meaningful, or must eviction operate on up-projected K/V?
- Is the attention sink a necessary consequence of Softmax, or can architecture remove it?
- For agent workloads (short, tool-interleaved turns): how does KV reuse across turns change the optimal cache policy — and does MLA's tiny cache change the serving calculus (disaggregation, speculative decoding)?
- How does KV cache management interact with MoE expert routing (sparsity-aware caching)?
- What is the optimal tier-placement policy (which layers/heads GPU vs DRAM vs SSD), and can it be learned per-request under SLOs?

## Possible Thesis Ideas (Refined)

1. **Unified learned KV cache manager across all four pillars** — a policy that jointly decides bit-width (quantize), which entries to drop (evict), which tier to place (offload), and whether the latent is compressible (architectural-aware), optimized for SLO-constrained goodput. No existing system composes all four; the state space is large but learnable via RL/offline optimization.

2. **Latent-cache-aware serving stack** — adapt PagedAttention-style block management, preemption, and offloading to MLA's one-latent-per-token format. Serving engines still handle MLA awkwardly; this is a concrete systems gap with immediate deployment value.

3. **Post-hoc MLA conversion (MHA2MLA at LoRA scale)** — a low-cost recipe to convert trained MHA/GQA models to latent KV; the open question is data/FLOPs needed and how close the converted model gets to natively-trained MLA. Directly bridges the ~50% (Palu) → ~93% (MLA) gap.

4. **Agent-aware KV lifecycle** — eviction/offloading policy for multi-turn tool-using agents: system prompts and tool definitions are high-value reusable tokens, intermediate thought tokens are low-value; a tier-aware policy keeping high-value tokens GPU-resident directly serves the user's agents priority.

## Next Step

**Topic completed.** 🎉

Transitioning to **Batching and Scheduling** — the next llm-systems topic (scheduling requests and tokens). It connects naturally: KV cache size determines how many sequences fit in memory, and the scheduler decides how to spend that memory across concurrent requests — the natural continuation of the inference-serving → kv-cache arc. First question: how do serving systems decide *when* to run each request and *how many tokens* to process per step?

---

*This is a capstone/synthesis note — no new papers were read and no web search was performed (per capstone-day policy). It consolidates Days 1–4 (KIVI, Make Each Token Count/StreamingLLM, ShadowKV, MLA + related papers) into the topic map above.*
