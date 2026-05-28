# Lolita 架构对比分析

## 对比日期
2026-05-13

## Lolita 架构

```
lolita/
├── soul.md
├── router.md
├── memory.md
├── tools.md
├── workflow.md
├── skills/
│   ├── investment.md
│   ├── academic.md
│   ├── writing.md
│   ├── tech.md
│   ├── info.md
│   └── health.md
├── advanced/
│   ├── frontier.md
│   ├── anti_bubble.md
│   ├── self_learning.md
│   ├── review.md
│   ├── antifragile.md
│   └── knowledge_base.md
├── eval/
│   ├── test_cases.md
│   ├── scoring.md
│   └── failure_rules.md
└── logs/
    ├── task_log.md
    ├── review_log.md
    └── update_log.md
```

## 核心差异

| 维度 | Amadeus (旧) | Lolita | Amadeus (新) |
|------|--------------|--------|--------------|
| 文档化 | 集中（单文件800行） | 分散（多文件） | 分散（20个模块） |
| 可执行性 | 强（Python脚本） | 弱（纯文档） | 强（保留脚本） |
| 模块化 | 弱 | 强 | 强 |
| 评估体系 | 无 | 有 | 有（eval/） |
| 自学习 | 部分 | 完整 | 完整（advanced/） |
| 反脆弱 | 无 | 有 | 有（advanced/） |
| 数据采集 | 强 | 未知 | 强（保留脚本） |
| 实际推送 | 有（Cron+微信） | 未知 | 有（保留） |

## 借鉴内容

### 已借鉴
1. **模块化目录结构** - rules/, templates/, eval/, logs/, advanced/
2. **router.md** - 任务路由模块
3. **workflow.md** - 工作流程模块
4. **eval/** - 评估体系（test_cases, scoring, failure_rules）
5. **logs/** - 日志体系（task_log, review_log, update_log）
6. **advanced/** - 高级功能（self_learning, antifragile, knowledge_base）

### 保留优势
1. **Python脚本** - 数据采集、分析、推送能力
2. **Cron调度** - 自动化推送
3. **微信集成** - 实际消息推送
4. **模拟盘** - 20万模拟盘引擎

## 架构改进

### 旧架构问题
- 单文件800行，维护困难
- 职责混杂，难以定位
- 无评估体系，无法量化迭代
- 无日志体系，无法追溯

### 新架构优势
- 20个独立模块，职责单一
- 易于查找和修改
- 评估体系可量化迭代效果
- 日志体系可追溯任务/复盘/更新

## 执行记录

### 执行步骤
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

### 关键决策
- 保留Python脚本执行能力（Lolita纯文档，我们保留脚本）
- 保留Cron调度和微信推送能力
- 新增评估和日志体系（借鉴Lolita）
- 新增反脆弱和自学习机制（借鉴Lolita）
