# 2026-08-24 — Reasoning Capstone: Generation → Verification → RL Acquisition, and the Missing Test-Time-Search Bridge

Course: Agents
Topic: Reasoning
Stage: Capstone (Day 5) — Topic summary and advance
Confidence: 0.75 → 0.83

## Today's Question

After four days of mapping the Reasoning topic — generation, verification, RL acquisition, and reward engineering for agent domains — what is the unified picture, and where is the frontier for thesis-level work?

## Topic Map: Reasoning

```
Agent Architectures (completed)
└── Tool Use (completed)
    └── Planning (completed)
        └── Memory (completed, 5d / 15 papers / conf 0.82)
            └── Reasoning (completed, 5d / 15 papers / conf 0.83)
                └── RL for Agents (NEXT →)
```

| Day | Date | Focus | Main Paper | Conf After |
|-----|------|-------|-----------|------------|
| 1 | Aug 10 | Generation / survey | Chain-of-Thought Prompting (Wei 2022) | 0.35 |
| 2 | Aug 14 | Verification / PRM | Let's Verify Step by Step (Lightman 2023) | 0.55 |
| 3 | Aug 17 | RL acquisition / verifiable rewards | DeepSeek-R1 (DeepSeek-AI 2025) | 0.68 |
| 4 | Aug 21 | RLVR beyond math/code / reward engineering | SEEA-R1 (Tian 2025) | 0.75 |
| 5 | Aug 24 | **Topic Synthesis** | Unified picture and open frontier | **0.83** |

## Journey Recap

### Day 1 — The Canonical Foundation: Generation
**Main**: Chain-of-Thought prompting (Wei 2022) — intermediate reasoning steps as exemplars and generated traces; the "scratchpad" that externalizes computation; an emergent ability that appears only at scale.
**Related**: Self-consistency (Wang 2022) — sample diverse paths + majority vote, the cheapest statistical "verification"; Huang 2023 — intrinsic self-correction fails without external feedback and can even degrade answers.
**Insight**: The topic's central tension was born here: **generation vs. verification**. CoT showed models can *produce* traces; the question the whole field then chased is how to know *which* trace is right.

### Day 2 — Trained Verification: Outcome vs. Process Supervision
**Main**: Let's Verify Step by Step (Lightman 2023) — process reward models (PRMs) beat outcome reward models (ORMs) on hard tasks (MATH 78%); PRM800K's 800K human step labels made per-step verification a scalable training target.
**Related**: Uesato 2022 — outcome supervision is competitive on easy tasks (GSM8K), process needed for reasoning errors; Snell 2024 — test-time compute allocation by prompt difficulty gives 4x+ efficiency over best-of-N, and a small model + test-time compute beats a 14x larger model.
**Insight**: Verification became a *learned, step-granular signal* and a *compute allocator*. The PRM800K human-label bottleneck was the ceiling that pushed the field toward RL-based implicit process learning (Day 3).

### Day 3 — RL Acquisition: Reasoning Can Be Trained, Not Just Harvested
**Main**: DeepSeek-R1 — pure RL (GRPO) with rule-based verifiable rewards (accuracy + format) on math/code elicits reasoning with zero human-labeled trajectories; R1-Zero's "aha moment" (emergent self-reflection, self-verification); full pipeline = cold-start SFT → RL → rejection sampling → final RL.
**Related**: DeepSeekMath (GRPO algorithm — critic-free PPO with group-relative baseline), Kimi k1.5 (independent cross-lab confirmation + length penalty + long2short distillation).
**Insight**: For verifiable domains, the environment/rule *is* the verifier and outcome-level RL provides implicit process pressure — human-labeled PRMs are largely bypassed. The agent-domain question became: **what counts as "verifiable" in open-ended tasks?**

### Day 4 — When Verifiability Disappears: Reward Engineering for Agent Domains
**Main**: SEEA-R1 (Tian 2025) — Tree-GRPO (MCTS rollouts densify sparse terminal rewards inside GRPO) + MGRM (learned multimodal generative reward model replaces hand-crafted rewards); self-evolution without ground-truth reward retains most performance (80.3% vs 85.07% on ALFWorld textual).
**Related**: RAGEN — the cautionary negative result: without *reasoning-aware* rewards, multi-turn agent RL collapses to shallow strategies or hallucinated thoughts (Echo Trap variance cliffs); WebRL — self-evolving curriculum + outcome-supervised RM for web agents (4.8% → 42.4% WebArena-Lite).
**Insight**: "Verifiable" is a *design variable, not a given*. The verifier hierarchy is now a complete design ladder, and reward engineering (densify / estimate / create signals) is where agent RLVR actually lives.

## Unified Understanding

The Reasoning map's spine is a single progression: **generate traces → verify traces → train the generator against the world's own signal**.

```
┌──────────────────────────────────────────────────────────┐
│ 3. RL ACQUISITION (Days 3–4) — the reward signal IS      │
│    the verifier: rule-based → ORM → generative RM →      │
│    search-densified (verifier hierarchy as design ladder)│
├──────────────────────────────────────────────────────────┤
│ 2. VERIFICATION (Day 2) — ORM vs PRM; verifier-guided    │
│    test-time compute allocation (Snell); label bottleneck │
├──────────────────────────────────────────────────────────┤
│ 1. GENERATION (Day 1) — CoT traces as externalized       │
│    computation; self-consistency; intrinsic self-        │
│    correction fails without grounded feedback (Huang)    │
└──────────────────────────────────────────────────────────┘
```

Five cross-cutting findings:

1. **The verifier hierarchy is a design ladder, not a menu.** Rule-based verifiers (R1, math/code) → learned discriminative RMs (WebRL's ORM) → learned generative RMs (SEEA-R1's MGRM) → search-densified sparse signals (Tree-GRPO). Each rung trades verifier fidelity and reward-hacking surface for coverage of more open-ended tasks. Day 4's thesis idea — operationalize this ladder as a design space with measurable axes (fidelity, coverage, hacking surface) — is the map's most actionable output.

2. **Generation sets the ceiling; verification/reward design determines how much of it you harvest; compute allocation decides the cost.** This three-way split (Day 1 → Day 2 → Day 2/Snell) organizes every method read: self-consistency, PRMs, RLVR, MCTS densification, and curriculum-from-failure all act on one of these three levels.

3. **Reasoning emergence is NOT automatic outside clean verifiers.** R1-Zero's "aha moment" appears when the reward is unambiguous (deterministic answer / unit test). RAGEN shows the agent-domain reality: without reasoning-aware rewards, policies collapse to shallow strategies — the same root cause as Huang 2023's intrinsic self-correction failure (no grounded signal), now manifesting at training time instead of inference time. The optimistic "RL just works" reading of Day 3 must be paired with Day 4's caveat.

4. **The test-time search axis was deferred, and that gap is now the map's clearest frontier.** Day 1 named search (ToT/MCTS) as an axis but the topic evolved through verification and RL instead; o1-style verifier-guided search, STaR bootstrapping, and MCTS-based reasoning were never read directly. The map positions them as the bridge between "grow reasoning" (RL acquisition, Days 3–4) and "search reasoning at inference time" — and the natural place where RL-trained policies and verifier-guided search compose.

5. **Free grounded feedback is the agent's unique asset.** Tool results and environment signals are correct-by-construction verification for the steps that touch the world. The open question from Day 2 (do trained verifiers disagree with grounded feedback?) matured into Day 4's concrete claim: in non-verifiable domains, learned RMs are the *only* viable reward channel — but grounding could replace them where it exists. This is the agents-specific edge of the whole map.

## Key Concepts (consolidated)

- Chain-of-thought prompting: reasoning traces as externalized computation (emergent at scale)
- Self-consistency: sample-and-marginalize as the cheapest verification signal
- Intrinsic vs. external-feedback self-correction (Huang 2023 negative result)
- Process reward model (PRM) vs outcome reward model (ORM); PRM800K "first incorrect step" labeling
- Process supervision value grows with task difficulty (GSM8K vs MATH)
- Test-time compute allocation: per-prompt difficulty-adaptive search budget (Snell 2024)
- GRPO: critic-free PPO, group-relative baseline; R1 pipeline (cold-start SFT → RL → rejection sampling → final RL)
- RL with verifiable rewards (RLVR): environment/rule as the verifier; emergent self-verification ("aha moment")
- Reward hacking / format-reward gaming; verifiability bottleneck for open-ended tasks
- Long2short distillation + length penalty (Kimi k1.5)
- Verifier hierarchy: rule-based → discriminative RM → generative RM → search-densified sparse signal
- Tree-GRPO: MCTS densification of sparse terminal rewards inside GRPO
- MGRM: multimodal generative reward model for self-evolution without ground truth
- Reasoning emergence requires reasoning-aware rewards (RAGEN negative result; Echo Trap)
- Self-evolving curriculum: task generation from failures (WebRL)
- Sparse feedback → densification / learned estimation / signal creation triad

## Open Questions (most important for the frontier)

1. **What counts as "verifiable" in open-ended agent tasks?** The R1 recipe's engine is a deterministic correctness signal; web/tool/embodied tasks lack it. The hierarchy's rungs answer partially, but a principled definition of task verifiability — and a way to *measure* the hacking surface at each level — is missing.
2. **Does RL with verifiable rewards produce generalizable reasoning or task-specific verifier gaming?** The R1-vs-RAGEN contrast makes this urgent: do policies learn to reason, or to satisfy these particular reward functions?
3. **Does emergent self-verification ("aha moment") survive outside clean rule-verifier setups?** Can it be deliberately shaped with verification-specific rewards instead of hoped for?
4. **How do trained verifiers interact with free grounded feedback (tool results, environment signals) in agent loops — where do they disagree, and can grounding replace learned RMs where it exists?**
5. **Is the test-time search axis (verifier-guided search, MCTS reasoning, STaR) complementary to RL-trained reasoning — and how do search and RL compose in one agent?** (The deferred gap from Day 1.)
6. **How do GRPO-style group baselines compose with learned verifiers in the loop (PRM-guided sampling + GRPO)?** Do they compose or conflict?

## Possible Thesis Ideas (refined)

1. **Verifiable-reward design for agent tasks** — operationalize the verifier hierarchy (rule → ORM → generative RM → MCTS-densified) as a design space with measurable axes (fidelity, coverage, reward-hacking surface), and build a selector that picks the minimal rung that makes reasoning emerge on a given task family. The single most developed direction on this map.
2. **Verification-signal selection meta-controller for agent reasoning** — the Day 1/2 idea, now grounded in the hierarchy: dynamically choose the cheapest reliable signal (self-consistency votes vs. lightweight verifier vs. free environment feedback) per step of a long-horizon task, trading accuracy against latency/cost.
3. **Reasoning-aware reward audit** — an early-warning detector for RAGEN-style shallow-strategy collapse during agent RL training (reward satisfied without reasoning), before the policy converges to non-reasoning behavior.
4. **Test-time search × RL hybrid for agents** — combine verifier-guided search (the deferred Day 1 axis) with RL-trained long-CoT policies under a compute budget; fills the map's clearest gap and directly tests open question 5.
5. **Emergent verification as a learned skill** — probe whether R1-style self-verification transfers across domains, and whether targeted verification rewards can shape it instead of waiting for emergence.
6. **Grounded verification for RLVR agents** — use tool/environment feedback as the reward channel in GRPO (free process supervision); measure when grounding suffices vs. when a learned RM must be added (open question 4).

## Next Step

**Topic completed.** 🎉

Advancing to **RL for Agents** — the user's stated highest-priority direction (agents / reasoning / RL-for-agents). The next topic question: *How do RL-style training signals improve agent behavior?*

The Reasoning map transfers almost wholesale: GRPO and the RLVR recipe (Days 3–4) are the algorithmic core of RL-for-agents; the verifier hierarchy becomes the reward-design space for agent tasks; RAGEN's Echo Trap and WebRL's curriculum are agent-RL-specific mechanisms read in the wrong topic (they were triangulation papers here, they are main papers there). The first RL-for-agents question to ask: how does trajectory-level agent RL (StarPO-style) differ from token-level reasoning RL (GRPO-style) in reward design, stability, and credit assignment?

---

*This is a synthesis note (capstone). No new papers were read; the confidence update reflects consolidation of the 12 papers read over Days 1–4.*
