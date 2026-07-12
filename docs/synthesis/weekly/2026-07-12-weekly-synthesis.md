# 2026-07-12 — 第6周综合总结

Course: Weekly Synthesis
Topic: Weekly Synthesis
Week: 6 (2026-07-06 ~ 2026-07-11)

---

## 本周阅读记录

| 日 | 课程 | 主题 | 主要论文 |
|---|------|------|----------|
| 周一 7/6 | Agents | Planning (Day 1) | Understanding the planning of LLM agents: A survey (Huang 2024) |
| 周二 7/7 | Multimodal | Image-Text Reasoning (Day 1) | Explain Before You Answer: Survey on Compositional Visual Reasoning (Ke 2025) |
| 周三 7/8 | LLM Systems | Inference Serving — **Capstone (Day 5)** | DeepSpeed-FastGen: Dynamic SplitFuse (Holmes 2024) |
| 周四 7/9 | Generative Models | Score-Based Models (Day 2) | Score-Based SDE (Song 2021) |
| 周五 7/10 | Agents | Planning (Day 2) | LLM+P: Hybrid Classical Planner (Liu 2023) |
| 周六 7/11 | Research Lab | Failure Analysis | P3 Design Assumptions & Validation Gaps |

---

## 主要主题

### 1. Planning 的二元范式：纯LLM vs 混合规划

本周对 Planning 主题进行了深入探索。核心发现是 Planning 领域存在一条根本性的分界线：

- **纯LLM规划**（Plan-and-Solve, ReAct, Tree-of-Thought）——灵活但不可靠，>5步任务容易出错
- **混合规划**（LLM+P, TAPE, NL2Plan）——将自然语言翻译为PDDL或计划图，使用经典求解器保证正确性，但需要领域工程

**关键交叉观察：** Planning 的解耦思想（task-decoupled planning, Beyond Entangled Planning 2026）与 Inference Serving 中的 Dynamic SplitFuse（消除prefill/decode阶段区分）遵循相同的设计模式——将"做什么"和"怎么做"分离。

### 2. Inference Serving 完成：从PagedAttention到Dynamic SplitFuse

周三以 DeepSpeed-FastGen 作为 Capstone 完成了 Inference Serving 主题（5天，15篇论文，置信度0.86→完成）。**取得的完整路线图：**

- 基础层：PagedAttention（vLLM的非连续KV缓存）
- 调度架构：Disaggregation（DistServe）→ 统一调度（Sarathi-Serve）→ Dynamic SplitFuse
- 模型级别加速：Speculative Decoding
- 多模型共享：MuxServe + S3

**关键见解：** prefill/decode 区分是一个调度产物，不是根本约束。Dynamic SplitFuse 通过固定计算的token级调度消除了这个区分。主题前进至 KV Cache。

### 3. 图像-文本推理的新领域

Image-Text Reasoning 的起步（周二，第一次进入Multimodal课程）揭示了 **6种不同的推理类型**（空间、关系、逻辑、因果、数字、类比），当前VLM无法均匀处理。**反事实推理差距**是最突出的弱点（~50%，几乎随机）。

与此相关：**Explain-Before-Answer理念**——应该要求模型在给出最终答案之前产生中间解释，而不仅仅是可选步骤。

### 4. Score-Based Models的SDE统一

周四加深了对Score-Based Models的理解——Song等人的SDE框架（ICLR 2021）将NCSN（得分匹配+Langevin dynamics）和DDPM（去噪扩散）统一为同一个连续时间框架的两个特例。概率流ODE允许确定性的、可逆的采样和似然计算。

理论现在有三层：
1. **SDE框架**（统一几何）
2. **实际训练**（噪声条件化、渐进退火）
3. **似然理论**（得分匹配≈最大似然）

### 5. Research Lab：P3 Failure Postmortem

周六进行了P3原型周期的系统性事后分析，识别了**四个设计级故障模式**：

1. **代理变量失败**（Proxy variable failure）——使用指令长度作为复杂度信号
2. **接口不完整**——预算信号没有定义消费者
3. **模拟过度自信**——没有真实API测试
4. **度量聚合盲区**——87.9%压缩率的标题隐藏了双峰分布（JSON 96.7% vs 文本 18.7%）

**作为论文方向出现的主题模式：** Agent系统设计中的故障模式形态学。

---

## 跨课程连接

| 连接 | 涉及的课程 | 见解 |
|------|-----------|------|
| **解耦设计** | Agents (Planning) ↔ LLM Systems (Inference Serving) | 两个领域独立发现了"分离关注点"的价值：Planning中的task-decoupled planning，Inference Serving中消除prefill/decode阶段区分 |
| **验证差距** | Research Lab ↔ 所有课程 | 本周P3事后分析揭示的"模拟过度自信"是一个普遍问题——论文中的基准测试总是在受控条件下进行，但我们不知道其中多少结果能在实际部署中保持 |
| **规划作为搜索** | Agents (Planning) ↔ Generative Models (Score-Based) | MCTS规划与扩散模型的概率流ODE共享"逐渐精炼信念"的结构——两者都在搜索空间中导航，只是粒度不同 |
| **推理类型不对称** | Multimodal (Image-Text) ↔ Agents (Planning) | 两种模型在"简单"任务上表现良好，但在需要反事实推理或>5步规划的任务上失败——建议"推理深度"是一个跨模态的通用瓶颈 |

---

## 矛盾与张力

1. **纯LLM vs 混合规划** —— LLM+P 实现100%计划可行性，但需要PDDL模板工程。纯LLM规划灵活但不可靠。这两种方法在可预见的未来不会合并——需要**动态规划器选择**。

2. **模块推理 vs 端到端VLM** —— 基于模块的方法（NMNs、ViperGPT）提供可解释性但在现实世界中难以扩展。端到端VLM（LLaVA、Qwen2.5-VL）获得更高的原始分数但无法解释他们的推理。这不是一个中立的设计选择——它取决于部署场景（高风险需要可解释性）。

3. **模拟的压缩率 vs 真实的成本** —— P3纯化器的87.9%压缩率在纸面上令人印象深刻，但真实API计费按token计算，提示token比补全token便宜，缓存提供免费token。字符级压缩 ≠ token级成本节省。

---

## 未解决的问题

1. **规划器何时应该使用混合模式？** 是否存在一个原理性的"切换点"——当任务复杂度超过N步或包含严格前提条件时，自动从纯LLM规划切换到混合规划？
2. **KV缓存是系统瓶颈，但它在Agent工作负载下如何表现？** 推理服务现在已经覆盖了静态工作负载——Agent的短提示/长补全/工具间KV缓存重用模式呢？
3. **我们可以从Zero-shot导向的规划训练吗？** 当前的混合方法需要PDDL编译——下一个突破可能是端到端训练一个LLM，使其在不需要外部求解器的情况下表现出类似规划器的行为。
4. **反事实推理差距是根本性的还是数据问题？** 如果VLM在多模态数据上训练，其中反事实例子在自然分布中很少见，那么差距可能是数据分布的结果，而不是能力限制。
5. **P3的模拟过度自信仍然存在吗？** 事后分析识别了问题但还没有修复——真实的API测试结果是必要的下一步。

---

## 可能的论文方向

1. **用于Agent系统的解耦规划框架** —— 结合task-decoupled planning（来自Beyond Entangled Planning）和hybrid verification（来自TAPE）到一个统一代理架构中。扩展LLM的规划能力而不需要全PDDL流水线。**风险：** 中等。**需要的背景：** LLM+P, TAPE, 搜索算法。

2. **用于Agent工作负载的KV缓存生命周期管理** —— 设计一个将Agent的KV缓存视为一级资源的服务运行时，具有跨多轮Agent交互的驱逐、压缩和预取策略。**风险：** 中等偏高（系统实现工作量）。**需要的背景：** vLLM, 缓存策略, Agent运行时系统。

3. **Agent系统设计中的故障模式分类** —— 将P3事后分析的四个模式扩展为Agent系统的通用故障分类法，有具体的案例研究和缓解策略。可以为《Agent系统度量研究》或《设计方法论》论文。**风险：** 低。**需要的背景：** 对多种Agent系统的经验。

4. **用于图像-文本推理的规划-验证训练** —— 将RLVR应用于多模态推理，目标是中间推理步骤的正确性，而不仅仅是最终答案。解决反事实推理差距，通过程序化生成的问答对明确训练反事实推理。**风险：** 高（计算成本）。**需要的背景：** RLVR, VLM预训练, 场景图。

---

## 下周阅读计划

| 日 | 课程 | 主题 | 建议方向 |
|---|------|------|----------|
| 周一 | Agents | Planning (Day 3) | 搜索式规划方法（Tree-of-Thought、MCTS for LLM Agents） |
| 周二 | Multimodal | Image-Text Reasoning (Day 2) | 模块化推理实现（ViperGPT、VisProg） |
| 周三 | LLM Systems | **KV Cache (Day 1)** | 新主题启动——KV缓存量化和压缩方法调查 |
| 周四 | Generative Models | Score-Based Models (Day 3) | 得分匹配方法学的更深入理解（DSM vs SSM vs Sliced） |
| 周五 | Agents | Planning (Day 4) | 搜索式规划的具体实现（RAP: Reasoning with Planning） |
| 周六 | Research Lab | Project Planning | 基于事后分析的P3真实API测试计划 |

---

## 主题/课程调整

1. **Inference Serving → ✅ 完成，前进到 KV Cache** —— 周三在5天内达到置信度0.86。Strong foundation completed.
2. **Planning 继续到第3天** —— 置信度0.50，领域基础坚实，但还需要2-3天覆盖搜索方法和规划评估。
3. **Image-Text Reasoning 继续到第2天** —— 置信度0.38，刚刚开始建立领域地图。
4. **Score-Based Models 继续到第3天** —— 置信度0.60，SDE理论扎实，需要更多方法学细节。
5. **Research Lab：Failure Analysis → ✅ 完成，前进到 Project Planning** —— 基于失败模式分析，新的Project Planning迭代应优先考虑真实API验证计划。
6. **P3事后分析应该成为论文方向"Agent系统故障模式"的基础。**
