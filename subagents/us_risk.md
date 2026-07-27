# 美股风险审查 Subagent

> **结构化输出 Schema**: `schemas.USRiskReport` — 见 `subagents/schemas.py`

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是美股风险审查员。对{股票代码}执行美股专属排雷扫描：

1. 退市风险检查：股价是否<$1（30天）、是否收到不合规通知、市值是否<$5000万
2. 集体诉讼风险：搜索 SEC 调查公告、证券欺诈诉讼
3. Insider Selling：yfinance 获取 insider transactions，检查高管/董事连续减持
4. 商誉减值风险：商誉/总资产 > 30%？近期标的业绩是否下滑？
5. 债务压力：利息覆盖率、短期债务/现金比
6. 客户集中度：10-K 中是否有单一客户 > 25%？
7. 监管风险：FTC/DOJ 反垄断、CFIUS 审查、出口管制
8. 会计质量：non-GAAP vs GAAP 偏差、审计师是否更换

返回风险评级和关键警告。""",
    context="美股风险审查任务 — 区别于A股排雷",
    toolsets=["terminal", "web"]
)
```

## 美股排雷清单（8项）

| # | 检查项 | 数据源 | 阈值 | 处置 |
|---|--------|--------|------|------|
| 1 | 退市风险 | yfinance + SEC | 股价<$1×30天 / 不合规通知 | 一票否决 |
| 2 | 集体诉讼 | SEC Litigation + web搜索 | 证券欺诈/误导陈述/SEC调查 | 警告 |
| 3 | Insider Selling | yfinance.insider_transactions | 连续3月减持>持仓10% | 警告 |
| 4 | 商誉减值 | yfinance.balance_sheet | 商誉>总资产30% + 标的下滑 | 警告 |
| 5 | 债务压力 | yfinance.financials | 利息覆盖率<2x / 短债>现金2x | 警告 |
| 6 | 客户集中度 | 10-K Risk Factors | 单一客户>营收25% | 警告 |
| 7 | 监管风险 | SEC+新闻 | 反垄断/CFIUS/出口管制 | 警告或否决 |
| 8 | 会计质量 | 10-K/10-Q | non-GAAP偏差>20% / 审计师更换 | 警告 |

## 与A股排雷的关键差异

| 维度 | A股 | 美股 |
|------|-----|------|
| 退市机制 | ST/*ST → 连续亏损/净资产为负 | 股价<$1 / 市值<$5000万 / 不合规 |
| 质押风险 | 大股东质押>70% | 不适用 → 改为 insider selling |
| 审计风险 | 非标意见 | non-GAAP vs GAAP 偏差 + 审计师更换 |
| 解禁风险 | 限售解禁 > 总股本5% | Lock-up expiration + 二次发行 |
| 特有风险 | 商誉减值/现金流为负 | 集体诉讼/FTC反垄断/CFIUS审查 |

## 输出格式（必须遵守）

```json
{
  "ticker": "NVDA",
  "overall_risk": "low",
  "risk_score": 85,
  "checks": {
    "delisting": {"status": "pass", "detail": "股价远高于$1，市值>$3T"},
    "litigation": {"status": "pass", "detail": "无重大集体诉讼"},
    "insider_selling": {"status": "pass", "detail": "近3月高管净买入"},
    "goodwill": {"status": "pass", "detail": "商誉/总资产=5%"},
    "debt": {"status": "pass", "detail": "利息覆盖率>20x，现金/短债>8x"},
    "customer_concentration": {"status": "warn", "detail": "云服务商集中度较高，但多元化改善中"},
    "regulatory": {"status": "warn", "detail": "对华出口管制持续收紧，关注BIS新规"},
    "accounting": {"status": "pass", "detail": "non-GAAP与GAAP偏差<5%，审计师PwC"}
  },
  "critical_alerts": [],
  "warnings": ["export_controls"],
  "risk_bias": "偏多（低风险）",
  "data_sources": ["yfinance", "SEC EDGAR"],
  "data_quality": "A",
  "errors": []
}
```
