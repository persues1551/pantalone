# 新浪财经实时行情 API 格式

## 请求
```
GET https://hq.sinajs.cn/list=sh600519,sz000333,sh000001
Headers: Referer: https://finance.sina.com.cn
```

代码格式：`sh`+上交所代码 / `sz`+深交所代码。指数同理。

## 响应（个股）
```
var hq_str_sh600519="贵州茅台,1362.000,1361.330,1354.550,1363.580,1350.500,0,0,5083743,6886304982.000,200,1354.500,..."
```

字段顺序（0-indexed）：
| 索引 | 字段 | 说明 |
|------|------|------|
| 0 | 名称 | 股票名称 |
| 1 | 今开 | 今日开盘价 |
| 2 | 昨收 | 昨日收盘价 |
| 3 | 当前价 | 最新成交价 |
| 4 | 最高 | 今日最高 |
| 5 | 最低 | 今日最低 |
| 6 | 日期 | 格式 YYYY-MM-DD（可能为空） |
| 7 | 时间 | 格式 HH:MM:SS（可能为空） |
| 8 | 成交量 | 单位：**手**（1手=100股） |
| 9 | 成交额 | 单位：**元** |
| 10+ | 买卖盘 | 买1量,买1价,卖1量,卖1价,... |

## Python 解析示例
```python
import urllib.request

codes = ['sh600519', 'sz000333', 'sh600900']
url = f"https://hq.sinajs.cn/list={','.join(codes)}"
req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
resp = urllib.request.urlopen(req, timeout=10)
data = resp.read().decode('gbk')

for line in data.strip().split('\n'):
    code = line.split('=')[0].split('_')[2]
    fields = line.split('"')[1].split(',')
    name = fields[0]
    open_p = float(fields[1])
    prev_close = float(fields[2])
    price = float(fields[3])
    high = float(fields[4])
    low = float(fields[5])
    volume = int(float(fields[8]))  # 手
    amount = float(fields[9])       # 元
    change_pct = round((price - prev_close) / prev_close * 100, 2)
    print(f"{code} {name}: {price} ({change_pct:+.2f}%) vol={volume}手")
```

## 已知问题
- 中国移动(600941)等流动性较低的权重股，成交量字段可能异常偏小
- 数据编码为 GBK，部分股票名称含特殊字符
- 非交易时段返回的是上一交易日收盘数据
- 批量请求上限建议 ≤50 只，过多可能被限流

## 与东方财富对比
| 特性 | 新浪 | 东方财富 |
|------|------|----------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 速度 | 快 | 时快时慢 |
| 字段丰富度 | 基础行情 | K线/换手率等 |
| 批量查询 | 原生支持 | 需逐只查询 |
| 历史数据 | 无 | 有 |
