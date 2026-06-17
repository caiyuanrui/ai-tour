# 2026-06-17 — Inference Serving

Course: LLM Systems
Topic: Inference Serving
Stage: Day 2 — Deeper into scheduling & disaggregation
Confidence: 0.45 -> 0.60

## Today's Question

Day 1 established the basic landscape (continuous batching, PagedAttention, vLLM, Orca). Day 2 asks: **What comes after naive batching? How do modern systems solve the prefill-decode interference problem?**

Two threads emerged at OSDI 2024:
1. **Disaggregation** — physically separate prefill and decode onto different GPUs
2. **Chunked prefill** — split a prefill into small pieces and interleave with decodes on the same GPU

These represent the two dominant architectural directions in 2024-2025 inference serving.

## Main Paper

### Metadata

- Title: DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving
- Authors: Yinmin Zhong, Shengyu Liu, Junda Chen, Jianbo Hu, Yibo Zhu, Xuanzhe Liu, Xin Jin, Hao Zhang
- Year: 2024
- Venue: OSDI 2024
- Link: https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin

### Why this paper?

Day 1's survey mentioned disaggregation as a trend. DistServe is the canonical paper that launched the disaggregation wave. It's the most cited serving systems paper from OSDI 2024 and has directly influenced production deployments (e.g., Meta's LLaMA serving architecture).

### Core Problem

Existing systems colocate prefill and decode on the same GPU. This creates **prefill-decoding interference**:

| | Prefill | Decode |
|---|---------|--------|
| Compute profile | Compute-bound (matrix multiplications on full prompt) | Memory-bound (autoregressive token-by-token) |
| Latency metric | TTFT (time to first token) | TPOT (time per output token) |
| GPU utilization | High arithmetic intensity | Low arithmetic intensity |
| Sensitivity | Sensitive to batch size | Sensitive to memory bandwidth |

When both phases share a GPU, the scheduler must compromise — prioritizing prefill reduces decode latency but causes generation stalls; prioritizing decode sacrifices TTFT. **The fundamental claim: colocation is suboptimal for both.**

### Main Idea

**Disaggregate prefill and decode onto separate GPU groups.** Each phase gets its own:
- Resource allocation (how many GPUs)
- Parallelism strategy (TP degree, PP degree)
- Instance type (prefill GPUs can be higher-compute, decode GPUs higher-memory-bandwidth)

The key insight: prefill is compute-bound and benefits from larger TP degrees; decode is memory-bandwidth-bound and benefits from smaller TP degrees with more independent replicas.

### Technical Details

1. **Co-optimization of resource allocation.** Given TTFT and TPOT SLOs, DistServe finds the optimal GPU split between prefill and decode instances, and the optimal parallelism config for each. This is a constrained optimization problem over discrete choices.

2. **Pipeline-parallel-aware disaggregation.** When models use pipeline parallelism, microbatches from prefill propagate to decode instances. DistServe carefully manages microbatch boundaries to avoid pipeline bubbles at the disaggregation boundary.

3. **KV cache transfer.** Once prefill completes, the KV cache must be transferred from prefill GPU to decode GPU over the cluster network. DistServe co-optimizes placement based on bandwidth between GPU groups to minimize this transfer cost.

4. **Goodput metric.** Instead of raw throughput, DistServe optimizes for **goodput** — the maximum request rate that can be served while staying within *both* TTFT and TPOT SLOs simultaneously. This is a more realistic metric than throughput alone.

### Results

- Up to **7.4× more requests** served within SLO vs state-of-the-art (vLLM, Orca)
- Up to **12.6× tighter SLO** for the same request rate
- >90% of requests stay within latency constraints
- Evaluated on LLaMA, GPT variants, multiple hardware configs

### Research takeaway

DistServe proved that **disaggregation is not just possible but optimal** for production-grade serving. The architecture has been adopted by vLLM (v0.6+), TensorRT-LLM, and major cloud providers. However, it introduces a new challenge: **KV cache transfer bandwidth** between prefill and decode instances becomes the bottleneck in disaggregated deployments.

### Modern perspective (June 2026)

The disaggregation approach has matured significantly since DistServe. Key developments:
- **AMPD (2025)** extends disaggregation to multi-round inference, handling KV cache reuse across turns
- **WindServe (2025)** introduces stream-based fine-grained scheduling within the disaggregated paradigm
- Industry adoption: Meta, Google, and major cloud providers use disaggregated architectures in production
- Ongoing challenge: **KV cache transfer overhead** at scale remains an active research area

## Related Papers

### Paper 1: Sarathi-Serve

- **Title:** Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- **Authors:** Amey Agrawal, Nitin Kedia, Ashish Panwar, Jayashree Mohan, Nipun Kwatra, Bhargav S. Gulavani, Alexey Tumanov, Ramachandran Ramjee
- **Year:** 2024
- **Venue:** OSDI 2024
- **Link:** https://arxiv.org/abs/2403.02310

**Contribution:** Introduces **chunked-prefills** — splitting a prefill request into small compute-sized chunks — combined with **stall-free batching** that never pauses ongoing decode iterations.

**Relation to main paper:** Sarathi-Serve addresses the same prefill-decode interference problem but takes the **opposite approach**: instead of separating phases onto different GPUs, it interleaves small prefill chunks with decodes on the same GPU. This avoids the KV cache transfer overhead of disaggregation but requires careful token budget management.

**Why it matters:** Sarathi-Serve achieves 2.6× (Mistral-7B) to 5.6× (Falcon-180B with PP) serving capacity gains without needing extra GPUs or network bandwidth for KV transfer. It's complementary to DistServe — disaggregation + chunked prefill could be combined for further gains.

**Depth-needed:** Should be deep-read later when exploring scheduling/batching topics.

### Paper 2: Splitwise

- **Title:** Splitwise: Efficient Generative LLM Inference Using Phase Splitting
- **Authors:** Pratyush Patel, Esha Choukse, Chaojie Zhang, Inigo Goiri, Brijesh Warrier, Nithish Mahalingam, Ricardo Bianchini
- **Year:** 2024
- **Venue:** ISCA 2024
- **Link:** https://arxiv.org/abs/2311.18677

**Contribution:** Splits prefill and decode onto **different types of hardware** — e.g., H100 GPUs for prefill (compute-optimized) and A100 GPUs for decode (cost-efficient). Demonstrates that using heterogeneous hardware can reduce serving costs by 30-50% while meeting SLOs.

**Relation to main paper:** Splitwise predates DistServe (arXiv Nov 2023 vs Jan 2024) and explores a more **cost-efficiency-focused** version of the same idea. While DistServe optimizes for goodput on homogeneous clusters, Splitwise asks: "What if we use different GPU types for each phase?"

**Why it matters:** Splitwise introduces the economic dimension — disaggregation isn't just about latency, it's about **total cost of ownership**. This is critical for real deployments where GPU cost is the dominant expense.

**Depth-needed:** Useful as context. No need to deep-read unless exploring production deployment economics.

## Current Understanding

After Day 2, the inference serving map has expanded significantly:

**Baseline approaches (Day 1):**
- Continuous batching (Orca)
- PagedAttention for memory-efficient KV cache (vLLM)
- Selective batching and chunked prefill basics

**Architecture evolution (Day 2):**
- **DistServe** → disaggregation solves prefill-decode interference by separating phases onto different GPU groups. Core tradeoff: KV cache transfer overhead vs elimination of interference.
- **Sarathi-Serve** → chunked prefill solves the same problem within a single GPU. Core tradeoff: token budget management complexity vs no transfer overhead.
- **Splitwise** → heterogeneous disaggregation adds cost optimization. Different hardware for each phase.

**Key insight:** The field is converging on two parallel paths:
1. **Disaggregated architecture** (DistServe, Splitwise, AMPD, WindServe) — for large-scale deployments with many GPUs and fast interconnect
2. **Chunked prefill + stall-free scheduling** (Sarathi-Serve) — for single-GPU and small-cluster deployments where disaggregation overhead dominates

Both paths are now incorporated into production systems (vLLM supports both chunked prefill and disaggregated mode).

## Key Concepts

- **Prefill-decode interference**: The fundamental conflict when compute-bound (prefill) and memory-bound (decode) phases share a GPU
- **Goodput**: Request rate served while meeting *all* SLO constraints simultaneously (TTFT + TPOT)
- **Disaggregation**: Physically separating prefill and decode onto different GPU groups
- **Chunked prefill**: Splitting a prefill request into small chunks to enable fine-grained interleaving
- **Stall-free batching**: A scheduling policy that never pauses ongoing decode iterations
- **Token budget**: Maximum prefill tokens allowed per scheduling iteration to bound latency
- **KV cache transfer**: Moving KV cache from prefill GPU to decode GPU over network (the main cost of disaggregation)
- **Phase-aware hardware selection**: Using different GPU types (H100 for prefill, A100 for decode) for cost efficiency

## Open Questions

1. **KV cache transfer bottleneck**: As context lengths increase (128K+), KV cache size grows proportionally. Is there a fundamental bandwidth limit to disaggregation?
2. **Disaggregation + chunked prefill**: Can these two approaches be combined? Use chunked prefill within a disaggregated architecture?
3. **MoE model serving**: How do these optimizations transfer to Mixture-of-Experts models (DeepSeek-V3, Mixtral) where expert parallelism adds another dimension?
4. **Agent workloads**: Tool-interleaved LLM calls have very different prefill/decode ratios. What serving architecture is optimal for agentic patterns?
5. **Cache-aware scheduling**: Can the scheduler reuse KV cache across turns (e.g., multi-turn conversations, agent memory) to reduce prefill cost?

## Possible Thesis Ideas

1. **Unified scheduler for disaggregated + chunked inference** — design a scheduler that dynamically switches between disaggregated mode (for large prefills) and chunked-prefill mode (for small ones) based on request characteristics and cluster topology.

2. **KV cache compression for disaggregated transfer** — apply block-level quantization (KIVI-like) before transferring KV cache over the network, reducing transfer bandwidth by 2-4× while maintaining quality.

3. **Agent-aware inference scheduler** — build a serving system that profiles agent execution patterns and uses those profiles to pre-allocate KV cache space, pre-warm GPUs, and predict prefill/decode ratios.

## Next Step

On Day 3, explore **KV cache** deeper (the topic immediately adjacent to inference serving). Specifically, KV cache quantization, eviction, and compression — which are critical for both disaggregated architectures and long-context serving. This bridges into the next course topic (kv-cache).

Alternatively, if staying on inference serving for one more day: dive into **speculative decoding** (draft model + verification) as another major throughput optimization.

Decision: Advance to kv-cache topic next if confidence ≥ 0.80 by end of Day 3. Currently 0.60 — one more day on inference serving with speculative decoding, then evaluate.
