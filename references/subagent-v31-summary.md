# Subagent 实执行规则 v3.1 摘要

完整规则已整合到 `SOUL.md §14.4`（2026-05-14）。

## 核心变化

从"概念性角色名"变为"实际执行单元"。

## 12个章节

| 章节 | 内容 |
|------|------|
| 一、核心目标 | 6条禁止事项 |
| 二、触发条件 | 13类必须启用 + 6类可不启用 + L0-L4映射 |
| 三、任务分解格式 | Task Decomposition模板 |
| 四、调用协议 | 任务包格式 + 统一输出格式 |
| 五、权限边界 | 11个Subagent详细"可以做/不能做" |
| 六、执行顺序 | 4类任务强制流程（投资/科研/技术/写作） |
| 七、汇总规则 | 6件事 + 冲突处理格式 |
| 八、强制执行摘要 | L3/L4必须包含 |
| 九、Subagent自检 | 7项清单 |
| 十、主Agent自检 | 9项清单 |
| 十一、防假Subagent | 10条禁令 + 纠错格式 |
| 十二、最终纪律 | 8条底线 |

## 关键规则

- L0/L1：可不拆Subagent
- L2：视情况拆1-2个
- L3/L4：必须拆Subagent
- 高风险：必须拆 + Risk Agent
- Risk Agent永远用DeepSeek，不允许降级小米
- Risk Agent否决高于所有其他Subagent

## 执行顺序（投资报告）

```
Router Agent → Market Data → Financial → Theme → Technical → Macro → Report → Risk → Main
```

## 备份

SOUL.md.bak.20260514
