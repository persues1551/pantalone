# Dexter & Dexter-A 研究笔记（2026-05-13）

## Dexter（virattt/dexter，⭐25,486）

TypeScript + Bun + LangChain + Ink(React CLI)。终端金融研究Agent。

### 核心设计
- **SOUL.md**：投资哲学文档（巴菲特+芒格），不是prompt而是价值观
- **三层上下文管理**：微压缩(8条工具结果/80K token) → 记忆写盘 → 全量压缩 → 截断
- **Scratchpad**：工具调用入参/返回/摘要记录到 `.dexter/scratchpad/` JSONL
- **Skills扩展**：SKILL.md格式，2个内置（DCF估值8步、X情绪研究）
- **大结果持久化**：超大工具结果存盘，上下文只留摘要

### 22个MCP工具
`list_skills` / `load_skill` / `backtest` / `factor_analysis` / `pattern_recognition` / `get_market_data` / `web_search` / `run_swarm` 等

### 数据源
FinancialDatasets API（美股）、web_search三级降级（Exa→Perplexity→Tavily）、X搜索、Playwright浏览器

## Dexter-A（abrclano/dexter-A，⭐3）

Dexter的A股中国适配版，dev分支71文件改动。

### 新增模块
- **东方财富妙想API**（5工具）：行情/研报/自然语言选股/自选股/模拟器。需 `MX_APIKEY`
- **Tushare Pro API**（20+工具）：财务报表/北向资金/融资融券/大宗交易/涨跌停/业绩预告。需2000积分token
- **A股分析技能**（6步）：识别意图→数据采集→排雷检查→估值分析→技术面→综合研判
- **CHINA_MARKETS.md**：A股交易规则/监管体系/退市新规/估值框架

### 已借鉴到Amadeus的改进
1. SOUL.md灵魂文件 ✅
2. 排雷检查（5项） ✅
3. 草稿本Scratchpad ✅
4. 大结果持久化 ✅
5. Skills步骤清单格式 ✅
6. 美股板块扩展（yfinance） ✅
7. 三级降级搜索 ✅

### 待接入（主人提供token后）
- Tushare Pro（2000积分，~200元或签到+邀请）
- 东方财富妙想API（需申请MX_APIKEY）

## 美股数据源评估

| 数据源 | 免费额度 | 用途 | 状态 |
|--------|---------|------|------|
| yfinance | 无限 | 股价/基本面/财报 | ✅ 已安装 |
| SEC EDGAR | 无限 | SEC文件 | 可用 |
| Financial Modeling Prep | 250次/天 | 结构化财报 | 需API key |
| Finnhub | 60次/分 | 综合数据 | 需API key |
| Alpha Vantage | 25次/天 | 技术指标 | 太受限 |
| Polygon | 5次/分 | 股价 | 免费层太弱 |

推荐组合：yfinance（主力） + FMP（补充） + SEC EDGAR（权威）
