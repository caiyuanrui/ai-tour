# 2026-09-04 — RL for Agents

Course: Agents
Topic: RL for Agents
Stage: Day 3 — the credit-assignment axis: dense turn-level rewards vs terminal-only outcomes
Confidence: 0.50 -> 0.62

## Today's Question

Day 2 (Tool-R1 / RLFactory / Search-R1) showed that the GRPO-for-tool-use school reduces reward design to composing cheap verifier rungs (execution success + LLM judge) and attacks sample efficiency from both the algorithm side (dynamic sample queue) and the engineering side (async caller). But Day 2's open question #3 was left unresolved: **credit-assignment granularity** — the current practice is *terminal outcome reward + channel-level shaping* (retrieved-token masking, observation markers); nobody had shown whether per-decision-point / per-turn reward shaping actually beats terminal-only rewards on long agent trajectories, or what mechanism would implement it.

Day 2's Next Step made this the Day 3 priority: "pick a paper that studies process-level shaping for agent trajectories — either a process-reward/step-level approach for tool agents, or a study of token/observation masking versus terminal rewards."

Today's question: **when trajectories grow to tens or hundreds of tool calls, is terminal outcome reward the right supervision unit — and what concrete mechanisms exist for densifying credit down to the turn or token level, without paying for expensive process annotations or per-step critics?**

## Main Paper

### Metadata

- Title: TRACE: Turn-level Reward Assignment via Credit Estimation for Long-Horizon Agents
- Authors: Leitian Tao, Baolin Peng, Wenlin Yao, Tao Ge, Hao Cheng, Mike Hang Wang, Jianfeng Gao, Sharon Li
- Year: 2026 (arXiv 2607.13988, 2026-07-15)
- Venue: arXiv
- Link: https://arxiv.org/abs/2607.13988

### Why this paper?

Day 2's open question #3 named the exact paper class to attack next: per-decision-point / per-turn reward shaping for long agent trajectories. TRACE is the cleanest verified member of that class I could find: it assigns **dense turn-level rewards via credit estimation** — no critic, no process labels, no cold-start SFT — and reports large gains on a long-horizon search benchmark (BrowseComp-Plus). It is the direct empirical answer to the question "does per-turn shaping beat terminal-only rewards on long horizons?", and its mechanism (a frozen-reference log-ratio as a state value, with TD across tool-call boundaries) is concrete and transferable.

### Core Problem

Multi-turn agents solve complex tasks through extended sequences of tool interactions before producing a final answer. Credit assignment is the fundamental challenge: **outcome rewards are reliable for short-horizon reasoning but become sparse and high-variance as trajectories grow to tens or hundreds of tool calls — and they are misleading.** A failed rollout may contain many useful actions that moved the agent closer to the goal, yet outcome-only training assigns them the same negative advantage as the eventual mistake. This is Day 2's "terminal reward + channel shaping" status quo being attacked at the reward level: the shaping so far happened in the *information channel* (what tokens the policy attends to / is scored on); TRACE shapes the *reward itself* at tool-call granularity.

### Main Idea

TRACE densifies credit using only quantities already available in policy-gradient training:

1. **Represent rollouts as state transitions at tool-call boundaries** — the trajectory is cut into turns, each ending in a tool call, so credit can be assigned per turn rather than once at the end.
2. **Gold-answer log-probabilities from a frozen reference model** are obtained and transformed into **log-ratio state values** (the log-ratio of policy vs reference probability of the gold answer is used as a value estimate of the current state — the RLHF-style advantage proxy repurposed as a value function).
3. **Per-action rewards are derived as Temporal-Difference (TD) changes in those log-ratio state values** — each turn gets the *change* in estimated state value, not a share of the terminal outcome.
4. **No additional critic and no process-label training** — the frozen reference model replaces the learned value function, which is the elegant trick: process supervision without paying for process labels.
5. A property worth noting: the **one-step log-ratio TD component telescopes across redundant tool calls**, which prevents redundant turns from accumulating spurious credit — important for search trajectories that contain repeated/parallel tool calls.

### Experiments / Results

- **Setup:** pure RL — *no cold-start supervised fine-tuning stage, no agentic mid-training stage, no training on live-web data*. Base models trained directly with the dense reward.
- **Closed-web BrowseComp-Plus:** Qwen3-4B from **7.2 → 35.6**; Qwen3-30B-A3B from **8.4 → 42.6** (roughly a 5× relative gain on the small model).
- The learned search behavior **transfers to open-web benchmarks** (not just the closed-web training distribution).
- Learning curves show **earlier improvement and faster convergence** during RL training — the dense signal starts moving the policy before terminal outcomes would arrive.

### Limitations

- **Requires a gold answer** whose log-probability the reference model can score. Search/QA tasks have canonical golds; many agent tasks (open-ended web, GUI, negotiation) do not — the method's applicability outside answer-grounded domains is the open question.
- The **frozen reference model is now a load-bearing component**: its log-probability calibration quality bounds the value estimates. As the policy improves past the reference, log-ratios grow and could become unstable or gameable (verbosity/format exploits that inflate gold-answer logprobs) — the reasoning topic's reward-hacking concern re-posed at the log-ratio level.
- Evidence is from the search/tool-use domain (BrowseComp family); GUI/embodied generalization is untested. (These last two points are inferences from the abstract + the method's structure, not claims the paper's abstract states outright.)

### Research takeaway

For the topic map: **the credit-assignment granularity question has a concrete affirmative answer — per-turn TD-style dense rewards over log-ratio state values beat terminal-only outcomes on long horizons, and they can be built without critics or process labels by reusing the frozen reference model as the value source.** This closes the loop with Day 2's channel-level shaping: masking says "tool output is context, not text to imitate" (loss level); TRACE says "each turn's contribution to reaching the gold is its own reward" (reward level). They operate on different layers and are plausibly complementary — a question Day 4/5 should note.

### Modern perspective

Read against the reasoning topic's RLVR: TRACE is RLVR's answer to the "sparse reward for long agentic trajectories" failure mode — the *same* verifiable-reward school, but with the terminal verifier's signal diffused backward in time via TD. Read against Day 1's ETO: both reject terminal-only scalar reward, but ETO replaces it with contrastive *pairs* from exploration (off-policy DPO), while TRACE keeps the scalar channel and makes it *dense* (on-policy TD). That contrast is now the sharpest open comparison in the topic: dense-scalar vs pair-based credit, both claiming to fix long-horizon credit.

## Related Papers

### Paper 1: Contrastive Branch Policy Optimization (CBPO)

- **Authors:** Ying Wang, Changlin Qiu, Bang Lin, Linbo Jin, Wen Jiang, Zhe Sun, Jingli Yang (2026)
- **Link:** https://arxiv.org/abs/2608.24300

**Contributions:**
- Identifies that RLVR's sparse outcome rewards give no signal for which intermediate decisions caused success, and that branch sampling — the standard way to induce local comparisons — conflates **two distinct problems**: allocating a fixed rollout budget, and translating branch outcomes into token-level credit.
- **Disentangles them:** generation-entropy screens candidate branch positions across the whole response; path-level and node-level decay distribute a fixed budget across trajectories and positions (preventing exploration collapse onto a few paths or adjacent tokens).
- **Contrastive Branch Value (CBV):** a parent trajectory plus branches sharing an identical token prefix form an *exact-prefix group*; reward variation within that controlled group is an outcome-based estimate of *local decision sensitivity*, used to rescale continuation advantages **without changing their sign**. Multiple selected nodes on one trajectory → the trajectory is partitioned into non-overlapping credit segments, avoiding duplicated gradients on shared tokens.
- **Requires only outcome rewards, no process-level annotation.** Results: 10 benchmarks (5 math reasoning + 5 knowledge-intensive search), consistently outperforms SOTA policy-optimization and branch-based methods at two model scales.

**Relation to main paper:** CBPO is the competing mechanism for the exact same problem — both answer "how do we densify credit for long tool-integrated trajectories using only outcome rewards?" TRACE uses TD over frozen-reference log-ratio state values; CBPO uses contrastive branch values from budgeted branch sampling. TRACE needs a gold-answer-scoring reference; CBPO needs a rollout-budget allocation policy. Both explicitly avoid process labels and critics — converging evidence that the field's credit-assignment frontier is *outcome-only dense credit*, and the design space splits on where the value signal comes from (reference log-probs vs sampled branches).

**Deep-read later:** Yes — as the main comparison axis for a possible "dense credit assignment methods" thesis chapter or survey.

### Paper 2: LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents

- **Authors:** Yiming Du, Yuxin Jiang, Tao Yuan, Jianbo Dai, Shaowei Wang, Jierun Chen, Chaofan Tao, Xianzhi Yu, Lifeng Shang, Kam-Fai Wong, Xiaohui Li, Haoli Bai (2026)
- **Link:** https://arxiv.org/abs/2608.17393

**Contributions:**
- Observes that RL for coding agents runs inside **long-running agent harnesses** (OpenHands SDK, Claude Code, OpenCode), whose native execution environments are **misaligned with policy-gradient training**: environmental crashes and reward hacking corrupt outcome signals, and train-inference discrepancies decouple rollout behavior from policy updates.
- **Three pillars:** (1) *faithful optimization* — in-process LLM proxying captures raw generation streams for token-level alignment and robust trainer-side log-probability recomputation, even under harness-side compaction or re-serialization; (2) *reliable execution* — scalable sandbox orchestration with image caching and stage-wise anti-reward-hacking defenses; (3) *observable training* — an integrated plugin automating validation/monitoring plus a Live UI for trajectory diagnostics.
- **Results:** trains sparse-MoE Qwen3.5-35B-A3B with GSPO across three native harnesses; SWE-bench Verified improves OpenHands SDK 64.0→70.4, Claude Code 62.4→68.2, OpenCode 57.2→66.6, while keeping rollout-training probability correlation above 0.99.

**Relation to main paper:** LEGO-RL is the *systems precondition* for everything TRACE and CBPO do. TRACE's log-ratio TD and CBPO's advantage rescaling both assume the trainer's log-probabilities faithfully match what the policy actually rolled out; LEGO-RL's in-process proxying + trainer-side logprob recomputation exists precisely because harness compaction/re-serialization silently breaks that assumption. It also connects the credit-assignment axis to the architectures topic's **harness** concept (Day 1 of that topic: the scaffold around the model matters as much as the model) and to the reasoning topic's stability question (Echo Trap) at the systems level: reward hacking here isn't the policy gaming a judge — it's the *environment/harness* corrupting the outcome signal.

**Deep-read later:** Yes — as the systems-layer reference for any "RL for coding agents" project; its anti-reward-hacking sandbox defenses are directly reusable.

## Current Understanding

Day 3 fills the credit-assignment layer of the RL-for-agents map, and the topic now has four populated layers:

1. **The reward channel design is a solved-enough layer (Days 1-2).** Scalar outcome rewards can be composed from cheap verifier rungs (execution success + LLM judge), and "verifiable" for agents means *executable*. Sample efficiency is handled by queues and async systems.

2. **Credit assignment granularity is now a real design axis with verified mechanisms (Day 3).** Three mechanisms, all outcome-only:
   - **Terminal-only + channel masking** (Day 2 status quo; Search-R1's retrieved-token masking, RLFactory's observation markers) — shapes what the policy attends to, leaves the reward sparse;
   - **Dense turn-level TD** (TRACE) — frozen-reference log-ratio state values, per-turn TD rewards, telescopes across redundant calls; large verified gains (BrowseComp-Plus 7.2→35.6 / 8.4→42.6) *without* cold-start SFT;
   - **Token-level contrastive credit** (CBPO) — budgeted branch sampling + exact-prefix contrastive branch values rescaling continuation advantages.
   The map's rule of thumb is now: **the longer and more tool-dense the horizon, the more the reward should be densified; the design space splits on where the value signal comes from (reference log-probs vs sampled branches), and both avoid process labels.**

3. **Systems fidelity is the silent precondition.** LEGO-RL shows that harness crashes, reward hacking at the environment level, and train-inference logprob drift quietly corrupt *any* credit-assignment scheme, because dense credit is computed from log-probabilities. Rollout-train probability correlation (>0.99 in LEGO-RL) is a newly visible hygiene metric for the whole school.

4. **Two open comparisons crystallize.** (a) Dense-scalar (TRACE) vs pair-based (ETO) credit — both fix long-horizon credit, neither has been run head-to-head on identical tasks. (b) TRACE's "no cold-start SFT needed when credit is dense" result directly challenges the SFT-bootstrap→RL curriculum assumption from Day 1's open questions — if dense credit removes the need for an agentic SFT mid-training stage, the curriculum question splits into "how much SFT for protocol fidelity" vs "how dense must the reward be to skip SFT."

## Key Concepts

- Long-horizon credit assignment: outcome rewards sparse, high-variance, and misleading for tens-to-hundreds of tool calls
- Turn-level reward assignment via TD over state values (per-tool-call-boundary credit)
- Frozen-reference log-ratio as a state value (gold-answer log-probabilities, no critic, no process labels)
- One-step log-ratio TD telescoping across redundant tool calls
- Pure-RL result: dense credit removes the need for cold-start SFT / agentic mid-training / live-web data
- Outcome-only dense credit as the field's convergence point (TRACE and CBPO both avoid process annotations)
- Branch sampling budget allocation vs branch-to-token credit translation (CBPO's disentanglement)
- Exact-prefix groups + Contrastive Branch Value: outcome-based local decision-sensitivity estimate
- Non-overlapping credit segments to avoid duplicated gradients on shared tokens
- Harness-native RL: native harness environments misaligned with policy-gradient training
- Train-inference discrepancy: harness compaction/re-serialization decouples rollout behavior from policy updates
- Rollout-training probability correlation as a hygiene metric for logprob-faithful RL
- Reward hacking at the environment/harness level (vs policy-level judge gaming)
- Dense-scalar vs pair-based credit (TRACE vs ETO) as the sharpest open comparison

## Open Questions

- **Where does the value signal for dense credit come from?** TRACE uses a frozen reference model scoring gold answers; CBPO uses budgeted branch sampling. When is each cheaper/more robust, and does a hybrid (reference log-ratios *and* branch contrasts) dominate? (new)
- **Does dense credit remove the SFT-bootstrap requirement generally?** TRACE shows pure RL works for long-horizon search without cold-start SFT. Does that hold for GUI/web/embodied agents, where protocol fidelity (action syntax) is harder to discover by exploration? (sharpened from Day 1 Q5)
- **Dense-scalar vs pair-based head-to-head:** TRACE-style TD over log-ratio values vs ETO-style exploration preference pairs — same task suite, sample efficiency + final performance. (Day 1 Q2, now with two concrete dense-credit implementations)
- **Gold-answer dependence:** TRACE needs gold answers to score; how far can log-ratio state values stretch toward tasks with no canonical gold (open-ended web, GUI, negotiation)? (new)
- **Does channel-level masking compose with dense rewards?** Day 2's retrieved-token masking shapes the loss; TRACE shapes the reward. Additive or redundant? (new)
- **Log-ratio stability and gaming:** as the policy improves past the frozen reference, do log-ratio TD rewards become unstable or exploitable (verbosity/format inflation of gold-answer logprobs)? (new — the reasoning topic's reward-hacking concern at the log-ratio level)
- **Systems fidelity:** how many production agent-RL runs are silently degraded by harness-level logprob drift (compaction, re-serialization), and should rollout-train probability correlation become a standard reported metric? (new)
- **Beyond search/tool domains:** do TRACE/CBPO transfer to GUI (Android/web) and embodied control, where "gold" and even "turn boundaries" are fuzzier? (Day 1 Q4, still open — Day 4 target)
- **ETO vs GRPO head-to-head**, **judge reliability/drift**, **multi-objective agent RL**, **stability analogues of Echo Trap** — carried forward from Day 2, still open.

## Possible Thesis Ideas

- **Credit-source selection for agent RL** — a meta-controller choosing between dense-credit mechanisms (reference log-ratio TD, branch-contrastive, channel masking, terminal-only) per task family, priced by gold-answer availability × rollout budget × horizon length — operationalizes the Day 3 design space as a measurable axis.
- **Gold-free log-ratio value estimation** — extend TRACE's frozen-reference trick to tasks without gold answers, using outcome-free proxy targets (e.g. reference-model agreement, verifier scores, self-consistency) as the state-value basis; measures how much of dense credit's gain survives without golds.
- **Dense-vs-pair credit, controlled** — TRACE-style TD vs ETO-style preference pairs on a fixed long-horizon tool suite: the topic's sharpest unanswered comparison, now with concrete implementations on both sides.
- **SFT-free agent RL curriculum** — follow TRACE's no-cold-start result: map the task families where pure dense-credit RL replaces the SFT→RL ladder entirely, and where protocol fidelity still forces an SFT rung.
- **Log-ratio reward-hacking defenses** — detect/penalize policy exploitation of frozen-reference log-ratio rewards (verbosity/format inflation), the TRACE-domain analogue of R1-Zero's format gaming.
- **Harness-fidelity auditing** — build a rollout-train probability correlation monitor (LEGO-RL's metric) as a standard diagnostic for agent RL runs across harnesses.

## Next Step

Day 4 (next agents run, Mon 2026-09-07) should close the last big gap in the topic's open question #8 / Day 1 Q4: **does the outcome-reward recipe generalize past code/search tools to GUI and web agents, where "execution success" is fuzzy?** Main-paper candidate is **DigiRL** (verified arXiv **2406.11896**, "DigiRL: Training In-The-Wild Device-Control Agents with Autonomous Reinforcement Learning", Bai 2024, NeurIPS 2024) — offline RL warm start + offline-to-online RL inside a parallelized Android environment with a VLM-based evaluator; it also tests reward design under stochasticity and non-stationarity (advantage estimators enhanced for stochasticity + automatic curriculum), which triangulates the Day 2/3 sample-efficiency and credit themes from the GUI domain. Related candidates: the Agent-R1 unified agentic-RL framework (verified arXiv **2511.14460**) for the framework/comparison axis, and optionally AgentGym/SWE-RL — note SWE-RL and AgentGym remembered IDs were wrong this run (see footer); verify before use. Day 5 (Fri) is the topic capstone.

---

*Search note: web_search unavailable and the arXiv API host (export.arxiv.org) was unreachable/429-throttled this run; candidates were discovered and verified via the arxiv.org search UI + abstract pages (HTML) with a stdlib parser. Semantic Scholar was also 429 at run time. Wrong remembered IDs recorded for future runs: DigiRL = 2406.11896 (NOT 2406.04896), SWE-RL 2504.18487 is a physics paper, AgentGym 2407.13844 is a lyophilization paper, Agent-R1 2503.22781 is a medical paper; the Agent-R1 unified framework ID 2511.14460 verified correct. All three selected papers (TRACE 2607.13988, CBPO 2608.24300, LEGO-RL 2608.17393) verified by direct abstract-page lookup with full abstracts.*
