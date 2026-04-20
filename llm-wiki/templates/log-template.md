# {{知识库名称}} - 日志

Append-only 操作记录。用 `grep "^## \[" log.md | tail -10` 查看最近活动。

## 日志格式

```markdown
## [YYYY-MM-DD] ingest | 来源标题
- 处理了 raw/文件名
- 更新了 [[页面A]]、[[页面B]]
- 新建了 [[页面C]]
- 标注了 [[页面D]] 的冲突

## [YYYY-MM-DD] query | 用户问题摘要
- 查看了 [[页面A]]、[[页面B]]
- 生成了回答（沉淀为 [[新页面E]]）

## [YYYY-MM-DD] lint | 发现的问题
- 孤立页面：[[页面F]]
- 冲突标注：[[页面G]]
- 建议：...
```

---

## 历史记录

（每次 ingest/query/lint 在此追加）
