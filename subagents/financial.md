# 财报分析 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是财报分析专家。分析{股票代码}的财务数据：
1. 最近4个季度营收/利润趋势
2. ROE/毛利率/净利率变化
3. 现金流质量
4. 估值水平（PE/PB/PEG）
5. 与同行业对比

返回财务面评分和结论。""",
    context="财报分析任务",
    toolsets=["terminal", "web"]
)
```

## 关注重点

- 营收增长是否持续
- 利润质量（扣非vs非经常）
- 现金流是否匹配利润
- 估值是否合理
