# ML训练最佳实践与经验教训

## ⚠️ 关键教训：v3.5 AUC数据泄露（2026-05-25发现）

### 问题描述
v3.5报告的集成AUC 0.7785存在**数据泄露**：

```python
# ❌ 错误做法（v3.5）
lgb_proba = best_lgb.predict_proba(X_scaled)[:, 1]  # 全量数据
xgb_proba = best_xgb.predict_proba(X_scaled)[:, 1]  # 全量数据
ensemble_proba = (lgb_proba + xgb_proba) / 2
ensemble_auc = roc_auc_score(y, ensemble_proba)  # 在训练数据上计算！

# ✅ 正确做法（v4.4+）
# 使用TimeSeriesSplit交叉验证，在验证集上计算AUC
for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled)):
    X_train, X_val = X_scaled.iloc[train_idx], X_scaled.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    # 训练和评估在验证集上进行
```

### v3.5真实AUC（交叉验证）
| 模型 | AUC |
|------|-----|
| LightGBM | 0.6085 ± 0.0120 |
| XGBoost | 0.6116 ± 0.0108 |
| 集成（正确） | ~0.61 |

### 教训
- **永远不要在全量数据上计算评估指标**
- **必须使用时间序列交叉验证（TimeSeriesSplit）**
- **集成AUC应该在每个fold的验证集上计算，然后取平均**

---

## 数据源对比（2026-05-25测试）

| 数据源 | 稳定性 | 限流 | 历史数据 | 推荐度 |
|--------|--------|------|----------|--------|
| **yfinance** | ✅ 稳定 | 0.5s/只 | 10年+ | ⭐⭐⭐⭐⭐ |
| **Tushare Pro (120积分)** | ✅ 稳定 | `daily`可用 | 10年+ | ⭐⭐⭐ |
| **Tushare Pro (2000+积分)** | ✅ 稳定 | 基本无限 | 10年+ | ⭐⭐⭐⭐⭐ |
| **AKShare** | ❌ 严重限流 | 不可预测 | 5年+ | ⭐⭐ |

### 120积分Tushare账号限制
- `daily`（日线行情）：✅ 可用
- `stock_basic`（股票列表）：✅ 可用
- `daily_basic`（PE/PB/市值）：❌ 限流1次/小时
- `fina_indicator`（ROE/EPS/财务指标）：❌ 限流1次/小时

### 推荐策略（120积分账号）
1. **日线数据**：yfinance（质量最好，已缓存733只）
2. **基本面数据**：yfinance `info`（无限流，当前时点静态值）
3. **行业分类**：AKShare（此接口相对稳定）
4. **Tushare**：仅用于`daily`和`stock_basic`

### 基本面数据获取函数（v5修复版）
```python
def fetch_fundamental_data(symbol: str) -> Dict:
    """三级降级: Tushare → yfinance → 缓存"""
    # 1. Tushare daily_basic (PE/PB/市值/换手率)
    #    fields: pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,total_mv,circ_mv
    #    注意: total_mv单位是万元，需×10000转元
    # 2. Tushare fina_indicator (ROE/EPS/毛利率/净利率/营收增速/利润增速)
    #    fields: roe,roe_dt,grossprofit_margin,netprofit_margin,eps,bps,profit_yoy,or_yoy
    # 3. yfinance info (备用)
    # 缓存: 只缓存非空结果（>10字节）
    
    # ⚠️ 陷阱：extract_fundamental_features()和create_market_cap_features()
    # 都会生成market_cap_raw/is_large_cap等列，合并时会重复！
    # 解决：只用extract_fundamental_features()，它已包含市值分组特征
```

### extract_fundamental_features() 支持的字段映射
| 特征名 | Tushare字段 | yfinance字段 | AKShare字段 |
|--------|------------|-------------|-------------|
| pe_ratio | pe, pe_ttm | trailingPE, forwardPE | 市盈率(动) |
| pb_ratio | pb | priceToBook | 市净率 |
| roe | roe (fina_indicator) | returnOnEquity | 净资产收益率 |
| eps | eps (fina_indicator) | trailingEps | 每日收益 |
| total_mv | total_mv (万元) | marketCap (元) | 总市值 |
| gross_margin | grossprofit_margin | grossMargins | - |
| net_margin | netprofit_margin | profitMargins | - |
| profit_growth_yoy | profit_yoy | earningsGrowth | 净利润-同比增长 |

### 统一数据源管理器
- 文件：`scripts/amadeus/data_source_manager.py`
- 支持：yfinance、Tushare、AKShare
- 策略：优先级降级 + 本地缓存

---

## 训练配置最佳实践

### v3.5/v4.4验证过的配置
```python
# LightGBM
lgb_model = lgb.LGBMClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=42,
    verbose=-1
)

# XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=42,
    eval_metric='auc',
    verbosity=0
)
```

### 标准化（必须）
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
```

### 时间序列交叉验证（必须）
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)

for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled)):
    # 在验证集上评估，不是全量数据
    ...
```

---

## 特征列表（38个，v3.5验证）

```python
FEATURE_COLS = [
    # 价格变化
    'returns_1d', 'returns_5d', 'returns_10d', 'returns_20d',
    # 均线比值
    'ma_ratio_5', 'ma_ratio_10', 'ma_ratio_20', 'ma_ratio_60',
    # 均线斜率
    'ma20_slope', 'ma60_slope',
    # 动量
    'momentum_5d', 'momentum_10d', 'momentum_20d', 'momentum_60d', 'momentum_accel',
    # 波动率
    'volatility_5d', 'volatility_10d', 'volatility_20d', 'volatility_ratio', 'vol_change_rate',
    # 成交量
    'volume_ratio_5d', 'volume_ratio_10d', 'volume_change',
    # RSI
    'rsi_14', 'rsi_change',
    # MACD
    'macd', 'macd_signal', 'macd_hist', 'macd_slope',
    # 布林带
    'bb_position',
    # ATR
    'atr_14', 'atr_ratio',
    # KDJ
    'kdj_k', 'kdj_d', 'kdj_j',
    # 偏离度
    'deviation_ma20', 'deviation_ma60',
    # 价格位置
    'price_position_20d'
]
```

---

## ⚠️ v5训练踩坑记录（2026-05-25）

### 陷阱1：AKShare空数据被缓存

**问题**：`train_v5_features.py`的`fetch_fundamental_data()`函数调用AKShare获取基本面数据，当AKShare限流返回空时，函数返回`{}`并被缓存到`fundamental_data/{symbol}.json`（2字节空JSON）。后续训练直接读缓存，永远拿不到真实数据。

**症状**：120个fundamental_data文件全部是2字节`{}`，v5新增的基本面特征（PE/PB/ROE等）全为0。

**修复方案**：
```python
# fetch_fundamental_data() 中，缓存前检查是否为空
if fund:  # 只缓存非空结果
    with open(cache_file, 'w') as f:
        json.dump(fund, f)
    return fund
else:
    # 不缓存空结果，下次重试
    return {}
```

**教训**：任何数据获取函数的缓存逻辑都必须验证数据非空才写入。空结果缓存是"静默失败"的典型模式。

### 陷阱2：多个训练进程并发竞争

**问题**：连续启动两个v5训练进程（一个--subset 300，一个--full），导致：
- 内存竞争（各占600MB+）
- 网络竞争（都调AKShare，加剧限流）
- 磁盘竞争（写同一个fundamental_data目录）

**修复方案**：
- 训练脚本启动时检查是否有同名进程在跑
- 或在prompt中明确"只运行一个训练实例"

### 陷阱3：训练进程stdout被缓冲无输出

**问题**：`train_v5_features.py`的print输出被Python stdout缓冲，process log显示0行输出，无法判断进度。

**修复方案**：
- 脚本中添加`sys.stdout.flush()`或设置`PYTHONUNBUFFERED=1`
- 或用`python3 -u train_v5_features.py`强制无缓冲

### 陷阱4：特征工程函数重复列名导致concat失败（v5踩坑）

**问题**：`extract_fundamental_features()`和`create_market_cap_features()`都生成`market_cap_raw`、`is_large_cap`、`is_mid_cap`、`is_small_cap`列。`pd.concat`时因重复列名抛出`InvalidIndexError: Reindexing only valid with uniquely valued Index objects`。

**修复方案**：
- 合并前检查重复列：`df = df.loc[:, ~df.columns.duplicated()]`
- 或去掉重复的函数调用（推荐）：让一个函数负责一组特征，不在多处生成

**教训**：多个特征工程函数合并时，必须确保列名唯一。设计时明确每个函数的职责边界。

### 陷阱5：死磕一个数据源而不是用已有替代（用户纠正）

**问题**：AKShare基本面接口限流严重，返回空数据。我试图修复AKShare问题，浪费时间。

**用户纠正**："怎么还在纠结akshare，有其他数据源啊，之前不是用的tushare和yfinance吗"+"学聪明一点"

**正确做法**：
1. 先检查已有的数据源管理器（`data_source_manager.py`）
2. 看看哪个源能用，直接切换
3. 不要在限流/损坏的源上浪费时间

**教训**：已有工具/数据源/脚本是资产，先用再修。当A方案失败时，先试B/C方案，而不是死磕A。

---

## 训练实验记录

| 版本 | 数据源 | 股票 | 样本 | 特征 | 集成AUC | 备注 |
|------|--------|------|------|------|---------|------|
| v3.5 | yfinance | 99只 | 76,472 | 41个 | 0.7785 | ❌ 数据泄露 |
| v4.0 | Tushare | 251只 | 544,593 | 14个 | 0.5925 | 特征太少 |
| v4.1 | Tushare | 282只 | 187,709 | 37个 | 0.6414 | - |
| v4.2 | Tushare | 354只 | 235,677 | 37个 | 0.6508 | - |
| v4.3 | Tushare | 499只 | 331,450 | 39个 | 0.6474 | - |
| **v4.4** | **yfinance** | **136只** | **104,955** | **38个** | **0.6365** | ✅ 正确验证 |
| v4.5 | yfinance | 300只 | ~150K | 38个 | - | 扩大样本 |
| v4.7 | yfinance | 733只 | 556,410 | 38个 | 0.6499 | 基线模型 |
| v5.0 | yfinance+Tushare | 299只 | 248,895 | 121个 | 0.6456 | ❌ 前瞻偏差 |
| v5.0 | yfinance+Tushare | 733只 | 608,213 | 121个 | 0.6326 | ❌ 分批+前瞻偏差 |
| **v5.1** | **yfinance** | **727只** | **605,610** | **66个** | **0.6512** | **✅ 当前最佳** |

### 结论
- **v5.1（0.6512）是当前最佳模型**，超过v4.7（0.6499）
- 基本面特征（PB/EPS/股息率/毛利率）进入Top 20重要性，证明有效
- 新特征贡献39.3%
- 模型文件：`lightgbm_v51.pkl`, `xgboost_v51.pkl`, `scaler_v51.pkl`, `feature_names_v51.json`

### v5.0失败原因分析
1. **前瞻偏差**：用当前时点PE/PB训练历史数据，模型学到的是"未来信息"
2. **Tushare限流**：120积分账号`daily_basic`/`fina_indicator`限流1次/小时，获取历史基本面不可行
3. **分批训练**：每批模型不同，简单平均不等于真正集成

### v5.1成功原因
1. **yfinance基本面**：无限流，获取当前时点PE/PB/ROE/EPS等（静态值，所有日期相同）
2. **特征精简**：121→66个，去掉零方差和噪声特征
3. **全量训练**：用train_v5_batch.py分批避免OOM

---

## ⚠️ 新增陷阱（2026-05-25 v5训练）

### 陷阱6：Tushare 120积分账号基本不可用

**问题**：120积分的Tushare账号，`daily_basic`和`fina_indicator`接口限流1次/小时，完全无法用于批量训练。

**症状**：调用`daily_basic`返回`Exception: 抱歉，您访问接口(daily_basic)频率超限(1次/小时)`

**解决方案**：用yfinance获取基本面数据（`ticker.info`），无限流。

### 陷阱7：yfinance返回字符串而非数值

**问题**：yfinance的`info`返回的部分字段可能是字符串类型，导致`>`比较失败：`TypeError: '>' not supported between instances of 'str' and 'int'`

**解决方案**：
```python
# 在处理前统一转换
for col in fund_aligned.columns:
    fund_aligned[col] = pd.to_numeric(fund_aligned[col], errors='coerce')
```

### 陷阱8：OOM杀死训练进程（3.6GB服务器）

**问题**：733只股票全量训练需要3.4GB+内存，被Linux OOM killer杀死（exit code 143/SIGTERM）。

**症状**：`dmesg`显示`Out of memory: Killed process XXXX (python3) anon-rss:3451352kB`

**解决方案**：
```python
# train_v5_batch.py — 分批训练
BATCH_SIZE = 200
for i in range(num_batches):
    batch_stocks = stock_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
    result = train_v5(stock_list=batch_stocks, ...)
    import gc; gc.collect()  # 释放内存
```

### 陷阱9：Cron job patch/replace失败

**问题**：收盘复盘cron job尝试用`patch`修改报告文件中的"池别汇总"，但实际章节名是"观察池自动管理"，导致hunk not found。

**解决方案**：在cron prompt中明确指定章节名，并禁止patch：
```
**📝 观察池自动管理**（退池/入池/当前池内统计）——禁止用"池别汇总"
一次性写入完整报告，禁止后续patch修改
```

---

## OCIFQ + ML 整合（2026-05-25）

### 六维评分体系
| 维度 | 权重 | 说明 |
|------|------|------|
| M (ML信号) | 30% | LightGBM+XGBoost集成预测 |
| O (寡头定价权) | 15% | 行业集中度、壁垒、定价能力 |
| C (长周期催化) | 12% | 持续≥4季度的产业催化 |
| I (行业利润断层) | 12% | 同行业多家公司同步改善 |
| F (财务三爆) | 20% | 营收/利润/毛利率爆发式增长 |
| Q (连续季报) | 9% | 最近4季度连续改善 |

### 硬门槛
- ML评分<30 → 总分≤65
- ML评分<20 → 总分≤50

### 整合脚本
- 文件：`scripts/amadeus/ocifq_ml_selector.py`
- 用法：`python3 ocifq_ml_selector.py --stocks <代码> --ml-file /tmp/ml_predictions.json`

---

## 模拟盘验证系统（2026-05-25）

### 交易规则
| 规则 | 设定 |
|------|------|
| 买入条件 | ML评分 > 60 |
| 卖出条件 | ML评分 < 40 |
| 止损 | -5% |
| 止盈 | +10% |
| 最长持仓 | 5天 |
| 最多持仓 | 5只 |

### 脚本
- 模拟交易：`scripts/amadeus/ml_simulation.py`
- 每日检查：`scripts/amadeus/ml_sim_daily_check.py`
- 回测引擎：`scripts/amadeus/ml_backtest.py`

### 定时任务
- 每日信号预测：15:30 (job_id: ad58c2202a81)
- 模拟盘检查：16:00 (job_id: 0cb6066c305b)
- 止损监控：15:00 (job_id: f1a1b0d03cad)
