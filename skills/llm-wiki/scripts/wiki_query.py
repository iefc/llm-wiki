#!/usr/bin/env python3
"""
LLM Wiki - 查询知识库

Usage:
    python3 wiki_query.py --path ~/my-knowledge-base --question "LLM Wiki 和 RAG 的核心区别是什么？"

这个脚本只做机械性搜索。真正的查询由 LLM 在 IDE 中完成：
  1. 读取 index.md 找到相关页面
  2. 读取相关页面，综合生成回答
  3. 有价值的回答 → 询问用户是否沉淀为 Wiki 页面
"""

import argparse
import sys
from pathlib import Path


def search_wiki(kb_path: Path, query: str, max_results: int = 5) -> list:
    """在 Wiki 中搜索相关内容（简单关键词匹配）"""
    wiki_dir = kb_path / "wiki"
    if not wiki_dir.exists():
        return []

    results = []
    query_words = query.lower().split()

    for page_path in wiki_dir.glob("*.md"):
        if page_path.name in ("index.md", "log.md"):
            continue
        content = page_path.read_text(encoding="utf-8")
        content_lower = content.lower()

        title = None
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            continue

        score = sum(10 if w in title.lower() else 1 if w in content_lower else 0 for w in query_words)
        if score > 0:
            results.append({"title": title, "file": page_path.name, "score": score, "preview": content[:200]})

    return sorted(results, key=lambda x: x["score"], reverse=True)[:max_results]


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 查询")
    parser.add_argument("--path", required=True, help="知识库路径")
    parser.add_argument("--question", required=True, help="查询问题")
    parser.add_argument("--max-results", type=int, default=5, help="最大结果数")
    args = parser.parse_args()

    kb_path = Path(args.path).expanduser().resolve()

    if not (kb_path / "CLAUDE.md").exists():
        print(f"[ERROR] '{kb_path}' 不是有效的 LLM Wiki 知识库")
        sys.exit(1)

    print(f"[QUERY] {args.question}")
    print(f"[KB]    {kb_path}")
    print()

    results = search_wiki(kb_path, args.question, args.max_results)

    if not results:
        print("[WARN] 未找到直接相关的页面")
        print()
        print("提示：")
        print("  - 如果是全新主题，先摄入相关资料")
        print("  - 在 IDE 中让 LLM 结合 raw/ 中的原始资料回答")
        return

    print(f"[INFO] 找到 {len(results)} 个相关页面:\n")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [[{r['title']}]] (相关度: {r['score']})")

    print()
    print("[DONE] 搜索完成")
    print()
    print("在 IDE 中让 LLM 做深度查询：")
    print("  1. 读取 index.md 找到相关页面")
    print("  2. 综合 Wiki 中的知识生成回答")
    print("  3. 有价值的回答 → 询问是否沉淀为 Wiki 页面")


if __name__ == "__main__":
    main()
