# 数据质量等级系统 (data_quality.py)

**创建日期**: 2026-05-21
**脚本**: `~/.hermes/scripts/amadeus/data_quality.py`

## 用途

统一评估报告所用数据的完整性、新鲜度、来源可靠性。每份cron报告必须在正文第一段嵌入data_quality.py输出。

## 等级规则

| 等级 | 得分 | 含义 | 能否用于胜率统计 |
|------|------|------|------------------|
| A | ≥85% | 核心数据齐全且今日 | ✅ |
| B | ≥70% | 主要数据齐全，个别有备用源 | ✅ |
| C+ | ≥50% | 部分缺失但有备用源 | ✅ |
| C | ≥30% | 主要依赖web_search/LLM推理 | ⚠️ |
| D | ≥15% | 旧cache/字段异常 | ❌ |
| F | <15% | 数据完全缺失 | ❌ |

**自动下调规则**: 有≥15分权重的核心项缺失时，从A/B/C+自动降到C/D。

## 8项核心数据

| 数据项 | 权重 | cache_pattern | 验证条件 |
|--------|------|---------------|----------|
| 指数数据 | 20 | market_{date}.json→indices | dict且≥2个指数 |
| 涨跌停数据 | 20 | market_{date}.json→pools | limit_up_count>0 |
| 市场总貌 | 15 | market_{date}.json→market | total>1000 |
| 北向资金 | 10 | market_{date}.json→north | net_flow非None |
| 连板数据 | 10 | market_{date}.json→lianban | 非空列表 |
| 板块数据 | 10 | market_{date}.json→sectors | total_count>0 |
| 板块资金流 | 10 | market_{date}.json→sector_flow | top_inflow非空 |
| 个股实时行情 | 5 | realtime_*.json | 非None |

## 数据加载逻辑

`_load_cache_file(pattern)` 的降级链:
1. 精确匹配 `market_{today}.json→field`
2. 从 `market_{today}.json` 提取嵌套字段（字段映射: indices→indices, limit_pools→pools）
3. glob找最新文件，标记为过期

## 用法

```bash
python3 data_quality.py                 # 人类可读报告
python3 data_quality.py --json          # JSON输出
python3 data_quality.py --report-fragment  # 报告片段（嵌入报告用）
python3 data_quality.py 2026-05-20      # 指定日期评估
```

## 嵌入报告方式

```python
# 在cron prompt中:
运行 `python3 ~/.hermes/scripts/amadeus/data_quality.py --report-fragment`
# 将输出粘贴在报告正文第一段
# 等级低于C+时加"⚠️ 数据降级，分析可靠性降低"警告
```

## Pitfalls

1. **indices/limit数据在market_*.json中**: 不是独立的indices_{date}.json，而是market_{date}.json的嵌套字段。cache_pattern必须用`market_{date}.json→indices`格式
2. **板块数据经常为None**: amadeus_data.py的collect_sectors()偶尔返回None（AKShare偶发），导致该项0分但不影响整体等级判定
3. **个股实时行情盘前为缺失**: realtime数据需盘中amadeus_realtime.py按需调用，盘前/盘后该项为0分是正常的
4. **emotion.py和data_quality.py可能显示不同结果**: emotion.py读market_*.json中的pools/indices直接返回fresh，data_quality.py有独立的验证逻辑（检查字段有效性），两者判断标准不同
5. **不要信任LLM手动计算的数据等级**: 必须用脚本输出，LLM会遗漏检查项

## 与其他模块的关系

- **amadeus_emotion.py**: 检查情绪温度数据的新鲜度（data_freshness/stale_warnings字段）
- **amadeus_data.py**: 生成market_{date}.json，是data_quality.py的主要数据源
- **data_validator.py**: 单项数据验证（NaN/Inf/0检测），data_quality.py在更上层做整体评估
