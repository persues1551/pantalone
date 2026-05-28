# 架构重构计划

## 日期
2026-05-13

## 背景

借鉴 Lolita 架构，将 Amadeus 从单文件 800 行 SKILL.md 重构为 20 个独立模块。

## 新架构目录结构

```
amadeus/
├── SOUL.md                    (灵魂文档，最高优先级)
├── SKILL.md                   (精简版，仅保留核心引用)
├── router.md                  (任务路由)
├── workflow.md                (工作流程)
├── rules/
│   ├── data_rules.md          (数据规则)
│   ├── trading_rules.md       (交易规则)
│   ├── pool_rules.md          (观察池规则)
│   ├── risk_rules.md          (风险控制)
│   └── multi_asset_rules.md   (多资产规则)
├── templates/
│   ├── review_template.md     (复盘模板)
│   ├── morning_template.md    (盘前模板)
│   └── quick_advice.md        (快速建议模板)
├── eval/
│   ├── test_cases.md          (测试用例)
│   ├── scoring.md             (评分标准)
│   └── failure_rules.md       (失败规则)
├── logs/
│   ├── task_log.md            (任务日志规范)
│   ├── review_log.md          (复盘日志规范)
│   └── update_log.md          (更新日志规范)
├── advanced/
│   ├── self_learning.md       (自学习机制)
│   ├── antifragile.md         (反脆弱设计)
│   └── knowledge_base.md      (知识库管理)
├── scripts/                   (已有，保持不变)
├── references/                (已有，保持不变)
└── cache/                     (已有，保持不变)
```

## 规则映射表

| 新模块 | 来源 | 核心内容 |
|--------|------|----------|
| router.md | SKILL.md开头 | 任务类型识别、模型选择规则 |
| workflow.md | 核心流程+迭代原则 | 10步核心流程、预测闭环、审批规则 |
| rules/data_rules.md | 数据铁律+连板规则 | 数据铁律、连板规则、事实校验、数据采集体系 |
| rules/trading_rules.md | 情绪温度+排雷+评级 | 情绪温度公式、排雷5项、基本面A-E、资金流分析 |
| rules/pool_rules.md | 观察池相关 | 观察股格式、池子结构、自动入池/退池规则 |
| rules/risk_rules.md | 风险控制+Token优化 | 投资风险、Token优化、会话管理 |
| rules/multi_asset_rules.md | 多资产模块 | 债券/汇率/黄金/商品/ETF分析 |
| templates/review_template.md | 收盘复盘模板 | 13段完整复盘模板 |
| templates/morning_template.md | 盘前预案模板 | 9段盘前预案模板 |
| templates/quick_advice.md | 快速建议格式 | 核心判断+模拟计划+回避清单+纪律 |
| eval/test_cases.md | 新建 | 情绪温度/排雷/评级/连板/资金流测试用例 |
| eval/scoring.md | 综合评分 | 6维度100分制、情绪温度分级 |
| eval/failure_rules.md | 故障排查 | Cron静默停止、API断连、数据缺失处理 |
| logs/task_log.md | 草稿本 | 工具调用日志、数据采集记录、自动清理 |
| logs/review_log.md | 预测闭环 | 预测记录、验证结果、教训记录 |
| logs/update_log.md | 新建 | 规则变更、脚本修复、配置变更记录 |
| advanced/self_learning.md | AIHOT自迭代 | 扫描流程、评估标准、行动规则 |
| advanced/antifragile.md | 新建 | 三级降级、API故障预案、推送重试 |
| advanced/knowledge_base.md | 上下文持久化 | 参考文件清单、上下文字段、维护规则 |

## 执行步骤

1. 创建目录结构（rules/, templates/, eval/, logs/, advanced/）
2. 创建 router.md + workflow.md
3. 拆分 rules/ 目录（5个文件）
4. 创建 templates/ 目录（3个文件）
5. 创建 eval/ 目录（3个文件）
6. 创建 logs/ 目录（3个文件）
7. 创建 advanced/ 目录（3个文件）
8. 精简 SKILL.md（800行→120行）
9. 更新所有引用路径
10. 验证 cron job 加载正常

## 关键决策

1. **保留Python脚本执行能力** - Lolita纯文档，我们保留脚本
2. **保留Cron调度和微信推送能力** - 实际推送能力
3. **新增评估和日志体系** - 借鉴Lolita
4. **新增反脆弱和自学习机制** - 借鉴Lolita

## 风险控制

1. **原子切换** - 先创建新文件，验证无误后再删除旧内容
2. **引用检查** - 确保所有内部链接正确
3. **Cron测试** - 切换后立即测试一个cron job
4. **回滚方案** - 保留原SKILL.md备份
