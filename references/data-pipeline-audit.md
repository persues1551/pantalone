# Amadeus 数据管线审计报告 (2026-05-20)

## 审计范围
盘前早报、午间复盘、收盘复盘三份cron报告的完整数据采集→处理→输出链路。

## 架构概览

```
cron触发 → 主Agent加载上下文 → delegate_task并行5个subagent → 综合生成报告 → 独立审查 → 发送
              ↓                        ↓
    amadeus_context.py        ┌─ market_data: amadeus_emotion.py + amadeus_market_filter.py
    amadeus_sim_integrate.py  ├─ technical:   amadeus_indicators.py
    amadeus_data.py           ├─ macro:       amadeus_global.py (web toolset备用)
                              ├─ theme:       amadeus_news_scanner.py (web toolset备用)
                              └─ risk:        amadeus_screening.py
```

## 数据源分类

### A类：结构化接口（AKShare/腾讯/新浪直连）

| 脚本 | API | 底层源 | 数据 | 可靠性 |
|------|-----|--------|------|--------|
| amadeus_data.py | `ak.stock_zh_a_spot()` | 新浪 | 全市场个股 | ⭐⭐⭐⭐ |
| amadeus_data.py | `ak.stock_zh_index_daily()` | AKShare | 指数日线 | ⭐⭐⭐⭐⭐ |
| amadeus_data.py | `ak.stock_zt_pool_em/dtgc/zbgc/strong` | 东方财富 | 涨跌停池/连板 | ⭐⭐⭐⭐⭐ |
| amadeus_data.py | `ak.stock_margin_sse()` | 上交所 | 融资融券 | ⭐⭐⭐⭐ |
| amadeus_data.py | `ak.stock_hsgt_hist_em()` | 东方财富 | 北向资金 | ⭐⭐⭐(不稳定) |
| amadeus_data.py | `ak.stock_board_industry_name_em()` | 东方财富 | 板块行情 | ⭐⭐⭐(RemoteDisconnected) |
| amadeus_data.py | `ak.stock_board_industry_summary_ths()` | 同花顺 | 板块资金流 | ⭐⭐⭐(单位待验) |
| amadeus_market_filter.py | `curl qt.gtimg.cn` | 腾讯 | 实时指数 | ⭐⭐⭐⭐⭐ |
| amadeus_sim_integrate.py | `curl qt.gtimg.cn` | 腾讯 | 持仓价格 | ⭐⭐⭐⭐⭐ |
| amadeus_global.py | `ak.index_us_stock_sina()` | 新浪 | 美股 | ⭐⭐⭐(常null) |
| amadeus_global.py | `ak.futures_zh_daily_sina(XINA50)` | 新浪 | A50期货 | ⭐⭐⭐(常null) |
| amadeus_global.py | `ak.stock_hk_index_daily_sina(HSI)` | 新浪 | 恒指 | ⭐⭐⭐⭐ |
| amadeus_global.py | `ak.currency_boc_sina()` | 新浪/央行 | 汇率 | ⭐⭐⭐(常null) |
| amadeus_news_scanner.py | `ak.stock_info_global_em/cls/sina/ths()` | 4源 | 新闻 | ⭐⭐⭐⭐ |
| amadeus_indicators.py | `ak.stock_zh_a_daily()` | 新浪 | 个股K线 | ⭐⭐⭐⭐ |
| amadeus_screening.py | `ak.stock_pledge_stat_em()` | 东方财富 | 质押 | ⭐⭐⭐⭐ |
| amadeus_screening.py | `ak.stock_financial_abstract_ths()` | 同花顺 | 财报 | ⭐⭐⭐⭐ |

### B类：web_search / Tavily（备用）

cron prompt给macro和theme subagent分配了`web` toolset，但**实际脚本中无任何调用**。
web_search仅在AKShare全部失败时由subagent LLM自行决定使用，正常流程不走此路径。

### C类：LLM推断（无结构化数据源）

| 数据 | 风险 |
|------|------|
| 宏观政策分析（货币/财政/产业方向） | 高 — 可能编造 |
| 题材催化分析（消息面解读、轮动逻辑） | 高 — 可能编造 |
| 明日预测（概率判断） | 高 — 主观 |
| 综合评分（6维度100分） | 中 — 公式化但有主观成分 |
| 仓位建议 | 低 — 基于固化规则 |

## 关键问题

### 🔴 P0：cron引用3个不存在的脚本（2026-05-21更正：全部已存在）

| 引用名 | 状态(2026-05-20) | 2026-05-21更正 | 实际路径 |
|--------|------|---------|----------|
| amadeus_realtime.py | ❌不存在 | ✅已存在 | `~/.hermes/scripts/amadeus/amadeus_realtime.py` |
| amadeus_external.py | ❌不存在 | ✅已存在 | `~/.hermes/scripts/amadeus/amadeus_external.py` |
| amadeus_sector_flow.py | ❌不存在 | ✅已存在 | `~/.hermes/scripts/amadeus/amadeus_sector_flow.py` |

原审计时间(2026-05-20)这些脚本尚未创建，2026-05-20下午已全部补齐。

### 🔴 P0：amadeus_emotion.py无过期检测（2026-05-21更正：已修复）

原问题：只找最新文件不检查日期，会静默使用昨日数据。

修复历史：
- v2.0(2026-05-20)：`load_limit_data()` 和 `load_index_data()` 增加过期检测，降级到旧文件时标记stale
- v3.0(2026-05-21)：`load_market_extra()` 补齐过期检测，与前两者一致

当前逻辑（三个函数统一）：
1. 精确匹配 market_{today}.json → 读取，返回 (data, True, today)
2. 不存在 → glob 找最新文件 → 读取，返回 (data, False, file_date) ← 标记stale
3. 都没有 → 返回 (None, False, "none")

输出：`stale_warnings` 列表 + `data_freshness: "fresh"/"stale"` 字段

### 🟡 P1：无交叉数据验证

各数据源独立采集，没有自动对比。例如：
- 指数数据：AKShare(新浪) vs 腾讯API — 未交叉验证
- 板块资金流：同花顺 vs 东方财富 — 未交叉验证（且单位可能不同）
- 北向资金：沪股通+深股通 — 当前只取沪股通

### 🟡 P1：外围市场数据经常为null

今日(5/20)实际数据：spx=null, a50=null, usdcny=null。只有道指/纳指/恒指有值。
原因：AKShare的新浪接口对部分品种返回空。无有效降级。

### 🟢 P2：板块资金流单位未核验

同花顺`stock_board_industry_summary_ths()`返回值偏小（如电力+13.44），可能是万元而非亿元。
需与东方财富数据交叉验证确定单位。

## 降级链路（当前实现）

```
指数:     AKShare → Ashare(新浪+腾讯) → "数据缺失"
板块:     AKShare board_industry_name_em → amadeus_data.py collect_sectors()
资金流:   同花顺 summary_ths → "板块资金流暂缺"
北向:     AKShare hsgt_hist_em → "北向资金暂缺"
连板:     强势股池 → 从涨停池推断
外围:     AKShare index_us_stock_sina → null
新闻:     4源并行，任一成功即用
情绪:     读cache → 无cache则"数据缺失"
价格:     腾讯API → "价格获取失败"
```

## 验证机制现状

### ✅ 已有
- 情绪温度公式固化在amadeus_emotion.py（禁止LLM手算）
- 模拟盘价格通过腾讯API校验
- 独立review subagent检查"数据是否可验证"
- JSON文件带collected_at时间戳
- REPORT标记强制

### ❌ 缺失（2026-05-21更新）
- ~~无自动交叉验证（多源比对）~~ 仍缺失
- ~~cache过期检测（emotion.py会用昨日数据）~~ → 已修复(v3.0 2026-05-21)
- LLM生成内容的编造检测 → 仍缺失
- 板块资金流单位核验 → 仍缺失
- subagent输出格式约束（JSON schema验证） → 仍缺失
- **数据质量等级制度** → 已新增 `data_quality.py` (2026-05-21)
- **报告数据来源标注** → 已新增，cron强制data_quality.py --report-fragment
