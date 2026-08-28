# 2026-08-28 — RL for Agents

Course: Agents
Topic: RL for Agents
Stage: Day 1 — the map: what makes RL-for-agents different from RL-for-reasoning
Confidence: 0.00 -> 0.35

## Today's Question

The Reasoning topic (completed 2026-08-24) mapped how RL-style signals grow *reasoning*: verifiable rewards, the verifier hierarchy, GRPO/RLVR, and the reward-engineering triad (densification / learned estimation / signal creation). RL-for-agents is the same family of tools aimed at a different target — **agent behavior**: multi-turn tool use, web navigation, environment interaction, recovery from failures. Today's question: **when the objective is not a correct answer but a successful trajectory, what are the distinct RL training signals, design axes, and system bottlenecks — and how do they differ from the reasoning setting?**

This is Day 1, so per the topic-ordering rule the main paper is a survey/context paper that lays out the whole design space.

## Main Paper

### Metadata

- Title: Reinforcement Learning Foundations for Deep Research Systems: A Survey
- Authors: Wenjun Li, Zhi Chen, Jingru Lin, Hannan Cao, Wei Han, Sheng Liang, Zhi Zhang, Kuicai Dong et al.
- Year: 2025
- Venue: arXiv 2509.06733
- Link: https://arxiv.org/abs/2509.06733

### Why this paper?

The topic question asks *how* RL-style training signals improve agent behavior; this survey is, by its own claim, the first dedicated to the RL foundations of agentic (deep-research-style) systems. It systematizes exactly the axes this topic needs to map: data synthesis, RL methods for agentic research (stability, sample efficiency, long-context handling, reward and credit design, multi-objective), and agentic RL training systems — plus evaluation. It also gives the cleanest statement of why RL beats SFT/DPO for agents, which anchors the whole topic.

### Core Problem

Agentic systems (Planner + Coordinator + Executors, tools like search/browse/code) are trained in practice as a **single planner** connected to core tools, because end-to-end training of the full stack is impractical. The training-method problem: **SFT imparts protocol fidelity but suffers from imitation bias, exposure bias, and underuses environment feedback. DPO is schema- and proxy-dependent, off-policy, and weak for long-horizon credit assignment and multi-objective trade-offs — and both rely on human-defined decision points and labeled comparisons.** RL is the principled alternative because it optimizes trajectory-level policies, enabling exploration, recovery behaviors, and principled credit assignment, while reducing dependence on human priors and rater biases.

### Main Idea

The survey organizes RL-for-agents along three axes:

1. **Data synthesis and curation** — how to generate/curate trajectories for RL training (the agent's "experience" plays the role that static corpora play for SFT).
2. **RL methods for agentic research** — covering: stability (PPO/GRPO tuning), sample efficiency, long-context handling, **reward and credit design** (the heart of the topic: outcome vs process rewards, learned RMs, verifiable rewards, credit assignment over long horizons), multi-objective optimization, and multimodal integration.
3. **Agentic RL training systems and frameworks** — the infrastructure bottleneck: rollout generation, environment interaction, reward computation, and policy updates at scale.

It also covers agent architecture/coordination and evaluation/benchmarks (QA, VQA, long-form synthesis, domain-grounded tool-interaction tasks).

### Technical Details

- Frames the SFT → DPO → RL progression as a ladder: SFT = imitation/exposure-biased but cheap; DPO = off-policy preference optimization, weak on long-horizon credit assignment; RL = on-policy trajectory-level optimization with exploration and recovery, the only one that uses closed-loop environment feedback directly.
- Identifies the standard deployment pattern: hierarchical stacks (Planner/Coordinator/Executors) but training a single planner with tool access, not the whole stack.
- Distills recurring patterns across recent agentic-RL work and surfaces infrastructure bottlenecks (rollout throughput, environment stability, reward latency) plus practical guidance for training robust agents.

### Research takeaway

The survey's central claim for this topic's map: **for agent behavior, the training signal is the trajectory, and the two hard problems are (a) credit assignment over long horizons and (b) reward design when success is not rule-verifiable.** These are exactly the gaps SFT and DPO cannot close, and exactly where the reasoning topic's verifier hierarchy (rule → ORM → generative RM → search-densified) gets re-posed at trajectory granularity.

### Modern perspective

Read against the Reasoning capstone: RLVR (R1) solved rule-verifiable *reasoning*; RL-for-agents inherits the same machinery but faces **sparser, later, noisier, and less verifiable rewards** over longer horizons, plus an environment in the loop that must be simulated, sandboxed, and kept stable during training. The survey is the map; ETO and AGILE (related papers) are two concrete instantiations of the design space — exploration-based DPO-style trajectory optimization and full PPO with an agentic stack.

## Related Papers

### Paper 1: Trial and Error: Exploration-Based Trajectory Optimization for LLM Agents (ETO)

- **Authors:** Yifan Song, Da Yin, Xiang Yue, Jie Huang, Sujian Li, Bill Yuchen Lin (2024)
- **Link:** https://arxiv.org/abs/2403.02502

**Contributions:**
- Proposes ETO (Exploration-based Trajectory Optimization): instead of training only on successful expert trajectories, the agent **explores, fails, and learns from its exploration failures**.
- Iterative loop: exploration phase collects failure trajectories to form contrastive trajectory pairs; training phase updates the policy with **DPO on those preference pairs**.
- Consistently surpasses baselines on three complex tasks, and remains effective even when no expert trajectory is available — a key property for open-ended agent domains.

**Relation to main paper:** ETO is the "learning signal from exploration, not from a scalar reward" school. The survey says RL enables exploration and recovery; ETO shows a concrete, cheap instantiation — you don't need an environment reward function at all, just contrastive pairs from the agent's own failures. It answers part of the reward-design axis: *preference pairs from exploration are a valid reward channel for agents*.

**Deep-read later:** Yes — DPO-based trajectory optimization is a direct competitor axis to reward-model-based RL (GRPO/PPO) and connects to the reasoning topic's DPO threads; also relevant to sample-efficiency thesis ideas.

### Paper 2: AGILE: A Novel Reinforcement Learning Framework of LLM Agents

- **Authors:** Peiyuan Feng, Yichen He, Guanhua Huang, Yuan Lin, Hanchong Zhang, Yuchen Zhang, Hang Li (2024)
- **Link:** https://arxiv.org/abs/2405.14751

**Contributions:**
- AGILE (AGent that Interacts and Learns from Environments): formulates LLM-agent construction as an RL problem where **the LLM is the policy model**, fine-tuned with **PPO**.
- The agent goes beyond conversation: **reflection, tool usage, and expert consultation**, with memory.
- Releases ProductQA (challenging online-shopping QA); experiments on ProductQA, MedMCQA, HotPotQA show **7B/13B PPO-trained agents outperform GPT-4 agents**.
- Ablation study shows memory, tools, consultation, reflection, **and RL are all indispensable** — RL is not a marginal add-on.

**Relation to main paper:** AGILE is the "full PPO stack" school: the survey's axis-2 methods (PPO stability) + axis-1 (data) realized in one framework, and it gives the cleanest ablation evidence that RL training signals matter on top of a capable agent architecture. It also foreshadows the RLHF-adjacent question of what reward signal drives PPO here (task success + auxiliary signals).

**Deep-read later:** Maybe — the ablation methodology (which component contributes what) is a model for how to evaluate agent-RL contributions; the exact reward design would be worth checking against the survey's reward/credit axis.

## Current Understanding

The RL-for-agents map begins with a clean division of labor vs. the Reasoning topic:

1. **The training signal is the trajectory, not the answer.** In reasoning, a correct answer (or unit test) verifies the trace; in agents, the environment's response to actions over many turns is the only ground truth. This shifts the problem from "reward the right answer" to "credit the right actions" — the survey's long-horizon credit assignment axis.
2. **Three RL training-signal channels are now visible:** (a) scalar rewards from the environment/verifiers (PPO/GRPO — AGILE, and the reasoning topic's RLVR family), (b) preference pairs from the agent's own exploration failures (DPO — ETO), (c) learned reward models when neither rule nor preference is cheap (the reasoning topic's ORM/MGRM line, which carries over directly).
3. **SFT/DPO/RL is a ladder, not a menu.** The survey's framing: SFT = protocol fidelity (imitation/exposure biased), DPO = off-policy preference optimization (weak on long-horizon credit), RL = on-policy trajectory optimization (exploration + recovery + credit assignment, but hardest to stabilize). Most practical systems will use all three in sequence — SFT to bootstrap, then RL on top.
4. **Systems matter as much as algorithms.** Rollout generation, environment stability, and reward latency are the recurring infrastructure bottlenecks; this echoes the architectures topic's "harness engineering" lesson — RL-for-agents is a systems problem as much as a learning problem.
5. **The reasoning topic's verifier hierarchy survives, re-posed at trajectory granularity.** Rule-based → ORM → generative RM → search-densified becomes: environment success → learned outcome RM → generative trajectory RM → exploration-derived preference pairs (ETO). Same ladder, longer horizon, noisier rungs.

## Key Concepts

- RL for agents = trajectory-level policy optimization with environment feedback in the loop
- SFT → DPO → RL ladder: imitation/exposure bias → off-policy preference limits → on-policy credit assignment
- Long-horizon credit assignment as the central agent-RL problem
- Reward design axes: scalar environment reward, learned reward models, exploration-derived preference pairs
- ETO (Exploration-based Trajectory Optimization): contrastive trajectory pairs from failures + DPO update
- AGILE: LLM-as-policy PPO framework with reflection, tools, expert consultation, memory
- Planner/Coordinator/Executor hierarchical stacks trained as a single planner + tools
- Data synthesis and curation as RL-for-agents axis 1
- Agentic RL training systems: rollout throughput, environment stability, reward latency bottlenecks
- Trajectory-level verifier hierarchy (environment success → ORM → generative RM → exploration pairs)

## Open Questions

- What is the right credit-assignment granularity for long agent trajectories — per-tool-call, per-decision-point, or only terminal? Does the answer depend on horizon length or task type?
- How do exploration-derived preference pairs (ETO) compare against scalar-reward RL (PPO/GRPO) in sample efficiency and final performance, on the same agent tasks?
- The survey says DPO is weak for long-horizon credit assignment — but ETO applies DPO to whole trajectories. Is the fix trajectory-level framing, or is DPO fundamentally limited for agents?
- Can the reasoning topic's RLVR machinery (verifiable rewards, GRPO) be transferred to agents where "verifiable" is fuzzy (web success, task completion) — is environment feedback a strong enough verifier, and when does it need a learned RM?
- How should SFT-bootstrap → RL-finetune curricula be designed for agents — how much SFT data before RL, and does the answer vary by task family (web, tool, embodied)?
- Multi-objective agent RL: how to trade task success against cost, latency, safety, and verbosity when rewards are multiple and conflicting (survey's multi-objective axis is under-explored)?
- Stability: what are the agent-domain analogues of the reasoning topic's Echo Trap — and do PPO/GRPO stabilization tricks transfer?
- Is the single-planner-with-tools pattern a ceiling — would hierarchical RL over Coordinator + Executors beat it, and what reward/credit machinery would that require?

## Possible Thesis Ideas

- **Exploration-pair vs reward-model RL for agents, controlled** — on a fixed agent task suite (tool use / web), compare ETO-style DPO on exploration pairs vs GRPO with learned ORM, measuring sample efficiency, stability, and generalization; map which tasks prefer which reward channel.
- **Credit-assignment granularity for tool-using agents** — vary the reward granularity (terminal-only, per-tool-call, per-decision-point) and measure learning speed + final success; produce a practical recipe for when to use process-shaped signals.
- **Verifier transfer from reasoning to agents** — reuse the reasoning topic's verifier hierarchy (rule → ORM → generative RM) as a *taxonomy of agent reward channels* and build a selector that picks the cheapest sufficient channel per task family.
- **SFT-then-RL curriculum design for agents** — measure how the SFT bootstrapping corpus size/quality gates downstream RL gains; identify the minimal SFT prerequisite for RL to add value.
- **Multi-objective agent RL** — reward design that jointly optimizes success, cost, and safety with explicit trade-off controls, addressing the survey's under-explored multi-objective axis.

## Next Step

Day 2 should attack the top open question: the concrete comparison between exploration-derived preference pairs (ETO) and scalar-reward RL for agents — ideally a follow-up/competing method in the trajectory-optimization school, or a canonical GRPO-for-tool-use paper (e.g. the Tool-R1 / RLFactory line surfaced during today's search). Also candidate: a canonical web-agent RL paper (AgentQ-class) if it surfaces reliably, to triangulate the reward-design axis from the web domain.

---

*Search note: web_search unavailable in this cron environment; candidates discovered via arXiv API (fetch_arxiv_retry.py) with full abstracts. AgentQ did not surface under any queried title form (name collisions with quantum-computing papers) — deferred to a later day rather than forced from memory.*
