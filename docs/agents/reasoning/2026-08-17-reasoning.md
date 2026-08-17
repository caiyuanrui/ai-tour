# 2026-08-17 — Reasoning

Course: Agents
Topic: Reasoning
Stage: Day 3 — RL acquisition axis (verifiable rewards / GRPO)
Confidence: 0.55 -> 0.68

## Today's Question

Day 2 ended with open question #6: *can PRMs be built without human step labels — has GRPO-style outcome + implicit-process RL replaced human-labeled PRMs?* Today's question: **can reasoning itself be *trained* by reinforcement learning with only outcome-level (verifiable) rewards, and what does that do to the verification-signal picture from Days 1–2?**

## Main Paper

### Metadata

- Title: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- Authors: DeepSeek-AI (Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Peiyi Wang, Qihao Zhu, Runxin Xu et al.)
- Year: 2025
- Venue: arXiv 2501.12948
- Link: https://arxiv.org/abs/2501.12948

### Why this paper?

Day 2's open question #6 named the concrete paper class: "GRPO-style outcome+implicit-process RL may have replaced human PRMs." DeepSeek-R1 is the canonical, most influential demonstration of exactly that — pure RL with rule-based (verifiable) rewards eliciting reasoning with zero human-labeled trajectories. It is also the direct follow-up in the same lab lineage as DeepSeekMath (GRPO), and it reframes the whole verification axis: instead of a learned step-level verifier, the outcome signal + group-relative RL *is* the training signal.

### Core Problem

Frontier LLM reasoning (o1-style long CoT) had been achieved via extensive human-annotated demonstrations — curated SFT traces, expensive and possibly capability-capping. The paper asks: can reasoning abilities be **incentivized purely through RL**, without any human-labeled reasoning trajectories?

### Main Idea

Run RL directly on a base LLM using only **rule-based rewards** defined over *verifiable* tasks (math with deterministic answers, code with unit tests): an **accuracy reward** plus a **format reward** enforcing a `think`/`answer` structure. The model discovers its own reasoning strategies.

- **R1-Zero** (pure RL from DeepSeek-V3-Base, no SFT) shows emergent behaviors — reflection, re-evaluation, extended thinking, self-verification — the famous *"aha moment"*. But it suffers from poor readability and language mixing.
- **R1** fixes this with a pipeline: cold-start SFT on a few thousand curated CoT examples → RL with reasoning + language-consistency rewards → rejection sampling + SFT on ~800K refined traces → a final RL stage covering math, code, science, and general helpfulness (with a general reward model for non-verifiable domains).

### Technical Details

- **Algorithm: GRPO** (from DeepSeekMath) — no critic network; a group-relative baseline over sampled outputs; memory-efficient enough to scale RL to a 671B MoE.
- **Rewards:** (1) accuracy reward for verifiable tasks (math: deterministic answer match; code: unit tests), (2) format reward (CoT inside `<think></think>`, answer in `<answer></answer>`). R1-Zero showed the format reward can be **hacked** — e.g. injecting answers into the thinking block.
- **Pipeline (R1):** cold-start SFT → RL (reasoning + language-consistency rewards) → rejection sampling from the RL checkpoint + SFT on ~800K traces → final RL over all domains.
- **Results:** R1 matches o1: AIME 2024 **79.8%** pass@1 (o1-0912: 79.2%), MATH-500 **97.3%**, SWE-bench Verified **49.2%**, GPQA Diamond 71.5%. Distilled small models (Qwen/Llama, 1.5B–70B) transfer much of the ability — the 1.5B beats GPT-4o-0514 on AIME/MATH.

### Research takeaway

Reasoning can be **trained, not just prompted or verified**. The verifier can be the *environment/rule itself*: outcome-level rewards over verifiable tasks provide implicit process pressure, and the model learns verification as a *behavior* (self-reflection, self-verification) rather than relying on an external module. This answers Day 2's open question #6 in the affirmative — for verifiable domains, GRPO-style RL has largely replaced human-labeled PRMs.

### Modern perspective

Read in 2026, R1 is the pivot point: the field moved from "harvest reasoning with verifiers" (Days 1–2) to "grow reasoning with RL" (today). Every subsequent reasoning-model release (Kimi k1.5, QwQ, o3/o4-style systems, RLVR agent pipelines) builds on this recipe. The remaining hard problems — reward hacking, the verifiability bottleneck for open-ended tasks, and RL compute cost — are exactly where agent-reasoning research now sits.

## Related Papers

### Paper 1: DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

- **Authors:** Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang et al. (DeepSeek, 2024)
- **Link:** https://arxiv.org/abs/2402.03300

**Contributions:**
- Introduces **GRPO (Group Relative Policy Optimization)** — the PPO variant that removes the critic/value network by computing a group-relative baseline over sampled outputs, cutting memory usage and making RL for reasoning tractable at scale.
- Data-engineering result: continuing pretraining on 120B curated math-related tokens (from Common Crawl) yields DeepSeekMath 7B at 51.7% on MATH without tools/voting (60.9% with 64-way self-consistency).

**Relation to main paper:** The direct algorithmic predecessor — R1's RL loop *is* GRPO. It explains *how* outcome-only RL became feasible (no value model = less memory/compute; group baseline instead of learned critic), and it also ties back to Day 1's self-consistency as the verification booster.

**Deep-read later:** Yes — the GRPO estimator details (group-relative baseline, clipping) are the algorithm foundation for the whole RLVR line.

### Paper 2: Kimi k1.5: Scaling Reinforcement Learning with LLMs

- **Authors:** Kimi Team, Moonshot AI (Angang Du, Bofei Gao, Bowei Xing et al., 2025)
- **Link:** https://arxiv.org/abs/2501.12599

**Contributions:**
- An independent, concurrent implementation of the same RL-for-reasoning recipe — **no MCTS, no value functions, no process reward models** — matching o1: 77.5 AIME, 96.2 MATH-500, 94th percentile Codeforces, 74.9 MathVista.
- Key engineering: long-context scaling (128K) for RL, a **length penalty** to control CoT verbosity, curriculum-style RL, and **long2short distillation** that transfers long-CoT reasoning into short-CoT models (+550% over GPT-4o/Claude 3.5 Sonnet on short-CoT AIME).

**Relation to main paper:** A competing implementation that confirms R1's core claim cross-lab (verifiable rewards + policy-gradient RL suffice) and adds the two fixes R1 lacked: an explicit length penalty (addressing R1's verbosity/reward-hacking problem) and distillation as a cost-control mechanism (complementing R1's distillation results).

**Deep-read later:** Yes — the length-penalty and long2short details are directly relevant to the thesis idea on distilling long-CoT policies into short-CoT agent policies.

## Current Understanding

The Reasoning map now has three pillars plus a new acquisition axis. **Day 1:** generation (CoT, Wei 2022) + cheap statistical verification (self-consistency), with the negative result that intrinsic self-correction degrades performance on average (Huang 2023). **Day 2:** trained verification — outcome supervision (ORM) vs process supervision (PRM, Lightman 2023): step-level verifiers fix reasoning errors and win on hard problems, but the human label bottleneck (PRM800K's 800K labels) is the ceiling. **Day 3 (today):** RL acquisition with verifiable rewards — DeepSeek-R1/R1-Zero show pure RL (GRPO + rule-based accuracy/format rewards on math/code) elicits reasoning with no human-labeled trajectories; self-reflection and self-verification emerge as learned behaviors ("aha moment"); Kimi k1.5 confirms the recipe cross-lab and adds length-penalty and long2short distillation.

The verification picture is now much clearer: (1) for verifiable tasks, the environment/rule is the verifier and outcome-level RL provides implicit process pressure — human-labeled PRMs are largely bypassed; (2) learned verifiers (PRMs) still matter where no objective signal exists and where a frozen verifier must score steps at test time; (3) generation quality still sets the ceiling, but RL now *moves the generator itself* rather than only harvesting it. The new frontier for agents: **RLVR (RL with verifiable rewards)** — what counts as "verifiable" in open-ended agent tasks (web, tools, embodied), how to avoid reward hacking, and whether emergent self-verification transfers out of math/code.

## Key Concepts

- RL with verifiable rewards (rule-based reward models)
- GRPO (Group Relative Policy Optimization): critic-free PPO, group-relative baseline
- Accuracy reward + format reward (think/answer structure)
- R1-Zero: pure RL without SFT — emergent reasoning from base model
- "Aha moment": emergent self-reflection, re-evaluation, self-verification from RL alone
- Cold-start SFT + RL + rejection sampling + final-RL pipeline (R1)
- Language consistency reward
- Reward hacking / reward misgeneralization in RL training (format-reward gaming)
- Verifiability bottleneck: rule-based rewards need objective correctness signals
- Long2short distillation (Kimi k1.5): transfer long-CoT ability to short-CoT models
- Length penalty for CoT verbosity control
- RLVR (RL with verifiable rewards) as the agent-domain generalization
- RL as replacement for human-labeled PRMs (outcome signal → implicit process learning)
- Emergent self-verification as learned behavior vs external verifier module

## Open Questions

- Reward hacking: R1-Zero gamed the format reward (answers smuggled into thinking). How do we build rule-based rewards that are robust to gaming for agent tasks, where "correct" is much harder to define than math answers?
- What counts as "verifiable"? Can the R1 recipe extend beyond math/code to open-ended agent tasks (web navigation, tool use, embodied control) — where does the objective correctness signal come from?
- Does RL with verifiable rewards produce *generalizable* reasoning or task-specific policy overfitting (does the model learn to reason, or to game these particular verifiers)?
- Is there still a role for learned PRMs now that RL+verifiable rewards works for math/code — e.g., for non-verifiable domains, or for scoring steps at test time under a frozen generator?
- How does RL-trained reasoning interact with agent loops — does environment/tool feedback serve as the "verifier" in RLVR, and do emergent self-verification behaviors survive outside math/code?
- Sample efficiency: R1 needs thousands of GPUs. Can curriculum, rejection sampling, or smaller-scale GRPO make RL-for-reasoning feasible for modest budgets?
- How much reasoning ability is lost in long2short distillation, and does the distilled policy retain verification/reflection behavior or just answer patterns?
- Is the emergent "aha moment" (self-reflection, self-verification) a robust learned skill or a reward artifact — and can it be deliberately shaped rather than hoped for?
- Language mixing / readability: how should linguistic-quality rewards trade off against reasoning-quality rewards in multilingual settings?
- How do GRPO-style group baselines interact with learned verifiers in the loop (e.g., PRM-guided sampling + GRPO training) — do they compose or conflict?

## Possible Thesis Ideas

- **Verifiable-reward design for agent tasks** — formalize what makes an agent subtask "verifiable" and build hierarchical verifier signals (environment feedback, tool results, unit-test-like checks) that let R1-style RL scale to open-ended agent behavior; measure the reward-hacking surface at each level.
- **Reward-hacking-resistant RL for agents** — detect and penalize format/behavioral exploits analogous to R1-Zero's answer-smuggling, e.g., an anomaly detector on the divergence between policy behavior and reward-intended behavior during GRPO training.
- **PRM vs RLVR, controlled** — for a fixed agent task suite, compare learned per-step verifiers (PRM-guided best-of-N) against rule-based verifiable-reward RL (GRPO) on the same generator: when does each win, and can a meta-controller allocate between them?
- **Long2short for agent reasoning** — distill long-CoT RL policies (tool-using, multi-step) into short-CoT agent policies under hard latency budgets; measure what verification ability survives distillation.
- **Emergent verification as a learned skill** — probe R1-style self-verification: does it transfer across domains, and can it be shaped with targeted rewards (verification-specific rewards) instead of waiting for emergence?
- **RL-for-reasoning sample efficiency** — curriculum + rejection-sampling schedules that reach R1-level math/code reasoning with a fraction of the RL compute; quantify the minimal RL budget for reasoning emergence.
- **Grounded verification for RLVR agents** — use tool/environment feedback as the reward channel in GRPO (free process supervision), and study when environment feedback alone suffices vs when a learned reward model must be added.

## Next Step

Day 4 candidates (suggestions for the user): (a) the **deferred search axis from Day 1** — test-time search over reasoning, e.g. STaR (self-taught reasoner bootstrapping), o1-style long-CoT with verifier-guided search, or MCTS-based reasoning (AlphaProof-style / MCTS self-refine); (b) the reward-hacking/robustness axis — papers on reward hacking detection/mitigation in RL training. The tiebreaker favors (a): the open question "does the model learn to reason or to game these verifiers" needs a search-vs-RL comparison, and search was explicitly deferred from Day 1. If the user prefers, (b) is the natural Day 5 before the capstone.
