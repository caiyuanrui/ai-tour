# 2026-08-31 — RL for Agents

Course: Agents
Topic: RL for Agents
Stage: Day 2 — the GRPO-for-tool-use school: outcome rewards, sample efficiency, and reward layers
Confidence: 0.35 -> 0.50

## Today's Question

Day 1 mapped the RL-for-agents design space at the conceptual level: three reward channels (scalar environment reward, exploration-derived preference pairs, learned reward models) and the trajectory-level verifier hierarchy (environment success → ORM → generative trajectory RM → exploration pairs). Day 1's Next Step named the concrete comparison to attack next: the **GRPO-for-tool-use family** (Tool-R1 / RLFactory line) versus the exploration-pair school (ETO, Day 1 related).

Today's question: **when the reward channel is a scalar signal computed from tool/environment feedback — the R1/GRPO school — what concrete reward design choices and training-system tricks make it work for agentic tool use?** Specifically: what counts as a "verifiable" outcome reward when the task is not math or code, how do you make GRPO sample-efficient when online tool rollouts are expensive, and where does the reward/credit machinery get shaped (observation markers, token masking, reward layers)?

## Main Paper

### Metadata

- Title: Tool-R1: Sample-Efficient Reinforcement Learning for Agentic Tool Use
- Authors: Yabo Zhang, Yihan Zeng, Qingyun Li, Zhen Hu, Kavin Han, Wangmeng Zuo
- Year: 2025
- Venue: arXiv 2509.12867
- Link: https://arxiv.org/abs/2509.12867

### Why this paper?

Day 1's open question #4 asked whether the reasoning topic's RLVR machinery (verifiable rewards, GRPO) transfers to agents where "verifiable" is fuzzy. Tool-R1 is the direct answer: it takes the R1 recipe — outcome-based reward guiding policy optimization — and adapts it to tool use, showing exactly what "verifiable" means when the tool is code execution. It also answers the sample-efficiency half of open question #2 (how scalar-reward RL survives the cost of online tool rollouts) with a dynamic sample queue. It is the canonical member of the GRPO-for-tool-use family that Day 1's Next Step named.

### Core Problem

LLMs are strong at language and reasoning but limited on real-world tasks that require up-to-date knowledge, precise operations, or specialized tool use. The R1-style RL recipe (rule-verifiable rewards + GRPO) solved math/code reasoning, but agentic tool use is different: (a) there is no clean rule-verifiable answer — tool output must be judged; (b) online rollouts that actually call tools are expensive, so naive online RL is sample-inefficient; (c) tasks are compositional and multi-step, so credit assignment spans tool calls.

### Main Idea

Tool-R1 trains an LLM to perform general, compositional, multi-step tool use **by generating executable Python code**. Two design moves:

1. **Outcome-based reward that composes two verifier rungs:** (a) **code execution success** (the rule-based rung — did the generated code run) and (b) **LLM-based answer judgment** (the generative-judge rung — did the final answer satisfy the query). This is the reasoning topic's verifier hierarchy (rule → generative RM) re-posed at trajectory granularity, exactly as Day 1 predicted.
2. **Dynamic sample queue for sample efficiency:** high-quality trajectories are cached and reused across training steps, reducing the overhead of costly online sampling. The queue is the system-level answer to "online tool RL is expensive."

Supporting detail: Tool-R1 supports user-defined tools and standard libraries, with **variable sharing across steps** so a multi-step workflow builds coherent state (the output of one tool call feeds the next), which is what makes the code-native action space compositional.

### Experiments / Results

- Benchmark: GAIA (broad, real-world agentic QA).
- Result: ~10% gain over strong baselines on accuracy, with larger improvements on complex multi-step tasks; robustness also improves.
- Claim: the combination of outcome rewards + sample queue is what makes tool-augmented reasoning reliable and efficient.

### Limitations

- The LLM-as-judge reward rung is itself a model: it can be noisy, biased, or gamed as the policy improves (the reasoning topic's reward-hacking concern, now at the judge level).
- The action space is Python code execution — this covers code-accessible tools but says nothing about GUI, web clicks, or embodied actions (the generalization question for open question #4).
- "High-quality" trajectories in the sample queue need a quality filter; reuse risks distribution shift as the policy improves (old trajectories become stale).
- Single-benchmark (GAIA) evidence; no head-to-head against the preference-pair school (ETO) on identical tasks.

### Research takeaway

For the topic map: **the verifier hierarchy transfers to agents almost verbatim — rule rung (execution success) + generative-judge rung (LLM-as-judge) — and the binding constraint is sample efficiency, not reward design.** The dynamic sample queue is the first concrete answer to Day 1's "systems bottleneck" axis at the algorithm level.

### Modern perspective

Read against Day 1: the survey said "reward and credit design is the heart of agent RL"; Tool-R1 shows the reward design reduces to composing two cheap rungs (execution success + LLM judge), and the harder problem is feeding the optimizer enough good experience per unit cost. Read against the reasoning topic: this is RLVR for tools — the verifiable-reward trick works as soon as you define "verifiable" as *executable* rather than *checkable by rule*.

## Related Papers

### Paper 1: RLFactory: A Plug-and-Play Reinforcement Learning Post-Training Framework for LLM Multi-Turn Tool-Use

- **Authors:** Jiajun Chai, Guojun Yin, Zekun Xu, Chuhuai Yue, Yi Jia, Siyu Xia, Xiaohan Wang, Jiwen Jiang et al. (2025)
- **Link:** https://arxiv.org/abs/2509.06980

**Contributions:**
- A plug-and-play RL post-training framework for **multi-round** tool use with three distinct pieces: (i) **tool-call stability** — an asyncio-based asynchronous caller plus a decoupled tool/training architecture that survives tool heterogeneity and interface failures; (ii) **a reward layer supporting rule-based, model-judgment, and tool-verification signals** — i.e. a pluggable verifier hierarchy for diverse evaluation needs; (iii) **MDP reconstruction** — observation markers derived from tool feedback close the loop among model, tools, and environment, driving a generate-parse-invoke-update workflow for dynamic policy optimization.
- Results: training on Search-R1 with Qwen3-4B, it reaches **0.486 test score on Natural Questions**, beating larger models trained with similar techniques (Qwen2.5-7B-Instruct-GRPO at 0.473), and increases training throughput **6.8×**.

**Relation to main paper:** RLFactory is the competing implementation of the same GRPO-for-tool-use school. Where Tool-R1 hard-codes one reward composition, RLFactory exposes the reward layer as a configurable design axis (rule / judge / tool-verification) — this is Day 1's verifier hierarchy made into a pluggable system component. Its async caller + decoupled architecture attacks the same systems bottleneck Tool-R1 addresses with a sample queue, from the engineering side. Its observation markers are a concrete credit-assignment shaping mechanism for open question #1.

**Deep-read later:** Yes — the reward-layer abstraction is the most directly reusable artifact for the "verifier transfer" thesis idea; its ablation of which reward rung matters when is the natural next read.

### Paper 2: Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning

- **Authors:** Bowen Jin, Hansi Zeng, Zhenrui Yue, Jinsung Yoon, Sercan Arik, Dong Wang, Hamed Zamani, Jiawei Han (2025)
- **Link:** https://arxiv.org/abs/2503.09516

**Contributions:**
- Extends RL-for-reasoning to retrieval: the LLM learns to autonomously generate (multiple) search queries during step-by-step reasoning with real-time retrieval, optimizing full reasoning trajectories with multi-turn search interactions.
- Two concrete machinery choices: **retrieved token masking** (stabilizes RL training by masking retrieved text in the loss — the model is not asked to predict tool output, only to use it) and a **simple outcome-based reward**.
- Results: +41% (Qwen2.5-7B) and +20% (Qwen2.5-3B) over RAG baselines on seven QA datasets; also contributes empirical insights into RL optimization methods, LLM choices, and response-length dynamics in retrieval-augmented reasoning.

**Relation to main paper:** Search-R1 is the predecessor/foundation of the family — Tool-R1's name inherits the R1 lineage, and RLFactory literally post-trains Search-R1. Search is a tool, so Search-R1 is the first clean demonstration that outcome-based reward + GRPO works when the tool is a search engine; Tool-R1 generalizes the same recipe to arbitrary code-accessible tools. The retrieved-token masking is the most instructive credit-shaping trick of the three papers: it tells the policy "tool feedback is context, not text to imitate," a sibling of RLFactory's observation markers.

**Deep-read later:** Maybe — its empirical study of response-length dynamics is a useful caution for verbosity collapse in tool-RL (ties to the multi-objective open question).

## Current Understanding

Day 2 makes the GRPO-for-tool-use school concrete, and the topic map now has three distinct layers:

1. **The reward design reduces to composing cheap verifier rungs.** Tool-R1 = execution success (rule) + LLM-as-judge (generative); RLFactory = a pluggable reward layer with rule / model-judgment / tool-verification rungs; Search-R1 = simple outcome reward. The reasoning topic's verifier hierarchy transfers almost verbatim — the difference is that the *rule* rung for agents is "did the tool execute," not "is the answer correct," and everything above it is judge-shaped. This directly answers Day 1 open question #4: environment/tool feedback is a strong enough base verifier when success is executable; a learned judge (or tool-verification) rung is added when it is not.

2. **Sample efficiency is the binding constraint, and it is attacked from both sides.** Tool-R1 caches and reuses high-quality trajectories (algorithm side); RLFactory uses an async caller + decoupled architecture for 6.8× throughput (engineering side). Day 1's "systems bottleneck" axis is now populated with concrete mechanisms — and a new question: sample-queue reuse risks stale-trajectory distribution shift as the policy improves.

3. **Credit assignment shaping happens through the information channel, not the reward function.** Search-R1 masks retrieved tokens in the loss ("tool output is context, not text to imitate"); RLFactory injects observation markers to close the MDP loop. Neither needs per-step reward models — they shape what the policy attends to and what it is scored on. This is the first concrete evidence for Day 1's credit-assignment-granularity question: the current practice is *terminal reward + channel-level shaping*, not per-tool-call rewards.

4. **The ETO-vs-GRPO comparison crystallizes.** ETO (Day 1) needs no reward function at all — it learns from the agent's own failure pairs via DPO, off-policy and cheap, but inherits DPO's known long-horizon credit weakness. Tool-R1/RLFactory need an outcome reward but are on-policy, explore and recover directly, and can use execution/judge signals. The honest trade-off is: **reward-free + off-policy (ETO) vs reward-required + on-policy (GRPO) — sample efficiency and reward reliance are the two axes a controlled comparison must measure** (open question #2, still unanswered head-to-head).

## Key Concepts

- Outcome-based reward for tool use = code execution success (rule rung) + LLM answer judgment (generative-judge rung)
- Verifier hierarchy transfers to agents: rule (execution) → model judgment → tool verification
- Code-native action space: executable Python as the tool-calling interface with variable sharing across steps
- Dynamic sample queue: caching + reusing high-quality trajectories to cut online rollout cost
- Sample-queue staleness: reused trajectories can drift out of distribution as the policy improves
- Reward layer as a pluggable system component (rule / judge / tool-verification signals)
- Async tool caller + decoupled tool/training architecture (tool heterogeneity and interface robustness)
- MDP reconstruction via observation markers from tool feedback (generate-parse-invoke-update loop)
- Retrieved-token masking: tool output is context, not text to imitate (loss-level credit shaping)
- GRPO-for-tool-use family: Search-R1 (retrieval tool) → Tool-R1 (code tools) → RLFactory (framework)
- "Verifiable" for agents = executable (vs "checkable by rule" for math/code)
- ETO vs GRPO trade-off axes: reward-free off-policy (DPO) vs reward-required on-policy (PPO/GRPO)

## Open Questions

- **LLM-as-judge in the RL loop:** how reliable is the judge rung as the policy improves — does the judge drift, can the policy game it (reward hacking at the judge level), and does the reasoning topic's "judge must be reasoning-aware" lesson apply to tool agents? (new, sharpened from Day 1 Q4)
- **ETO vs GRPO head-to-head:** on the same agent task suite, do exploration-derived preference pairs (reward-free, off-policy DPO) or outcome-reward GRPO win in sample efficiency and final performance — and does the answer depend on reward verifiability? (Day 1 Q2, now concrete enough to design)
- **Credit-assignment granularity:** do channel-level shaping tricks (retrieved-token masking, observation markers) suffice, or does per-tool-call / per-decision-point reward shaping beat terminal-only rewards on long horizons? (Day 1 Q1, now with two concrete mechanisms to test)
- **Beyond executable tools:** does the outcome-reward recipe generalize past code/search tools to web navigation, GUI, and embodied control, where "execution success" is fuzzier? (Day 1 Q4, sharpened)
- **Sample-queue staleness:** how should "high-quality" trajectories be selected for reuse, and does reuse introduce distribution shift or reward-hacking amplification as the policy evolves? (new)
- **SFT-bootstrap → RL curricula:** how much and what kind of SFT data gates the gains from Tool-R1-style RL? (Day 1 Q5, still open)
- **Stability:** what are the agent-domain analogues of the reasoning topic's Echo Trap in multi-turn tool RL — verbosity collapse, judge overfitting, execution-loop repetition? (Day 1 Q7, now with Search-R1's response-length dynamics as evidence the problem is real)
- **Multi-objective agent RL:** how to trade task success against cost, latency, safety, and verbosity when reward rungs are multiple and conflicting? (Day 1 Q6, still open)

## Possible Thesis Ideas

- **Reward-rung selector (verifier transfer, now concrete):** operationalize RLFactory's reward layer as a taxonomy of agent reward rungs (rule → judge → tool-verification) and learn which rung or composition is cheapest-sufficient per task family — the "verifier transfer from reasoning to agents" idea gains a concrete substrate.
- **Judge-hacking-resistant tool RL:** detect and penalize the policy's exploitation of the LLM-judge rung (analogous to R1-Zero's format-reward gaming), e.g. an anomaly detector comparing judge scores against execution-grounded evidence.
- **ETO vs GRPO controlled study:** on a fixed tool-use suite, measure sample efficiency, stability, and generalization of exploration-pair DPO vs outcome-reward GRPO, varying reward verifiability — the field's most direct unanswered comparison.
- **Credit-shaping via channel masking:** extend Search-R1's retrieved-token masking and RLFactory's observation markers into a general recipe for "tool output as context" — study whether loss-level masking replaces per-step reward shaping.
- **Sample-queue curriculum:** a staleness-aware replay strategy for dynamic sample queues (when to evict, how to re-weight old trajectories) to prevent distribution shift in online tool RL.

## Next Step

Day 3 should attack the credit-assignment axis now that it has concrete mechanisms: pick a paper that studies **process-level shaping for agent trajectories** — either a process-reward/step-level approach for tool agents, or a study of token/observation masking versus terminal rewards. Alternative (if a verified candidate surfaces): a **web-agent RL** paper to test the outcome-reward recipe beyond executable tools — the AgentQ-class gap from Day 1 remains; do not re-attempt AgentQ keyword search (it is not on arXiv under that title), use `--ids` only with a verified ID.

---

*Search note: web_search unavailable in this cron environment; candidates discovered via arXiv API (fetch_arxiv_retry.py) with full abstracts. All three arXiv IDs verified by direct lookup (Tool-R1 2509.12867, RLFactory 2509.06980, Search-R1 2503.09516).*
