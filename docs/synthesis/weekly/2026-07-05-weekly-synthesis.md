# 2026-07-05 — Weekly Synthesis (Week 5)

## This Week's Readings

| Date | Course | Topic | Main Paper | Confidence Δ |
|------|--------|-------|-----------|-------------|
| Jun 29 (Mon) | Agents | Tool Use — Safety & Composition | ChainCaps (Jiang 2026) | 0.62 → 0.70 |
| Jun 30 (Tue) | Multimodal | VLMs — Topic Capstone | VLM Pretraining Synthesis | 0.74 → **0.82** ✅ |
| Jul 1 (Wed) | LLM Systems | Inference Serving — Day 4 | Sarathi-Serve (Agrawal 2024) | 0.68 → 0.78 |
| Jul 2 (Thu) | Generative Models | Score Models — Day 1 | Consistency Models (Song 2023) | 0.00 → 0.40 |
| Jul 3 (Fri) | Agents | Tool Use — Topic Capstone | Tool Use Synthesis | 0.70 → **0.82** ✅ |
| Jul 4 (Sat) | Research Lab | Experiment Log | P3: Stateful Routing + Purification Benchmark | 0.00 → 0.75 |

## Major Themes

### 1. 里程碑：完成两大主题 + 两个主题接近完成
本周完成两个完整主题的探索：

- **agents/tool-use**（5天，conf 0.82）—— 从 Toolformer 自监督工具学习到 ChainCaps 工具组合安全，完整覆盖四阶段
- **multimodal/vlm-pretraining**（5天，conf 0.82）—— 从 CLIP 对比预训练到 MM1 设计空间方法论

同时 **llm-systems/inference-serving** 接近完成（4天，conf 0.78），再有一天即可进入下一个主题（KV Cache）。

### 2. 工具组合安全 —— 新的安全维度
本周最重要的新发现：**工具组合安全**作为独立研究维度出现。

- **ChainCaps**: 单调能力衰减 + MCP 代理实现运行时安全
- **ToolPrivBench**: 特权感知的工具选择（过度授予问题）
- **ChainFuzzer**: 灰盒模糊测试发现多工具漏洞（365个漏洞，302个需要多步骤触发）

核心洞察：数现有的每个工具独立安全检查都通过的情况下，组合效果可能不安全。这在保护机制上打开了一个全新的方向。

### 3. 推理系统的分叉路径：分块预填 vs. 分离式推理
Sarathi-Serve 提出**分块预填+无停顿批处理**作为分离式推理的轻量级替代方案：

| 方案 | 复杂性 | 适用场景 | 核心机制 |
|------|--------|---------|---------|
| DistServe (分离式) | 高 | 集群规模 | 独立的预填/解码服务器集群 |
| Sarathi-Serve (分块预填) | 低 | 单节点 | 将预填拆分为调度单元，填充解码空闲 |

设计选择取决于部署规模——这不是非此即彼的对抗，而是分层方案。

### 4. 单步生成取得进展
Consistency Models 展示了无需对抗训练即可从学习到的扩散先验进行单步生成（CD FID 3.55 @ 1步）。与质量差距仍然存在（CT FID 8.70 vs DDPM FID 3.17），但趋势清晰：采样效率在系统性地提升，直接相关于实时部署。

### 5. P3 原型验证确认
研究实验室的 P3 原型完成了两个关键实验：

- **观察净化**: 8种真实工具输出上 87.9% 压缩率，大型 JSON 压缩至 3.3%，所有边缘情况安全
- **状态路由**: 修复了始终-ECONOMY 的 bug（旧路由 8/8 步走 ECONOMY，新路由正确分配 2 ECONOMY + 4 STANDARD + 2 DEEP）
- **根因确认**: 逐指令长度是任务复杂度的糟糕代理——累积工具输出大小是最强信号

P3 的三个组件中 2 个已达到生产就绪。

## Cross-Course Connections

### Agents ↔ Systems
ChainCaps 的工具组合安全是一个处于边界的系统问题。MCP 代理实现是一种纯系统方法，解决了代理安全问题。这意味着**代理安全的下一个前沿可能是系统层的**，而非仅仅对齐训练。

### Agents ↔ Research Lab
P3 原型的令牌经济学与代理架构密切相关。只要代理运行在按令牌计费的 API 上，令牌消耗就是核心成本——P3 的观察净化 + 状态路由提供了 23-50% 的理论成本节约。这与工具组合安全相连接：更多工具调用意味着更多令牌，意味着更大的 P3 应用空间。

### Generative Models ↔ Agents
Consistency Models 的单步生成启发了新的应用：代理环境中的**实时感知**——如果视觉推理可以缩短到单次前向传播，多模态代理可以在每个步骤中"看"到更多内容而不成为延迟瓶颈。

### Multimodal ↔ Generative Models
Consistency Models 应用于潜在空间产生了潜在一致性模型（LCM），广泛用于实时文生图。这与扩散基础部分紧密相关，展示了分数估计和扩散之间的深层连接。

## Contradictions and Tensions

### 分离式 vs. 分块预填
DistServe 认为完全分离是必要的，而 Sarathi-Serve 认为分块预填可以在单个服务器上实现类似收益。这种紧张关系反映了推理系统中不同层级的优化范式。正确的答案可能是：**取决于规模**。

### 一致性 vs. 质量
Consistency Models 在单步生成上取得了令人印象深刻的进步（FID 3.55），但仍然落后于扩散模型 1000 步（DDPM FID 3.17）。问题是：这个差距是**根本性的**（单步约束意味着信息瓶颈）还是**工程性的**（更大的模型、更好的训练可以弥合差距）？

### 工具覆盖 vs. 工具安全
使用工具越多，攻击面就越大。Agent 能力和 Agent 安全之间存在根本性权衡。ChainCaps 的单调衰减尝试限制这个权衡，但一般工具（如代码解释器）的能力预算是一个开放问题。

## Open Problems

1. **面对数十万 API 的工具组合安全如何扩展？** ChainCaps 只在有限的 API 集上验证。单调衰减能否扩展到开放世界？

2. **P3 的真实 API 成本验证尚未完成。** 状态路由将更多步骤提升至 STANDARD/DEEP，增加了每步成本。87.9% 的压缩能否抵消这些成本增加？需要实际 API 调用实验。

3. **LLM 系统的下一主题应该是什么？** 推理服务接近第 5 天，下一个主题是 KV 缓存（KV 缓存量化、驱逐、PagedAttention 优化）或批处理与调度。

4. **agents/planning 应该从哪个角度切入？** Language Agent Tree Search？SayCan-style 任务分解？层次化规划系统？

5. **Consistency Models 的单步质量天花板。** 这能否通过更大的模型或更好的训练目标超越？

## Possible Thesis Ideas

### 短期项目（原型级）
1. **P3 真实 API 成本验证** —— 在 GAIA/SWE-bench 上运行 P3，测量实际令牌节约（本周已验证 87.9% 压缩，下一个是端到端测试）
2. **统一工具安全框架** —— 结合 ChainCaps（衰减）+ ToolPrivBench（选择）+ ChainFuzzer（测试）为一个可验证安全的代理架构
3. **KV 缓存量化实验** —— 在 PagedAttention 上验证块级量化（作为 LLM 系统推理服务的自然延续）

### 中期项目（方向级）
4. **面向代理推理的自适应服务** —— 结合 Sarathi-Serve 的分块预填 + 令牌经济学 + KV 缓存复用，专门用于工具交织的代理负载
5. **实时代理感知的 Consistency Models** —— 应用 LCM/一致性蒸馏实现单步感知，实现多模态代理的实时决策

### 远期项目（论文级）
6. **最小复杂度代理路由** —— 系统评估代理任务中复杂度预测的廉价信号（指令长度、工具输出大小、类型分布），发布测量研究（2-3 周文献 + 2 周实验）

## What To Read Next

- **agents/planning**: Tree-of-Thoughts → Language Agent Tree Search → ReAct-based planners
- **multimodal/image-text-reasoning**: MMStar, LLaVA-NeXT, Chain-of-Thought with vision
- **llm-systems/kv-cache**: KIVI (KV cache quantization), StreamingLLM, H2O
- **generative-models/score-models**: Score-based SDE → Flow Matching → Rectified Flow
- **research-lab/failure-analysis**: P3 graceful degradation gap, always-ECONOMY case study

## Course/Topic Adjustments

| Course | Active Topic | Status | Next Step |
|--------|-------------|--------|-----------|
| Agents | **Planning** (new, 0.0) | 🟢 Active | Tree-of-Thoughts or LATS |
| Multimodal | **Image-Text Reasoning** (new, 0.0) | 🟢 Active | LLaVA-NeXT or MMStar |
| LLM Systems | **Inference Serving** (4d, 0.78) | 🟢 Active | Day 5 capstone → advance to KV Cache |
| Generative Models | **Score-Based Models** (1d, 0.40) | 🟢 Active | Day 2: score-based SDE or flow matching |
| Research Lab | **Failure Analysis** (new, 0.0) | 🟢 Active | P3 limitations analysis |

**Completed this week:** agents/tool-use ✅, multimodal/vlm-pretraining ✅

## Weekly Reflection

本周是第 5 周，也是**高潮周**——完成两个完整主题（Tool Use 和 VLM Pretraining），另外两个主题接近完成（Inference Serving 和 Diffusion Foundations 上周完成）。

研究的三个新兴方向值得特别关注：

1. **工具组合安全**——当代理可以自由调用工具链时，组合级安全成为瓶颈。这为安全研究打开了一个全新的领域，紧跟在工具调用可靠性之后。

2. **分块预填作为分离式推理的轻量级替代**——两种方法在核心推理优化路径上都有位置，具体取决于部署规模。

3. **P3 原型验证**——令牌经济的实验证实展示了如何通过系统级的观察压缩和路由优化来经济高效地应对代理成本问题。这是论文级的发现，可以在真实代理基准上验证。

下周的关键决策：**Inference Serving** 到达第 5 天（Capstone），应推进到 KV Cache；**Planning** 作为代理线路的下一个主要挑战展开；**Image-Text Reasoning** 启动多模态的第二主题。
