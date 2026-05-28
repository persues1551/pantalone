# Perplexity上下文压缩集成（2026-05-22）

## 概述
Query-Aware Context Compression，在LLM摘要之前按相关性预过滤中间消息。
已集成到 `agent/context_compressor.py` 作为 Phase 2.5。

## 技术原理
传统压缩：prune tool results → protect head → protect tail → summarize ALL middle
Perplexity增强：prune tool results → protect head → protect tail → **filter by relevance** → summarize relevant middle

## 实现位置
`agent/context_compressor.py`（Hermes核心）
- `_CJK_RE` — CJK字符检测正则
- `_score_message_relevance(message, query_keywords)` — 消息相关性评分（0-1）
- `_filter_by_relevance(turns, query, keep_ratio)` — 按相关性过滤消息
- Phase 2.5 in `compress()` — 在Phase 2和Phase 3之间自动执行

## CJK处理（关键）
中文没有空格分词，`\w+`会把整段中文匹配为一个token。
修复方案：
- 关键词提取：中文用单字符拆分（`re.findall(r'[\u4e00-\u9fff]', text)`）
- 相似度计算：中文用子串匹配（`kw in text`），英文用词级匹配（`set overlap`）
- 过滤阈值：`len(w) > 1 or is_cjk(w)` 保留所有CJK单字

## 参数
- `keep_ratio=0.6` — 保留60%最相关消息
- 仅在中间消息>6条时触发（小消息列表不需要过滤）
- 从最后一条用户消息提取query关键词
- 始终保留最近1条消息（时效性保障）

## 测试用例
```python
# 中文
c._filter_by_relevance(msgs, 'RAG优化检索')  # → 5/8, dropped=3
# 英文
c._filter_by_relevance(msgs, 'RAG retrieval optimization')  # → 5/9, dropped=4
# 空query
c._filter_by_relevance(msgs, '')  # → 全保留, dropped=0
```

## 升级路径
当前用关键词匹配（零成本），可升级为：
1. Embedding粗筛 + LLM精排（混合方案，精度最高）
2. 纯Embedding（text-embedding-3-small，中等精度，低延迟）
