# Gateway重启与Cron任务故障排查

## 常见问题：Gateway重启导致Cron任务错过执行窗口

### 症状
- Cron任务的`last_run_at`显示几天前执行过
- 任务schedule正常（如每天21:00），但连续多天未执行
- 任务本身没有报错

### 根因诊断

```bash
# 1. 检查Gateway重启历史
grep -E "Cron ticker (started|stopped)" ~/.hermes/logs/gateway.log | tail -20

# 2. 检查Gateway启动时间
grep "Starting Hermes Gateway" ~/.hermes/logs/gateway.log | tail -10

# 3. 检查健康检查日志
tail -20 ~/.hermes/logs/health_check.log
```

### 根因：PATH问题导致重启失败

**2026-05-27案例**：
- 健康检查脚本使用`hermes`命令
- cron环境下PATH不包含`/home/ubuntu/.local/bin/`
- 导致`hermes: command not found`，重启一直失败
- Gateway长时间未运行，所有定时任务错过执行窗口

### 修复方案

修改以下脚本，使用完整路径：

```bash
# ~/.hermes/scripts/check_gateway_health.sh
# 将所有 hermes 命令替换为完整路径
/home/ubuntu/.local/bin/hermes gateway restart

# ~/.hermes/scripts/restart_gateway.sh
cd /home/ubuntu/.hermes && /home/ubuntu/.local/bin/hermes gateway restart
```

### 验证修复

```bash
# 手动运行健康检查脚本
bash ~/.hermes/scripts/check_gateway_health.sh

# 检查日志是否还有 "command not found"
grep "command not found" ~/.hermes/logs/health_check.log | tail -5
```

---

## Cron任务投递渠道迁移

### 场景
需要将所有推送任务从一个渠道（如微信）迁移到另一个渠道（如Discord）

### 操作步骤

```python
# 1. 查看当前所有任务
cronjob(action='list')

# 2. 查看可用的投递目标
send_message(action='list')

# 3. 批量更新deliver字段
cronjob(action='update', job_id='<job_id>', deliver='<new_target>')
```

### 注意事项
- 容错备份任务（deliver=local）不需要修改
- 更新后立即验证：`cronjob(action='list')`确认deliver字段已更新
- 记录到memory：主渠道已从X迁移到Y

---

## amadeus_data.py超时问题

### 症状
- 收盘复盘报告显示"市场总貌/板块数据/个股行情"缺失
- data_quality.py等级为C或更低

### 根因
AKShare API响应慢，某些collect函数耗时过长

### 修复：添加超时机制

```python
import signal
from functools import wraps

class TimeoutError(Exception):
    pass

def timeout(seconds=30):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"{func.__name__} timeout after {seconds}s")
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator

# 为每个collect函数添加@timeout装饰器
@timeout(30)
def collect_market_overview():
    ...
```

### 效果
- 单个函数超时后自动跳过，不会阻塞整个脚本
- 其他数据源正常采集，只缺失超时的部分

---

## Crontab权限受限时的时间门控模式（2026-05-28）

### 场景
系统crontab（`/var/spool/cron/crontabs/ubuntu`）需要root权限修改，`sudo`不可用（setuid问题），但需要限制脚本只在特定时间执行。

### 问题
原cron触发时间：08:55/09:25/11:55/13:25/15:25/17:00（每天6次），导致Gateway频繁重启打断正在处理的会话。

### 解决方案：脚本内时间门控

在脚本内部添加时间判断，外部cron照常触发但脚本自行过滤：

```bash
#!/bin/bash
# restart_gateway.sh — 只在凌晨3点执行，其他时间静默退出

HOUR=$(date '+%H')
if [ "$HOUR" != "03" ]; then
    exit 0
fi

LOG="/home/ubuntu/.hermes/logs/gateway_restart.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restarting gateway (scheduled 03:00)..." >> "$LOG"
cd /home/ubuntu/.hermes && /home/ubuntu/.local/bin/hermes gateway restart >> "$LOG" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restart complete, exit=$?" >> "$LOG"
```

### 关键点
- **不修改crontab** — 因为权限受限，改不了就不改
- **脚本自过滤** — `HOUR != "03"` → `exit 0`，静默退出无副作用
- **cron仍触发** — syslog中会看到cron触发记录，但脚本立即退出
- **systemd兜底** — `hermes-gateway.service`有`Restart=always`+`RestartSec=5`，崩溃自动恢复，主动重启是锦上添花

### 何时用此模式
- 需要修改crontab但无root权限
- crontab由其他系统管理（如cpanel、面板工具），手动改会被覆盖
- 想在脚本层面控制执行频率，不依赖外部调度器
