# 2026-08-26 — Batching and Scheduling

Course: LLM Systems
Topic: Batching and Scheduling
Stage: Day 2 — Prediction-Based Scheduling (SSJF / output-length prediction)
Confidence: 0.45 -> 0.58

## Today's Question

Day 1 mapped the scheduling design space along three axes: cache-aware request scheduling (SGLang / RadixAttention), preemptive policy under unknown output lengths (FastServe / skip-join MLFQ), and cross-instance dynamic scheduling (Llumnix). The Day-1 note left open question #6: *prediction-based scheduling — output-length predictors (ELIS/SSJF) claim big wins — how robust are they across workloads, and do they compose with cache-aware batching?*

Today drills into the **prediction axis**: can the scheduler know *in advance* how long a request will run, and should it schedule on that knowledge? Three papers triangulate the axis — SSJF (the canonical proxy-model + SJF scheduler, directly named in the open question), ProD (why *point* prediction is fundamentally unreliable — output length is a heavy-tailed prompt-conditioned distribution), and ESTP (the modern predictor: entropy + semantic attention signals harvested for free from prefill, integrated end-to-end with a length-aware scheduler).

## Main Paper

### Metadata

- **Title:** Efficient Interactive LLM Serving with Proxy Model-based Sequence Length Prediction (SSJF)
- **Authors:** Haoran Qiu, Weichao Mao, Archit Patke, Shengkun Cui, Saurabh Jha, Chen Wang, Hubertus Franke, Zbigniew T. Kalbarczyk, Ravishankar K. Iyer (UIUC + IBM Research)
- **Year:** 2024
- **Venue:** arXiv:2404.08509
- **Link:** https://arxiv.org/abs/2404.08509

### Why this paper?

Day 1's open question #6 named ELIS/SSJF as the concrete paper class for the prediction axis. SSJF is the verified, canonical representative: a complete system (predictor + scheduler) with clean, large wins over FCFS. It is the natural day-2 main paper because it converts the axis's vague question ("can prediction help?") into a concrete mechanism ("proxy-model length prediction → speculative shortest-job-first") whose weaknesses the two related papers then attack directly.

### Core Problem

LLM requests have **unknown, highly variable execution times** because generation is autoregressive — the scheduler does not know how long a job will run until it finishes. FCFS (the default in most serving stacks) therefore suffers **head-of-line blocking**: a short request queues behind a long one. This is the same problem OS schedulers solved decades ago with shortest-job-first (SJF), but SJF requires knowing job sizes, which LLM serving does not provide.

### Main Idea

**Speculative shortest-job-first (SSJF):** use a *light proxy model* to predict each request's output sequence length from its input, then schedule requests in SJF order. The key design stance: prediction is *speculative* — an estimate used to form a priority ordering, not a guarantee — and the scheduler is a **scheduling-layer-only change**: SSJF does not modify memory management or batching strategies, so it drops into existing engines that already do dynamic or continuous batching.

### Technical Details

- **Proxy model as job-size oracle:** a small, fast model trained on (prompt → observed output length) pairs predicts each request's length before it enters the scheduling queue. The proxy must be far cheaper than the target model's own prefill+decode, or the prediction cost eats the gains.
- **SJF ordering on predictions:** the queue is ordered shortest-predicted-first, attacking the head-of-line blocking failure mode directly (the abstract confirms the scheduler is speculative SJF using proxy-model predictions).
- **No changes to memory/batching:** the contribution is orthogonal to PagedAttention-style memory management and Orca-style continuous batching — it layers on top, which is why its gains (2.2–3.6× throughput vs FCFS) appear *across* no-batching, dynamic-batching, and continuous-batching settings.
- **Results (abstract-verified):** 30.5–39.6% lower average job completion time and 2.2–3.6× throughput vs FCFS schedulers, evaluated on real-world datasets and production workload traces.

*Note: the exact proxy-model architecture (model class, training recipe) and the misprediction-correction mechanics are not in the abstract; they should be verified against the full paper when web access is available. What is abstract-verified: proxy-model prediction, speculative SJF, scheduling-layer-only scope, and the headline numbers above.*

### Limitations

- **Prediction accuracy ceiling:** the scheduler is only as good as the proxy. A long job mispredicted as short jumps the queue and delays everyone — the *worst case* of SJF with bad estimates.
- **Fairness / starvation:** SJF is optimal for *mean* completion time but can starve long jobs under load — directly touching Day 1's open question #5 (the fairness axis, cf. Satori-style fair scheduling).
- **Point prediction is fundamentally noisy:** for prompts whose output length is underdetermined (same prompt → many plausible lengths), a single predicted scalar is a weak signal — ProD (below) formalizes exactly this.
- **Proxy cost:** a separate model adds inference overhead and a training/maintenance burden; ESTP (below) is motivated precisely by eliminating this.
- **No composition story:** the paper does not study how prediction interacts with cache-aware batching (SGLang radix-tree reuse) or preemptive policies (FastServe) — the open composition questions from Day 1 remain.

### Research takeaway

Length prediction converts the LLM scheduling problem from *"job sizes unknown"* to *"job sizes noisy"* — and SJF on noisy estimates still delivers 2-3× throughput wins. This reframes Day 1's insight: the scheduler's information problem is attackable at the **prediction layer**, not just the policy layer. Prediction-based scheduling is a distinct, fourth axis of the design space: cache-aware (SGLang), preemptive (FastServe), cross-instance (Llumnix), and *length-aware* (SSJF).

### Modern perspective

2025–2026 work treats the *predictor* as the bottleneck, not the scheduler. ProD (2604.07931) argues point targets are the wrong supervision (heavy-tailed length distributions), and ESTP (2608.15592) replaces the separate proxy model with signals extracted from the target model's own prefill (entropy + attention). The axis is maturing into a serving-stack primitive — length-aware scheduling now appears in end-to-end system evaluations (ESTP integrates with a length-aware scheduler and reports throughput + padding-ratio gains). The open frontier: composing length prediction with radix-tree cache reuse, MoE serving (Gimbal-style coordinated scheduling explicitly avoids output-length prediction — an interesting contrast), and agent workloads.

## Related Papers

### Paper 1 — Robust Length Prediction: A Perspective from Heavy-Tailed Prompt-Conditioned Distributions (ProD)

- **Authors:** Jing Wang, Yu-Yang Qian, Ke Xue, Chao Qian, Peng Zhao, Zhi-Hua Zhou (Nanjing University)
- **Year:** 2026 · arXiv:2604.07931 · https://arxiv.org/abs/2604.07931

**Contribution (quick note):**
- Shows that even under a fixed model and decoding setup, the *same prompt* induces a **prompt-conditioned output-length distribution**, not a deterministic scalar — and this distribution is consistent with **heavy-tailed** behavior. Single-shot sampled lengths are therefore unreliable training targets.
- Casts length prediction as **robust estimation from heavy-tailed distributions**: ProD-M uses a median-based target for robust point prediction; ProD-D uses a distributional target that preserves prompt-conditioned uncertainty. Both variants reuse the served LLM's own hidden states.
- Provides theoretical justification (estimation-error analysis under a surrogate model) and consistent gains in prediction quality across diverse scenarios.

**Relation to main paper:** ProD attacks SSJF's weakest component — how the predictor is trained. SSJF's proxy learns from observed lengths as if each prompt had one true length; ProD shows that supervision is noisy by construction and that robust targets (median / distribution) fix it. Same axis, methodological upgrade: *better prediction targets, not better scheduling policy*.

### Paper 2 — When Entropy Is Not Enough: Reclaiming Lost Semantics in LLM Output Length Prediction (ESTP)

- **Authors:** Feiyang Ren, Shengtao Wen, Lingbing Guo, Yu Tian, Yuanning Cui, Xiang Chen
- **Year:** 2026 · arXiv:2608.15592 (Aug 2026) · https://arxiv.org/abs/2608.15592

**Contribution (quick note):**
- Critiques **entropy-guided token pooling**: token-wise entropy ignores differences in *semantic content*, so important tokens are underweighted and low-information tokens get disproportionate weight — hurting length-prediction reliability.
- **ESTP (Entropy-and-Semantic Token Pooling)** combines entropy with **attention-based importance scores** derived from self-attention weights computed during prefill — capturing both uncertainty and semantic importance with minimal extra compute and near-zero memory overhead.
- On the ForeLen benchmark: better prediction accuracy / lower error than entropy-only baselines; integrated with a **length-aware scheduler** end-to-end, it improves throughput and reduces the padding ratio.

**Relation to main paper:** ESTP is the predictor-design axis *two years later*: SSJF needed a separate proxy model (cost + maintenance); ESTP shows the signal can be harvested for free from the target model's prefill activations — and demonstrates the end-to-end scheduler integration SSJF's successors aim for. It also partially answers the "how robust" half of open question #6: better signals → more robust predictions.

## Current Understanding

The batching-scheduling map after Day 2 gains a **fourth axis: prediction-based (length-aware) scheduling**:

1. **Batching granularity (foundation):** request-level → iteration-level (continuous batching) → token-level (Dynamic SplitFuse).
2. **Cache-aware scheduling (SGLang):** scheduling = cache management; batches formed to maximize radix-tree prefix reuse.
3. **Preemptive policy (FastServe):** scheduling = latency control under uncertainty; token-granularity preemption with KV offloading.
4. **Cross-instance scheduling (Llumnix):** scheduling = placement over time; live migration across engines.
5. **Length-aware scheduling (SSJF + ProD + ESTP):** scheduling = ordering under noisy job-size estimates. The predictor converts unknown lengths into noisy estimates; SJF on the estimates delivers 2-3× wins; robustness comes from better targets (ProD: median/distributional, heavy-tailed-aware) and better signals (ESTP: prefill entropy + semantic attention).

Cross-axis interactions now visible: SJF's starvation risk connects to fairness (open question #5); misprediction could be corrected by FastServe-style preemption (speculative + preemptive hybrid); batch formation by prediction vs. by prefix-reuse are two competing batch-shaping signals that nobody has unified. Also new: the length-prediction axis gives LLM serving the *job-size oracle* OS schedulers have had since SJF — but with an accuracy tax, and with the extra wrinkle that the distribution is heavy-tailed and prompt-conditioned (ProD).

Confidence 0.45 -> 0.58: the prediction axis is now understood end-to-end (canonical system, robustness critique, modern predictor). Still missing: fairness-aware scheduling, deadline/SLO-aware scheduling, MLA-cache-aware scheduling, and agent-workload-specific scheduler design — those remain for Days 3-5.

## Key Concepts

- SSJF: speculative shortest-job-first scheduling driven by proxy-model output-length prediction
- Proxy-model length prediction: light model trained on (prompt → observed length) to estimate job size before scheduling
- Output-length prediction as scheduling signal: converting unknown autoregressive cost into a noisy estimate
- Heavy-tailed prompt-conditioned length distributions: the same prompt induces a length *distribution*, not a scalar (ProD)
- Robust length-prediction targets: median (ProD-M) / distributional (ProD-D) supervision instead of single-sample labels
- Entropy + semantic token pooling (ESTP): prefill self-attention importance scores combined with token entropy for near-free length prediction
- Length-aware scheduling: end-to-end schedulers that consume predicted lengths to shape batching/ordering and reduce padding

## Open Questions

- What is the *optimal* cache-aware scheduling policy — can radix-tree reuse be co-optimized with prefill/decode batching and SLOs, or is it inherently heuristic? *(carried)*
- How do preemption (FastServe), cache-awareness (SGLang), and instance migration (Llumnix) interact? Preempting evicts/offloads KV — does it destroy the reuse cache-aware scheduling preserves? *(carried)*
- For agent workloads (short, tool-interleaved, shared system prompts): is prefix reuse the dominant win (SGLang) or does tail-latency control (FastServe-style preemption) matter more? *(carried)*
- How does scheduler design change with MLA-style caches (14× smaller KV)? Migration and preemption get cheaper — does that shift the optimal policy? *(carried)*
- Fairness: continuous batching lets long requests starve short ones (max-driven batch-cost effect) — what is the right fairness/throughput trade-off, and does SJF-style prediction *add* a starvation axis? *(carried + sharpened)*
- How robust are proxy-model length predictions across workloads, and what is the accuracy-vs-overhead trade-off of the proxy model itself (vs. free prefill-derived signals like ESTP)? *(from today)*
- If prompt-conditioned output length is a heavy-tailed distribution (ProD), is *point* prediction the right target at all — or should schedulers consume distributions (quantile-aware SJF, risk-aware ordering)? *(from today)*
- Do length-prediction schedulers compose with cache-aware batching? Prediction reshapes batch formation — does it help or hurt radix-tree prefix reuse (SGLang)? *(from today)*
- Can SSJF's starvation risk be bounded without losing its mean-completion-time gains — e.g. hybrid SJF+aging or fair-share over predicted lengths? *(from today)*
- Length prediction for MoE: does expert routing interact with predicted lengths (cf. Gimbal, which explicitly avoids output-length prediction)? *(from today)*

## Possible Thesis Ideas

- **Cache-aware + preemptive unified scheduler:** jointly maximize radix-tree reuse and support token-granularity preemption with KV offloading — the two axes currently live in separate systems. *(carried)*
- **Agent-aware scheduling policy:** exploit agent workload structure (system prompt + tool schema as long-lived shared prefixes, short interleaved turns) to optimize cost-per-tool-call and SLO attainment. *(carried)*
- **SLO-constrained cache-aware batching:** batch formation as an optimization over prefix-reuse × deadline-feasibility (extends DistServe's goodput framing with the reuse dimension). *(carried)*
- **Scheduling under MLA caches:** quantify how 14× smaller KV caches change the preemption-vs-reuse trade-off. *(carried)*
- **Robust length-prediction + cache-aware unified scheduler:** consume *distributional* length targets (ProD-style) inside a radix-tree batch former (SGLang-style) — prediction used for batch formation and memory reservation, not just queue ordering. *(from today)*
- **Fair length-aware scheduling:** SSJF + bounded starvation — quantile-based SJF or aging over predicted lengths, with a fairness/throughput Pareto analysis (answers the sharpened open question #5). *(from today)*
- **Speculative length correction:** hybrid of SSJF's prediction and FastServe-style preemption so mispredictions are corrected on the fly (predict → run → correct on overrun) — the two axes each compensate the other's failure mode. *(from today)*
- **Zero-cost predictors from prefill activations:** ESTP-style attention/entropy signals as a drop-in length predictor for existing schedulers — no proxy model, no extra inference; study accuracy across workloads and integration with continuous batching. *(from today)*

## Next Step

Day 3 should pick the next concrete axis from the carried open questions. The strongest candidates: (a) **fairness-aware scheduling** (open question #5 now sharpened by SSJF's SJF starvation risk — Satori, "Towards Efficient and Fair LLM Serving", is the canonical target), (b) **deadline/SLO-aware scheduling** (the goodput framing from inference-serving Day 2, extended to per-request deadlines), or (c) the **prediction × preemption hybrid** (open question #6 follow-up). Confidence 0.58 < 0.80, days_spent 2 < 5 — no advancement today.

---

*Note: general web search unavailable this run; paper discovery via arXiv API with retry/backoff (fetch_arxiv_retry.py). All three abstracts verified from arXiv API responses. ELIS (named in Day 1's open question) did NOT surface on arXiv under any queried title form ("Efficient Long Inference via Short-Output Scheduling", "Long Inference AND Short-Output", "ELIS AND short-output" — all zero results); SSJF is the verified canonical representative of the output-length-predictor class. Exact proxy-model architecture details for SSJF are outside the abstract and marked for verification.*
