# 资金面与机构动向 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是资金面分析师。分析A股资金面与机构动向：
1. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py lhb_all {日期} 获取全市场龙虎榜
2. 对观察池标的运行：python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py lhb {代码} {日期} 获取龙虎榜席位
3. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py rzrq {代码} 获取融资融券趋势
4. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py dzjy {代码} 获取大宗交易
5. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py north 获取北向资金实时流向

返回资金面综合评分和结论。""",
    context="资金面分析任务",
    toolsets=["terminal"]
)
```

## 数据源

1. `a_stock_data_supp.py` — 龙虎榜席位/融资融券/大宗交易/北向资金（主源，东财datacenter+同花顺）
2. `tushare_data.py` — 北向资金日级历史（补充，Tushare Pro）

## 数据源优先级

> 东财datacenter有风控，所有请求走em_get()自动限流。批量调用时每请求间隔≥1s。

| 端点 | 数据源 | 封IP风险 | 用途 |
|------|--------|---------|------|
| 龙虎榜 | 东财 datacenter | 中（已限流） | 机构/游资席位、净买入排名 |
| 融资融券 | 东财 datacenter | 中（已限流） | 杠杆资金趋势 |
| 大宗交易 | 东财 datacenter | 中（已限流） | 溢价/折价、买卖方 |
| 北向资金 | 同花顺 hsgtApi | 极低 | 盘中分钟级流向 |

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "dragon_tiger": {
    "market_summary": {"total_stocks": 15, "top_net_buy": [{"code": "002384", "name": "东山精密", "net_buy_wan": 106525}]},
    "pool_stocks": {
      "002384": {"records": 1, "institution_net": 5000, "top_buy_seats": ["机构专用"]}
    }
  },
  "margin": {
    "600519": {"latest_date": "2026-06-02", "rzye_yi": 196.6, "trend": "下降", "days_of_change": 3}
  },
  "block_trades": {
    "600519": {"count": 2, "avg_premium_pct": -1.5, "note": "小幅折价"}
  },
  "northbound": {"hgt_yi": -9.28, "sgt_yi": -31.1, "total_yi": -40.38, "bias": "净流出"},
  "capital_score": 65,
  "capital_bias": "偏空",
  "key_signals": ["北向净流出40亿", "茅台融资余额连续3日下降", "东山精密龙虎榜机构净买入"]
}
```

## 评分标准

| 维度 | 权重 | 评分规则 |
|------|------|---------|
| 龙虎榜机构净买入 | 30% | 机构净买>5000万=80+, >0=60+, <0=40- |
| 融资融券趋势 | 25% | 连续3日增加=80+, 稳定=60+, 连续下降=40- |
| 大宗交易 | 15% | 溢价成交=80+, 平价=60+, 折价>5%=40- |
| 北向资金 | 30% | 净流入>20亿=80+, 震荡=60+, 净流出>20亿=40- |

## 关键判断

- **龙虎榜席位**：机构专用席位净买入 > 5000万 = 强烈看多信号
- **融资融券**：融资余额连续增加 = 杠杆资金看好，但也可能是过度乐观
- **大宗交易**：持续折价 > 5% = 机构减持信号
- **北向资金**：盘中分钟流是最可靠的盘中信号，收盘前30分钟方向最准
