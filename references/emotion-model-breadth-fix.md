# 情绪温度模型宽度因子修复（2026-05-28）

## 问题

原模型用阈值跳跃判断市场宽度，导致18分偏差（预测49 vs 实际36）。

## 原始实现（有问题）

```python
# 涨停>100=满分, >80=20, >50=15, >30=10, <30=5
if zt > 100: width_score = 25
elif zt > 80: width_score = 20
elif zt > 50: width_score = 15
elif zt > 30: width_score = 10
else: width_score = 5
```

**问题**：阈值跳跃太大，涨停31只和29只差5分（10 vs 5），涨停81只和79只差5分（20 vs 15）。

## 修复后实现（连续函数）

```python
# 优先用真实上涨家数比
if breadth_up and breadth_down:
    breadth_pct = breadth_up / (breadth_up + breadth_down) * 100
    width_score = max(0, min(25, (breadth_pct - 20) / 60 * 25))
# 降级用涨停数连续函数
elif zt > 0:
    width_score = max(0, min(25, zt / 120 * 25))
```

**效果**：
- 涨停30只：30/120*25 = 6.25分（原来5分）
- 涨停50只：50/120*25 = 10.4分（原来15分）
- 涨停80只：80/120*25 = 16.7分（原来20分）
- 涨停120只：120/120*25 = 25分（满分）

## 数据来源

- **优先**：`market`字段中的`up`/`down`（上涨/下跌家数）
- **降级**：`pools`字段中的`limit_up_count`（涨停数）

## 公式

完整公式：`涨停跌停比×25 + 市场宽度×25 + 连板高度×20 + 炸板率×15 + 成交额变化×15`

脚本：`scripts/amadeus/amadeus_emotion.py`
