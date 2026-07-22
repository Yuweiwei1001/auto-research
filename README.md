# Auto-Research: Universal Autonomous Research Loop

<div align="center">

**🔬 AI 驱动的全自动科研循环引擎**

*假设生成 → 实验执行 → 结果分析 → 独立验证 → 决策升级*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Agent](https://img.shields.io/badge/AI-Agent-blue)](SKILL.md)

</div>

---

## 这是什么？

Auto-Research 是一个**领域无关的自主科研循环 Skill**，设计为 AI 编码助手（如 Qoder、Claude Code、Cursor 等）的插件。它将科研实验的完整生命周期——从假设生成到独立验证——编排为一个可自动运行的闭环，让 AI Agent 像研究员一样迭代探索。

**核心理念**：Loop Engineering（循环工程）—— 不是让 AI 一次性给出答案，而是让 AI 在结构化的实验循环中持续迭代、自我纠错、积累知识。

### 核心特性

| 特性 | 描述 |
|------|------|
| 🔄 **闭环循环** | 假设→实验→分析→决策→下一轮，全自动 |
| 🛡️ **验证器分离** | 生成器和验证器是不同 Agent，防止自我欺骗 |
| 💰 **预算熔断** | 实验数/时间/连续失败多维预算控制 |
| 📋 **循环契约** | 持久化目标、边界、状态，支持断点续跑 |
| 🌐 **领域无关** | 所有领域配置集中在一个 YAML 文件中 |
| 🔀 **Open/Closed 模式** | 严格门控 vs 允许探索性 wild card |
| 📊 **方法谱系** | 自动追踪方法演化、继承关系 |
| ⏸️ **断点续跑** | 会话中断后精确恢复 |
| 🎯 **两阶段验证** | 快筛→深验→全量，渐进式投入资源 |

---

## 快速开始

### 前置条件

- 支持 Skill 的 AI 编码助手（Qoder / Claude Code / Cursor 等）
- Git（用于实验检查点和版本管理）
- 你的研究项目的实验运行脚本

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/Yuweiwei1001/auto-research.git
cd auto-research

# 2. 将 Skill 文件复制到你的项目中
# 方式 A：作为子目录
cp -r . /path/to/your-project/.agents/skills/auto-research/

# 方式 B：直接复制核心文件
mkdir -p /path/to/your-project/.agents/skills/auto-research/references
cp SKILL.md /path/to/your-project/.agents/skills/auto-research/
cp references/* /path/to/your-project/.agents/skills/auto-research/references/
```

### 初始化研究领域

```bash
# 在你的项目中创建实验目录
mkdir -p experiments/results experiments/decisions

# 从模板创建配置（选择一个适合你领域的模板）
cp .agents/skills/auto-research/templates/general/research_domain.yaml experiments/research_domain.yaml

# 编辑配置文件，填入你的领域信息
# 必须修改的字段：
#   - domain.name / description / target_metric / target_value
#   - baselines（你的基线方法和指标）
#   - experiment_runner.run_command（你的实验运行命令）
```

### 启动研究循环

在 AI 助手中输入：

```
/auto-research
```

---

## 配置指南

### 核心配置文件：`research_domain.yaml`

这是唯一需要修改的领域配置文件。完整字段说明：

```yaml
domain:
  name: "研究领域名称"
  target_metric: "accuracy"     # 你的主指标
  target_value: 0.90            # 目标值

experiment_runner:
  env_setup: "conda activate myenv"
  run_command: "python run.py --exp-id {exp_id} --method {method} --seed {seed}"
  result_path: "experiments/results/{exp_id}.json"
  parallelism: "serial"         # 或 "parallel:4"
```

### 可用模板

| 模板 | 适用场景 | 路径 |
|------|---------|------|
| `general` | 任何可量化研究 | `templates/general/` |
| `ml_experiment` | 深度学习/ML 训练 | `templates/ml_experiment/` |
| `nlp_benchmark` | NLP 基准测试 | `templates/nlp_benchmark/` |

### 实验结果文件格式

你的实验脚本需要输出一个 JSON 结果文件：

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

---

## 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                    Auto-Research Loop                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 0: 读取上下文 + 预算预检                           │
│      ↓                                                   │
│  Phase 1: 检索创新来源 → 生成 5-8 个假设                  │
│      ↓                                                   │
│  Phase 2: 串行/并行执行实验（子代理）                      │
│      ↓                                                   │
│  Phase 3: 批次汇总 + 决策规则引擎                         │
│      ↓                                                   │
│  Phase 3.5: 独立验证（验证器 Agent）                      │
│      ↓                                                   │
│  Phase 3.6: 更新循环契约 + 工作日志                       │
│      ↓                                                   │
│  Phase 4: 向用户报告 / 自动继续下一批次                   │
│      ↓                                                   │
│  └──→ 回到 Phase 0（如 auto_continue=true）              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 决策规则引擎

15 条结构化决策规则自动驱动研究方向：

- **持续改进** → 继续微调
- **停滞** → 换方向
- **退化** → 回滚 + 冷却
- **达成目标** → 多设置验证
- **预算耗尽** → 强制停止

详见 [decision-rules.md](references/decision-rules.md)

---

## 使用示例

### 示例 1：联邦学习研究

```yaml
# experiments/research_domain.yaml
domain:
  name: "多模态联邦学习"
  target_metric: "final5_avg"
  target_value: 0.83

experiment_runner:
  env_setup: "conda activate flower"
  run_command: "python run_fl.py --exp-id {exp_id} --rounds {rounds}"
  parallelism: "serial"  # 单 GPU
```

完整示例见 [examples/federated_learning/](examples/federated_learning/)

### 示例 2：NLP 情感分析

```yaml
domain:
  name: "多模态情感分析"
  target_metric: "weighted_f1"
  target_value: 0.82

experiment_runner:
  env_setup: "conda activate nlp"
  run_command: "python run_sentiment.py --exp-id {exp_id} --epochs {rounds}"
  parallelism: "parallel:2"  # 双 GPU
```

完整示例见 [examples/nlp_sentiment/](examples/nlp_sentiment/)

### 示例 3：材料科学（非 ML）

```yaml
domain:
  name: "钙钛矿太阳能电池效率优化"
  target_metric: "power_conversion_efficiency"
  target_value: 0.26

experiment_runner:
  env_setup: ""
  run_command: "python simulate.py --exp-id {exp_id} --params {overrides}"
  result_parser: "csv"
  parallelism: "parallel:8"  # 集群并行仿真
```

---

## 项目结构

```
auto-research/
├── SKILL.md                          # 核心 Skill 定义（AI Agent 读取此文件）
├── README.md                         # 本文件
├── LICENSE                           # MIT 许可证
├── CONTRIBUTING.md                   # 贡献指南
├── references/                       # Skill 参考文件
│   ├── data-formats.md               # 数据格式定义
│   ├── decision-rules.md             # 决策规则详表
│   ├── subagent-template.md          # 实验执行子代理模板
│   └── verifier-agent-template.md    # 验证 Agent 模板
├── templates/                        # 领域配置模板
│   ├── general/                      # 通用模板
│   ├── ml_experiment/                # ML 实验模板
│   └── nlp_benchmark/                # NLP 基准模板
├── examples/                         # 使用示例
│   ├── federated_learning/           # 联邦学习示例
│   └── nlp_sentiment/                # NLP 情感分析示例
├── scripts/                          # 辅助脚本
│   └── init_research.py              # 项目初始化脚本
└── docs/                             # 详细文档
    ├── getting-started.md            # 入门指南
    ├── configuration.md              # 配置详解
    └── domain-adaptation.md          # 领域适配指南
```

---

## 与其他工具的区别

| 特性 | Auto-Research | AI Scientist | 手动实验 |
|------|:---:|:---:|:---:|
| 结构化实验治理 | ✅ | ❌ | ❌ |
| 验证器分离 | ✅ | ❌ | 可选 |
| 预算熔断 | ✅ | ❌ | 手动 |
| 断点续跑 | ✅ | ❌ | N/A |
| 领域无关 | ✅ | 部分 | ✅ |
| 方法谱系追踪 | ✅ | ❌ | 手动 |
| 决策规则引擎 | ✅ | ❌ | 人工判断 |
| 循环契约 | ✅ | ❌ | ❌ |

---

## 适配你的研究领域

只需 3 步：

1. **选择模板** → 从 `templates/` 复制最接近的模板
2. **填写配置** → 修改 `research_domain.yaml` 中的领域信息
3. **准备实验脚本** → 确保你的脚本能接受参数并输出 JSON 结果

详细指南见 [docs/domain-adaptation.md](docs/domain-adaptation.md)

---

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

主要贡献方向：
- 新增领域模板（生物信息学、材料科学、经济学等）
- 改进决策规则
- 增加实验适配器类型（Slurm 集群、Docker 容器等）
- 文档和示例完善

---

## 许可证

[MIT License](LICENSE)

---

## 引用

如果本项目对你的研究有帮助，请引用：

```bibtex
@software{auto_research_2026,
  title = {Auto-Research: Universal Autonomous Research Loop},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/Yuweiwei1001/auto-research}
}
```

---

## 致谢

本项目的设计灵感来源于实际的多模态联邦学习科研实践（74+ 次自动化实验迭代），
经过从领域特定到通用化的抽象提炼而成。
