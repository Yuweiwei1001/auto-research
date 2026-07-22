# 数据格式定义

auto-research Skill 使用的所有数据文件格式定义。所有格式均为领域无关设计。

---

## 1. experiment_log.jsonl

每行一条 JSON 记录，追加写入。

```json
{
  "id": "EXP-007",
  "timestamp": "2026-07-11T14:30:00",
  "batch": 2,
  "round": 3,
  "method": "method_v3",
  "tier": "quick_screen",
  "hypothesis": "假设描述",
  "inspiration": [
    {"type": "paper", "title": "论文名", "section": "相关章节"},
    {"type": "deep_research", "section": "章节"}
  ],
  "changes": "修改了哪些文件、具体改了什么",
  "overrides": {
    "param1": "value1",
    "param2": "value2"
  },
  "metrics": {
    "primary_metric": 0.768,
    "secondary_metrics": {
      "metric_a": 0.792,
      "metric_b": 0.771
    }
  },
  "baseline_comparison": {
    "primary_baseline": {"primary_metric": 0.826, "diff": "-0.058"},
    "current_best": {"primary_metric": 0.821, "diff": "-0.053"}
  },
  "outcome": "improvement",
  "decision": "下一步决策描述",
  "error_log": null,
  "git_commit_before": "abc1234",
  "git_commit_after": "def5678",
  "config_file": "configs/method_config.yaml",
  "result_file": "experiments/results/EXP-007.json",
  "log_file": "experiments/results/EXP-007.log",
  "loop_mode": "closed",
  "seed": 42,
  "duration_minutes": 12.5
}
```

### outcome 枚举值

| 值 | 含义 |
|----|------|
| `improvement` | 主指标比 current_best 提升 ≥ `upgrade_threshold` |
| `marginal` | 主指标有提升但 < `upgrade_threshold` |
| `neutral` | 主指标基本持平（差异 < `neutral_threshold`） |
| `regression` | 主指标下降 ≥ `upgrade_threshold` |
| `failed` | 实验报错或崩溃 |
| `wild_card` | open 模式下的探索性实验，不受指标门控 |
| `early_stop` | 实验被早期停止规则终止 |

---

## 2. experiment_master.csv

人类可读的实验总表，每次实验追加一行。

### 表头

```csv
id,timestamp,batch,round,method,tier,hypothesis,inspiration,primary_metric,vs_baseline,outcome,loop_mode,seed,notes
```

### 字段说明

| 字段 | 说明 |
|------|------|
| id | 实验 ID（如 EXP-007） |
| timestamp | ISO 格式时间戳 |
| batch | 批次号（从 1 开始） |
| round | 批次内轮次号 |
| method | 方法名/版本 |
| tier | quick_screen / deep_verify / full_run |
| hypothesis | 假设简述（≤50 字符） |
| inspiration | 灵感来源简述 |
| primary_metric | 主指标值（由 research_domain.yaml 定义） |
| vs_baseline | 与主基线的差值 |
| outcome | improvement / marginal / neutral / regression / failed / wild_card / early_stop |
| loop_mode | closed / open |
| seed | 随机种子 |
| notes | 备注 |

---

## 3. method_lineage.yaml

方法谱系图，记录每个方法版本的来源和演变。

```yaml
methods:
  method_v3:
    origin: "v2 + 某论文核心思想"
    parent: [method_v2, paper_x]
    role: innovation  # innovation / baseline / ablation
    status: active  # active / superseded / dead_end / baseline / stable
    best_primary_metric: 0.768
    key_idea: "核心创新点描述"
    git_commit: "def5678"
    config_overrides:
      param1: value1
    notes: "观察备注"
    first_appeared: "EXP-007"
    experiments: ["EXP-007", "EXP-008", "EXP-012"]
```

### status 枚举值

| 值 | 含义 |
|----|------|
| `active` | 当前最新版本，仍在迭代 |
| `superseded` | 已被更新的版本替代 |
| `dead_end` | 证明无效，不再继续 |
| `baseline` | 基线方法，不参与迭代 |
| `stable` | 已稳定，不需要继续优化 |

---

## 4. 批次决策报告

保存在 `experiments/decisions/batch_{NNN}_summary.md`

```markdown
# 批次 {NNN} 汇总报告

**生成时间**: YYYY-MM-DD HH:MM
**实验数**: N (快速筛选 X + 深度验证 Y + wild card Z)
**总耗时**: X 小时
**循环模式**: closed | open
**预算状态**: 已用 M / 上限 N 实验，已用 H / 上限 T 小时

## 实验结果

| ID | 方法 | 假设 | Tier | Primary Metric | vs Baseline | Mode | 结果 |
|----|------|------|------|----------------|-------------|------|------|

## 最佳实验

**{exp_id}** — {method} — {target_metric}: {value}
- 假设: {hypothesis}
- 灵感来源: {inspiration}
- 关键改动: {changes}

## 趋势分析

{对整体趋势的分析}

## 验证报告

**验证 Agent 结论**: APPROVED | REJECTED | CONDITIONAL
**issues_found**: {N} 个 (critical: X, warning: Y, info: Z)

## 决策

**依据**: {触发的决策规则}
**行动**: {下一步具体行动}
**预期**: {对下一批次的预期}

## Git 状态

- 批次开始 commit: {hash}
- 批次结束 commit: {hash}
- 回滚次数: {N}
```

---

## 5. 结果文件 (experiments/results/{exp_id}.json)

由实验包装脚本自动生成。具体字段由 `experiment_runner.result_parser` 决定。

### 通用必需字段

```json
{
  "exp_id": "EXP-007",
  "method": "method_name",
  "timestamp": "ISO 时间戳",
  "status": "success | failed",
  "exit_code": 0,
  "metrics": {
    "primary_metric_name": 0.768
  },
  "overrides": {},
  "duration_minutes": 12.5,
  "seed": 42
}
```

### 可选扩展字段

```json
{
  "training_history": [...],
  "config_snapshot": {},
  "resource_usage": {
    "gpu_memory_mb": 8192,
    "cpu_percent": 85
  }
}
```

---

## 6. 全局工作日志 (experiments/work_log.md)

每次重要事件追加一条，Agent 在开始新批次前读最近 5-10 条。

### 格式

```markdown
## {YYYY-MM-DD} {事件类型}
- **关键发现**: 本次事件的核心结论
- **最佳实验**: {exp_id} — {method} — {metric}: {value}
- **已排除**: 本事件排除的方向及原因
- **下一批重点**: 建议的下一步行动
```

### 事件类型

| 类型 | 含义 |
|------|------|
| Batch 完成 | 一个实验批次结束 |
| 方向切换 | 触发停滞规则，换方向 |
| 基线刷新 | 重新运行基线实验 |
| 论文复现 | 复现了新论文 |
| 冷却开始 | 触发退化规则，进入冷却期 |
| 冷却结束 | 冷却期结束 |
| 目标达成 | 达到目标值且稳定 |

---

## 7. 循环契约 (experiments/loop_contract.md)

循环的"灵魂"文件，定义目标、边界和当前状态。

### 结构

```markdown
# 循环契约

## 研究目标
{一句话描述目标 + 成功标准}

## 当前阶段
{阶段名、当前方法版本、当前最佳指标、与基线差距}

## 已排除方向
{表格：方向、排除批次、原因}

## 待探索方向
{checklist 形式列出未探索的技术路线}

## 预算状态
{表格：指标、当前值、上限}

## 循环模式
{closed/open、触发方式、自动继续开关}

## 时间线
{表格：批次、日期、实验数、最佳指标、关键发现、决策}
```

### 更新规则

- 每个批次启动时：读取契约，了解当前状态和待探索方向
- 每个批次结束后：更新当前阶段、已排除方向、预算状态、时间线
- 触发方向切换时：更新待探索方向列表

---

## 8. research_domain.yaml（核心配置）

完整的领域配置文件格式，详见 `templates/` 目录下的示例。

### 顶层结构

```yaml
domain:           # 研究领域基本信息
key_variables:    # 关键实验变量
experiment_tiers: # 实验层级定义
baselines:        # 基线方法及其指标
methods:          # 可用方法注册
budget:           # 预算配置
loop:             # 循环模式配置
experiment_runner: # 实验适配器
literature_references: # 文献参考
innovation_sources:    # 创新来源优先级
```
