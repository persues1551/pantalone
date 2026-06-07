# Decision Log JSON 结构

## 文件位置
`~/.hermes/cache/amadeus/decision_log.json`

## 顶层结构
```json
{
  "version": "1.0",
  "created": "2026-05-30",
  "entries": [...],
  "stats": {
    "total_predictions": N,
    "verified": N,
    "hits": N,
    "misses": N
  }
}
```

## Entry 结构
```json
{
  "id": "YYYYMMDD-NN",
  "date": "YYYY-MM-DD",
  "type": "大盘方向|板块|个股",
  "prediction": "可验证的预测文本",
  "confidence": 0.55,
  "status": "pending|verified",
  "source": "晚间复盘20260602",
  "target": "600487",           // 可选，个股/板块代码
  "verified_date": "YYYY-MM-DD", // 验证后填入
  "result": "hit|miss"           // 验证后填入
}
```

## 读取方法
```python
# ✅ 正确：用terminal读取
result = terminal("cat ~/.hermes/cache/amadeus/decision_log.json")
log = json.loads(result["output"])

# ❌ 错误：用read_file读取（带行号前缀，需额外处理）
```

## 写入方法
```python
log["entries"].append(new_entry)
log["stats"]["total_predictions"] += N
write_file("~/.hermes/cache/amadeus/decision_log.json", json.dumps(log, indent=2, ensure_ascii=False))
```

## Pitfalls
- entries是数组，不是predictions
- id格式YYYYMMDD-NN，NN从01递增
- type字段值：大盘方向/板块/个股（不是"大盘预测"）
- status只在收盘复盘验证后从pending改为verified
- 读取时不要用read_file（行号前缀导致JSON解析失败）
