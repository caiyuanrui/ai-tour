# 2026-06-21 — Weekly Synthesis

## This Week's Readings

- Agents / Agent Architectures: Generative Agents — Memory + Reflection + Planning architecture
- Multimodal / VLM Pretraining: SigLIP — Pairwise sigmoid loss for batch-size-independent VLM training
- LLM Systems / Inference Serving: DistServe — Prefill-decode disaggregation for goodput-optimized serving
- Generative Models / Diffusion Foundations: EDM — Systematic design space decomposition for diffusion models
- Agents / Tool Use: Toolformer — Self-supervised tool learning via perplexity-based filtering
- Research Lab / Project Planning: Token-Economic Validation — Priority #3 (Practical Budget-Controlled ReAct Agent) confirmed by HPCA 2026

## Major Themes

- **从架构基础到实践分化 — 本周完成了 Agents 架构闭卷（Generative Agents Day 5），同时启动了 Tool Use 新主题。跨越 6 个课程/主题，展示了研究地图从结构认知到机制理解的系统性演进**
- **服务系统进入解耦时代 — DistServe 证明了 prefill-decode 解耦是生产级推理服务的最优架构，已进入 vLLM、TensorRT-LLM 等主流系统。Sarathi-Serve 的块化 prefill 方案提供了互补的单 GPU 路径**
- **扩散模型设计空间的系统化 — EDM 将扩散模型从单点改进（DDPM, NCSN）提升到设计空间分解的工程科学水平。预调节函数和高阶 ODE 求解器成为标准**
- **VLM 预训练的三角优化 — 损失函数（SigLIP）、数据筛选（DataComp）、训练技巧（EVA-CLIP）构成三个独立可优化的维度，三者可组合带来额外收益**
- **实用 Token 预算控制获得最强外部验证 — HPCA 2026 论文从基础设施角度证明了 naive agent 推理的经济不可持续性，SupervisorAgent（ICLR 2026）提供了无重训的运行时 Token 优化方案。Priority #3 从有趣方向升级为工程紧迫任务**
- **工具使用的三范式成型 — 自监督（Toolformer）、监督微调（Gorilla）、上下文学习（GPT-4/Claude function calling）三种范式的优劣和适用边界更加清晰**

## Cross-Course Connections

- **Agents ↔ LLM Systems (Week 3 重复主题):** DistServe 的预填-解码解耦与代理工作负载的爆发式计算模式之间的矛盾加剧 — 代理在工具调用间的空闲期浪费了解耦系统中的 GPU 资源，而块化 prefill（Sarathi-Serve）恰好能应对代理的短 burst 请求。这是从前提到的交叉方向（代理感知推理调度器）的新增证据
- **Agents ↔ Research Lab:** 本周在 Agents 完成 Tool Use 的第一个地图点（Toolformer）的同时，Research Lab 将 Priority #3（Token 预算控制的 ReAct 代理）从论文验证推进到工程规划阶段。Toolformer 的自监督范式（用下一个 token 预测作为工具用性的代理）与 Priority #3 的运行时滤波器（用廉价信号决定何时分配昂贵计算）共享相同的原则 — 用信号质量而非模型大小管理成本
- **Generative Models ↔ Agents (Week 2 主题延续):** EDM 的预调节框架揭示了扩散模型性能主要由数据表示和求解器的设计选择决定，而非模型架构。这呼应了代理架构课程的核心发现（Day 4 CodeAct） — 行动接口（ACI）设计比模型选择更重要。两个课程独立收敛于同一个元认知：**接口/表示工程 > 模型架构工程**
- **LLM Systems ↔ Generative Models:** DistServe 预填-解码解耦引起的 KV cache 网络传输瓶颈与 EDM 的确定性 ODE 求解器（Heun 2 阶）引发相同问题 — 系统瓶颈正从计算/显存向互联带宽转移。解耦架构需要更高效的内存压缩/传输（KIVI 风格的块级量化），快速采样需要减少求解步骤
- **Multimodal ↔ Agents:** SigLIP 的成对 sigmoid 损失与 Toolformer 的困惑度过滤共享基本逻辑 — 用二元决策替代全局归一化。两者都在各自领域证明了 `局部信号 > 全局归一化` 的原则
- **Synthesis (本周):** 一个令人惊喜的模式正在出现 — 本周 5 个不同课程/主题的论文（Generative Agents, SigLIP, DistServe, EDM, Toolformer）全部来自 2022-2024 年。这标志着研究地图正在从快速消费新论文转向深度消化经典之作。这不是问题 — 知识深度正在建立

## Contradictions and Tensions

- **解耦（DistServe）vs 块化（Sarathi-Serve）— 代理还没有自己的答案:** DistServe 将预填和解码放在不同 GPU 上（消除干扰但增加传输成本），Sarathi-Serve 在单 GPU 上交错块化预填和解码（避免传输但增加调度复杂度）。对于代理工作负载（爆发式、工具交错、多回合），哪种架构更优？两者都不是为代理设计的。从本周的 HPCA 2026 论文看，代理的 Token 消耗模式需要全新的架构
- **自监督（Toolformer）vs 监督（Gorilla）— 泛化 vs 精度:** Toolformer 可以在 6 个简单 API 上自监督学习工具使用，Gorilla 在数千个复杂 API 上监督微调。两个极端之间的决策边界在哪里？什么时候需要昂贵的监督数据？两个方向都没有提供选择指南
- **EDM 确定性 ODE vs 随机 SDE:** EDM 采用确定性概率流 ODE 和 2 阶 Heun 求解器（稳定但可能缺乏模式覆盖），而原始的 SDE 方法（Song 2021）有更好的多样性但质量略低。在实践中，现代扩散模型都使用确定性求解器加速采样，但这是否牺牲了生成多样性？
- **认知层次 vs 工具复杂性:** 当代理获得更复杂的工具（代码执行、数据库查询）时，CogRouter 的四层认知层次是否需要重新设计？Generative Agents 的反思周期在城市模拟中足够，但在实时工具交互中太慢。Trading off complexity 和 responsiveness 没有通用方案
- **SigLIP 的变化 vs 整体改进:** SigLIP 显著改进了 CLIP 训练效率，但 DataComp 和 EVA-CLIP 也取得了幅度相当甚至更大的改进（且不需要改变损失函数）。这三个方向是否真的正交可叠加？如果收益是相加的，这只是工程问题；如果重叠，则研究资源需要重新分配

## Open Problems

- **代理工作负载的推理服务架构（第 3 周持续）。** 爆发式、工具交错、高容器化的小请求（类似 lambda 函数）在现有服务系统中根本没有优化的执行模型
- **KV cache 传输带宽（第 3 周升级）。** 随着上下文长度增加到 128K+，解耦系统中 KV cache 传输成本成为新的性能瓶颈。块级量化（KIVI）可能是解决方案，但需要服务于吞吐量的联合优化
- **自监督工具学习的扩展性。** Toolformer 在 6 个 API 上有效。有没有办法将自监督扩展到数百个 API 而不退化为噪声？
- **扩散模型潜空间预调节理论。** EDM 的预调节是为像素空间设计的。潜扩散（Stable Diffusion）需要不同的预调节策略，但目前缺乏理论基础
- **Token 预算控制的主动 vs 被动机制。** 是让代理自主决定何时停止思考（如 CogRouter），还是在系统层强制 Token 限制（SupervisorAgent）？两者的结合可能是最优的但尚未被研究
- **单一代理 vs 多代理的 Token 经济学差异。** SupervisorAgent 适用于多代理系统。其无 LLM 自适应滤波器能否应用于单一代理 ReAct 循环？这是 Priority #3 需要回答的问题
- **扩散模型设计空间向视频和时间数据的推广。** EDM 的系统性消融方法论能否扩展到视频扩散（额外的时序维度）？这可能是生成模型领域的一个博士级别项目

## Possible Thesis Ideas

- **[P3] 实用 Token 预算控制 ReAct 代理（可执行，本周最强信号）** — 问题：现有代理在无限计算下浪费 Token。为什么重要：HPCA 2026 从基础设施层面证明了不可持续性。方法：运行时观察纯化滤波器 + 2-3 级推理努力路由（使用 API 提供商的 thinking budget 控制）。无重训，纯工程。预期收益：每个任务减少 30-50% Token 消耗。评估：每任务 Token 数、成功率、每任务成本。风险：低（现有组件可组合，仅需集成）。下一步：在 Hermes 代理中实现 MVP
- **[P2] 统一资源自适应代理框架（高新颖性，第 2 周延伸）** — 同时调整推理深度（CogRouter）和信息获取（DeepControl）的双轴适应。新增 SupervisorAgent 的运行时滤波作为第三个维度。没有现有论文涵盖所有三个。风险：中等（三个组件均需独立构建和验证）。
- **[P1] 自适应认知深度用于真实世界代理任务（已验证，需要训练管道）** — CogRouter 仅在 ALFWorld 和 ScienceWorld 上验证。扩展到网页浏览和 API 编排需要新的训练数据。风险：高（需要模拟环境）。新信号：DistServe 的 goodput 指标可以重新定义为代理认知成本的衡量标准
- **扩散模型设计空间的课程化。** EDM 的消融方法论可用于创建 diffusion model design space 的教学/交互式地图。这不是研究论文方向，而是教育工具方向。与本网站（AI Tour）高度一致
- **内存架构的统一视角。** Generative Agents 的记忆流、PagedAttention 的块管理、EDM 的预调节函数、SigLIP 的独立成对损失 — 所有这些都以不同的方式解决同一个问题：管理有限的信息容量。一个跨领域的统一内存管理理论是可能的但需要高度抽象

## What To Read Next

- Agents / Tool Use: ToolLLM 或 in-context function calling 论文 — 加深对监督和 ICL 范式的理解
- LLM Systems / Inference Serving → KV Cache: KIVI（KV cache 量化）和 StreamingLLM（窗口式注意力），这两者直接桥接推理服务和代理记忆
- Generative Models / Diffusion Foundations → Sampling: DPM-Solver（当前标准快速采样器），连接 EDM 的确定性 ODE 框架到实际求解器
- Multimodal / VLM Pretraining: 数据筛选（DataComp 筛选策略）或损失函数变体探索 — 两者都直接连接本周的开放问题
- Research Lab: 实现 Priority #3 MVP — 在 Hermes 代理中构建 Token 预算控制器
- New recommendation: **Memory for agents 作为跨领域主题** — A-MEM、Mem0、MemGPT 等代理记忆系统的工作连接了 Agents（Generative Agents 的记忆流）、LLM Systems（KV cache 管理）和 Research Lab（Priority #3 的观察纯化）

## Next Week Adjustments

- **Agents (Tool Use):** 第 1 天，置信度 0.35 — 需要继续 3-4 天。周一和周五两个 slot 都分配给 Tool Use。计划：ToolLLM（监督范式）→ in-context function calling（ICL 范式）→ 工具使用与规划的交互
- **Multimodal (VLM Pretraining):** 3 天，置信度 0.68 — 再读 1-2 天然后进入下一主题（Image-Text Reasoning 或 Grounding）
- **LLM Systems (Inference Serving):** 2 天，置信度 0.60 — 下一主题应为 KV Cache（缓存管理）或 Memory Optimization。注意：周一过后的 Agents slot 可能通过工具范式影响系统需求
- **Generative Models (Diffusion Foundations):** 3 天，置信度 0.78 — 非常接近推进阈值（0.80）。Day 4（DPM-Solver）后很可能推进到 Sampling 或 Score Models 主题
- **Research Lab:** 从 project-planning 推进到 implementation-notes — 开始构建 Priority #3 MVP。不晚于下周六
- **主站状态更新:** 反映新的 Topic 进度（Agent Architectures ✅ Completed, Tool Use 🟢 Active）
- **Synthesis:** 创建第 3 周 synthesis 导航条目
