# task_log.md — 任务日志规范

## 草稿本（Scratchpad）— 工具调用审计

**脚本**：`scripts/amadeus/amadeus_scratchpad.py`

## 日志格式

每次数据采集后，记录调用日志：

```bash
python3 ~/.hermes/scripts/amadeus/amadeus_scratchpad.py log "ak.stock_zh_a_spot" '{"market":"A股"}' "返回3800只股票快照" 1200
python3 ~/.hermes/scripts/amadeus/amadeus_scratchpad.py log "ak.stock_zt_pool_em" '{"date":"20260513"}' "涨停45只" 800
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| tool | 工具/函数名 | `ak.stock_zh_a_spot` |
| params | 调用参数（JSON） | `{"market":"A股"}` |
| result | 结果摘要 | "返回3800只股票快照" |
| size | 结果大小（字符数） | 1200 |

## 查看日志

```bash
# 今日统计
python3 ~/.hermes/scripts/amadeus/amadeus_scratchpad.py stats

# 最近20条
python3 ~/.hermes/scripts/amadeus/amadeus_scratchpad.py tail
```

## 自动清理

每周日自动清理30天前的记录。

## 大结果持久化

当工具返回结果过大（>5000字符）时，不将完整结果注入上下文，而是：

1. 保存到 `~/.hermes/cache/amadeus/scratchpad/` 目录
2. 上下文中只保留摘要（前200字符 + "..." + 文件路径）
3. 需要详细数据时，从文件读取

示例：
```python
# 返回结果>5000字符时
result = ak.stock_zh_a_spot()  # 返回3800行DataFrame
if len(str(result)) > 5000:
    path = f"~/.hermes/cache/amadeus/scratchpad/spot_{date}.json"
    result.to_json(path)
    summary = f"返回{len(result)}只股票，已保存到{path}，前5只：{result.head().to_string()}"
    # 上下文中只注入summary，不注入完整result
```

## 日志用途

1. **调试**：追踪数据采集过程，定位失败环节
2. **审计**：记录每次API调用，避免重复采集
3. **优化**：分析高频调用，优化采集顺序
4. **成本**：监控API调用量，控制成本
