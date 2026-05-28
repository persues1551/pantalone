# Subagent 执行协议 v3.4（2026-05-15 验证）

## 前提条件

**cron任务必须在enabled_toolsets中包含`delegation`，否则delegate_task静默不可用。**

已验证：8个Amadeus cron任务全部加了delegation。

## 角色映射

| 文件 | 角色 | toolsets | 调用时机 |
|------|------|----------|----------|
| review.md | 审查复盘 | terminal, web | 报告后（必须） |
| market_data.md | 市场数据 | terminal | 并行采集 |
| technical.md | 技术分析 | terminal | 并行采集 |
| financial.md | 财报分析 | terminal, web | 按需 |
| theme.md | 题材分析 | web | 并行采集 |
| macro.md | 宏观分析 | terminal, web | 并行采集 |
| risk.md | 风控审查 | terminal | 并行采集 |
| report.md | 报告撰写 | 内联 | 汇总阶段 |

## 并行架构

```
1. 加载上下文
2. delegate_task(tasks=[market_data, technical, macro, theme, risk]) 并行
3. 综合生成报告
4. delegate_task → review 独立审查
```

## 已知陷阱

1. delegation工具集缺失 → delegate_task静默不可用
2. Agent默认自我审查 → prompt必须强制"不可自己审查"
3. 串行执行效率低 → 用delegate_task batch模式并行
