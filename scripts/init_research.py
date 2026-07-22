#!/usr/bin/env python3
"""
Auto-Research 项目初始化脚本

用法:
    python init_research.py --domain "研究领域名称" --metric "accuracy" --target 0.90
    python init_research.py --template ml_experiment
    python init_research.py --template general --interactive

功能:
    1. 创建 experiments/ 目录结构
    2. 从模板生成 research_domain.yaml
    3. 创建 loop_contract.md 初始文件
    4. 创建 method_lineage.yaml 初始文件
    5. 创建 work_log.md 初始文件
    6. 初始化 experiment_log.jsonl 和 experiment_master.csv
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

AVAILABLE_TEMPLATES = ["general", "ml_experiment", "nlp_benchmark"]


def create_directory_structure(base_dir: Path):
    """创建实验目录结构"""
    dirs = [
        base_dir / "experiments",
        base_dir / "experiments" / "results",
        base_dir / "experiments" / "decisions",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录: {d.relative_to(base_dir)}/")


def copy_template(template_name: str, base_dir: Path):
    """从模板复制 research_domain.yaml"""
    template_path = TEMPLATES_DIR / template_name / "research_domain.yaml"
    target_path = base_dir / "experiments" / "research_domain.yaml"

    if not template_path.exists():
        print(f"  ✗ 模板不存在: {template_path}")
        print(f"    可用模板: {', '.join(AVAILABLE_TEMPLATES)}")
        sys.exit(1)

    if target_path.exists():
        print(f"  ⚠ 配置已存在: {target_path.relative_to(base_dir)}")
        response = input("    覆盖? (y/N): ").strip().lower()
        if response != 'y':
            print("    跳过")
            return

    import shutil
    shutil.copy2(template_path, target_path)
    print(f"  ✓ 创建配置: experiments/research_domain.yaml (模板: {template_name})")


def create_loop_contract(base_dir: Path, domain_name: str = "你的研究领域"):
    """创建循环契约初始文件"""
    target = base_dir / "experiments" / "loop_contract.md"
    if target.exists():
        print(f"  ⚠ 已存在: experiments/loop_contract.md，跳过")
        return

    content = f"""# 循环契约 — Auto-Research Loop Contract

> 每个批次启动时先读此文件，结束时更新此文件。

---

## 研究目标

{{在此填写你的研究目标}}

**成功标准**: {{主指标}} > {{目标值}} 且 std < confidence_threshold
**当前状态**: 🆕 初始化

---

## 当前阶段

- **阶段名**: Phase 0 — 初始化
- **当前方法版本**: 无
- **当前最佳**: 无
- **差距**: 待基线实验确定

---

## 已排除方向

| 方向 | 排除批次 | 原因 |
|------|---------|------|
| （暂无） | — | — |

---

## 待探索方向

- [ ] {{在此列出你计划探索的技术路线}}

---

## 预算状态

| 指标 | 当前值 | 上限 |
|------|--------|------|
| 本批次实验数 | 0 | 见 research_domain.yaml |
| 全局累计实验数 | 0 | 见 research_domain.yaml |
| 冷却期剩余批次 | 0 | — |

---

## 循环模式

- **模式**: closed
- **触发方式**: manual
- **自动继续**: 关闭

---

## 时间线

| 批次 | 日期 | 实验数 | 最佳指标 | 关键发现 | 决策 |
|------|------|--------|---------|---------|------|
| — | {datetime.now().strftime('%Y-%m-%d')} | 0 | — | 项目初始化 | — |

---

## 更新日志

- **创建时间**: {datetime.now().strftime('%Y-%m-%d')}
- **最后更新**: {datetime.now().strftime('%Y-%m-%d')} (初始化)
"""
    target.write_text(content, encoding="utf-8")
    print(f"  ✓ 创建: experiments/loop_contract.md")


def create_method_lineage(base_dir: Path):
    """创建方法谱系初始文件"""
    target = base_dir / "experiments" / "method_lineage.yaml"
    if target.exists():
        print(f"  ⚠ 已存在: experiments/method_lineage.yaml，跳过")
        return

    content = """# 方法谱系图 — 记录每个方法版本的来源和演变
# 由 auto-research Skill 自动维护，也可手动编辑

methods: {}
  # 示例:
  # proposed_v1:
  #   origin: "初始版本"
  #   parent: []
  #   role: innovation
  #   status: active
  #   best_primary_metric: null
  #   key_idea: "核心创新点"
  #   git_commit: null
  #   first_appeared: null
  #   experiments: []
"""
    target.write_text(content, encoding="utf-8")
    print(f"  ✓ 创建: experiments/method_lineage.yaml")


def create_work_log(base_dir: Path):
    """创建工作日志初始文件"""
    target = base_dir / "experiments" / "work_log.md"
    if target.exists():
        print(f"  ⚠ 已存在: experiments/work_log.md，跳过")
        return

    content = f"""# 全局工作日志

> 每次重要事件追加一条。Agent 在开始新批次前读最近 5-10 条。

---

## {datetime.now().strftime('%Y-%m-%d')} 项目初始化
- **关键发现**: 项目初始化完成，准备开始第一个实验批次
- **最佳实验**: 无
- **已排除**: 无
- **下一批重点**: 运行基线实验，确定起点
"""
    target.write_text(content, encoding="utf-8")
    print(f"  ✓ 创建: experiments/work_log.md")


def create_experiment_files(base_dir: Path):
    """创建实验日志和总表初始文件"""
    # experiment_log.jsonl
    log_target = base_dir / "experiments" / "experiment_log.jsonl"
    if not log_target.exists():
        log_target.write_text("", encoding="utf-8")
        print(f"  ✓ 创建: experiments/experiment_log.jsonl")

    # experiment_master.csv
    csv_target = base_dir / "experiments" / "experiment_master.csv"
    if not csv_target.exists():
        csv_target.write_text(
            "id,timestamp,batch,round,method,tier,hypothesis,inspiration,primary_metric,vs_baseline,outcome,loop_mode,seed,notes\n",
            encoding="utf-8"
        )
        print(f"  ✓ 创建: experiments/experiment_master.csv")


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Research 项目初始化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python init_research.py --template general
  python init_research.py --template ml_experiment
  python init_research.py --template nlp_benchmark
  python init_research.py --template general --project-dir /path/to/project
        """
    )
    parser.add_argument(
        "--template", "-t",
        choices=AVAILABLE_TEMPLATES,
        default="general",
        help="选择领域模板 (默认: general)"
    )
    parser.add_argument(
        "--project-dir", "-d",
        default=".",
        help="目标项目目录 (默认: 当前目录)"
    )

    args = parser.parse_args()
    base_dir = Path(args.project_dir).resolve()

    print(f"\n🔬 Auto-Research 初始化")
    print(f"{'='*50}")
    print(f"  目标目录: {base_dir}")
    print(f"  模板: {args.template}")
    print(f"{'='*50}\n")

    print("[1/5] 创建目录结构...")
    create_directory_structure(base_dir)

    print("\n[2/5] 生成领域配置...")
    copy_template(args.template, base_dir)

    print("\n[3/5] 创建循环契约...")
    create_loop_contract(base_dir)

    print("\n[4/5] 创建方法谱系和工作日志...")
    create_method_lineage(base_dir)
    create_work_log(base_dir)

    print("\n[5/5] 创建实验记录文件...")
    create_experiment_files(base_dir)

    print(f"\n{'='*50}")
    print(f"✅ 初始化完成！")
    print(f"\n下一步:")
    print(f"  1. 编辑 experiments/research_domain.yaml，填入你的领域信息")
    print(f"  2. 编辑 experiments/loop_contract.md，填写研究目标")
    print(f"  3. 确保你的实验脚本能输出 JSON 结果文件")
    print(f"  4. 在 AI 助手中输入 /auto-research 启动研究循环")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
