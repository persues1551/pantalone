# 风险整改自动化流程（2026-05-26）

## 触发条件

收盘复盘报告中发现以下风险项目时，必须自动整改：
1. 止损未执行（报告称"止损连续N天未执行"）
2. 池子膨胀（B池>50只）
3. 违规操作（止损线已触发但未执行）
4. 数据源问题（报告判断与实际数据不符）

## 整改流程

### 第一步：验证实际数据

```python
import json
from pathlib import Path

# 读取session_context.json
session_file = Path.home() / ".hermes" / "cache" / "amadeus" / "session_context.json"
with open(session_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

stock_notes = data.get('stock_notes', {})

# 检查止损状态
stop_loss_rules = {
    'A': -10.0,
    'B': -5.0,
    'C': -3.0
}

for code, info in stock_notes.items():
    pool = info.get('pool', '')
    pnl = info.get('pnl_pct', 0)
    name = info.get('name', '未知')
    
    if pool in stop_loss_rules and pnl and pnl < stop_loss_rules[pool]:
        print(f"⚠️ {code} {name} ({pool}池): {pnl}% 已触发止损线")
```

### 第二步：执行整改

#### 2.1 B池清理

```python
# 统计B池数量
b_pool_stocks = {code: info for code, info in stock_notes.items() if info.get('pool') == 'B'}
print(f"当前B池数量: {len(b_pool_stocks)}只")

if len(b_pool_stocks) > 50:
    # 按浮盈排序，保留前50只
    sorted_b_pool = sorted(b_pool_stocks.items(), key=lambda x: x[1].get('pnl_pct', 0) or 0, reverse=True)
    keep_b_pool = sorted_b_pool[:50]
    remove_b_pool = sorted_b_pool[50:]
    
    # 更新stock_notes
    from datetime import datetime
    for code, info in remove_b_pool:
        stock_notes[code]['pool'] = '退池'
        stock_notes[code]['last_update'] = datetime.now().strftime('%Y-%m-%d')
        stock_notes[code]['note'] = info.get('note', '') + ' | B池清理退池'
    
    # 保存更新后的数据
    data['stock_notes'] = stock_notes
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

#### 2.2 止损执行

```python
# 检查需要止损的股票
need_stop_loss = []
for code, info in stock_notes.items():
    pool = info.get('pool', '')
    pnl = info.get('pnl_pct', 0)
    name = info.get('name', '未知')
    
    if pool in stop_loss_rules and pnl and pnl < stop_loss_rules[pool]:
        need_stop_loss.append((code, name, pool, pnl))

if need_stop_loss:
    print("需要止损的股票:")
    for code, name, pool, pnl in need_stop_loss:
        print(f"  {code} {name} ({pool}池): {pnl}%")
    
    # 执行止损（标记为退池）
    for code, name, pool, pnl in need_stop_loss:
        stock_notes[code]['pool'] = '退池'
        stock_notes[code]['last_update'] = datetime.now().strftime('%Y-%m-%d')
        stock_notes[code]['note'] = f"止损触发退池 ({pnl}%)"
    
    # 保存更新后的数据
    data['stock_notes'] = stock_notes
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 第三步：同步更新pool_state.json

```python
pool_state_file = Path.home() / ".hermes" / "cache" / "amadeus" / "pool_state.json"
if pool_state_file.exists():
    with open(pool_state_file, 'r', encoding='utf-8') as f:
        pool_state = json.load(f)
    
    # 更新池子数量
    b_pool_count = sum(1 for info in stock_notes.values() if info.get('pool') == 'B')
    a_pool_count = sum(1 for info in stock_notes.values() if info.get('pool') == 'A')
    c_pool_count = sum(1 for info in stock_notes.values() if info.get('pool') == 'C')
    
    pool_state['summary']['b_pool'] = b_pool_count
    pool_state['summary']['a_pool'] = a_pool_count
    pool_state['summary']['c_pool'] = c_pool_count
    pool_state['summary']['total'] = a_pool_count + b_pool_count + c_pool_count
    
    with open(pool_state_file, 'w', encoding='utf-8') as f:
        json.dump(pool_state, f, ensure_ascii=False, indent=2)
```

### 第四步：生成整改报告

```python
rectification_report = f"""# 风险整改报告 {datetime.now().strftime('%Y-%m-%d')}

## 整改项目

### 1. B池膨胀问题 ✅ 已完成
- **问题**：B池从合理数量膨胀至{len(b_pool_stocks)}只
- **整改**：清理B池，保留前50只（按浮盈排序），移出{len(remove_b_pool)}只至退池
- **结果**：B池数量从{len(b_pool_stocks)}只减少至{len(keep_b_pool)}只

### 2. 止损状态验证 ✅ 已完成
- **检查结果**：{'有' if need_stop_loss else '无'}止损触发
- **止损规则**：A池-10% / B池-5% / C池-3%

## 整改结果

### 观察池现状
| 池 | 数量 | 说明 |
|---|------|------|
| A池 | {a_pool_count}只 | 长期价值核心持仓 |
| B池 | {b_pool_count}只 | 趋势跟踪（已清理） |
| C池 | {c_pool_count}只 | 事件驱动 |

---

**整改完成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
**整改执行人**：Amadeus
**验证状态**：✅ 已完成
"""

# 保存整改报告
report_file = Path.home() / ".hermes" / "cache" / "amadeus" / f"rectification_report_{datetime.now().strftime('%Y%m%d')}.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(rectification_report)

print(f"整改报告已保存至：{report_file}")
```

## 注意事项

1. **数据验证优先**：整改前必须验证实际数据，不能依赖报告中的错误判断
2. **同步更新**：整改后必须同步更新session_context.json和pool_state.json
3. **生成报告**：整改后必须生成整改报告，记录整改内容和结果
4. **止损规则**：A池-10% / B池-5% / C池-3%，只有实际触发才报告"止损触发"

## 相关脚本

- 止损监控：`scripts/amadeus/stop_loss_monitor.py`
- 观察池管理：`scripts/amadeus/pool_manager.py`
- 数据验证：`scripts/amadeus/data_validator.py`
