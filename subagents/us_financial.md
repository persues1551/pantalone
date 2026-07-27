# 美股财务分析 Subagent

> **结构化输出 Schema**: `schemas.USFinancialReport` — 见 `subagents/schemas.py`

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是美股财务分析专家。分析{股票代码}的财务数据：
1. 使用 yfinance 获取最近4个季度营收/利润/自由现金流趋势
2. 获取 forward PE、trailing PE、EV/EBITDA、PEG
3. 计算 ROE、毛利率、营业利润率、FCF yield
4. 获取 SEC EDGAR 最近 10-K/10-Q 的关键披露（业务描述、风险因素、管理层讨论）
5. 对比至少2家同行的利润断层
6. 会计口径校验：季度对季度、币种标注、行业差异、异常值复核

返回财务面评分和结论。""",
    context="美股财报分析任务 — yfinance + SEC EDGAR",
    toolsets=["terminal", "web"]
)
```

## 数据源优先级

1. **yfinance** — 财务报表、估值指标、股价（主力）
2. **SEC EDGAR** — 10-K/10-Q原始文件（权威，免费）
   - 提交索引：`https://data.sec.gov/submissions/CIK{CIK}.json`
   - 10-K/10-Q 直接通过 xbrl 或 html 获取
3. **Financial Modeling Prep** — 结构化财务数据（备用，需 API key）

## 会计口径校验（强制）

- **季度对季度**：同比 = 最新季度 vs 上年同季度，不得与上份年报累计数对比
- **累计与单季**：10-Q 累计口径需拆成单季；无法拆分时明确标注
- **币种**：ADR（如 TSM）财务可能以非美元披露，表格标题写清币种
- **行业差异**：银行不用毛利率/经营现金流，改用 ROE/净息差/CET1
- **异常值复核**：盈利增长>100%、ROE>100%、目标价偏离>40% → 检查原始字段

## 美股 vs A股财务指标差异

| 指标 | A股 | 美股 |
|------|-----|------|
| 核心估值 | PE/PB/PEG | forward PE / trailing PE / EV/EBITDA |
| 现金流 | 经营现金流 | FCF yield (自由现金流/市值) |
| 盈利能力 | 扣非ROE | GAAP ROE + non-GAAP调整 |
| 成长性 | 营收/利润增速 | 营收增速 + consensus beat 记录 |
| 质量 | 毛利率/净利率 | 营业利润率 + gross margin + SBC占比 |

## 输出格式（必须遵守）

下列数字仅为 Schema 形状示例，不是当前 NVDA 财务事实；实际执行必须重新读取 SEC EDGAR、yfinance/FMP 并写明 `as_of` 或数据日期。

```json
{
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "currency": "USD",
  "financial_score": 85,
  "valuation": {
    "forward_pe": 28.5,
    "trailing_pe": 42.0,
    "ev_ebitda": 25.0,
    "peg": 0.85,
    "fcf_yield": 3.2
  },
  "growth": {
    "revenue_yoy": "+78%",
    "eps_yoy": "+120%",
    "fcf_yoy": "+95%",
    "revenue_beat_streak": 6,
    "eps_beat_streak": 8
  },
  "profitability": {
    "roe": 55.0,
    "gross_margin": 72.0,
    "operating_margin": 58.0,
    "net_margin": 48.0
  },
  "balance_sheet": {
    "debt_to_equity": 0.15,
    "current_ratio": 3.5,
    "cash_to_debt": 8.0,
    "goodwill_to_assets": 0.05
  },
  "peer_comparison": [
    {"ticker": "AMD", "forward_pe": 22.0, "gross_margin": 52.0, "revenue_yoy": "+15%"},
    {"ticker": "AVGO", "forward_pe": 25.0, "gross_margin": 68.0, "revenue_yoy": "+25%"}
  ],
  "ocifq": {
    "oligopoly": "GPU市场>80%份额，CUDA生态锁定",
    "catalyst": "AI基础设施投资持续，Blackwell平台放量",
    "industry_moat": "营业利润率58% vs 同行均值35%，断层+23pp",
    "financial_blast": "营收+78%/每股+120%/FCF+95%，三爆确认",
    "quarterly_continuity": "连续8季beat consensus + 连续6季guidance上调"
  },
  "accounting_notes": "GAAP口径，non-GAAP与GAAP偏差<5%",
  "data_sources": ["SEC EDGAR", "yfinance"],
  "evidence_refs": {
  "valuation": "https://finance.yahoo.com/quote/NVDA/key-statistics",
  "growth": "https://www.sec.gov/Archives/edgar/data/{CIK}/{accession}/report.htm",
  "profitability": "https://finance.yahoo.com/quote/NVDA/financials",
  "balance_sheet": "https://finance.yahoo.com/quote/NVDA/balance-sheet",
  "peers": "https://finance.yahoo.com/quote/AMD/key-statistics",
  "oligopoly": "https://www.sec.gov/Archives/edgar/data/{CIK}/{accession}/business.htm",
  "catalyst": "https://www.sec.gov/Archives/edgar/data/{CIK}/{accession}/mdna.htm",
  "industry_moat": "https://finance.yahoo.com/quote/NVDA/financials",
  "financial_blast": "https://finance.yahoo.com/quote/NVDA/cash-flow",
  "quarterly_continuity": "https://www.sec.gov/Archives/edgar/data/{CIK}/{accession}/quarterly.htm"
  },
  "data_quality": "A",
  "errors": []
}
```
