# data_quality.py 使用指南

## 概述

`data_quality.py` 是 Amadeus 数据质量等级评估模块，统一评估8项核心数据的完整性、新鲜度、来源可靠性。

## 用法

```bash
# 人类可读报告
python3 ~/.hermes/scripts/amadeus/data_quality.py

# JSON输出（供脚本消费）
python3 ~/.hermes/scripts/amadeus/data_quality.py --json

# 报告片段（直接粘贴到报告中）
python3 ~/.hermes/scripts/amadeus/data_quality.py --report-fragment
```

## 等级规则

| 等级 | 得分 | 能否用于胜率统计 | 说明 |
|------|------|-----------------|------|
| A | ≥85% | ✅ | 核心数据齐全且今日 |
| B | ≥70% | ✅ | 主要数据齐全，个别缺失有备用 |
| C+ | ≥50% | ✅ | 部分缺失但有备用源 |
| C | ≥30% | ❌ | 主要依赖web_search/LLM推理 |
| D | ≥15% | ❌ | 旧cache、字段异常、来源不明 |
| F | <15% | ❌ | 数据完全缺失 |

**自动降级规则**：有≥15分权重的核心项缺失时，从A/B/C+降到C/D。

## 8项核心数据

| 数据项 | 权重 | cache来源 | 验证条件 |
|--------|------|-----------|---------|
| 指数数据 | 20 | market_{date}.json→indices | dict且≥2个指数 |
| 涨跌停数据 | 20 | market_{date}.json→pools | limit_up_count > 0 |
| 市场总貌 | 15 | market_{date}.json→market | total > 1000 |
| 北向资金 | 10 | market_{date}.json→north | net_flow 非 None |
| 连板数据 | 10 | market_{date}.json→lianban | list且非空 |
| 板块数据 | 10 | market_{date}.json→sectors | total_count > 0 |
| 板块资金流 | 10 | market_{date}.json→sector_flow | top_inflow 非空 |
| 个股实时行情 | 5 | realtime_*.json | 非 None |

## 嵌入报告的方式

cron报告中必须在正文第一段粘贴 `--report-fragment` 输出：

```markdown
**数据等级：A**（85%）

| 数据项 | 状态 | 来源 |
|--------|------|------|
| 指数数据 | ✅ | 结构化接口(今日) |
| 涨跌停数据 | ✅ | 结构化接口(今日) |
...

⚠️ 市场有风险，投资需谨慎！以上仅作为教学案例，不作为投资建议！
```

## pitfall：cache_pattern 必须用 → 嵌套路径

data_quality.py 的 `CORE_ITEMS` 中，`cache_pattern` 字段如果数据在 market_*.json 内部，
必须用 `market_{date}.json→field` 格式（箭头嵌套路径），不能用独立文件名。

**错误**：`"cache_pattern": "indices_{date}.json"` → 找不到文件，误判为"缺失"
**正确**：`"cache_pattern": "market_{date}.json→indices"` → 从 market_*.json 中提取

已有字段映射：`indices→indices`, `limit_pools→pools`, `market_overview→market`,
`north_flow→north`, `lianban→lianban`, `sectors→sectors`, `sector_flow→sector_flow`

如果新增数据项且数据在 market_*.json 内部，需要在 `_load_cache_file()` 的 `field_map` 中添加映射。

## 与 amadeus_emotion.py 的关系

- `amadeus_emotion.py`：情绪温度计算（5维度加权），检查3个数据源的新鲜度
- `data_quality.py`：数据质量等级评估（8项核心数据），输出报告所需的来源标注

两者独立运行，cron报告中两个都要调用。
