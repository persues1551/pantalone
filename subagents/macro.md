# 宏观分析 Subagent

## 执行方式

通过 `delegate_task` 调用：

```python
delegate_task(
    goal="""你是宏观经济分析师。分析当前宏观环境对A股的影响：
1. 运行 python3 ~/.hermes/scripts/amadeus/amadeus_external.py 采集外围市场数据
2. 分析国内经济数据、货币政策方向、财政政策
3. 分析海外环境（美联储/美元/原油/黄金）

返回宏观面评分和结论。""",
    context="宏观分析任务",
    toolsets=["terminal", "web"]
)
```

## 数据源

1. amadeus_external.py — 外围市场（AKShare→腾讯API双源降级）（主源）
2. amadeus_global.py — 外围市场旧版（备用）
3. web_search — 当脚本数据不足时补充宏观新闻（按需）

## 输出格式（必须遵守）

**必须返回以下JSON结构：**

```json
{
  "global_markets": {
    "dji": {"close": 40000, "pct": 0.5, "source": "akshare_sina"},
    "nasdaq": {"close": 16000, "pct": 0.3, "source": "akshare_sina"},
    "spx": {"close": 5000, "pct": 0.4, "source": "akshare_sina"},
    "a50": {"close": 13000, "pct": -0.2, "source": "tencent"},
    "hsi": {"close": 18000, "pct": 0.1, "source": "akshare_sina"},
    "usdcny": 7.25
  },
  "macro_analysis": {
    "monetary_policy": "描述（基于公开数据，非推测）",
    "fiscal_policy": "描述",
    "overseas_impact": "描述",
    "data_freshness": "今日数据|昨日数据|数据缺失"
  },
  "macro_score": 65,
  "macro_bias": "中性偏多|中性|中性偏空",
  "errors": [],
  "data_sources": ["amadeus_external.py", "web_search(如有)"]
}
```

## 关键规则

1. **外围市场数据必须来自脚本**，不可编造指数点位
2. **脚本返回 null 的项目保持 null**，不可用 LLM 推断补全
3. **宏观分析可以基于公开信息推理**，但必须标注"基于XX消息/数据推断"
4. **政策方向判断必须有事实依据**，不可凭空预测
5. **web_search 结果必须标注来源URL**
