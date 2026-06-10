# 2026-06-10 — Inference Serving

Course: llm-systems  
Topic: inference-serving  
Stage: 1 / ~5  
Confidence: 0.00 -> 0.45

## Today's Question

How are LLM inference systems optimized for throughput and latency?

## Main Paper

### Metadata

- **Title:** LLM Inference Serving: Survey of Recent Advances and Opportunities
- **Authors:** Baolin Li, Yankai Jiang, Vijay Gadepally, Devesh Tiwari
- **Year:** 2024
- **Venue:** arXiv 2407.12391
- **Link:** https://arxiv.org/abs/2407.12391

### Why this paper?

First day of the topic — a survey that maps the entire field is the best place to start. Covers KV cache management, computation scheduling, deployment strategies, and emerging areas.

### Core Problem

LLM inference is fundamentally different from traditional ML inference: autoregressive decoding has two phases (prefill + decode) with very different compute/memory profiles. The KV cache grows dynamically per request, is huge (GBs per sequence), and causes severe fragmentation. Serving systems must balance throughput, latency, and cost simultaneously — the "inference trilemma."

### Main Idea

Organize the serving optimization landscape into four categories:

1. **Memory management & caching** — PagedAttention, KV cache compression, long-context support
2. **Computation scheduling** — continuous batching, disaggregated prefill/decode, model parallelism
3. **Cloud deployment** — serverless, spot instance recovery, autoscaling
4. **Emerging areas** — speculative decoding, quantization-aware serving, multi-LM orchestration

The survey provides a structured taxonomy of ~40 systems published between Jan 2023 and June 2024.

### Technical Details

**KV cache problem:** For a single sequence of length L with h heads and d dimensions per head, the KV cache size = 2 × L × h × d × (bytes per element). For Llama-2 70B (h=64, d=128), L=4096 gives ~256 MB per sequence. At 8 concurrent requests, that's 2 GB — and it grows linearly with L and batch size.

**Key innovations by category:**

| Category | Representative System | Idea |
|----------|----------------------|------|
| KV management | vLLM / PagedAttention | Non-contiguous block-based KV cache with page tables |
| KV management | vAttention | Contiguous virtual memory via demand paging |
| Batching | Orca | Token-level (continuous) batching: new requests join at any decode step |
| Batching | Sarathi-Serve | Chunked prefill interleaved with decode → no pipeline bubbles |
| Disaggregated | Splitwise / DistServe | Separate prefill and decode on different GPU pools |
| Compression | KIVI / Gear / MiniCache | Asymmetric quantization, low-rank error compensation, layer merging |

**Continuous batching** is now industry standard (vLLM, TGI, TensorRT-LLM all implement it). Prior systems batched at request granularity (coarse). Orca showed that scheduling at the **iteration level** — adding new requests to the batch as soon as one finishes — improves throughput by up to 36.9× over naive batching.

### Results

- PagedAttention (vLLM): **2–4× throughput gain** over FasterTransformer and Orca at equal latency; near-zero memory waste.
- Continuous batching: **up to 36.9×** over naïve static batching (Orca OSDI'22).
- Disaggregated inference: **1.3–2.0×** throughput improvement with separate prefill/decode instances.
- KV cache compression: **4-bit quantization** (KIVI) with minimal quality loss; **3–5× memory reduction** (MiniCache).

### Limitations

- Survey only covers system-level optimizations — excludes algorithmic changes (e.g., Medusa, speculative decoding) that are equally important.
- Most systems evaluated on NVIDIA GPUs only; AMD, Apple Silicon, and custom hardware (Cerebras, Groq) are understudied.
- Real-world serving dynamics (bursty traffic, heterogeneous models, SLA heterogeneity) are poorly captured by academic benchmarks.

## Related Papers

### 1. Efficient Memory Management for LLM Serving with PagedAttention (Kwon et al., SOSP 2023)

- **Contribution:** Introduced PagedAttention — partitioning KV cache into fixed-size blocks managed via a page table (like OS virtual memory). Eliminates fragmentation, enables copy-on-write sharing across requests.
- **Relation to main paper:** The most impactful concrete system covered by the survey. vLLM is now the de facto standard for open-source LLM serving.
- **Why it matters:** Transformed LLM serving from a memory-bound to a compute-bound problem for many workloads. The dual benefit of reduced fragmentation + flexible sharing is why vLLM achieves 2–4× throughput gains.
- **Deep read later:** Yes — the PagedAttention kernel implementation, memory manager design, and scheduling policy deserve full attention.

### 2. Orca: A Distributed Serving System for Transformer-Based Generative Models (Yu et al., OSDI 2022)

- **Contribution:** Introduced **iteration-level scheduling** (continuous batching) and **selective batching** (only compute attention for unfinished sequences). Showed that request-level batching leaves massive GPU utilization on the table.
- **Relation to main paper:** Orca established the serving paradigm that all subsequent systems build on. vLLM and Sarathi-Serve are extensions of Orca's architecture.
- **Why it matters:** The 36.9× throughput improvement over naïve baselines reset expectations for what LLM serving could achieve. Every modern serving engine uses continuous batching.
- **Deep read later:** Maybe — the core idea is simple, but the distributed implementation details (model parallelism, scheduling policy) could be useful.

## Current Understanding

LLM inference serving is currently undergoing rapid evolution, driven by the unique memory/compute asymmetry of autoregressive decoding.

**The core tension:** Prefill is compute-bound (processes full prompt in parallel), decode is memory-bound (reads KV cache for one token at a time). These phases interfere when colocated on the same GPU, making joint optimization hard.

**Three key levers for optimization:**
1. **Memory efficiency** — reduce KV cache footprint (compression, paging, offloading)
2. **Scheduling** — maximize GPU utilization (continuous batching, disaggregation)
3. **Parallelism** — distribute across devices (tensor/pipeline parallelism, expert parallelism)

The field is converging on disaggregated architectures (separate prefill/decode pools) as the next step beyond continuous batching. The tradeoff is increased network bandwidth requirements between pools.

## Key Concepts

- Continuous batching (iteration-level scheduling)
- PagedAttention and non-contiguous KV cache
- Prefill-decode disaggregation
- KV cache quantization (KIVI: per-channel key, per-token value)
- Selective batching (Orca)
- Chunked prefill (Sarathi-Serve)
- Memory pooling and dynamic block allocation
- Response length prediction for batching

## Open Questions

- Does disaggregated inference make sense for single-GPU deployments, or only clusters?
- How do serving systems handle long-context (128K+) KV cache without DRAM overflow?
- What is the optimal block size for PagedAttention across model scales and hardware?
- Can KV cache compression (4-bit) be combined with PagedAttention's non-contiguous blocks?
- How well do these optimizations transfer to MoE models (Mixtral, DeepSeek-V2)?
- What serving architecture enables cost-effective agent workloads (many turns, tool calls between tokens)?

## Possible Thesis Ideas

- **Adaptive disaggregation** — dynamically decide whether to split prefill/decode per-request based on prompt length, available KV cache, and latency SLA. Most current systems use static pool separation.
- **KV cache-aware agent scheduler** — for agent workloads where LLM calls are interleaved with tool calls, the KV cache must persist across turns. Designing a serving system that exploits idle KV cache during tool execution could improve throughput.
- **Hybrid PagedAttention + compression** — PagedAttention uses full-precision blocks. Combining it with on-the-fly block-level quantization (similar to KIVI) could further reduce memory while retaining non-contiguous allocation benefits.

## Next Step

Continue with a deep read of vLLM (PagedAttention paper) to understand the block management algorithm and kernel implementation. Then explore KV cache compression (KIVI or Gear). The topic likely needs 3–4 more days to gain enough confidence (target 0.80) for a reliable topic map.
