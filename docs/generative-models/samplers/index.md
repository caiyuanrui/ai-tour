# Sampling

**Question:** How do samplers trade quality, speed, and likelihood?

✅ **Completed** — 5 days · 15 papers · conf 0.82 (2026-09-03)

This directory contains daily research-map notes for this topic.

| Date | Papers | Confidence |
|------|--------|------------|
| [2026-08-06](2026-08-06-samplers.md) | DPM-Solver (Lu 2022) + DEIS + UniPC | 0.00 → 0.45 |
| [2026-08-13](2026-08-13-samplers.md) | DPM-Solver++ (Lu 2022) + GENIE + Analytic-DPM | 0.45 → 0.58 |
| [2026-08-20](2026-08-20-samplers.md) | Align Your Steps (Sabour 2024) + Restart Sampling + ADD/SDXL-Turbo | 0.58 → 0.68 |
| [2026-08-27](2026-08-27-samplers.md) | Consistency Trajectory Models (Kim 2023) + DMD + Rectified Flow | 0.68 → 0.74 |
| [2026-09-03](2026-09-03-samplers-capstone.md) | Topic Capstone — Sampling Synthesis (Day 5, no new papers) | 0.74 → 0.82 |

**Topic completed.** Five-day map: 少步采样 = 控制概率流 ODE 离散化误差的一切手段。免训练侧四轴（求解器阶数 / 参数化 ε-vs-x₀ + thresholding / 随机性 / AYS 时间步调度）× 训练侧四机制（一致性 CM→CTM / 分布匹配 DMD / 拉直 reflow / 对抗 ADD）。Next: Flow Matching.
