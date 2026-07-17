# Pantalone Subagents

本目录保存Pantalone按需调用的专业角色和可选结构化数据契约。Subagent不是daemon，也不会因文件存在而自动执行。

## 角色

| 文件 | 职责 | 可选Schema |
|---|---|---|
| `market_data.md` | 市场数据 | `MarketDataReport` |
| `technical.md` | 技术分析 | `TechnicalAnalysisReport` |
| `financial.md` | 财务分析 | `FinancialReport` |
| `theme.md` | 题材分析 | `ThemeAnalysisReport` |
| `macro.md` | 宏观分析 | `MacroAnalysisReport` |
| `risk.md` | 风险审查 | `RiskScreeningReport` |
| `capital.md` | 资金分析 | `CapitalFlowReport` |
| `research.md` | 研报与公告 | `ResearchCoverageReport` |
| `review.md` | 独立复核 | `ReviewResult` |
| `etf.md` | ETF分析 | 共享ETF枚举 |
| `etf_reviewer.md` | ETF复核 | `ETFReviewResult` |

## 执行边界

- 由`router.md`和`workflow_v4_unified.md`决定是否调用；
- 外部脚本必须检查`HERMES_HOME`和文件存在性；
- 缺失或失败时写明errors并降级；
- Schema是可选契约，不代表Hermes会自动执行`with_structured_output`；
- `protocol.md`是执行协议，`checklist.md`是输出前清单，`schemas.py`是数据模型，均不作为独立delegate目标。