# amadeus_news_scanner.py CLI 参考

## 实际可用命令（2026-06-05验证）

```bash
# 热点扫描（文本输出，无JSON模式）
python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py hotspots

# 完整扫描（保存到缓存文件）
python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py scan
```

## 已知陷阱

1. **`--json` 参数不存在**：传入会报 "Unknown command: --json"
2. **`hotspots` 在cron上下文中经常超时**（60s限制）：pitfall #84
3. **`scan` 也经常超时**（120s限制）：pitfall #84
4. **无结构化JSON输出**：只有文本输出和缓存文件

## 缓存文件

- 路径：`~/.hermes/cache/amadeus/news_latest.json`
- 格式：`{"scan_time": "ISO datetime", "headlines": [...], "count": N}`
- ⚠️ scan_time必须检查是否今天，过期数据需标注

## 降级策略

当news_scanner超时/失败时：
1. 读取`news_latest.json`缓存（检查scan_time）
2. 如果缓存也过期，在报告中标注"新闻采集超时"
3. 不要无限等待——直接跳过新闻板块
