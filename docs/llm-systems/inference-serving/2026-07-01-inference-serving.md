# 2026-07-01 — Inference Serving (Day 4)

Course: LLM Systems
Topic: Inference Serving
Stage: Day 4 — Chunked Prefill & Stall-Free Batching
Confidence: 0.68 → 0.78

## Today's Question

How can serving systems eliminate prefill-decode interference without full disaggregation?

## Main Paper

**"Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"**

- **Authors:** Amey Agrawal, Ashish Panwar, Nitin Kedia, et al.
- **Year:** 2024
- **Venue:** arXiv:2403.02310 / OSDI 2024
- **Link:** https://arxiv.org/abs/2403.02310

### Core Problem

Existing LLM serving systems face a fundamental tension:
- **Prefill is compute-bound** — wants large batches, produces KV cache fast
- **Decode is memory-bound** — wants small batches, reads KV cache slowly
- When mixed in a batch, prefill delays decode (increasing TTFT/TBT) while decode wastes GPU compute during prefill's KV cache fill

### Main Idea: Chunked Prefill + Stall-Free Batching

Instead of treating a prefill request as an atomic unit, **split it into chunks** and schedule them across decode iterations:

1. **Chunked prefill**: divide a prefill's sequence into fixed-size chunks (e.g., 512 tokens). Each chunk is scheduled as an independent batch item alongside decode tokens.
2. **Stall-free batching**: never let a request preempt another request's ongoing decode. Instead, prefill chunks fill the slack compute cycles of decode iterations.

This eliminates the prefill-decode interference without requiring disaggregated architectures (separate prefill/decode servers).

### Technical Details

- **Chunk size**: tuned to match decode iteration time — a chunk should take about the same time as one decode iteration
- **Scheduling policy**: at each iteration, admit as many prefill chunks as will fit within the decode iteration's compute budget (based on the batch's current decode phase)
- **KV cache**: chunked prefill naturally extends PagedAttention — each chunk allocates its own blocks
- **Comparison to disaggregation**: Sarathi-Serve achieves comparable TTFT/P50/TBT improvements to DistServe without splitting the model across separate prefill/decode clusters

### Key Results

| Metric | Improvement vs. vLLM |
|--------|----------------------|
| TTFT (time to first token) | 2-4× reduction at high load |
| Throughput | comparable or better |
| Implementation complexity | Lower than full disaggregation |

### Research Takeaway

Sarathi-Serve shows that **prefill-decode interference can be mitigated via smarter scheduling within a single server**, without needing the operational complexity of disaggregated serving. This is especially valuable for single-GPU deployments where disaggregation is impractical.

### Modern Perspective

Sarathi-Serve's chunked prefill has become a standard feature in modern serving systems (vLLM adopted similar techniques). The positioning relative to disaggregation is clear: chunked prefill is the right solution for single-node deployments; disaggregation pays off at cluster scale.

## Key Concepts

- Chunked prefill: splitting prefill into fixed-size scheduling units
- Stall-free batching: non-preemptive per-iteration scheduling
- Prefill-decode interference: compute-bound vs memory-bound conflict
- Iteration-level scheduling: admit work in each forward pass
- Chunk size tuning: match chunk compute to decode iteration time

## Open Questions

- What is the optimal chunk size — does it depend on model size, hardware, or request patterns?
- Can chunked prefill be combined with disaggregation for multi-GPU settings?
- How does chunked prefill interact with speculative decoding's draft-verify cycle?
- For agent workloads (short bursts), is chunked prefill's benefit diminished?

## Next Step

Day 5 should explore KV cache optimization techniques (e.g., quantization, eviction) or advance to the next topic (KV Cache).
