# 市场数据采集 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是市场数据采集专家。执行以下任务：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_emotion.py 采集情绪温度
2. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_sector_flow.py 采集板块资金流
3. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_market_filter.py 采集大盘信号
4. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py north 获取北向资金实时分钟流向

返回结构化数据摘要。""",
    context="数据采集任务",
    toolsets=["terminal"]
)
```

## 数据源优先级

1. **amadeus_emotion.py** — 情绪温度（公式固化，读缓存+过期检测）
2. **amadeus_sector_flow.py** — 板块资金流（同花顺，带单位核验）
3. **amadeus_market_filter.py** — 大盘信号（腾讯API+AKShare）
4. **a_stock_data_supp.py north** — 北向资金实时分钟流（同花顺hsgtApi）（新增）

## 输出格式（必须遵守）

**必须返回以下JSON结构，不可省略字段：**

```json
{
  "emotion": {"score": 65, "level": "中性偏强", "components": {}},
  "sector_flow": {"top_inflow": [], "top_outflow": []},
  "market_filter": {"level": "震荡偏强", "position_pct": 50},
  "northbound": {
    "hgt_yi": -9.28,
    "sgt_yi": -31.1,
    "total_yi": -40.38,
    "bias": "净流出",
    "intraday_signal": "尾盘加速流出"
  },
  "data_quality": "A"
}
```

## 北向资金分钟流判断

- **盘中净流入 > 20亿** = 强烈看多
- **盘中净流入 0-20亿** = 中性偏多
- **盘中净流出 0-20亿** = 中性偏空
- **盘中净流出 > 20亿** = 强烈看空
- **尾盘30分钟方向** = 最可靠信号（机构调仓）
