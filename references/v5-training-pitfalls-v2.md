# v5 ML训练踩坑记录（v2，2026-05-25更新）

## 1. Tushare daily_basic严重限流

**问题**：120积分账号的`daily_basic`接口限流1次/小时，`fina_indicator`同理。
**影响**：v5.0训练时基本面数据全部返回空`{}`。
**解决**：改用yfinance `info`获取基本面（无限流，但只有当前时点数据）。

## 2. 前瞻偏差（Look-ahead Bias）

**问题**：v5.0用当前时点的PE/PB/ROE填充所有历史日期，模型"看到"了未来数据。
**影响**：AUC反而低于v4.7（0.6326 vs 0.6499）。
**教训**：基本面数据必须用历史时点（按月/季度采样+前向填充）。yfinance无法获取历史基本面，需要Tushare升级积分或换数据源。

## 3. SHAP特征筛选过度

**问题**：v5.2用SHAP从69特征筛选到50个，去掉了16个有用特征（包括is_large_cap、pe_quantile、rs_vol_10d等）。
**影响**：AUC从0.6512降到0.6385。
**教训**：SHAP筛选top_n不宜过紧，建议保留80%以上特征。或直接不筛选，让模型自己学习特征权重。

## 4. 宏观特征引入噪声

**问题**：v5.2加入大盘动量、波动率等宏观特征，但这些特征对个股预测帮助有限。
**影响**：可能贡献了部分AUC下降。
**教训**：宏观特征需要与个股特征有明确的因果关系才加入，否则是噪声。

## 5. 三模型集成无显著优势

**问题**：v5.2/v5.3加入CatBoost（LGB+XGB+CB三模型集成），但AUC没有显著提升。
**原因**：LightGBM和XGBoost已经是梯度提升树的最优实现，CatBoost对类别特征友好但A股特征都是数值。
**教训**：二模型集成（LGB+XGB均值）已足够，三模型增加复杂度但收益有限。

## 6. OOM杀死全量训练

**问题**：733只股票全量训练需要3.4GB内存，服务器只有3.6GB，被OOM killer杀死。
**解决**：分批训练（每批200只），每批完成后`gc.collect()`释放内存，最后加权合并AUC。
**脚本**：`train_v5_batch.py` / `train_v52_batch.py` / `train_v53_batch.py`

## 7. Pandas concat重复列名

**问题**：`extract_fundamental_features`和`create_market_cap_features`都创建了market_cap_raw、is_large_cap等列，concat时报`InvalidIndexError`。
**解决**：去掉重复的`create_market_cap_features`调用，基本面特征函数已包含市值分组。

## 8. 数据类型比较错误

**问题**：yfinance返回的基本面数据可能包含字符串（如info中的某些字段），与数值比较时报`'<' not supported between instances of 'int' and 'str'`。
**解决**：在`extract_features_from_aligned`开头加`pd.to_numeric(col, errors='coerce')`强制转换。

## 9. 基本面特征key不匹配

**问题**：Tushare返回英文key（pe_ratio、pb_ratio），但extract函数用中文key（市盈率、市净率）查找。
**解决**：extract函数同时支持中英文key：`for k in ['市盈率(动)', '市盈率-动态', 'PE', 'pe_ratio', 'pe_ttm']`

## 10. 最佳实践总结

| 维度 | 最佳方案 | 备注 |
|------|---------|------|
| 数据源 | yfinance | 无限流，数据质量好 |
| 基本面 | yfinance info（静态） | Tushare限流严重 |
| 特征数 | 66个（v5.1） | 不宜过多也不宜过少 |
| 模型 | LGB+XGB二模型集成 | 三模型无显著优势 |
| 筛选 | 不筛选或宽松筛选 | SHAP top_n≥80%特征数 |
| 训练 | 分批200只避免OOM | 每批gc.collect() |
| 验证 | TimeSeriesSplit 5-fold | 禁止在全量数据上算AUC |
