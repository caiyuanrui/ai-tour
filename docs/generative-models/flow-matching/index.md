# Flow Matching

**Question:** How does flow matching relate to diffusion and continuous normalizing flows?

🟢 **Active** — Starting 2026-09-03

This directory contains daily research-map notes for this topic.

## Notes

| Date | Paper | Paradigm | Link |
|------|-------|----------|------|

## Connection to Previous Topics

Flow matching is the natural continuation of Sampling: Day 4 of the samplers topic already
paved the way with **Rectified Flow** (reflow recursively re-pairs couplings so trajectories
become straight, making single-step Euler exact) — the canonical bridge between the
speed-of-sampling question and the flow-based generative framework. The topic spans:

- **Flow matching objective**: conditional flow matching (CFM) as a simulation-free
  regression target for continuous normalizing flows (Lipman et al. 2022)
- **Rectified flow**: learning straight-line ODEs between π₀ and π₁ via least-squares reflow
- **Relation to diffusion**: probability-flow ODE / score matching as a special case of flow
  on the Gaussian path; noise-conditioning as one choice of interpolation
- **Speed**: straight trajectories → few-step / single-step sampling without distillation
