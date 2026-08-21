# 2026-08-21 — Reasoning

Course: Agents
Topic: Reasoning
Stage: Day 4 — RLVR beyond math/code: reward engineering for agent domains
Confidence: 0.68 -> 0.75

## Today's Question

Day 3 (DeepSeek-R1) established that **RL with verifiable rewards** (RLVR) elicits reasoning in math/code, where a deterministic answer or unit test provides the objective signal. But Day 3's top open questions were: *what counts as "verifiable" in open-ended agent tasks (web navigation, embodied control)?* and *does environment/tool feedback serve as the verifier in RLVR, and does reasoning even emerge there?* Today's question: **when an agent's environment gives sparse, non-rule-verifiable feedback — no deterministic answer, no unit test — how must the reward signal be engineered for R1-style RL to still work?**

## Main Paper

### Metadata

- Title: SEEA-R1: Tree-Structured Reinforcement Fine-Tuning for Self-Evolving Embodied Agents
- Authors: Wanxin Tian, Shijie Zhang, Kevin Zhang, Xiaowei Chi, Chunkai Fan, Junyu Lu, Yulin Luo, Qiang Zhou et al.
- Year: 2025
- Venue: arXiv 2506.21669
- Link: https://arxiv.org/abs/2506.21669

### Why this paper?

Day 3's open question #11 named the concrete frontier: *"Can the R1 recipe extend beyond math/code to open-ended agent tasks (web navigation, tool use, embodied control) — where does the objective correctness signal come from?"* SEEA-R1 is the most direct attack on that question: it takes the R1/RFT recipe (GRPO + RL on a reasoning model) into **embodied agents (ALFWorld)** and makes exactly the two adaptations the question demands — (1) densifying sparse rewards with MCTS rollout estimates inside GRPO (Tree-GRPO), and (2) replacing rule-based rewards with a learned **multimodal generative reward model (MGRM)** for domains where no rule exists. It is the algorithm-lineage follow-up to Day 3's GRPO thread (same family, tree-structured variant).

### Core Problem

RFT (R1-style reinforcement fine-tuning) works when rewards are verifiable (math answers, unit tests). Embodied agent tasks break both assumptions: (1) **sparse delayed rewards** — a single task-level success signal arrives after dozens of steps, giving no intermediate learning signal for multi-step reasoning; (2) **no hand-craftable reward** — defining per-task, per-scene reward functions doesn't generalize to novel tasks and environments, so self-evolution can't happen.

### Main Idea

Two components, each aimed at one obstacle:

- **Tree-GRPO (Tree-based Group Relative Policy Optimization):** merges Monte Carlo Tree Search into GRPO. MCTS rollouts estimate step-level intermediate values, converting the sparse terminal reward into denser per-step signals that guide multi-step reasoning. The group-relative baseline machinery of GRPO is preserved, but the advantage estimates are computed over the tree-structured rollout.
- **MGRM (Multi-modal Generative Reward Model):** a learned reward model that outputs reward estimates across tasks and scenes (textual *and* multimodal observations), replacing hand-crafted reward functions. Because it's generative and trainable, the agent can adapt rewards autonomously — the loop that makes self-evolution (learning from its own rollouts without ground-truth reward) possible.

### Technical Details

- Evaluated on **ALFWorld** (textual and multi-modal settings).
- **With ground-truth reward:** 85.07% (textual) / 46.27% (multi-modal), surpassing prior SOTA and GPT-4o.
- **Without ground-truth reward** (MGRM-only, the self-evolving regime): 80.3% (textual) / 44.03% (multi-modal) — still above all open-source baselines, showing reward estimation generalizes rather than memorizing task-specific rules.
- This is the first RFT framework for embodied self-evolution; Tree-GRPO and MGRM are the two reusable mechanisms.

### Research takeaway

"Verifiable" is a **design variable, not a given**. When no rule exists, you synthesize the verification signal in one of two ways: densify the sparse signal you *do* have (MCTS rollout estimates inside the RL loop) or learn the reward (a generative reward model). SEEA-R1 shows both are compatible with GRPO-family algorithms and that the learned-reward route retains most of the ground-truth performance — the first quantitative evidence that R1-style RL can self-evolve without any verifier at all.

### Modern perspective

Read as part of the reasoning map, SEEA-R1 completes the RLVR picture: the verifier hierarchy is now (1) rule-based verifiers (math/code — R1), (2) learned discriminative RMs (ORM — WebRL, today's related paper), (3) learned generative RMs (MGRM — SEEA-R1), (4) search-densified signals from sparse environment feedback (Tree-GRPO). Each step up the hierarchy trades verifier fidelity for coverage of open-ended tasks. This directly informs Day 3's thesis idea *"verifiable-reward design for agent tasks"* — the design space now has concrete axes.

## Related Papers

### Paper 1: RAGEN: Understanding Self-Evolution in LLM Agents via Multi-Turn Reinforcement Learning

- **Authors:** Zihan Wang, Kangrui Wang, Qineng Wang, Pingyue Zhang, Linjie Li, Zhengyuan Yang, Xing Jin, Kefan Yu et al. (2025)
- **Link:** https://arxiv.org/abs/2504.20073

**Contributions:**
- Proposes **StarPO** (State-Thinking-Actions-Reward Policy Optimization), a general trajectory-level framework for multi-turn agent RL, and **RAGEN**, a modular training/evaluation system, studied on four stylized environments.
- **Echo Trap finding:** multi-turn agent RL exhibits recurring reward variance cliffs and gradient spikes; fixed by StarPO-S (trajectory filtering + critic incorporation + gradient stabilization).
- **The key negative result for the RLVR question:** *without fine-grained, reasoning-aware reward signals, agent reasoning hardly emerges through multi-turn RL* — agents collapse to shallow strategies or hallucinated thoughts.

**Relation to main paper:** RAGEN is the cautionary analysis under SEEA-R1's optimistic result. It says naive trajectory-level RL does **not** automatically elicit reasoning in agent settings — the reward must be reasoning-aware. SEEA-R1's Tree-GRPO densification and WebRL's ORM are exactly the kinds of reward engineering RAGEN's finding says are necessary. Together they answer Day 3's open question #15 (does environment feedback alone suffice in RLVR? — no, unless engineered).

**Deep-read later:** Yes — StarPO/StarPO-S details and the Echo Trap analysis are directly relevant to the *reward-hacking-resistant RL for agents* thesis idea.

### Paper 2: WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning

- **Authors:** Zehan Qi, Xiao Liu, Iat Long Iong, Hanyu Lai, Xueqiao Sun, Wenyi Zhao, Yu Yang, Xinyue Yang et al. (2024)
- **Link:** https://arxiv.org/abs/2411.02337

**Contributions:**
- An online-curriculum RL framework for web agents addressing three challenges: training-task scarcity, sparse feedback, and policy distribution drift.
- Mechanisms: **self-evolving curriculum** (new tasks generated from unsuccessful attempts), a robust **outcome-supervised reward model (ORM)**, and adaptive RL strategies.
- Results: WebArena-Lite success rate 4.8% → 42.4% (Llama-3.1-8B) and 6.1% → 43% (GLM-4-9B), surpassing GPT-4-Turbo (17.6%) and GPT-4o (13.9%).

**Relation to main paper:** The web-domain counterpart to SEEA-R1. WebRL uses a learned **discriminative** ORM trained on outcome labels (sparse web success signals), while SEEA-R1 uses a **generative** reward model plus MCTS densification — two different answers to the same sparse-reward problem. WebRL also adds the curriculum dimension (task generation from failures) that SEEA-R1 lacks, and its ORM is the direct descendant of Day 2's outcome-supervision line (Lightman/Uesato), now deployed as a training-time reward channel rather than a test-time scorer.

**Deep-read later:** Yes — the self-evolving curriculum mechanism is a strong candidate mechanism for the *RL-for-reasoning sample efficiency* thesis idea.

## Current Understanding

The Reasoning map's RL-acquisition pillar now covers the full reward-signal design space. Day 3 established the recipe (GRPO + verifiable rewards) in math/code. Today's set shows what happens when verifiability disappears:

1. **The verifier hierarchy is a design ladder.** Rule-based verifiers (R1, math/code) → learned discriminative ORMs (WebRL, for sparse web success) → learned generative reward models (SEEA-R1's MGRM, for domains with no rule at all) → search-densified signals from sparse environment feedback (Tree-GRPO's MCTS-into-GRPO). Each rung covers more open-ended tasks at the cost of verifier fidelity and reward-hacking surface.
2. **Reward engineering, not just reward choice, is where agent RLVR lives.** Sparse feedback is attacked from three sides: densification (MCTS rollouts), learned estimation (ORM/MGRM), and signal *creation* (WebRL's curriculum generates new training tasks from failures — a data-side fix for the scarcity problem).
3. **Reasoning emergence is not automatic in agents.** RAGEN's negative result (reasoning hardly emerges in multi-turn RL without reasoning-aware rewards) is the crucial caveat to Day 3's optimism: in math/code the verifier is so clean that reasoning emerges as a byproduct; in agent environments the reward must be deliberately shaped or the policy collapses to shallow strategies. This reframes open question #13 (generalization vs task-specific overfitting): the danger is not just gaming a verifier, but the policy never learning to reason at all.
4. **The learned-RM question from Day 2/3 is answered concretely.** Open question #12 ("is there still a role for learned reward models?") — yes: ORMs and generative RMs are the *only* viable reward channel in non-verifiable agent domains, and SEEA-R1 quantifies the ground-truth gap (85.07% → 80.3% textual) when the RM substitutes for the rule.

## Key Concepts

- RLVR beyond math/code: sparse, non-rule-verifiable agent rewards
- Tree-GRPO: MCTS integrated into GRPO for dense intermediate signals from sparse terminal rewards
- MGRM (Multi-modal Generative Reward Model): learned generative reward estimation across tasks/scenes
- Self-evolution without ground-truth reward (80.3% vs 85.07% on ALFWorld textual)
- StarPO (State-Thinking-Actions-Reward Policy Optimization): trajectory-level agent RL
- Echo Trap: reward variance cliffs + gradient spikes in multi-turn agent RL (StarPO-S stabilization)
- Reasoning emergence requires reasoning-aware rewards (RAGEN negative result)
- Self-evolving curriculum: generate new training tasks from unsuccessful attempts (WebRL)
- Outcome-supervised reward model (ORM) as training-time reward channel for web agents
- Verifier hierarchy: rule-based → discriminative RM → generative RM → search-densified sparse signal
- Sparse feedback → densification / learned estimation / signal creation triad

## Open Questions

- Does Tree-GRPO's MCTS densification compose with rule-based verifiers — i.e. is the densification benefit additive to clean verifiable rewards, or only relevant when rewards are sparse?
- How does MGRM's reward estimation generalize across *unseen* environments, and when does it drift into reward hacking (rewarding behavior that looks good but doesn't complete tasks)?
- RAGEN shows reasoning needs reasoning-aware rewards in stylized environments — what exactly makes a reward "reasoning-aware" in real agent tasks (web, embodied)? Is it step granularity, trajectory filtering, or the state/action modeling itself?
- Can WebRL-style curriculum (task generation from failures) be combined with R1-style verifiable rewards to fix both data scarcity AND reward gaming simultaneously?
- Echo Trap: is it a general property of trajectory-level agent RL, and does Tree-GRPO or StarPO-S-style stabilization transfer across frameworks?
- Where does the "shallow strategies or hallucinated thoughts" failure (RAGEN) sit relative to Day 1's intrinsic self-correction failure (Huang 2023) — same root cause (no grounded signal), different manifestation?
- Does emergent self-verification (R1's "aha moment") survive in agent RLVR settings, or does it require the clean rule-verifier setup to arise at all?

## Possible Thesis Ideas

- **Verifiable-reward design for agent tasks (now concrete)** — operationalize the verifier hierarchy (rule → ORM → generative RM → MCTS-densified) as a design space with measurable axes: fidelity, coverage, reward-hacking surface; pick the minimal rung that makes reasoning emerge on a given task family.
- **Reward-shaping via search for sparse-reward agents** — extend Tree-GRPO's MCTS densification to web/tool agents; study where rollout-based intermediate rewards beat learned RMs (and vice versa) per task type.
- **Reasoning-aware reward audit** — a method to detect RAGEN-style "shallow strategy" collapse during agent RL training (reward that is satisfied without reasoning), i.e. an early-warning signal before the policy converges to non-reasoning behavior.
- **Curriculum-from-failure + verifiable-reward hybrid** — combine WebRL's self-evolving curriculum with rule-based verifiers to grow both the task distribution and the reasoning ability jointly; measure whether curriculum-generated tasks close the generalization gap in open question #13.
- **Generative RM drift detection** — monitor MGRM-style reward models for silent reward-hacking drift as the policy evolves; connect to Day 3's reward-hacking detection thesis idea.

## Next Step

Day 5 (capstone) is next agents run (Monday 2026-08-24): synthesize the Reasoning topic — generation (Day 1) → verification (Day 2) → RL acquisition (Day 3) → reward engineering for agent domains (Day 4). Remaining thread to acknowledge in the capstone: the **deferred test-time search axis** (STaR, o1-style verifier-guided search, MCTS reasoning) from Day 1, which was never read — the capstone can position it as the gap between "harvest/grow reasoning" (Days 2–4) and "search reasoning at inference time".
