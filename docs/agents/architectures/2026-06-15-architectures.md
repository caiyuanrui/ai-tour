# 2026-06-15 — Agent Architectures

Course: Agents
Topic: Agent Architectures
Stage: Day 5 — Capstone
Confidence: 0.75 -> 0.85

## Today's Question

How do memory, reflection, and planning components integrate into a complete agent architecture that produces believable, emergent behavior?

## Main Paper

### Metadata

- Title: Generative Agents: Interactive Simulacra of Human Behavior
- Authors: Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
- Year: 2023
- Venue: UIST 2023 (ACM Symposium on User Interface Software and Technology)
- Link: https://arxiv.org/abs/2304.03442

### Why this paper?

This is the canonical architecture that demonstrates how memory, reflection, and planning work together in a single agent system. While ReAct showed the Thought-Action-Observation loop and ToT explored structured reasoning, Generative Agents is the first paper to show a complete, self-contained architecture where agents maintain persistent memory, reflect on past experiences, form higher-level insights, and plan future behavior — all while interacting with each other in a multi-agent setting. It's the perfect capstone for the architectures topic because it unifies almost every architectural component we've studied into one coherent system.

### Core Problem

How can LLM-based agents produce believable, coherent human-like behavior over extended periods, including forming opinions, remembering past interactions, making plans, and exhibiting emergent social behaviors — all without explicit scripting?

### Main Idea

Extend an LLM with three core architectural components:

1. **Memory Stream** — A complete natural-language record of everything the agent experiences. Every observation, conversation, and action is stored as an atomic memory entry with a timestamp.

2. **Reflection** — High-level synthesis where the agent periodically reviews recent memories and extracts higher-level insights and beliefs. For example, after observing that "Klaus mentioned his project multiple times" → the agent might reflect "Klaus is passionate about his work."

3. **Planning & Retrieval** — The agent uses its memories to dynamically plan daily behavior. Plans are hierarchical: day-level → hour-level → action-level. The retrieval mechanism selects the most relevant memories based on recency, importance, and relevance.

### Technical Details

- **Memory formulation:** Each memory entry contains timestamp, description, and an importance score (0-10). Importance is scored by the LLM itself.
- **Reflection trigger:** When the cumulative importance of recent memories exceeds a threshold, the agent generates a reflection by asking the LLM to identify high-level patterns.
- **Planning:** At the start of each day, the agent generates a plan (structured as "wake up at X, then Y..."). Plans are decomposed and stored as if they are memories, so they influence future reflection.
- **Retrieval:** Uses a weighted combination of recency, importance, and relevance (via embedding similarity) to select the top-N memories for the LLM context.
- **Multi-agent interaction:** Agents share a common environment. When one agent acts, the action is broadcast as an observation to nearby agents. This enables social dynamics to emerge from individual agent decisions.

### Results

- Agents produce believable individual behaviors: waking up, cooking breakfast, going to work, socializing.
- Emergent social behavior: From a single seed ("Agent A wants to throw a Valentine's Day party"), agents autonomously spread invitations, form new relationships, coordinate arrival times.
- Ablation study confirms all three components (observation/recording, reflection, planning) are necessary for believable behavior.

### Limitations

- Sandboxed environment (text-based, small town of 25 agents). Scaling to larger worlds is untested.
- Importance scoring by the LLM itself introduces potential bias.
- Reflection is periodic and coarse-grained — the agent may miss subtle patterns.
- The architecture assumes agents operate in synchronous time steps, which limits real-time responsiveness.
- No explicit learning or skill acquisition mechanism — agents don't improve at tasks over time.

### Modern perspective (2026)

Generative Agents established the "memory + reflection + planning" paradigm that most modern agent architectures build on. Key evolutions since:
- A-MEM (2025) formalized agentic memory using Zettelkasten-style linking (NeurIPS 2025)
- Mem0 and similar systems now provide production-grade agent memory with persistence layers
- The reflection component has been adopted by virtually every serious agent system
- The paper's emphasis on emergent behavior sparked the multi-agent systems research direction

## Related Papers

### Paper 1: Voyager — An Open-Ended Embodied Agent with Large Language Models

- Authors: Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar
- Year: 2023
- Venue: NeurIPS 2023
- Link: https://arxiv.org/abs/2305.16291

**Contribution (3 bullets):**
- Introduces the first LLM-powered embodied lifelong learning agent (in Minecraft) with three components: automatic curriculum, skill library of executable code, and iterative prompting with environment feedback.
- Achieves 3.3× more unique items, 2.3× longer travel distances, and 15.3× faster tech tree progression vs. prior SOTA.
- The skill library (Python code) enables composition and mitigates catastrophic forgetting — skills are temporally extended, interpretable, and composable.

**Relation to main paper:** Complementary architecture. Where Generative Agents uses natural-language memory + reflection for social simulation, Voyager uses executable code libraries + automatic curriculum for embodied skill acquisition. Both show that agent architectures benefit from a persistent store (memories vs. skills) beyond the context window, but they solve different problems: social believability vs. open-ended exploration.

### Paper 2: A-MEM — Agentic Memory for LLM Agents

- Authors: Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang
- Year: 2025
- Venue: NeurIPS 2025
- Link: https://arxiv.org/abs/2502.12110

**Contribution (3 bullets):**
- Proposes a dynamic, agentic memory system based on the Zettelkasten method — memories are atomic notes with structured attributes (descriptions, keywords, tags), automatically linked by meaningful similarity.
- Introduces memory evolution: new memories can update existing memories' contextual representations, enabling the knowledge network to continuously refine itself.
- Outperforms SOTA baselines across six foundation models, showing that dynamic memory organization outperforms fixed storage/retrieval.

**Relation to main paper:** Direct evolution. A-MEM formalizes and improves the memory component of the Generative Agents architecture. Where Generative Agents used a flat memory stream with hand-crafted retrieval weighting, A-MEM creates structured, interconnected memory networks with automated linking and evolution. This represents the trajectory from ad-hoc memory → principled memory systems in agent architectures.

## Current Understanding

The architectures topic has now covered the main lineages of LLM agent architecture:

1. **ReAct loop** — The foundational Thought-Action-Observation pattern (Day 2)
2. **Structured reasoning** — Tree/Graph of Thoughts extends ReAct to non-linear search spaces (Day 3)
3. **Code-native actions** — CodeAct shows executable code as a superior action representation, with SWE-agent demonstrating environment-specific ACI design (Day 4)
4. **Memory + Reflection + Planning** — Generative Agents shows how persistent memory, periodic reflection, and hierarchical planning integrate into a coherent architecture for long-term coherent behavior (Today)

The meta-insight is that while each paper presents distinct architectural patterns, they share a common underlying structure: an LLM core surrounded by augmentative components (memory, tools, search, reflection). The "harness" or "scaffold" wrapping the model is increasingly recognized as the main determinant of agent capability.

## Key Concepts

- Memory stream: complete natural-language record of agent experiences
- Reflection: periodic high-level synthesis of memories into insights and beliefs
- Hierarchical planning: day-level → hour-level → action-level plan decomposition
- Retrieval weighting: recency × importance × relevance for memory selection
- Skill library: executable code as persistent, composable agent knowledge
- Automatic curriculum: LLM-driven task proposal based on current state
- Iterative prompting: environment feedback + execution errors + self-verification for program improvement
- Zettelkasten memory: atomic notes with structured attributes and automatic linking
- Memory evolution: new memories updating existing memories' representations

## Open Questions

- Can the Generative Agents architecture scale to hundreds or thousands of agents without collapsing into incoherence?
- How should agents balance reflection frequency vs. real-time responsiveness — is periodic reflection sufficient?
- Does the memory + reflection + planning pattern generalize beyond social simulation to tool-use and task-completion domains?
- Can code-native skill libraries (Voyager) and natural-language memory (Generative Agents) be unified into a single architecture?
- Is retrieval-based context augmentation sufficient, or do agents need true gradient-based learning over their experience?

## Possible Thesis Ideas

- **Unified memory-skill architecture** — Combine Generative Agents-style natural-language memory with Voyager-style code skill libraries in a single agent that can both reflect on past experiences and execute learned skills.
- **Adaptive reflection scheduling** — Develop a dynamic reflection strategy that adjusts frequency and depth based on task complexity, novelty of observations, and time-criticality of decisions.
- **Memory-evolution metrics** — Design evaluation metrics for agent memory quality (not just task completion) — measuring memory coherence, retrieval precision, and the quality of reflections.
- **ACI for long-term agents** — Extend the ACI (Agent-Computer Interface) concept from SWE-agent to multi-day agent interactions where the interface must support memory, planning, and reflection alongside tool execution.

## Next Step

Advance from architectures to the next topic: **Tool Use**. The question shifts from "how are agents structured?" to "how do agents decide when and how to use external tools?" This is a natural progression — now that we understand the architectural patterns, we can explore how architectures enable tool-use behavior.
