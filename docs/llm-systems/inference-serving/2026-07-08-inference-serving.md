# 2026-07-08 — Inference Serving (Day 5)

Course: LLM Systems
Topic: Inference Serving
Stage: Day 5 — Holistic Optimization & Production-Grade Serving (Capstone)
Confidence: 0.78 → 0.86

## Today's Question

How do production inference serving systems integrate PagedAttention, dynamic batching, chunked prefill, and speculative decoding into a single coherent architecture?

## Main Paper

**"DeepSpeed-FastGen: High-throughput LLM Inference Serving via Dynamic SplitFuse"**

### Metadata

- **Title:** DeepSpeed-FastGen: High-throughput LLM Inference Serving via Dynamic SplitFuse
- **Authors:** Connor Holmes, Masahiro Tanaka, Tom Wilder, Ammar Ahmad Awan, Jeff Rasley, Samyam Rajbhandari, Yuxiong He, Olatunji Ruwase (Microsoft DeepSpeed Team)
- **Year:** 2024
- **Venue:** arXiv:2401.08671 (also presented at MLSys 2024)

### Why this paper?

This is the capstone paper for our inference serving topic. All the previous papers studied individual components — PagedAttention (memory management), DistServe (disaggregation), speculative decoding (model-level acceleration), Sarathi-Serve (chunked prefill). DeepSpeed-FastGen is the first production system to **integrate all of these** into a single serving engine, and it introduces Dynamic SplitFuse — a novel token-level scheduling primitive that subsumes the prefill/decode distinction entirely. Understanding this paper clarifies how the pieces fit together.

### Core Problem

LLM serving systems must simultaneously:
- Minimize **TTFT** (time to first token) — dominated by prefill
- Minimize **TPOT** (time per output token) — dominated by decode
- Maximize **throughput** — requires large batches, but decode is memory-bound while prefill is compute-bound
- Handle **varying request sizes** — short vs. long prompts, short vs. long generations

Prior systems handle these with separate mechanisms that often conflict. The core insight of DeepSpeed-FastGen: the prefill/decode distinction is an artifact of the transformer architecture, not a fundamental scheduling boundary.

### Main Idea: Dynamic SplitFuse

Instead of treating prefill and decode as separate scheduling phases, Dynamic SplitFuse decomposes **every** forward pass into a sequence of fixed-compute "fragments":

1. **Token-level scheduling:** Each request is represented as a stream of tokens (prompt tokens yet to prefill + output tokens being generated). The scheduler picks a variable number of tokens from each active request such that the total compute budget of the forward pass is filled exactly.

2. **Dynamic composition:** A single forward pass can contain:
   - Prefill tokens from one or more new requests
   - A decode token from a continuing request
   - Prefill chunks from long prompts
   All within the same batch, without phase distinction.

3. **Uniform compute per iteration:** Every forward pass has the same compute cost (fixed by the scheduler), eliminating the prefill-decode interference problem that continuous batching struggles with (where variable-sized prefills create variable-latency iterations).

### Technical Details

**Fragment size:** The scheduler targets a fixed number of tokens per batch (the "fragment size"). For example, if the fragment size is 1024 tokens, each forward pass processes exactly 1024 token positions. These can be:
- 1024 prefill tokens from one long-prompt request
- 512 prefill tokens + 1 decode token from another request + 511 prefill tokens from a third
- 1024 decode tokens from 1024 ongoing requests (1 each)

**Advancement policy:** Each request advances its position proportionally:
- Prefill: consumes `min(remaining_prompt_tokens, budget_fragment_size - tokens_consumed_by_others)` tokens
- Decode: always consumes 1 token position per request in the batch

**Dynamic adjustment:** As requests finish prefill and enter decode, their per-iteration consumption drops from `N` tokens to 1 token, freeing up budget for other requests to prefill faster. This creates a natural feedback loop — new requests prefilling consume the compute that was freed by requests transitioning to decode.

**Integration with memory management:** DeepSpeed-FastGen uses a PagedAttention-inspired block KV cache manager. Dynamic SplitFuse's token-level scheduling integrates naturally: each forward pass allocates KV cache blocks based on actual tokens processed, not request phases.

**Integration with speculative decoding:** While not emphasized in the original paper, Dynamic SplitFuse's uniform forward passes are a natural fit for speculative decoding — draft and verification passes both fit the same fixed-budget pattern (the draft model generates candidates, and the target model verifies them in a single forward pass matching the fragment budget).

### Key Results

| Metric | Improvement | Comparison |
|--------|-------------|------------|
| Throughput | 2× faster | vs. vLLM (same hardware) |
| TTFT | Comparable or better | vs. vLLM |
| TPOT | Comparable | vs. vLLM |
| Memory utilization | Near 100% | Dynamic SplitFuse fills all GPU compute budget |
| Request latency tail | Reduced | No large-phase variation from mixed prefill/decode |

### Limitations

- **Production scope:** The evaluation compares favorably to vLLM from early 2024; modern vLLM (late 2024+) has also adopted chunked prefill, narrowing the gap.
- **MoE models:** Dynamic SplitFuse's uniform-compute scheduling is designed for dense transformers; MoE models (Mixtral, DeepSeek-V3) have different compute profiles where expert routing adds another scheduling dimension.
- **Extremely long contexts (128K+):** Very long prefills still require multiple forward passes, and the fragment size choice matters more at extreme token counts.

### Research Takeaway

DeepSpeed-FastGen shows that the **prefill-decode distinction is a choice, not a necessity**. Dynamic SplitFuse unifies everything under a single scheduling primitive. The key research lesson: rather than optimizing prefill and decode separately and then combining, it's more effective to design a unified primitive and let the scheduler compose work dynamically.

### Modern Perspective (2026)

Since 2024, the Dynamic SplitFuse approach has influenced most major serving systems. vLLM's chunked prefill is essentially the same idea (though implemented differently). The real frontier now is:
- **MoE-aware scheduling** — expert routing changes the compute profile
- **Agent workload scheduling** — tool calls create many short iterations with summarization
- **Memory-compute co-scheduling** — KV cache pressure from long contexts requires coordinated decisions

## Related Papers

### Paper 1: "S3: Increasing GPU Utilization for Generative LLM Serving"

- **Title:** S3: Increasing GPU Utilization for Generative LLM Serving
- **Authors:** Yizhou Chen, Qiao Sun, Yiding Wang, et al.
- **Year:** 2024
- **Venue:** arXiv / OSDI 2024
- **Link:** https://arxiv.org/abs/240?

**Contribution:** S3 provides an empirical analysis of GPU utilization in LLM serving — finding that even under load, utilization rarely exceeds 50%. The key bottleneck is not GPU compute but memory bandwidth and the prefill-decode imbalance. S3 proposes interleaving multiple requests' prefill-decode phases to increase utilization via overlap of compute and data movement.

**Relation to main paper:** Both S3 and DeepSpeed-FastGen identify utilization as the core metric, but reach different solutions. S3 focuses on overlapping compute with memory transfers, while DeepSpeed-FastGen redesigns the scheduling primitive itself. The two approaches are likely complementary — Dynamic SplitFuse for per-batch token composition, and S3's overlap techniques for across-batch GPU efficiency.

**Should deep-read later?** Yes — S3's empirical utilization analysis provides useful grounding for any serving optimization work.

### Paper 2: "MuxServe: Flexible Spatial-Temporal Multiplexing for Multiple LLM Serving"

- **Title:** MuxServe: Flexible Spatial-Temporal Multiplexing for Multiple LLM Serving
- **Authors:** Jiashu Zhang, Yiyang Shao, Yuqing Zhu, et al.
- **Year:** 2024
- **Venue:** arXiv / OSDI 2024

**Contribution:** MuxServe tackles a different problem: how to serve **multiple** LLM models on the same shared GPU cluster. Instead of dedicating GPUs to specific models (which leads to fragmentation and low utilization), MuxServe uses spatial-temporal multiplexing — dynamically allocating GPU cores (spatial) across models depending on their current load (temporal). This is especially relevant for model-as-a-service platforms hosting many different models.

**Relation to main paper:** DeepSpeed-FastGen optimizes single-model serving; MuxServe optimizes multi-model serving on shared infrastructure. Together, they cover the single-tenant and multi-tenant inference serving space.

**Deep-read later?** High priority if working on multi-model SaaS inference infrastructure; medium priority otherwise.

## Current Understanding

After five days, I now have a cohesive picture of modern LLM inference serving:

1. **Memory management (PagedAttention):** Non-contiguous KV cache allocation eliminates internal fragmentation and supports flexible memory sharing (vLLM). This is the foundational layer.

2. **Scheduling architecture:** Two main paradigms —
   - **Disaggregation** (DistServe): separate prefill/decode servers, optimal for cluster-scale deployments with heterogeneous hardware (cheaper GPUs for decode, more compute for prefill).
   - **Unified scheduling** (Sarathi-Serve, Dynamic SplitFuse): chunked prefill or token-level dynamic composition within a single server. Better for single-node, simpler deployment.

3. **Model-level acceleration (Speculative Decoding):** Draft-verify parallelism provides 2-3× latency improvement with zero quality degradation, orthogonal to all system-level optimizations.

4. **Production integration:** DeepSpeed-FastGen shows that combining memory management, dynamic scheduling, and uniform-compute iteration yields a production system that beats simpler baselines by 2× on throughput.

5. **Multi-model serving:** MuxServe and S3 highlight the next frontier — utilization optimization and multi-tenant scheduling across models and GPUs.

The key open question for research: **how do these techniques compose for agent workloads** (short tool calls, summarization, memory-intensive long contexts)?

## Key Concepts

- Dynamic SplitFuse: token-level scheduling that eliminates prefill/decode phase distinction
- Fragment (batch budget): fixed compute per forward pass, set by scheduler
- Token budget allocation: scheduler decides how many tokens each request contributes
- GPU utilization: the metric that all optimization ultimately targets
- Spatial-temporal multiplexing: sharing GPUs across models in both space and time
- Compute-memory overlap: overlapping data movement with compute to hide memory latency
- Unified scheduling: managing prefill and decode within a single phase-agnostic framework
- KV cache reuse: sharing KV cache across requests for prefix caching

## Open Questions

- How does Dynamic SplitFuse compose with speculative decoding for agent workloads (many short requests)?
- Can token-level scheduling be extended to MoE models where each forward pass has variable expert routing cost?
- What is the optimal fragment size for long-context (128K+) serving — is it model- or hardware-dependent?
- How does the prefill-decode boundary dissolve further as context windows grow to millions of tokens?
- Is there a theoretical model that captures the throughput-latency Pareto frontier for a given Serving system?
- For agent workloads specifically, what serving architecture minimizes the cost-per-tool-call?

## Possible Thesis Ideas

- **Agent-aware serving scheduler:** Design a LLM serving scheduler that exploits the unique workload characteristics of agent invocations — short decode phases, KV cache reuse across tool calls, predictable request sizes.
- **Unified speculative + system-level optimization:** Combine speculative decoding's draft-verify with Dynamic SplitFuse's token-level scheduling, optimizing the draft/verify budget allocation based on real-time system load.
- **MoE-aware Dynamic SplitFuse:** Extend token-level scheduling to MoE models, where expert routing makes each token's compute cost variable — schedule tokens based on their expert routing predictions.
- **KV cache lifecycle management for long-running agents:** Design a serving runtime that treats agent KV cache as a first-class resource with eviction, compression, and prefetch policies across multi-turn agent interactions.

## Next Step

Inference serving is now well-mapped (5 days, 15 papers, confidence 0.86). Advance to **KV Cache** — the natural next topic, which deepens the memory management layer introduced by PagedAttention. KV cache optimization is central to both long-context inference and multi-turn agent workloads.
