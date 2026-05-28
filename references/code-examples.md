# Amadeus 代码示例与详细数据

## 单票上限规则（v3.1修复）

```python
min_lot_cost = price * 100  # 最少1手所需金额
pct_limit = total_value * 0.25  # 25%仓位限制
max_per_stock = max(pct_limit, min_lot_cost)  # 取大值，确保高价股能买至少1手
```

## 模拟盘集成命令

```bash
# 1. 查看当前持仓状态（含实时价格和浮盈浮亏）
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py status

# 2. 收盘后记录日盈亏
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py daily_update

# 3. 记录交易
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py record '{"action":"buy","code":"600900","name":"长江电力","pool":"A","price":27.0,"shares":500,"reason":"模拟买入"}'

# 4. 买入评分
python3 ~/.hermes/scripts/amadeus/amadeus_buy_scorer.py

# 5. 大盘环境过滤
python3 ~/.hermes/scripts/amadeus/amadeus_market_filter.py

# 6. 排雷扫描
python3 ~/.hermes/scripts/amadeus/amadeus_screening.py
```

## to_docx.py 用法

```bash
# 正确：从stdin读取
cat report.md | python3 ~/.hermes/scripts/amadeus/to_docx.py "标题" output.docx

# 错误：会导致空白文档
python3 to_docx.py input.md output.docx
```

## Ashare API

```python
from Ashare import get_price
data = get_price('sh000001', end_date='20260506', count=1)
# 返回DataFrame：open, high, low, close, volume
```

## 腾讯行情API（终极备用）

```bash
# 指数实时
curl -s "https://qt.gtimg.cn/q=sh000001,sz399001,sz399006" | iconv -f gbk -t utf-8
# 格式：v_sh000001="1~上证指数~000001~现价~昨收~开盘~成交量~...~涨跌幅~...~日期时间~..."
# 关键字段位置：[3]=现价 [4]=昨收 [32]=涨跌幅% [33]=最高 [34]=最低 [37]=成交额(万)

# 个股实时
curl -s "https://qt.gtimg.cn/q=sh601138,sz002475,sz300502" | iconv -f gbk -t utf-8
```

## Research Agent 用法

```bash
python3 amadeus_research.py --topic "半导体板块投资机会" --depth 2
python3 amadeus_research.py --list-sessions
python3 amadeus_research.py --report <session_id>
```

## v3版本对比数据

| 指标 | 旧规则v1 | v2(回放) | v3(严格) |
|------|----------|----------|----------|
| 最终资产 | 199,583 | 214,160 | 205,013 |
| 收益率 | -0.2% | +7.08% | +2.51% |
| 交易次数 | 4笔 | 7笔 | 9笔 |
| 最高暴露 | 47% | 64% | 42% |

## 交易记录（5/6-5/14）

| 日期 | 操作 | 代码 | 名称 | 价格 | 股数 | 金额 | 盈亏 | 触发规则 |
|------|------|------|------|------|------|------|------|----------|
| 5/6 | 买入 | 601138 | 工业富联 | 62.00 | 400 | 24,800 | - | 评分76 |
| 5/7 | 买入 | 601138 | 工业富联 | 63.20 | 300 | 18,960 | - | 分批确认 |
| 5/11 | 买入 | 002475 | 立讯精密 | 76.06 | 300 | 22,818 | - | 评分86 |
| 5/12 | 卖出 | 601138 | 工业富联 | 70.50 | 200 | 14,100 | +1,597 | +8%止盈 |
| 5/13 | 卖出 | 601138 | 工业富联 | 70.80 | 100 | 7,080 | +829 | +8%止盈 |
| 5/14 | 卖出 | 601138 | 工业富联 | 68.29 | 100 | 6,829 | +578 | +8%止盈 |

## 情绪温度验证数据

| 日期 | 温度 | 分级 | 验证 |
|------|------|------|------|
| 5/6 | 72 | 高潮 | ✅ |
| 5/12 | 42 | 升温 | ✅ |
| 5/13 | 80 | 高潮 | ✅ |
| 5/14 | 28 | 修复 | ✅ |

## Research Agent 角色评审

| 角色 | 视角 | 关注点 |
|------|------|--------|
| 🐂 Bull | 成长型 | 上行空间、创新性 |
| 🐻 Bear | 价值型 | 下行风险、估值 |
| 📊 Quant | 量化型 | 数据充分性、回测 |
| 🌍 Macro | 宏观型 | 政策方向、资金流向 |
| 🔄 Contrarian | 逆向型 | 市场共识、反面论据 |
