# v3.0+ 脚本清单

## 新建脚本

| 脚本 | 路径 | 功能 | 用法 |
|------|------|------|------|
| amadeus_screening.py | scripts/amadeus/ | 排雷扫描（ST/质押/商誉/审计/现金流） | `python3 amadeus_screening.py [代码]` |
| amadeus_valuation.py | scripts/amadeus/ | 估值模型（PE-Band+分位数） | `python3 amadeus_valuation.py [代码]` |
| amadeus_market_filter.py | scripts/amadeus/ | 大盘环境四级过滤器 | `python3 amadeus_market_filter.py` |
| amadeus_buy_scorer.py | scripts/amadeus/ | 买入信号评分系统（满分100） | `python3 amadeus_buy_scorer.py [代码]` |
| amadeus_emotion.py | scripts/amadeus/ | 情绪温度标准化计算（v2.0含过期检测） | `python3 amadeus_emotion.py [日期]` |
| amadeus_realtime.py | scripts/amadeus/ | 实时行情+技术指标（腾讯API+AKShare） | `python3 amadeus_realtime.py [--indices]` |
| amadeus_external.py | scripts/amadeus/ | 外围市场多源冗余采集 | `python3 amadeus_external.py` |
| amadeus_sector_flow.py | scripts/amadeus/ | 板块资金流独立入口+单位核验 | `python3 amadeus_sector_flow.py` |
| tushare_data.py | scripts/amadeus/ | Tushare数据源（北向/SHIBOR/筹码/十大活跃） | `python3 tushare_data.py [north\|shibor\|cyq\|top10\|all]` |
| tavily_search.py | scripts/ | Tavily AI搜索 | `python3 tavily_search.py "关键词"` |

## 重写脚本

| 脚本 | 变更 |
|------|------|
| amadeus_sim_integrate.py | v2.0: 实时价格获取(腾讯API)+单票上限检查+总暴露检查+部分平仓+价格校验 + GBK编码修复 |
| amadeus_indicators.py | v2.0: RSI/MACD写入JSON+WATCHLIST同步+禁止买入检查+均线趋势计算 |
| amadeus_collect_all.sh | 修复废弃引用+嵌入排雷/过滤/pool_manager auto/情绪温度/daily_update |
| amadeus_data.py | 新增collect_sector_flow()同花顺板块资金流采集 + 北向资金Tushare降级 + 板块列名兼容 |
| amadeus_pool_manager.py | 新增auto命令：自动scan退池+integrate-news入池+写入日志 |
| amadeus_emotion.py | v2.0: 过期检测+market_extra(连板/成交额)+data_freshness字段 |
| amadeus_market_filter.py | GBK编码修复 |
| amadeus_global.py | 被 amadeus_external.py 替代（多源降级） |

## collect_all.sh 执行顺序

```bash
1. amadeus_data.py           # 市场数据（指数/涨跌停/北向/板块/板块资金流）
2. amadeus_indicators.py     # 技术指标（MA/MACD/RSI/布林带）
3. amadeus_financials.py     # 财报数据
4. amadeus_news_scanner.py   # 新闻扫描
5. amadeus_screening.py      # 排雷扫描
6. amadeus_pool_manager.py auto  # 观察池自动管理（退池+入池+日志）
7. amadeus_market_filter.py  # 大盘环境过滤
8. amadeus_sim_integrate.py daily_update  # 模拟盘日更新
9. amadeus_emotion.py        # 情绪温度计算
```
