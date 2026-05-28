# update_log.md — 更新日志规范

## 日志格式

每次规则变更、脚本修复、配置变更后，记录更新日志。

### 记录格式

```markdown
## YYYY-MM-DD HH:MM - 更新标题

**类型**：规则变更 / 脚本修复 / 配置变更 / 新增功能
**模块**：影响的模块（rules/trading_rules.md 等）
**变更内容**：
- 具体变更1
- 具体变更2

**原因**：为什么要变更
**影响**：变更带来的影响
**验证**：如何验证变更正确
```

## 示例

```markdown
## 2026-05-13 15:37 - 架构重构：模块化拆分

**类型**：规则变更
**模块**：SKILL.md → router.md + workflow.md + rules/ + templates/ + eval/ + logs/ + advanced/
**变更内容**：
- 将800行SKILL.md拆分为18个独立模块
- 新增router.md（任务路由）
- 新增workflow.md（工作流程）
- 新增rules/目录（5个规则文件）
- 新增templates/目录（3个模板文件）
- 新增eval/目录（3个评估文件）
- 新增logs/目录（3个日志文件）
- 新增advanced/目录（3个高级功能文件）

**原因**：借鉴Lolita架构，提高模块化程度和可维护性
**影响**：所有cron job需要更新引用路径
**验证**：测试cron job加载正常
```

## 变更类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 规则变更 | SKILL.md/SOUL.md规则修改 | "新增不操作清单第9条" |
| 脚本修复 | Python脚本bug修复 | "修复amadeus_data.py KeyError" |
| 配置变更 | config.yaml配置修改 | "调整chunk间隔3→5秒" |
| 新增功能 | 新增模块/工具/规则 | "新增地缘政治事件分析模块" |

## 变更记录

### 2026-05-13

| 时间 | 类型 | 模块 | 变更 |
|------|------|------|------|
| 15:37 | 规则变更 | 全局 | 架构重构：模块化拆分（借鉴Lolita） |
| 12:06 | 脚本修复 | gateway/platforms/weixin.py | 修复iLink限流后session损坏问题 |
| 12:06 | 配置变更 | config.yaml | 调整chunk间隔3→5秒，重试5→6次 |

### 2026-05-12

| 时间 | 类型 | 模块 | 变更 |
|------|------|------|------|
| 19:08 | 规则变更 | SKILL.md | 新增多资产扩展模块（v2.2） |
| 16:56 | 脚本修复 | amadeus_simulator.py | 修复INIT_CAPITAL硬编码bug |
| 15:40 | 新增功能 | amadeus_context.py | 投研上下文持久化（v2.3） |

## 变更统计

| 类型 | 本月次数 |
|------|----------|
| 规则变更 | 3 |
| 脚本修复 | 5 |
| 配置变更 | 2 |
| 新增功能 | 4 |

## 变更审批规则

参见 `workflow.md` 中的「重要改动审批规则」。

**可直接执行不审批**：
- 纯bug修复（脚本报错、接口403、字段缺失等）
- 已确认方案的执行（主人已说OK的）
- 文档/格式/注释类改动
- 安全漏洞修复

**必须审批**：
- 架构级变更
- Cron任务新增/大幅修改
- 数据采集流程变更
- 模型/Provider切换
- 费用相关变更

---

## 2026-05-14 系统修复与审计

### 规则修复
- workflow.md "系统迭代原则"：区分bug修复（可直接执行）和规则变更（必须确认），对齐SOUL.md §15.2
- workflow.md "定时推送配置"：更新为16个cron任务，盘前早报改为08:30
- router.md "多模型协作路由"：盘前/午盘/收盘报告改为L3→DeepSeek，与SOUL.md §14.4对齐
- SOUL.md §15.2：添加cron自动推送预授权例外

### 脚本修复
- amadeus_sim_integrate.py：新建模拟盘集成脚本（status/daily_update/record）
- amadeus_pool_manager.py：修复盘前时段价格显示（昨收价替代current=0）
- amadeus_predictions.py：重写match_dimension函数，新增板块数据验证
- amadeus_data.py：新增collect_sectors()采集496个行业板块数据；涨停池head(20)→head(50)

### 数据修复
- 14只观察股entry_price更新为昨收价
- 300433蓝思科技pool从"观察"修正为"C"

### 安全修复
- config.yaml权限改为600（API密钥保护）

## 2026-05-14 SOUL.md §14 Subagent实执行规则v3.1

**修改内容**：SOUL.md §14.4~§14.10 替换为 Subagent 实执行规则 v3.1
**行数变化**：原454行 → 新509行（+55行）
**新增关键内容**：
- 12个章节：核心目标/触发条件/任务分解格式/调用协议/权限边界/执行顺序/汇总规则/执行摘要/自检清单/防假Subagent/最终纪律
- 11个Subagent详细权限边界（每个有"可以做/不能做"）
- 4类任务强制执行顺序（投资/科研/技术/写作）
- 防止"假Subagent"的10条禁令
- 主Agent自检清单（9项）
- Subagent自检清单（7项）
**备份**：SOUL.md.bak.20260514
