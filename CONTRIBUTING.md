# Contributing to Auto-Research

感谢你对 Auto-Research 项目的关注！欢迎任何形式的贡献。

## 贡献方向

### 高优先级

- **新增领域模板**：为更多研究领域提供开箱即用的 `research_domain.yaml` 模板
  - 生物信息学（基因组学、蛋白质结构预测）
  - 材料科学（DFT 计算、分子动力学）
  - 经济学/社会科学（计量模型、因果推断）
  - 系统研究（性能基准、编译器优化）
  - 强化学习（reward 优化）
  
- **实验适配器扩展**：支持更多实验运行方式
  - Slurm/PBS 集群提交
  - Docker 容器化运行
  - Jupyter Notebook 执行
  - API 调用型实验（如 LLM 评估）

- **决策规则改进**：基于实际使用反馈优化规则引擎

### 中优先级

- 文档完善和翻译（英文 README）
- 更多使用示例
- 初始化向导改进
- CI/CD 集成模板（GitHub Actions）

### 低优先级

- 可视化仪表板
- 实验结果自动绘图
- 论文写作辅助集成

## 开发指南

### 项目结构约定

```
auto-research/
├── SKILL.md              # 核心 Skill 定义（修改需慎重，影响所有用户）
├── references/           # 参考文件（Agent 运行时读取）
├── templates/            # 领域模板（新增模板放这里）
├── examples/             # 使用示例
├── scripts/              # 辅助脚本
└── docs/                 # 文档
```

### 新增领域模板

1. 在 `templates/` 下创建新目录（如 `templates/bioinformatics/`）
2. 创建 `research_domain.yaml`，遵循 `templates/general/` 的 schema
3. 确保所有必填字段都有注释说明
4. 在 README.md 的模板表格中添加条目

### 修改核心 Skill

修改 `SKILL.md` 或 `references/` 下的文件时：

1. 确保改动是**领域无关的**（不引入任何特定领域的硬编码）
2. 新增的占位符必须在 `subagent-template.md` 中说明来源
3. 新增的决策规则必须在 `decision-rules.md` 中完整定义
4. 测试：至少在一个领域示例上验证改动不会破坏流程

### 提交规范

- 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式
- 类型：`feat` / `fix` / `docs` / `refactor` / `test`
- 示例：`feat: add bioinformatics domain template`

## 行为准则

- 尊重所有贡献者
- 建设性讨论
- 以项目利益为先

## 许可证

贡献即表示你同意你的贡献以 [MIT License](LICENSE) 发布。
