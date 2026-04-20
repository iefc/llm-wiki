#!/usr/bin/env python3
"""
LLM Wiki - 健检知识库健康度

Usage:
    python3 wiki_lint.py --path ~/my-knowledge-base

检查内容：
  1. 孤立页面（无 inbound 链接）
  2. 冲突标注
  3. 过时页面（超过 6 个月未更新）
  4. index.md 一致性

真正的 LLM 驱动的 lint（在 IDE 中）会做得更深入：
  - 语义矛盾检测
  - 建议新问题/新来源/值得深挖的方向
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta


def extract_links(content: str) -> set:
    """提取 [[页面名]] 格式的链接"""
    return set(re.findall(r'\[\[([^\]]+)\]\]', content))


def find_orphan_pages(kb_path: Path) -> list:
    """找出孤立页面（没有被其他页面链接）"""
    wiki_dir = kb_path / "wiki"
    if not wiki_dir.exists():
        return []

    all_links = set()
    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        content = page_path.read_text(encoding="utf-8")
        all_links.update(extract_links(content))

    orphans = []
    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        content = page_path.read_text(encoding="utf-8")
        title = None
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if title and title not in all_links:
            orphans.append((title, page_path.name))

    return orphans


def find_conflicts(kb_path: Path) -> list:
    """找出标记了冲突的页面"""
    wiki_dir = kb_path / "wiki"
    if not wiki_dir.exists():
        return []

    conflicts = []
    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        content = page_path.read_text(encoding="utf-8")
        if "[CONFLICT]" in content:
            title = None
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            conflicts.append(title or page_path.stem)

    return conflicts


def find_outdated_pages(kb_path: Path, months: int = 6) -> list:
    """找出可能过时的页面"""
    wiki_dir = kb_path / "wiki"
    if not wiki_dir.exists():
        return []

    outdated = []
    cutoff = datetime.now() - timedelta(days=months * 30)

    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        mtime = datetime.fromtimestamp(page_path.stat().st_mtime)
        if mtime < cutoff:
            content = page_path.read_text(encoding="utf-8")
            title = None
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            outdated.append((title or page_path.stem, mtime.strftime("%Y-%m-%d")))

    return outdated


def check_index_consistency(kb_path: Path) -> list:
    """检查 index.md 与实际页面的一致性"""
    wiki_dir = kb_path / "wiki"
    index_path = wiki_dir / "index.md"

    if not index_path.exists():
        return ["index.md 不存在"]

    issues = []
    index_content = index_path.read_text(encoding="utf-8")

    # 统计实际页面数
    actual_count = sum(1 for p in wiki_dir.glob("*.md") if p.name not in ("index.md", "log.md"))
    issues.append(f"实际页面数: {actual_count}")

    return issues


def append_lint_to_log(kb_path: Path, orphans: list, conflicts: list, outdated: list) -> None:
    """追加 lint 结果到 log.md"""
    log_path = kb_path / "wiki" / "log.md"
    if not log_path.exists():
        return

    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## [{today}] lint | 健康检查\n"
    entry += f"- 孤立页面：{len(orphans)} 个\n"
    entry += f"- 冲突标注：{len(conflicts)} 个\n"
    entry += f"- 过时页面：{len(outdated)} 个\n"

    if orphans:
        entry += f"- 孤立页面列表：{', '.join(['[[' + t + ']]' for t, _ in orphans])}\n"
    if conflicts:
        entry += f"- 冲突页面：{', '.join(['[[' + t + ']]' for t in conflicts])}\n"

    entry += "- LLM 建议：在 IDE 中运行深度 lint（语义矛盾检测 + 新问题建议）\n"

    log_path.write_text(log_path.read_text(encoding="utf-8").rstrip() + entry + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 健检")
    parser.add_argument("--path", required=True, help="知识库路径")
    parser.add_argument("--no-log", action="store_true", help="不更新 log.md")
    args = parser.parse_args()

    kb_path = Path(args.path).expanduser().resolve()

    if not (kb_path / "CLAUDE.md").exists():
        print(f"[ERROR] '{kb_path}' 不是有效的 LLM Wiki 知识库")
        sys.exit(1)

    print(f"[INFO] 健检知识库: {kb_path}")
    print(f"[INFO] 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 1. 孤立页面
    print("[1/4] 孤立页面（无 inbound 链接）...")
    orphans = find_orphan_pages(kb_path)
    if orphans:
        print(f"  [WARN] {len(orphans)} 个孤立页面:")
        for title, fname in orphans:
            print(f"    - [[{title}]] ({fname})")
    else:
        print("  [OK] 无孤立页面")

    # 2. 冲突标注
    print()
    print("[2/4] 冲突标注...")
    conflicts = find_conflicts(kb_path)
    if conflicts:
        print(f"  [INFO] {len(conflicts)} 个页面有冲突标注:")
        for title in conflicts:
            print(f"    - [[{title}]]")
    else:
        print("  [OK] 无冲突标注")

    # 3. 过时页面
    print()
    print("[3/4] 过时页面（6个月以上）...")
    outdated = find_outdated_pages(kb_path)
    if outdated:
        print(f"  [WARN] {len(outdated)} 个可能过时的页面:")
        for title, mtime in outdated:
            print(f"    - [[{title}]] (最后更新: {mtime})")
    else:
        print("  [OK] 无过时页面")

    # 4. 一致性
    print()
    print("[4/4] index.md 一致性...")
    issues = check_index_consistency(kb_path)
    for issue in issues:
        print(f"  [INFO] {issue}")

    # 更新 log.md
    if not args.no_log:
        append_lint_to_log(kb_path, orphans, conflicts, outdated)
        print()
        print(f"  [INFO] 已追加到 log.md")

    # 总结
    print()
    print("=" * 50)
    total = len(orphans) + len(conflicts) + len(outdated)
    if total == 0:
        print("[PASS] 健康检查通过")
    else:
        print(f"[INFO] 发现 {total} 个问题")
        print()
        print("在 IDE 中让 LLM 做深度 lint：")
        print("  - 语义矛盾检测（跨页面）")
        print("  - 建议新问题和新来源")
        print("  - 建议值得深挖的方向")


if __name__ == "__main__":
    main()
