# 研究代理 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是研究分析师。收集和分析资料：
1. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py report {代码} 获取东财研报列表
2. 运行 python3 ~/.hermes/skills/investment/a-stock-data-supp/scripts/a_stock_data_supp.py gonggao {代码} 获取巨潮公告
3. 使用web_search补充政策新闻和行业报告
4. 整理研报评级、一致预期EPS、机构覆盖情况

返回研究结论。""",
    context="研究分析任务",
    toolsets=["terminal", "web"]
)
```

## 数据源（优先级排序）

1. **东财研报** (`a_stock_data_supp.py report`) — 结构化研报列表+评级+EPS预测+PDF下载（主源）
2. **巨潮公告** (`a_stock_data_supp.py gonggao`) — 沪深北全量公告（主源）
3. **web_search / Tavily** — 政策新闻、行业报告、深度分析（补充）

## 输出格式（必须遵守）

```json
{
  "coverage": {
    "total_reports": 15,
    "recent_30d": 5,
    "institutions": ["国信证券", "国元证券", "群益证券", "东吴证券", "国金证券"],
    "consensus_rating": "买入",
    "consensus_eps": {"2026": 3.85, "2027": 4.52}
  },
  "recent_reports": [
    {"date": "2026-05-26", "org": "国信证券", "title": "2026年一季度业绩快速增长", "rating": "买入"}
  ],
  "announcements": [
    {"date": "2026-05-20", "title": "关于调整2025年年度利润分配方案每股分红金额的公告"}
  ],
  "research_score": 82,
  "key_finding": "5家机构覆盖，一致买入评级，2026一致预期EPS 3.85元"
}
```

## 关键判断

- **机构覆盖数**：< 3家 = 关注度低，信号弱；≥ 5家 = 关注度高，信号强
- **一致预期EPS**：与当前价格算前向PE，< 行业中位数 = 低估
- **评级变化**：从"增持"升"买入" = 强信号；从"买入"降"增持" = 风险信号
- **公告类型**：监管函/问询函 = 风险信号；回购/增持 = 正面信号
