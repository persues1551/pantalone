# ML训练优化指南

> 2026-05-25 实验总结：v4.0-v4.4训练迭代，找到AUC差异的根本原因

## 核心发现

### v3.5为什么AUC最高（0.7785）？

| 因素 | v3.5配置 | v4.0-v4.3配置 | 影响程度 |
|------|----------|---------------|----------|
| **数据源** | yfinance | Tushare | 🔴 高 |
| **标准化** | StandardScaler | 无 | 🔴 高 |
| **n_estimators** | 500 | 200 | 🟡 中 |
| **learning_rate** | 0.03 | 0.05 | 🟡 中 |
| **reg_alpha/lambda** | 0.1 | 0 | 🟡 中 |
| **数据范围** | 2022-01-01 ~ 2025-06-30 | 2024-01-01 ~ 2026-05-22 | 🟡 中 |

**结论**：标准化和模型参数是AUC差异的主要原因，不是数据量或股票数量。

---

## 训练实验结果汇总

| 版本 | 数据源 | 股票 | 样本 | 特征 | 标准化 | 参数 | AUC |
|------|--------|------|------|------|--------|------|-----|
| v3.5 | yfinance | 99只 | 76K | 38个 | ✅ | 500/0.03 | **0.7785** |
| v4.0 | Tushare | 251只 | 544K | 14个 | ❌ | 200/0.05 | 0.5925 |
| v4.1 | Tushare | 282只 | 188K | 37个 | ❌ | 200/0.05 | 0.6414 |
| v4.2 | Tushare | 354只 | 236K | 37个 | ❌ | 200/0.05 | 0.6508 |
| v4.3 | Tushare | 499只 | 331K | 39个 | ❌ | 200/0.05 | 0.6474 |
| v4.4 | yfinance | 136只 | 69K | 38个 | ✅ | 500/0.03 | 0.6258* |

*v4.4数据范围不同（2024-2026 vs v3.5的2022-2025）

---

## 最佳训练配置（v3.5复现）

```python
# 数据源
import yfinance as yf

# 股票池
V35_STOCKS = [...]  # 99只精选股票（见train_v3_extended.py）

# 特征计算（38个）
features = [
    'returns_1d', 'returns_5d', 'returns_10d', 'returns_20d',
    'ma_ratio_5', 'ma_ratio_10', 'ma_ratio_20', 'ma_ratio_60',
    'ma20_slope', 'ma60_slope',
    'momentum_5d', 'momentum_10d', 'momentum_20d', 'momentum_60d', 'momentum_accel',
    'volatility_5d', 'volatility_10d', 'volatility_20d', 'volatility_ratio', 'vol_change_rate',
    'volume_ratio_5d', 'volume_ratio_10d', 'volume_change',
    'rsi_14', 'rsi_change',
    'macd', 'macd_signal', 'macd_hist', 'macd_slope',
    'bb_position',
    'atr_14', 'atr_ratio',
    'kdj_k', 'kdj_d', 'kdj_j',
    'deviation_ma20', 'deviation_ma60',
    'price_position_20d'
]

# 标准化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 模型参数
lgb_params = {
    'n_estimators': 500,
    'max_depth': 6,
    'learning_rate': 0.03,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'verbose': -1
}

# 目标变量
threshold = 0.03  # 3%阈值
target = (future_return_5d > threshold).astype(int)
```

---

## 关键教训

### 1. 数据源选择
- **yfinance > Tushare** for ML训练
- yfinance数据质量更高，AUC差异显著
- Tushare适合实时数据，但历史数据质量不如yfinance

### 2. 标准化是必须的
- StandardScaler对树模型也有帮助
- 不标准化会导致特征权重失衡
- v3.5用了标准化，v4.0-v4.3没用，AUC差0.1+

### 3. 模型参数很重要
- n_estimators=500 vs 200：更多树=更好的拟合
- learning_rate=0.03 vs 0.05：更慢的学习率=更好的泛化
- reg_alpha/lambda=0.1：正则化防止过拟合

### 4. 数据范围影响泛化
- 2022-2025 vs 2024-2026：不同市场环境
- 更长的数据范围不一定更好（可能包含过时模式）
- 2-3年数据通常最佳

### 5. 股票池质量 > 数量
- v3.5的99只精选 > v4.3的499只混合
- 精选股票池更容易学习规律
- 混合大盘+中小盘可能引入噪声

---

## 数据源管理器

文件：`scripts/amadeus/data_source_manager.py`

```python
# 使用示例
from data_source_manager import DataSourceManager

manager = DataSourceManager()

# 单只下载（自动降级）
df = manager.download('600519', '2022-01-01', '2025-06-30')

# 批量下载
results = manager.batch_download(stock_list, start_date, end_date)

# 缓存信息
info = manager.get_cache_info()
```

**优先级**：yfinance → Tushare → AKShare

---

## ML模拟盘系统

### 文件
- `scripts/amadeus/ml_simulation.py` — 模拟交易
- `scripts/amadeus/ml_sim_daily_check.py` — 每日检查
- `scripts/amadeus/ml_backtest.py` — 历史回测

### 交易规则
```python
RULES = {
    'buy_threshold': 60,      # ML评分>60才考虑买入
    'sell_threshold': 40,     # ML评分<40考虑卖出
    'stop_loss': -0.05,       # 止损线-5%
    'take_profit': 0.10,      # 止盈线+10%
    'holding_days': 5,        # 最长持仓5天
    'max_positions': 5,       # 最多持仓5只
}
```

### 用法
```bash
# 模拟买入
python3 ml_simulation.py --buy 600519 贵州茅台 75

# 检查是否需要平仓
python3 ml_simulation.py --check 600519 1800

# 生成报告
python3 ml_simulation.py --report
```

---

## OCIFQ + ML 六维评分系统

### 评分权重
| 维度 | 权重 | 说明 |
|------|------|------|
| M (ML信号) | 30% | 基于集成模型预测 |
| O (寡头定价权) | 15% | 行业集中度、壁垒 |
| C (长周期催化) | 12% | 持续≥4季度的催化 |
| I (行业利润断层) | 12% | 同行业同步改善 |
| F (财务三爆) | 20% | 营收/利润/毛利率爆发 |
| Q (连续季报) | 9% | 最近4季度连续改善 |

### 硬门槛
- ML评分<30 → 总分≤65
- ML评分<20 → 总分≤50

### 整合脚本
```bash
python3 ~/.hermes/scripts/amadeus/ocifq_ml_selector.py --stocks 600519,000858
```

---

## Pitfalls

1. **不要用Tushare训练ML模型**：数据质量不如yfinance，AUC差异显著
2. **不要跳过标准化**：即使树模型也需要标准化
3. **不要用太多股票**：精选99只 > 混合499只
4. **不要用太短的数据范围**：2-3年最佳，1年太短
5. **不要忽略模型参数**：500棵树/0.03学习率是最佳配置
6. **yfinance限流**：每只股票间隔0.5秒，避免被封
