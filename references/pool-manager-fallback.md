# Pool Manager 数据源降级梯队

**修复日期**: 2026-05-21
**脚本**: `~/.hermes/scripts/amadeus/amadeus_pool_manager.py`

## 问题

原 `fetch_sina_prices()` 是唯一数据源。新浪API挂了→全部股票显示"⚠️无法获取行情"，没有降级。

对比：amadeus_data.py（AKShare→Ashare降级）、amadeus_realtime.py（腾讯→AKShare→Ashare降级）都有梯队，唯独pool_manager没有。

## 修复

新增4级降级函数 `fetch_prices_with_fallback(codes) → (prices, source, missing)`

| 级别 | 函数 | 数据源 | 特点 |
|------|------|--------|------|
| 1 | fetch_sina_prices() | 新浪API | 批量查询，速度快 |
| 2 | fetch_tencent_prices() | 腾讯API(qt.gtimg.cn) | 批量查询，GBK编码 |
| 3 | fetch_akshare_prices() | AKShare stock_zh_a_spot() | 全量拉取再过滤 |
| 4 | fetch_ashare_prices() | Ashare(新浪+腾讯双源) | 逐只查询，最慢 |

**关键逻辑**: 每级只处理上一级缺失的股票，不重复查询。最后返回missing_codes标记完全无数据的股票。

## 调用点

- `scan_pool()`: 扫描退池/入池条件时调用
- `report()`: 生成池状态报告时调用
- `check_minefield()`: 仍用fetch_sina_prices()（单只查询，暂不改）

## Pitfalls

1. **AKShare stock_zh_a_spot() 很慢**: 全量拉取5000+只股票，~10秒。只在前面级别缺失时才调用
2. **Ashare是逐只查询**: 如果池里有50只股票且全部缺失，会发50次HTTP请求。设了timeout但仍然慢
3. **source字段标记**: 新浪返回的数据没有source字段，fetch_prices_with_fallback会补上"source":"sina"
4. **返回值类型变了**: 原fetch_sina_prices返回dict，新函数返回tuple(prices, source, missing)。已更新scan_pool和report的调用
5. **check_minefield未改**: 排雷只查1只股票，用新浪够了。如果新浪挂了，排雷会返回"无法获取行情"，不会触发降级

## 类推教训

同类型脚本（数据采集/行情获取）应该有相同级别的降级机制。发现一个模块有降级时，必须检查同类模块。
