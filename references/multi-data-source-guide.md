# 多数据源采集指南

## 数据源清单

| 脚本 | 数据源 | 覆盖内容 | 稳定性 |
|------|--------|----------|--------|
| `amadeus_data.py` | 新浪/同花顺/Ashare | 市场总貌、指数、涨跌停、连板、北向资金、板块 | ⭐⭐⭐⭐ |
| `amadeus_global.py` | Investing | 美股三大指数、A50期货、港股、汇率 | ⭐⭐⭐ |
| `amadeus_indicators.py` | AKShare | 观察股MA/MACD/RSI/布林带/量价 | ⭐⭐⭐ |
| `amadeus_financials.py` | 同花顺+巨潮 | 个股财报 | ⭐⭐⭐ |
| `amadeus_news_scanner.py` | 东方财富/财联社/新浪/同花顺 | 新闻4源260条 | ⭐⭐⭐⭐ |

## Ashare API 用法

```python
import sys
sys.path.insert(0, '/home/ubuntu/.hermes/scripts/amadeus')
from Ashare import get_price

# API: get_price(code, end_date='', count=10, frequency='1d', fields=[])

# 获取上证指数某日数据
data = get_price('sh000001', end_date='20260506', count=1)
# 返回DataFrame: open, high, low, close, volume

# 获取多日数据
data = get_price('sh000001', end_date='20260506', count=5)

# 获取个股数据
data = get_price('600900', end_date='20260506', count=1)
```

## 数据采集优先级

1. **先用amadeus_data.py**（多源冗余，最稳定）
2. **失败再用AKShare单源**（板块API不稳定）
3. **最后用Ashare备用**（新浪+腾讯双源）

## 已知坑

### AKShare板块API不稳定
- `stock_board_industry_name_em()` 经常 `RemoteDisconnected`
- 备用方案：用amadeus_data.py的`collect_sectors()`

### Ashare个股历史数据可能为空
- 对于5/6-5/8的历史数据，Ashare可能返回空DataFrame
- 原因：数据源可能不保留太久的历史
- 备用方案：用AKShare的`stock_zh_a_hist()`

### 北向资金数据缺失
- `stock_hsgt_hist_em()` 返回的近期数据可能是NaN
- 原因：数据源延迟或接口问题
- 备用方案：用amadeus_data.py的`collect_north_flow()`

## 历史数据回溯采集

```python
import sys, json, os
sys.path.insert(0, os.path.expanduser("~/.hermes/scripts/amadeus"))
from Ashare import get_price

dates = ['20260506', '20260507', '20260508']

for d in dates:
    for code, name in [('sh000001','上证'), ('sz399001','深证'), ('sz399006','创业板')]:
        data = get_price(code, end_date=d, count=1)
        if data is not None and len(data) > 0:
            row = data.iloc[0]
            print(f"{d} {name}: {row['close']:.2f}")
```
