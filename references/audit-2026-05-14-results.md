# Amadeus v3.0 审计报告摘要 (2026-05-14)

## 审计前评分：4.4/10

| 维度 | 评分 | 核心问题 |
|------|------|----------|
| 数据采集 | 6/10 | 一键脚本硬bug |
| 财报分析 | 4/10 | 排雷无脚本、估值空白 |
| 情绪分析 | 6/10 | 连板数据源失真 |
| 题材分析 | 5/10 | 资金流长期缺失 |
| 技术触发 | 5/10 | RSI/MACD不入JSON |
| 模拟盘 | 2/10 | 数据库从未写入 |
| 风控 | 4/10 | Risk Agent未实现 |
| 组合管理 | 3/10 | 依赖不运作的模拟盘 |
| 评分复盘 | 5/10 | 3/5维度无法验证 |
| Subagent | 3/10 | 全部空壳 |
| 模型路由 | 5/10 | 路由冲突 |
| 自动化 | 5/10 | API无健康检查 |

## 三个结构性缺陷

1. **Execution Gap**：规则写了但没执行（模拟盘0条记录、Subagent全空壳）
2. **Data Pipeline Gap**：数据采了但核心链路断了（RSI不入JSON、资金流不采）
3. **Documentation Inflation**：3000行markdown vs 2000行Python

## 修复统计

| 优先级 | 数量 | 状态 |
|--------|------|------|
| P0 | 10 | ✅ 全部完成 |
| P1 | 17 | ✅ 全部完成 |
| P2 | 全部 | ✅ 全部完成 |

## 修复后评分：约6.5/10

## 防复发机制（12项全部有效）

1. cron自动调用daily_update
2. 实时价格获取（腾讯API）
3. 单票25%上限自动拦截
4. 总暴露70%上限自动拦截
5. 禁止买入条件自动检查
6. WATCHLIST与pool_rules同步
7. 涨停阈值板块区分规则
8. cron报告强制调用sim步骤
9. L3/L4强制审查流程
10. collect_all.sh全流程
11. 模型路由统一
12. Subagent降级

## 新增/修改文件清单

| 文件 | 操作 |
|------|------|
| amadeus_collect_all.sh | 修改（修复废弃引用） |
| amadeus_sim_integrate.py | 重写v2.0（实时价格+单票检查） |
| amadeus_indicators.py | 重写v2.0（RSI入JSON+禁止买入检查） |
| amadeus_screening.py | 新建（排雷5项） |
| amadeus_valuation.py | 新建（PE-Band估值） |
| amadeus_market_filter.py | 新建（大盘四级过滤） |
| amadeus_buy_scorer.py | 新建（买入评分100分制） |
| rules/data_rules.md | 修改（涨停阈值区分） |
| rules/risk_rules.md | 修改（买入规则+三层清仓） |
| workflow.md | 修改（金额统一+模拟盘步骤） |
| router.md | 修改（模型路由统一） |
| subagents/protocol.md | 重写（降级为提示词模板库） |
| subagents/checklist.md | 重写（降级为自检清单） |
| subagents/review.md | 新建（审查复盘型v3.2） |
| SKILL.md | 修改（v3.0.0+全面更新） |
