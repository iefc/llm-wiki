#!/usr/bin/env python3
"""
LLM Wiki - 摄入新资料

Usage:
    python3 wiki_ingest.py --path ~/my-knowledge-base --source ~/article.pdf --tags "AI,机器学习"
    python3 wiki_ingest.py --path ~/my-knowledge-base --source ~/notes.md --tags "产品,设计"

这个脚本只做机械性工作：
  1. 复制文件到 raw/
  2. 打印相关页面供 LLM 参考

真正的"编译"（读资料→写 wiki/）由 LLM 在 IDE 中完成。
"""

import argparse
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

TEMPLATE_LOG_ENTRY = """
## [{date}] ingest | {title}
- 来源：raw/{filename}
- 标签：{tags}
- 相关页面：{related}
- 新建页面：TBD（由 LLM 填写）
"""


def copy_source_to_raw(kb_path: Path, source: Path, tags: list) -> Path:
    """复制源文件到 raw/，返回目标路径"""
    raw_dir = kb_path / "raw"
    raw_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = source.suffix
    new_name = f"{timestamp}_{source.stem}{ext}"
    dest = raw_dir / new_name

    shutil.copy2(source, dest)

    if tags:
        (dest.with_suffix(".tags")).write_text(", ".join(tags), encoding="utf-8")

    return dest


def find_related_pages(kb_path: Path, content: str) -> list:
    """根据内容找到相关的 Wiki 页面"""
    wiki_dir = kb_path / "wiki"
    if not wiki_dir.exists():
        return []

    related = []
    content_lower = content.lower()

    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        page_content = page_path.read_text(encoding="utf-8").lower()

        title = None
        for line in page_content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        if title and any(word in content_lower for word in title.lower().split()):
            related.append((page_path.stem, title))

    return related


def append_to_log(kb_path: Path, source: Path, tags: list, related: list) -> None:
    """追加 ingest 记录到 log.md"""
    log_path = kb_path / "wiki" / "log.md"
    if not log_path.exists():
        return

    entry = TEMPLATE_LOG_ENTRY.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        title=source.stem,
        filename=f"{source.stem}{source.suffix}",
        tags=", ".join(tags) if tags else "无",
        related=", ".join([f"[[{t[1]}]]" for t in related]) if related else "无",
    )

    log_path.write_text(log_path.read_text(encoding="utf-8").rstrip() + "\n" + entry + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 摄入新资料")
    parser.add_argument("--path", required=True, help="知识库路径")
    parser.add_argument("--source", required=True, help="源文件路径")
    parser.add_argument("--tags", default="", help="标签，逗号分隔")
    parser.add_argument("--no-log", action="store_true", help="不更新 log.md")
    args = parser.parse_args()

    kb_path = Path(args.path).expanduser().resolve()

    if not (kb_path / "CLAUDE.md").exists():
        print(f"[ERROR] '{kb_path}' 不是有效的 LLM Wiki 知识库（缺少 CLAUDE.md）")
        print(f"[HINT] 先运行: python3 wiki_init.py --path {kb_path} --name '名称'")
        sys.exit(1)

    source_path = Path(args.source).expanduser()
    if not source_path.exists():
        print(f"[ERROR] 源文件不存在: {source_path}")
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    print(f"[INFO] 摄入资料: {source_path.name}")
    if tags:
        print(f"[INFO] 标签: {', '.join(tags)}")

    # 复制到 raw/
    dest = copy_source_to_raw(kb_path, source_path, tags)
    print(f"[INFO] 已复制到: {dest}")

    # 读取内容并查找相关页面
    try:
        content = dest.read_text(encoding="utf-8")
    except Exception:
        content = ""

    related = find_related_pages(kb_path, content)
    if related:
        print(f"[INFO] 发现 {len(related)} 个相关页面:")
        for stub, title in related:
            print(f"  - [[{title}]]")
    else:
        print("[INFO] 未发现直接相关的页面（将创建新页面）")

    # 更新 log.md
    if not args.no_log:
        append_to_log(kb_path, source_path, tags, related)
        print(f"[INFO] 已追加到 log.md")

    print()
    print("[DONE] 资料已摄入！")
    print()
    print("下一步:")
    print("  1. 在 IDE 中打开知识库目录")
    print("  2. 让 LLM 阅读 raw/ 中新增的文件")
    print("  3. LLM 会将知识编译到 wiki/（更新现有页面 + 建链接 + 标注冲突）")
    print("  4. 完成后 LLM 会更新 index.md 和 log.md")


if __name__ == "__main__":
    main()
