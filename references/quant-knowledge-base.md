# 量化投资知识库

> 创建时间：2026-05-25
> 定期更新：每周日10:00（job:9d6919e8ae5f）
> 完整文件：`/tmp/quant_knowledge.md`

## 概述

基于2026-05-25的ML训练实验和网络搜索，建立了完整的量化投资知识库，覆盖9大领域。

## 核心发现

### 1. 当前模型瓶颈

| 指标 | 当前值 | 目标 |
|------|--------|------|
| AUC | 0.6499 | 0.75+ |
| 特征数 | 38 | 80+ |
| 特征类型 | 技术为主 | 技术+基本面+另类 |

### 2. 最有效的改进路径

**Phase 1：特征扩展（预期AUC → 0.68-0.70）**
- 新增20+技术因子（多周期动量、波动率族、量价因子）
- 新增15+基本面因子（PE、PB、ROE、毛利率等）
- 添加行业分类特征（申万一级行业 one-hot）
- 添加市值分组特征（大盘/中盘/小盘）
- 目标特征数：80+

**Phase 2：标签优化（预期AUC → 0.70-0.72）**
- 多窗口标签（1d/3d/5d/10d）
- 相对收益标签（超额收益）
- Learning to Rank
- 三分类标签（大涨/震荡/大跌）

**Phase 3：模型升级（预期AUC → 0.72-0.75）**
- 添加CatBoost作为第3个基学习器
- 添加TabNet作为第4个基学习器
- 实现多层Stacking
- 贝叶斯超参数优化（Optuna）

**Phase 4：A股适配（预期AUC → 0.75-0.78）**
- 涨跌停处理逻辑
- 停牌/复牌处理
- 市场状态识别特征
- 行业中性化处理

### 3. 关键技术细节

#### 3.1 高阶技术因子

```python
# 多周期动量
- 3/8/13/21日动量
- 动量加速度（动量的一阶差分）
- 动量稳定性（动量序列的标准差/均值）
- 路径依赖动量（过去N天中有M天上涨的比例）

# 波动率族
- Parkinson波动率（用日内最高最低价估计）
- Garman-Klass波动率
- Yang-Zhang波动率（处理隔夜跳空）
- 波动率锥（不同周期波动率的百分位排名）

# 成交量与流动性
- VWAP偏离度
- 量价相关性（过去N日价格变化与成交量变化的相关性）
- Amihud非流动性指标（|收益|/成交额）
- 量价背离（价格创新高但成交量未创新高）
```

#### 3.2 基本面因子

```python
# 估值因子
- PE/PB/PS/EV-EBITDA/PEG/股息率
- F-score（Piotroski基本面综合评分）

# 质量因子
- ROE/ROA/毛利率/净利率
- 资产负债率/现金流/营业收入
- 应计项目（Accruals）
- M-score（Beneish盈余操纵检测）

# 成长因子
- 营收同比增长率（单季、TTM）
- 净利润同比增长率
- 预期盈利增长率（分析师一致预期）
- 盈利超预期（实际-预期）
```

#### 3.3 另类因子

```python
# A股可获取的另类数据
- 龙虎榜数据（机构/游资买卖情况）
- 融资融券余额及变化
- 北向资金（沪深港通）持仓变化
- 股东户数变化（筹码集中度）
- 限售股解禁信息
- 新闻情绪数据（财联社、东方财富、雪球）
- 搜索热度（百度指数、微信指数）
```

### 4. 模型优化方案

#### 4.1 多层Stacking集成

```
Layer 1: LightGBM + XGBoost + CatBoost + TabNet + MLP
    ↓
Layer 2: Ridge回归（元学习器）
    ↓
Layer 3: 最终预测
```

#### 4.2 样本权重优化

```python
# 时间衰减权重
weights = np.exp(-0.01 * (latest_date - sample_date).days)

# 行业均衡权重
industry_weights = 1 / industry_counts[sample_industry]
```

#### 4.3 概率校准

```python
from sklearn.calibration import CalibratedClassifierCV
calibrated_model = CalibratedClassifierCV(model, method='isotonic')
```

### 5. A股特殊处理

#### 5.1 涨跌停处理

```python
# 涨跌停阈值
thresholds = {
    '主板': 0.10,
    '科创板': 0.20,
    '创业板': 0.20,
    '北交所': 0.30,
    'ST': 0.05
}

# 涨停时不追高，跌停时不抄底
if price_change >= threshold * 0.95:
    signal = '涨停，不追高'
elif price_change <= -threshold * 0.95:
    signal = '跌停，不抄底'
```

#### 5.2 市场状态识别

```python
# 基于MA20和MA60判断市场状态
if ma20 > ma60 and ma20_slope > 0:
    market_state = '牛市'
elif ma20 < ma60 and ma20_slope < 0:
    market_state = '熊市'
else:
    market_state = '震荡'
```

### 6. 实施路线图

| Phase | 内容 | 预期AUC | 时间 |
|-------|------|---------|------|
| 1 | 特征扩展（38→80+） | 0.68-0.70 | 1-2周 |
| 2 | 标签优化 | 0.70-0.72 | 1周 |
| 3 | 模型升级（CatBoost+TabNet+Stacking） | 0.72-0.75 | 2周 |
| 4 | A股适配 | 0.75-0.78 | 1-2周 |
| 5 | 组合与风控 | 实盘可用 | 2周 |

### 7. 参考文献

1. WorldQuant 101 Formulaic Alphas (2015)
2. Advances in Financial Machine Learning - Marcos Lopez de Prado (2018)
3. Machine Learning for Asset Managers - Marcos Lopez de Prado (2020)
4. Active Portfolio Management - Grinold & Kahn (2000)
5. 因子投资：方法与实践 - 石川 等（2020）

### 8. 开源工具

```python
# 数据获取
pip install akshare tushare baostock

# ML/DL
pip install lightgbm xgboost catboost
pip install pytorch-tabnet  # TabNet
pip install optuna  # 超参数优化

# 因子分析
pip install alphalens  # 因子分析工具
pip install pyfolio  # 投资组合分析
pip install zipline-reloaded  # 回测框架

# 遗传规划
pip install gplearn  # 符号回归/因子挖掘
```

---

**核心建议**：AUC从0.6499到0.75+，最直接有效的路径是**扩展特征（尤其是基本面因子+行业特征）** 和**优化标签（Learning to Rank或多分类）**。
