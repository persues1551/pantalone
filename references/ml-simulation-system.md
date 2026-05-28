# ML模拟盘验证系统

## 系统架构

| 脚本 | 功能 | 用法 |
|------|------|------|
| `ml_simulation.py` | 模拟交易 | `--buy/--sell/--check/--report/--trades` |
| `ml_sim_daily_check.py` | 每日检查 | 自动生成状态报告 |
| `ml_backtest.py` | 历史回测 | `--stocks <代码> --start 2024-01-01` |
| `ocifq_ml_selector.py` | 六维评分 | `--stocks <代码> --ml-file <文件>` |

## 交易规则

| 规则 | 设定 |
|------|------|
| 买入条件 | ML评分 > 60 |
| 卖出条件 | ML评分 < 40 |
| 止损 | -5% |
| 止盈 | +10% |
| 最长持仓 | 5天 |
| 最多持仓 | 5只 |
| 单笔金额 | 10万 |

## 定时任务

| 任务 | 时间 | Job ID |
|------|------|--------|
| ML每日信号预测 | 15:30 | ad58c2202a81 |
| ML模拟盘检查 | 16:00 | 0cb6066c305b |
| 止损自动监控 | 15:00 | f1a1b0d03cad |

## 使用方法

### 模拟交易

```bash
# 模拟买入
python3 ~/.hermes/scripts/amadeus/ml_simulation.py --buy 600519 贵州茅台 75

# 检查是否需要平仓
python3 ~/.hermes/scripts/amadeus/ml_simulation.py --check 600519 1800

# 模拟卖出
python3 ~/.hermes/scripts/amadeus/ml_simulation.py --sell 600519 1800

# 查看绩效报告
python3 ~/.hermes/scripts/amadeus/ml_simulation.py --report

# 查看交易记录
python3 ~/.hermes/scripts/amadeus/ml_simulation.py --trades
```

### 历史回测

```bash
# 回测2024年至今（2年+数据）
python3 ~/.hermes/scripts/amadeus/ml_backtest.py --stocks 600519,000858,300750 --start 2024-01-01

# 输出：总收益率、年化收益、夏普比率、最大回撤、胜率、盈亏比
```

### 每日检查

```bash
# 运行每日检查
python3 ~/.hermes/scripts/amadeus/ml_sim_daily_check.py
```

## 数据存储

- 交易记录：`~/.hermes/cache/amadeus/ml_simulation/trades.json`
- 每日报告：`~/.hermes/cache/amadeus/ml_simulation/daily_report.json`
- 回测结果：`~/.hermes/cache/amadeus/ml_backtest/`

## 回测价值

- 验证ML信号在不同市场环境下的表现
- 发现模型在牛市/熊市/震荡市的有效性差异
- 优化交易规则（止损、止盈、持仓天数）
- 增强训练效果（用回测结果反馈给模型）

## 每日工作流

```
15:00  止损监控 → 检查持仓是否触及止损
15:30  ML信号 → 生成今日评分
16:00  模拟盘 → 检查持仓状态，生成报告

每周：
- 回测验证 → 用历史数据验证模型
- 复盘分析 → 统计胜率、盈亏比
- 规则优化 → 根据结果调整参数
```

## ML模型本质说明

**LightGBM + XGBoost = 梯度提升树**

```
输入：44个特征（RSI、MACD、均线、PE、ROE...）
    ↓
两棵"决策树森林"（LightGBM + XGBoost）
    ↓
简单平均集成
    ↓
输出：0-100评分（越高越看好）
```

**AUC 0.7785含义**：
- 0.5 = 随机猜（没用）
- 0.7 = 一般
- 0.7785 = 还行，但有22%会判断错
- 1.0 = 完美（不存在）

**正确理解**：ML信号是"参考"（30%权重），不是"指令"。OCIFQ基本面分析才是"灵魂"（70%权重）。
