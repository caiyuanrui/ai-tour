# 2026-06-14 — Weekly Synthesis

## This Week's Readings

- Agents / Agent Architectures: Tree of Thoughts (ToT — Yao 2023) — search-based reasoning beyond linear ReAct
- Multimodal / VLM Pretraining: Visual Instruction Tuning (LLaVA — Liu 2023) — CLIP + connector + LLM paradigm
- LLM Systems / Inference Serving: LLM Inference Serving Survey (Li 2024) — KV cache, batching, disaggregation
- Generative Models / Diffusion Foundations: NCSN (Song & Ermon 2019) — score-based perspective and SDE unification
- Agents / Agent Architectures: CodeAct (Wang 2024) — code-native actions and harness engineering
- Research Lab / Project Planning: CogRouter + ARES + DeepControl — adaptive reasoning depth validated

## Major Themes

- 搜索式推理成为主流：ToT/GoT 从线性 ReAct 扩展到树/图搜索，LLM 同时作为生成器和评估器
- 代码即行动（Code-as-Action）：CodeAct 和 SWE-agent 证明代码执行作为行动空间的优势，Agent-Computer Interface (ACI) 成为新设计维度
- 统一化趋势持续：SDE 框架统一了 DDPM 和 NCSN（扩散 + 分数匹配），LLaVA 的 connector 架构成为 VLM 标准模式
- 推理服务的三重杠杆：内存管理（PagedAttention）、调度（连续批处理）、解耦（prefill/decode 分离）
- 自适应推理深度（Adaptive Cognitive Depth）已成为已验证研究方向 — CogRouter 和 ARES 独立验证
- 基础设施即架构：Harness Engineering（行动接口 → 工作流 → 持久化三层）将框架基础设施提升为一等架构要素

## Cross-Course Connections

- Agents ↔ LLM Systems：代理工作负载（burty、工具交错）对推理服务提出独特挑战，当前服务系统未针对此场景优化
- Agents ↔ Generative Models：ReAct 的 Thought-Action-Observation 循环与扩散的去噪迭代同构 — 两者都是逐步精细化过程
- Agents ↔ Research Lab：CogRouter 验证了自适应推理深度的可行性（Week 1 提出的 thesis idea 已被独立论文证实）
- LLM Systems ↔ Agents：KV cache 是连接点 — 代理的长时间交互产生巨大 KV cache，PagedAttention 的非连续块管理可能启发代理记忆系统设计
- Generative Models ↔ VLM：扩散模型在 VLM 高分辨率编码（S2, AnyRes）中的应用 — 空间细节的逐步还原类似扩散过程
- 所有课程 → Synthesis：迭代精细化和记忆瓶颈是所有课程共享的深层模式

## Contradictions and Tensions

- 通用代码执行（CodeAct）vs 环境特定 ACI（SWE-agent）— 统一行动空间 vs 专用界面
- AG-172：ToT 的搜索策略（BFS/DFS）在高质量但高成本（10-100× token 开销）和低成本但低质量（直接 CoT）之间没有理论指导
- G-85：DDPM 的噪声预测（简单实用）vs NCSN 的分数匹配（理论优雅）— 为什么实用的训练目标胜过理论严谨的？这是一个开放的理论问题
- 预填充计算密集 vs 解码内存密集 — 同一 GPU 上的共存干扰使得联合优化困难，解耦方案增加网络带宽需求
- Router 方法（ARES 外部轻量级分类器）vs 训练代理人本身（CogRouter 的 CoSFT+CoPO）— 实用性 vs 优雅性
- VLM 连接器：线性投影（LLaVA 简单有效）vs Q-Former（BLIP-2 参数高效但指令跟随能力受限）

## Open Problems

- 代理最优推理服务：如何设计服务于爆发式、工具交错的代理工作负载，而非稳定的对话流量？
- 自适应搜索-蒸馏：能否将 ToT 搜索模式蒸馏到单次前向传递中，使推理保持搜索级质量但成本降至 CoT 级别？
- 统一记忆架构：PagedAttention 的块粒度内存管理能否泛化到代理记忆、扩散潜空间和 VLM 交叉注意力？
- 认知深度层次的可迁移性：CogRouter 的 4 级层次（本能 → 常规 → 审慎 → 战略）能否迁移到真实世界的代理环境（网页浏览、API 编排、编码）？
- 最优块大小：PagedAttention 的块大小在不同模型规模和硬件上的最优值是什么？
- 结合适应：推理深度适应（CogRouter/ARES）和信息获取控制（DeepControl）能否合并为统一框架？
- 长上下文 KV cache（128K+）：超长序列的 KV cache 如何避免 DRAM 溢出？
- 置信度校准敏感性：CogRouter 的置信度感知优势对 LLM 通常存在的校准误差有多敏感？

## Possible Thesis Ideas

- 统一资源自适应代理框架（优先级 1）：结合推理深度适应（CogRouter/ARES）和信息获取控制（DeepControl）的双轴适应框架。这比任何现有工作都更全面，因为到目前为止没有论文同时研究两个维度。风险：高。新颖性：高。
- 自适应认知深度用于真实世界代理任务（优先级 1b）：在 CogRouter 的认知层次基础上扩展到真实环境（网页浏览、API 编排）。CogRouter 仅在 ALFWorld 和 ScienceWorld（模拟环境）上测试，真实世界代理的挑战完全不同。独特角度：信息过载使得自适应深度在网页代理中特别关键。
- 实用 ReAct 代理带 Token 预算控制（优先级 3，最高速度路径）：使用现有 API 控制（Anthropic thinking budget, OpenAI reasoning.effort）构建轻量级自适应深度代理。无模型训练需要，即时可衡量结果。可发布为技术报告或博客。
- KV cache 感知代理调度器：设计一个服务系统，利用代理在工具调用期间空闲的 KV cache，将释放的内存重新分配给其他请求，并在工具返回时恢复状态。
- 自适应视觉 Token：根据图像复杂度动态分配更多/更少的视觉 Token，降低简单图像成本，提高复杂图像细节。
- 自适应行动格式选择：构建一个根据任务难度和环境约束在文本工具调用、代码执行和结构化接口之间动态切换的架构 — 统一 ReAct 和 CodeAct 两大分支。

## What To Read Next

- Agents: Tool Use 主题 — Toolformer / Gorilla / API-Bank 作为下一主题
- LLM Systems: vLLM / PagedAttention 深度阅读 — 理解块管理算法和 CUDA 内核实现
- Generative Models: DPM-Solver 和一致性模型 — 加速采样的实用技术
- Multimodal: 进入 Image-Text Reasoning 主题 — 或继续 VLM Pretraining 进入高分辨率方向
- Research Lab: 实现 Priority 3（实用 Token 预算控制代理）作为下一个实验
- Everything: Agent workload-aware serving survey — 如果存在的话，连接 agents 和 LLM Systems

## Next Week Adjustments

- Agents (Architectures): 当前置信度 0.75，days_spent=4。应按计划在第 5 天推进到下一主题（Tool Use），除非本周的 Day 5 笔记明确说明战略重要性
- LLM Systems (Inference Serving): 仅 1 天，置信度 0.45 — 需要继续至少 3-4 天以达到 0.80，计划阅读 vLLM（PagedAttention）和 KIVI（KV cache 压缩）
- Generative Models (Diffusion Foundations): 2 天，置信度 0.65 — 继续 1-2 天进入采样方法主题（DPM-Solver, DDIM, consistency models）
- Multimodal (VLM Pretraining): 2 天，置信度 0.60 — 再读 1-2 天（高分辨率 VLM, InternVL）后进入下一主题
- Research Lab: 开始实现 Priority 3——使用 Hermes 或轻量级 Python 框架构建自适应深度 ReAct 代理
- mkdocs nav: 添加 Week 2 synthesis 到导航
