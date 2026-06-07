# 风控审查 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是风控审查员。对观察池标的执行排雷扫描：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_screening.py 获取选股结果（ST/质押/商誉/审计/现金流）
2. 对观察池标的运行筹码分析：
   - python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py gdrs {代码} 获取股东户数变化
   - python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py jxjj {代码} {今日日期} 获取限售解禁
   - python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py dzjy {代码} 获取大宗交易
3. 检查退市风险、质押风险、商誉风险、审计意见、现金流风险
4. 新增筹码风险：股东户数异常增加、近期大额解禁、大宗持续折价

返回风控结论。""",
    context="风控审查任务",
    toolsets=["terminal"]
)
```

## 数据源

1. **amadeus_screening.py** — 排雷扫描（东方财富+同花顺）（主源）
2. **a_stock_data_supp.py gdrs** — 股东户数变化（东财datacenter）（新增）
3. **a_stock_data_supp.py jxjj** — 限售解禁日历（东财datacenter）（新增）
4. **a_stock_data_supp.py dzjy** — 大宗交易（东财datacenter）（新增）
5. **amadeus_buy_scorer.py** — 买入评分（按需）

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "screening": {
    "002384": {"st_risk": "pass", "pledge_risk": "pass", "goodwill_risk": "warn", "audit_risk": "pass", "cashflow_risk": "pass"}
  },
  "chip_analysis": {
    "002384": {
      "holder_trend": "筹码集中(股东户数连续2季下降)",
      "lockup_risk": "无近期解禁",
      "block_trade_signal": "近30日无大宗交易"
    }
  },
  "risk_verdicts": {
    "002384": {"overall": "warn", "issues": ["商誉占比偏高"], "chip_warnings": []}
  },
  "risk_score": 75,
  "risk_bias": "中性",
  "critical_alerts": []
}
```

## 排雷清单（9项）

| # | 检查项 | 数据源 | 阈值 | 处置 |
|---|--------|--------|------|------|
| 1 | ST风险 | amadeus_screening | ST/*ST | 一票否决 |
| 2 | 质押风险 | amadeus_screening | 质押>70% | 警告 |
| 3 | 商誉风险 | amadeus_screening | 商誉>净资产50% | 警告 |
| 4 | 审计意见 | amadeus_screening | 非标意见 | 一票否决 |
| 5 | 现金流 | amadeus_screening | 连续3季负 | 警告 |
| 6 | **股东户数** | a_stock_data_supp.py gdrs | 连续3季增加>20% | 警告（筹码分散） |
| 7 | **限售解禁** | a_stock_data_supp.py jxjj | 30天内解禁>总股本5% | 警告 |
| 8 | **大宗交易** | a_stock_data_supp.py dzjy | 连续折价>5% | 警告（机构减持） |
| 9 | 大额解禁 | a_stock_data_supp.py jxjj | 解禁>总股本20% | 一票否决 |

## 筹码风险判断标准

- **股东户数连续3季度增加 > 20%** = 筹码分散，主力出货
- **30天内解禁 > 总股本5%** = 解禁压力
- **大宗交易连续折价 > 5%** = 机构减持信号
- **股东户数连续3季度下降** = 筹码集中，主力吸筹（正面信号）
