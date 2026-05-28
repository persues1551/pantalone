# 止损机制与入池规范

## 止损确认机制

### 问题
止损执行严重滞后——报告中显示-5%止损线，实际拖到-10%甚至-20%才退池

### 解决方案

#### 1. 止损确认脚本 (stop_loss_confirmation.py)

```python
#!/usr/bin/env python3
"""
止损确认机制 - 验证止损是否真正执行
每日收盘后运行，检查是否有超过止损线但未退池的持仓
"""
import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".hermes" / "cache" / "amadeus"
CONTEXT_FILE = CACHE_DIR / "session_context.json"
ALERT_FILE = CACHE_DIR / "stop_loss_alerts.json"

# 止损规则
STOP_LOSS_RULES = {
    'A': -0.10,  # A池 -10%
    'B': -0.05,  # B池 -5%
    'C': -0.03,  # C池 -3%
}

def check_stop_loss():
    """检查所有持仓的止损状态"""
    with open(CONTEXT_FILE, 'r') as f:
        context = json.load(f)
    
    stock_notes = context.get('stock_notes', {})
    alerts = []
    
    for code, info in stock_notes.items():
        pool = info.get('pool', '')
        if pool not in ['A', 'B', 'C']:
            continue
        
        pnl = info.get('pnl_pct', 0)
        if pnl is None:
            pnl = 0
            
        stop_loss_line = STOP_LOSS_RULES.get(pool, -0.05)
        
        # 突破止损线
        if pnl <= stop_loss_line:
            alerts.append({
                'code': code,
                'name': info.get('name', ''),
                'pool': pool,
                'pnl_pct': pnl,
                'stop_loss_line': stop_loss_line,
                'status': 'BREACH',
                'message': f"{code} {info.get('name','')} 浮盈{pnl:.1%} 已突破{pool}池止损线{stop_loss_line:.0%}"
            })
        # 接近止损线80%
        elif pnl <= stop_loss_line * 0.8:
            alerts.append({
                'code': code,
                'name': info.get('name', ''),
                'pool': pool,
                'pnl_pct': pnl,
                'stop_loss_line': stop_loss_line,
                'status': 'WARNING',
                'message': f"{code} {info.get('name','')} 浮盈{pnl:.1%} 接近{pool}池止损线{stop_loss_line:.0%}"
            })
    
    if alerts:
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts,
            'breach_count': len([a for a in alerts if a['status'] == 'BREACH']),
            'warning_count': len([a for a in alerts if a['status'] == 'WARNING'])
        }
        with open(ALERT_FILE, 'w') as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)
        
        print(f"⚠️ 发现 {len(alerts)} 个止损告警：")
        for alert in alerts:
            print(f"  {alert['status']}: {alert['message']}")
    else:
        print("✅ 所有持仓止损状态正常")
    
    return alerts
```

#### 2. 止损滞后告警Cron任务 (stop_loss_alert_cron.py)

```python
#!/usr/bin/env python3
"""
止损滞后自动告警 - 每小时检查一次
如果发现超过止损线的持仓，发送告警直到执行止损
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".hermes" / "cache" / "amadeus"
ALERT_FILE = CACHE_DIR / "stop_loss_alerts.json"

def check_and_alert():
    """检查止损状态并生成告警消息"""
    result = subprocess.run(
        ['python3', str(Path.home() / '.hermes' / 'scripts' / 'amadeus' / 'stop_loss_confirmation.py')],
        capture_output=True, text=True
    )
    
    if ALERT_FILE.exists():
        with open(ALERT_FILE, 'r') as f:
            alert_data = json.load(f)
        
        breach_count = alert_data.get('breach_count', 0)
        if breach_count > 0:
            alerts = alert_data.get('alerts', [])
            breach_alerts = [a for a in alerts if a['status'] == 'BREACH']
            
            message = f"🚨 **止损滞后告警** ({datetime.now().strftime('%H:%M')})\n\n"
            message += f"发现 {breach_count} 只持仓已突破止损线但未执行止损：\n\n"
            
            for alert in breach_alerts:
                message += f"- **{alert['code']} {alert['name']}**: 浮盈{alert['pnl_pct']:.1%}，止损线{alert['stop_loss_line']:.0%}\n"
            
            message += "\n**请立即检查并执行止损！**"
            print(message)
            return True
    
    print("✅ 止损状态正常，无告警")
    return False
```

#### 3. Cron任务配置

```json
{
    "id": "stop_loss_alert_hourly",
    "name": "止损滞后自动告警",
    "schedule": {"kind": "cron", "expr": "0 * * * 1-5"},
    "script": "amadeus/stop_loss_alert_cron.py",
    "deliver": "discord:mortis2887_47447",
    "enabled_toolsets": ["terminal"]
}
```

---

## 入池OCIFQ强制评分

### 问题
观察池入池流程绕过OCIFQ评分门槛（如002535林州重机仅因"逆向买入逻辑"入池）

### 解决方案

修改`amadeus_pool_manager.py`的`add_stock`函数，添加OCIFQ检查：

```python
def add_stock(code: str, pool: str, reason: str):
    # OCIFQ强制评分检查
    if reason and 'OCIFQ' not in reason and '逆向' not in reason.lower():
        import sys
        print(f"⚠️ {code} 入池被拒绝：缺少OCIFQ评分", file=sys.stderr)
        return False
    
    # 原有逻辑...
```

### 补丁脚本 (ocifq_enforce.py)

```python
#!/usr/bin/env python3
"""入池OCIFQ强制评分 - 确保所有入池股票都经过OCIFQ评分"""
import json
from pathlib import Path

POOL_MANAGER = Path.home() / ".hermes" / "scripts" / "amadeus" / "amadeus_pool_manager.py"

def patch_pool_manager():
    with open(POOL_MANAGER, 'r') as f:
        content = f.read()
    
    if 'ocifq_enforce' in content:
        print("✅ 已包含OCIFQ强制评分检查")
        return
    
    check_code = '''
    # OCIFQ强制评分检查 - 由ocifq_enforce.py添加
    if reason and 'OCIFQ' not in reason and '逆向' not in reason.lower():
        import sys
        print(f"⚠️ {code} 入池被拒绝：缺少OCIFQ评分", file=sys.stderr)
        return False
'''
    
    lines = content.split('\n')
    new_lines = []
    in_add_stock = False
    docstring_count = 0
    
    for line in lines:
        new_lines.append(line)
        if 'def add_stock(' in line:
            in_add_stock = True
        if in_add_stock and '"""' in line:
            docstring_count += 1
            if docstring_count == 2:
                new_lines.append(check_code)
                in_add_stock = False
    
    content = '\n'.join(new_lines)
    
    with open(POOL_MANAGER, 'w') as f:
        f.write(content)
    
    print("✅ 已添加OCIFQ强制评分检查")
```

### 使用方法

```bash
# 运行补丁脚本
python3 ~/.hermes/scripts/amadeus/ocifq_enforce.py

# 验证补丁生效
grep "ocifq_enforce" ~/.hermes/scripts/amadeus/amadeus_pool_manager.py
```

---

## 止损规则速查表

| 池别 | 止损线 | 预警线(80%) | 操作 |
|------|--------|-------------|------|
| A池 | -10% | -8% | 立即止损 |
| B池 | -5% | -4% | 立即止损 |
| C池 | -3% | -2.4% | 立即止损 |

**2026-05-27教训**：
- 8只退出股票亏损超-10%（最高-19.6%）
- 止损应在-5%执行，实际拖了数倍
- 根因：缺乏止损确认机制和滞后告警
