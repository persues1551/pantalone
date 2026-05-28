# Amadeus 系统连续性检查清单

定期检查各组件是否正常工作，发现问题立即修复。

## 检查项

### 1. 模拟盘 (simulator.db)
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py status
```
- 检查：positions/trades/daily_pnl 是否有数据
- 问题：全0 → cron未调用record/daily_update
- 修复：更新cron prompt加入模拟盘集成步骤

### 2. 观察池价格
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py report
```
- 检查：现价是否显示N/A
- 问题：N/A → entry_price=0 或 Sina API盘前返回current=0
- 修复：批量更新entry_price；pool_manager.py用prev_close降级

### 3. 预测验证
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py stats
python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py verify
```
- 检查：准确率是否合理（非0%）；verify输出是否有"无法自动验证"
- 问题：0%或"缺少匹配逻辑" → match_dimension字段不匹配
- 修复：检查amadeus_data.py输出格式，更新match_dimension的字段路径

### 4. 投研上下文
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_context.py summary
```
- 检查：板块趋势/教训/待办是否有数据
- 问题：空 → context.json未初始化或被清空
- 修复：通过cron报告自动写入

### 5. 市场数据缓存
```bash
ls -la ~/.hermes/cache/amadeus/market_*.json | tail -5
```
- 检查：是否有最近交易日的数据
- 问题：缺失 → amadeus_data.py未运行
- 修复：手动运行 `python3 ~/.hermes/scripts/amadeus/amadeus_data.py`

### 6. 涨停池截取量
```bash
grep "head(" ~/.hermes/scripts/amadeus/amadeus_data.py
```
- 检查：limit_up_stocks是否截取过少
- 问题：head(20) → 涨停股被截断，验证失败
- 修复：改为head(50)或更大

## 常见坑

| 坑 | 表现 | 根因 | 修复 |
|----|------|------|------|
| 模拟盘空库 | 0条记录 | cron只读不写 | prompt加record/daily_update |
| 盘前价格N/A | 现价显示N/A | Sina API current=0 | 用prev_close降级 |
| 预测验证0% | "无法自动验证" | 字段路径不匹配 | 更新match_dimension |
| 观察池数量不一致 | 记忆vs实际差异 | 未同步更新 | 检查后更新memory |
| 涨停股截断 | 验证"不含XX" | head(20)太少 | 改head(50) |
