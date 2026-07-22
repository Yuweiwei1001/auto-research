# 入门指南

## 5 分钟快速上手

### Step 1: 安装 Skill

将 auto-research 复制到你的项目中：

```bash
# 在你的研究项目根目录
mkdir -p .agents/skills/auto-research/references

# 复制核心文件
cp /path/to/auto-research/SKILL.md .agents/skills/auto-research/
cp /path/to/auto-research/references/* .agents/skills/auto-research/references/
```

### Step 2: 初始化实验目录

```bash
# 方式 A：使用初始化脚本（推荐）
python /path/to/auto-research/scripts/init_research.py --template ml_experiment

# 方式 B：手动创建
mkdir -p experiments/results experiments/decisions
cp /path/to/auto-research/templates/ml_experiment/research_domain.yaml experiments/
```

### Step 3: 配置你的领域

编辑 `experiments/research_domain.yaml`，**必须修改**的字段：

```yaml
domain:
  name: "你的研究方向"           # ← 改这里
  target_metric: "accuracy"     # ← 改这里（你的主指标名）
  target_value: 0.90            # ← 改这里（你的目标值）

baselines:                      # ← 改这里（你的基线方法）
  - method: Your-Baseline
    metrics:
      accuracy: 0.85

experiment_runner:
  env_setup: "conda activate yourenv"   # ← 改这里
  run_command: "python your_script.py --exp-id {exp_id} --seed {seed}"  # ← 改这里
```

### Step 4: 准备实验脚本

你的实验脚本需要：
1. 接受命令行参数（exp-id, method, seed 等）
2. 运行实验
3. 输出 JSON 结果文件到 `experiments/results/{exp_id}.json`

最简结果文件格式：

```json
{
  "exp_id": "EXP-001",
  "method": "proposed",
  "status": "success",
  "metrics": {
    "accuracy": 0.87
  }
}
```

### Step 5: 启动

在 AI 助手中输入：

```
/auto-research
```

Agent 会自动：
1. 读取你的配置和历史
2. 生成 5-8 个实验假设
3. 逐个运行实验
4. 分析结果并做决策
5. 向你报告

---

## 常用命令

| 命令 | 功能 |
|------|------|
| `/auto-research` | 启动新批次 |
| `/auto-research continue` | 继续上一批次 |
| `/auto-research report` | 查看当前状态 |
| `/auto-research contract` | 查看/编辑循环契约 |

---

## 第一次运行的建议

1. **先跑基线**：确保 `baselines` 中的指标是本地实测的
2. **小预算开始**：`max_experiments_per_batch: 5`，观察循环是否正常
3. **closed 模式**：先用严格门控，熟悉后再切 open
4. **auto_continue: false**：先手动确认每批次，信任后再开自动

---

## 故障排除

### Agent 找不到 Skill

确保文件路径正确：
```
your-project/
└── .agents/skills/auto-research/
    ├── SKILL.md
    └── references/
        ├── data-formats.md
        ├── decision-rules.md
        ├── subagent-template.md
        └── verifier-agent-template.md
```

### 实验运行失败

1. 手动运行 `experiment_runner.run_command`，确认能正常执行
2. 确认结果文件路径与 `result_path` 配置一致
3. 确认 JSON 格式正确（必需字段：exp_id, method, status, metrics）

### 预算耗尽

修改 `research_domain.yaml` 中的 `budget` 配置，或重置 `experiment_log.jsonl`。
