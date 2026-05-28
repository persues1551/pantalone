# Tushare Pro 120积分接口清单

## 环境

- 版本：tushare 1.4.29
- Python：`~/.hermes/hermes-agent/venv/bin/python3`（不在系统Python）
- 积分：120级

## ✅ 可用接口

| 接口 | 用途 | 返回字段 | 验证日期 |
|------|------|---------|---------|
| `daily` | A股个股日线 | ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount | 2026-05-20 |
| `moneyflow_hsgt` | 北向资金 | trade_date, ggt_ss, ggt_sz, hgt, sgt, north_money, south_money | 2026-05-20 |
| `ggt_top10` | 港通十大活跃股 | trade_date, ts_code, name, close, p_change, rank | 2026-05-20 |
| `hsgt_top10` | 北向十大活跃股 | trade_date, ts_code, name, close, change, rank | 2026-05-20 |
| `stock_basic` | 股票基础信息 | ts_code, name, market, list_status 等 | 2026-05-20 |
| `cyq_perf` | 筹码分布 | ts_code, trade_date, his_low, his_high, cost_5pct~cost_95pct, weight_avg | 2026-05-20 |
| `shibor` | SHIBOR利率 | date, on, 1w, 2w, 1m, 3m | 2026-05-20 |
| `index_basic` | 指数基础信息 | ts_code, name, market, publisher, category | 2026-05-20 |

## ❌ 不可用接口（需更高积分）

| 接口 | 所需积分 | 替代方案 |
|------|---------|---------|
| `index_daily` | 2000+ | AKShare stock_zh_index_daily |
| `index_weekly` | 2000+ | AKShare |
| `daily_basic` | 2000+ | 无直接替代（PE/PB/换手率） |
| `trade_cal` | 120+ | AKShare tool_trade_date_hist_sina |
| `margin_detail` | 2000+ | AKShare stock_margin_sse |
| `stk_limit` | 2000+ | AKShare stock_zt_pool_em |
| `ths_index` / `ths_daily` | 2000+ | AKShare stock_board_industry_summary_ths |
| `cn_gdp` / `cn_cpi` | 2000+ | AKShare macro_china_gdp |
| `fund_daily` | 2000+ | AKShare fund_etf_hist_em |
| `fx_obasic` | 2000+ | AKShare currency_boc_sina |
| `concept_detail` | 2000+ | AKShare stock_board_concept_name_em |
| `news` | - | AKShare stock_info_global_em/cls/sina/ths |

## 关键发现

1. **北向资金最稳定**：`moneyflow_hsgt` 返回完整的沪股通/深股通/港股通数据，比 AKShare 的 `stock_hsgt_hist_em`（经常返回NaN）可靠得多
2. **筹码分布独特**：`cyq_perf` 提供成本分布百分位数（5%/15%/50%/85%/95%），可用于支撑压力位判断，AKShare 无等价接口
3. **SHIBOR利率**：`shibor` 提供隔夜/1周/2周/1月/3月利率，可用于宏观资金面分析
4. **个股日线可用**：`daily` 接口对个股完全可用（如600519.SH茅台），但指数日线需更高积分
5. **日期格式**：Tushare 使用 `YYYYMMDD` 格式（无横杠），注意与 `YYYY-MM-DD` 的转换

## 使用方式

```bash
# 独立脚本调用（通过 venv Python subprocess）
python3 ~/.hermes/scripts/amadeus/tushare_data.py north
python3 ~/.hermes/scripts/amadeus/tushare_data.py shibor
python3 ~/.hermes/scripts/amadeus/tushare_data.py cyq 600519
python3 ~/.hermes/scripts/amadeus/tushare_data.py top10
python3 ~/.hermes/scripts/amadeus/tushare_data.py daily 600519

# amadeus_data.py 中自动降级使用
# collect_north_flow() AKShare失败时自动调用 Tushare
```
