# 2026-09-02 — Batching and Scheduling

Course: LLM Systems
Topic: Batching and Scheduling
Stage: Day 3 — KVCache-Centric Cluster Scheduling (Mooncake / CacheBlend / Preble)
Confidence: 0.58 -> 0.66

## Today's Question

Day 2 mapped the prediction axis (SSJF / ProD / ESTP), leaving the scheduling map at five axes: batching granularity, cache-aware scheduling (SGLang), preemptive policy (FastServe), cross-instance migration (Llumnix), and length-aware scheduling (SSJF). The most concrete carried question is the agent-workload one — “is prefix reuse the dominant win, or does tail-latency control matter more?” — plus the KV-reuse-across-turns question carried from inference-serving. Today drills into the **KV/prefix-centric scheduling axis at cluster scale**: what happens when the KV cache becomes a first-class, globally-scheduled resource — a disaggregated cache pool spanning GPU/CPU/SSD, prefix-aware request routing, and a scheduler whose objective is reuse-amplified throughput under SLOs? Three papers triangulate: Mooncake (the production KVCache-centric scheduler behind Kimi), CacheBlend (extending reuse to non-prefix chunks via KV fusion), and Preble (distributed prompt scheduling co-optimizing reuse and load-balancing).

## Main Paper

### Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving

- Authors: Ruoyu Qin, Zheming Li, Weiran He, Mingxing Zhang, Yongwei Wu, Weimin Zheng, Xinran Xu
- Year: 2024
- Venue: arXiv:2407.00079 (v4)
- Link: https://arxiv.org/abs/2407.00079

### Why this paper?

Day 1 left open how cache-awareness scales past a single engine (SGLang's radix tree is per-instance) and how multi-turn KV reuse could cut prefill cost (open question carried from inference-serving). Mooncake is the production answer from Moonshot AI (Kimi): it makes the KV cache a first-class cluster-wide resource with its own scheduler. It is canonical (real deployment, 75% more requests under real workloads), directly attacks the topic's highest-priority open question (long-context / multi-turn agent-like workloads), and completes the map's trajectory from PagedAttention (KV as a paged resource) to KV as the organizing principle of the serving architecture.

### Core Problem

Long-context and multi-turn workloads expose two structural inefficiencies in conventional serving. (1) Prefill and decode have conflicting resource profiles — prefill is compute-bound, decode is memory-bandwidth-bound — and when co-located on the same GPU they interfere, wasting throughput (the DistServe/Splitwise observation). (2) Repeated requests recompute the same KV cache: shared system prompts, multi-turn conversation history, RAG chunks. Prefix caching exists (SGLang) but is confined to a single engine, so reuse does not survive across a cluster. Mooncake also faces a reality academic schedulers assume away: production load can exceed cluster capacity, so the scheduler must sometimes reject requests to keep SLOs.

### Main Idea

A **KVCache-centric disaggregated architecture**: separate the prefill and decode clusters (phase disaggregation), and treat the KV cache itself as a disaggregated pool built from the underutilized CPU, DRAM, and SSD of the GPU cluster. The core is a **KVCache-centric scheduler** that (a) routes each request's prefill to wherever its prefix KV already lives (reuse-aware routing), (b) schedules cache blocks across the GPU/CPU/SSD tiers as a first-class resource, and (c) balances maximizing *effective* throughput (reuse-amplified) against meeting latency SLOs. Under overload it adds a **prediction-based early-rejection policy** to protect SLO attainment.

### Technical Details

Abstract-verified components: prefill/decode cluster separation; a disaggregated KVCache pool layered over spare CPU/DRAM/SSD of the GPU cluster; a KVCache-centric scheduler whose objective is maximizing effective throughput while satisfying latency SLOs; a prediction-based early-rejection policy for overloaded scenarios. Results: up to 525% throughput increase over baseline in simulated long-context scenarios while still adhering to SLOs; under real workloads the architecture lets Kimi handle 75% more requests. (Block-level cache placement/eviction policy, the exact reuse metric, and the rejection predictor's mechanism are beyond the abstract — marked for full-paper verification when web access is available.)

### Research takeaway

Mooncake completes the trajectory this map has been building across two topics: PagedAttention made KV a paged, swappable resource (inference-serving Day 1); Dynamic SplitFuse made scheduling token-level (inference-serving Day 5); Mooncake makes the KV cache the organizing principle of the whole serving architecture. The scheduler's job is no longer just “which batch/token next” but “where does the KV live, who can reuse it, and can we afford to run this request at all”. It is the production proof that the prefix-reuse wins SGLang showed at engine level survive and amplify at cluster scale — and that KV placement is a scheduling decision, not a memory-management footnote. The 525% (simulated) / 75% (real) numbers are the strongest evidence yet for the agent-workload hypothesis: reuse-heavy, long-context traffic is where cache-centric scheduling pays most.

### Modern perspective

Mooncake optimizes for Kimi's workload profile (long-context, high prefix reuse), so its wins do not necessarily transfer to short, diverse workloads. The early-rejection policy raises fairness and availability questions — which requests get shed under overload is a policy decision, and the abstract does not characterize it. Prefix reuse is still *exact-prefix* matching: RAG-style non-prefix chunks do not hit. The disaggregated cache pool assumes spare CPU/DRAM/SSD in the cluster — a different calculus for GPU-only deployments. 2025-2026 successors push the same idea further: CacheBlend fuses KV of non-identical prefixes; Preble distributes prompt scheduling with load-balance co-optimization; KVCache-centric pooling has become a common architecture template across serving stacks.

## Related Papers

### 1. CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion

- Authors: Jiayi Yao, Hanchen Li, Yuhan Liu, Siddhant Ray, Yihua Cheng, Qizheng Zhang, Kuntai Du, Shan Lu, Junchen Jiang
- Year: 2024
- Venue: arXiv:2405.16444 (v3)
- Link: https://arxiv.org/abs/2405.16444
- Deep read later: True

Contribution:

Reuses precomputed KV caches even when the reused text is NOT an input prefix — the case that defeats naive prefix caching. The trick: selectively recompute the KV values of a small subset of tokens to partially update each reused KV cache, fixing the cross-attention with preceding text that makes non-prefix KV stale. Recompute is pipelined with KV retrieval from slower storage, so caches can live on cheaper, larger devices without adding inference delay. Results: 2.2-3.3x lower TTFT and 2.8-5x higher throughput vs full KV recompute, with no generation-quality loss, across 3 open-source LLMs and 4 benchmarks.

Relation to main paper:

Generalizes the reuse primitive that Mooncake and SGLang rely on. Mooncake's cache pool serves *exact* prefix hits; CacheBlend extends reuse to mid-context chunks (exactly the RAG pattern that breaks prefix caches). Same KVCache-centric philosophy — but instead of routing around the cache, it fuses and partially recomputes. Together they define the reuse spectrum: exact-prefix (SGLang/Mooncake) → fused-non-prefix (CacheBlend).

### 2. Preble: Efficient Distributed Prompt Scheduling for LLM Serving

- Authors: Vikranth Srivatsa, Zijian He, Reyna Abhyankar, Dongming Li, Yiying Zhang
- Year: 2024
- Venue: arXiv:2407.00023 (v2)
- Link: https://arxiv.org/abs/2407.00023
- Deep read later: True

Contribution:

First distributed LLM serving platform targeting prompt sharing. Modern prompts carry domain instructions, tool-use illustrations, and long context — much of it repetitive across requests — but prior KV-reuse work was single-GPU. Preble designs a distributed scheduling system that co-optimizes KV state reuse and computation load-balancing with a new scheduling algorithm plus a hierarchical scheduling mechanism. On real workloads and request arrival patterns with two open-source LLMs: 1.5-14.5x average latency and 2-10x p99 latency improvement over SOTA serving systems.

Relation to main paper:

Answers the 'distributed' half of cache-aware scheduling. SGLang's radix tree is single-engine; Mooncake disaggregates by phase but keeps one scheduler; Preble makes reuse-vs-load-balance an explicit co-optimization at the scheduling layer — a different decomposition of the same problem (which engine should run this prompt to maximize global reuse without hot-spotting any one engine).

## Current Understanding

After Day 3 the batching-scheduling map gains its sixth axis — **cluster-scale KVCache-centric scheduling**: 1) batching granularity (foundation): request → iteration (continuous batching) → token (Dynamic SplitFuse); 2) cache-aware scheduling (SGLang): single-engine radix-tree prefix reuse; 3) preemptive policy (FastServe): token-granularity preemption with KV offloading; 4) cross-instance migration (Llumnix); 5) length-aware scheduling (SSJF/ProD/ESTP); 6) KVCache-centric cluster scheduling (Mooncake + CacheBlend + Preble): the KV cache becomes a global tiered resource (GPU/CPU/SSD), scheduling = reuse-aware routing + cache placement + SLO-constrained admission, and reuse extends from exact prefixes (Mooncake/SGLang) to fused non-prefix chunks (CacheBlend) with distributed reuse+load co-optimization (Preble). The key reframe: Day 1's cache-aware scheduling is the single-engine special case of what Mooncake does cluster-wide. The scheduler's objective becomes maximizing *effective* (reuse-amplified) throughput under SLOs, with admission control when overloaded — which finally gives the agent-workload question a concrete answer: multi-turn and long-context traffic is exactly where prefix reuse is largest (system prompt + tool schema + conversation history as long-lived shared prefixes), and Mooncake's real-workload 75% request gain is the evidence. Confidence 0.58 -> 0.66: the cluster-scale reuse axis is now understood end-to-end (production architecture, reuse-generalization, distributed co-optimization). Still missing: fairness/SLO-aware admission policies, memory-fragmentation-aware scheduling, multi-tenant scheduling, and MLA-cache-aware scheduling.

## Key Concepts

- KVCache-centric disaggregated architecture: separate prefill/decode clusters + disaggregated cache pool on the cluster's spare CPU/DRAM/SSD
- KVCache-centric scheduler: reuse-aware request routing + cache-block placement + SLO-constrained admission as one decision
- Effective throughput: reuse-amplified throughput as the scheduling objective (vs raw throughput)
- Prediction-based early rejection: admission control under overload to protect SLO attainment
- KV fusion (CacheBlend): reusing non-prefix KV chunks by selectively recomputing a small subset of tokens
- Recompute-retrieval pipelining: hiding KV retrieval from slower storage tiers behind partial recompute
- Non-prefix KV reuse: extending prefix-cache hits to mid-context chunks (RAG pattern)
- Distributed prompt scheduling (Preble): co-optimizing KV reuse and computation load-balancing
- Hierarchical scheduling: multi-level scheduling structure for distributed prompt sharing

## Open Questions

- Can Mooncake-style exact-prefix reuse extend to CacheBlend-style non-prefix fusion at cluster scale — can a fused (partially recomputed) KV block be a first-class cache-pool object with its own placement/eviction policy? *(from today)*
- Where should KV fusion live — in the scheduler (routing decides fuse-vs-fetch-vs-recompute) or in the cache layer (transparent to scheduling)? *(from today)*
- Mooncake's early rejection: what is the right admission policy — fairness across tenants vs SLO protection — and which requests get shed first under overload? *(from today)*
- Does the disaggregated cache pool's CPU/DRAM/SSD assumption hold for GPU-only clusters — what is the minimal tier configuration that still yields reuse benefits? *(from today)*
- Agent workloads: how do Mooncake-style reuse + CacheBlend fusion + SSJF length prediction compose into one agent-serving scheduler with a cost-per-tool-call objective? *(from today, sharpens carried agent question)*
- Preble's reuse-vs-load co-optimization vs preemption/migration (FastServe/Llumnix): does load-balancing destroy the reuse it tries to maximize? *(from today, sharpens carried question)*
- Can the KVCache-centric objective (effective throughput under SLO) consume SSJF-style length predictions — giving the admission controller a better cost estimate per request? *(from today)*
- How does scheduler design change with MLA-style caches (14x smaller KV)? Does a smaller cache change the cache-pool tiering calculus (less SSD offload needed)? *(carried)*
- Fairness: continuous batching lets long requests starve short ones — what is the right fairness/throughput trade-off, and does early rejection add a second fairness axis? *(carried + sharpened)*
- What is the optimal cache-aware scheduling policy — can radix-tree reuse be co-optimized with prefill/decode batching and SLOs, or is it inherently heuristic? *(carried)*

## Possible Thesis Ideas

- Agent-serving scheduler with reuse-aware admission: Mooncake-style KVCache-centric routing + SSJF-style length prediction to decide per-request admission/routing for tool-interleaved agent workloads, optimizing cost-per-tool-call under SLOs. *(from today)*
- Unified prefix-reuse primitive: combine exact-prefix radix trees (SGLang), non-prefix KV fusion (CacheBlend), and cluster-scale cache pooling (Mooncake) into one cache abstraction with learned placement/eviction across tiers. *(from today)*
- Fusion-aware scheduling: make KV-fusion cost an explicit input to request routing — a three-way decision (fuse vs fetch vs recompute) at scheduler level. *(from today)*
- Reuse-aware admission control: SLO-constrained early rejection with fairness guarantees when reuse is heterogeneous across tenants. *(from today)*
- Hierarchical reuse+load scheduler: Preble-style co-optimization extended with migration (Llumnix) and preemption (FastServe) — the full distributed scheduling space in one policy. *(from today)*
- Cache-aware + preemptive unified scheduler: jointly maximize radix-tree reuse and support token-granularity preemption with KV offloading. *(carried)*
- SLO-constrained cache-aware batching: batch formation as an optimization over prefix-reuse x deadline-feasibility. *(carried)*
- Robust length-prediction + cache-aware unified scheduler: consume distributional length targets (ProD-style) inside a radix-tree batch former. *(carried)*

## Next Step

Day 4 should pick the next concrete axis from the carried open questions. Strongest candidates: (a) **fairness / SLO-aware scheduling** — the admission-control question is now sharpened by Mooncake's early rejection (Satori, 'Towards Efficient and Fair LLM Serving', is the canonical target named in Day 2's next step); (b) **memory-fragmentation-aware scheduling** (TetriInfer / OptLLM — scheduling to reduce KV fragmentation); or (c) **multi-tenant scheduling** (S-LoRA / Punica). Confidence 0.66 < 0.80, days_spent 3 < 5 — no advancement today.

---

*Note: general web search unavailable this run; paper discovery via arXiv API with retry/backoff (fetch_arxiv_retry.py). All three abstracts verified from arXiv API responses. Mooncake = arXiv:2407.00079 (remembered ID correct); CacheBlend = 2405.16444 (remembered ID 2502.07563 was wrong — that is LASP-2); Preble = 2407.00023 (remembered ID 2411.04614 was wrong — that is a math paper). CacheBlend's and Preble's arXiv IDs were recovered via exact-title/AND queries after initial 429 rate-limiting. Mooncake's block-level cache placement/eviction and rejection-predictor mechanics are beyond the abstract and marked for verification.*
