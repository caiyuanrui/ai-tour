# 2026-08-16 — Weekly Synthesis

## This Week's Readings

- agents / reasoning: Chain-of-Thought Prompting Elicits Reasoning (Wei 2022) + Self-Consistency + LLMs Cannot Self-Correct Yet — Day 1
- multimodal / video-understanding: LLaVA-Video: An Image is Worth 1,024 Tokens + Qwen2.5-VL + LongVideoBench — Day 2
- llm-systems / kv-cache: KV Cache Topic Capstone (Day 5) — conf 0.80, advance to batching-scheduling
- generative-models / samplers: DPM-Solver++: Guided Sampling + GENIE + Analytic-DPM — Day 2
- agents / reasoning: Let's Verify Step by Step (Lightman 2023, PRMs) + Uesato 2022 + Snell 2024 test-time compute — Day 2
- ai-blogs / openai: Third-party cyber evaluations + Daybreak GPT-5.6-Cyber + trusted-hands program — Day 2

## Major Themes

- Verification signals became the week's spine. Agents/Reasoning read the verification axis end-to-end (self-consistency → outcome vs process supervision → verifier-guided test-time compute), and the same 'which signal tells us the intermediate steps are right' question appeared everywhere else: samplers asked which parameterization (x₀ vs ε) makes the guided ODE stable; video asked which frame budget preserves temporal correctness; OpenAI's cyber evals asked which containment boundary keeps a lowered-safeguard agent in scope. Generation quality sets the ceiling; verification quality determines how much of it is harvested.
- Resource/budget allocation is the meta-pattern, now visible in every course: video (tokens-per-frame × frames-per-video under a context budget), KV cache (the four pillars — quantize/evict/offload/architectural — compose under a memory budget, and no system yet does all four with a learned policy), samplers (NFE-per-trajectory allocation under a quality budget), reasoning (Snell: compute-optimal per-prompt search budget, 4x over best-of-N, small model + test-time compute beats a 14x larger one), OpenAI (300 vs 600 turn reasoning budgets on ExploitBench). 'How to spend a fixed budget' is the shared design question across all five courses.
- Measurement is a first-order variable, not a detail. LongVideoBench showed video LMM performance scales with frame count — the harness decides the score; ARC-AGI-3's harness settings (retained reasoning, compaction) tripled scores; this week OpenAI's cyber-eval incidents showed harness settings (internet access, disabled classifiers) are a safety boundary that can leak. Eval configuration inflates or leaks — a two-sided confound, completing last week's 'harness as hidden variable' into a general audit problem.
- Generation and verification are decoupled competencies. CoT showed models can generate good traces; PRMs/verifiers decide which trace is right; in samplers the generator (network output) and the integrator (solver + thresholding) are similarly separable — x₀ prediction changes the integrand's properties, thresholding keeps the trajectory in-distribution. In both fields the bottleneck has moved from producing candidates to judging them.
- The supervision-quality gradient is task-dependent. Uesato: on GSM8K, outcome supervision suffices; Lightman: on MATH, process supervision clearly wins (78% vs ORM). The value of fine-grained process signal grows with task difficulty — the same gradient that explains why GRPO/RLVR (outcome + implicit process) replaced human-labeled PRMs, and why grounded tool feedback is a free process signal for agents.
- Data scarcity attacks two flanks: PRM800K's 800K human step labels (label scarcity) vs LLaVA-Video-178K synthetic video instructions (raw-data scarcity). Both weeks' answers converge on automation — synthetic pipelines and RL-derived pseudo-labels — and both leave the 'does synthetic data amplify hallucination' question open.

## Cross-Course Connections

- Test-time compute triangulates across three courses: reasoning (Snell: difficulty-adaptive search budget, compute-optimal scaling), samplers (NFE/FID Pareto, per-trajectory budget), video (frame-count scaling on LongVideoBench). Three fields independently conclude the optimal compute allocation is per-instance, not uniform — a unified 'difficulty-aware compute allocation' thesis direction has evidence from all three.
- Parameterization determines integrand stability (DPM-Solver++ x₀ vs ε) ↔ process supervision determines which steps get credit (Lightman PRM vs ORM): both say the object being evaluated/generated must match how it will be used. Sampling stability and reasoning verification share the 'choose the right representation of intermediate state' principle.
- Eval environments as two-sided confounds: OpenAI cyber incidents (lowered safeguards → boundary drift/misconfiguration → real internet contact) parallel LongVideoBench (frame count determines score) and ARC-AGI-3 (harness triples score). The agent eval harness is simultaneously a performance lever and an attack surface — an audit methodology spans all three.
- Grounded feedback as free supervision: for agents, tool results are correct-by-construction verification (Reasoning open question #3) — the same logic as thresholding keeping x₀ in-distribution (samplers) and containment keeping cyber agents in-scope (OpenAI). External grounding beats internal reflection in every domain read this week (self-correction fails without external signal).
- Synthetic data and automated labels connect reasoning and video: PRM800K's label bottleneck motivates RL-derived process signals; LLaVA-Video-178K shows synthetic instruction data substitutes for scarce raw video-text. Both topics converge on 'automate the data' as the answer to their respective scarcity.
- Composition safety continues to generalize: memory poisoning (Week 10) → cyber eval containment (Week 11): individually-innocent harness settings (internet on, classifiers off) compose into boundary-breaking behavior. Same composition-property lesson as ChainCaps tool chains — safety is a property of the composed system, and this week it applies to measurement infrastructure itself.

## Contradictions and Tensions

- Self-consistency works; intrinsic self-correction fails. Both are 'think again' mechanisms: majority voting over sampled paths reliably improves accuracy, but prompting a model to re-examine its own answer degrades it (Huang 2023). The difference is aggregation + a decision rule vs. trusting the same generator's second opinion — more thinking only helps with an external or statistical anchor.
- Outcome vs process supervision flips with difficulty: Uesato (GSM8K: outcome ≈ process, far cheaper) vs Lightman (MATH: process wins big). Neither is universally right — the optimal signal is task- and metric-dependent (reasoning errors vs final-answer errors), which is exactly what a verification-signal selector must model.
- More frames → better video performance vs. fewer steps → better sampler performance: video wants to spend more tokens (until saturation), samplers want to spend fewer NFE (until quality loss). Both are budget-allocation claims; the apparent contradiction dissolves once the bottleneck resource is identified (context for video, time for sampling).
- Training-free vs distilled speed: DPM-Solver++ reaches 15-20 steps with zero training; LCM/SDXL-Turbo reach 1-4 steps with distillation. The 'no-free-lunch' between solver accuracy and learned few-step maps remains — and Analytic-DPM adds stochasticity as an orthogonal dial.
- Capability measurement requires lowering safeguards; safety requires raising them. OpenAI's cyber evals measured capability by disabling classifiers and enabling internet — and containment failed twice. Daybreak answers with access-layer safety (identity, hardware keys, monitoring) instead of model-level guardrails, but 'completion rate 95% ≠ safe' — refusal tuning improves task completion without establishing alignment.
- PRM800K's 800K human labels were the ceiling of that approach; the field moved to GRPO-style implicit process rewards. Yet process supervision's demonstrated superiority (MATH 78%) is precisely what GRPO approximates — the human-label bottleneck may have been the real reason the field switched reward paradigms, not a discovered inferiority of process signals.

## Open Problems

- Can PRMs be built without human step labels — via RLVR outcome signals, tool-result grounding, or execution-derived pseudo-labels? PRM800K's 800K labels were expensive and the field's shift to GRPO suggests it, but no clean study isolates what process information RL-derived rewards actually capture.
- Where do trained verifiers disagree with free grounded feedback in agent loops? For steps that touch the world, tool results are correct-by-construction; PRMs add value on steps that don't. The cost/quality frontier of verification-signal mixtures is unmapped.
- Is the attention sink / guidance instability a necessary consequence of the architecture (Softmax attention; ε-parameterized integrand), or designable away? Both KV cache (sinks) and samplers (guidance instability) have a heuristic workaround (sink preservation; thresholding) with no theory.
- Does the 'more frames → better' finding hold past saturation, or is there a token wall (O(T) context explosion)? Video token budgets, KV cache, and context management are the same wall at three scales.
- How do reasoning-budget policies (300 vs 600 turns on ExploitBench) interact with capability measurement — does token budget change the rank order of models on agentic cyber evals? Connects the token-budget thesis line to security evaluation.
- Can thresholding (samplers) and compaction (context management) be replaced by learned, provably distribution-preserving operators? Both are the largest heuristic in their respective stacks.

## Possible Thesis Ideas

### Verification-Signal Selection for Agent Reasoning (extended, now week-anchored)

- **Problem:** An agent has multiple verification signals — self-consistency votes (cheap, statistical), a lightweight PRM (learned, step-level), free tool/environment feedback (grounded, correct-by-construction), outcome checks — and their value is task- and step-type-dependent (Uesato's GSM8K-vs-MATH gradient, Snell's difficulty-adaptive budgets, LongVideoBench's frame-count finding). No system dynamically chooses which signal to spend on which step under a latency/cost constraint.
- **Why it matters:** This week's readings show the verification axis is where reasoning progress now lives (PRMs, test-time compute, compute-optimal scaling 4x, small-model-beats-14x). A selector that mixes cheap statistical, learned, and grounded signals is the agentic generalization of that axis — and directly serves the user's agents priority.
- **Method:** Meta-controller over (step type, difficulty estimate, budget) → verification signal choice; train on agent trajectories with labeled step correctness; evaluate on MATH-style, tool-use, and web-agent tasks under fixed token/latency budgets.
- **Background:** CoT (Wei 2022), self-consistency (Wang 2022), PRM/PRM800K (Lightman 2023), Uesato 2022, Snell 2024 test-time compute, grounded-feedback idea from reasoning Day 2.
- **Evaluation:** Best-of-N vs PRM-guided vs selector-guided accuracy per token spent; step-level accuracy of selected signals; degradation under budget pressure; comparison against fixed-signal baselines.
- **Risk:** Medium — signal value is hard to measure per step, but partial results (difficulty-dependent selection beats uniform) are publishable.
- **Next step:** Design the step taxonomy (grounded vs ungrounded, hard vs easy); baseline the three pure signals on an agent benchmark with a token budget.
- **Confidence:** 4/5

### Difficulty-Aware Compute Allocation Across Domains: A Unified Budget Controller

- **Problem:** Three fields independently found that optimal compute allocation is per-instance: reasoning (Snell: per-prompt search budget, 4x over best-of-N), video (frame count scales performance, allocation is tokens-per-frame × frames-per-video), sampling (per-trajectory NFE allocation). No framework treats these as one problem — how to spend a fixed compute budget across heterogeneous steps (reasoning steps, video frames, denoising steps) of a multimodal agent.
- **Why it matters:** The user's token-budget research line (P3) and this week's readings converge: budgets are everywhere, difficulty is the key variable, and a unified controller is the natural thesis.
- **Method:** Learn a difficulty estimator (per reasoning step / per video segment / per diffusion trajectory) and a budget allocator; connect Snell-style search budgets, LLaVA-Video-style token budgets, and sampler NFE budgets under one latent 'difficulty' axis.
- **Background:** Snell 2024, LongVideoBench frame-count finding, DPM-Solver++ NFE analysis, KV cache budget literature, P3 token-budget work.
- **Evaluation:** End-to-end multimodal agent tasks (perception + reasoning + generation) with a fixed total budget; compare uniform vs difficulty-aware allocation; report accuracy-per-token curves.
- **Risk:** High-medium — cross-domain unification is ambitious; start with two domains (reasoning + video) and show the transfer.
- **Next step:** Replicate Snell's difficulty-adaptive allocation on a video-reasoning task with a frame budget; check whether the same difficulty estimator transfers.
- **Confidence:** 3/5

### Grounded PRM Distillation: Process Verifiers from Execution Outcomes

- **Problem:** PRMs demonstrably beat ORMs on hard tasks (MATH 78%) but require expensive human step labels (PRM800K, 800K). For agents, execution outcomes (tool results, tests, environment feedback) are free, correct-by-construction process signals for exactly the steps that touch the world.
- **Why it matters:** Directly answers reasoning Day 2's top open question (PRMs without human labels) and gives agents a cheap, grounded verifier for trajectory selection and RL training — the natural successor to both PRM800K and GRPO.
- **Method:** Generate agent trajectories with tool-call steps; label step correctness by execution outcome (passed/failed, observed effect vs expectation); distill a step-level PRM; measure how much of the Lightman gap it recovers vs human-labeled PRMs.
- **Background:** Lightman 2023 (PRM800K), Uesato 2022, GRPO/RLVR, tool-use topic (execution verification), reasoning open question #1/#3.
- **Evaluation:** PRM accuracy vs human-labeled PRM on held-out agent tasks; best-of-N gain over ORM; label-cost comparison (zero human labels); transfer from MATH-like to tool-use domains.
- **Risk:** Medium — execution outcomes only cover grounded steps; the interesting question is how the distilled PRM behaves on ungrounded steps (extrapolation).
- **Next step:** Prototype on a tool-use benchmark (e.g., web agents with deterministic tool results); measure step-level label quality from outcomes.
- **Confidence:** 4/5

### Eval Environment as a Two-Sided Confound: An Audit Methodology for Agent Benchmarks

- **Problem:** Harness settings are a first-order variable in both directions: ARC-AGI-3 tripled from harness changes; LongVideoBench scores scale with frame count; OpenAI cyber evals leaked past containment when safeguards were lowered. No methodology audits agent-benchmark environments for inflation (performance) and leakage (safety) simultaneously.
- **Why it matters:** Benchmark comparisons drive model/agent design; the audit framework extends last week's 'harness as confound' thesis into a tooling/methodology contribution motivated by real incidents (UK AISI, Irregular).
- **Method:** Systematically vary eval-environment dimensions (internet access, safeguard levels, credential scoping, containment, frame/token budgets) across public agent benchmarks; produce a per-benchmark confound map and a containment-audit checklist.
- **Background:** OpenAI cyber eval incidents (2026-08), ARC-AGI-3 harness study, LongVideoBench, agent evaluation topic (upcoming in agents course).
- **Evaluation:** Variance decomposition of benchmark scores across environment dimensions; leakage-incident reproduction rate; published confound maps for 3-5 benchmarks.
- **Risk:** Low-medium — compute-heavy but methodologically straightforward; the incident motivation makes it timely.
- **Next step:** Pick 3 agent benchmarks; enumerate the environment dimension grid (from the OpenAI incident categories); run the first inflation-vs-leakage ablation.
- **Confidence:** 4/5

### Guidance-Stable Samplers and Learnable Thresholding

- **Problem:** High-order solvers are unstable under large classifier-free guidance; DPM-Solver++ patches this with x₀ prediction + a heuristic clamp (thresholding). Why x₀ is more stable has no theory; thresholding is the largest heuristic in the stack; Analytic-DPM's optimal variance is an unused principled stochasticity dial.
- **Why it matters:** Sampling is the runtime of every text-to-image system; a theory-grounded, guidance-independent stable solver removes the remaining heuristics and connects to the stochasticity dimension.
- **Method:** Analyze the guided ODE's integrand properties (Lipschitz/conditioning) under ε vs x₀ vs v parameterization; design a provably guidance-stable high-order integrator; replace clamp with a learned distribution-preserving projection; test ODE + optimal-variance injection.
- **Background:** DPM-Solver/DPM-Solver++ (Lu 2022), GENIE (learned higher-order terms), Analytic-DPM (Bao 2022), EDM design space.
- **Evaluation:** FID-per-NFE at CFG 7-8 vs DPM-Solver++/DDIM; stability metrics (trajectory divergence) vs guidance scale; likelihood-quality trade-off with optimal variance.
- **Risk:** Medium — theory is hard, but empirical stability curves at increasing CFG are publishable progress.
- **Next step:** Measure integrand Lipschitz constants across parameterizations on a small latent diffusion model; identify the exact instability mechanism (multistep error accumulation vs Lipschitz blow-up).
- **Confidence:** 3/5


## What To Read Next

- Agents / Reasoning Day 3 (Mon): test-time compute / long-CoT axis that Snell 2024 opens — 'Towards Reasoning Era: A Survey of Long Chain-of-Thought' or scaling-law analyses of inference-time compute
- Multimodal / Video Understanding Day 3 (Tue): the long-video token wall — ReTaKe (arXiv:2412.20504) or VideoStreaming/Flash-VStream memory-based streaming
- LLM Systems / Batching and Scheduling Day 1 (Wed): new topic — how serving systems decide when to run each request and how many tokens to process per step
- Generative Models / Samplers Day 3 (Thu): step/noise schedule optimization (Align Your Steps) or the training-free vs distillation below-15-step zone
- Agents / Reasoning Day 4 (Fri): automated PRM construction (Math-Shepherd / rStar-Math) answering open question #1, or search-based reasoning (ToT/MCTS) depth
- AI Blogs / OpenAI Day 3 (Sat): GPT-5.6 model-architecture posts + broader alignment research (GPT-Red self-improvement) to complete the map beyond systems and cyber

## Next Week Adjustments

- Monday (agents/reasoning): Day 3 — test-time compute / long-CoT axis; candidate: long-CoT survey for map context, then Snell-style scaling analyses
- Tuesday (multimodal/video-understanding): Day 3 — long-video token wall; candidate: ReTaKe or VideoStreaming line (O(T) token explosion)
- Wednesday (llm-systems/batching-scheduling): Day 1 — start the new topic: request/token scheduling (Orca continuous batching was read in inference-serving; go deeper on scheduling policies)
- Thursday (generative-models/samplers): Day 3 — step/noise schedule optimization (Align Your Steps) or the few-step training-free frontier
- Friday (agents/reasoning): Day 4 — automated PRM construction (Math-Shepherd / rStar-Math) or search-based reasoning depth
- Saturday (ai-blogs/openai): Day 3 — GPT-5.6 architecture + alignment research posts
- Index hygiene: all topic indexes verified complete this week (reasoning, video-understanding, kv-cache capstone row, samplers, openai all present and matching state history); continue the cross-check pattern
- Synthesis focus for Week 12: the verification-signal selection thesis (4/5) is now the strongest line — if reasoning Day 3 confirms test-time-compute mechanics, consider locking it as the primary thesis direction
