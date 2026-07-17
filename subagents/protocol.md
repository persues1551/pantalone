# protocol.md — Subagent 执行协议 v4.0

**重要**：本目录下的subagent具有真实执行能力，通过Hermes的 `delegate_task` 调用独立agent。

## 结构化输出（新增 v4.0）

Schema是可选契约，定义在 `schemas.py`，用于校验和渲染跨Agent数据。当前Markdown subagent通过 `delegate_task` 执行；仅在调用方显式接入结构化输出时才使用Pydantic模型：

| 文件 | Schema类 | 用途 |
|------|---------|------|
| market_data.md | `MarketDataReport` | 市场数据汇总 |
| technical.md | `TechnicalAnalysisReport` | 技术分析 |
| financial.md | `FinancialReport` | 财报分析 |
| theme.md | `ThemeAnalysisReport` | 题材分析 |
| macro.md | `MacroAnalysisReport` | 宏观分析 |
| risk.md | `RiskScreeningReport` | 风控排雷 |
| capital.md | `CapitalFlowReport` | 资金面分析 |
| research.md | `ResearchCoverageReport` | 研报覆盖 |
| review.md | `ReviewResult` | 审查复盘 |
| etf_reviewer.md | `ETFReviewResult` | ETF审查 |

**模式**：
1. 默认 `delegate_task` 返回文本，不宣称Hermes会自动调用Pydantic；
2. 调用方需要结构化数据时，可显式按对应Schema解析和校验；
3. `render_*` 函数将已校验实例转回Markdown供下游消费；
4. provider或调用路径不支持结构化输出时，保留自由文本并明确降级。

## 执行方式

所有subagent通过 `delegate_task()` 调用，每个subagent获得：
- 独立会话上下文（不了解报告生成过程）
- 独立终端会话
- 指定的toolsets

## 角色模板与执行映射

| 文件 | 角色 | 执行方式 | toolsets | Schema |
|------|------|----------|----------|--------|
| review.md | 审查复盘 | delegate_task（独立审查） | terminal, web | ReviewResult |
| market_data.md | 市场数据 | delegate_task（数据采集+验证） | terminal, web | MarketDataReport |
| technical.md | 技术分析 | delegate_task（指标计算） | terminal | TechnicalAnalysisReport |
| financial.md | 财报分析 | delegate_task（财报查询） | terminal, web | FinancialReport |
| theme.md | 题材分析 | delegate_task（板块研究） | web | ThemeAnalysisReport |
| macro.md | 宏观分析 | delegate_task（宏观数据） | terminal, web | MacroAnalysisReport |
| risk.md | 风控审查 | delegate_task（排雷扫描） | terminal | RiskScreeningReport |
| capital.md | 资金面 | delegate_task | terminal, web | CapitalFlowReport |
| research.md | 研报覆盖 | delegate_task | terminal, web | ResearchCoverageReport |
| etf_reviewer.md | ETF审查 | delegate_task | terminal, web | ETFReviewResult |
| report.md | 报告撰写 | 内联（不调delegate） | — | — |
| vision.md | 视觉分析 | vision工具 | vision | — |
| ops.md | 运维 | terminal | terminal | — |
| code.md | 代码 | delegate_task | terminal, file | — |

## Cron报告审查流程

每个cron报告生成后必须经过独立审查：
1. 生成报告
2. `delegate_task` 调用review.md的审查流程
3. 审查通过(score≥70) → 发送
4. 审查不通过 → 修改后重新审查（最多1轮）
5. 仍有critical问题 → 升级给用户

## 输出格式

报告中**不标注**角色分工标签（如"[Market Data] 输出"）。
直接输出分析内容，格式参考 `templates/` 目录下的模板。

subagent内部使用结构化JSON输出时，必须遵循 `schemas.py` 定义的字段名和类型。
