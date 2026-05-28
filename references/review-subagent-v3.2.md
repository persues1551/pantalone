# Review Subagent v3.2 — 审查复盘型规则摘要

完整文件：`~/.hermes/skills/investment/amadeus/subagents/review.md`（397行）

## 核心要点

- L3/L4任务必须经过审查才能输出
- 7种Reviewer角色（投资/科研/写作/数据/技术/商业/学习）
- 审查结论：通过/有条件通过/退回修改/否决
- Review Subagent ≠ Risk Agent：Review查质量，Risk查安全

## 执行流程

```
专业Subagent完成 → 生成草稿 → Review Subagent审查 → Risk Agent最终审查 → 输出
```

## 投资类审查重点（Professional Investor Reviewer）

- 数据是否真实、是否存在未来函数、是否盘后倒推
- 财报是否支撑评级、估值是否合理
- 技术触发是否具体、是否有失效条件
- 仓位是否合理、风控是否完整
- 模拟盘是否可能被误解为实盘建议

## 否决条件

- 数据缺失却给确定结论
- 财报缺失却给A/B评级
- 模拟盘没有触发条件/失效条件
- 使用T日结果倒推T日预测
