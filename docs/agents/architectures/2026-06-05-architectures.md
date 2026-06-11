# 2026-06-05 — Agent Architectures (Day 2)

Course: Agents
Topic: Agent Architectures
Stage: Day 2 — Canonical implementation
Confidence: 0.35 → 0.55

## Today's Question

How do agents combine reasoning traces with external actions?

## Main Paper

**"ReAct: Synergizing Reasoning and Acting in Language Models"**

- **Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
- **Year:** 2023
- **Venue:** ICLR 2023 / arXiv:2210.03629
- **Link:** https://arxiv.org/abs/2210.03629

### Why this paper?

ReAct is the most influential agent architecture paper of the LLM era. It defines the standard pattern — interleaved Thought/Action/Observation — that almost all modern agent frameworks (LangChain, AutoGPT, OpenAI Assistants) follow.

### Core Problem

LLM reasoning (Chain-of-Thought) and acting (tool use) were studied separately. CoT reasons internally but cannot access external information, leading to hallucination and stale knowledge. Acting alone (e.g., calling APIs) lacks the structure to plan and recover from errors.

### Main Idea

Interleave **reasoning traces** and **task-specific actions** in a single prompt sequence:

```
Thought: I need to find the birth year of Person X.
Action: Search[Person X]
Observation: Person X was born in 1985.
Thought: Now I need to find their first published paper.
Action: Search[Person X first paper]
...
```

This loop continues until the task is solved. The reasoning trace serves as working memory; actions ground reasoning in external reality; observations provide feedback for error recovery.

### Technical Details

- No fine-tuning required — works with 1-2 in-context examples
- Implements a simple API: Thought, Action (with tool-specific arguments), Observation (tool output)
- Tested on: HotpotQA (reasoning + search), ALFWorld (text-game), WebShop (online shopping)
- Key results: +34% on ALFWorld, +10% on WebShop over imitation learning baselines

### Research takeaway

ReAct's key insight is architectural: **the LLM's context window is the agent's memory and planning workspace**. There is no separate memory system, no formal planning module — the agent uses its own text generation as a scratchpad that it re-reads at every step. This is simple, elegant, and surprisingly effective.

### Modern perspective (2026)

ReAct remains the dominant agent architecture. Extensions include: Reflexion (adds explicit self-reflection and memory), ReST (reinforcement self-training), and multi-agent variants. The main limitation is context window size — long ReAct trajectories hit token limits. Modern implementations use sliding windows, summarization, or external memory to mitigate this.

## Related Papers

### Paper 1: "Reflexion: Language Agents with Verbal Reinforcement Learning"

- **Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao
- **Year:** 2023
- **Venue:** NeurIPS 2023 / arXiv:2303.11366
- **Role:** Follow-up extension

**Contribution:** Adds a self-reflection module and episodic memory to the ReAct loop. The agent reflects on its failures in natural language, stores reflections in a memory buffer, and retrieves them in subsequent trials (no weight updates needed).

**Relation to main paper:** Adds the reflection phase that Masterman et al.'s survey identified as critical. Demonstrates that "verbal reinforcement" (textual self-critique) can substitute for expensive RL fine-tuning.

**Why it matters:** Reflexion achieved 91% pass@1 on HumanEval (coding), surpassing GPT-4, using only verbal feedback. This suggests reflection is a powerful and underexplored dimension.

### Paper 2: "Toolformer: Language Models Can Teach Themselves to Use Tools"

- **Authors:** Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, et al.
- **Year:** 2023
- **Venue:** arXiv:2302.04761
- **Role:** Complementary tool-use paradigm

**Contribution:** Self-supervised approach to tool use — the model generates API calls in its text, filters those that improve prediction loss, and fine-tunes on the augmented data. Becomes a fluent tool-user without human annotations.

**Relation to main paper:** ReAct uses prompting for tool use; Toolformer uses fine-tuning. Together they define the two main approaches to making LLMs tool-capable. Toolformer's approach is more thorough but requires training; ReAct is zero-shot but less reliable.

## Current Understanding

The ReAct pattern (Thought → Action → Observation → Thought → ...) is the dominant agent architecture for LLMs. Key properties:

1. **Emergent memory**: the context window serves as both working memory and task trace
2. **Interpretable**: every step is human-readable
3. **Extensible**: tools are just APIs plugged into the Action slot
4. **Self-correcting**: failed actions produce error observations that the next Thought can address

The main open question is how to extend ReAct beyond the context window's limits for long-horizon tasks. Reflexion addresses this with external episodic memory; Toolformer addresses the tool discovery problem.

## Key Concepts

- Thought-Action-Observation loop
- Reasoning trace as working memory
- Tool use via API calls in natural language
- In-context learning for agent behavior
- Self-reflection and verbal reinforcement
- Self-supervised tool use

## Open Questions

- How long can a ReAct trajectory effectively be before context window limits degrade performance?
- Is the Thought-Action-Observation pattern optimal for all tasks, or specialized patterns needed?
- How should agents prioritize between thinking more (more reasoning steps) vs. acting more (more tool calls)?
- Can reflection be interleaved during execution (not just after failure)?

## Possible Thesis Ideas

- **Adaptive ReAct depth** — dynamically decide whether the next step should be a Thought (more reasoning) or an Action (call tool) based on uncertainty estimation
- **Hierarchical ReAct** — nested Thought-Action loops where high-level plans decompose into sub-trajectories

## Next Step

Day 3 should explore planning-focused agent architectures (e.g., Tree-of-Thought, or mechanistic interpretability of agents).
