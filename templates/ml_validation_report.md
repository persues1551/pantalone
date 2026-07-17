# ML 验证报告模板

> 用于 ML 模型预测验证的标准化报告格式
> 不构成投资建议

## 基本信息

- **报告时间**: {datetime}
- **模型版本**: {model_version}
- **验证标的**: {symbol_list}
- **数据区间**: {start_date} → {end_date}

## 预测摘要

| 标的 | 预测方向 | 预测置信度 | 实际涨跌幅 | 是否命中 | 偏差分析 |
|------|----------|-----------|-----------|---------|---------|
| {code} | {direction} | {confidence}% | {actual}% | {hit/miss} | {analysis} |

## 总体验证指标

- **总预测数**: {total}
- **命中数**: {hits}
- **命中率**: {hit_rate}%
- **平均置信度**: {avg_confidence}%
- **平均偏差**: {avg_deviation}%

## 错误分析

| 错误类型 | 次数 | 占比 | 典型特征 |
|----------|------|------|----------|
| 方向错误 | {count} | {pct}% | {pattern} |
| 幅度偏差 | {count} | {pct}% | {pattern} |
| 时机偏差 | {count} | {pct}% | {pattern} |

## 数据来源

- 行情数据: {data_source}
- 财务数据: {data_source}
- 情绪数据: {data_source}

## 风险提示

- {risk_item}
- {risk_item}

## 失效条件

- {failure_condition}
- {failure_condition}

---

*以上仅作为模型验证记录，不构成投资建议*
