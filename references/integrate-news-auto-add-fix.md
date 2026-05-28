# integrate-news 自动入池修复 (2026-05-21)

## 问题

`amadeus_pool_manager.py integrate-news` 命令只生成候选建议但不调用 `add_stock()` 入池。

**症状**：观察池日报显示"新入池：0只"连续6天，但integrate-news确实发现了候选。

**根因**：`integrate_news()`函数只打印建议列表（"🟢建议入B池"），但循环中没有调用`add_stock()`。

## 修复

在 `integrate_news()` 函数的 suggestions 循环中添加自动入池逻辑：

```python
# 在 print 语句后添加
if "❌" not in s.get("action", "") and "suggested_pool" in s:
    code = s["code"]
    pool = s["suggested_pool"]
    reason = s.get("catalyst", s.get("reason", ""))
    
    # 过滤条件
    skip = False
    if s.get("sentiment", 0) < 0:  # 当日大跌
        skip = True
    elif any("无法获取行情" in r for r in s.get("risks", [])):
        skip = True
    elif code in existing:  # 已在池中
        skip = True
    
    if not skip:
        add_stock(code, pool, reason)
        added_count += 1
```

## 过滤规则

| 条件 | 处理 |
|------|------|
| 排雷失败（ST/退市） | 跳过（已有） |
| 情绪<0（当日大跌） | 跳过 |
| 无法获取行情数据 | 跳过 |
| 已在池中 | 跳过 |

## 验证

修复后执行 `integrate-news`：
- 发现36个候选
- 自动入池约20只（过滤后）
- 池内从78只增加到174只

## 防复发

此修复已合入 `amadeus_pool_manager.py`，后续执行 `integrate-news` 会自动入池。
