# ML训练工作流详细文档

## 数据源优先级

| 优先级 | 数据源 | 稳定性 | 限流情况 | 适用场景 |
|--------|--------|--------|----------|----------|
| 1 | **Tushare Pro** | ✅ 稳定 | 0.35秒/次 | 历史日线、股票列表 |
| 2 | AKShare | ⚠️ 不稳定 | 严重限流 | 备用、实时行情 |
| 3 | 腾讯API | ✅ 稳定 | 无限流 | 实时行情 |

**关键**：AKShare的`stock_zh_a_spot_em()`经常限流（RemoteDisconnected），获取股票列表优先用Tushare的`stock_basic`。

## 本地缓存策略

```
~/.hermes/cache/amadeus/
├── hs300_data/
│   ├── hs300_stocks.json          # 股票列表缓存（不过期）
│   └── {code}_{start}_{end}.parquet  # 个股数据缓存
├── stock_data/
│   ├── stock_list.json            # 通用股票列表
│   └── historical/                # 历史数据缓存
└── ml_models/
    ├── lightgbm_v*.pkl
    ├── xgboost_v*.pkl
    └── ensemble_v*_config.json
```

**规则**：
1. 股票列表缓存后永不过期（手动更新）
2. 个股数据缓存1天有效
3. 首次下载后后续训练秒级加载

## 特征工程（v3.5验证有效的44个特征）

### 必须包含的特征类别

1. **价格变化**（5个）
   - pct_change, pct_change_2d, pct_change_5d, pct_change_10d, pct_change_20d

2. **均线相关**（8个）
   - ma5/10/20/60_slope
   - price_vs_ma5/10/20/60

3. **动量**（5个）
   - momentum_5d/10d/20d/60d
   - momentum_accel（动量加速度）

4. **RSI**（2个）
   - rsi_14, rsi_change

5. **MACD**（2个）
   - macd_hist, macd_slope

6. **布林带**（2个）
   - bb_position, bb_width

7. **波动率**（5个）
   - volatility_5/10/20, volatility_ratio, vol_change_rate

8. **成交量**（3个）
   - volume_ratio, volume_ratio_20, volume_change

9. **ATR**（1个）
   - atr_ratio

10. **KDJ**（3个）
    - kdj_k, kdj_d, kdj_j

11. **价格位置**（1个）
    - price_position_20d

**⚠️ 教训**：v4.0用14个特征AUC只有0.59，v3.5用44个特征AUC达0.78。特征数量很重要！

## 目标变量定义

```python
# 正确（v3.5验证）
df['target'] = (df['future_return_5d'] > 0.03).astype(int)  # 3%阈值

# 错误（v4.0教训）
df['target'] = (df['future_return_5d'] > 0.02).astype(int)  # 2%阈值，AUC下降
```

**⚠️ 教训**：2%阈值导致正样本比例过高（~30%），模型区分能力下降。3%阈值更优。

## 数据清洗（必须步骤）

```python
# 关键：替换inf为NaN
combined[feature_cols] = combined[feature_cols].replace([np.inf, -np.inf], np.nan)
combined = combined.dropna(subset=feature_cols + ['target'])
```

**⚠️ 教训**：XGBoost对inf值敏感，会报错`Input data contains inf`。

## 训练参数（v3.5验证）

```python
# LightGBM
lgb.LGBMClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_samples=100,
    random_state=42,
    verbose=-1
)

# XGBoost
xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_samples=100,
    random_state=42,
    eval_metric='auc',
    verbosity=0
)
```

## 训练量实验结论

| 实验 | 股票 | 时间 | 特征 | 阈值 | AUC | 结论 |
|------|------|------|------|------|-----|------|
| v3.5 | 99只 | 2年 | 44个 | 3% | **0.7785** | 基准 |
| v4.0 | 251只 | 10年 | 14个 | 2% | 0.5925 | 特征太少+阈值错误 |
| v4.1 | 200只 | 3年 | 37个 | 3% | 训练中 | 接近v3.5配置 |

**关键发现**：
1. **特征数量 > 数据量**：44个特征比14个特征AUC高0.18
2. **阈值很重要**：3%比2%阈值AUC更高
3. **时间范围**：3-5年最优，10年太长（旧数据噪声）
4. **股票池**：沪深300大盘股波动小，预测难度大

## 训练脚本清单

| 脚本 | 用途 | 状态 |
|------|------|------|
| `train_v3_extended.py` | v3.5训练（99只股票） | ✅ 生产 |
| `train_v41_hs300.py` | v4.1训练（沪深300） | 🔄 实验 |
| `ml_predict.py` | 实时预测 | ✅ 生产 |
| `ml_daily_predict.py` | 每日报告 | ✅ 生产 |
| `ml_data_manager.py` | 数据管理 | ✅ 工具 |

## 预测脚本用法

```bash
# 单只股票
python3 ~/.hermes/scripts/amadeus/ml_predict.py --stock 600519

# 多只股票
python3 ~/.hermes/scripts/amadeus/ml_predict.py --stocks 600519,000858 --report

# 观察池
python3 ~/.hermes/scripts/amadeus/ml_predict.py --pool
```
