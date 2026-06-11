# 2026-06-07 — Weekly Synthesis: Week 1

## This Week's Readings

**Week of June 1–7, 2026** — First week of AI Tour.

| Day | Course | Topic | Main Paper |
|-----|--------|-------|------------|
| Mon 6/1 | Agents | Architectures | Survey (Masterman et al. 2024) |
| Tue 6/2 | Multimodal | VLM Pretraining | CLIP (Radford et al. 2021) |
| Wed 6/3 | LLM Systems | Inference Serving | Survey (Li et al. 2024) |
| Thu 6/4 | Generative Models | Diffusion Foundations | DDPM (Ho et al. 2020) |
| Fri 6/5 | Agents | Architectures Day 2 | ReAct (Yao et al. 2023) |
| Sat 6/6 | Research Lab | Project Planning | Week 1 Meta Analysis |

**Total: 15 papers read (5 main + 10 related)**

## Major Themes

### 1. Iterative Refinement as a Universal Computation Pattern

Every course studies a system that improves an intermediate state through repeated steps:

- **Agents (ReAct):** Thought → Observation → Next Thought (refine trajectory)
- **Diffusion (DDPM):** Noisy input → Denoise → Less noisy (refine image)
- **LLM Inference:** KV cache grows with each token → Next token prediction (refine sequence)
- **VLM (CLIP):** Single pass, but the contrastive loss implicitly tests multiple candidates

This suggests iterative refinement may be a universal mechanism for difficult AI problems — not just a trick for generation or agents.

### 2. Memory is the Universal Bottleneck

Every field runs into a memory wall:

| Field | Memory Bottleneck | Solution |
|-------|------------------|----------|
| LLM Serving | KV cache exceeds GPU memory | PagedAttention (non-contiguous) |
| Agents | Context window caps trajectory length | Episodic memory (Reflexion) |
| Diffusion | No explicit memory — all computation in inference | Variable step count (DDIM) |
| VLM | Cross-modal attention is expensive | Dual-encoders + lightweight connector |

**Key observation:** The solutions are domain-specific but the problem is the same — we need efficiently addressable, dynamically-sized memory that grows with task complexity.

### 3. The Speed-Quality Tradeoff is Everywhere

| Method | Full Version | Fast Version | Cost |
|--------|-------------|--------------|------|
| DDPM | 1000 steps, high quality | DDIM 10-50 steps | Slight quality loss |
| Naive batching | Wait for complete batch | Continuous batching | More complex scheduling |
| ReAct (prompt) | Zero-shot, slower | Toolformer (finetuned) | Training cost |

In every case, the fast version achieves 10-50x speedup with acceptable quality loss. The "right" operating point depends on the application.

## Cross-Course Connections

### Agents ↔ LLM Systems

- **Direct connection:** Agent workloads have the hardest inference requirements — bursty, variable-length, tool-interleaved. Every agent trajectory is a new serving challenge.
- **Insight:** Current LLM serving research (continuous batching, disaggregated prefill/decode) doesn't model agent workloads. There is a gap.

### Agents ↔ Generative Models

- **Structural similarity:** ReAct's Thought-Action-Observation loop is isomorphic to diffusion's noising-denoising loop. Both involve iterative refinement toward a goal.
- **Insight:** Understanding diffusion dynamics (why denoising works) might inform agent design (why re-reading the trajectory helps).

### Multimodal ↔ Agents

- **Direct connection:** Agents that can see and hear are strictly more capable than text-only agents. But multimodal adds latency and cost.
- **Tension:** CLIP's dual-encoder is fast but shallow; LLM-based VLMs (GPT-4V) are deep but slow.

### LLM Systems ↔ Generative Models

- **Direct connection:** Diffusion models need GPU compute for inference too. The serving problems are similar (batch size, memory, latency).
- **Key difference:** Diffusion models have fixed inference cost per image, independent of image complexity. LLMs cost proportional to token count.

## Contradictions and Tensions

### 1. Zero-Shot vs. Fine-Tuned for Tool Use

**ReAct** (zero-shot prompting) requires no training but makes mistakes and wastes tokens. **Toolformer** (fine-tuned) is more reliable but requires expensive training data generation. No clear winner — likely depends on whether you control the model.

### 2. Contrastive vs. Generative for VLM Pretraining

**CLIP** (contrastive) gives fast, generalizable representations but cannot generate text. **LLaVA-type models** (generative after connector) can answer questions but are slower and more complex. The field is moving toward combined approaches, but there's no principled theory for how to balance the two objectives.

### 3. Single LLM vs. Multi-Agent

Single LLM with tools (ReAct) is simpler but limited by one model's capacity. Multi-agent systems are more flexible but introduce coordination overhead and failure modes. The scaling laws for multi-agent systems are unknown.

## Open Problems

1. **Agent workload-aware serving:** How should inference systems be designed for bursty, interleaved agent workloads rather than steady chat traffic?
2. **Unified memory architecture:** Can PagedAttention's block-granularity memory management generalize to agent memory, diffusion latent spaces, and VLM cross-attention?
3. **Optimal refinement depth:** For a given task, how many ReAct steps / diffusion steps / KV cache tokens are "enough"? Is there a universal rule?
4. **Contrastive-generative tradeoff:** What is the Pareto frontier between contrastive alignment and generative capability in VLMs?

## Possible Thesis Ideas

### Idea 1: Agent-Optimized Inference Serving (Medium Risk)

**Problem:** LLM serving systems (vLLM, TensorRT-LLM) assume steady chat-like traffic. Agent workloads have bursty, tool-interleaved patterns that waste allocated KV cache during tool calls.

**Approach:** Design a serving scheduler that pauses KV cache state during agent tool calls, reallocates freed memory to other requests, and restores state when the tool returns.

**Required background:** Inference serving + agent architectures + systems programming.

**Evaluation:** Throughput and latency comparison on agent benchmarks (SWE-bench, AgentBench) against vLLM and TensorRT-LLM.

**Next step:** Profile real agent trajectories to characterize KV cache idle patterns.

### Idea 2: Adaptive ReAct — Dynamic Reasoning Depth (Low-Medium Risk)

**Problem:** ReAct wastes tokens on unnecessary reasoning for simple tasks, while complex tasks get insufficient reasoning.

**Approach:** Use the LLM's token-level uncertainty (entropy over top-k tokens) to decide at each step: (a) produce another Thought, (b) execute an Action, or (c) produce the final answer.

**Required background:** Agent architectures + uncertainty estimation / confidence calibration.

**Evaluation:** Token efficiency (tokens saved), task success rate (does dynamic reasoning improve accuracy), and trajectory length distribution.

**Next step:** Implement a prototype with DeepSeek API — compare fixed-depth ReAct vs. adaptive-depth ReAct.

### Idea 3: Diffusion-Enhanced ReAct (Higher Risk, Higher Reward)

**Problem:** ReAct's discrete Thought/Observation steps are inefficient — each step is a separate LLM call.

**Approach:** Model the agent's trajectory as a continuous refinement process inspired by diffusion. Each "denoising step" refines the plan instead of generating discrete thoughts.

**Required background:** Diffusion models + agent architectures + generative modeling theory.

**Evaluation:** Compare against ReAct on long-horizon planning tasks (ALFWorld, WebShop).

## What To Read Next

### For Agents
- "Tree of Thoughts" (Yao et al. 2023) — reasoning-focused agent architecture
- "SWE-agent" (Yang et al. 2024) — practical agent system design
- "AgentBench" (Liu et al. 2023) — agent evaluation framework

### For LLM Systems
- "FlashAttention" (Dao et al. 2022) — memory-efficient attention
- "Splitwise" (Patel et al. 2024) — disaggregated inference

### For Generative Models
- "Score-Based Generative Modeling" (Song & Ermon 2019) — score matching perspective
- "Flow Matching" (Lipman et al. 2023) — alternative to diffusion

### For Multimodal
- "LLaVA" (Liu et al. 2023) — modern VLM architecture
- "SigLIP" (Zhai et al. 2023) — improved CLIP training

## Course/Topic Adjustments

No adjustments needed for the first week. The pace (1 main + 2 related per day) feels right for building breadth.

For Week 2, consider:
- **Agents:** Move to Tool Use or Planning topic starting Friday
- **LLM Systems:** Continue on Inference Serving (Day 2) or move to KV Cache
- **Generative Models:** Continue on Diffusion Foundations (Day 2 — Score-Based Models)
- **Multimodal:** Continue on VLM Pretraining (Day 2 — LLaVA)
