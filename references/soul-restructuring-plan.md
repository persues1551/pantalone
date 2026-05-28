# SOUL.md 最小可行拆分方案 (2026-05-14)

## 当前问题

SOUL.md 1372行，§14（Subagent规则）占550行（40%），混合了原则/流程/规则/子Agent/权限/模板。

## 拆分原则

```
SOUL.md  → 我是谁、我信什么、我不能做什么（最高原则，不可违反）
router.md → 我接到任务后怎么分（路由、模型、触发条件）
workflow.md → 我怎么干（执行顺序、汇总、输出、复盘）
subagents/ → 每个角色能做什么不能做什么（权限边界）
rules/   → 各领域具体规则（已有，保持不变）
```

## 目标结构

### SOUL.md（~467行，减66%）

保留：
- §1 我是谁（10行）
- §2 核心定位（34行）
- §3 数字人格风格（23行）
- §4 核心原则（84行）— 核心，不可删
- §6 信息来源与证据分级（37行）
- §15 权限规则（110行）— 权限，不可删
- §16 中断恢复规则（18行）
- §20 推荐表达方式（71行）
- §21 我不能做什么（47行）— 边界，不可删
- §22 最终原则（23行）

移出：
- §5 工作流程 → workflow.md
- §7 综合研究 → rules/research_rules.md（新建）
- §8 投资分析 → rules/trading_rules.md（合并）
- §9 科研学术 → rules/research_rules.md（新建）
- §10 写作表达 → rules/writing_rules.md（新建）
- §11 数据方法 → rules/data_rules.md（合并）
- §12 技术工具 → rules/tech_rules.md（新建）
- §13 学习规划 → rules/learning_rules.md（新建）
- §14 架构Subagent → router.md + workflow.md + subagents/
- §17 输出规范 → workflow.md
- §18 风险控制 → rules/risk_rules.md（合并）
- §19 复盘进化 → workflow.md

### router.md（~250行）

从SOUL.md移入：
- §5.1 通用工作流
- §5.2 任务类型识别（详细版）
- §5.3 复杂任务处理
- §14.4 二 Subagent触发条件
- §14.4 三 任务分解格式
- §14.4 四 调用协议（部分）

### workflow.md（~350行）

从SOUL.md移入：
- §5.4 执行类任务纪律
- §14.4 六 Subagent执行顺序（4类）
- §14.4 七 结果汇总规则
- §14.4 八 强制执行摘要
- §14.4 十 主Agent自检清单
- §17 输出规范
- §19 复盘与进化机制

### subagents/（新建13文件，~349行）

| 文件 | 内容 |
|------|------|
| protocol.md | 调用协议（任务包格式+输出格式） |
| research.md | Research Agent权限边界 |
| market_data.md | Market Data Agent权限边界 |
| financial.md | Financial Agent权限边界 |
| macro.md | Macro Agent权限边界 |
| theme.md | Theme Agent权限边界 |
| technical.md | Technical Agent权限边界 |
| vision.md | Vision Agent权限边界 |
| code.md | Code Agent权限边界 |
| ops.md | Ops Agent权限边界 |
| report.md | Report Agent权限边界 |
| risk.md | Risk Agent权限边界+否决权 |
| checklist.md | 自检清单+防假Subagent+纪律 |

### rules/（现有5个 + 新建4个）

新建：
- rules/research_rules.md（§7综合研究 + §9科研学术）
- rules/writing_rules.md（§10写作表达）
- rules/tech_rules.md（§12技术工具）
- rules/learning_rules.md（§13学习规划）

## 拆分前后对比

| 维度 | 拆分前 | 拆分后 |
|------|--------|--------|
| SOUL.md | 1372行 | ~467行（-66%） |
| router.md | 95行 | ~250行 |
| workflow.md | 185行 | ~350行 |
| subagents/ | 不存在 | 13文件 ~349行 |
| rules/ | 5文件 | 9文件 |
| 文件总数 | 8个 | 17个 |
| 总行数 | ~1832行 | ~1832行（不变） |

## 引用关系

```
SOUL.md（最高原则）
  ├── router.md（任务路由）
  │     └── subagents/*.md（权限边界）
  ├── workflow.md（执行流程）
  │     └── subagents/checklist.md（自检清单）
  ├── rules/*.md（领域规则）
  └── templates/*.md（输出模板）
```

## 风险评估

| 风险 | 等级 | 应对 |
|------|------|------|
| 拆分后引用断裂 | 中 | 每个文件开头标注"参见"链接 |
| cron prompt引用SOUL章节 | 低 | cron prompt不直接引用§号 |
| Agent上下文加载变多 | 低 | 按需加载，不全量读取 |

## 执行状态

- [ ] 待主人确认后执行
- 备份已创建：SOUL.md.bak.20260514
