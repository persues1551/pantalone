# 情绪温度数据管线修复记录（2026-05-20）

## 问题

`amadeus_emotion.py` 的 `calc_emotion()` 函数依赖两个数据源：
1. `limit_data` — 涨跌停数据（来自 `limit_*.json` 或 `market_*.json` 的 `pools` 字段）
2. `index_data` — 指数数据（来自 `indices_*.json` 或 `market_*.json` 的 `indices` 字段）

但实际数据格式与脚本预期不匹配：

| 维度 | 脚本期望的字段 | 实际数据位置 | 结果 |
|------|--------------|-------------|------|
| 连板高度 | `limit_up_stocks[].连板数` | `lianban[].board_count` | 始终缺失 |
| 成交额 | `index_data[key].volume` | `market.total_amount`（万亿） | 始终缺失 |

导致情绪温度数据完整度只有 65/100，连板和成交额两个维度（共35分权重）始终为0。

## 修复方案

### 1. 新增 `load_market_extra()` 函数

从 `market_*.json` 中提取额外数据：
```python
def load_market_extra(target_date=None):
    """从 market_*.json 加载额外数据（连板、成交额）"""
    market_file = CACHE_DIR / f"market_{today_str}.json"
    # 读取 lianban + market.total_amount + pools
    return {
        "lianban": market.get("lianban"),
        "total_amount": market.get("market", {}).get("total_amount"),
        "pools": market.get("pools"),
    }, True, today_str
```

### 2. 修改 `calc_emotion()` 签名

新增 `market_extra=None` 参数。

### 3. 连板高度读取逻辑

```python
# 优先从 market_extra 的 lianban 数据读取
if market_extra and market_extra.get("lianban"):
    for s in market_extra["lianban"]:
        lb = s.get("board_count", 0)
        if lb > max_lb: max_lb = lb
# 降级：从 limit_up_stocks 的连板数字段读取
if max_lb == 0 and limit_data:
    for s in limit_data.get("limit_up_stocks", []):
        lb = s.get("连板数", 0)
        if lb > max_lb: max_lb = lb
```

### 4. 成交额读取逻辑

```python
vol_yi = 0
# 优先从 market_extra 读取（单位：万亿→亿）
if market_extra and market_extra.get("total_amount"):
    vol_yi = float(market_extra["total_amount"]) * 10000
# 降级：从 index_data 的 volume 字段读取
elif index_data:
    for key in ["sh000001", "sz399001"]:
        v = index_data[key].get("volume", 0)
        if v > 0: vol += v
    if vol > 0: vol_yi = vol / 1e8
```

## 数据来源映射

```
amadeus_data.py → market_2026-05-20.json
  ├── market.total_amount  → 成交额（万亿）
  ├── pools.limit_up_count → 涨停数
  ├── pools.limit_down_count → 跌停数
  ├── lianban[].board_count → 连板高度
  └── indices[key].close   → 指数收盘价

amadeus_emotion.py 读取:
  ├── load_limit_data()    → pools 字段
  ├── load_index_data()    → indices 字段
  └── load_market_extra()  → lianban + total_amount（修复新增）
```

## 验证结果

修复前：情绪温度49分，完整度65/100，缺失连板+成交额
修复后：情绪温度67分，完整度100/100，连板11板满分+成交额29760亿满分

## 教训

1. **数据格式文档化**：amadeus_data.py 的输出字段名必须在 SKILL.md 中文档化，避免下游脚本猜错字段名
2. **跨脚本字段验证**：新增数据源后，必须检查所有消费脚本的字段引用是否匹配
3. **market_*.json 是核心缓存**：大多数消费脚本应优先从 market_*.json 读取，而非独立的 limit_*.json / indices_*.json
