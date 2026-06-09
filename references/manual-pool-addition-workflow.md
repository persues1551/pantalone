# 手动入池工作流（新闻扫描超时时）

## 触发条件
`amadeus_news_scanner.py scan` 或 `hotspots` 命令超时（常见于财联社API阻塞），且缓存 `news_latest.json` / `news_scan_*.json` 过期（>1天）。

## 流程

### 1. 获取今日涨停股
```python
import akshare as ak
df = ak.stock_zt_pool_em(date='YYYYMMDD')  # 今日涨停池
```

### 2. 筛选龙头（按成交额排序）
```python
# 按成交额降序，取前10-15只
df_sorted = df.sort_values('成交额', ascending=False).head(15)
```

### 3. 手动入池 session_context.json
```python
import json
from datetime import datetime

with open('/home/ubuntu/.hermes/cache/amadeus/session_context.json', 'r') as f:
    ctx = json.load(f)

stock_notes = ctx.get('stock_notes', {})
today = datetime.now().strftime('%Y-%m-%d')

for s in hot_stocks:
    code = s['code']
    if code not in stock_notes or stock_notes[code].get('pool') == '退池':
        stock_notes[code] = {
            'pool': 'C',           # 新入池默认C池
            'status': '观察',
            'note': s['reason'],
            'entry_date': today,
            'entry_price': 0,
            'last_analysis': today,
            'source': '今日涨停入池'
        }

ctx['stock_notes'] = stock_notes
with open('/home/ubuntu/.hermes/cache/amadeus/session_context.json', 'w') as f:
    json.dump(ctx, f, ensure_ascii=False, indent=2)
```

### 4. 运行 pool_manager.py auto
```bash
python3 ~/.hermes/scripts/amadeus/pantalone/amadeus_pool_manager.py auto
```
这会更新行情数据并执行退池检查。

## ⚠️ Pitfalls

1. **数据源是 session_context.json，不是 pool_state.json**
   - `pool_manager.py scan_pool()` 读取 `ctx.get("stock_notes", {})`
   - `pool_state.json` 是旧格式（OCIFQ扫描结果），与pool_manager无关
   - 检查池子状态应读 session_context.json 的 stock_notes

2. **stock_notes中的pool字段值**
   - 正常值: "A", "B", "C"
   - 退池标记: "退池"
   - 不是 "A池", "B池", "C池"

3. **已退池股票可重新入池**
   - 检查条件: `stock_notes[code].get('pool') == '退池'`
   - 只有"退池"状态可覆盖，已在A/B/C池的不重复入池

4. **涨停原因字段可能为空**
   - `ak.stock_zt_pool_em()` 的涨停原因列经常为空
   - 需要手动根据股票名称/行业判断热点板块

5. **AKShare涨停池日期格式**
   - 参数格式: `date='20260608'`（YYYYMMDD，无连字符）
   - 非交易日会报错或返回空

## 典型热点板块识别
从涨停股名称推断：
- 机器人: 埃斯顿、国机精工、绿的谐波
- AI/算力: 天娱数科、达实智能、中望软件
- 半导体: 中巨芯、亚翔集成、金安国纪
- 新材料: 华正新材、泰和新材
- 军工: 神剑股份、中天火箭
- 电力: 西昌电力、节能铁汉
