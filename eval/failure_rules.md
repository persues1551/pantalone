# failure_rules.md — 失败规则与故障排查

## Cron 调度器静默停止

**症状**：所有 cron job `last_run_at` 为 null，推送不到。

**根因**：Hermes gateway 的 cron ticker 在 drain-timeout 重启后静默假死。`gateway/run.py` 将 tick 异常记录为 DEBUG 级别，日志不可见。

**代码修复**：
```bash
sed -i 's/logger.debug("Cron tick error/logger.warning("Cron tick error/' ~/.hermes/hermes-agent/gateway/run.py
```

**保底**：系统 crontab 三重重启（08:55/11:55/15:25）确保每次推送前 ticker 鲜活。

**详细排查**：见 hermes-agent 技能 → Cron Job Troubleshooting。

## amadeus_data.py 部分崩溃

**症状**：脚本在涨跌停采集步骤抛出 `KeyError`（东方财富 API 列名变更），但市场总貌和指数数据已成功缓存。

**应对**：
1. 脚本崩溃后，先读缓存文件：`cat ~/.hermes/cache/amadeus/market_YYYY-MM-DD.json`
2. 缓存中 `indices` 和 `pools`（含涨停/跌停/炸板/连板）通常可用
3. 用 pools 数据替代 market 数据生成报告
4. 标注缺失字段（市场宽度、成交额），按情绪温度规则处理

## 东方财富个股API 全面断连

**症状**：`ak.stock_zh_a_hist()` 所有个股查询返回 `RemoteDisconnected`。

**根因**：东方财富服务器对批量历史K线请求限流或临时维护。

**应对（已验证有效）**：
1. **立即降级至新浪 API**：`https://hq.sinajs.cn/list=sh600519,sz000333,...`
2. 新浪返回格式：`var hq_str_sh600519="名称,今开,昨收,当前价,最高,最低,日期,时间,成交量(手),成交额(元),买1量,买1价,卖1量,卖1价,..."`
3. 个股涨跌幅 = `(当前价 - 昨收) / 昨收 × 100`
4. 一次请求可批量查询多只股票，逗号分隔
5. **需要 Referer header**：`Referer: https://finance.sina.com.cn`
6. 数据编码为 GBK，需 `.decode('gbk')`

**不可用时的替代**：Ashare (`scripts/amadeus/Ashare.py`) 内置新浪+腾讯双内核，代码更简洁。

## 板块资金流单位存疑

**症状**：`ak.stock_board_industry_summary_ths()` 返回的净流入数值偏小（如电力净流入13.44，与3.27万亿总成交额不匹配）。

**待验证**：同花顺接口返回的净流入单位可能是**万元**而非亿元。

**暂定处理**：使用同花顺数据时标注【单位待核验】，同时尝试东方财富 `ak.stock_sector_fund_flow_rank()` 做交叉验证。

## 模拟器 INIT_CAPITAL 硬编码bug

**症状**：`amadeus_simulator.py` 第60行 `INIT_CAPITAL = 100000.0` 与规范要求的 20万 不符。

**修复**：已修改为 `INIT_CAPITAL = 200000.0`，并同步修改第139行 print 输出。

**验证**：删除旧 DB 后重新 `init`，status 确认显示 `"initial_capital": 200000.0`。

## legu 接口非交易时段返回全零

**症状**：`stock_market_activity_legu()` 在 A 股非交易时段（含盘前）返回 `up=0, down=0, flat=总股数, total_amount=0`。

**判断**：若 pools 中有涨停/跌停数据但 legu 返回全零 → 非交易时段正常行为，以 pools 数据为准。

**策略**：盘前早报优先用东方财富涨停/跌停/炸板池的历史数据，legu 仅作交叉验证。

## QQ WebSocket 导致 ticker 假死

**症状**：gateway 日志中 QQ 频繁 `Disconnected` / `Session error (4009)`，每次断连触发 cron ticker stop → start。

**根因**：QQ Bot WebSocket 连接不稳定，每天断连 4-5 次。

**修复**：所有 Amadeus cron job 改为投递微信（`origin`），输出 `.docx` Word 文档。

**保底**：系统 crontab `55 8 * * 1-5 /home/ubuntu/.hermes/scripts/restart_gateway.sh` 每日 08:55 重启 gateway。

## 财联社新闻返回空数据

**症状**：news_YYYY-MM-DD.json 中 cls 为空列表。

**排查**：检查 `amadeus_news.py` 中的 API URL 和解析逻辑，可能接口已升级。

**降级**：用 AKShare 其他新闻接口或直接抓取财联社网页。

## 强势股池/连板数据脚本崩溃

**症状**：`amadeus_data.py` 在强势股池步骤 KeyError 或崩溃。

**应对**：
1. 从已缓存的 `pools.limit_up_stocks` 中推断活跃题材
2. 连板高度估算：查历史涨停池数据，或从控制台输出提取
3. 情绪温度中"连板高度"因子用估算值，标注【连板数据存疑】

## amadeus_indicators.py RSI/MACD不写入JSON

**症状**：indicators_YYYY-MM-DD.json 中无 rsi14 和 macd_signal 字段。

**根因**：脚本计算了 RSI/MACD 并 print 到控制台，但 `json.dump` 时未包含这些字段。

**临时应对**：从脚本运行的控制台输出中手动提取 RSI/MACD 值。

**永久修复**：修改 `amadeus_indicators.py`，在保存JSON前将 `rsi14` 和 `macd_signal` 加入 data dict。

## 通用降级策略

```
Level 1: 主数据源（东方财富/同花顺）
  ↓ 失败
Level 2: 备用数据源（新浪/腾讯）
  ↓ 失败
Level 3: 标注"数据缺失"
```

**禁止**：搜索失败时编造结果。宁可写"数据缺失"，也不脑补。
