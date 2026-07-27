# 美股纳入 Pantalone 业务范畴 — 集成方案

> 2026-07-26 设计稿 | 待用户审核后执行

## 现状

`amadeus-us-market` skill 已有扎实的美股分析基础，但作为独立「外围市场参考」运行，
未集成到 Pantalone 的四层框架、8阶段研究和 subagent 体系。

## 缺口清单（5项）

### 1. Agent 定义更新
**文件**：`/home/ubuntu/.hermes/agents/pantalone.md`

- 主责增加「美股」
- 能力表增加一行：`美股分析 | 指数/行业轮动/OCIFQ选股/深度研究`
- 添加美股相关 Skill 引用

### 2. Pantalone SKILL.md 更新
- **When to Use**：增加「美股指数、个股、ETF、行业轮动及深度研究」
- **数据源规则**：增加美股数据优先级（yfinance > SEC EDGAR > FMP）
- **4层框架美股适配**：增加美股版 Layer 1-4 映射表
- **桥接引用**：明确「美股深度研究 → 加载 amadeus-us-market」

### 3. 新增美股 Subagent（2-3个）

Pantalone 现有 9 个 subagent 全为 A股设计。需要：

| 新 Subagent | 职责 | 数据源 |
|-------------|------|--------|
| `us_market_data.md` | 美股大盘数据 + 行业轮动 | yfinance, ^VIX, ^TNX, SPDR ETFs |
| `us_financial.md` | 美股财报分析（SEC 10-K/10-Q） | SEC EDGAR, yfinance.financials |
| `us_risk.md` | 美股风险审查（区别于 A股排雷） | SEC filings, earnings surprises, class actions |

这些 subagent 遵循 Pantalone 现有 `delegate_task` + JSON Schema 模式。

### 4. Schema 扩展
**文件**：`subagents/schemas.py`

增加：
- `USMarketDataReport` — 指数/VIX/DXY/10Y/板块轮动
- `USFinancialReport` — forward PE, FCF yield, 10-K 季报拆解
- `USRiskReport` — 区别于 A股的排雷清单

### 5. 适配映射文档
**新增文件**：`references/us-market-pantalone-adaptation.md`

- **4层框架 → 美股映射**：
  - Layer 1（版本周期）→ 财报季/美联储周期
  - Layer 2（供应链）→ 全球供应链（已部分覆盖）
  - Layer 3（龙一）→ 护城河+利润断层
  - Layer 4（择时）→ yfinance 技术指标
- **OCIFQ → 美股因子映射**：
  - 寡头定价权(O) → 护城河宽度
  - 行业利润断层(I) → 竞争格局+市场份额
  - 连续季报(Q) → SEC Edgar 季度环比
- **排雷清单 → 美股风险清单**：
  - ST风险 → delisting risk
  - 质押风险 → insider selling
  - 商誉风险 → goodwill impairment

## 不变的部分

- `amadeus-us-market` SKILL.md 保持独立，作为外围市场速览入口
- 现有 Pantalone 4层框架核心逻辑不变，只加美股映射层
- `.hermes/` 下的 scripts 无需新增（yfinance 可直接在 subagent 中调用）

## 优先级

| 序号 | 改造项 | 工作量 |
|------|--------|--------|
| P0 | Agent 定义 + SKILL.md When to Use 更新 | 小 |
| P1 | `us_market_data.md` subagent | 中 |
| P2 | `us_financial.md` subagent | 中 |
| P3 | Schema 扩展 | 中 |
| P4 | `us_risk.md` subagent + 适配映射文档 | 小 |
| P5 | 4层框架美股适配文档 | 小 |
