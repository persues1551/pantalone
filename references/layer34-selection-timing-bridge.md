# Layer3→4研究接口 — 选股结果补充技术证据

## 流程

```
OCIFQ选股完成 →
  输出候选列表(标的+评分) →
    在外部能力真实可用时调用 short_term_analyzer.py →
      每个标的返回技术面评分与证据方向 →
        综合输出: 证据强弱、缺口和完整建仓门槛复核状态
```

## 脚本

`layer34_bridge.py` — 可选外部能力；缺失时按本文手工整理技术证据，不得声称脚本已运行

```python
# 输入: OCIFQ选股结果JSON
# 处理: 对每个标的补充技术证据
# 输出: 证据汇总与完整建仓门槛复核表

输入格式:
{
  "candidates": [
    {"code": "600309", "name": "万华化学", "ocifq_score": 85, "reason": "..."},
    {"code": "600346", "name": "恒力石化", "ocifq_score": 67, "reason": "..."}
  ]
}

输出格式:
{
  "results": [
    {
      "code": "600309",
      "name": "万华化学",
      "ocifq_score": 85,
      "tech_score": 72,
      "evidence_direction": "supportive",
      "price_zone_evidence": {"low": 70.5, "high": 72.0},
      "pool_stop_status": "unknown",
      "entry_gate_status": "incomplete",
      "authorization_status": "not_authorized"
    }
  ]
}
```

## 综合证据规则

| OCIFQ评分 | 技术面评分 | 证据输出 |
|-----------|-----------|---------|
| ≥80 | ≥70 | 基本面与技术证据均较强，进入完整建仓门槛复核 |
| ≥80 | 50-69 | 基本面证据较强，技术证据中性，保留缺口 |
| ≥80 | <50 | 技术风险证据较强，降低研究置信度 |
| 60-79 | ≥70 | 技术证据较强，但基本面证据不足，保留缺口 |
| 60-79 | <70 | 两类证据均不足，不生成建仓建议 |
| <60 | 任意 | OCIFQ证据不足，不进入建仓门槛复核 |

评分只能提供研究证据，不能直接生成建仓、仓位或交易动作。只有通过 `rules/risk_rules.md` 的完整建仓门槛、风险审查和25%单票上限后，才能形成待授权建议；生产动作必须获得用户逐次明确授权。
