# 配置详解

## research_domain.yaml 完整字段说明

### domain（必填）

```yaml
domain:
  name: string          # 研究领域名称（用于报告标题）
  description: string   # 一句话描述研究问题
  target_metric: string # 主指标名（必须与结果 JSON 中的 key 一致）
  target_value: float   # 目标值（超过此值 + 稳定 = 成功）
  confidence_threshold: float  # std < 此值视为稳定（默认 0.01）
```

**注意**：`target_metric` 的值必须与你的实验结果 JSON 中 `metrics` 对象的 key 完全匹配。

### decision_thresholds（可选）

```yaml
decision_thresholds:
  upgrade_threshold: 0.01       # 提升 ≥ 此值 → improvement
  stagnation_threshold: 0.005   # 连续提升 < 此值 → 停滞
  neutral_threshold: 0.003      # 差异 < 此值 → neutral
```

如不配置，使用上述默认值。对于指标量级不同的领域需要调整：
- 指标范围 0-1：默认值适用
- 指标范围 0-100：乘以 100（如 upgrade_threshold: 1.0）
- 指标为损失值（越小越好）：需要反转逻辑（暂不支持，计划中）

### key_variables（推荐）

定义实验中的关键变量，用于扩展验证（规则 9/10）：

```yaml
key_variables:
  - name: string        # 变量名
    values: list        # 可选值列表
    description: string # 描述
    config_path: string # 在实验配置中的路径（用于 --override）
```

### experiment_tiers（必填）

定义实验的层级，每层对应不同的资源投入：

```yaml
experiment_tiers:
  quick_screen:
    timeout_minutes: int    # 超时时间
    description: string     # 描述
    # 可添加任何领域特定参数（如 num_rounds, num_epochs 等）
  deep_verify:
    timeout_minutes: int
    description: string
  full_run:
    timeout_minutes: int
    description: string
```

### baselines（必填）

基线方法列表，Agent 会用这些值做对比：

```yaml
baselines:
  - method: string      # 方法名
    config: string      # 配置文件路径
    script: string      # 运行脚本路径
    metrics:
      metric_name: float  # 指标值（key 必须与 target_metric 一致）
    source: string      # 来源说明（"本地实测" 或 "论文声称"）
```

**重要**：`source` 为 "论文声称" 时，Agent 会标注需要复现验证。

### methods（必填）

注册所有可用的实验方法：

```yaml
methods:
  method_name:
    script: string    # 运行脚本
    config: string    # 配置文件
```

### budget（必填）

预算控制，防止无限运行：

```yaml
budget:
  max_experiments_per_batch: int   # 单批次上限（推荐 10-15）
  max_hours_per_batch: int         # 单批次时间上限（小时）
  max_total_experiments: int       # 全局上限（推荐 100-300）
  max_consecutive_failures: int    # 连续失败上限（推荐 2-3）
  cooldown_after_regression: int   # 退化后冷却批次数
  cooldown_experiment_cap: int     # 冷却期单批次上限
```

### loop（必填）

循环模式配置：

```yaml
loop:
  mode: "closed" | "open"    # closed=严格门控, open=允许 wild card
  auto_continue: bool         # 是否自动启动下一批次
  trigger: "manual"           # 触发方式（目前仅支持 manual）
  open_slot_ratio: float      # open 模式下 wild card 比例（默认 0.2）
```

**模式选择建议**：
- 初期/资源有限 → `closed`
- 中后期/需要探索 → `open`
- 整晚运行 → `auto_continue: true`

### experiment_runner（必填，核心）

定义如何运行实验：

```yaml
experiment_runner:
  env_setup: string       # 环境激活命令（如 "conda activate env"）
  run_command: string     # 运行命令模板
  result_path: string     # 结果文件路径模板
  log_path: string        # 日志文件路径模板
  result_parser: string   # 解析方式: json / csv / regex
  parallelism: string     # "serial" 或 "parallel:N"
  timeout:                # 各层级超时
    quick_screen: int
    deep_verify: int
    full_run: int
```

**run_command 可用占位符**：

| 占位符 | 含义 |
|--------|------|
| `{exp_id}` | 实验 ID |
| `{method}` | 方法名 |
| `{rounds}` | 轮数/epochs |
| `{seed}` | 随机种子 |
| `{overrides}` | 参数覆盖（key=value 格式） |
| `{config}` | 配置文件路径 |
| `{script}` | 脚本路径 |

### literature_references（推荐）

相关文献列表，供 Agent 检索创新来源：

```yaml
literature_references:
  - title: string
    authors: string
    venue: string
    experiment_setup: string   # 实验设置
    key_technique: string      # 核心技术
    code_url: string | null    # 代码链接
    local_file: string | null  # 本地 PDF 路径
```

### innovation_sources（可选）

创新来源优先级配置：

```yaml
innovation_sources:
  priority:
    - level: 1
      name: "本地资源"
      sources: [list of paths/descriptions]
    - level: 2
      name: "网络搜索"
      sources: [list of venues/keywords]
    - level: 3
      name: "交叉融合"
      sources: [list of combination ideas]
```

---

## 配置文件最佳实践

1. **先小后大**：初始 `max_total_experiments: 50`，验证流程后再扩大
2. **基线先行**：确保 baselines 的指标是本地实测的
3. **单一指标**：`target_metric` 只设一个，多目标用 secondary_metrics
4. **合理超时**：根据实际实验时间设置，留 20% 余量
5. **版本控制**：将 `research_domain.yaml` 纳入 Git 管理
