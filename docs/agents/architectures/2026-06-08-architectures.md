# 2026-06-08 — Agent Architectures (Day 3)

Course: Agents
Topic: Agent Architectures
Stage: Day 3 — Planning-Focused Reasoning
Confidence: 0.55 → 0.65

## Today's Question

How do agents go beyond linear reasoning to explore multiple solution paths?

## Main Paper

**"Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (ToT)**

- **Authors:** Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, Karthik Narasimhan
- **Year:** 2023
- **Venue:** NeurIPS 2023 / arXiv:2305.10601
- **Link:** https://arxiv.org/abs/2305.10601

### Why this paper?

After covering ReAct (linear Thought-Action loop), ToT is the natural next step — it introduces explicit search over reasoning paths, bridging LLM agents with classical AI planning.

### Core Problem

Chain-of-Thought (CoT) and ReAct generate a single linear reasoning path. This fails for tasks that require exploration, lookahead, or backtracking — if the first few steps are wrong, the entire trajectory is wasted.

### Main Idea

Represent intermediate reasoning steps as nodes in a tree, and use search strategies (BFS, DFS) to explore multiple paths simultaneously:

1. **Thought decomposition**: break the problem into intermediate "thoughts" (coherent text units)
2. **Generation**: at each node, prompt the LLM to generate K candidate next thoughts
3. **Evaluation**: have the LLM self-evaluate each candidate (sure/maybe/impossible)
4. **Search**: use BFS (breadth) or DFS (depth) with pruning

### Technical Details

- **Thought**: a full sentence or equation, not a token — unlike CoT's token-level
- **Evaluation**: LLM provides a scalar value or classification for each partial solution
- **Search strategies**:
  - BFS: keep top-b candidates at each depth (good for breadth-heavy tasks like Creative Writing)
  - DFS with pruning: explore one branch, backtrack on failure (good for Math puzzles)
- **Results**: Game of 24: 4% (CoT GPT-4) → 74% (ToT GPT-4). Creative Writing: human eval shows dramatic improvement

### Research takeaway

The key insight is that **LLMs can serve as both the generator and the evaluator** in a search algorithm. This is a fundamental shift from "use LLM once for answer" to "use LLM iteratively in a search loop". The LLM becomes a component in a larger reasoning system.

### Modern perspective (2026)

ToT sparked a wave of search-based reasoning extensions (GoT, RAP, AoT, MCTSr). The main limitation is cost — ToT uses 10-100x more tokens than CoT. Practical systems use cheap/fast models for evaluation and expensive models for generation, or distill search patterns into single-pass finetuned models.

## Related Papers

### Paper 1: "Graph of Thoughts: Solving Elaborate Problems with Large Language Models" (GoT)

- **Authors:** Maciej Besta, Nils Blach, Ales Kubicek, et al.
- **Year:** 2024
- **Venue:** AAAI 2024 / arXiv:2308.09687
- **Role:** Extension of ToT

**Contribution:** Generalizes ToT from tree to arbitrary graph structures — thoughts can be combined, distilled, or fed back. Enables complex operations like merging multiple reasoning paths.

**Relation to main paper:** ToT is a special case of GoT (tree as a restricted graph). GoT adds: (1) merging independent thought chains, (2) feedback loops, (3) distillation from many thoughts to one. Achieves +62% on sorting quality with -31% cost vs ToT.

**Should deep-read later?** Useful as a reference but the practical value depends on task type — graph structures add complexity.

### Paper 2: "Self-Refine: Iterative Refinement with Self-Feedback"

- **Authors:** Aman Madaan, Niket Tandon, Prakhar Gupta, et al.
- **Year:** 2023
- **Venue:** NeurIPS 2023 / arXiv:2303.17651
- **Role:** Complementary iterative refinement

**Contribution:** Single loop of generate → self-feedback → refine → generate, repeated until convergence. No search, just iterative improvement.

**Relation to main paper:** ToT uses search (exploring alternatives); Self-Refine uses iterative refinement (improving the same path). Both are forms of "LLM evaluates LLM" but with different strategies. Self-Refine is simpler and cheaper.

## Current Understanding

LLM reasoning can be categorized by its search structure:

| Method | Structure | Search | Cost | Use Case |
|--------|-----------|--------|------|----------|
| CoT | Linear | None | Low | Simple reasoning |
| ReAct | Linear + tools | Implicit | Medium | Interactive tasks |
| Self-Refine | Loop | None | Medium | Writing, code |
| ToT | Tree | BFS/DFS | High | Puzzles, planning |
| GoT | Graph | Arbitrary | Very High | Complex reasoning |

The spectrum is from "single shot" (CoT) to "deliberate search" (GoT). The right choice depends on task complexity and cost budget.

## Key Concepts

- Thought decomposition + search
- LLM as generator and evaluator
- BFS vs DFS for reasoning
- Self-evaluation and pruning
- Graph-structured reasoning (GoT)
- Iterative refinement vs. search-based reasoning

## Open Questions

- What is the optimal tradeoff between search breadth (ToT) and search depth (deep CoT)?
- Can search patterns be distilled into a single forward pass (e.g., via training)?
- How should the evaluation function be calibrated — is LLM self-evaluation reliable enough?
- Does the benefit of ToT/GoT hold for tasks beyond puzzles and math?

## Possible Thesis Ideas

- **Search-to-Distill** — train a model to internalize ToT search patterns so inference is single-pass but retains search-level quality
- **Adaptive search strategy** — dynamically choose between CoT, ReAct, ToT, or GoT based on task features and budget

## Next Step

Day 4 should explore evaluation of agents, or move to the next topic (Tool Use) if confidence >= 0.80 by then.
