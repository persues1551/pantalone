# 模拟盘集成指南

## 背景
模拟盘引擎 (`amadeus_simulator.py`) 自 2026-05 创建以来从未被 cron 报告实际调用。
规则写了"必须包含模拟盘"，但 prompt 缺少具体的 API 调用指令，导致数据库始终为空。

## 架构

```
amadeus_simulator.py    → 模拟盘引擎（开仓/平仓/查询）
simulator.db            → SQLite 数据库（positions/trades/daily_pnl 三表）
amadeus_context.py      → 投研上下文（独立于模拟盘）
```

### 数据库表结构

**positions** - 持仓表
- code, name, pool, buy_date, buy_price, shares
- stop_loss, take_profit, status (holding/closed)
- close_date, close_price, pnl, pnl_pct, notes

**trades** - 交易流水
- code, action (buy/sell), price, shares, amount, date, reason

**daily_pnl** - 日盈亏
- date (PK), total_value, cash, positions_value, pnl_day, pnl_total, drawdown

## Cron 集成步骤

### 1. 盘前早报 (08:30)
```
## 模拟盘
1. 运行 `python3 ~/.hermes/scripts/amadeus/amadeus_simulator.py status`
2. 查看当前持仓，检查是否触及止损/止盈
3. 根据盘前分析制定今日交易计划（标的/触发价/金额/理由）
4. 输出模拟账户状态 + 今日计划
```

### 2. 午间复盘 (12:00)
```
## 模拟盘
1. 运行 `python3 ~/.hermes/scripts/amadeus/amadeus_simulator.py status`
2. 对照盘前计划，检查是否触发买入/卖出条件
3. 如有触发，调用 Python 接口记录：
   python3 -c "
   import sys; sys.path.insert(0, '/home/ubuntu/.hermes/scripts/amadeus')
   from amadeus_simulator import init_db, open_position, close_position
   conn = init_db()
   # open_position(conn, '600900', '长江电力', 'A', 28.5, 1000)
   # close_position(conn, 1, 29.0, '触及止盈')
   "
4. 输出模拟账户台账
```

### 3. 收盘复盘 (15:30)
```
## 模拟盘
1. 运行 `python3 ~/.hermes/scripts/amadeus/amadeus_simulator.py status`
2. 记录今日所有交易（如有未记录的）
3. 输出完整台账：期初/买入/佣金/持仓/现金/总资产/盈亏/收益率/风险暴露
```

## 关键教训
- **规则 ≠ 执行**：SKILL.md 写了规则，但 cron prompt 必须有具体的 shell 命令
- **数据必须从 DB 读取**：禁止编造持仓/交易数据
- **初始资金**：200,000 元
- **仓位限制**：单票 1-2.5 万，总风险暴露 ≤ 60%
