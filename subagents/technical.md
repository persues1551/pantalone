# 技术分析 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是技术分析专家。对观察池标的执行技术分析：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_realtime.py 获取实时行情+技术指标
2. 分析MA5/10/20/60均线位置、RSI(14)、MACD(12,26,9)
3. 判断布林带位置、支撑位/压力位

返回技术面评分和结论。""",
    context="技术分析任务",
    toolsets=["terminal"]
)
```

## 数据源

1. amadeus_realtime.py — 腾讯API实时行情 + AKShare技术指标（主源）
2. amadeus_indicators.py — 批量技术指标计算（备用）

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "stocks": {
    "600900": {
      "price": 28.5,
      "change_pct": 1.2,
      "MA5": 28.0,
      "MA10": 27.5,
      "MA20": 27.0,
      "RSI14": 55.0,
      "rsi_status": "中性",
      "macd_signal": "多头",
      "BB_upper": 30.0,
      "BB_lower": 26.0,
      "vol_ratio": 1.2,
      "ma_trend": "多头",
      "support_20d": 26.5,
      "resistance_20d": 29.0,
      "buy_blocked": [],
      "source": "tencent+akshare"
    }
  },
  "summary": {
    "bullish_count": 3,
    "bearish_count": 1,
    "neutral_count": 2
  },
  "errors": [],
  "data_sources": ["amadeus_realtime.py"]
}
```

## 关键规则

1. **所有数值必须来自脚本输出**，不可手算或估算
2. **RSI/MACD/布林带必须由脚本计算**，LLM 不可自行推断技术指标值
3. **实时价格来自腾讯API**，不可编造
4. **脚本失败时放入 errors**，不可跳过
5. **买点/卖点信号基于规则判断**，不可凭感觉
