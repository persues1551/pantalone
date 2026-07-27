# 美股 Pantalone 适配映射文档

> v5.2 — 将 Pantalone 四层框架和 OCIFQ 方法论映射到美股市场

## 四层框架美股映射

### Layer 1：版本与补丁 → 宏观周期 + 财报季

| A股框架 | 美股映射 | 跟踪指标 |
|---------|----------|----------|
| 主线版本识别 | 宏观周期（扩张/放缓/衰退） | GDP增速、PMI、失业率 |
| 补丁事件 | 财报季惊喜/暴雷、美联储决议 | earnings surprise %、FOMC dot plot |
| 催化事件 | 技术突破（AI/量子）、监管变化、并购潮 | 行业ETF资金流、IPO市场温度 |

### Layer 2：供应链与利润 → 全球供应链 + 终端需求

| A股框架 | 美股映射 | 数据源 |
|---------|----------|--------|
| 终端需求识别 | 美国消费支出结构 + 企业资本开支 | BEA PCE、Census retail sales |
| 供应链位置 | 全球价值链定位（设计/制造/品牌） | 10-K Supply Chain披露 |
| 利润分配 | 行业利润率分层 + 集中度趋势 | yfinance行业对比 |

### Layer 3：选龙头 → 护城河 + 利润断层

| A股框架 | 美股映射 | 判断标准 |
|---------|----------|----------|
| 寡头定价权(O) | 品牌护城河 / 网络效应 / 转换成本 / 规模经济 | Morningstar Wide Moat + 毛利率>行业均值 |
| 长周期催化(C) | 技术平台锁定 / AI基础设施 / 专利悬崖 | 10-K Risk Factors + 行业研报 |
| 行业利润断层(I) | 营业利润率 > 同行中位数 + 竞争优势持续期 | yfinance.financials |
| 财务三爆(F) | 营收>15% + FCF yield>3% + ROE>15% | 10-K/10-Q + yfinance |
| 连续季报(Q) | 连续4季beat consensus + guidance上调 | earnings history |

### Layer 4：择时 → 技术面 + 宏观因子

| A股框架 | 美股映射 | 工具 |
|---------|----------|------|
| 技术指标 | MA/RSI/MACD/布林带（yfinance） | yfinance.history |
| 资金流向 | ETF申赎、put/call ratio、margin debt | FINRA、CFTC |
| 宏观因子 | 利率敏感度、美元强弱、信用利差 | FRED数据 |
| 风险收益比 | 历史VaR、ATR、最大回撤 | yfinance + 自行计算 |

## 市场数据对比

| 维度 | A股 | 美股 |
|------|-----|------|
| 交易时间 | 9:30-15:00 CST | 9:30-16:00 EST（北京时间21:30-次日4:00） |
| 实时数据 | 腾讯API/AKShare（免费） | yfinance（免费，延迟15分钟） |
| 财务报告 | 季报/年报（巨潮） | 10-Q/10-K（SEC EDGAR） |
| 排雷 | ST/质押/商誉/审计 | delisting/诉讼/insider selling |
| 交易规则 | T+1, ±10%涨跌停 | 主要适用证券T+1结算（2024-05-28起）, 无涨跌停, 熔断机制 |
| ETF生态 | ~1000只，A股为主 | ~3000只，全球配置 |

## Subagent 路由规则

美股任务在 Pantalone 框架内的分发逻辑：

1. **用户问美股大盘/外围** → `us_market_data.md` + `../amadeus-us-market/SKILL.md`（速览模式）
2. **用户问美股个股深度研究** → `us_market_data.md` → `us_financial.md` → `us_risk.md` → summary（完整8阶段简化为3阶段）
3. **用户问美股建仓/筛选** → `../amadeus-us-market/references/us-market-screening-and-entry.md`（9步全流程）
4. **用户问美股非科技板块** → `../amadeus-us-market/references/us-non-tech-sector-screening.md`
5. **用户问A股受美股影响** → `amadeus-us-market` 7步传导分析
6. **用户问杠杆/做空 ETF** → `us_market_data.md`（杠杆信号段）+ `references/us-leveraged-etf-guide.md`（标的+风控）

## 数据源等级

| 优先级 | 数据源 | 适用范围 | 限制 |
|--------|--------|----------|------|
| 1 | SEC EDGAR | 10-K/10-Q、8-K、proxy | 免费、权威、10次/秒限流 |
| 2 | yfinance | 行情、财务、估值、insider | 免费、有429限流 |
| 3 | Financial Modeling Prep | 结构化财务、DCF、评级 | 250次/天免费、需API key |
| 4 | 券商研报 | 行业分析、目标价 | 可能有利益冲突，作为参考 |
| 5 | TradingView/Finviz | 技术图表、screener | 辅助工具，不直接引用 |

## 失效条件

美股分析在以下条件失效时必须标注：

1. yfinance 连续3次429 → 跳过实时数据，使用最近缓存
2. SEC EDGAR CIK找不到 → 降级为 yfinance 数据
3. 非交易日 → 使用最近交易日数据，标注日期
4. ADR币种不匹配 → 标注原始币种，不做自动换算
5. 财报口径不一致 → 标注GAAP/non-GAAP差异
