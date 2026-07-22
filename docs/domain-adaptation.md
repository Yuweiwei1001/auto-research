# 领域适配指南

## 核心原则

Auto-Research 的所有领域特定信息都集中在 `research_domain.yaml` 一个文件中。
适配新领域 = 填写这个文件 + 准备实验脚本。Skill 核心逻辑无需任何修改。

---

## 适配清单

### 必须完成

- [ ] 定义 `domain`（研究领域、主指标、目标值）
- [ ] 定义 `baselines`（至少 1 个基线方法及其实测指标）
- [ ] 定义 `experiment_runner`（如何运行实验、如何读取结果）
- [ ] 定义 `experiment_tiers`（快筛/深验/全量的时间配置）
- [ ] 定义 `budget`（预算限制）
- [ ] 准备实验脚本（接受参数 → 运行 → 输出 JSON）

### 推荐完成

- [ ] 定义 `key_variables`（关键实验变量）
- [ ] 填写 `literature_references`（相关文献）
- [ ] 定义 `methods`（可用方法注册）
- [ ] 配置 `innovation_sources`（创新来源）

---

## 不同领域的适配示例

### 1. 深度学习（训练-评估循环）

**特点**：需要 GPU、训练时间长、有 epoch 概念

```yaml
experiment_tiers:
  quick_screen:
    num_epochs: 10
    timeout_minutes: 20
  deep_verify:
    num_epochs: 50
    timeout_minutes: 90
  full_run:
    num_epochs: 100
    timeout_minutes: 180

experiment_runner:
  env_setup: "conda activate dl"
  run_command: "python train.py --exp-id {exp_id} --epochs {rounds} --seed {seed}"
  parallelism: "serial"  # 单 GPU
```

### 2. NLP（预训练模型微调）

**特点**：epoch 少但每 epoch 时间长、多种子敏感

```yaml
experiment_tiers:
  quick_screen:
    num_epochs: 3
    timeout_minutes: 30
  deep_verify:
    num_epochs: 10
    timeout_minutes: 120

experiment_runner:
  env_setup: "conda activate nlp"
  run_command: "python finetune.py --exp-id {exp_id} --epochs {rounds} --lr {overrides}"
  parallelism: "parallel:2"  # 多 GPU
```

### 3. 仿真/数值计算（无训练循环）

**特点**：参数扫描、可高度并行、结果确定性

```yaml
experiment_tiers:
  quick_screen:
    num_samples: 100
    timeout_minutes: 10
  deep_verify:
    num_samples: 1000
    timeout_minutes: 60
  full_run:
    num_samples: 10000
    timeout_minutes: 240

experiment_runner:
  env_setup: ""
  run_command: "python simulate.py --exp-id {exp_id} --params {overrides}"
  parallelism: "parallel:8"  # 集群并行
  result_parser: "csv"
```

### 4. 强化学习

**特点**：reward 曲线、需要多 episode、方差大

```yaml
domain:
  target_metric: "mean_reward_100ep"
  confidence_threshold: 0.05  # RL 方差大，阈值放宽

experiment_tiers:
  quick_screen:
    num_episodes: 1000
    timeout_minutes: 30
  deep_verify:
    num_episodes: 5000
    timeout_minutes: 120

experiment_runner:
  env_setup: "conda activate rl"
  run_command: "python train_rl.py --exp-id {exp_id} --episodes {rounds} --seed {seed}"
```

### 5. 系统研究（性能基准）

**特点**：指标为延迟/吞吐量、需要多次运行取平均

```yaml
domain:
  target_metric: "p99_latency_ms"
  target_value: 10.0  # 越低越好（注意：当前假设越高越好）

experiment_tiers:
  quick_screen:
    num_requests: 10000
    timeout_minutes: 5
  deep_verify:
    num_requests: 100000
    timeout_minutes: 30

experiment_runner:
  env_setup: ""
  run_command: "python benchmark.py --exp-id {exp_id} --config {overrides}"
  parallelism: "serial"
```

### 6. 计算化学/材料科学

**特点**：DFT 计算、长时间运行、集群提交

```yaml
domain:
  target_metric: "formation_energy"
  target_value: -2.5  # eV/atom

experiment_tiers:
  quick_screen:
    kpoints: "2x2x2"
    timeout_minutes: 60
  deep_verify:
    kpoints: "4x4x4"
    timeout_minutes: 240
  full_run:
    kpoints: "6x6x6"
    timeout_minutes: 720

experiment_runner:
  env_setup: "module load vasp"
  run_command: "python run_dft.py --exp-id {exp_id} --params {overrides}"
  parallelism: "serial"  # 集群调度
```

---

## 实验脚本接口规范

你的实验脚本需要满足以下接口：

### 输入（命令行参数）

```bash
python your_script.py \
  --exp-id EXP-001 \        # 实验唯一标识
  --method proposed \        # 方法名
  --seed 42 \               # 随机种子
  --rounds 50 \             # 轮数/epochs（可选）
  --override param1=val1    # 参数覆盖（可选）
```

### 输出（JSON 结果文件）

```json
{
  "exp_id": "EXP-001",
  "method": "proposed",
  "timestamp": "2026-01-01T12:00:00",
  "status": "success",
  "exit_code": 0,
  "metrics": {
    "your_target_metric": 0.87
  },
  "duration_minutes": 15.3,
  "seed": 42
}
```

### 失败时

```json
{
  "exp_id": "EXP-001",
  "method": "proposed",
  "status": "failed",
  "exit_code": 1,
  "error": "CUDA out of memory",
  "metrics": null
}
```

---

## 常见问题

### Q: 我的指标是"越小越好"（如 loss、latency），怎么办？

当前版本假设指标越大越好。临时解决方案：
- 取倒数：`metric = 1 / loss`
- 取负数：`metric = -latency`
- 在实验脚本中做转换后输出

### Q: 我的实验需要提交到 Slurm 集群？

```yaml
experiment_runner:
  env_setup: ""
  run_command: "sbatch --wait run_job.sh {exp_id} {method} {seed}"
  timeout:
    quick_screen: 60  # 包含排队时间
```

### Q: 我有多个数据集需要分别测试？

将数据集作为 `key_variables`：

```yaml
key_variables:
  - name: dataset
    values: ["dataset_a", "dataset_b", "dataset_c"]
    description: "测试数据集"
    config_path: "data.dataset_name"
```

### Q: 如何从零开始（没有基线）？

1. 先手动运行一个简单方法作为基线
2. 将结果填入 `baselines`
3. 或者设置 `target_value` 为一个合理的预期值，`baselines` 留空
