# 腾讯行情API — 终极备用数据源

## 概述

腾讯行情API（qt.gtimg.cn）是最稳定的实时行情备用数据源。当AKShare连接超时、RemoteDisconnected时使用。

## 端点

```
https://qt.gtimg.cn/q={codes}
```

- codes 用逗号分隔：`sh000001,sz399001,sz399006`
- 指数代码：上证`sh000001`、深证`sz399001`、创业板`sz399006`、科创50`sh000688`
- 个股代码：沪市`sh600xxx`、深市`sz000xxx`/`sz002xxx`/`sz300xxx`

## 响应格式

GBK编码，需 `iconv -f gbk -t utf-8` 转码。

每条数据格式：
```
v_sh000001="1~上证指数~000001~现价~昨收~开盘~成交量~...~日期时间~涨跌额~涨跌幅~最高~最低~现价/成交量/成交额~成交量~成交额(万)~...";
```

## 关键字段位置（~分隔）

| 索引 | 字段 | 示例 |
|------|------|------|
| 1 | 名称 | 上证指数 |
| 3 | 现价 | 4199.19 |
| 4 | 昨收 | 4242.57 |
| 5 | 开盘 | 4256.16 |
| 32 | 涨跌幅% | -1.02 |
| 33 | 最高 | 4258.86 |
| 34 | 最低 | 4184.04 |
| 37 | 成交额(万) | 100900644 |

## 使用示例

```bash
# 指数
curl -s "https://qt.gtimg.cn/q=sh000001,sz399001,sz399006" | iconv -f gbk -t utf-8

# 个股（观察池）
curl -s "https://qt.gtimg.cn/q=sh601138,sz002475,sz300502,sz300308" | iconv -f gbk -t utf-8

# Python解析
import subprocess, re
result = subprocess.run(['bash', '-c',
    'curl -s "https://qt.gtimg.cn/q=sh000001" | iconv -f gbk -t utf-8'],
    capture_output=True, text=True, timeout=10)
m = re.search(r'v_(\w+)="(.+)"', result.stdout)
fields = m.group(2).split('~')
name, price, change_pct = fields[1], fields[3], fields[32]
```

## 优势

- 无需API Key、无需登录
- 响应快（<2s）
- 稳定性极高（腾讯CDN）
- 支持批量查询

## 限制

- 仅实时行情，无历史数据
- GBK编码需转码
- 字段位置固定但数量多，需精确解析
- 非官方API，可能随时变更

## 触发条件

当以下情况发生时自动降级到腾讯API：
1. AKShare `RemoteDisconnected` 或超时
2. amadeus_data.py 采集失败
3. 东方财富API连接中断

## 验证记录

| 日期 | 场景 | 结果 |
|------|------|------|
| 2026-05-14 | 午间复盘，AKShare全部超时 | ✅ 腾讯API成功获取指数+个股 |
