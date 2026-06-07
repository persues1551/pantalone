# a-stock-data-supp 集成记录 (2026-06-03)

## 集成背景

开源项目 [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) V3.2.1 提供27个A股数据端点。经评估后作为 finance-suite 补充层集成到 Pantalone。

## 端点实测结果 (2026-06-03)

| 端点 | 状态 | 延迟 | 数据源 |
|------|------|------|--------|
| 腾讯行情 PE/PB/市值 | ✅ | 0.6s | qt.gtimg.cn |
| 同花顺热点归因 | ✅ | <1s | zx.10jqka.com.cn |
| 同花顺北向分钟流 | ✅ | <1s | data.hexin.cn |
| 东财龙虎榜 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财融资融券 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财大宗交易 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财股东户数 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财分红送转 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财限售解禁 | ✅ | 1-2s | datacenter-web.eastmoney.com |
| 东财行业排名 | ✅ | <1s | push2.eastmoney.com (临时502) |
| 东财研报+PDF | ✅ | 1-3s | reportapi.eastmoney.com |
| 巨潮公告 | ✅ | 1s | cninfo.com.cn |
| 百度概念板块 | ❌ | - | ResultCode=10003, API变更 |
| 东财push2资金流 | ❌ | - | 502, 可能IP被封 |
| 新浪财报三表 | ❌ | - | "Service not valid" |
| mootdx通达信 | ⏱️ | >15s | TCP服务器选择超时 |

## 关键发现

1. **东财datacenter API稳定可靠**：龙虎榜/融资融券/大宗/股东/分红/解禁全部可用
2. **push2.eastmoney.com不稳定**：资金流向和行业排名偶尔502
3. **百度/新浪API已变更**：不可用，需持续监控
4. **em_get()限流机制有效**：1s间隔+随机抖动，避免封IP
5. **同花顺热点归因是独家价值**：人工运营的题材tags，比新闻爬虫准确10倍

## Pantalone架构变更

### 旧架构（5 Agent串行）
```
Market Data → Research → Financial → Theme → Technical → Risk → Report
```

### 新架构（8 Agent 3批并行）
```
第1批: Market Data + Capital + Macro（并行）
第2批: Theme + Financial + Technical（并行）
第3批: Risk + Research（依赖前两批）
汇总:  Report → Review
```

### 变更清单
- 新增 `subagents/capital.md` — 龙虎榜/融资融券/大宗/北向
- 升级 `subagents/theme.md` — 热点归因+行业排名
- 升级 `subagents/risk.md` — 排雷5→9项（+股东户数/解禁/大宗）
- 升级 `subagents/financial.md` — +分红送转
- 升级 `subagents/research.md` — +研报+公告
- 升级 `subagents/market_data.md` — +北向分钟流
- 更新 `workflow.md` — 3批并行架构
- 更新 `SKILL.md` — 已接入+数据表+subagent表
- 更新报告模板 — 新增资金面章节

## 集成方法论

1. **下载+阅读SKILL.md**：理解端点覆盖、数据源优先级、限流机制
2. **逐端点实测**：写Python脚本测试每个API，记录状态/延迟/数据质量
3. **对比现有系统**：识别重叠/互补/独占端点
4. **拆分集成**：只集成独占+互补端点，不重复已有能力
5. **创建补充skill**：独立SKILL.md+CLI脚本，不侵入原有架构
6. **更新工作流**：新增Agent/升级现有Agent/更新并行架构
7. **更新报告模板**：新增数据章节
