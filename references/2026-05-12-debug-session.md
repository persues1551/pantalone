# 2026-05-12 调试记录

## 触发场景
主人询问"股票推送呢"——盘前早报 cron job 未推送。

## 根因链

### 1. Cron 调度器假死（表层）
- Hermes gateway cron ticker 在 5月11日 20:48 最后一次 `started` 后静默停止
- 5月12日 09:00 盘前早报 `last_run_at` 为 null，未执行
- 手动 `cronjob run` 仅重新调度（next_run_at 改为立即）但未触发执行
- 最终通过 `hermes gateway restart` 恢复，后续午间/收盘均正常

### 2. amadeus_data.py 数据采集崩溃（更深层）
- `stock_zh_a_spot()` 盘前(09:06)返回全部平盘：up=0, down=0, flat=5514, total_amount=0
- `collect_market_overview()` 返回全0数据，market 字段 unusable
- 涨跌停池 `collect_limit_pools()` 首次运行时崩溃 KeyError（疑似 API 偶发超时），第二次手动运行成功

### 3. NaN 崩溃（边界条件）
- `collect_north_flow()` 中 `stock_hsgt_hist_em` 返回 `当日成交净买额` 为 NaN
- `float(NaN) / 1e8` → 不崩溃但产生 NaN 值，JSON 序列化时可能出问题
- 修复：加 `pd.isna()` 检查 + try/except 包装

## 修复内容

### amadeus_data.py（~/hermes/scripts/amadeus_data.py）
1. **日期感知**：盘前（<9:30）自动查询 T-1 日期
2. **NaN 处理**：北向资金 `net_flow` 加 `pd.isna()` 防护
3. **指数降级**：无当日数据时取最近2条，自动带 `t_minus_2_close`
4. **函数签名**：`collect_limit_pools(query_date)`, `collect_lianban(query_date)`, `collect_index_data(query_date_str)` 均支持外部传入日期

### amadeus skill（~/.hermes/skills/investment/amadeus/SKILL.md）
1. **日期口径铁律**：盘前用 T-1 查涨跌停池/指数
2. **API 降级策略**：全0检测 → 改查 T-1；空 DataFrame → retry；单接口崩溃不中断
3. **Cron 可靠性规则**：每次早报检查 ticker 状态
4. **系统迭代原则**：复盘发现问题直接修复，不请示

## 验证结果
- 盘前早报：09:56 执行成功
- 午间复盘：12:41 执行成功
- 收盘复盘：15:53 执行成功
- 三项均状态 ok
