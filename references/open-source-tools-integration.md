# 开源投资工具集成指南

## 已部署工具清单

| 工具 | Stars | 用途 | 模块文件 |
|------|-------|------|----------|
| **Qlib** | 43.4K | 因子挖掘+模型训练+回测框架 | `qlib_backtest.py` |
| **OpenBB** | 68K | 金融数据平台（32+数据源） | `openbb_integration.py` |
| **FinRL** | 15.2K | 强化学习交易（PPO/A2C/DDPG/TD3/SAC） | `finrl_integration.py` |
| **LightGBM/XGBoost** | — | ML信号生成 | `ml_signal.py` |
| **ChromaDB** | — | 向量数据库（语义搜索） | `vector_search.py` |

## 模块文件位置

所有模块在 `~/.hermes/scripts/amadeus/` 下：

| 模块 | 文件 | 功能 |
|------|------|------|
| 回测增强 | `qlib_backtest.py` | IC分析、分组收益、风险归因、夏普比率 |
| ML信号 | `ml_signal.py` | LightGBM/XGBoost评分、46特征、时间序列CV |
| OpenBB数据层 | `openbb_integration.py` | 32+数据源、MCP Server、统一API |
| FinRL策略 | `finrl_integration.py` | PPO/A2C/DDPG/TD3/SAC五种DRL算法 |
| 因子挖掘 | `factor_miner.py` | RD-Agent风格、5类因子、自动验证迭代 |
| 集成中心 | `pantalone_tools_hub.py` | 统一入口、综合信号生成 |
| 训练脚本 | `train_models.py` | 模型训练（双数据源：AKShare+yfinance） |
| 优化脚本 | `optimize_ml.py` | 超参数调优、特征工程 |
| 训练v3 | `train_v3_final.py` | 50只股票集成训练 |
| 训练v3扩展 | `train_v3_extended.py` | 100只股票扩展训练 |
| 实时预测 | `ml_predict.py` | 单只/多只/观察池ML信号 |
| 每日报告 | `ml_daily_predict.py` | 每日ML信号报告生成 |
| QA闭环 | `qa_loop.py` | 测试套件+自动重试修复 |

## 综合信号生成

```bash
python3 ~/.hermes/scripts/amadeus/pantalone_tools_hub.py --comprehensive --stock 600519
```

输出格式：
```json
{
  "ml_score": {"score": 72.5, "signal": "买入"},
  "rl_signal": {"signal": "买入", "strength": 65},
  "factor_signals": {"valid_factors": 8, "best_factors": [...]},
  "composite_score": 68.5,
  "recommendation": "买入"
}
```

## ML模型状态（2026-05-24更新）

| 版本 | 股票 | 样本 | LightGBM AUC | XGBoost AUC | 集成AUC | 路径 |
|------|------|------|--------------|-------------|---------|------|
| v2 | 20 | 16,736 | 0.5932 | — | — | `ml_models/lightgbm_optimized.pkl` |
| v3.4 | 50 | 38,642 | 0.5826 | 0.5821 | 0.7430 | `ml_models/ensemble_v3_final.pkl` |
| **v3.5** | **99** | **76,472** | **0.6085** | **0.6116** | **0.7785** | `ml_models/ensemble_v3_extended.pkl` |

**训练脚本**：`train_v3_final.py`（50只）、`train_v3_extended.py`（100只）
**预测脚本**：`ml_predict.py`（实时预测）、`ml_daily_predict.py`（每日报告）

## 因子分析结果（99只沪深300成分股）

| 因子 | 重要性 | 等级 | 说明 |
|------|--------|------|------|
| volatility_20d | 864 | A | 20日波动率（最重要） |
| ma60_slope | 675 | A | 60日均线斜率 |
| momentum_60d | 642 | A | 60日动量 |
| ma_ratio_60 | 563 | B | 60日均线比值 |
| atr_14 | 549 | B | 14日ATR |

## 数据源备选策略

**优先级**：AKShare → yfinance → OpenBB

AKShare连接不稳定时自动降级到yfinance：
```python
# 茅台：600519 → 600519.SS (上海)
# 五粮液：000858 → 000858.SZ (深圳)
```

## 依赖安装

```bash
# 在Hermes venv中安装
source ~/.hermes/hermes-agent/venv/bin/activate
uv pip install pyqlib openbb finrl lightgbm xgboost catboost scikit-learn
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install sentence-transformers chromadb
```

## Pitfall

1. **JSON序列化错误**：numpy/pandas类型不能直接json.dump，需要自定义NumpyEncoder
2. **无穷大值**：特征计算可能产生inf，需要用 `X.replace([np.inf, -np.inf], np.nan).fillna(0)` 处理
3. **yfinance A股代码格式**：600519→600519.SS（上海），000858→000858.SZ（深圳）
4. **FinRL安装**：需要stable-baselines3，安装较慢
