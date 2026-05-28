# A股数据源参考

## AKShare 已验证接口

### ✅ 稳定可用
| 接口 | 用途 | 注意 |
|------|------|------|
| `stock_market_activity_legu()` | 涨跌家数、涨停跌停、活跃度 | 最优先使用 |
| `stock_zh_index_daily(symbol="sh000001")` | 上证指数日线 | volume是手，非金额 |
| `stock_zh_index_daily(symbol="sz399001")` | 深证成指 | 同上 |
| `stock_zh_index_daily(symbol="sz399006")` | 创业板指 | 同上 |
| `stock_zt_pool_em(date="YYYYMMDD")` | 涨停板池 | 不含ST？待验证 |
| `stock_zt_pool_dtgc_em(date="YYYYMMDD")` | 跌停板池 | |
| `stock_zt_pool_zbgc_em(date="YYYYMMDD")` | 炸板池 | |
| `stock_zt_pool_strong_em(date="YYYYMMDD")` | 强势股池 | 含历史连板股，非当日涨停 |
| `stock_sse_summary()` | 上交所概况 | 市值、上市家数 |
| `stock_margin_sse()` | 融资融券 | 会滞后1天 |

### ⚠️ 不稳定（超时/连接重置）
| 接口 | 问题 |
|------|------|
| `stock_zh_a_spot_em()` | RemoteDisconnected |
| `stock_board_industry_name_em()` | RemoteDisconnected |
| `stock_zh_index_daily_em()` | RemoteDisconnected |
| `stock_szse_summary()` | ConnectionResetError |

### ❌ 不存在
| 接口 | |
|------|------|
| `stock_hsgt_north_net_flow_in_em()` | 北向资金 |

## 2026-05-12 复盘数据管道发现

### 指标脚本JSON持久化（已修复 v2.1）
`amadeus_indicators.py` v2.1 已修复，RSI14 和 macd_signal 已写入JSON。
JSON字段含: code, pool, date, close, change_pct, MA5-MA60, vol_ratio, bb_width, RSI14, macd_signal。

### 板块资金流单位（2026-05-20 已验证）
同花顺 `stock_board_industry_summary_ths()` 返回的净流入数值**单位为亿元**。
验证数据：半导体+141.81亿、电池+32.06亿、光伏设备+20.32亿 — 与市场常识吻合。
`amadeus_sector_flow.py` 内置自动单位核验逻辑（基于数值大小启发式判断）。
列名：`板块`（非`板块名称`）、`净流入`、`涨跌幅`（2026-05-20实测）。

### 连板数据降级策略
当 `stock_zt_pool_strong_em()` 崩溃时，可从 `stock_zt_pool_em()` 涨停池数据推断连板：
- 检查涨停股是否连续多日出现在涨停池中
- 或从脚本控制台输出（amadeus_indicators.py 打印了连板信息）提取
- 精确连板数需强势股池接口正常工作

### 财联社新闻API
`amadeus_news.py` 返回空数据（cls为空列表）。API格式可能已变更，需排查。

### 北向资金
`stock_hsgt_north_net_flow_in_em()` 接口不存在。需找到正确的AKShare接口名或用新浪/东方财富直接抓取。

## 待补充数据
1. **成交额** — 已解决：从 market_*.json 的 market.total_amount 读取（2026-05-20）
2. **北向资金** — 已解决：Tushare moneyflow_hsgt 作为 AKShare 备用（2026-05-20）
3. **行业板块涨跌** — 同花顺可用，单位已验证为亿元（2026-05-20）
4. **个股财务数据** — amadeus_financials.py 待验证
5. **外围市场** — A50期货、汇率数据仍不稳定，amadeus_external.py 已增加腾讯API备用但仍3/5缺失
6. **RSI/MACD** — amadeus_realtime.py 已解决（腾讯API实时行情+AKShare技术指标）
7. **连板数据** — 已解决：从 market_*.json 的 lianban[].board_count 读取（2026-05-20）
8. **SHIBOR利率** — 新增：tushare_data.py shibor（2026-05-20）
9. **筹码分布** — 新增：tushare_data.py cyq（2026-05-20）

## 环境配置
- Python: `/usr/bin/python3`（带 akshare）
- 安装: `pip install akshare --break-system-packages`
- Venv Python 需要单独安装 akshare
