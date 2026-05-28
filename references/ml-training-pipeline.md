# ML训练流水线文档

## 训练版本历史

| 版本 | 股票数 | 样本数 | 特征数 | 数据范围 | 集成AUC | 结论 |
|------|--------|--------|--------|----------|---------|------|
| v3.5 | 99只 | 76,472 | 44 | 2年 | 0.7785 | ❌ 数据泄露 |
| v4.7 | 733只 | 556,410 | 38 | 3年 | 0.6499 | 基线模型 |
| v5.0 | 299只 | 248,895 | 121 | 3年 | 0.6456 | ❌ 基本面有前瞻偏差 |
| **v5.1** | **727只** | **605,610** | **66** | **3年** | **0.6512** | **当前最佳** |
| v5.2 | 训练中 | — | 50(SHAP) | 3年 | — | 三模型集成+SHAP+Optuna |

## 数据源限制（120积分Tushare账号）

### Tushare接口限流情况
| 接口 | 限流 | 可用性 |
|------|------|--------|
| daily | 无明显限流 | ✅ |
| stock_basic | 无明显限流 | ✅ |
| daily_basic | **1次/小时** | ❌ 基本不可用 |
| fina_indicator | **1次/小时** | ❌ 基本不可用 |

### 推荐数据源策略（优先级）
1. **日线数据**：yfinance（主，已缓存733只）
2. **基本面数据**：yfinance `info`（无限流，当前时点PE/PB/ROE/EPS/毛利率/净利率/市值）
3. **行业分类**：AKShare（相对稳定）
4. **Tushare**：仅用于`daily`和`stock_basic`

### ⚠️ 常见错误
- **不要死磕AKShare**：主人已多次指出已有Tushare和yfinance，不应卡在AKShare限流上
- **不要只用一个数据源**：必须有降级策略（yfinance → Tushare → AKShare）

## v5.1特征体系（66个）

### v4技术特征（37个）
均线(4)、均线斜率(4)、RSI+变化(2)、MACD(3)、布林带(4)、ATR(2)、成交量比(2)、动量(4)、波动率(2)、振幅(1)、均线位置(4)、高低比(1)、线性回归斜率(3)、RSI背离(1)

### v5高阶技术特征（10个）
波动率族(vol_of_vol, volatility_ratio)、ADX+DI(3)、OBV变化(2)、MFI(1)、VPT变化(1)、相对强度(1)

### 基本面特征（19个，静态值）
估值(pe_ratio, pe_inverse, pe_quantile, pb_ratio, pb_quantile, dv_ratio)、市值(log_market_cap, market_cap_raw, is_large_cap, is_mid_cap, is_small_cap)、盈利(roe, roe_pb, eps)、成长性(revenue_growth_yoy, profit_growth_yoy, peg_approx)、利润率(gross_margin, net_margin)

## OOM解决方案：分批训练

**问题**：733只股票全量训练需要3.4GB+内存，3.6GB服务器被OOM killer杀死。

**方案**：分批训练脚本，每批200只，完成后`gc.collect()`释放内存。

```bash
python3 train_v5_batch.py  # 自动分4批训练+合并结果
```

**关键**：必须在每批结束后调用`gc.collect()`，否则内存不会释放。

## ⚠️ 数据类型错误修复

**错误**：`TypeError: '>' not supported between instances of 'str' and 'int'`

**原因**：yfinance返回的基本面数据可能包含字符串类型，或DataFrame列类型不一致。

**修复**：
```python
# 在特征提取前，强制转换所有列为数值
for col in fund_aligned.columns:
    fund_aligned[col] = pd.to_numeric(fund_aligned[col], errors='coerce')

# 比较前显式转换
pe = fund_aligned['pe_ratio'].astype(float)
valid = (pe > 0) & (pe < 1000)
```

## ⚠️ 重复列名导致concat失败

**错误**：`InvalidIndexError: Reindexing only valid with uniquely valued Index objects`

**原因**：`extract_fundamental_features`和`create_market_cap_features`创建了相同的列（market_cap_raw, is_large_cap等）。

**修复**：合并前检查重复列，或去掉功能重复的函数。

## v5.2新特性（开发中）

### 三模型集成
- LightGBM + XGBoost + CatBoost
- 权重：LGB 0.4 + XGB 0.3 + CB 0.3
- CatBoost对类别特征（行业）天然友好

### SHAP特征筛选
- 从71个特征筛选到50个最重要的
- 用`shap.TreeExplainer`计算特征重要性
- 选择top_n特征训练

### Optuna超参数优化
- 贝叶斯优化，20 trials
- 优化参数：n_estimators, max_depth, learning_rate, subsample, colsample_bytree, reg_alpha, reg_lambda, min_child_samples

### 多标签训练
- 3天涨2%、5天涨3%、10天涨5%
- 综合标签：任意窗口达标即为正样本
- 当前用5天涨3%作为主标签

### 宏观特征
- 上证指数动量（5天/10天）
- 上证指数波动率（10天）
- 沪深300动量（5天）
- 创业板动量（5天）

## 生产模型更新流程

更新`ml_predict.py`时需同步更新：
1. `_load_models()` — 加载新版本模型文件
2. `calculate_features()` — 匹配训练时的特征体系
3. `fetch_fundamentals()` — 获取基本面数据（如果需要）
4. `predict()` — 传递symbol参数给calculate_features

**验证命令**：
```bash
python3 -c "from ml_predict import MLPredictor; p = MLPredictor(); print(p.predict('600519'))"
```

## 训练脚本

| 脚本 | 用途 | 版本 |
|------|------|------|
| `train_v51.py` | v5.1训练（yfinance基本面） | v5.1生产 |
| `train_v5_batch.py` | v5.1分批训练（避免OOM） | v5.1 |
| `train_v52.py` | v5.2训练（三模型+SHAP+Optuna） | v5.2开发 |
| `train_v52_batch.py` | v5.2分批训练 | v5.2开发 |
| `ml_predict.py` | 实时预测 | v5.1 |
| `ml_daily_predict.py` | 每日信号报告 | v5.1 |

## 模拟盘系统

| 脚本 | 功能 | 定时任务 |
|------|------|---------|
| `ml_simulation.py` | 模拟交易 | — |
| `ml_sim_daily_check.py` | 每日检查 | 16:00 |
| `ml_backtest.py` | 历史回测 | — |
| `stop_loss_monitor.py` | 止损监控 | 15:00 |

## 交易规则

买入ML>60，卖出ML<40，止损-5%，止盈+10%，最长5天，最多5只，单笔10万。
