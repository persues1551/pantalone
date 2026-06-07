# 财报分析 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是财报分析专家。分析{股票代码}的财务数据：
1. 最近4个季度营收/利润趋势
2. ROE/毛利率/净利率变化
3. 现金流质量
4. 估值水平（PE/PB/PEG）
5. 与同行业对比
6. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py fhzz {代码} 获取分红送转历史

返回财务面评分和结论。""",
    context="财报分析任务",
    toolsets=["terminal", "web"]
)
```

## 数据源

1. **amadeus_financials.py** — 同花顺+巨潮（主源）
2. **腾讯行情API** — PE/PB/市值（实时）
3. **a_stock_data_supp.py fhzz** — 分红送转历史（东财datacenter）（新增）
4. **Tushare daily_basic** — 基本面指标（备用，限流1次/小时）

## 关注重点

- 营收增长是否持续
- 利润质量（扣非vs非经常）
- 现金流是否匹配利润
- 估值是否合理
- **分红送转**：连续高分红 = 管理层对盈利有信心；突然停止分红 = 现金流紧张信号

## 输出格式（必须遵守）

```json
{
  "financial_score": 78,
  "revenue_trend": "连续4季增长(+30%/+25%/+28%/+32%)",
  "profit_trend": "连续4季增长(+50%/+42%/+45%/+55%)",
  "roe": 18.5,
  "gross_margin": 42.3,
  "cashflow_quality": "经营现金流/净利润=1.2，质量优秀",
  "valuation": {"pe_ttm": 19.76, "pb": 6.10, "peg": 0.85},
  "dividend": {"连续分红年数": 5, "近3年股息率": [1.5, 1.8, 2.1], "趋势": "逐年提高"},
  "peer_comparison": "估值低于行业中位数(PE 25)",
  "key_risks": ["估值偏低但可能是价值陷阱"]
}
```
