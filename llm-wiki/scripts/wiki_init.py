#!/usr/bin/env python3
"""
LLM Wiki - 初始化新知识库

Usage:
    python3 wiki_init.py --path ~/my-knowledge-base --name "我的知识库" --description "个人知识管理系统"
"""

import argparse
import sys
import shutil
from pathlib import Path
import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"


def init_knowledge_base(path: str, name: str, description: str) -> None:
    """初始化一个新的 LLM Wiki 知识库"""
    kb_path = Path(path).expanduser().resolve()

    if kb_path.exists() and (kb_path / "CLAUDE.md").exists():
        print(f"[ERROR] '{kb_path}' 已经是 LLM Wiki 知识库（CLAUDE.md 已存在）")
        sys.exit(1)

    print(f"[INFO] 初始化知识库: {kb_path}")
    print(f"[INFO] 名称: {name}")
    print(f"[INFO] 描述: {description}")

    # 创建目录结构
    for d in ["raw", "wiki", "self"]:
        (kb_path / d).mkdir(parents=True, exist_ok=True)

    # 复制 Schema 模板为 CLAUDE.md
    claude_md_src = TEMPLATES_DIR / "CLAUDE.md"
    claude_md_dst = kb_path / "CLAUDE.md"
    if claude_md_src.exists():
        shutil.copy2(claude_md_src, claude_md_dst)
    else:
        claude_md_dst.write_text("# CLAUDE.md\n\n（请在 IDE 中让 LLM 根据这个 Schema 规范初始化）\n", encoding="utf-8")

    # 创建 index.md
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    index_md = kb_path / "wiki" / "index.md"
    index_md.write_text(f"""# {name} - 索引

## 概述

{description}

## 概念分类

（摄入资料后自动生成）

## 页面索引

（暂无页面）

## 统计

- 总页面数：0
- 创建日期：{today}
""", encoding="utf-8")

    # 创建 log.md
    log_md = kb_path / "wiki" / "log.md"
    log_md.write_text(f"""# {name} - 日志

Append-only 操作记录。用 `grep "^## \\[" log.md | tail -10` 查看最近活动。

---

## 历史记录

- {today} - 知识库初始化

""", encoding="utf-8")

    # 创建 self/ 基础页面
    (kb_path / "self" / "principles.md").write_text(f"""# 核心原则

## 写作原则

- 简洁明了，避免冗余
- 结构清晰，层次分明
- 事实准确，标注来源

## 更新日期

{today}
""", encoding="utf-8")

    (kb_path / "self" / "goals.md").write_text(f"""# 当前目标

## 短期目标（1-3个月）

- {{目标}}

## 中期目标（3-12个月）

- {{目标}}

## 长期愿景

{{愿景}}

## 更新日期

{today}
""", encoding="utf-8")

    print()
    print("[DONE] 知识库初始化完成！")
    print()
    print(f"  {kb_path}/")
    print(f"  ├── CLAUDE.md   # Schema（LLM 的行为规范）")
    print(f"  ├── raw/         # 原始资料层（只读）")
    print(f"  ├── wiki/")
    print(f"  │   ├── index.md # 内容索引")
    print(f"  │   └── log.md   # 操作日志")
    print(f"  └── self/        # 自我层（可选）")
    print()
    print("下一步:")
    print(f"  1. cd {kb_path}")
    print(f"  2. 将资料放入 raw/ 目录")
    print(f"  3. 在 IDE 中让 LLM 阅读 raw/ 并编译到 wiki/")
    print(f"  4. 使用 wiki_ingest.py 辅助机械性工作")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化新的 LLM Wiki 知识库")
    parser.add_argument("--path", required=True, help="知识库路径")
    parser.add_argument("--name", required=True, help="知识库名称")
    parser.add_argument("--description", default="", help="知识库描述")
    args = parser.parse_args()
    init_knowledge_base(args.path, args.name, args.description)
