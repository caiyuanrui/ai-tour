# 2026-08-14 — Reasoning

Course: Agents
Topic: Reasoning
Stage: Day 2 — Verification axis (process reward models)
Confidence: 0.35 -> 0.55

## Today's Question

Day 1 mapped the generation-vs-verification tension: CoT showed models can *generate* good traces, but how do we get a trustworthy signal on *which* trace is correct? Today's question: **where should the verification signal come from — outcome or process supervision — and what does a trained verifier actually buy us?**

## Main Paper

### Metadata

- Title: Let's Verify Step by Step
- Authors: Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Bowen Baker, Teddy Lee, Jan Leike, John Schulman et al. (OpenAI)
- Year: 2023 (ICLR 2024)
- Venue: arXiv 2305.20050
- Link: https://arxiv.org/abs/2305.20050

### Why this paper?

Day 1's open question #4 asked exactly this: "Where should the verification signal come from? Learned verifiers (PRMs), environment feedback, tool results, or self-consistency statistics?" The Day 1 "Next Step" also flagged the verification axis as unexplored. This paper is the canonical anchor of that axis — the paper that established process reward models (PRMs) as a serious alternative to outcome supervision and released the PRM800K dataset that the whole verifier literature builds on.

### Core Problem

State-of-the-art LLMs still make logical mistakes on multi-step reasoning. To train more reliable models you must choose a supervision signal: **outcome supervision** (feedback only on the final result) or **process supervision** (feedback on each intermediate step). Outcome supervision is cheap to collect but ignores *where* the reasoning went wrong; process supervision is more informative but human labeling of every step is expensive. Which one actually produces better models?

### Main Idea

Train a **process reward model (PRM)** that assigns a score to each step of a solution, and use it to select the best-of-N sampled solutions at test time. The key data contribution is **PRM800K**: 800,000 step-level human feedback labels collected by asking labelers to mark the *first incorrect step* in model-generated solutions (a deliberately lightweight annotation interface that scales).

The comparison is against an **outcome reward model (ORM)** trained on final-answer correctness only. Both models are judged by how much they improve a fixed base generator under best-of-N selection on MATH.

### Technical Details

- **Dataset**: PRM800K — 800K human step-level labels on MATH-style solutions. Labelers mark the first incorrect step; everything after it is implicitly wrong, everything before is implicitly right. This makes annotation cheap and consistent.
- **Model**: PRM trained to predict per-step correctness from these labels; a softmax over "the first error was here" gives a per-step probability, and the whole-solution score is the product (or log-sum) of step scores.
- **Result 1**: process supervision *significantly* outperforms outcome supervision on MATH — the process-supervised model solves **78%** of a representative 500-problem subset, a large margin over the ORM baseline.
- **Result 2**: active learning meaningfully improves process-supervision efficiency — labeling the most informative solutions first reduces the label budget needed for a given accuracy.
- **Notable nuance**: process supervision wins even when compared fairly against outcome supervision, and the PRM's advantage grows with the number of samples (best-of-N) considered.

### Research takeaway

Verification is a *learnable, step-granular* signal. "Which step went wrong" is a more informative and more generalizable training target than "was the final answer right." This is the moment the field's verification axis crystallized: outcome reward → process reward, and the object of study became the reward model rather than the generator.

### Modern perspective

Read in 2026, PRMs are everywhere: verifier-guided test-time search (Snell 2024, read today), RL training of reasoning models (o1-style long-CoT uses process-like reward shaping; GRPO/RLVR pipelines reward intermediate correctness), and automated PRM construction (Math-Shepherd, rStar-Math, RL-distilled PRMs) all descend from this paper's framing. The one thing that did *not* survive unchanged is the human-label bottleneck — PRM800K's 800K labels were the ceiling of that approach, and the field's next move (after today's reading) is: can you build PRMs without human step labels?

## Related Papers

### Paper 1: Solving Math Word Problems with Process- and Outcome-Based Feedback

- **Authors:** Jonathan Uesato, Nate Kushman, Ramana Kumar, Francis Song, Noah Siegel, Lisa Wang, Antonia Creswell, Geoffrey Irving et al. (DeepMind, 2022)
- **Link:** https://arxiv.org/abs/2211.14275

**Contributions:**
- The first comprehensive comparison of process-based vs outcome-based supervision on a natural-language reasoning task (GSM8K).
- Surprising finding: pure outcome-based supervision achieves **similar final-answer error rates with far less label effort** — on GSM8K you don't need step labels to fix wrong answers.
- BUT: for *reasoning* errors (correct answer, wrong steps), process-based supervision — or a learned reward model emulating process feedback — is necessary. Improves prior best from 16.8% → 12.7% final-answer error and 14.0% → 3.4% reasoning error.

**Relation to main paper:** Direct predecessor and competing view. Lightman et al. extends this exact comparison to the harder MATH dataset — and the conclusion *flips*: on MATH, process supervision clearly dominates. Together the two papers say something important: the value of process supervision grows with task difficulty and with the strictness of the error metric (final-answer vs reasoning correctness).

**Why it matters:** It frames the supervision trade-off as a *task-dependent* decision, not a universal law — exactly the kind of nuance an agent's verification-signal selector (thesis idea #1) needs.

**Deep-read later?** Yes, moderately — the "outcome works on easy tasks, process needed on hard tasks" gradient is a testable hypothesis for agent domains.

### Paper 2: Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters

- **Authors:** Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar (UC Berkeley, 2024)
- **Link:** https://arxiv.org/abs/2408.03314

**Contributions:**
- Analyzes two mechanisms for scaling test-time computation: (1) **search against a dense process-based verifier** (best-of-N, beam search guided by a PRM), and (2) **adaptive distribution updating** (sequential revision of the answer given the prompt).
- Key finding: the effectiveness of each method *depends critically on prompt difficulty* — hard prompts need more search, easy prompts are best answered directly.
- A **compute-optimal scaling strategy** that allocates test-time compute per prompt (based on a difficulty estimate) improves efficiency **4x+ over a best-of-N baseline**.
- In a FLOPs-matched comparison, test-time compute lets a smaller base model **outperform a 14x larger model** on problems where it already attains non-trivial accuracy.

**Relation to main paper:** The follow-up that moves the PRM from *training-time* supervision to *test-time* compute allocation. Lightman 2023 shows a PRM is a better selector of sampled solutions; Snell 2024 shows *how much* search to spend with that selector, per prompt. It is the bridge from verification to the modern test-time-compute scaling paradigm (o1-style).

**Why it matters:** It reframes verification from a training-data question into an *inference-cost* question — "which verification signal, spent on which steps, for how many tokens" — which is precisely the design space of an agent that must trade accuracy against latency and cost on long-horizon tasks.

**Deep-read later?** Yes — this is the on-ramp to the test-time-compute / long-CoT axis, the natural Day 3 reading.

## Current Understanding

The Reasoning map now has its second pillar. Day 1: **generation** (CoT) and the cheap statistical verification of self-consistency. Day 2: **trained verification** — the axis splits into two supervision paradigms:

1. **Outcome supervision (ORM)** — cheap labels, fixes wrong final answers; competitive on easy tasks (GSM8K, Uesato 2022).
2. **Process supervision (PRM)** — step-level labels, fixes *reasoning* errors; wins clearly on hard tasks (MATH 78%, Lightman 2023) and enables verifier-guided search.
3. **Test-time dimension (Snell 2024)** — the verifier is not only a training signal but a *compute allocator*: search-with-PRM beats plain best-of-N when the compute budget is allocated per-prompt difficulty.

The generation-vs-verification tension resolves into a richer picture: generation quality sets the ceiling, verification quality determines how much of that ceiling you harvest, and *how you spend compute* decides the cost. For agents specifically, environment/tool feedback is a *free, grounded* verification signal that neither ORMs nor PRMs need to imitate — a key open question is how trained verifiers interact with (and can be replaced by) grounded signals in agent loops.

## Key Concepts

- Process reward model (PRM): per-step correctness scorer for multi-step reasoning
- Outcome reward model (ORM): final-answer-only correctness scorer
- Process supervision vs outcome supervision: which step went wrong vs was the answer right
- PRM800K: 800K step-level human labels; "first incorrect step" annotation interface
- Best-of-N selection with a trained verifier
- Active learning for reward-model label efficiency
- Process supervision value grows with task difficulty (GSM8K vs MATH)
- Reasoning errors vs final-answer errors (decoupled failure modes)
- Test-time compute allocation: per-prompt difficulty-adaptive search budget
- Verifier-guided search vs adaptive distribution updating (sequential revision)
- Compute-optimal scaling: 4x efficiency vs best-of-N; small model + test-time compute > 14x larger model

## Open Questions

1. Can PRMs be built **without human step labels**? PRM800K's 800K labels were expensive; automated/RL-derived process signals (and grounding on tool results) are the obvious next question — is the human-label ceiling the reason the field moved to GRPO-style outcome + implicit-process RL?
2. **Do PRMs transfer across domains?** Trained on MATH, do they score agent trajectories, code, or web tasks sensibly — or is process verification inherently domain-bound?
3. **How do trained verifiers interact with grounded feedback in agent loops?** For an agent, tool results and environment signals are free, correct-by-construction verification for the steps that touch the world. Where do PRMs still add value over grounding, and where do they disagree?
4. **Process reward hacking** — a generator can learn to produce steps a PRM scores highly but that are subtly wrong. How do you detect and defend against verifier gaming as generators get stronger?
5. **What is the right granularity of process feedback** — per token, per parseable step, per tool call? Snell's dense-PRM results and PRM800K's step interface give different answers.

## Possible Thesis Ideas

- **Verification-signal selection for agent reasoning** (extended from Day 1) — a meta-controller choosing between self-consistency votes, a lightweight PRM, and free environment/tool feedback per step, now grounded in today's finding that the *value* of each signal is task-difficulty- and step-type-dependent (Uesato's GSM8K-vs-MATH gradient + Snell's compute-optimal allocation).
- **Compute-optimal reasoning budget for agents** — apply Snell-style per-prompt difficulty estimation to agent trajectories: spend search/verification compute on the hard steps, answer directly on the easy ones, with a hard latency/cost constraint (connects to the token-budget work in ai-blogs).
- **Grounding as free process supervision** — study whether tool-result feedback can *replace* PRM step labels in agent training (RLVR-style): which steps of an agent trajectory have grounded verification available, and can the model learn to rely on it rather than a learned reward?
- **PRM distillation from grounded execution** — train a process verifier for agent actions using execution outcomes as pseudo-labels, sidestepping the human-label bottleneck that PRM800K exposed.

## Next Step

Day 3 of Reasoning: read the test-time-compute / long-CoT axis that Snell 2024 opens (o1-style RL-trained long reasoning, e.g. the "Towards Reasoning Era: A Survey of Long Chain-of-Thought" or the scaling-law-style analyses of inference-time compute). Alternatively go deeper on PRM construction without human labels (Math-Shepherd / rStar-Math style automated process supervision), which directly answers open question #1.

Confidence: 0.35 -> 0.55 (understand the verification axis — PRMs vs ORMs, process supervision, and verifier-guided test-time compute; still have not read search-based reasoning in depth, RL-trained long-CoT, or automated PRM construction)
