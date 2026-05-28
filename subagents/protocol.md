# protocol.md — Subagent 执行协议 v3.0

**重要**：本目录下的subagent具有真实执行能力，通过Hermes的 `delegate_task` 调用独立agent。

## 执行方式

所有subagent通过 `delegate_task()` 调用，每个subagent获得：
- 独立会话上下文（不了解报告生成过程）
- 独立终端会话
- 指定的toolsets

## 角色模板与执行映射

| 文件 | 角色 | 执行方式 | toolsets |
|------|------|----------|----------|
| review.md | 审查复盘 | delegate_task（独立审查） | terminal, web |
| market_data.md | 市场数据 | delegate_task（数据采集+验证） | terminal, web |
| technical.md | 技术分析 | delegate_task（指标计算） | terminal |
| financial.md | 财报分析 | delegate_task（财报查询） | terminal, web |
| theme.md | 题材分析 | delegate_task（板块研究） | web |
| macro.md | 宏观分析 | delegate_task（宏观数据） | terminal, web |
| risk.md | 风控审查 | delegate_task（排雷扫描） | terminal |
| report.md | 报告撰写 | 内联（不调delegate） | — |
| vision.md | 视觉分析 | vision工具 | vision |
| ops.md | 运维 | terminal | terminal |
| code.md | 代码 | delegate_task | terminal, file |

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
