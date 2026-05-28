# 市场数据采集 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是市场数据采集专家。执行以下任务：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_emotion.py 采集情绪温度
2. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_sector_flow.py 采集板块资金流
3. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_market_filter.py 采集大盘信号

返回结构化数据摘要。""",
    context="数据采集任务",
    toolsets=["terminal"]
)
```

## 数据源优先级

1. amadeus_emotion.py（公式固化，读缓存+过期检测）
2. amadeus_sector_flow.py（同花顺，带单位核验）
3. amadeus_market_filter.py（腾讯API+AKShare）

## 输出格式（必须遵守）

**必须返回以下JSON结构，不可省略字段：**

```json
{
  "emotion": {
    "score": 76,
    "level": "高潮",
    "data_freshness": "fresh|stale",
    "stale_warnings": [],
    "components": {}
  },
  "sector_flow": {
    "top_inflow": [{"name": "xxx", "net_inflow_yi": 1.23, "change_pct": 0.5}],
    "top_outflow": [],
    "key_flow": [],
    "unit_standardized": "亿元",
    "unit_confidence": "high|medium|low"
  },
  "market_filter": {
    "level": "震荡偏强",
    "limit_up": 54,
    "limit_down": 15,
    "index_change_pct": 0.5
  },
  "errors": [],
  "data_sources": ["amadeus_emotion.py", "amadeus_sector_flow.py", "amadeus_market_filter.py"]
}
```

## 关键规则

1. **不可编造数据**：所有数字必须来自脚本输出
2. **必须标注数据来源**：每个数据点标注来自哪个脚本
3. **过期数据必须标注**：如果 emotion 返回 `data_freshness: "stale"`，必须在报告中注明
4. **单位必须标准化**：板块资金流统一用"亿元"
5. **脚本失败不可跳过**：如果某个脚本失败，放入 `errors` 数组，不可用 LLM 推断替代
