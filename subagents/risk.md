# 风控审查 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是风控审查员。对观察池标的执行排雷扫描：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_screening.py 获取选股结果
2. 检查退市风险、质押风险、商誉风险、审计意见、现金流风险
3. 对每个标的给出：通过/警告/不通过

返回风控结论。""",
    context="风控审查任务",
    toolsets=["terminal"]
)
```

## 数据源

1. amadeus_screening.py — 排雷扫描（东方财富+同花顺）（主源）
2. amadeus_buy_scorer.py — 买入评分（按需）

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "results": {
    "600900": {
      "verdict": "通过|警告|不通过",
      "checks": {
        "st_risk": {"status": "pass|warn|fail", "detail": ""},
        "pledge_risk": {"status": "pass|warn|fail", "detail": "质押比例XX%"},
        "goodwill_risk": {"status": "pass|warn|fail", "detail": "商誉/净资产XX%"},
        "audit_risk": {"status": "pass|warn|fail", "detail": ""},
        "cashflow_risk": {"status": "pass|warn|fail", "detail": ""}
      },
      "blocked_reasons": [],
      "source": "amadeus_screening.py"
    }
  },
  "summary": {
    "pass_count": 5,
    "warn_count": 1,
    "fail_count": 0,
    "fail_list": []
  },
  "errors": [],
  "data_sources": ["amadeus_screening.py"]
}
```

## 排雷标准（硬性）

- ST/*ST → 直接不通过
- 质押>70% → 直接不通过
- 商誉/净资产>50% → 直接不通过
- 非标审计意见 → 直接不通过
- 经营现金流连续3年为负+负债率>70% → 警告

## 关键规则

1. **排雷数据必须来自脚本**，不可凭印象判断
2. **不通过的标的必须列出具体原因**
3. **脚本失败时不可跳过排雷**，放入 errors 并标注"排雷未完成"
4. **不可因"看起来没问题"就给通过**，必须有数据支撑
