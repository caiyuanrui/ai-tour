# Reasoning

Question: **How do agents improve reasoning through search, reflection, verification, or self-consistency?**

✅ **Completed** — 2026-08-10 → 2026-08-24 · 5 days · 15 papers · conf 0.83

## Notes

| Date | Paper | Paradigm | Link |
|------|-------|----------|------|
| 2026-08-10 | Chain-of-Thought Prompting (Wei 2022) | Generation / Survey | [📄](2026-08-10-reasoning.md) |
| 2026-08-14 | Let's Verify Step by Step (Lightman 2023) | Verification / PRM | [📄](2026-08-14-reasoning.md) |
| 2026-08-17 | DeepSeek-R1 (DeepSeek-AI 2025) | RL acquisition / verifiable rewards | [📄](2026-08-17-reasoning.md) |
| 2026-08-21 | SEEA-R1 (Tian 2025) | RLVR beyond math/code / reward engineering | [📄](2026-08-21-reasoning.md) |
| 2026-08-24 | Topic Capstone — Generation → Verification → RL Acquisition | Capstone / Synthesis | [📄](2026-08-24-reasoning.md) |

## Map

The Reasoning topic's spine is a single progression: **generate traces (CoT) → verify traces (ORM/PRM, test-time compute) → train the generator against the world's own signal (RLVR)**. The verifier hierarchy (rule-based → discriminative RM → generative RM → search-densified) is the design ladder that carries the topic into RL-for-agents.
