# Auto Research — Universal Autonomous Research Loop Skill

A domain-agnostic autonomous research循环引擎：读取实验历史 → 检索创新来源 → 制定假设 → 实现代码 → 跑实验 → 记录结果 → 分析决策 → 独立验证。
批量自主运行（默认 5-8 轮快速筛选 + 1-2 轮深度验证），汇总后向用户报告。

适用于任何可量化指标的实证研究领域：机器学习、NLP、计算机视觉、材料科学、生物信息学等。

## 触发命令

- `/auto-research` — 启动新批次
- `/auto-research continue` — 基于上一批次结果继续（如 auto_continue=true 则自动触发）
- `/auto-research report` — 只查看当前状态，不启动新实验
- `/auto-research contract` — 查看/编辑循环契约
- `/auto-research init` — 初始化新研究领域（从模板创建配置）

## 核心约束

1. **所有结果从文件读取**（`experiments/results/{exp_id}.json`），禁止读终端输出
2. **失败实验也记录**，标注 outcome=failed，包含 error_log
3. **每个假设必须标注灵感来源**（论文/报告/网络搜索/交叉融合）
4. **两阶段验证**：快速筛选 → 有希望的方向升级为深度验证
5. **Git 检查点**：每轮实验前 commit，失败可回滚
6. **实验包装器**：统一通过用户定义的 `experiment_runner` 运行实验
7. **预算熔断**：每次实验前后检查预算状态，超限则强制停止（规则 11-13）
8. **验证器分离**：生成器（执行 Agent）和验证器（验证 Agent）必须是不同的 Agent
9. **循环契约驱动**：每个批次先读契约、结束时更新契约
10. **领域无关**：所有领域特定配置集中在 `research_domain.yaml`，Skill 核心逻辑不含任何领域硬编码

## 文件结构

```
experiments/
├── research_domain.yaml         # 研究领域配置（目标、基线、文献、预算、循环模式、实验适配器）
├── loop_contract.md             # 循环契约（目标、边界、当前状态）
├── work_log.md                  # 全局工作日志（跨批次上下文延续）
├── experiment_log.jsonl         # 实验日志（追加写入，每行一条 JSON）
├── experiment_master.csv        # 人类可读总表
├── method_lineage.yaml          # 方法谱系图
├── results/                     # 实验结果文件
│   └── {exp_id}.json / .log
└── decisions/                   # 批次决策报告 + 验证报告
    └── batch_{NNN}_summary.md
```

## 主流程

### Phase 0: 读取上下文 + 预算预检

> **并行读取**：步骤 1-8 之间无依赖关系，应尽可能并行执行。

**上下文精简策略**（长程运行防止上下文溢出）：
- `work_log.md`：只读最后 5 条日志（约 50 行），不读全文
- `experiment_master.csv`：只读表头 + 最后 15 行，不读全部
- `DEEP_RESEARCH_*.md`：只读 TL;DR + Executive Summary（前 30 行）
- `method_lineage.yaml`：读全文（通常 < 150 行）
- `batch_XXX_summary.md`：只读最近一个批次的报告
- 实验结果 JSON：只在需要对比时按需读取

1. 读取 `experiments/research_domain.yaml` — 获取研究领域配置、基线、文献、**预算配置、循环模式、实验适配器**
2. 读取 `experiments/loop_contract.md` — 获取循环契约
3. 读取 `experiments/work_log.md` **最近 5-10 条** — 获取跨批次上下文
4. 读取 `experiments/experiment_master.csv` — 获取所有历史实验
5. 读取 `experiments/method_lineage.yaml` — 获取方法谱系和当前最佳
6. 读取最近一批次的 `experiments/decisions/batch_XXX_summary.md`（如有）
7. 读取 `DEEP_RESEARCH_*.md`（如有）— 获取 deep research 报告
8. 执行 `git status` 和 `git log --oneline -5` — 获取代码状态
9. **预算预检**：
   - 统计 `experiment_log.jsonl` 中总实验数 → 检查 `budget.max_total_experiments`
   - 检查 `loop_contract.md` 中 `冷却期剩余批次` → 如有冷却，限制实验数
10. **基线校准检查**：检查 baselines 的 `source` 字段。
    如果基线数字来自论文声称而非本地实测，标注需要复现刷新。
11. **动态加载基线值**：从 `research_domain.yaml` 读取当前基线指标，禁止硬编码。

### Phase 1: 检索创新来源 → 制定批次计划

**创新来源检索链**（按优先级）：

1. **本地资源（最快）**：
   - 读取 `DEEP_RESEARCH_*.md` 中相关章节
   - 读取领域文献笔记目录
   - 检查已复现论文的报告，提取可用技术模块

2. **网络搜索（补充）**：
   - 针对当前瓶颈搜索最新论文
   - 关注 `research_domain.yaml` 中定义的目标会议/期刊

3. **论文复现（深入理解）**：
   - 如果某篇论文的思路很有价值但细节不明，复现其方法
   - 复现产出可提供方法细节和实测数字

4. **交叉融合（深层）**：
   - 将不同论文的技术模块进行组合
   - 跨领域迁移学习

**制定批次计划**：

分析历史实验趋势，结合**循环契约中的待探索方向**，提出 5-8 个实验假设。每个假设包含：

```json
{
  "hypothesis": "假设描述",
  "inspiration_sources": [
    {"type": "paper", "title": "论文名", "section": "相关章节"}
  ],
  "tier": "quick_screen | deep_verify",
  "method": "方法名",
  "overrides": {"param1": "value1"},
  "expected_impact": "预期效果描述",
  "risk": "风险描述",
  "loop_mode": "closed | open"
}
```

**循环模式选择**：
- **closed 模式**（默认）：所有实验严格执行决策规则，每个实验必须过指标门控
- **open 模式**：允许 `open_slot_ratio`（默认 20%）的实验为 wild card，不受指标门控

**预算检查**：计划实验数不得超过 `budget.max_experiments_per_batch`。

### Phase 2: 实验执行

#### 并行策略

读取 `research_domain.yaml` 的 `experiment_runner.parallelism` 配置：
- `serial`（默认）：所有实验严格串行（适用于单 GPU 环境）
- `parallel:N`：最多 N 个实验并行（适用于多 GPU / 集群环境）

#### 执行流程

对每个实验，逐个（或并行）执行：

0. **预算检查**：
   - 检查 `batch_experiment_count` < `budget.max_experiments_per_batch`
   - 检查批次运行时间 < `budget.max_hours_per_batch`
   - 超限 → 停止执行，跳到 Phase 3
1. **Git checkpoint**：`git add -A; git commit -m "checkpoint: before {exp_id}"`
2. **派发子代理**（GeneralPurpose Agent）：详见 `references/subagent-template.md`
3. **接收结果**：子代理返回结构化 JSON
4. **记录结果**（主代理负责，子代理禁止修改 experiments/）：
   - 追加到 `experiments/experiment_log.jsonl`
   - 追加行到 `experiments/experiment_master.csv`
5. **更新计数器**：`batch_experiment_count += 1`
6. **Git 管理**：
   - 有效（improvement/neutral）：`git commit -m "exp {exp_id}: {outcome}"`
   - 无效（regression/failed）：`git checkout HEAD~1` 回滚
   - wild card（open 模式）：无论结果如何都保留

**实验升级机制**（仅 closed 模式）：
- 快速筛选结果中主指标提升 ≥ `upgrade_threshold` → 自动升级为深度验证
- 深度验证结果稳定（std < `confidence_threshold`）→ 升级为完整运行

### Phase 3: 批次汇总 + 决策

1. 对比本批次所有实验的 metrics
2. 识别最佳实验和最差实验
3. 分析趋势：哪些方向有效？哪些停滞？
4. **论文对标**：将方法与已复现论文实测数字做对比
5. 写入 `experiments/decisions/batch_{NNN}_summary.md`
6. 应用决策规则确定下一步行动（详见 `references/decision-rules.md`）

### Phase 3.5: 独立验证（验证器 Agent）

> **核心原则**：生成器（Phase 2 的执行 Agent）和验证器必须是不同的 Agent。

派发一个**只读验证 Agent**（详见 `references/verifier-agent-template.md`），独立审查：

1. **指标一致性**：experiment_log 中的数字 vs results JSON 中的原始数据
2. **决策规则应用**：触发条件是否正确、优先级是否正确执行
3. **预算合规**：是否超出预算限制
4. **代码变更审查**：git diff 是否与假设描述一致
5. **实验完整性**：结果文件是否完整、失败实验是否有 error_log
6. **方法谱系一致性**：lineage 中的指标与实验结果是否匹配

**验证结论**：
- `APPROVED`：通过，继续 Phase 4
- `REJECTED`：有 critical issue，主代理修正后重新提交验证
- `CONDITIONAL`：通过但有 ≥ 3 个 warning，需在下一批次前处理

### Phase 3.6: 更新循环状态

1. **更新循环契约**（`experiments/loop_contract.md`）
2. **追加全局工作日志**（`experiments/work_log.md`）
3. **处理冷却期**：如触发退化规则，设置冷却期

### Phase 4: 向用户展示报告

输出格式：

```markdown
## 批次 {NNN} 汇总报告

**实验数**: {N} (快速筛选 {X} + 深度验证 {Y} + wild card {Z})
**最佳实验**: {exp_id} — {method} — {target_metric}: {value}
**vs 基线**: {primary_baseline} {value} ({diff})
**循环模式**: {closed | open}
**预算**: 已用 {M}/{budget_max} 实验，已用 {H}h/{budget_hours}h

### 实验结果表
| ID | 方法 | 假设 | Tier | Best | Last | {Metric} | vs Baseline | Mode | 结果 |
|----|------|------|------|------|------|----------|-------------|------|------|

### 验证报告
**结论**: APPROVED | CONDITIONAL
**Issues**: {N} 个 (critical: X, warning: Y, info: Z)

### 趋势分析
...

### 决策
{基于决策规则的下一步建议}

### 自动继续
{如果 auto_continue=true 且决策为"继续"，自动启动下一批次}
```

## 实验运行方式

### 实验适配器（Experiment Adapter）

所有实验通过 `research_domain.yaml` 中定义的适配器运行：

```yaml
experiment_runner:
  # 环境准备命令（每次实验前执行）
  env_setup: "conda activate myenv"  # 或 "source venv/bin/activate" 或留空
  
  # 实验运行命令模板
  # 可用占位符: {exp_id}, {method}, {rounds}, {seed}, {overrides}, {config}, {script}
  run_command: "python scripts/run_experiment.py --exp-id {exp_id} --method {method} --rounds {rounds} --seed {seed} --override {overrides}"
  
  # 结果文件路径模板
  result_path: "experiments/results/{exp_id}.json"
  log_path: "experiments/results/{exp_id}.log"
  
  # 结果解析方式
  result_parser: "json"  # json / csv / regex / custom
  
  # 并行策略
  parallelism: "serial"  # serial / parallel:N
  
  # 超时配置（分钟）
  timeout:
    quick_screen: 30
    deep_verify: 60
    full_run: 120
```

### 创建新方法

当现有方法都不适合时，子代理可以创建全新方法：

1. 按项目结构创建新方法代码
2. 创建对应的运行脚本和配置文件
3. 在 `method_lineage.yaml` 中注册新方法节点
4. 通过 `experiment_runner.run_command` 运行

### 多种子重复验证

当深度验证显示有希望的结果时，触发多种子验证：
- 同一配置跑 3+ 个不同种子
- 汇总时计算 mean ± std
- 如果 std < `confidence_threshold`，视为稳定

## 长程运行与断点续跑

### 长程运行配置

当 `auto_continue=true` 时，批次自动连跑，无需用户干预。
停止条件由预算熔断规则和退化规则自动触发。

### 断点续跑

如果会话中断，使用 `/auto-research continue` 恢复：
1. Phase 0 自动从 `experiment_log.jsonl` 读取已完成实验
2. 检查 `loop_contract.md` 中的当前批次号
3. 检查 git 状态：如有未提交的实验代码，先 commit 再继续
4. 从下一个未完成的假设继续执行

**关键保障**：
- 每个实验前有 Git checkpoint，崩溃不丢失代码
- `experiment_log.jsonl` 追加写入，已完成实验不丢失
- `loop_contract.md` 记录批次进度，可精确续跑

## 参考文件

- `references/subagent-template.md` — 子代理 prompt 模板
- `references/verifier-agent-template.md` — 验证 Agent prompt 模板
- `references/data-formats.md` — JSON/YAML 格式定义
- `references/decision-rules.md` — 决策规则详表（含预算熔断规则）
