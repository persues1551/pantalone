# 10模块投研系统架构 (2026-05-21)

## 模块清单

| # | 模块 | Skill位置 | 核心功能 |
|---|------|-----------|---------|
| 1 | Policy-Monitor | `investment/policy-monitor` | 政策新闻监控+影响评估 |
| 2 | Stock-Analyst | `investment/pantalone` | OCIFQ(60%)+择时(40%) |
| 3 | Daily-Trade-Review | `investment/pantalone` | 盘前/午间/收盘三档cron |
| 4 | Quant-KB | `investment/quant-kb` | 量化策略/指标/模型知识库 |
| 5 | Stock-Watcher | `investment/stock-watcher` | 盘中异动监控+自动推送 |
| 6 | A-Shares-Data | `investment/pantalone` | AKShare+Tushare数据源 |
| 7 | Report-Extractor | `core/report-extractor` | PDF研报/财报解析 |
| 8 | Risk-Alert-System | `investment/risk-alert-system` | 三层风险监控体系 |
| 9 | Backtest-Engine | `core/backtest-engine` | 策略回测框架 |
| 10 | Skill-Vetter | `core/skill-vetter` | 技能安全审计 |

## 新增脚本

| 脚本 | 功能 | Cron |
|------|------|------|
| `amadeus_watcher.py` | 盘中异动监控（涨跌幅/止损/涨停/跌停） | `*/30 9-11,13-15 * * 1-5` |
| `amadeus_knowledge.py` | 知识沉淀（预测追踪/实体档案/错误记录） | `30 16 * * 1-5` + `0 17 * * 5` |

## 五层报告架构

```
Level 4: 多视角审议（周报）
├─ 多空辩论（多头/空头/风险经理/PM）
├─ 技术共识（5种方法交叉验证）
└─ 策略回测（Backtest-Engine）

Level 3: 深度研究（周报）
├─ OCIFQ完整评估（五维评分）
├─ 研报/财报分析（Report-Extractor）
└─ 量化策略参考（Quant-KB）

Level 2: 日常监控（盘中）
├─ 异动监控（Stock-Watcher每30分钟）
├─ 风险预警（Risk-Alert实时）
└─ 政策监控（Policy-Monitor每日）

Level 1: 日常报告（盘前/午间/收盘）
├─ 盘前：政策+风险+OCIFQ+策略
├─ 午间：早盘验证+异动回顾
└─ 收盘：风险+行业断层+池管理
```

## 模板清单

| 模板 | 文件 | 用途 |
|------|------|------|
| 盘前早报v3.5 | `templates/morning_report_v3.5.md` | 政策+风险+OCIFQ+量化策略 |
| 收盘复盘v3.5 | `templates/closing_report_v3.5.md` | 风险评估+行业断层验证+综合评分 |
| 周报深度研究v3.5 | `templates/weekly_report_v3.5.md` | 研报分析+策略回测+多空辩论+技术共识 |
| 多空辩论 | `templates/bull_bear_debate.md` | 多头/空头/风险经理/PM决策 |
| 技术共识 | `templates/technical_consensus.md` | MA/RSI/MACD/布林带/量价交叉验证 |

## 通用技能 vs 领域技能

**通用技能（core/，Amadeus层面）**：
- knowledge-crystallizer - 知识沉淀
- backtest-engine - 回测引擎
- skill-vetter - 安全审计
- report-extractor - 文档解析

**领域技能（investment/，Pantalone层面）**：
- pantalone - 投研主模块
- stock-picking - OCIFQ选股
- stock-watcher - 盘中异动监控
- quant-kb - 量化知识库
- policy-monitor - 政策监控
- risk-alert-system - 风险预警
- amadeus-report-review - 投资报告审查
- amadeus-us-market - 美股分析
- finance-suite - 金融全家桶
- vibe-trading-setup - Vibe-Trading配置
