# 题材分析 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是题材分析师。分析当前A股热点题材：
1. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py hot 获取同花顺热点归因（题材tags）
2. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py scan 采集新闻（补充）
3. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py hyph 获取行业板块排名
4. 分析涨停板块TOP5、政策催化、板块轮动信号
5. 题材三项检查：盘面强度、消息催化、成交容量

返回题材面评分和结论。""",
    context="题材分析任务",
    toolsets=["terminal", "web"]
)
```

## 数据源（优先级排序）

1. **同花顺热点归因** (`a_stock_data_supp.py hot`) — 人工运营题材tags，最强信号（主源）
2. **东财行业排名** (`a_stock_data_supp.py hyph`) — ~100行业涨跌排名（主源）
3. **amadeus_news_scanner.py** — 4源新闻（东方财富+财联社+新浪+同花顺）（补充）
4. **web_search** — 补充热点新闻和政策消息（按需）

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "hot_reasons": [
    {"code": "000010", "name": "*ST美丽", "change_pct": 4.98, "reasons": ["庭外重组", "一季报扭亏", "市政工程"]}
  ],
  "theme_heat": {
    "top_themes": [{"name": "ST摘帽", "count": 8}, {"name": "人形机器人", "count": 5}],
    "new_themes": ["超级电容", "铟靶材"],
    "fading_themes": ["低空经济"]
  },
  "industry_ranking": {
    "top3": [{"name": "航空机场", "change_pct": -1.39}],
    "bottom3": [{"name": "水泥", "change_pct": -1.90}]
  },
  "rotation_signal": "防御板块(航空/铁路)抗跌，进攻板块(半导体/AI)回调",
  "theme_score": 72,
  "theme_bias": "中性偏弱",
  "key_signals": ["ST摘帽题材活跃(8只涨停)", "人形机器人持续有催化"]
}
```

## 题材三项检查

| 检查项 | 权重 | 评分规则 |
|--------|------|---------|
| 盘面强度 | 40% | 涨停>5只=80+, 涨停2-5只=60+, <2只=40- |
| 消息催化 | 35% | 有政策/产业催化=80+, 无明显催化=50- |
| 成交容量 | 25% | 板块成交额>100亿=80+, 50-100亿=60+, <50亿=40- |

## 关键判断

- **同花顺reason tags**是独家数据：人工运营的题材归因标签，比新闻爬虫准确10倍
- **题材热度词频统计**：reason字段中"+"分隔的tags，词频最高的就是当日主线
- **行业排名**：东财~100行业，比同花顺90行业更全。涨跌家数比涨跌幅更有意义
