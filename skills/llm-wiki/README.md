# llm-wiki Skill

基于 Karpathy LLM Wiki 概念的知识库管理系统。

## 目录结构

```
llm-wiki/
├── SKILL.md              # Skill 定义（触发条件 + 行为规则）
├── templates/
│   ├── index-template.md # wiki/index.md 生成模板
│   ├── page-template.md  # 页面模板
│   ├── hot-template.md   # 会话热缓存模板
│   ├── log-template.md   # 日志模板
│   └── CLAUDE.md        # Wiki Schema（知识库宪法）
├── scripts/
│   ├── wiki_init.py     # 初始化知识库
│   ├── wiki_ingest.py   # 摄入新资料
│   ├── wiki_query.py    # 查询知识库
│   └── wiki_lint.py     # 检查知识库健康度
└── README.md
```

## 触发条件

当用户要求以下操作时自动应用：

| 场景 | 说明 |
|------|------|
| "帮我查一下..." | 查询知识库 |
| "帮我摄入..." | 摄入新资料到 Wiki |
| "出一个方案设计" | 写入方案到 `wiki/方案设计/` |
| "帮我整理一下..." | 知识整理和归纳 |

## 快速开始

### 初始化新知识库

```bash
python scripts/wiki_init.py ~/my-wiki
```

### 摄入新资料

```bash
python scripts/wiki_ingest.py ~/my-wiki raw/article.md
```

### 查询

```bash
python scripts/wiki_query.py ~/my-wiki "如何部署 Prometheus"
```

### Lint

```bash
python scripts/wiki_lint.py ~/my-wiki
```

## Wiki 目录结构

```
wiki/
├── index.md          # 内容索引（按分类组织）
├── log.md            # 操作日志（append-only）
├── hot.md            # 会话热缓存（约 500 词）
├── CLAUDE.md         # Schema（LLM 的行为规范）
├── 分类目录/
│   ├── 页面A.md
│   └── 页面B.md
└── raw/              # 原始资料（只读）
```

## 链接规范

> ⚠️ 链接必须包含子目录路径，格式为 `[[子目录/文件名]]`

- ✅ 正确：`[[ai-工具与平台/Karpathy-Guidelines-项目]]`
- ❌ 错误：`[[Karpathy-Guidelines-项目]]`

## frontmatter 必填字段

```yaml
---
title: 页面标题
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/源文件.md]
category: 分类名
---
```

## 核心原则

1. **你写 Wiki，用户读 Wiki**。用户不写 Wiki
2. **Wiki 是持久、复合的 artifact**。不是每次查询重新生成
3. **一次编译，持久持有**。新资料来了更新现有页面 + 建链接
4. **raw/ 不可变**。使用 `chmod -R a-w raw/` 强制文件系统级只读
