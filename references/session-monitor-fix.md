# Session监控脚本修复记录

## 修复日期
2026-05-24

## 问题
`check_session_size.py` 统计数据库全量消息（含10天前旧数据），导致 `/new` 后仍触发 ALERT 误报。

## 根因
- Session ID 是固定的：`agent:main:weixin:dm:o9cq802TZLYkDYpP8A7yL8hAqY7s@im.wechat`
- `/new` 只重置对话上下文，**不清理数据库旧消息**
- 脚本统计 `COUNT(*) FROM messages WHERE session_id = ?`，包含所有历史消息

## 修复方案
改为只统计最近24小时的消息：

```python
cutoff = time.time() - (LOOKBACK_HOURS * 3600)
cur.execute(
    "SELECT COUNT(*), COALESCE(SUM(LENGTH(content)), 0) FROM messages "
    "WHERE session_id = ? AND timestamp >= ?",
    (SESSION_ID, cutoff)
)
```

## 修复后效果
```
修复前: ALERT|100|151167  (10天前的旧数据)
修复后: OK|0|0|24h        (最近24小时无消息)
```

## 文件位置
- 脚本：`~/.hermes/scripts/check_session_size.py`
- Cron job：`e7e196fffe0c`（每天20:00执行）

## 教训
1. `/new` 不清理数据库，监控脚本必须按时间窗口统计
2. 修改后必须立即测试，不能说"下次生效"
