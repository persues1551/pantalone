# Gateway重启cron修复记录（2026-05-28）

## 问题

系统crontab配了`restart_gateway.sh`，每天6次触发（08:55/09:25/11:55/13:25/15:25/17:00），打断正在处理的会话。

## 根因

Pantalone skill中记录了"系统crontab三重重启确保ticker鲜活"，但实际配置了6次重启。

## 修复过程

1. **无法直接修改crontab** — `/var/spool/cron/crontabs/`权限不足，sudo setuid位丢失
2. **脚本级时间门控** — 在`restart_gateway.sh`内加时间判断：

```bash
#!/bin/bash
HOUR=$(date '+%H')
if [ "$HOUR" != "03" ]; then
    exit 0
fi
# 实际重启逻辑
cd /home/ubuntu/.hermes && /home/ubuntu/.local/bin/hermes gateway restart
```

3. **最终改为直接禁用** — 主人要求取消，脚本改为`exit 0`

## 教训

1. Gateway有systemd `Restart=on-failure`，不需要主动重启
2. 脚本级时间门控是crontab无法编辑时的有效替代方案
3. sudo损坏时，所有需要root权限的操作都会失败，应优先修复sudo
