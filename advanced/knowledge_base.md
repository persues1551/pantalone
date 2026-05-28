# knowledge_base.md — 知识库管理

## 参考文件清单

| 文件 | 路径 | 内容 |
|------|------|------|
| 灵魂文档 | `SOUL.md` | 投资哲学、价值观、工作原则、能力范围、表达方式、禁止事项 |
| 任务路由 | `router.md` | 任务类型识别、模型选择规则 |
| 工作流程 | `workflow.md` | 核心流程、预测闭环、迭代原则、审批规则 |
| 数据规则 | `rules/data_rules.md` | 数据铁律、连板规则、事实校验、数据采集体系 |
| 交易规则 | `rules/trading_rules.md` | 情绪温度、排雷检查、基本面评级、资金流分析 |
| 观察池规则 | `rules/pool_rules.md` | 观察股格式、池子结构、自动入池/退池规则 |
| 风险控制 | `rules/risk_rules.md` | 投资风险、Token优化、会话管理 |
| 多资产规则 | `rules/multi_asset_rules.md` | 债券/汇率/黄金/商品/ETF分析 |
| 复盘模板 | `templates/review_template.md` | 13段完整复盘模板 |
| 盘前模板 | `templates/morning_template.md` | 9段盘前预案模板 |
| 快速建议 | `templates/quick_advice.md` | 核心判断+模拟计划+回避清单+纪律 |
| 测试用例 | `eval/test_cases.md` | 情绪温度/排雷/评级/连板/资金流测试 |
| 评分标准 | `eval/scoring.md` | 6维度100分制、情绪温度分级 |
| 失败规则 | `eval/failure_rules.md` | 故障排查手册 |
| 任务日志 | `logs/task_log.md` | 工具调用日志规范 |
| 复盘日志 | `logs/review_log.md` | 预测记录、验证结果、教训记录 |
| 更新日志 | `logs/update_log.md` | 规则变更、脚本修复、配置变更记录 |
| 自学习 | `advanced/self_learning.md` | AIHOT日报扫描、迭代流程 |
| 反脆弱 | `advanced/antifragile.md` | 三级降级、API故障预案、推送重试 |
| 知识库管理 | `advanced/knowledge_base.md` | 本文件 |

## 外部参考文件

| 文件 | 路径 | 内容 |
|------|------|------|
| 数据源文档 | `references/data-sources.md` | AKShare 已验证接口、不稳定接口、缺失数据清单 |
| 新浪API格式 | `references/sina-api-format.md` | 新浪财经实时行情 API 完整格式文档 |
| AKShare新闻源 | `references/akshare-news-sources.md` | AKShare新闻接口实测对比 |
| Token审计 | `references/token-audit.md` | Token 消耗审计报告 |
| Dexter研究 | `references/dexter-research.md` | Dexter/Dexter-A研究报告 |
| Dexter改进路线图 | `references/dexter-improvement-roadmap.md` | Dexter改进方向和借鉴点 |
| 地缘政治分析 | `references/geopolitical-event-analysis.md` | 地缘政治事件→受益标的分析框架 |
| 新浪财经搜索 | `references/sina-finance-search.md` | Sina Finance实时新闻采集方法 |
| 目录结构 | `references/directory-structure.md` | 完整目录结构文档 |
| 微信限流修复 | `references/weixin-rate-limit-fix.md` | iLink API限流问题修复记录 |
| 架构重构计划 | `references/architecture-restructuring-plan.md` | 模块化重构方案 |
| 架构重构清单 | `references/architecture-restructuring-checklist.md` | 重构查漏补缺清单 |
| Lolita对比 | `references/lolita-architecture-comparison.md` | Lolita架构对比分析 |
| 调试会话 | `references/2026-05-12-debug-session.md` | 关键调试过程记录 |
| 连续性检查清单 | `references/continuity-checklist.md` | 系统组件连续性检查清单 |
| Cron容错模式 | `references/cron-fault-tolerance-pattern.md` | context_from备份去重模式 |
| 市场数据结构 | `references/market-data-structure.md` | amadeus_data.py输出字段说明 |
| 模拟盘集成指南 | `references/simulator-integration-guide.md` | amadeus_sim_integrate.py使用说明 |
| 合规审计报告 | `references/compliance-audit-2026-05-14.md` | 首次全面合规审计报告 |

## 上下文字段说明

| 字段 | 用途 | 更新时机 |
|------|------|----------|
| market_stance | 当前市场立场（偏多/偏空/震荡） | 每次复盘更新 |
| prediction_streak | 预测准确率连击 | 每次验证预测后 |
| recent_predictions | 最近10条预测记录 | 每次写入预测时 |
| sector_trends | 板块趋势跟踪 | 复盘发现主线变化时 |
| stock_notes | 个股分析笔记 | 分析新标的或更新结论时 |
| lessons_learned | 教训（最近20条） | 发现错误/优化时 |
| pending_todos | 待办事项 | 发现可改进项时 |

## 知识库维护规则

### 更新频率

| 类型 | 频率 | 负责人 |
|------|------|--------|
| 规则文件 | 每次规则变更时 | Amadeus自动 |
| 模板文件 | 每次模板变更时 | Amadeus自动 |
| 参考文件 | 每次发现新知识时 | Amadeus自动 |
| 上下文文件 | 每次复盘/预测时 | Amadeus自动 |

### 更新流程

1. 发现需要更新的内容
2. 评估影响范围
3. 更新相关文件
4. 记录到 `logs/update_log.md`
5. 验证更新正确

### 版本管理

- 每次重大更新记录版本号
- 版本号格式：vX.Y.Z（主版本.次版本.修订版本）
- 主版本：架构级变更
- 次版本：功能新增
- 修订版本：bug修复

## 大结果持久化

当工具返回结果过大（>5000字符）时，不将完整结果注入上下文，而是：

1. 保存到 `~/.hermes/cache/amadeus/scratchpad/` 目录
2. 上下文中只保留摘要（前200字符 + "..." + 文件路径）
3. 需要详细数据时，从文件读取

## 知识图谱

### 核心概念关系

```
SOUL.md（灵魂/价值观）
    ↓ 指导
router.md（任务路由）
    ↓ 分发
workflow.md（工作流程）
    ↓ 执行
rules/（规则）
    ↓ 约束
templates/（模板）
    ↓ 输出
eval/（评估）
    ↓ 反馈
logs/（日志）
    ↓ 记录
advanced/（高级功能）
    ↓ 迭代
```

### 知识流向

```
外部数据 → 数据采集 → 数据处理 → 分析判断 → 报告输出 → 复盘验证 → 知识沉淀
```

## 知识库健康检查

### 每月检查项

| 检查项 | 检查内容 | 异常处理 |
|--------|----------|----------|
| 文件完整性 | 所有文件是否存在 | 补充缺失文件 |
| 内容一致性 | 各文件引用是否正确 | 修复错误引用 |
| 过时内容 | 是否有过时信息 | 更新或删除 |
| 重复内容 | 是否有重复定义 | 合并重复内容 |

### 健康指标

| 指标 | 正常范围 | 异常处理 |
|------|----------|----------|
| 文件数量 | 20个 | 检查是否有缺失 |
| 引用正确率 | 100% | 修复错误引用 |
| 更新频率 | 每周至少1次 | 检查是否有遗漏 |
| 知识覆盖度 | >90% | 补充缺失知识 |
