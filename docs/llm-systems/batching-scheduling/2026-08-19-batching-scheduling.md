# 2026-08-19 — Batching and Scheduling

Course: LLM Systems
Topic: Batching and Scheduling
Stage: Day 1 — Cache-Aware Request Scheduling (SGLang / RadixAttention)
Confidence: 0.00 -> 0.45

## Today's Question

The inference-serving topic mapped the *lower* layers of the serving stack: memory management (PagedAttention), phase separation (DistServe, Splitwise), token-level scheduling (Dynamic SplitFuse), and speculative acceleration. The new topic asks the *scheduler's* question directly: given a stream of heterogeneous requests — different input lengths, output lengths, priorities, and shared prefixes — **who gets to run, when, and on what**? Day 1 needs the design space: what does a scheduler decide, and what information does it use to decide? The three papers chosen triangulate three orthogonal scheduling axes: cache-aware request scheduling inside one engine (SGLang), preemptive scheduling policy under unknown output lengths (FastServe), and dynamic scheduling *across* instances (Llumnix).

## Main Paper

### Metadata

- **Title:** SGLang: Efficient Execution of Structured Language Model Programs
- **Authors:** Lianmin Zheng, Liangsheng Yin, Zhiqiang Xie, Chuyue Sun, Jeff Huang, Cody Hao Yu, Shiyi Cao, Christos Kozyrakis, et al. (Stanford + UC Berkeley + NVIDIA)
- **Year:** 2023 (v2 2024)
- **Venue:** arXiv:2312.07104 — **NeurIPS 2024 Best Paper**
- **Link:** https://arxiv.org/abs/2312.07104

### Why this paper?

SGLang is the natural bridge from the completed KV-cache topic into batching-scheduling: its headline optimization, **RadixAttention**, is a *cache-aware scheduler* — it reuses KV cache across requests by treating the cache as a radix tree and scheduling around it. It is simultaneously canonical (NeurIPS 2024 best paper), representative (the runtime behind much of the 2025-2026 open-source agent/LLM serving stack), and recent. Reading it first gives Day 1 the key insight that *scheduling and caching are the same problem*: the scheduler's job is to maximize KV-cache reuse while keeping batches full.

### Core Problem

Multi-step LLM applications (agents, RAG pipelines, few-shot, multi-turn chat) send many requests that **share prefixes**: the system prompt, the tool definitions, the document prefix, the dialogue history. Standard serving engines treat each request as an independent generation and re-compute the shared prefix's KV cache every time — often the majority of prefill compute. Separately, the scheduler must decide *when* to run each request (batching) to maximize throughput without destroying latency. SGLang's thesis: both problems are one — if the system executes *programs* of LLM calls (not isolated generations) and schedules with cache-awareness, throughput improves dramatically.

### Main Idea

A full-stack system with two parts:

1. **Frontend language** — primitives for composing LLM calls (generation, parallelism control, structured output) so the runtime can *see* the program structure and optimize across calls.
2. **Runtime with RadixAttention** — a **radix tree** (prefix tree) over all cached KV tensors. Each request's prompt is matched against the tree; the longest matching prefix's KV is *reused* (zero recompute), and the new suffix is appended as a child node. **Cache-aware scheduling**: when evicting, the LRU policy is aware of the tree structure; when batching, requests sharing prefixes are co-scheduled so their computation overlaps. Also includes **compressed finite state machines (CFSM)** for fast structured-output decoding (JSON regex → FSM), and co-location of prefill and decode in the same batch (the same "stall-free" idea as Sarathi, but generalized).

### Technical Details

- **Radix tree KV cache:** nodes = cached KV blocks; a request's prefix is a path; reference counting lets the scheduler know which cache lines are shared by multiple future requests (high reuse value) vs. private.
- **Cache-aware eviction:** LRU with *tree structure* — evict leaf nodes first, avoid evicting nodes shared by many requests (the scheduler can keep a shared system-prompt subtree alive while individual dialogue branches come and go).
- **RadixAttention reuse at scale:** in agent workloads where every turn re-sends the same system prompt + tool schema, prefill cost for the shared prefix drops to ~0.
- **CFSM for JSON/grammar decoding:** converts the output grammar into a finite state machine ahead of time, so decoding only ever proposes valid next tokens — no rejection sampling, and structured outputs decode faster than free-form.
- **Throughput results:** up to **6.4×** higher throughput vs. state-of-the-art systems across agent control, logical reasoning, few-shot benchmarks, JSON decoding, RAG pipelines, and multi-turn chat (measured on LLMs and VLMs).

### Limitations

- **Reuse is bounded by the workload:** RadixAttention shines when requests share prefixes (agents, RAG, chat); for independent, cold-prefix requests the tree adds overhead without reuse benefit.
- **Cache state pressure:** keeping the radix tree alive costs GPU memory — the scheduler must trade reuse potential against memory budget; eviction policy quality matters as much as the tree itself.
- **Single-engine scope:** SGLang schedules within one instance/engine; it does not answer cross-instance placement, migration, or cluster-level load balancing (that's Llumnix's axis, below).
- **Scheduling remains heuristic:** cache-aware batching and eviction are engineered policies; there is no principled account of *optimal* cache-aware scheduling under SLOs.

### Research takeaway

The scheduler's real resource is not GPU FLOPs — it is **reusable KV state**. SGLang reframes batching-scheduling as: build batches that maximize cache reuse, evict to preserve high-value shared prefixes, and let the program structure (frontend) inform runtime decisions. This connects directly to the KV-cache topic: MLA shrank the cache per token, RadixAttention stops re-computing it across requests — two complementary attacks on the same memory-bandwidth bottleneck.

### Modern perspective

SGLang won NeurIPS 2024 best paper and its runtime became one of the two dominant open-source serving engines (with vLLM) for 2025-2026 frontier workloads; its "structured programs + cache-aware execution" model is now the standard frame for agent serving. Later work extends the axis: prefix-aware batching (AlignedServe 2026), cache-aware routing across replicas, and joint scheduling of prefill/decode with cache reuse (the Dynamic SplitFuse line from inference-serving Day 5 composes naturally with RadixAttention).

## Related Papers

### Paper 1 — FastServe: Fast Distributed Inference Serving for Large Language Models

- **Authors:** Bingyang Wu, Yinmin Zhong, Zili Zhang, et al. (Peking University)
- **Year:** 2023 · arXiv:2305.05920 · https://arxiv.org/abs/2305.05920

**Contribution (quick note):** FastServe attacks the *scheduling policy* axis: LLM requests have unknown, highly variable output lengths, so FCFS/run-to-completion suffers head-of-line blocking (a short request stuck behind a long one). FastServe exploits the autoregressive pattern to preempt at **per-output-token granularity** and runs a **skip-join Multi-Level Feedback Queue (MLFQ)** scheduler: each queue level has a time slice; requests get demoted on overrun, and — exploiting the "semi-information-agnostic" setting — the scheduler uses the *input length* to place each arrival in a good initial queue and skip higher-priority queues, reducing wasteful demotions. GPU memory is managed by proactive offloading/uploading of intermediate state (KV) to host memory during preemption.

**Relation to main paper:** SGLang is cache-aware but *non-preemptive* within the engine (it finishes or evicts); FastServe adds the preemption dimension — a scheduler can *pause* a running request and run someone else, at token granularity, with the KV state swapped out. The two are complementary primitives: cache-aware batching (SGLang) + preemptive policy (FastServe) are both needed for latency-SLO scheduling under heterogeneous workloads. FastServe reports up to 31.4×/17.9× throughput gains vs. vLLM under the same average/tail-latency constraints. Worth a deep read later — preemption + KV offloading is exactly the mechanism that agent-interleaved workloads stress.

### Paper 2 — Llumnix: Dynamic Scheduling for Large Language Model Serving

- **Authors:** Biao Sun, Ziming Huang, Hanyu Zhao, Wencong Xiao, Xinyi Zhang, Yong Li, Wei Lin (Alibaba PAI)
- **Year:** 2024 · arXiv:2406.03243 · https://arxiv.org/abs/2406.03243

**Contribution (quick note):** Llumnix moves scheduling to the **instance level**: requests are heterogeneous and unpredictable in resource/latency needs, and static placement causes queuing delays, poor tail latency, and SLO violations. Like OS context-switching across CPU cores, Llumnix **reschedules running requests across model instances** using an efficient, scalable **live migration** mechanism for requests and their in-memory KV state (migration cost amortized by migrating only when the gain is large). A dynamic policy unifies load balancing, resource-fragmentation mitigation, and priority/SLO differentiation. Results: an order of magnitude better tail latency, up to 1.5× faster high-priority requests, and up to 36% cost savings at similar tail latency vs. SOTA systems.

**Relation to main paper:** SGLang optimizes scheduling *inside* an engine; Llumnix optimizes scheduling *across* engines. The two compose: a cluster-level dynamic scheduler (Llumnix) routing/migrating requests between cache-aware engines (SGLang) is the emerging production architecture. Llumnix also surfaces the cost question SGLang ignores — migration overhead and placement decisions under cost constraints — and shows that scheduling is not just per-request ordering but *placement over time*. Worth a deep read later for the agent-runtime topic (long-running tool-using agents need exactly this kind of stateful migration).

## Current Understanding

The batching-scheduling map after Day 1 has three orthogonal scheduling axes, plus the foundation from the inference-serving topic:

1. **Batching granularity (foundation, from inference-serving):** request-level → iteration-level (continuous batching, Orca) → token-level (Dynamic SplitFuse). The batch is the scheduler's unit of compute; modern schedulers form batches at every iteration.
2. **Cache-aware scheduling (SGLang / RadixAttention):** the scheduler treats reusable KV state (radix tree) as a first-class resource — batches are formed to maximize prefix reuse; eviction protects high-reuse shared prefixes. **Scheduling = cache management.**
3. **Preemptive policy (FastServe / skip-join MLFQ):** when output lengths are unknown, schedulers can preempt at token granularity with KV offloading; input-length-aware placement reduces demotions. **Scheduling = latency control under uncertainty.**
4. **Instance-level dynamic scheduling (Llumnix):** placement and live migration across engines, unifying load balancing, fragmentation, and priorities. **Scheduling = placement over time, not just ordering.**

Key cross-cutting insight: LLM scheduling is uniquely hard because *the cost of a request is unknown until it finishes* (autoregressive), *the state is heavy* (KV cache — scheduling decisions have memory consequences), and *workloads share structure* (prefixes — scheduling decisions have reuse consequences). No single paper covers all four axes; the field is converging on cluster schedulers over cache-aware engines with preemptive, priority-aware policies.

## Key Concepts

- RadixAttention: radix-tree KV cache reuse + cache-aware scheduling
- Cache-aware eviction: LRU on tree structure, protecting shared (system-prompt) prefixes
- Compressed finite state machine (CFSM): grammar-constrained decoding as a scheduling-friendly primitive
- Continuous batching (Orca, foundation): iteration-level batch formation
- Token-level scheduling (Dynamic SplitFuse, foundation): phase-agnostic batch budget
- Preemptive scheduling at token granularity: skip-join MLFQ (FastServe)
- Semi-information-agnostic scheduling: using input length to set initial MLFQ queue
- KV offload/upload for preemption: swapping intermediate state between GPU and host
- Instance-level dynamic scheduling: live request migration across engines (Llumnix)
- Scheduling objectives: throughput vs. tail latency vs. SLO attainment vs. cost
- Head-of-line blocking: the failure mode FCFS schedulers hit with variable output lengths

## Open Questions

- What is the *optimal* cache-aware scheduling policy — can radix-tree reuse be co-optimized with prefill/decode batching and SLOs, or is it inherently heuristic?
- How do preemption (FastServe), cache-awareness (SGLang), and instance migration (Llumnix) interact? Preempting a request evicts/offloads its KV — does that destroy the reuse that cache-aware scheduling is trying to preserve?
- For agent workloads (short, tool-interleaved, shared system prompts): is prefix reuse the dominant win (SGLang), or does tail-latency control (FastServe-style preemption) matter more? What is the right scheduler mix?
- How does scheduler design change with MLA-style caches (14× smaller KV)? Migration and preemption get cheaper — does that shift the optimal policy?
- Fairness: continuous batching lets long requests starve short ones (the max-driven batch-cost effect) — what is the right fairness/throughput trade-off (cf. resource-fair scheduling, ISJL, 2026)?
- Prediction-based scheduling: output-length predictors (ELIS/SSJF) claim big wins — how robust are they across workloads, and do they compose with cache-aware batching?

## Possible Thesis Ideas

- **Cache-aware + preemptive unified scheduler:** a scheduler that jointly maximizes radix-tree reuse and supports token-granularity preemption with KV offloading — the two axes are currently in separate systems.
- **Agent-aware scheduling policy:** exploit agent workload structure (system prompt + tool schema as long-lived shared prefixes, short interleaved turns) to define a scheduler that optimizes cost-per-tool-call and SLO attainment — connects directly to the user's agents priority.
- **SLO-constrained cache-aware batching:** formulate batch formation as an optimization over prefix-reuse × deadline-feasibility (extends DistServe's goodput framing with the reuse dimension).
- **Scheduling under MLA caches:** since migration/preemption cost scales with KV size, quantify how 14× smaller caches change the preemption-vs-reuse trade-off — a systems study with clean experiments.

## Next Step

Day 2 should drill into one axis with a second paper: candidates are (a) prediction-based scheduling (SSJF / ELIS — output-length prediction), (b) fairness-aware batching (resource-fair scheduling / ISJL), or (c) the Orca → continuous-batching canonical read for the foundation layer. The topic map will decide by then; confidence 0.45 < 0.80, days_spent 1 < 5 — no advancement today.

---

*Note: general web search unavailable this run; paper discovery via arXiv API with retry/backoff. All three abstracts verified (fetch_arxiv_retry.py --ids / --query). FastServe's remembered arXiv ID (2301.11784) was wrong (cattle trade network paper) — recovered via exact-title search; correct ID is 2305.05920.*
