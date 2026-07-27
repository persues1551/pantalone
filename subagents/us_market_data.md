# 美股市场数据 Subagent

> **结构化输出 Schema**: `schemas.USMarketDataReport` — 见 `subagents/schemas.py`

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是美股市场数据采集专家。执行以下任务：
1. 使用 yfinance 获取三大指数（^GSPC/^IXIC/^DJI）+ 罗素2000（^RUT）5日/1月/3月表现
2. 获取 VIX（^VIX）、美元指数（DX-Y.NYB）、10年期美债收益率（^TNX）
3. 计算各指数距52周高点回撤、50/200日均线位置、60日年化波动率
4. 获取11只SPDR行业ETF（XLC/XLY/XLP/XLE/XLF/XLV/XLI/XLB/XLRE/XLK/XLU）+ SMH半导体ETF的1月/3月/1年收益
5. 判断行业轮动：区分趋势强但接近高位 vs 长期景气短期回撤 vs 长短期走弱
6. 判断杠杆ETF信号：VIX水平 + 指数趋势 + MACD → 推荐杠杆方向与标的

返回结构化数据。""",
    context="美股市场数据采集任务 — 覆盖指数/VIX/DXY/美债/行业轮动/杠杆ETF信号",
    toolsets=["terminal"]
)
```

## 数据源优先级

1. **yfinance** — 指数、ETF、VIX、DXY、TNX（主力，免费无API key）
2. **^VIX / ^TNX / DX-Y.NYB** — yfinance Ticker直接拉取
3. **SPDR ETFs** — 11行业+SMH，yfinance批量下载
4. **杠杆ETF行情** — TQQQ/SQQQ/UPRO/SPXU/SOXL/SOXS（按需拉取）

## 行业轮动判断规则

- **趋势强但接近高位**：1月收益>5% 且 距高点<3% → 不追涨
- **长期景气、短期回撤**：1年收益>15% 且 1月收益<0% 且 距高点>5% → 重点筛选
- **长短期同时走弱**：1月收益<0% 且 1年收益<5% → 回避（除非基本面拐点）

## 杠杆ETF信号（新增 v5.2）

在完成大盘数据和行业轮动后，输出杠杆/反向 ETF 使用建议。

### 信号判断流程

```
1. VIX 水平
   ├─ <15 → 仅在其余确认项完整时研究 3x 候选
   ├─ 15-20 → 可研究 2x/3x，收紧仓位与退出条件
   ├─ 20-25 → 默认降级 2x 或 avoid
   ├─ 25-30 → 默认 avoid；反向产品仍需全部确认项
   └─ >30 → 默认 avoid，不根据 VIX 单独给出任何方向

2. 指数趋势（以纳指为主，标普确认为辅）
   ├─ >20MA 且 MACD 多头 → 做多信号
   ├─ <20MA 且 MACD 空头 → 做空信号
   └─ 其他 → 不使用杠杆

3. 输出推荐
   ├─ 做多信号 + VIX<25 → TQQQ/UPRO/SOXL（按波动匹配）
   ├─ 做空信号 + VIX 25-30 + 趋势/动量/广度/流动性全确认 → SQQQ/SPXU候选
   └─ 信号矛盾或VIX 20-25 → 不做或降级 2x
```

### 杠杆ETF输出格式

在 `USMarketDataReport` 中增加 `leveraged_signal` 字段。详细标的清单和风控规则见 `references/us-leveraged-etf-guide.md`。

## 建仓速度判断

| VIX | 10Y美债 | 建仓建议 |
|-----|---------|----------|
| <15 | <4.0% | 正常速度，但仍受组合风险预算和单标的上限约束 |
| 15-20 | 4.0-4.5% | 正常速度，控制杠杆 |
| 20-25 | 4.5-5.0% | 减速建仓，保留20%现金 |
| >25 | >5.0% | 暂停新建仓，只持有核心仓位 |

## 输出格式（必须遵守）

```json
{
  "indices": {
    "^GSPC": {"price": 5500.0, "5d_return": 1.2, "1m_return": 3.5, "3m_return": 8.2, "52w_high_drawdown": -2.1, "above_50ma": true, "above_200ma": true, "volatility_60d": 14.5},
    "^IXIC": {"price": 18000.0, "5d_return": 1.8, "1m_return": 4.2, "3m_return": 10.1, "52w_high_drawdown": -1.8, "above_50ma": true, "above_200ma": true, "volatility_60d": 18.2},
    "^DJI": {"price": 39000.0, "5d_return": 0.8, "1m_return": 2.1, "3m_return": 5.5, "52w_high_drawdown": -3.2, "above_50ma": true, "above_200ma": true, "volatility_60d": 11.0},
    "^RUT": {"price": 2100.0, "5d_return": -0.5, "1m_return": 1.2, "3m_return": 3.8, "52w_high_drawdown": -5.5, "above_50ma": false, "above_200ma": true, "volatility_60d": 22.0}
  },
  "vix": {"value": 16.5, "level": "低恐慌"},
  "dxy": {"value": 104.2, "level": "偏强"},
  "tnx": {"value": 4.25, "level": "中等"},
  "sector_rotation": {
    "trending_high": ["XLK", "SMH"],
    "pullback_opportunity": ["XLV", "XLF"],
    "weakening": ["XLE", "XLU"],
    "neutral": ["XLC", "XLY", "XLP", "XLI", "XLB", "XLRE"]
  },
  "market_regime": "risk_on",
  "position_advice": "正常建仓",
  "leveraged_signal": {
    "direction": "long",
    "inputs_complete": true,
    "trend_confirmed": true,
    "momentum_confirmed": true,
    "breadth_confirmed": true,
    "liquidity_confirmed": true,
    "volatility_confirmed": true,
    "vix_value": 16.5,
    "vix_level": "low",
    "recommended": [{"ticker": "TQQQ", "leverage": 3, "position_pct": 5, "stop_loss": -5, "max_hold_days": 5}],
    "not_recommended": [],
    "rationale": "示例数据满足趋势条件；仅生成研究候选，不构成自动交易指令"
  },
  "data_quality": "A",
  "data_date": "2026-07-25",
  "errors": []
}
```

未同时拿到 VIX、底层指数趋势、MACD 和成交量时，`direction` 必须为 `avoid`，不得用默认值补出方向。所有推荐须通过组合层风险预算复核；本 Subagent 不自动下单、不写入持仓或观察池。
