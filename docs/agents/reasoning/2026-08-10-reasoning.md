# 2026-08-10 — Reasoning

Course: Agents
Topic: Reasoning
Stage: Day 1 — Survey / Landscape
Confidence: 0.00 -> 0.35

## Today's Question

How do agents improve reasoning through search, reflection, verification, or self-consistency — and what is the canonical foundation these four axes build on?

## Main Paper

### Metadata

- Title: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
- Authors: Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc Le, Denny Zhou
- Year: 2022
- Venue: NeurIPS 2022 (arXiv 2201.11903)
- Link: https://arxiv.org/abs/2201.11903

### Why this paper?

This is the correct Day 1 paper for the Reasoning topic. Every later reasoning technique — self-consistency, ToT, reflection, verifiers, test-time compute scaling — is either an extension of or a reaction to chain-of-thought prompting. It is the canonical anchor of the entire reasoning map, and it has not yet been read directly in this course (it was only referenced in the architectures topic). Reading it first gives the topic a fixed origin point.

### Core Problem

Large language models (scaled up to 540B parameters) still fail on multi-step reasoning tasks: arithmetic word problems, commonsense reasoning, symbolic manipulation. The standard few-shot prompting paradigm — input → output — forces the model to produce the final answer in one shot, with no intermediate computation. Scaling model size alone improves fluency but shows flat or saturated accuracy on hard multi-step problems like GSM8K.

### Main Idea

Chain-of-thought prompting is a simple, training-free method: instead of providing (input → output) exemplars, provide (input → chain of thought → output) exemplars, where the chain of thought is a series of intermediate reasoning steps written in natural language. The model is then prompted to generate its own reasoning trace before the final answer.

Key properties that make it work:

1. **It decomposes multi-step problems** — each intermediate step reduces the difficulty of the remaining computation, analogous to how humans solve problems step by step.
2. **It provides a controllable window for computation** — the model gets to "think" in text before committing to an answer.
3. **It is an emergent ability** — the method only yields large gains at sufficient scale (e.g., 540B PaLM), appearing at roughly 100B parameters and growing with scale. Small models do not benefit.

### Technical Details

- **Setup**: 8 CoT exemplars on GSM8K; standard few-shot with greedy decoding.
- **Results**: PaLM 540B with CoT prompting achieves state of the art on GSM8K (58% vs. 33% for standard prompting, 55% for fine-tuned GPT-3 with verifier), beating the prior SOTA without any fine-tuning or task-specific components.
- **Coverage**: gains across arithmetic (GSM8K, SVAMP, MAWPS), commonsense (CommonsenseQA, StrategyQA), and symbolic reasoning (last-letter concatenation, coin-flip tracking).
- **Robustness**: CoT prompting is sensitive to exemplar choice (there is variance across different exemplar sets), a known limitation.
- **Emergence curve**: the benefit scales with model size; it is not present in smaller models.

### Research takeaway

The paper establishes the central paradigm of LLM reasoning: **generate intermediate reasoning in natural language before the answer**. The insight is that reasoning traces act as a scratchpad that externalizes computation — a theme that directly connects to the agent architectures topic (ReAct's Thought-Action loop is CoT applied to action selection).

### Modern perspective

Read in 2026, CoT is the "Newtonian mechanics" of reasoning research: superseded in raw power by RL-trained long-CoT models (o1-style), but still the conceptual foundation everything builds on. The open research frontier it spawned — how to *verify* the generated reasoning trace (not just generate it) — is precisely where the field moved: self-consistency, verifiers, process reward models, and test-time compute scaling.

## Related Papers

### Paper 1: Self-Consistency Improves Chain of Thought Reasoning in Language Models

- **Authors:** Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou (2022)
- **Link:** https://arxiv.org/abs/2203.11171

**Contributions:**
- Replaces greedy decoding in CoT with a **sample-and-marginalize** decoding strategy: sample multiple diverse reasoning paths, then pick the most consistent answer by majority vote over the final answers.
- Intuition: a complex reasoning problem admits multiple correct ways of thinking that should converge on the same answer; consistent answers are more likely correct than any single sampled path.
- Striking gains on top of CoT: GSM8K +17.9% (to ~78%), SVAMP +11.0%, AQuA +12.2%, StrategyQA +6.4%, ARC-challenge +3.9%.

**Relation to main paper:** Direct follow-up; it answers CoT's biggest weakness — the variance and unreliability of a single sampled reasoning path — by aggregating many paths. It is the **self-consistency** axis named in the topic question.

**Why it matters:** Self-consistency is the cheapest "verification" signal that exists (no trained verifier, no environment feedback), and it presages the modern test-time-compute trade: spend more inference tokens to gain accuracy. Its core assumption — answer agreement implies correctness — later becomes a research question itself.

**Deep-read later?** Yes, moderately — the sampling/marginalization idea reappears in PRM-based approaches and best-of-N selection.

### Paper 2: Large Language Models Cannot Self-Correct Reasoning Yet

- **Authors:** Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou (2023)
- **Link:** https://arxiv.org/abs/2310.01798

**Contributions:**
- Critically examines **intrinsic self-correction** (an LLM correcting its own answer with no external feedback) and finds it largely fails: without external feedback, LLMs struggle to self-correct, and performance sometimes *degrades* after self-correction.
- Distinguishes intrinsic self-correction from self-correction with external feedback (e.g., verifiers, environment signals, tool results) — the latter is where the real gains are.
- On reasoning benchmarks, prompting the model to "re-examine and correct" its answer does not reliably fix errors and can flip correct answers to wrong ones.

**Relation to main paper:** This is the critical counterweight to the CoT paradigm's optimism. CoT gives the model more tokens to think; self-correction asks it to think *again* — and this paper shows that without a *ground-truth signal*, more thinking does not equal better answers. It motivates the **verification** axis of the topic question: reasoning improvement must come with an external check, not just internal reflection.

**Why it matters:** It frames the field's biggest architectural debate — is the bottleneck *generation* (producing good traces) or *verification* (knowing which trace is right)? Reflexion's verbal reinforcement (read in architectures) works *because* it uses environment/test feedback, which is exactly the external signal this paper says is necessary.

**Deep-read later?** Yes — the intrinsic-vs-external feedback distinction is a core conceptual lens for the rest of this topic.

## Current Understanding

The Reasoning topic sits on a canonical foundation: **chain-of-thought prompting** (Wei 2022). The topic question names four improvement axes, and today's reading gives each an anchor:

1. **Generation**: CoT — decompose the problem into explicit intermediate steps. The base mechanism everything else augments.
2. **Self-consistency**: sample multiple CoT paths, majority-vote answers (Wang 2022). Cheap statistical verification; the first "test-time compute" trade-off.
3. **Reflection / self-correction**: without external feedback, self-correction is unreliable and can hurt (Huang 2023). Reflection works only when grounded in a signal (test result, verifier, tool feedback) — this connects directly to Reflexion and the agent architecture work already covered.
4. **Search & verification**: ToT (tree search over thoughts, read in architectures), and trained verifiers / PRMs — the axes not yet read in depth in this topic.

The map's central tension: **generation vs. verification**. CoT showed models can generate good traces; the field's subsequent progress (self-consistency → verifiers → RL-trained long-CoT) is largely about getting a trustworthy signal on which trace is correct.

## Key Concepts

- Chain-of-thought prompting (CoT): intermediate reasoning steps as exemplars and generated traces
- Emergent ability: CoT benefits appear only at scale (~100B+)
- Scratchpad / externalized computation: reasoning trace as working memory
- Self-consistency decoding: sample diverse paths + marginalize answers
- Intrinsic vs. external-feedback self-correction
- Test-time compute trade-off (more tokens → more accuracy)
- Generation vs. verification framing of reasoning research

## Open Questions

1. **Why does CoT emerge only at scale?** What mechanistic change at ~100B parameters enables intermediate reasoning to help?
2. **Self-consistency's assumption**: when does answer-agreement stop implying correctness (e.g., all sampled paths share the same systematic error)?
3. **Is self-correction ever useful intrinsically?** Huang 2023 shows degradation on average — but are there task families where intrinsic reflection reliably helps?
4. **Where should the verification signal come from?** Learned verifiers (PRMs), environment feedback, tool results, or self-consistency statistics — what is the right cost/quality mix for an agent?
5. **How does CoT interact with agent loops?** ReAct applies CoT to action selection; does a reasoning trace in an agent context serve as plan, working memory, or both?

## Possible Thesis Ideas

- **Verification-signal selection for agent reasoning** — a meta-controller that dynamically chooses the cheapest reliable verification signal (self-consistency votes vs. a lightweight verifier vs. environment feedback) for each step of a long-horizon agent task, trading accuracy against inference cost. Directly extends today's generation-vs-verification tension into the agent setting.
- **Self-consistency with calibrated disagreement** — instead of majority voting, use the *disagreement structure* among sampled reasoning paths (clusters, confidence, divergence points) as a signal for when to stop and ask for help or trigger re-planning.
- **When reflection helps: a task taxonomy** — characterize which task types benefit from intrinsic reflection despite Huang 2023's negative average result; a classifier that predicts whether self-correction will help before applying it.

## Next Step

Day 2 of Reasoning: read the search axis — Tree-of-Thoughts was covered at the architecture level (2026-06-08); go deeper on search-based reasoning and/or test-time compute scaling (o1-style long-CoT, e.g., "Let's Think Step by Step" RL scaling work or a long-CoT survey). Alternatively, read the verification axis (trained verifiers / process reward models). Candidate: the "Towards Reasoning Era: A Survey of Long Chain-of-Thought" survey as map context.

Confidence: 0.00 -> 0.35 (understand the canonical foundation and the four-axis map, but have not yet read any axis in depth — search and verification remain unexplored)
