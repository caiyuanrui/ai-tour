# 2026-09-03 — Sampling Topic Capstone: 速度-质量-似然权衡的完整谱系

Course: generative-models
Topic: samplers
Stage: Capstone (Day 5 of 5)
Confidence: 0.74 -> 0.82

> **综合笔记（capstone day）**：本日不读新论文、不检索，只综合前四天笔记（2026-08-06 / 08-13 / 08-20 / 08-27）与本主题状态文件，为 Sampling 主题收尾并推进到 **flow-matching**。

## Topic Map

| Day | Date | 主轴 | 主论文（+ 相关） | 置信度 |
|-----|------|------|------------------|--------|
| 1 | 2026-08-06 | 求解器阶数：免训练高阶 ODE 求积 | DPM-Solver（+ DEIS, UniPC） | 0.00 → 0.45 |
| 2 | 2026-08-13 | 参数化 × guidance 稳定性 | DPM-Solver++（+ GENIE, Analytic-DPM） | 0.45 → 0.58 |
| 3 | 2026-08-20 | 时间步调度优化与免训练极限 | Align Your Steps（+ Restart, ADD） | 0.58 → 0.68 |
| 4 | 2026-08-27 | 训练侧少步采样的内部机制 | CTM（+ DMD, Rectified Flow） | 0.68 → 0.74 |
| 5 | 2026-09-03 | **Capstone 综合** | —（无新论文） | 0.74 → 0.82 |

## Journey Recap

**Day 1 — 求解器阶数（DPM-Solver / DEIS / UniPC）**：把采样问题形式化为解一个**半线性概率流 ODE**——其线性部分可精确积分，唯一需要数值近似的是一项"网络输出的指数加权积分"。高阶指数积分器（2-3 阶）对该积分做高精度近似，多步变体复用历史网络评估，使高阶不增加 NFE。免训练把 NFE 从 ~1000 压到 10-20 步。DDIM 被还原为 1 阶特例。地图第一轴：**阶数越高、同 NFE 下离散化误差越小**。

**Day 2 — 参数化 × guidance（DPM-Solver++ / GENIE / Analytic-DPM）**：真实文生图几乎总用大 CFG scale，而高阶求解器在 guidance 下数值不稳定（多步外推放大 guidance 引起的剧烈输出变化）。解法是**换参数化**：从 ε 预测换到 x₀ 预测（轨迹更平滑、对 guidance 鲁棒）+ thresholding（把预测 x₀ 截回数据范围）。随机性/方差是正交旋钮——Analytic-DPM 给出解析最优反向方差。地图第二轴：**参数化方式决定求解器在 guidance 下的稳定性**。

**Day 3 — 时间步调度可优化（AYS / Restart / ADD）**：时间步排布（线性/余弦/EDM ρ-spacing）此前全是手工启发式。AYS 从随机微积分推导可计算的**失真度量**，用动态规划求全局最优调度——免梯度、对求解器黑盒友好、几乎零成本；少步数（4-10 步）下收益最大，且与蒸馏叠加（能进一步改善 LCM）。Restart 是另一条免训练路线：周期性注入噪声"重启"，用 SDE 随机性收缩 ODE 累积误差。ADD/SDXL-Turbo 是训练侧极端（1-4 步）。地图第三轴：**调度本身是几乎免费的第四自由度**；开放问题 #6 部分回答——免训练中间地带存在（4-10 步）但到不了 1 步。

**Day 4 — 训练侧内部机制（CTM / DMD / Rectified Flow）**：训练侧不是单一机制而是**四条正交路线**：一致性（CM→CTM：把"同点映射"推广为"任意轨迹区间跳跃算子"，混合去噪得分匹配+轨迹一致性+对抗损失，单步 CIFAR-10 FID 1.73 / ImageNet-64 1.92，**保留得分功能与 likelihood**——修复了 CM"加速必损质量、丢得分"两大缺陷）、分布匹配（DMD：近似 KL 梯度 = 目标得分 − 合成得分，双得分网络 + 回归损失，免对抗）、拉直（Rectified Flow：reflow 递归重排耦合让轨迹变直，单步 Euler 即精确）、对抗（ADD，Day 3 已读）。跨轴洞见：AYS（优化步长）与 reflow（拉直轨迹）从两端攻击同一个"离散化误差"。

## Unified Understanding — 跨日主线

五天下来，Sampling 主题可以用**一句话**收束：

> 少步采样 = 控制概率流 ODE 离散化误差的一切手段；免训练侧在**固定轨迹**上优化离散化（阶数 × 参数化 × 调度 × 随机性），训练侧在**重塑轨迹**（拉直 / 跳跃化 / 分布匹配 / 对抗压缩），使离散化本身变得不重要。

**三维权衡（质量 / 速度 / 似然）的完整谱系：**

| 轴 | 自由度 | 代表方法 | 步数区间 | 代价 |
|----|--------|----------|----------|------|
| 免训练·求解器 | 阶数、多步复用 | DDIM → DPM-Solver/DEIS → UniPC | 10-20（少至 4-10） | 无 |
| 免训练·参数化 | ε vs x₀ 预测、thresholding | DPM-Solver++ | 10-20（CFG 下稳定） | 无 |
| 免训练·随机性 | 方差调度、重启 | Analytic-DPM、Restart | 中-多步质量提升 | 无 |
| 免训练·调度 | 时间步排布 | AYS（失真度量 + DP） | 4-10 免费提升 | 无 |
| 训练·一致性 | 同点映射 → 区间跳跃 | CM → LCM → CTM | 1-4 | 训练 + 质量封顶（CTM 缓解） |
| 训练·分布匹配 | KL 梯度 = 双得分差 | DMD | 1 | 训练 + 双网络 |
| 训练·拉直 | 耦合重排使轨迹变直 | Rectified Flow / reflow | 1（Euler 精确） | 多轮 reflow 训练 |
| 训练·对抗 | score distillation + 判别器 | ADD (SDXL-Turbo) | 1-4 | 训练 + 对抗不稳定 |

**跨领域模式（对 thesis 地图最重要）：**

1. **"加速"不是一个问题而是一族机制。** 免训练侧四条轴、训练侧四条路线，彼此正交、可叠加（AYS × LCM、CTM 混合目标、DMD×CTM 得分复用都是未闭合的组合空间）。任何"更快采样"的新工作都应先指明自己动的是哪根轴。
2. **免训练与训练在"离散化误差"上汇合。** AYS 为弯曲轨迹优化步长；reflow 把轨迹变直让步长不再重要；CTM 学跳跃算子让任意步长都成立。三者是同一枚硬币的三面。
3. **似然是蒸馏的隐性牺牲品。** 除 CTM（保留得分、可算 likelihood）外，DMD/ADD/reflow 都只优化样本质量；"训练侧加速是否系统性牺牲 likelihood/可控性"至今无系统测量——这是全主题最干净的研究缺口。
4. **与 score-models 主题衔接：** CM 在 score-models（07-02）读过，其"加速必损质量"缺陷在 CTM 处修复；score smoothing 与少步采样的交互（平滑宽度 → 采样质量）仍未闭合。与 diffusion-foundations 衔接：EDM 设计空间（Day 3）是调度启发式的源头，AYS 是对它的直接升级。

## Consolidated Key Concepts

- 概率流 ODE 的半线性结构：线性部分闭式积分 + 网络输出的指数加权积分（DPM-Solver 家族的数学基础）
- 免训练四轴：求解器阶数 / 参数化（ε vs x₀ + thresholding）/ 随机性（最优方差、Restart 重启）/ 时间步调度（AYS 失真度量 + 动态规划）
- 训练侧四机制：一致性（CM→CTM 轨迹跳跃算子）/ 分布匹配（DMD 双得分差）/ 拉直（reflow）/ 对抗（ADD）
- CTM 混合目标：去噪得分匹配 + 轨迹一致性 + 对抗损失；保留得分功能与 likelihood（克服 CM 缺陷）
- 速度-质量谱系端点：免训练 4-10 步（免费）→ 训练 1 步（CTM FID 1.73 / DMD 2.62 / ADD SDXL 级）
- AYS × reflow 从两端攻击离散化误差；调度优化与蒸馏可叠加（AYS 改善 LCM）
- ODE 误差累积 vs SDE 随机性收缩误差（Restart 机制洞见）
- x₀ 预测在高阶求解 + 大 CFG 下比 ε 预测稳定（DPM-Solver++ 核心）

## Top Open Questions

1. **蒸馏的似然代价**：训练侧加速（DMD/ADD/reflow）是否系统性牺牲 likelihood、可控生成与分布覆盖？CTM 声称保留得分，缺口多大？（全主题最值得做的系统测量）
2. **统一蒸馏目标框架**：一致性 / 分布匹配 / 拉直 / 对抗四目标能否放进可调节损失组合，系统映射"目标权重 × 步数 × 质量"权衡面？对抗组件的真实贡献占比（CTM vs 无对抗版本）？
3. **CTM × AYS**：把 AYS 失真度量推广到 CTM 的轨迹跳跃空间，推导最优跳长排布——两条"学轨迹/优化轨迹"路线是否正交？
4. **免训练 vs 训练的边界量化**：以 CTM/DMD/reflow 1-2 步为参照系，免训练路线（AYS + DPM-Solver++ + Restart 叠加）的真实质量下限在哪？4 步以下必须训练的证据是什么？
5. **调度迁移理论**：AYS 的最优调度在 (求解器, 模型, 数据集) 之间的迁移规律？能否学到调度函数？最优调度是否随 CFG scale 移动（指导感知调度）？
6. **reflow 拉直与 CTM 轨迹学习能否统一**：都是"学轨迹"，是同一框架的两个极端（拉直 vs 跳跃算子）吗？与 flow-matching 的关系（见下）？

## Refined Possible Thesis Ideas

- **蒸馏感知调度（distillation-aware schedules）**：把 AYS 的调度优化从"对求解器黑盒"升级为"对蒸馏目标感知"——为 CTM 长跳 / reflow 直线轨迹推导各自的"最优步长已不重要"的临界条件，量化调度自由度何时消失。
- **统一蒸馏目标框架（consolidated from Day 4）**：把一致性 / 分布匹配 / 拉直三目标放进一个可调节损失组合，系统扫描"权重 × 步数 × 质量 × likelihood"权衡面——当前文献各用各的目标，无人系统对比；若 CTM 的得分保持性质可迁移，将得到"少步 + 可控 + 可算 likelihood"的通用蒸馏范式。
- **似然审计（likelihood audit）**：对 DMD/ADD/reflow/CTM 做同模型同数据的 likelihood + 可控性 + 分布覆盖系统测量，给出"训练侧加速的真实代价曲线"——直接服务开放问题 #1，是实证友好、边界清晰的 thesis 入口。
- **CTM × AYS 最优跳长**：把失真度量推广到轨迹跳跃空间，为 CTM 类模型推导最优长跳排布。
- **指导感知调度**：失真度量引入 CFG 项，推导 guidance 下的最优调度（开放问题 #5 的直接攻击线）。

## Next Step

**推进到 flow-matching**（下周四起）：Day 4 已铺路——Rectified Flow（2209.03003）是 flow-matching 主题的第一篇深读候选，其 reflow 递归拉直数学是"训练侧重塑轨迹"与 flow matching 理论的连接点。建议阅读顺序：Rectified Flow / Flow Matching for Generative Modeling (Lipman 2022) / 与 diffusion 的统一视角。Sampling 主题遗留的最强 thesis 信号（蒸馏似然审计、统一蒸馏目标框架）可交叉输入 generative-models 后续主题。

---

*本笔记为 capstone 综合笔记（Day 5），未阅读新论文、未做网络检索；内容综合自 2026-08-06 / 08-13 / 08-20 / 08-27 四篇 daily note 与状态文件。*
