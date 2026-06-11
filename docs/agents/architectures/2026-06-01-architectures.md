# 2026-06-01 — Agent Architectures

Course: Agents
Topic: Agent Architectures
Stage: Day 1 — Survey/Overview
Confidence: 0.00 → 0.35

## Today's Question

What are the recurring architectural patterns behind useful LLM-based agents?

## Main Paper

**"The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey"**

- **Authors:** Tula Masterman, Sandi Besen, Mason Sawtell, Alex Chao
- **Year:** 2024
- **Venue:** arXiv:2404.11584
- **Link:** https://arxiv.org/abs/2404.11584

### Why this paper?

A focused, recent survey that directly addresses the architectural side of LLM agents — single vs. multi-agent, planning/execution/reflection phases, communication patterns. Good starting point for mapping the design space.

### Core Problem

LLM agents need more than just prompt engineering; they need structured architectures that combine reasoning, planning, memory, and tool use into reliable systems. The field lacks a unified vocabulary for describing these architectures.

### Main Idea

The survey proposes a taxonomy organized around three axes: (1) single vs. multi-agent architectures, (2) the planning-execution-reflection loop, and (3) communication patterns between agents.

Key architectural patterns identified:

- **Single-agent architectures**: a single LLM handles reasoning + action. Simple but limited by context window and single-point failure.
- **Multi-agent architectures**: multiple specialized agents collaborate (manager-worker, peer-to-peer, debate). Higher robustness but harder coordination.
- **Planning phase**: task decomposition (hierarchical, sequential, constraint-based).
- **Execution phase**: tool calling, code execution, environment interaction.
- **Reflection phase**: self-evaluation, error correction, iterative refinement.

### Research takeaway

The architecture choice is not just about capability — it's about the reliability-expressiveness tradeoff. Single agents are easier to debug; multi-agent systems are harder to control but can recover from failures through redundancy.

### Modern perspective (2026)

This survey (Apr 2024) predates many 2025 advances in agent-to-agent protocols and standardized agent communication (e.g., ACP, MCP). But the core architectural patterns it describes remain valid — most modern systems still follow the perceive-reason-act loop.

## Related Papers

### Paper 1: "Large Language Model Agent: A Survey on Methodology, Applications and Challenges"

- **Authors:** Junyu Luo et al. (25 authors)
- **Year:** 2025
- **Venue:** arXiv:2503.21460
- **Role:** Broader context for the main paper

**Contribution:** Surveys 329 papers under a methodology-centered taxonomy covering architectural foundations, collaboration mechanisms, and evolutionary pathways. Unifies fragmented research threads.

**Relation to main paper:** Where Masterman et al. focus on architectural patterns, this survey adds the collaboration and evolution dimensions — how agents interact across time and scale.

**Should deep-read later?** Useful reference for breadth, but less architectural depth than the main paper.

### Paper 2: "Fundamentals of Building Autonomous LLM Agents"

- **Authors:** Victor de Lamo Castrillo, Habtom Kahsay Gidey, Alexander Lenz, Alois Knoll
- **Year:** 2025
- **Venue:** arXiv:2510.09244
- **Role:** Practical architecture blueprint

**Contribution:** Proposes four-component architecture for autonomous agents — perception system, reasoning system (CoT, ToT), memory system (short + long-term), execution system.

**Relation to main paper:** Provides a concrete implementation template for the patterns Masterman et al. describe abstractly. The four systems map directly to the planning-execution-reflection loop.

**Why it matters:** Bridges conceptual taxonomy and practical implementation — useful for anyone building their own agent.

## Current Understanding

LLM agent architectures follow a recurring pattern:

1. **Perception** → **Reasoning** → **Action** → **Reflection** → (loop)
2. Memory (short-term / long-term) threads through all stages
3. The main design choices are: single vs. multi-agent, degree of tool integration, reflection depth

The field has converged on this basic loop, but there is no consensus on:
- optimal memory structures
- when reflection helps vs. adds latency
- how to coordinate multi-agent teams

## Key Concepts

- Perception-Reasoning-Action loop
- Planning-execution-reflection cycle
- Single-agent vs. multi-agent architectures
- Tool integration patterns
- Memory as cross-cutting concern
- Agent communication protocols

## Open Questions

- Is the "one LLM + tools" pattern inherently limited compared to multi-agent systems?
- How does agent architecture scale with task complexity?
- What is the right level of autonomy — should agents ask for human approval on every tool call?
- Does adding reflection always improve reliability, or does it introduce hallucination cascades?

## Possible Thesis Ideas

- **Adaptive agent architecture selection** — a system that dynamically switches between single-agent and multi-agent modes based on task complexity and confidence
- **Minimal viable reflection** — finding the minimum reflection depth needed for reliable task completion

## Next Step

Day 2 should explore a canonical agent implementation (e.g., ReAct or Toolformer) to connect architectural patterns to concrete systems.
