# knowledge_base.md — 知识库管理

## 引用文件清单

| 文件 | 用途 | 更新频率 |
|------|------|----------|
| `references/2026-05-12-debug-session.md` | 调试会话记录 | 历史 |
| `references/akshare-news-sources.md` | AKShare新闻源 | 按需 |
| `references/architecture-restructuring-checklist.md` | 架构重构清单 | 按需 |
| `references/architecture-restructuring-plan.md` | 架构重构计划 | 按需 |
| `references/compliance-audit-2026-05-14.md` | 合规审计 | 季度 |
| `references/continuity-checklist.md` | 连续性检查清单 | 每日 |
| `references/cron-fault-tolerance-pattern.md` | Cron容错模式 | 按需 |
| `references/data-sources.md` | 数据源清单 | 按需 |
| `references/dexter-improvement-roadmap.md` | Dexter改进路线图 | 按需 |
| `references/dexter-research.md` | Dexter竞品研究 | 按需 |
| `references/directory-structure.md` | 目录结构 | 按需 |
| `references/geopolitical-event-analysis.md` | 地缘事件分析 | 按需 |
| `references/lolita-architecture-comparison.md` | Lolita架构对比 | 按需 |
| `references/market-data-structure.md` | 市场数据结构 | 按需 |
| `references/minimum-viable-split-pattern.md` | 最小可行拆分模式 | 按需 |
| `references/sina-api-format.md` | 新浪API格式 | 按需 |
| `references/sina-finance-search.md` | 新浪财经搜索 | 按需 |
| `references/simulator-integration-guide.md` | 模拟盘集成指南 | 按需 |
| `references/soul-restructuring-plan.md` | SOUL重构计划 | 已完成 |
| `references/subagent-v31-summary.md` | v3.1规则概要（已拆分到subagents/） | 历史 |
| `references/token-audit.md` | Token审计 | 月度 |
| `references/weixin-rate-limit-fix.md` | 微信限流修复 | 按需 |

## 上下文字段

每次Amadeus任务开始时，需加载：
1. 当前观察池状态（pool_manager.py status）
2. 最近一次复盘结论（amadeus_context.py summary）
3. 模拟盘状态（amadeus_sim_integrate.py status）

## 维护规则

- 新增references文件必须补充到本表
- 已完成的计划标记"已完成"，不删除
- 每季度清理过时文件
