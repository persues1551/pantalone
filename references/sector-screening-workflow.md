# 板块选股速筛工作流

> 从"某个板块值得看"到"具体标的入池"的完整链路。
> 适用场景：主人看到直播/新闻/研报提到某个板块，要求"研究一下选股"。

## 触发信号

- 主人截图直播/新闻，问"这个板块怎么样"
- 主人说"XX板块选股""XX概念研究一下"
- 研报/新闻提到某个新主线

## 5步流程

### Step 1: 板块全景扫描（2分钟）

搜索目标：
- 板块指数/ETF代码和近期表现
- 细分领域拆分（至少拆出5-8个子赛道）
- 每个子赛道的龙头公司（2-3只）
- 近期政策/事件催化
- 机构观点汇总

工具：web_search / Tavily 搜关键词组合，如「半导体材料 A股 龙头」「XX板块 国产替代 上市公司」

⚠️ AKShare板块数据常见失败：stock_board_concept_name_em() 和 stock_board_industry_name_em() 经常超时/连接断开。替代方案：用Jina Reader抓取东方财富财经首页 https://r.jina.ai/https://finance.eastmoney.com/a/czqyw.html 获取最新行业催化新闻；或用腾讯行情API直接拉候选标的的实时数据。详见 references/proven-data-api-patterns.md。

Jina Reader新闻发现（验证：2026-07-09）：
```bash
# 板块催化新闻发现
curl -s "https://r.jina.ai/https://finance.eastmoney.com/a/czqyw.html" -H "Accept: text/plain"

# 具体事件详情
curl -s "https://r.jina.ai/https://finance.eastmoney.com/a/<ID>.html" -H "Accept: text/plain"
```
当AKShare连接失败或超时时，Jina Reader是突破东方财富/百度新闻反爬的首选新闻获取工具。

多板块跨域研究：当主人说「研究XX和YY行业」（如半导体+存储），需要先识别两个行业的重叠标的（如兆易创新既是半导体也是存储），再分别列出各行业独有标的。重叠标的是重点分析对象。

### Step 2: 实时行情筛选（1分钟）

用腾讯行情API批量获取所有候选标的的实时数据：
```python
# 腾讯API格式：sh600xxx/sz000xxx/sz300xxx/sh688xxx
url = f'https://qt.gtimg.cn/q={",".join(codes)}'
# 关键字段：parts[3]=现价, parts[32]=涨跌%, parts[37]=成交额万, parts[39]=PE, parts[45]=总市值亿
```

筛选条件：
- 剔除ST、停牌、成交额<5000万
- 剔除PE为负或PE>500（泡沫）
- 按涨跌%排序，识别逆势上涨 vs 暴跌回调

### Step 3: OCIFQ快速打分（5分钟）

对通过Step 2的标的（通常15-20只），快速评估五维：

| 维度 | 快速判断方法 |
|------|-------------|
| O 寡头定价权 | 搜索"XX公司 市占率""XX公司 壁垒"，CR3是否>50% |
| C 长周期催化 | 催化持续≥4季度？AI/国产替代/政策是长周期 |
| I 行业利润断层 | 同行业多家公司同步业绩改善？搜"XX行业 业绩大增" |
| F 财务三爆 | 营收≥30%+利润≥50%+毛利率≥5pct，至少2项达标 |
| Q 连续季报 | 看最近4个季度的趋势，是否连续改善 |

**财务数据快速采集管线（验证：2026-07-09）**：
```python
import akshare as ak

# 批量获取多家公司的季度财务数据（每只~2秒）
stocks = [('603986', '兆易创新'), ('002371', '北方华创')]
for code, name in stocks:
    df = ak.stock_financial_abstract_ths(symbol=code, indicator='按报告期')
    for _, row in df.iterrows():
        rp = str(row.get('报告期', ''))
        if '2025' not in rp and '2026' not in rp:
            continue
        rev = row.get('营业总收入', '')
        rev_yoy = row.get('营业总收入同比增长率', '')
        profit = row.get('净利润', '')
        profit_yoy = row.get('净利润同比增长率', '')
        gross = row.get('销售毛利率', '')
        print(f"{rp}: 营收{rev}({rev_yoy}) 净利{profit}({profit_yoy}) 毛利率{gross}%")
```
可用列：报告期, 营业总收入, 营业总收入同比增长率, 净利润, 净利润同比增长率, 扣非净利润, 基本每股收益, 每股净资产, 销售毛利率, 销售净利率, 净资产收益率
详见 references/proven-data-api-patterns.md 第五章。

**K线技术分析快速获取（结合Step 2筛选后使用）**：
```bash
curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh603986,day,,,60,qfq"
```
返回 JSON 的 data.{code}.qfqday 数组，格式：[日期, 开盘, 收盘, 最高, 最低, 成交量]
从K线可计算：MA5/MA10/MA20、量比、20日涨跌幅、支撑/压力位、RSI估算。

输出：按OCIFQ总分排序，筛出前5-8只。

### Step 4: 深度对比分析（选做）

如果主人要求"深入分析"，对Top 2-3只做完整对比：
- 财务数据对比表（营收/净利/增速/毛利率/ROE/PE/PEG）
- 主营业务构成和客户结构
- 产能扩张计划
- 机构评级和目标价
- 股东结构（北向资金、大基金、社保）
- 近期公告和重大事项

工具：delegate_task 并行搜索每只标的的深度信息。

### Step 5: 入池建议

根据OCIFQ评分给出建议：
- ≥85分：A+评级候选；必须完成OCIFQ连续验证和风险审查，不得自动入池
- 70-84分：暂不入池，列入关注清单
- <70分：不建议关注

入池必须填：假设/催化剂/成功标准/失败标准/验证时间。

## 一日游判据

板块暴涨次日需观察：
- 资金流向是否持续（连续2日流入才确认主线）
- 前日涨停股是否分化（跌>5%的一日游概率高）
- 是否有新催化剂（政策/涨价/订单）

入池与退池建议唯一采用 `rules/pool_rules.md` 的权威格式与授权边界。

## 数据源优先级

实时行情：腾讯API（稳定）> AKShare（限流）
基本面：东方财富 > 同花顺 > AKShare
行业新闻：财联社 > 东方财富 > 新浪

## 典型输出格式

```
板块全景 → 实时行情表 → OCIFQ筛选表 → Top标的深度对比 → 入池建议
```

完整度控制：板块速报覆盖全景、数据、OCIFQ、风险和候选；需要更深证据时另出完整研究。
