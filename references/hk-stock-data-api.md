# 港股数据采集 API 参考

## 腾讯行情 API（港股实时行情+PE）

**接口**：`https://qt.gtimg.cn/q=hk{代码}`

**港股代码格式**：`hk00700`（腾讯）、`hk09988`（阿里）等，5位代码前加`hk`

**返回字段（~分隔）**：
- `parts[1]` = 名称
- `parts[2]` = 代码
- `parts[3]` = 最新价
- `parts[4]` = 昨收
- `parts[32]` = 涨跌幅(%)
- `parts[33]` = 最高价
- `parts[34]` = 最低价
- `parts[39]` = **市盈率PE**（动态）
- `parts[45]` = 总市值（亿港元）
- `parts[46]` = 市净率PB
- `parts[47]` = 股息率

**批量查询**：`https://qt.gtimg.cn/q=hk00700,hk09988,hk03690`（逗号分隔，多只一次返回）

**编码**：GBK，需 `iconv -f gbk -t utf-8`

**示例**：
```
curl -s "https://qt.gtimg.cn/q=hk00700" | iconv -f gbk -t utf-8
```

**解析代码**：

仓内纯解析器：`scripts/tencent_quote_parser.py::parse_tencent_quotes`。它只解析调用方提供的GBK响应字节，不发起网络请求，也不写缓存。默认测试使用固定脱敏fixture；需要验证实时端点时，显式设置`PANTALONE_LIVE_HTTPS=1`运行只读smoke test。

```python
for line in output.strip().split(";"):
    parts = line.split("~")
    if len(parts) < 50:
        continue
    name = parts[1]
    code = parts[2]
    price = parts[3]
    change_pct = parts[32]
    pe = parts[39]
    total_mv = parts[45]  # 亿港元
```

## 恒生指数/恒生科技

| 指数 | 代码 |
|------|------|
| 恒生指数 | `hkHSI` |
| 恒生科技 | `hkHSTECH` |

## 南向资金（AKShare）

```python
import akshare as ak
df = ak.stock_hsgt_fund_flow_summary_em()
# 返回字段：交易日、类型(沪港通/深港通)、板块(港股通(沪)/港股通(深))、
#          资金方向(南向/北向)、成交净买额、资金净流入
# 筛选南向：df[df["资金方向"]=="南向"]
```

**注意**：
- `成交净买额` 单位是亿元
- 沪港通和深港通分别返回，需合计
- AKShare 其他港股接口（stock_hk_spot_em、stock_hk_main_board_spot_em）经常 RemoteDisconnected，不可靠

## AH 股溢价

```python
import akshare as ak
df = ak.stock_zh_ah_spot()
# 返回：代码、名称、最新价、涨跌幅、成交量、成交额
# 注意：不包含 H 股代码/名称/溢价率（接口已简化）
```

## 港股 OCIFQ 评估要点

港股与A股OCIFQ框架相同，但有以下差异：
- **O（寡头）**：港股互联网巨头（腾讯/阿里/美团）寡头地位更稳固
- **C（催化）**：关注AI商业化、出海、回购分红
- **F（财务）**：港股科技股可能亏损（PE为负），需看营收增长和自由现金流
- **估值**：港股整体PE低于A股，AH溢价通常在120-160区间

## 高股息港股筛选

港股高股息标的特征：
- PE < 10
- 股息率 > 5%
- 国企/央企背景
- 现金流充沛
- 典型：建设银行(PE 6)、中海油(PE 9)、中国移动(PE 12)
