# 板块分析研究模板

## 研究流程

### Phase 1: 板块扫描
```bash
# 获取板块列表和涨跌幅
python3 -c "
import akshare as ak
df = ak.stock_board_industry_name_em()
print(df.sort_values('涨跌幅', ascending=False).head(10))
"
```

### Phase 2: 资金流向
```bash
# 板块资金流向
python3 -c "
import akshare as ak
df = ak.stock_sector_fund_flow_rank(indicator='今日')
print(df.head(10))
"
```

### Phase 3: 个股筛选
对目标板块内的个股进行：
1. 排雷扫描（amadeus_screening.py）
2. 估值评估（amadeus_valuation.py）
3. 技术指标（amadeus_indicators.py）
4. 买入评分（amadeus_buy_scorer.py）

### Phase 4: 假设生成
基于板块数据生成投资假设，例如：
- "XX板块受政策利好，龙头股估值仍低于历史中位数"
- "YY板块资金持续流入，技术面突破关键阻力位"

### Phase 5: 评审与报告
按标准流程评审，输出板块投资报告。

## 输出格式

```markdown
# XX板块投资研究报告

## 板块概况
- 近期涨跌幅、资金流向、估值水平

## 核心假设
- 多/空方向、逻辑链条、时间框架

## 个股推荐
| 标的 | 方向 | 入场 | 止损 | 目标 | 仓位 | 评分 |
|---|---|---|---|---|---|---|

## 风险提示
- 板块轮动风险、政策变化、估值回调

## 评审意见
- Bull/Bear/Quant/Macro/Contrarian 各自观点
```
