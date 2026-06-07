# Quant ML Integration Guide (from pantalone-quant-integration)

Detailed module usage, ML training pipeline, and integration patterns for the Pantalone quant system.

## Module Code Examples

### 1. Qlib Backtest (`qlib_backtest.py`)
```python
from qlib_backtest import PantaloneBacktest
bt = PantaloneBacktest()
results = bt.run_backtest(prices_df, signals_df, initial_capital=200000)
factor_analysis = bt.analyze_factor("momentum", factor_values, forward_returns)
```
Key metrics: IC, ICIR, 分组收益, 多空收益

### 2. ML Signal (`ml_signal.py`)
```python
from ml_signal import MLSignalGenerator
ml = MLSignalGenerator()
results = ml.train(df, model_type='lightgbm', forward_days=5, threshold=0.03)
signal = ml.predict(df, model_type='lightgbm')
score = ml.generate_ml_score(df)  # 0-100, 用于OCIFQ第六维度
```

### 3. OpenBB Data Layer (`openbb_integration.py`)
```python
from openbb_integration import OpenBBIntegration
obb = OpenBBIntegration()
price = obb.get_stock_price("AAPL", provider="yfinance")
fundamentals = obb.get_fundamentals("AAPL")
macro = obb.get_macro_data("GDP", provider="fred")
```
Providers: yfinance, fmp, alpha_vantage, tiingo, fred, intrinio, cboe, tradier

### 4. FinRL Strategy (`finrl_integration.py`)
```python
from finrl_integration import FinRLIntegration
finrl = FinRLIntegration()
results = finrl.train_agent(df, algo='ppo', total_timesteps=100000)
signal = finrl.predict_action(df, algo='ppo')
```
Algorithms: PPO, A2C, DDPG, TD3, SAC

### 5. Factor Miner (`factor_miner.py`)
```python
from factor_miner import FactorMiner
miner = FactorMiner()
factors = miner.generate_factors(df, theme='momentum')
validation = miner.validate_factor(factor, forward_returns, min_ic=0.03)
results = miner.iterate_factors(df, forward_returns, rounds=5, top_k=5)
```
Themes: momentum, mean_reversion, volatility, volume, technical

### 6. Comprehensive Signal (`pantalone_tools_hub.py`)
```python
from pantalone_tools_hub import PantaloneToolsHub
hub = PantaloneToolsHub()
signal = hub.generate_comprehensive_signal(df, "600519")
# Returns: ml_score, rl_signal, factor_signals, composite_score, recommendation
```

## ML Training Pipeline Details

### Data Source Priority
```
yfinance > Tushare > AKShare
```
- yfinance: free, parquet local cache, `.info` for fundamentals
- Tushare: 120积分 limited to `daily()` and `stock_basic()`, `daily_basic()` needs 5000积分
- AKShare: rate limiting severe, fundamental APIs return empty `{}`

### yfinance A-share Code Format
- Shanghai: `{code}.SS` (6-prefix)
- Shenzhen: `{code}.SZ` (non-6-prefix)

### Feature Engineering (44-62 features)
**Technical (44, required)**: returns_1d/5d/10d/20d, ma_ratio_5/10/20/60, momentum_5d/10d/20d/60d, volatility_5d/10d/20d, volume_ratio_5d/10d, rsi_14, macd/signal/hist, bb_position, atr_14, kdj, deviation_ma20/60, price_position_20d, momentum_accel, vol_change_rate, rsi_change, macd_slope, ma20_slope, ma60_slope

**Fundamental (18, needs 5000积分)**: pe_ttm, pe_percentile, pb, turnover_rate, log_market_cap, dv_ratio, etc.

**Capital Flow (6, needs 5000积分)**: main_net_flow, main_net_flow_ratio, super_net_flow, etc.

### Model Version History
| Model | AUC | Stocks | Features | Samples | Source | Notes |
|-------|-----|--------|----------|---------|--------|-------|
| v3.1 | 0.5832 | 50 | 44 | 38K | Tushare | Baseline |
| v4.7 | **0.6499** | 733 | 38 | 556K | yfinance | **Current best**, pure technical |
| v5.0 | 0.6326 | 733 | 121 | 608K | yfinance+Tushare | Look-ahead bias in fundamentals |

**Key finding**: v3.5 AUC 0.7785 had data leakage, actual 0.6085-0.6116. v4.7's 0.6499 is correct cross-validation result.

### Composite Signal Weights
```
ml_score * 0.30 + factor_score * 0.25 + technical_score * 0.20 + emotion_score * 0.15 + capital_score * 0.10
```

### Validated Factors
- ma60_slope (60-day MA slope) — most important
- volatility_20d — IC=0.15
- momentum_60d — IC=-0.12
- macd_hist, rsi_change

### Batch Training (OOM Solution)
733 stocks need 3.4GB memory, 3.6GB server gets OOM killed. Solution: 200 stocks per batch, `gc.collect()` after each batch.

## Vector Search Integration
session_search has vector semantic search via chromadb + sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) + torch CPU.

```bash
python3 ~/.hermes/scripts/vector_search.py index --limit 100
python3 ~/.hermes/scripts/vector_search.py stats
```

Storage: `~/.hermes/cache/vector_db/` (4040 indexed messages)

## Unique Pitfalls (not in main pantalone skill)

1. **ML features contain infinity**: returns/momentum features produce inf from division by zero. Must `X.replace([np.inf, -np.inf], np.nan).fillna(0)` before training.
2. **JSON serialization of numpy types**: numpy int32/float64/bool are not JSON serializable. Use custom `NumpyEncoder`.
3. **AKShare connection unstable**: Weekend/peak hours cause RemoteDisconnected. `train_models.py` has dual-source fallback: AKShare → yfinance.
4. **Feature duplicate columns**: Multiple functions creating same feature name (e.g., `is_large_cap`) causes `pd.concat` `InvalidIndexError`.
5. **Zero-variance features**: Industry one-hot and static fundamental features may be all zeros. Must filter `var()==0` before training.
6. **Forward look-ahead bias**: yfinance `.info` returns current values. For historical training, use Tushare `daily_basic` for historical monthly data (needs 5000积分), or accept technical-only features.
