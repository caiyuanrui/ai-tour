# 2026-07-19 — 第7周综合总结

Course: Weekly Synthesis
Topic: Weekly Synthesis
Week: 7 (2026-07-13 ~ 2026-07-18)

---

## 本周阅读记录

| 日 | 课程 | 主题 | 主要论文 |
|---|------|------|----------|
| 周一 7/13 | Agents | Planning (Day 3) | A Roadmap to Guide the Integration of LLMs in Hierarchical Planning (Puerta-Merino 2025) |
| 周二 7/14 | Multimodal | Image-Text Reasoning (Day 2) | ViperGPT: Visual Inference via Python Execution for Reasoning (Surís 2023) |
| 周三 7/15 | LLM Systems | **KV Cache (Day 1)** | KIVI: A Tuning-Free Asymmetric 2-bit Quantization for KV Cache (Liu 2024) |
| 周四 7/16 | Generative Models | Score-Based Models (Day 3) | Sliced Score Matching (Song 2019) |
| 周五 7/17 | Agents | Planning (Day 4) | HIPIF: Hierarchical Planning and Information Folding (Diao 2026) |
| 周六 7/18 | Research Lab | Project Planning (Day 1, Cycle 2) | Reasoning in Token Economies (Wang 2024) |

---

## 主要主题

### 1. 层次化结构：本周的跨课程核心模式

本周最显著的跨课程连接是"层次化"作为 AI 系统设计的通用原则在各个课程中反复出现：

- **Agents/Planning — HTN 层次化规划**：Puerta-Merino 路线图提出了 LLM 与 HTN 集成的5级框架（0-4），核心主张是 Agent skill 库应组织为 HTN 方法层次结构，而非扁平列表。
- **Agents/Planning — HIPIF 层次化分解**：Diao 等人（2026）的双层架构（高层规划器生成子目标，低层执行器执行动作）是 HTN 思想在端到端训练框架中的具体实例化。
- **Multimodal — ViperGPT 程序式推理**：通过将视觉查询分解为可执行的 Python 代码（函数调用树），形成一种隐式的层次化推理结构。
- **LLM Systems — Fractal KV-Cache**：KV 缓存码序列的组织采用递归定义的块结构，即是存储层面的层次化。
- **Research Lab — SDB 合同模式**：Runtime Architecture 论文中的 Stochatic-Deterministic Boundary 是一个四部分合同（提议者、验证者、提交者、拒绝者），本质上是一个层次化控制架构。

**关键见解：层次化正在成为 AI 系统设计的"元模式"**——不仅出现在经典的规划和推理中，也出现在系统基础设施、视觉推理和智能体运行时架构中。

### 2. 信息瓶颈：压缩、折叠、量化

另一条贯穿本周的线索是"信息瓶颈"——如何高效地通过有限容量通道传递信息：

- **KV Cache 量化（KIVI）**：将 FP16 KV 缓存压缩至 INT2，实现5倍内存缩减，<0.1 PPL 损失。
- **HIPIF 信息折叠**：完成子目标后将轨迹压缩为固定长度表示——功能上等同于 KV 缓存的时序版本。
- **ViperGPT 感知瓶颈（BLINK）**：人类 95.7% vs GPT-4V 51.3% 证明了感知层面的信息瓶颈，推理能力被底层感知的有限容量所限制。
- **Sliced Score Matching**：将 O(d²) Hessian 迹估算降低至 O(d) 的随机投影方法——这是信息瓶颈在训练算法层面的体现。

**跨领域问题：** 压缩粒度如何选择？KIVI 对键使用逐通道、对值使用逐token；HIPIF 每子目标折叠一次；ViperGPT 的视觉模块各司其职。每种应用自然决定了其压缩粒度——但优化这个粒度本身就是一个基础性问题。

### 3. Planning 主题深入：从5种范式到核心二分

Planning 主题在本周取得了显著进展（days_spent: 2→4, confidence: 0.50→0.72）：

- **Day 3 (HTN 路线图)**：引入了层次化规划作为纯LLM和混合PDDL之外的第三范式
- **Day 4 (HIPIF + 规划-执行分离 + 规划复用)**：增加了三个新维度——上下文压缩、安全驱动的规划-执行分离、经验驱动的规划复用

**核心二分法已经演变为：**

| 维度 | 两极 | 
|------|------|
| 规划结构 | 显式（PDDL/HTN/Code） vs 隐式（latent/no-plan） |
| 规划粒度 | 扁平（单层） vs 层次化（多层分解） |
| 上下文管理 | 累积（全部保留） vs 折叠（压缩已完成子目标） |
| 规划时机 | 预规划（plan-then-execute） vs 交错（ReAct） |
| 规划复用 | 从头生成 vs 检索+适配 |

**价值分布洞察：** 本周的5篇规划相关论文清楚地展示了"分层"的价值——预规划（安全的）、层次化分解（可扩展的）、折叠/压缩（高效的）、复用/检索（低延迟的）。每种技术针对规划的不同瓶颈。

### 4. 方法论成熟：评估与计量

本周出现了两个方法论贡献：

- **Token Economies（Wang 2024）**：固定预算基线 + 成本分解 + 多预算评估，直接揭示了之前被隐藏的计量膨胀。
- **Beyond Success Rate（Kassianik 2026）**：不同任务类型有不同预算扩展规则的实证证据。

这两个论文为 P3 的 Cycle 2 提供了方法论基础：**评估框架必须与运行时架构匹配**。如果智能体有预算信号但没有定义的消费者，评估就无法测量真正重要的事情。

### 5. Score-Based Models 的物理结构

Score-Based Models 本周完成了一个优雅的理论闭环（Sliced Score Matching 使训练可行，High-Order DSM 填补似然差距，Score Shocks 揭示 Burgers PDE 结构）：

- **Score Shocks（Sarkar 2026）**：扩散模型的得分场满足粘性 Burgers 方程，模式分离过渡对应激波前沿——得分误差在模式边界处被指数级放大。
- **三层次理解**：计算（SSM，O(d)可行）→ 统计（High-Order DSM，一阶不够）→ 物理（Burgers PDE，激波结构）。

---

## 跨课程连接

| 连接 | 涉及的课程 | 见解 |
|------|-----------|------|
| **层次化作为元模式** | Agents (Planning) ↔ Multimodal ↔ LLM Systems ↔ Research Lab | HTN / HIPIF / ViperGPT / Fractal KV-Cache / SDB 合同模式都体现了"分层分解+本地化处理"的相同设计原则。这不是巧合——这是 AI 系统的基本架构杠杆。 |
| **信息瓶颈无处不在** | LLM Systems (KV Cache) ↔ Agents (HIPIF) ↔ Multimodal (BLINK) | 从 GPU HBM 中的 KV 缓存字节到智能体长期上下文中的折叠表示到 VLM 中感知模块的信号质量——每个层面都受限于通过有限容量通道的信息流。**智能体系统设计就是瓶颈管理。** |
| **计量方法论平行进化** | Research Lab (P3) ↔ Agents (Planning) ↔ All courses | P3 的"模拟过度自信"发现与 Planning 的"纯LLM vs 混合"评估差距相同——我们在受控条件下测试，报告最佳情况，然后发现现实更复杂。需要更系统的评估方法论。 |
| **ReAct 默认值受到挑战** | Agents (Planning Day 4) ↔ Multimodal (Image-Text) | Plan-then-Execute 论文安全论点 + HIPIF 长程上下文论点 + ViperGPT 的预生成代码范式——三个独立的方向都在质疑 ReAct（交错思考-行动）作为默认架构是否合适。 |
| **代码作为统一行动语言** | Agents (Planning) ↔ Multimodal (ViperGPT) | HIPIF 的高层策略/低层执行器接口和 ViperGPT 的代码生成范式都使用**可执行代码**作为推理与行动之间的桥梁。Code-as-Action 的理念在 Agent 架构和视觉推理中同时出现。 |

---

## 矛盾与张力

1. **显式 vs 隐式规划** —— 本周通过 iCLP 引入了潜变量规划，它挑战了整个显式规划生成的前提。如果隐含规划在大规模上有效，那么所有的显式结构（PDDL、HTN、计划图）可能只是当前模型局限性的结果，而不是未来架构的基本要求。

2. **量化 vs 驱逐** —— KV 缓存有两个主要优化方向：缩小每个条目（量化）或移除条目（驱逐）。KIVI 和 H2O 代表相反的策略，它们的相互作用被低估了——量化是否会破坏驱逐方法所依赖的重要性信号？

3. **感知瓶颈 vs 推理扩展** —— BLINK 显示人类的感知（95.7%）与最好的 VLM（51.3%）之间存在巨大差距。但这个差距会随着模型规模扩大而消失吗？如果会，那么 ViperGPT 的基于程序的方法可能是暂时的桥梁。如果不会，那么感知和推理是根本独立的瓶颈。

4. **模仿 vs 真实规划** —— 本周复杂的规划方法（LLM+P、HTN 集成、HIPIF）让智能体看起来"会规划"，但大部分成功可能来源于模仿训练数据中的规划模式。RL 训练（GRPO、ORM）是否会导致真正的规划能力，还是仅仅更好的模仿？

5. **纯度 vs 成本** —— P3 的净化器在 JSON 上达到 96.7% 压缩但在文本上只有 18.7%。这是净化有用还是成本有效？答案取决于工作负载——以 JSON 为主的智能体得到巨大优势，以文本为主的智能体得到微小的收益。

---

## 未解决的问题

1. **层次化的最优深度是多少？** 无论是 HTN 方法深度、HIPIF 子目标层次、还是 ViperGPT 的函数调用树——层次化结构都存在自然的最优深度概念。如何自动确定？

2. **KV 缓存在智能体工作负载下的表现？** 大部分 KV 缓存研究是在连续文本生成上进行的。智能体的短提示-长工具输出-短下一个提示模式完全不同的——缓存重用、驱逐策略、预取模式都不同。

3. **感知瓶颈是根本性还是工程性的？** 如果 VLM 的感知在更大模型和数据规模下继续改善（即便以更慢的速度），那么 BLINK 差距可能是工程性的。如果感知改善停滞，则是根本性的架构限制，需要纯视觉子系统的专用接口（ViperGPT 风格）。

4. **RL 能否真正教会规划？** 本周确认了四种不同的规划范式。关键问题是 RL 训练（GRPO、Process Reward Models）在哪一个范式上最有效——训练 LLM 更好地规划，还是更好地模仿规划数据中的模式？

5. **P3 的真实 API 压缩率？** 87.9% 的模拟压缩率尚未在真实 API 调用上验证。真实 API 的 token 计费（提示 vs 补全、缓存命中 vs 未命中）会大幅改变成本计算方式。

---

## 可能的论文方向

1. **Agent 系统的层次化瓶颈理论** —— 将信息瓶颈概念应用于 Agent 架构设计：识别每个 Agent 架构中的瓶颈层级，推导最优层次深度、压缩粒度、和信号传递协议。结合本周四个课程中的层次化洞察（HTN、HIPIF、Fractal、SDB）为统一的 Agent 架构设计理论。**风险：** 中等偏高（需要形式化框架）。**需要的背景：** HTN 规划、信息论、Agent 系统设计。

2. **KV 缓存生命周期管理用于 Agent 工作负载** —— 设计一个针对多轮工具交互的 Agent 工作负载优化的 KV 缓存系统，具有于工具调用模式感知的驱逐和预取策略。将量化（KIVI）和结构化驱逐（Fractal）组合到统一的 Agent 缓存管理器中。**风险：** 中等（实现工作量大）。**背景：** vLLM、KV 缓存技术、Agent 运行时。

3. **预算感知的 ReAct Agent 评估方法论** —— 将 Token Economies 框架专门扩展到单 Agent ReAct 循环：定义路由开销分解、固定预算基线、每预算准确度报告。作为后续 P3 论文的方法论基础。**风险：** 低（方法论贡献）。**背景：** Token Economies 论文、P3 原型。

4. **用于层次化 Agent 规划的 Burgers 约束得分模型** —— 将扩散模型中的 Burgers PDE 结构（Score Shocks）与 Agent 系统的层次化规划架构联系起来：将智能体的规划空间视为连续空间上的得分场，使用 Burgers 动力学约束训练一个规划得分模型。**风险：** 高（跨领域新形而非渐进式贡献）。**背景：** 得分匹配、Burgers 方程、层次化规划。

5. **Agent 系统设计中的故障模式形态学** —— 将 P3 事后分析识别的四个故障模式（代理变量失败、接口不完整、模拟过度自信、度量聚合盲区）扩展为 Agent 系统评估的通用分类法，附带具体案例研究和缓解策略。**风险：** 低。**背景：** 对多种 Agent 系统的经验。

---

## 下周阅读计划

| 日 | 课程 | 主题 | 建议方向 |
|---|------|------|----------|
| 周一 | Agents | Planning (Day 5 — Capstone) | 规划主题总结与综合，准备前进至 Memory 或 Reasoning |
| 周二 | Multimodal | Image-Text Reasoning (Day 3) | 端到端 VLM 推理能力（GPT-4V、Gemini、Qwen2.5-VL）或 multimodal RLVR |
| 周三 | LLM Systems | KV Cache (Day 2) | KV 缓存驱逐方法（H2O、StreamingLLM、ReST-KV） |
| 周四 | Generative Models | Score-Based Models — 前进决策 | 置信度0.72（Day 3），需要再1天达成0.80或前进至 Sampling |
| 周五 | Agents | Planning (Day 5) 或 Memory/Raisonning | 视 Planning 完成情况而定 |
| 周六 | Research Lab | Project Planning (Day 2) | P3v2 SDB 合同设计 + 评估框架设计 |

---

## 主题/课程调整

1. **Planning 继续到第5天（Capstone）** —— 置信度0.72，还剩1天达到最大天数5天。下一次应完成 Planning 主题总结，前进至 Memory 或 Reasoning。
2. **Image-Text Reasoning 继续到第3天** —— 置信度0.50，刚刚建立了三种推理范式（基于程序、端到端、世界模型），还有很大探索空间。
3. **KV Cache 继续到第2天** —— 置信度0.35，刚完成量化基础，需要覆盖驱逐方法形成完整图景。
4. **Score-Based Models 前进决策待定** —— 置信度0.72，days_spent=3。需要决定是再读1天达到0.80，还是前进至 Sampling 主题。
5. **Research Lab：Project Planning 继续** —— 置信度0.72，Cycle 2 的设计阶段刚刚开始，还需要1-2天完成 SDB 合同和评估框架设计。
6. **跨课程主题"层次化作为元模式"值得持续追踪。** 这个方向可能发展为论文方向 #1（Agent 系统的层次化瓶颈理论）。
