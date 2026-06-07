---
name: pantalone
description: "Pantalone v3.7 — 投资研究系统。OCIFQ选股(寡头定价权×长周期催化×行业利润断层×财务三爆×连续季报)+Pantalone择时双轨制+ML六维评分(OCIFQ70%+ML30%)。ETF分析v3.5：9类分类+25字段+A-E评级。ML集成LightGBM+XGBoost(AUC 0.6512)。量化信号层：ML30%+因子25%+技术20%+情绪15%+资金10%。核心原则：诚实优于舒适、实质优于表演、数据先行、排雷优先、纪律大于判断。模块化架构：SOUL.md→router.md→workflow.md→subagents/(17文件)→rules/(9文件)→templates/(6文件)→references/(50+文件)。7个subagent+独立审查。模拟盘：量化评分(满分100)/分批建仓/三层清仓/大盘四级过滤。不构成投资建议。"
version: 3.5.0
---

# Pantalone 投研模块

## 核心引用

**灵魂文档**：`SOUL.md` — 投资哲学、价值观、工作原则。
**模块化架构**：SOUL.md → router.md(262行) → workflow.md(362行) → subagents/(14文件) → rules/(9文件) → templates/ → references/(22文件)。
**代码示例与详细数据**：`references/code-examples.md`（模拟盘命令、to_docx用法、腾讯API、v3版本对比、交易记录、情绪温度数据）
**Cron修改确认模板**：`templates/cron_change_template.md`（修改cron前必须使用）
**Cron容错与备份机制**：`references/cron-fault-tolerance-pattern.md`（备份渠道不能是同一渠道/限流诊断/补发流程/低分改进TODO）
**Cron时间表优化**：`references/cron-schedule-optimized.md`（2026-05-27更新：所有job间隔≥10分钟，限流诊断流程，Discord为主推送渠道）
**Perplexity上下文压缩**：`references/context-compression-perplexity.md`（Phase 2.5 query-aware过滤，CJK支持）
**规则系统**：`references/rule-system.md`（R-xx编号/触发条件/有效期/状态/继承性，收盘复盘必须检查和更新）
**继承项系统**：`references/inheritance-system.md`（每日收盘生成明日继承项，次日早盘必须读取）
**收盘复盘模板v3**：`templates/review_template.md`（30秒速读/预测命中率/规则系统/五级股票池/继承项/数据源逐项标注）
**止损自动监控**：`scripts/amadeus/stop_loss_monitor.py`（A池-10%/B池-5%/C池-3%，每天15:00自动检查）
**止损确认与告警**：`references/stop-loss-and-pool-rules.md`（止损确认机制+滞后告警+入池OCIFQ强制）
**决策日志系统**：`~/.hermes/cache/amadeus/decision_log.json`（预判→验证→命中率→改进闭环。晚间复盘写入预判，收盘复盘验证前日预判+写入新预判。详见self-improvement skill的Section十七+`references/investment-iteration-guide.md`）。**JSON结构**：顶层keys=`version/created/entries/stats`，`entries`是数组（非predictions），每条entry=`{id, date, type, prediction, confidence, status, source, target?, verified_date?, result?}`，`stats`=`{total_predictions, verified, hits, misses}`。读取时用`terminal("cat file")`而非`read_file`（后者带行号前缀LINE_NUM|CONTENT，JSON解析需额外处理）。**详细结构**：`references/decision-log-structure.md`
**Gateway故障排查**：`references/gateway-cron-troubleshooting.md`（PATH问题+超时修复+渠道迁移）
**风险整改自动化流程**：`references/risk-rectification-process.md`（2026-05-26：自动整改报告中的风险项目）

**数据管线审计**：`references/data-pipeline-audit.md`（2026-05-20完整审计：数据源分类/缺失脚本/降级链路/验证缺口）
**工作流审计报告**：`references/workflow-audit-20260515.md`（5个严重问题+修复清单+防复发机制）
**a-stock-data-supp集成记录**：`references/a-stock-data-integration.md`（2026-06-03：端点实测结果/架构变更/集成方法论）
**Subagent并行架构**：`references/subagent-execution-flow.md`（v3.4并行delegate_task流程）+ `references/subagent-protocol-v3.4.md`（角色映射+陷阱）
**ETF数据采集**：`references/etf-data-collection.md`（AKShare ETF接口坑+东方财富备用API+18只ETF实测数据源）
**Datasette集成**：`references/datasette-setup.md`（安装/示例数据库/JSON API/集成方案）
**开源工具集成**：`references/quant-ml-integration-guide.md`（ML训练流水线+Qlib/OpenBB/FinRL集成+因子分析+详细代码示例+特征工程+模型版本历史）
**量化信号模块**：`scripts/amadeus/pantalone_tools_hub.py`（综合信号：ML+RL+因子+技术面）
**向量搜索模块**：`references/vector-search-setup.md`（chromadb+sentence-transformers，语义搜索session历史）
**ML训练最佳实践**：`references/ml-training-best-practices.md`（2026-05-25：v3.5 AUC数据泄露教训、数据源对比、训练配置、38特征列表、OCIFQ+ML整合、模拟盘系统）
**ML模型状态**：v4.4交叉验证AUC 0.6365（正确），v3.5的0.7785是数据泄露
**ML训练优化指南**：`references/ml-training-optimization.md`（v4.0-v4.4训练实验总结：yfinance vs Tushare、标准化、参数调优、数据范围影响）
**量化知识库**：`/tmp/quant_knowledge.md`（2026-05-25创建：特征工程/因子挖掘/模型优化/标签工程/A股特性/实施路线图，每周日10:00自动更新，job:9d6919e8ae5f）
**v5特征扩展脚本**：`scripts/amadeus/train_v5_features.py`（113特征：38技术+26高阶技术+14基本面+31行业+4市值，预期AUC 0.68-0.70）
**统一数据源管理器**：`scripts/amadeus/data_source_manager.py`（yfinance/Tushare/AKShare多源降级+本地缓存）
**ML模拟盘系统**：`scripts/amadeus/ml_simulation.py`（模拟交易）+ `ml_sim_daily_check.py`（每日检查）+ `ml_backtest.py`（历史回测）
**ML模拟盘验证系统**：`references/ml-simulation-system.md`（模拟交易/回测引擎/每日检查/定时任务）
**情绪温度数据管线**：`references/emotion-data-pipeline-fix.md`（2026-05-20修复：连板/成交额字段映射）
**数据质量等级指南**：`references/data-quality-guide.md`（data_quality.py用法/等级规则/嵌入报告方式/pitfall）
**数据缺口处理指南**：`references/data-gap-handling.md`（新闻超时/北向缺失/pool为空/板块失败时的报告标注规范）
**JSON缓存文件结构**：`references/json-cache-structures.md`（market/pool_state/emotion/global四个缓存文件的完整字段说明+pitfalls，cron读取前必看）
**Cron Prompt提取方法**：`references/cron-prompt-extraction.md`（从jobs.json提取prompt的正确方法，避免unicode转义陷阱）
**数据质量系统详细文档**：`references/data-quality-system.md`（8项核心数据/cache加载逻辑/等级规则/pitfall/与其他模块关系）
**Pool Manager数据源降级**：`references/pool-manager-fallback.md`（4级降级梯队/调用点/pitfall/类推教训）
**Tushare接口清单**：`references/tushare-interfaces.md`（120积分可用/不可用接口+替代方案）
**OCIFQ选股框架**：`references/ocifq-framework.md`（行业印钞机五维评分+双轨制+实战案例）
**integrate-news自动入池修复**：`references/integrate-news-auto-add-fix.md`（2026-05-21修复：只生成建议不入池的bug）
**选股Skill**：`stock-picking` skill（OCIFQ选股完整流程，输出≥10只牛股）
**10模块投研系统**：`references/ten-module-investment-system.md`（完整架构：10个skill+五层报告+模板清单）
**盘中异动监控脚本**：`scripts/amadeus_watcher.md`（涨跌幅/止损/涨停监控，每30分钟执行）

## Agent体系命名（Commedia dell'arte）

- 主Agent = **Amadeus**（综合型数字人格Agent）
- 投研模块 = **Pantalone**（商人角色，管钱）
- 脚本文件名 = `amadeus_*.py`（保留不变，避免大规模引用更新）
- 投研目录 = `skills/investment/pantalone/`

## SOUL.md更新（2026-05-21）

主SOUL.md新增内容：
1. **6条通用核心原则**（从Amadeus SOUL.md提取）：诚实优于舒适、实质优于表演、数据优先、先查再想、复盘优于嘴硬、不确定就说不确定
2. **Karpathy四原则**：编码前思考、简洁优先、精准修改、目标驱动执行

投研SOUL.md新增：
- **4.15节 OCIFQ选股体系**：行业印钞机公式+五维评分+双轨评分

## 开源发布状态（2026-06-07）

Pantalone计划开源到GitHub，用于获取OpenAI Codex for Open Source奖励。

**已生成的开源文件**（位于`skills/investment/pantalone/`）：
- README.md — 项目介绍、安装、使用、架构
- LICENSE — MIT许可证
- CONTRIBUTING.md — 贡献指南
- .gitignore — 排除缓存/密钥/模型/日志
- .env.example — API key配置模板
- pyproject.toml — Python项目元数据
- requirements.txt — 依赖清单
- SECURITY_AUDIT.md — 安全审查报告（内部用，推送前删除）

**安全审计发现**：
- 🔴 dspy_optimize_skill.py第10行硬编码DeepSeek API key（sk-0877...），必须删除或改为环境变量
- ⚠️ SKILL.md含Discord channel ID和/home/ubuntu路径，需要清理
- ⚠️ 缓存文件（pool_state.json等）已在.gitignore中排除

**待办**：
- 主人提供GitHub Token后执行：gh auth login → 清理敏感数据 → gh repo create --public --push

**详细工作流**：`github-open-source-release` skill

## 环境

- Python：`/usr/bin/python3`（系统Python）
- AKShare：已装到系统Python
- 模型：mimo-v2.5-pro（默认）/ deepseek-v4-pro（备用，余额80 CNY）
- ⚠️ MiMo不支持vision，需看图时切DeepSeek
- Claude Code v2.1.148：`~/.npm-global/bin/claude`，小米中转+mimo-v2.5-pro。**主人要求：所有编程任务都用Claude Code**

**ML模拟盘系统**：`scripts/amadeus/ml_simulation.py`（模拟交易）+ `scripts/amadeus/ml_sim_daily_check.py`（每日检查）+ `scripts/amadeus/ml_backtest.py`（历史回测）。定时任务：每天15:30 ML信号(job:ad58c2202a81) + 每天16:00模拟盘检查(job:0cb6066c305b)。交易规则：买入ML>60，卖出ML<40，止损-5%，止盈+10%，最长持仓5天。
**OCIFQ+ML整合选股**：`scripts/amadeus/ocifq_ml_selector.py`（六维评分：OCIFQ 70% + ML 30%）
**ML训练经验**：`stock-picking/references/ml-training-lessons.md`（特征质量>数据数量、数据源降级策略）
**止损自动监控**：`scripts/amadeus/stop_loss_monitor.py`（A池-10%/B池-5%/C池-3%，每天15:00检查）
**达尔文评估报告**：`references/darwin-evaluation-20260528.md`（9维评分60.4→64.0，待优化：dim7整体架构需探索性重写）
**达尔文使用指南**：`references/darwin-skill-guide.md`（安装/流程/9维度/实战经验）
**电力板块研究**：`references/power-sector-research-20260528.md`（电力+电网设备估值对比、OCIFQ评分、持续性判断）
**实用技术分析双框架**：`references/ta-left-right-framework.md`（左侧MA120/MA50+低PE高股息、右侧放量突破，来自实战总结）
**持仓诊断流程**：`references/portfolio-diagnosis-workflow.md`（逐只分析→重叠检测→集中度→调仓建议，含ETF重叠检测方法）

## 已接入

- Tavily Search：1000次/月，key在~/.bashrc
- Tushare Pro：v1.4.29，token已配，120积分级（可用：daily/moneyflow_hsgt/ggt_top10/hsgt_top10/cyq_perf/shibor/stock_basic/index_basic。不可用：index_daily/daily_basic/trade_cal/margin_detail/stk_limit/ths_*/cn_gdp/cn_cpi）
- Tushare脚本：`tushare_data.py`（north/daily/shibor/cyq/top10/all），venv Python运行
- humanizer-zh：中文去AI痕迹
- 8个Pantalone技能（chanlun/sentiment/valuation/risk/sector-rotation/earnings/behavioral/seasonal）
- **a-stock-data-supp**：A股数据补充层（龙虎榜席位/融资融券/大宗交易/股东户数/分红送转/限售解禁/行业排名/同花顺热点归因/北向分钟流/东财研报/巨潮公告），13个端点，东财datacenter内置em_get限流防封。路径：`skills/investment/a-stock-data-supp/`，CLI：`scripts/a_stock_data_supp.py`

## 开源工具集成（2026-05-24新增）

### 已部署工具

| 工具 | Stars | 用途 | 状态 |
|------|-------|------|------|
| **Qlib** | 43.4K | 因子挖掘+模型训练+回测框架 | ✅ 已集成 |
| **OpenBB** | 68K | 金融数据平台（32+数据源） | ✅ 已集成 |
| **FinRL** | 15.2K | 强化学习交易（PPO/A2C/DDPG/TD3/SAC） | ✅ 已集成 |
| **LightGBM/XGBoost** | — | ML信号生成 | ✅ 已训练 |
| **ChromaDB** | — | 向量数据库（语义搜索） | ✅ 已部署 |

### 模块文件

| 模块 | 文件 | 功能 |
|------|------|------|
| 回测增强 | `scripts/amadeus/qlib_backtest.py` | IC分析、分组收益、风险归因、夏普比率 |
| ML信号 | `scripts/amadeus/ml_signal.py` | LightGBM/XGBoost评分、46特征、时间序列CV |
| OpenBB数据层 | `scripts/amadeus/openbb_integration.py` | 32+数据源、MCP Server、统一API |
| FinRL策略 | `scripts/amadeus/finrl_integration.py` | PPO/A2C/DDPG/TD3/SAC五种DRL算法 |
| 因子挖掘 | `scripts/amadeus/factor_miner.py` | RD-Agent风格、5类因子、自动验证迭代 |
| 集成中心 | `scripts/amadeus/pantalone_tools_hub.py` | 统一入口、综合信号生成 |
| 训练脚本 | `scripts/amadeus/train_models.py` | 模型训练（双数据源：AKShare+yfinance） |
| 优化脚本 | `scripts/amadeus/optimize_ml.py` | 超参数调优、特征工程 |
| **OCIFQ+ML整合** | `scripts/amadeus/ocifq_ml_selector.py` | 六维评分选股（OCIFQ70%+ML30%） |
| **ML模拟交易** | `scripts/amadeus/ml_simulation.py` | 模拟买卖、检查平仓、绩效报告 |
| **ML回测引擎** | `scripts/amadeus/ml_backtest.py` | 历史回溯验证、绩效统计 |
| **ML每日检查** | `scripts/amadeus/ml_sim_daily_check.py` | 每日模拟盘状态检查 |

### ML模型状态（2026-05-25更新）

| 版本 | 股票数 | 样本数 | 特征数 | 集成AUC | 状态 | 路径 |
|------|--------|--------|--------|---------|------|------|
| v3.5 | 99 | 76,472 | 41 | ~~0.7785~~ | ❌数据泄露 | `ml_models/ensemble_v3_extended.pkl` |
| v4.4 | 136 | 104,955 | 38 | 0.6365 | ✅正确 | `ml_models/lightgbm_v44.pkl` |
| v4.5 | 299 | 227,735 | 38 | 0.6427 | ✅正确 | `ml_models/lightgbm_v45.pkl` |
| v4.6 | 495 | 374,745 | 38 | 0.6465 | ✅正确 | `ml_models/lightgbm_v46.pkl` |
| v4.7 | 733 | 556,410 | 38 | 0.6499 | ✅正确 | `ml_models/lightgbm_v47.pkl` |
| v5.0 | 733 | 608K | 121 | 0.6326 | ❌前瞻偏差 | `ml_models/lightgbm_v5.pkl` |
| **v5.1** | **727** | **606K** | **66** | **0.6512** | ✅**当前最优** | `ml_models/lightgbm_v51.pkl` |
| v5.2 | 723 | 602K | 50 | 0.6385 | ⚠️SHAP过度筛选 | `ml_models/lightgbm_v52.pkl` |
| v5.3 | 运行中 | — | ~66 | — | 🔄训练中 | `scripts/amadeus/train_v53.py` |

**AUC提升趋势**（扩大样本有效，但边际递减）：
```
v4.4: 136只  → 0.6365
v4.5: 299只  → 0.6427 (+0.0062)
v4.6: 495只  → 0.6465 (+0.0038)
v4.7: 733只  → 0.6499 (+0.0034)
v5.1: 727只  → 0.6512 (+0.0013) ← 基本面特征生效
```

**v5特征扩展（113个）**：
| 特征分组 | 数量 | 说明 |
|---------|------|------|
| v4.7技术因子 | 38 | 保持兼容 |
| 高阶技术因子 | 26 | 多周期动量、波动率族、ADX、MFI、OBV、VWAP等 |
| 基本面因子 | 14 | PE/PB/ROE/EPS/市值/营收增长/利润增长等 |
| 申万行业 | 31 | one-hot编码覆盖31个行业 |
| 市值分组 | 4 | 大盘/中盘/小盘 + 对数市值 |

**⚠️ 关键教训（2026-05-25发现）**：v3.5的集成AUC 0.7785是**数据泄露**——在全量训练数据上计算的，不是在验证集上。v4.4的0.6365是正确的交叉验证结果，实际上优于v3.5的单模型AUC（0.6085-0.6116）。

**数据源**：yfinance（最优）> Tushare Pro > AKShare（严重限流）
**基本面数据**：yfinance `info`（主力，无限流）> Tushare `daily_basic`+`fina_indicator`（限流严重，120积分1次/小时）> AKShare（不可用）
**详细踩坑**：`references/v5-training-pitfalls.md`
**v5.1生产模型**：ml_predict.py已更新加载v5.1（66特征：37技术+10高阶+19基本面），predict()传递symbol参数获取基本面

**训练配置**：n_estimators=500, learning_rate=0.03, max_depth=7, reg_alpha=0.1, reg_lambda=0.1, subsample=0.8, colsample_bytree=0.7, StandardScaler标准化, TimeSeriesSplit 5-fold
**关键发现**：
- 集成模型（LightGBM+XGBoost简单平均）比单模型AUC提升27%+
- **特征质量 > 数据量**：v4.0用54万样本+14特征反而AUC下降，v3.5用7.6万样本+44特征效果更好
- 沪深300大盘股波动小，预测难度大于中小盘
- 10年旧数据可能包含过时模式，3-5年数据更合适

**训练数据源优先级**：Tushare Pro（稳定）> AKShare（限流严重）> Ashare
**股票池选择**：沪深300成分股（主人指示），本地缓存在 `~/.hermes/cache/amadeus/hs300_data/`
**训练流水线详细文档**：`references/ml-training-pipeline.md`（版本历史/教训/脚本清单/模拟盘系统）

**实时预测用法**（v5.1模型，66特征）：
```bash
python3 ~/.hermes/scripts/amadeus/ml_predict.py --stock 600519     # 单只
python3 ~/.hermes/scripts/amadeus/ml_predict.py --stocks 600519,000858 --report  # 多只+报告
python3 ~/.hermes/scripts/amadeus/ml_predict.py --pool             # 观察池
```
**预测器更新**：ml_predict.py已支持v5.1模型（优先加载v5.1，备用v3集成）。predict()传递symbol参数获取yfinance基本面数据。

### 因子分析结果（20只股票）

| 因子 | IC值 | 等级 | 有效性 |
|------|------|------|--------|
| ma60_slope | — | A | 60日均线斜率（最重要） |
| volatility_20d | 0.15 | A | 20日波动率 |
| momentum_60d | -0.12 | B | 60日动量 |
| macd_hist | — | B | MACD柱状图 |
| rsi_change | — | B | RSI变化 |

### 综合信号生成

```bash
# 生成综合信号（整合ML/RL/因子）
python3 ~/.hermes/scripts/amadeus/pantalone_tools_hub.py --comprehensive --stock 600519
```

输出示例：
```json
{
  "ml_score": {"score": 72.5, "signal": "买入"},
  "rl_signal": {"signal": "买入", "strength": 65},
  "factor_signals": {"valid_factors": 8, "best_factors": [...]},
  "composite_score": 68.5,
  "recommendation": "买入"
}
```

## 模拟盘规则（v3.1 强制）

引擎：`scripts/amadeus_sim_integrate.py`。详见 `workflow.md`。

**脚本清单**：`references/v3-scripts-guide.md`

### 买入规则

量化评分（满分100，门槛60）：OCIFQ选股(60%) + Pantalone择时(40%)

**OCIFQ选股维度（60分）**：
- O 寡头定价权（15%）：CR3集中度、专利壁垒、切换成本、毛利率≥30%
- C 长周期催化（10%）：催化持续≥4季度（AI/能源/技术迭代/政策）
- I 行业利润断层（10%）：同行业多家公司同步业绩改善
- F 财务三爆（15%）：收入≥30%+利润≥50%+毛利率≥5pct（≥2项达标）
- Q 连续季报（10%）：4季度收入/利润/毛利率连续改善

**Pantalone择时维度（40分）**：
- RSI/均线位置（10%）
- 量价配合（8%）
- 资金流向（7%）
- 消息催化（8%）
- 板块强度（7%）

**硬门槛**：三爆缺一项最高B级，F<70总分最高75，O<60最高A级
- 仓位：60-69分→10%(2万) | 70-79→15%(3万) | 80-89→20%(4万) | 90+→25%(5万)
- 分批建仓：首批50%，次日确认(不跌>2%)补50%
- 大盘过滤：主升浪(涨停>80)→70% | 震荡偏强→50% | 震荡→40% | 回调→20% | 恐慌→0%

### 清仓规则（三层）

1. 均线：跌破5日→减半 | 跌破10日→清仓 | 次日收回→不减
2. 分批止盈：+12%卖1/3 | +20%卖1/3 | +30%跟踪止盈 | 回撤-5%卖剩余
3. 时间：3-5天正常 | 5-7天减半 | 10天+无条件清仓

### 单票上限

`max(25%总仓位, 股价×100)` — 确保高价股至少买1手。详见 `references/code-examples.md`

### 每个cron报告必须调用

`python3 amadeus_sim_integrate.py status` + `daily_update`（收盘后）。详见 `references/code-examples.md`

### ⚠️ 情绪温度市场宽度因子（2026-05-28修复）
原实现用离散阈值（>100=25, >80=20, >50=15, >30=10, <30=5），跳跃过大导致偏差18分。
**修复**：改用连续函数 `width_score = max(0, min(25, zt / 120 * 25))`。
若有真实上涨家数数据，优先用 `breadth_pct = up/(up+down)*100` → `(breadth_pct-20)/60*25`。
文件：`amadeus_emotion.py` calc_emotion() 函数。

### ⚠️ OCIFQ强制评分补丁陷阱（2026-05-28发现）
`ocifq_enforce.py` 会往 pool_manager.py 注入OCIFQ检查代码。
**bug**：如果注入到 `remove_stock` 函数，会导致无法退池（退池不需要OCIFQ评分）。
**症状**：`python3 amadeus_pool_manager.py remove 002535 "reason"` → `⚠️ 入池被拒绝：缺少OCIFQ评分`
**修复**：删除 `remove_stock` 函数中的OCIFQ检查块（保留 `add_stock` 的检查）。
**教训**：OCIFQ评分只约束入池，不约束退池/降级。

## 数据采集体系

| 脚本 | 数据源 | 覆盖 |
|------|--------|------|
| amadeus_data.py | 新浪/同花顺/Ashare/**Tushare备用** | 市场总貌、指数、涨跌停、北向(AKShare→Tushare降级)、板块、板块资金流 |
| data_quality.py | cache文件+嵌套字段 | **数据质量等级评估**：8项核心数据×A/B/C+/C/D/F，报告必须嵌入 |
| amadeus_external.py | AKShare→腾讯API双源降级 | 美股三大指数、A50期货、港股、汇率（多源冗余） |
| amadeus_realtime.py | 腾讯API+AKShare | 实时行情+技术指标（MA/MACD/RSI/布林带） |
| amadeus_indicators.py | AKShare | MA/MACD/RSI/布林带（批量计算） |
| amadeus_financials.py | 同花顺+巨潮 | 财报 |
| amadeus_news_scanner.py | 东方财富/财联社/新浪/同花顺 | 新闻4源260条（⚠️无JSON输出，详见`references/news-scanner-cli.md`） |
| amadeus_sector_flow.py | 同花顺 | 板块资金流（独立入口+自动单位核验） |
| amadeus_etf_pool_manager.py | 新浪API+AKShare | ETF观察池管理（ABC池/退池/入池/止损/18项风险） |
| tushare_data.py | Tushare Pro(venv) | 北向资金(最稳)、SHIBOR利率、筹码分布、北向十大活跃、个股日线 |
| **a_stock_data_supp.py** | **东财datacenter+同花顺+腾讯+巨潮** | **龙虎榜席位、融资融券、大宗交易、股东户数、分红送转、限售解禁、行业排名、热点归因、北向分钟流、研报、公告（13端点，东财内置em_get限流）** |

**优先级**：amadeus_data → AKShare → 腾讯行情API → Tushare → Ashare → Tavily
**a_stock_data_supp.py优先级**：腾讯行情 → 同花顺热点/北向 → 巨潮公告 → 东财datacenter（有风控，走em_get限流）

### 统一验证模块 data_validator.py

### QA闭环测试系统（借鉴Replit）

**核心思想**：采集 → 验证 → 失败 → 自动修复 → 重验证，形成自我纠错闭环。

**文件位置**：
- 测试套件：`scripts/amadeus/tests/test_pantalone_data.py`
- 闭环Runner：`scripts/amadeus/qa_loop.py`

**测试分层**（5层递进）：
1. **格式验证**（单元测试）：数据字段完整性、数值范围、类型检查
2. **数据采集**（集成测试）：调用AKShare/新浪/腾讯验证实际采集
3. **交叉验证**（多信号）：同数据多源对比，发现单源偏差
4. **质量评级**：评分逻辑正确性验证
5. **脚本完整性**：必要文件存在、JSON缓存可解析

**用法**：
```bash
# 完整闭环
python3 ~/.hermes/scripts/amadeus/qa_loop.py
# 只跑格式验证（不依赖网络）
python3 ~/.hermes/scripts/amadeus/qa_loop.py --data-only
# 直接pytest
pytest ~/.hermes/scripts/amadeus/tests/test_pantalone_data.py -v
```

**触发时机**：
- 修改数据采集脚本后 → 必须运行 `qa_loop.py --data-only`
- 修改数据验证逻辑后 → 必须运行完整 `qa_loop.py`
- 周末/非交易时段 → 只跑格式验证，网络测试预期失败

**自动修复能力**：
- JSON缓存损坏 → 自动备份+重建
- 缺失文件 → 检测并报告
- 网络失败 → 等待5秒后重试（最多3次）

所有数据采集脚本共用 `data_validator.py`，提供：
- `is_valid_number(val)` — NaN/Inf/0检测
- `is_valid_flow(val)` — 资金流验证（允许负数）
- `is_fresh_date(date_str)` — 日期新鲜度检查（允许今天和昨天）
- `validate_quote/validate_index/validate_flow/validate_amount` — 各类数据验证
- `check_and_report(name, data, source, validator, fallback_fn)` — 通用检查+降级框架

**异常值检测规则**：
| 数据类型 | 异常条件 | 处理 |
|---------|---------|------|
| 北向资金 | NaN/0.0/日期过期 | 降级Tushare |
| 市场总貌 | 全市场<1000只 | 返回None |
| 指数价格 | price<=0 | 跳过该指数 |
| 汇率 | rate<5或>10 | 标记null |
| K线close | 全NaN/0/负数 | 返回error |
| 涨停数 | >500 | 打印警告 |
| 美股pct | NaN | 修复为0.0 |
**腾讯API**：无需Key，详见 `references/code-examples.md`
**板块资金流**：amadeus_data.py → collect_sector_flow()
**情绪温度**：amadeus_emotion.py（公式固化，禁止LLM手动算）
**个股观察池**：pool_manager.py auto（自动scan+integrate-news+apply+日志），数据存stock_notes
**ETF观察池**：etf_pool_manager.py auto（自动scan退池+新闻入池+18项风险检查+日志），数据存etf_notes。脚本：`scripts/amadeus/amadeus_etf_pool_manager.py`。ETF类型差异化止损（宽基-6%/行业-8%/QDII-10%/债券-3%）。详见 `rules/pool_rules.md` ETF章节
**观察池状态文件**：`cache/amadeus/pool_state.json`（动态状态，不存记忆。每次pool_manager执行后更新。含A/B/C池个股、盈亏、状态、主题、退池记录、活跃主题）

### 动态状态存储规范

频繁变化的数据（池子数量、个股、盈亏）**不存记忆**，存专用数据文件：
- `cache/amadeus/pool_state.json` — 观察池快照（谁产生数据谁负责更新）
- `cache/amadeus/pool_changes.log` — 入退池变更日志
- 需要引用时直接读文件，零token浪费

## 输出规范（严格遵守）

- **报告开头** `<!--REPORT_START-->`，结尾 `<!--REPORT_END-->`
- **报告开头必须包含数据质量区块**：运行 `python3 ~/.hermes/scripts/amadeus/data_quality.py --report-fragment`，将输出粘贴在报告正文第一段。等级低于C+时加"⚠️ 数据降级，分析可靠性降低"警告
- **回复只发摘要**（只保留关键数据，完整即可，不要为压缩而丢信息），完整版转.docx通过MEDIA:发送
- **⚠️ 所有文本输出必须过humanizer**：摘要文本发送前运行 `python3 ~/.hermes/scripts/amadeus/humanize_auto.py <报告文件> --inplace`；docx转换已自动集成humanizer（to_docx.py内建）
- **禁止输出代码块、bash命令、python脚本**
- 禁止标注Subagent分工标签
- 情绪评分量化（如7/10）
- 每份报告末尾列出数据来源+风险声明
- **发送前自检**：内容干净（无代码/skill元数据）？有REPORT标记？完整版走docx？
- **推送渠道**：Discord为主（channel ID:1509184957245948014），微信仅交互不推送

## 发送前自检清单（每次输出必须执行）

1. 内容干净？（无代码块、bash命令、python脚本、skill元数据）
2. 有REPORT标记？（`<!--REPORT_START-->` / `<!--REPORT_END-->`）
3. 完整版走docx？（`cat report.md | python3 ~/.hermes/scripts/amadeus/to_docx.py "标题" output.docx` → 回复中加`MEDIA:output.docx`）
4. **文本过humanizer？**（`python3 ~/.hermes/scripts/amadeus/humanize_auto.py <文件> --inplace`）
5. 摘要≤500字？（只保留关键数据）
6. 有免责声明？（市场有风险，投资需谨慎）
7. 数据来源标注？（每个数据点标明来源）
8. 无虚构数据？（所有数据可验证）
9. **有数据质量区块？（data_quality.py --report-fragment输出已在报告开头）**

## 失败模式与降级路径（集中式）

> **触发条件 / 一线修复 / 仍失败兜底** — 三段式编码，禁止只写正向流程。

| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|-----------|
| AKShare API超时/RemoteDisconnected | 重试3次，间隔5秒 | 降级新浪API → 标注"数据缺失" |
| 涨跌停池返回空DataFrame | 换日期重试（T-1） | 从market_*.json的pools字段提取 |
| 情绪温度缺2项以上数据 | 用amadeus_emotion.py自动降级 | 输出"情绪温度暂估：数据不足" |
| 北向资金NaN/0.0 | 降级Tushare moneyflow_hsgt | 标注"北向数据缺失" |
| 板块资金流单位存疑 | 交叉验证东方财富vs同花顺 | 标注"单位待核验" |
| to_docx.py转换失败 | 检查python-docx是否安装 | 降级发送纯markdown |
| humanize_auto.py篡改数据 | 校验关键数字/股票代码 | 回滚到humanize前版本 |
| cron推送被iLink限流 | 等10分钟后重试 | 保存本地，手动补发 |
| pool_manager remove被OCIFQ拦 | 检查是否误注入OCIFQ检查 | 直接编辑session_context.json |
| ML预测OOM | 分批200只+gc.collect() | 降级到v4.7模型 |
| Gateway重启打断会话 | 等重启完成后恢复 | 检查restart_gateway.sh时间门控 |
| sudo setuid损坏 | chmod 4755 /usr/bin/sudo | 用VNC登录腾讯云控制台修复 |

## 常见坑

1. **报告过大导致Gateway假死**：50-75KB报告分30+chunk触发iLink限流→event loop崩溃。修复：摘要+docx
2. **to_docx.py从stdin读取**：`cat file.md | python3 to_docx.py "标题" output.docx`
3. **模拟盘从未写入**：cron只读不调record。v3.0已修复
4. **情绪温度LLM偏差巨大**：28 vs 67差43分。必须用amadeus_emotion.py
5. **盘前Sina API返回current=0**：pool_manager用prev_close降级
6. **涨停阈值未区分板块**：主板10%/科创创业20%/北交所30%/ST 5%
7. **买入规则散落多处矛盾**：统一写入risk_rules.md
8. **高价股被单票上限误拦**：上限取max(25%,1手金额)
9. **Cron缺delegation工具集**：delegate_task不可用→subagent永不执行。修复：所有cron必须加`delegation`到enabled_toolsets
10. **分析必须全量调取数据**：不能只看规则文件，必须同时调取历史回放数据、观察池表现、交易记录、板块数据
11. **止损判断必须验证实际数据**（2026-05-26教训）：必须①读取pool_state.json实际浮亏 ②与止损线比较（A池-10%/B池-5%/C池-3%） ③只有实际触发才报告。不能依赖报告中的错误判断。
12. **风险整改必须自动执行**（2026-05-26教训）：收盘复盘中风险问题必须自动整改（清理池子、执行止损、更新状态），不能只报告不执行。详见`references/risk-rectification-process.md`。
13. **B池膨胀必须主动精简**（2026-05-26教训）：B池>50只时保留前50只（按浮盈排序），移出其余。同步更新session_context.json和pool_state.json。
14. **Cron docx发送必须有显式步骤**（2026-05-27教训）：cron prompt必须写明第四步：①保存markdown ②运行to_docx.py ③回复含MEDIA:标签。不能只写意图不写指令。
15. **渠道级限流导致全部推送失败**（2026-05-27教训）：微信iLink渠道级限流，6个任务30分钟内全部被挡。修复：任务间隔≥10分钟，Discord为主推送渠道。详见`references/cron-schedule-optimized.md`。
16. **自我审查反模式**：Agent默认读自己报告→说"看起来不错"→发送。必须在prompt中强制delegate_task独立审查，不可自己审查自己。
17. **amadeus_research.py字段不兼容**：session文件用`session_id`非`id`，depth存为字符串。已修复
18. **修改cron未确认**：SOUL.md 15.2要求cron修改必须确认。必须先输出变更清单等主人确认
19. **单轮多任务**：SOUL.md 15.4要求每轮只做一个主任务。用todo管理多步骤
20. **工具调用重复**：同一文件读3-4次浪费token。首次读取后缓存结果
21. **压缩摘要不可信**：上下文压缩可能记录"已完成"但实际未做。压缩后必须验证关键文件
22. **delegate_task batch上限3**：5个subagent必须分2批（3+2），不能一次传5个tasks
23. **amadeus_sector_flow.py已存在**（2026-05-21更正）：`~/.hermes/scripts/amadeus/amadeus_sector_flow.py`存在且可用。板块资金流有两个入口
24. **审查发现critical必须修正**：不能忽略审查结果，critical问题必须修正后重审通过才能发送
25. **AKShare fund_etf_hist_em连接不稳**：循环获取19只ETF历史数据时全部RemoteDisconnected。备用：东方财富pushapi+fundgz+pingzhongdata
26. **execute_code内report生成脚本**：写到scratchpad用terminal执行比inline execute_code可靠。大量数据直接write_file到cache目录
27. **f-string不能含反斜杠**：Python 3.11 f-string内不允许`\\`，用%格式化或先赋值变量替代
28. **execute_code 50 tool call limit**：batch操作必须分批执行，每批≤50次terminal调用。先计数再分批
29. **"执行退池"= run auto**：用户说"执行退池"时直接跑`auto`（退池+入池一步到位），不要拆成scan+apply
30. **精简池子策略**：B池>15只时按主题分类保留龙头，execute_code批量remove+直接改context做C→B升级
31. **语言强制**（2026-05-22教训）：cron prompt开头加"全程必须用中文"，输出规范末尾再加一次。不能只在SKILL.md里写
84. **amadeus_news_scanner.py CLI flags**（2026-06-05验证）：`--json`参数不存在（报"Unknown command"），`hotspots`命令在cron上下文中经常超时（60s）。正确用法：直接运行`python3 amadeus_news_scanner.py hotspots`获取文本输出，或从缓存`news_latest.json`读取（注意缓存可能过期，scan_time字段检查日期）。不支持结构化JSON输出。
85. **amadeus_emotion.py输出结构变更**（2026-06-05验证）：`emotion_YYYY-MM-DD.json`不再包含`dimensions`字典（旧文档中的`dimensions.limit_ratio.score`等路径不存在）。当前结构为扁平化：`score`/`level`/`components`(维度名称列表)/`missing`/`weights_used`/`data_completeness`/`data_freshness`。各维度分数详情只在脚本控制台输出中，不在JSON中。详见`references/json-cache-structures.md`。
86. **amadeus_emotion.py --json参数陷阱**（2026-06-04-05反复出现）：`--json`参数在某些上下文中被脚本当作日期字符串处理，导致输出含"使用2026-05-18的数据"警告且数据过期。最佳做法：不传参数直接运行，或用`python3 -c "import amadeus_emotion; ..."`直接调用。
87. **晚间复盘数据采集降级**（2026-06-05总结）：晚间复盘（21:00）时amadeus_news_scanner.py和amadeus_external.py均可能超时/失败。降级策略：①新闻从缓存读取（检查scan_time是否今天） ②外围市场3/5项缺失标注在数据等级中 ③板块数据AKShare RemoteDisconnected时标注缺失。报告开头用data_quality.py --report-fragment自动评估。
88. **市场数据JSON中indices字段独立于market**（2026-06-05验证）：指数数据在`d['indices']`下（key如`sh000001`），不在`d['market']`下。market只含总貌（up/down/flat/total_amount/limit_up等）。指数涨跌幅需手动计算：`(close - t_minus_2_close) / t_minus_2_close * 100`。

**Humanizer必须在cron prompt中显式执行**（2026-05-22教训）：cron prompt中加显式步骤`python3 humanize_auto.py <文件> --inplace`
**to_docx可靠调用**：`references/to_docx-reliable-usage.md`（2026-06-04：管道模式在execute_code中静默失败，改用直接import调用）
33. **数据缺口必须在报告正文中标注**（2026-06-03教训）：新闻超时/北向缺失/pool_state为空时，不能沉默跳过章节，必须在对应段落中标注缺口。详见`references/data-gap-handling.md`。
33. **ETF池管理与个股池独立**：etf_notes和stock_notes是context中独立字段，ETF池有差异化止损、折溢价检查、流动性门槛
34. **amadeus_emotion.py过期检测已完善**（2026-05-21更新）：v3.0补齐load_market_extra()过期检测，三数据源过期状态均注入stale_warnings字段
35. **无交叉数据验证**：脚本层各数据源独立采集，没有自动对比机制。review subagent不做数值交叉验证。
36. **板块资金流单位待验**：同花顺返回值可能是万元非亿元，至今未交叉核验。
37. **AKShare fund_etf_spot_em()慢但数据全**：~27秒获取1467只ETF全量数据。日常scan用Sina API（秒级），详细风险检查才调AKShare
38. **ETF入池来源**：个股池入池靠stocks_mentioned字段，ETF入池靠sectors字段映射到板块→ETF代码表
39. **humanizer篡改事实数据**（2026-05-27发现）：`humanize_auto.py --inplace`会篡改数字、股票代码、数据等级。修复：humanize后必须校验关键数据，发现篡改立即回滚。详见`references/humanizer-factual-errors.md`。
40. **安全扫描阻止pipe到python3**：cron job中`cat file | python3 script.py`会被`tirith:pipe_to_interpreter`拦截。**最佳替代**：用shell重定向 `python3 script.py args < input.md`（实测2026-05-29通过）。`exec(open())`模式因`__file__`未定义不可用。
41. **腾讯API返回GBK编码**：qt.gtimg.cn返回中文是GBK编码，必须用`result.stdout.decode('gbk', errors='replace')`
42. **Gateway重启诊断**（2026-05-28教训）：`restart_gateway.sh`被系统cron每天触发6次导致频繁打断。修复：脚本内时间门控`if [ "$HOUR" != "03" ]; then exit 0; fi`。详见`references/gateway-cron-troubleshooting.md`。
43. **Tushare在venv中**：Tushare安装在hermes-agent venv，不在系统Python。120积分可用接口有限。
44. **data_validator.py异常值检测**：所有数据采集脚本共用。新脚本必须import并使用，不可跳过验证
45. **amadeus_emotion.py数据格式不匹配**：读`limit_up_stocks`中`连板数`字段不存在（实际在`lianban[].board_count`），读`index_data.volume`不存在。已修复：新增load_market_extra()
46. **AKShare stock_zh_a_spot()瞬时故障**：偶尔只返回80只股票（应5000+）。建议：采集后校验`len(df) > 1000`，否则重试或降级
47. **integrate-news不自动入池**（2026-05-21修复）：原只生成候选不调add_stock()，导致6天只退不进。已修复：自动调用add_stock+过滤条件
48. **Cron任务撞限流**（2026-05-22大规模复盘）：14个job中7个被限流。修复：间隔≥10分钟，Discord为主推送渠道。详见`references/cron-schedule-optimized.md`。
49. **数据质量等级制度**（2026-05-21新增）：data_quality.py统一评估8项核心数据，等级低于C+必须加降级警告，D/F级不得进入正式胜率统计
50. **报告必须标注数据来源**（2026-05-21新增）：每个数据点标明来源类型，禁止web_search/LLM推理数据伪装成结构化接口数据
51. **pool_manager.py数据源降级梯队**（2026-05-21新增）：4级降级：新浪→腾讯API→AKShare→Ashare。每级只处理上一级缺失股票
52. **复盘自动改进闭环**（2026-05-21新增）：收盘复盘每次提取改进动作→保存到improvement_pending.json→下期验证。连续两天未完成标为🔴严重违规
53. **备份job改local保存**（2026-05-21新增）：3个容错备份job的deliver从origin改为local，渠道级限流备份照样被挡，主job失败时手动补发
54. **pool_manager.py remove_stock OCIFQ误拦**（2026-05-28修复）：`remove_stock`被`ocifq_enforce.py`注入OCIFQ检查导致退池被拒。铁律：OCIFQ检查只应用于add_stock，不应用于remove_stock。
55. **情绪温度市场宽度因子阈值跳跃**（2026-05-28修复）：改用连续函数`width_score = min(25, zt/120*25)`，有真实上涨家数时优先用breadth_pct
56. **Humanizer双重存在**（2026-05-28梳理）：humanize_auto.py（规则引擎）和humanizer-zh SKILL.md（参考规则库）是两套东西。to_docx.py内建调用humanize_auto.py
57. **amadeus_emotion.py市场宽度用proxy值**（2026-06-03发现）：`市场宽度`维度用`pools.limit_up_count`（从lianban[]统计的66只）而非`market.limit_up`（新浪返回的107只）。差异原因：pools只统计当日连板/首板中涨停的，market包含所有收盘涨停股。效果：宽度分数偏低（13.8/25 vs 可能的20+/25）。如果需要更准确的情绪温度，应改用`market.limit_up`作为宽度因子输入。
57. **低分报告无自动改进闭环**（2026-05-21发现）：评分<60时自动提取扣分项写入改进清单，下期必须验证
58. **做任务必须汇报结果**（行为规则）：做完不说话=违规。即使被中断也要说明执行程度
59. **类推检查**（行为规则）：发现某模块有某种机制时，必须主动检查同类模块是否也有
60. **修改后必须立即测试**（2026-05-24用户纠正）：任何脚本/配置/cron修改完成后，必须当场运行测试确认生效
61. **审计脚本必须审计实际端点**（2026-05-24发现）：从配置文件读取实际端点，不能硬编码。provider是小米MiMo中转+DeepSeek直连
62. **/new不清理数据库旧消息**（2026-05-24发现）：session ID固定，/new只重置上下文。监控脚本必须按时间窗口统计
63. **numpy类型JSON序列化**（2026-05-24反复出现）：所有ML结果保存必须用自定义NumpyEncoder转换np.int32/float32/bool_
64. **yfinance限流**（2026-05-24发现）：连续50+只触发HTTP 429。应对：每5只sleep 0.5秒，三源互备
65. **集成模型比单模型提升27%+**（2026-05-24验证）：LightGBM+XGBoost简单平均集成，AUC大幅提升
66. **v3.5 AUC数据泄露**（2026-05-25发现）：0.7785是在全量训练数据计算的，正确交叉验证结果是v4.4的0.6365
67. **ML训练数据源优先级**（2026-05-25验证）：yfinance（最优）> Tushare Pro > AKShare（严重限流）
68. **ML训练配置最佳实践**（2026-05-25验证）：n_estimators=500, lr=0.03, max_depth=6, StandardScaler+TimeSeriesSplit
69. **报告模板量化信号层**（2026-05-24升级）：权重ML30%+因子25%+技术20%+情绪15%+资金10%
70. **特征质量>数据量**（2026-05-25验证）：v4.0用54万样本+14特征AUC仅0.59，v3.5用7.6万样本+44特征效果好得多
71. **AKShare不可作主数据源**（2026-05-25反复验证）：频繁RemoteDisconnected。ML训练必须用Tushare Pro作主数据源
72. **Tushare限流需sleep 0.35s**（2026-05-25发现）：批量下载必须加延迟，股票列表必须本地缓存
73. **10年旧数据可能有害**（2026-05-25验证）：2016年与2026年市场规律差异大，3-5年数据足够
74. **选股必须OCIFQ+ML双轨**（2026-05-25主人纠正）：六维评分=OCIFQ(70%)+ML(30%)
75. **Tushare daily_basic限流1次/小时**（2026-05-25发现）：ML训练基本面数据必须用yfinance info（无限流）
76. **SHAP特征筛选过度**（2026-05-25验证）：从69筛到50个去掉了16个有用特征，AUC反降。建议保留≥80%特征
77. **OOM分批训练**（2026-05-25验证）：733只股票全量训练需3.4GB，服务3.6GB被OOM杀掉。解决：分批200只+gc.collect()
78. **Pandas concat重复列**（2026-05-25修复）：extract_fundamental_features和create_market_cap_features都创建相同列，concat报错。已去掉重复调用
79. **yfinance数据类型混用**（2026-05-25修复）：yfinance info返回值可能是字符串，用pd.to_numeric(col, errors='coerce')强制转换
80. **Cron script路径必须包含子目录**（2026-05-25修复）：amadeus_watcher.py在scripts/amadeus/下，cron的script应为`amadeus/amadeus_watcher.py`
81. **禁止只用ML分析股票**（2026-05-25用户纠正）：必须使用完整的OCIFQ+ML六维评分体系，ML只占30%。使用`ocifq_ml_selector.py`整合脚本
82. **Cron限流规则强化**（2026-05-26教训）：收盘后任务密集排布，盘中异动改为每小时。Discord已配置为主推送渠道
83. **收盘复盘v3模板**（2026-05-27升级）：新增30秒速读/预测命中率/规则系统R-xx/五级分类/继承项/数据源标注。详见`templates/review_template.md`
84. **amadeus_news_scanner.py频繁超时**（2026-05-29验证）：`scan --json`（120s超时）和`hotspots`（60s超时）在cron上下文中经常失败。降级策略：直接从东方财富/财联社网页抓取热点，或跳过新闻板块在报告中标注"新闻采集超时"。不要无限等待新闻脚本。
85. **amadeus_realtime.py不支持逗号分隔批量查询**（2026-05-29发现）：`amadeus_realtime.py 601138,300502,002475`返回"数据不足30日"错误。应逐只查询或用空格分隔。
86. **决策日志验证规则**（2026-05-30新增）：收盘复盘必须验证decision_log.json中pending预判。大盘方向±0.2%阈值，板块前1/3命中，个股方向一致命中。滚动20次命中率<50%触发改进闭环。详见self-improvement skill Section十七。
87. **Cron prompt从jobs.json提取需特殊处理**（2026-05-30发现）：`~/.hermes/cron/jobs.json`中prompt字段含unicode转义（`\uXXXX`），直接`json.loads`会因嵌套引号失败。正确方法：写Python脚到文件→逐字符扫描找字符串边界→`json.loads('"' + raw + '"')`解码。详见`references/cron-prompt-extraction.md`。
88. **read_file带行号前缀**（2026-06-02发现）：`read_file`返回格式`LINE_NUM|CONTENT`，在execute_code中解析JSON需先用`line.split("|", 1)[1]`去掉行号。**更简单的方法**：用`terminal("cat file")`读取JSON文件，返回纯内容可直接`json.loads`。
89. **amadeus_realtime.py多只股票输出被覆盖**（2026-06-02发现）：`amadeus_realtime.py 600487 000960`只返回最后一只的完整数据，前面的被覆盖。正确用法：逐只调用或检查`realtime_*.json`的stocks字典中是否包含所有请求的股票。
90. **execute_code中terminal返回值格式**（2026-06-02发现）：`terminal("cat file")`返回`{"output": "...", "exit_code": 0}`，output是纯字符串可直接`json.loads`。但需注意如果命令失败（exit_code!=0），output可能含错误信息不是JSON。
91. **东财API限流铁律**（2026-06-03验证）：所有eastmoney.com请求必须走`em_get()`统一入口（1s间隔+随机抖动+会话复用）。push2.eastmoney.com不稳定（偶尔502），datacenter-web.eastmoney.com稳定。数据源优先级：腾讯/同花顺（不封IP）> 东财datacenter（有风控）> 东财push2（不稳定）。
92. **外部数据工具集成方法论**（2026-06-03总结）
93. **to_docx.py管道在execute_code中静默失败**（2026-06-04发现）：`cat file | python3 to_docx.py`在execute_code环境中可能不生成文件、无输出、无报错。**可靠替代**：直接Python import调用`md_to_docx(content, title, path)`。调用后必须`ls -la`验证文件生成。
94. **amadeus_emotion.py --json被误解析为日期**（2026-06-04发现）：`--json`参数在某些上下文中被脚本当作日期字符串处理，导致输出含"使用2026-05-18的数据"警告且数据过期。解决：检查emotion脚本的参数解析逻辑，或改用`python3 -c "import amadeus_emotion; ..."`直接调用。：①下载SKILL.md理解覆盖范围 ②逐端点实测（写脚本+记录状态/延迟/质量） ③对比现有系统识别重叠/互补/独占 ④只集成独占+互补端点 ⑤创建补充skill（独立SKILL.md+CLI脚本） ⑥更新工作流（新Agent/升级现有/并行架构） ⑦更新报告模板。详见`pantalone/references/a-stock-data-integration.md`。

## ML模拟盘验证系统（2026-05-25新增）

### 系统架构

| 脚本 | 功能 | 用法 |
|------|------|------|
| `ml_simulation.py` | 模拟交易 | `--buy/--sell/--check/--report/--trades` |
| `ml_sim_daily_check.py` | 每日检查 | 自动生成状态报告 |
| `ml_backtest.py` | 历史回测 | `--stocks <代码> --start 2024-01-01` |
| `ocifq_ml_selector.py` | 六维评分 | `--stocks <代码> --ml-file <文件>` |

### 交易规则

| 规则 | 设定 |
|------|------|
| 买入条件 | ML评分 > 60 |
| 卖出条件 | ML评分 < 40 |
| 止损 | -5% |
| 止盈 | +10% |
| 最长持仓 | 5天 |
| 最多持仓 | 5只 |
| 单笔金额 | 10万 |

### 定时任务

| 任务 | 时间 | Job ID |
|------|------|--------|
| ML每日信号预测 | 15:30 | ad58c2202a81 |
| ML模拟盘检查 | 16:00 | 0cb6066c305b |
| 止损自动监控 | 15:00 | f1a1b0d03cad |

### 回测验证流程

```bash
# 回测2024年至今（2年+数据）
python3 ~/.hermes/scripts/amadeus/ml_backtest.py --stocks 600519,000858,300750 --start 2024-01-01
```

**回测价值**：
- 验证ML信号在不同市场环境下的表现
- 发现模型在牛市/熊市/震荡市的有效性差异
- 优化交易规则（止损、止盈、持仓天数）
- 增强训练效果（用回测结果反馈给模型）

### 数据存储

- 交易记录：`~/.hermes/cache/amadeus/ml_simulation/trades.json`
- 每日报告：`~/.hermes/cache/amadeus/ml_simulation/daily_report.json`
- 回测结果：`~/.hermes/cache/amadeus/ml_backtest/`

### ML模型本质说明

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

## ⚠️ 报告生成陷阱（2026-05-25）

**问题**：cron job中agent先生成报告再用patch修改章节名/内容，导致字符串不匹配（如用"池别汇总"代替实际的"观察池自动管理"）。

**铁律**：
1. **报告必须一次性写入完整内容，禁止生成后patch修改**
2. cron prompt中必须**明确列出每个章节的精确名称**，并加"禁止使用XXX"提示
3. 如果必须修改已写入的文件，先用read_file确认实际内容后再patch
4. 章节名必须与模板完全一致（closing_report_v3.5.md中的"观察池自动管理"，不是"池别汇总"）

## 报告格式规范

### 盘前早报
大局观四维度(指数/情绪/题材/消息) → 题材三项检查 → 排除方向 → 模拟盘具体化 → 操作纪律

### 午间复盘
市场定性 → 早盘预案验证(评分100) → 观察池表现 → 模拟台账 → 下午计划

### 收盘复盘
市场定性 → 板块资金流分析 → 预测验证(100分) → 观察池验证 → 模拟台账 → 成功/失败/优化 → 综合评分(6维度100分)

## Cron报告架构（v3.4 并行delegate_task）

**关键规则**：cron任务必须在`enabled_toolsets`中包含`delegation`，否则delegate_task静默不可用。

### 4步流程（2026-05-15端到端验证通过）
1. **加载上下文**：amadeus_context.py + amadeus_sim_integrate.py + amadeus_data.py
2. **并行数据采集**：`delegate_task(tasks=[...])` 批量调subagent并行
   - ⚠️ **delegate_task batch上限3个**，5个subagent必须分2批（3+2）
   - 第1批：market_data + technical + macro（~5分钟）
   - 第2批：theme + risk（~3分钟）
   - ⚠️ amadeus_sector_flow.py不存在，板块资金流数据通过amadeus_data.py获取
3. **综合生成报告**：汇总subagent结果 + 上下文 → 按模板生成报告
   - 必须包含完整模拟盘持仓（所有持仓，不只是1只）
   - 预测必须量化概率（如60%/25%/15%），不能只说方向
4. **独立审查**：`delegate_task` 调review（不可自己审查，不可跳过）
   - 审查发现critical→必须修正后重新审查
   - 实测：第1轮发现仓位数据矛盾（38%vs6.26%）→修正→第2轮74分通过

### 8个subagent（3批并行）

**第1批并行（3个）：**
| subagent | 职责 | toolsets | 脚本 |
|----------|------|----------|------|
| market_data | 情绪温度+板块资金流+大盘信号+**北向分钟流** | terminal | amadeus_emotion.py, amadeus_sector_flow.py, amadeus_market_filter.py, **a_stock_data_supp.py north** |
| **capital** | **龙虎榜席位+融资融券+大宗交易+北向资金** | terminal | **a_stock_data_supp.py lhb/rzrq/dzjy/north** |
| macro | 外围市场+宏观环境 | terminal, web | amadeus_external.py |

**第2批并行（3个）：**
| subagent | 职责 | toolsets | 脚本 |
|----------|------|----------|------|
| theme | **同花顺热点归因**+行业排名+新闻+题材 | terminal, web | **a_stock_data_supp.py hot/hyph**, amadeus_news_scanner.py |
| financial | 财报分析+**分红送转** | terminal, web | amadeus_financials.py, **a_stock_data_supp.py fhzz** |
| technical | MA/RSI/MACD/布林带/支撑压力 | terminal | amadeus_realtime.py, amadeus_indicators.py |

**第3批（依赖前两批）：**
| subagent | 职责 | toolsets | 脚本 |
|----------|------|----------|------|
| risk | 排雷扫描+**筹码分析(股东户数/解禁/大宗)** | terminal | amadeus_screening.py, **a_stock_data_supp.py gdrs/jxjj/dzjy** |
| research | **研报评级+公告**（按需启用） | terminal, web | **a_stock_data_supp.py report/gonggao** |

### ETF分析流程（v3.4新增，2026-05-17）
| subagent | 职责 | toolsets | 文件 |
|----------|------|----------|------|
| ETF Agent | 9类分类+25字段分析+A-E评级+A/B/C池+18风险检查+OCIFQ持仓评估 | terminal, web | subagents/etf.md |
| ETF Reviewer | 类型/数据/折溢价/触发失效/仓位约束+OCIFQ审查 | terminal, web | subagents/etf_reviewer.md |

**流程**：ETF Agent → ETF Reviewer → Risk Agent（最终否决权）→ Report Agent
**模板**：`templates/etf_analysis.md`
**数据源**：eastmoney fund API（稳定）优先于AKShare fund_etf_hist_em（连接不稳）
**评级体系**：A(≥8分)/B(≥6)/C(≥4)/D(≥2)/E(<2) — 基于规模/成交额/折溢价/费率/成立年限

**ETF OCIFQ适配（v3.5新增，2026-05-21）**：
评估ETF前十大持仓公司的OCIFQ均分：
- 均分≥80 → ETF质地优秀，优先推荐
- 均分70-79 → ETF质地良好，可配置
- 均分<70 → ETF质地一般，谨慎配置
- 行业集中度>40%的ETF需验证行业利润断层（I维度）
- 前十大持仓中有≥3家满足财务三爆（F维度）→ ETF评级+1

**⚠️ ETF重叠检测（2026-06-02新增）**：
持仓中有多个ETF时必须检查重叠度。常见重叠组合：
- 科创50ETF ∩ 科创芯片ETF：科创板芯片是科创50核心权重，持有两个=同一方向押两次
- 半导体设备ETF ∩ 科创50ETF：北方华创、中微公司同时出现在两个ETF中
- 创业板ETF ∩ 新能源ETF：宁德时代、阳光电源重叠
检测方法：对比前十大持仓，重叠>3只需警告用户合并。

### 审查规则
- 必须用delegate_task，不可自我审查
- score≥70且无critical→通过
- score<70或有critical→修改后重审（最多1轮）
- 仍不通过→标注"⚠️ 审查未完全通过"后发送

## 自我改进

详细规则见 `self-improvement` skill。

### 工程纪律（2026-05-24新增）

**修改后必须立即测试**：任何脚本/配置/cron修改完成后，必须当场运行测试确认生效，不能说"下次会生效"。这是基本工程纪律。违反案例：修改了check_session_size.py但说"下次cron会生效"，被主人纠正。

**数据脚本修改后必须运行QA闭环**：
```bash
# 格式验证（不依赖网络）
python3 -c "import json; json.load(open('file.json'))"
# 功能验证（依赖网络）
python3 script.py --test
```

### Cron报告生成纪律（2026-05-25新增）

- **一次性写入，禁止patch** — cron报告prompt必须明确"一次性写入完整报告，不要后续patch修改"
- **强制章节名** — prompt中用加粗标注必须使用的章节名，禁止用其他名称（如禁止"池别汇总"，必须用"观察池自动管理"）
- **详细模式** — `references/cron-report-patch-failure-pattern.md`

### ML训练纪律（2026-05-25新增）

- **缓存非空才写入** — 数据获取函数的缓存逻辑必须验证数据非空才写入，空结果缓存是"静默失败"
- **单实例训练** — 训练脚本启动前检查是否有同名进程在跑，避免并发竞争
- **stdout无缓冲** — 训练脚本用`python3 -u`或添加`sys.stdout.flush()`
- **详细模式** — `references/v5-training-pitfalls-v2.md`（2026-05-25更新：Tushare限流/SHAP过度筛选/OOM分批/数据类型混用）

### 向量搜索集成（2026-05-24新增）

session_search已集成向量语义搜索，支持"清除聊天记录"→"重置对话"的语义匹配。

**组件**：
- chromadb 1.5.9（向量数据库）
- sentence-transformers 5.5.1（嵌入模型：paraphrase-multilingual-MiniLM-L12-v2）
- torch 2.12.0+cpu

**索引新消息**：
```bash
python3 ~/.hermes/scripts/vector_search.py index --limit 100
```

**搜索测试**：
```bash
python3 ~/.hermes/scripts/vector_search.py search "清除聊天记录"
```

**存储路径**：`~/.hermes/cache/vector_db/`

**原理**：session_search_tool.py已修改，FTS5关键词搜索后自动执行向量搜索并合并结果。向量搜索能理解语义相似性（如"清除聊天记录"≈"重置对话"），弥补FTS5字面匹配的不足。

### 核心机制
1. 每次复杂任务完成后必须复盘（触发条件见skill）
2. 错误必须归类（10类错误体系）
3. 高频任务必须沉淀模板
4. 核心能力建立测试集
5. 四类资产持续更新（流程/模板/测试/经验）

### 本次会话（2026-05-15）审计发现的5个严重问题
1. 🔴 修改cron未确认（违反SOUL.md 15.2）→ 已修复：SOUL.md明确prompt/toolsets/schedule均需确认
2. 🔴 单轮多任务（违反SOUL.md 15.4）→ 已修复：memory强化规则
3. 🔴 压缩摘要不可信 → 已修复：memory强化"压缩后验证关键文件"
4. 🔴 工具调用重复浪费token → 已修复：memory强化"首次读取后缓存"
5. 🔴 自己审查自己 → 已修复：8个cron加delegation+prompt强制delegate_task

### 复盘格式
```
【任务复盘】
1. 本次任务目标：
2. 实际完成情况：
3. 用户是否满意：
4. 出现的问题：
5. 问题归因：
6. 可沉淀经验：
7. 下次执行应调整：
8. 是否需要更新模板/规则/测试集：
```

## Research Agent

受AI Scientist-v2启发。引擎：`amadeus_research.py`(680行)。5角色评审（Bull/Bear/Quant/Macro/Contrarian）。
用法详见 `references/code-examples.md`。架构详见 `references/ai-scientist-v2-architecture.md`。

## 已安装扩展

| 扩展 | 用途 |
|------|------|
| humanizer-zh | 中文去AI痕迹 |
| amadeus-chanlun | 缠论形态识别 |
| amadeus-sentiment | 情绪量化 |
| amadeus-valuation | DCF/DDM/PE-Band |
| amadeus-risk | VaR/CVaR/蒙特卡洛 |
| amadeus-sector-rotation | 行业轮动 |
| amadeus-earnings | 盈利预测 |
| amadeus-behavioral | 行为金融 |
| amadeus-seasonal | 日历效应 |
| Tavily | AI搜索1000次/月 |
| Tushare | A股数据API |

## Humanizer集成（全自动，报告发送前必做）

**自动处理**：`to_docx.py` 已内建humanizer，docx转换时自动去AI痕迹。
**手动处理**：摘要文本发送前运行 `python3 ~/.hermes/scripts/amadeus/humanize_auto.py <报告文件> --inplace`
**SKILL.md参考**：`~/.hermes/skills/writing/humanizer-zh/SKILL.md`（8424⭐，深度润色参考规则库）
**⚠️ 双重存在**：humanize_auto.py（规则引擎，5/22安装）和humanizer-zh SKILL.md（参考规则库，5/28安装）是两套东西。to_docx.py内建调用humanize_auto.py。SKILL.md作为深度润色参考。

### 使用方法
```bash
# 自动处理文件（原地修改）
python3 ~/.hermes/scripts/amadeus/humanize_auto.py <报告文件> --inplace

# 管道模式（stdin→stdout）
cat report.md | python3 ~/.hermes/scripts/amadeus/humanize_auto.py --stdin

# 检测AI痕迹分数（仅检测，不修改）
python3 ~/.hermes/scripts/amadeus/humanizer_report.py <报告文件> --check
```

### AI痕迹分数标准
- **0-30分**：优秀，无需处理
- **30-50分**：良好，可选择性处理
- **50-70分**：需要改进，建议humanizer处理
- **70-100分**：严重AI痕迹，必须处理

### 检测的AI模式
1. **内容模式**：夸大象征、宣传语言、模糊归因、挑战展望
2. **语言模式**：AI词汇、否定排比、三段式
3. **风格模式**：破折号过多、粗体过度、表情符号
4. **交流模式**：谄媚语气、知识截止

### 报告生成流程（全自动）
1. **生成报告**：按模板生成完整报告
2. **摘要humanizer**：`python3 humanize_auto.py <报告文件> --inplace`
3. **⚠️ humanize后必须校验**：humanizer可能篡改事实数据（数字/股票代码/数据等级），详见`references/humanizer-factual-errors.md`
4. **docx转换**：`to_docx.py`自动内建humanizer，无需额外步骤
5. **发送报告**：摘要+docx附件

### Humanizer处理示例
```python
# 如果AI痕迹分数>50，用delegate_task处理
delegate_task(goal="用humanizer-zh skill处理以下文本，去除AI痕迹：\n\n{报告内容}", 
              toolsets=["terminal", "file"])
```

---

## 报告格式铁律（2026-05-27，用户明确要求）

**⚠️ 用户对报告格式不满：参考文档105行，我们的输出300+行。必须精简。**

1. **行数限制**：早报80-120行，午间60-100行，收盘100-150行
2. **短段落+要点列表为主**，减少大表格使用
3. **结论先行**：每段第一句就是结论
4. **重点数据用粗体**，不用表格也能看清
5. **删掉废话**：禁止"经过分析"、"需要注意的是"、"总的来说"这类过渡句
6. **同类信息合并**，不要逐条罗列
7. **数字精确**：涨跌用具体点位和百分比，不用"小幅"、"大幅"

**好的写法**：白酒板块独秀，19涨0跌(+3.37%)，防御属性凸显。
**差的写法**：（列20行大表格+逐条分析+反复总结）

## Cron推送架构（2026-05-27重构）

**主推送渠道**：Discord（#常规频道，ID: 1509184957245948014）
**微信**：仅保留session连接，不再作为推送目标
**原因**：微信iLink渠道级限流，14:00后6个任务全部被挡

| 时间 | 任务 | 行数 | 内容 |
|------|------|------|------|
| 08:15 | 早间速报（补充版） | 20-30行 | 美股+隔夜+开盘预判 |
| 12:20 | 午间复盘 | 60-100行 | 半日复盘+预案验证 |
| 15:30 | 收盘复盘 | 100-150行 | 完整复盘+**昨晚预测验证** |
| **21:00** | **晚间复盘+次日预测** | 100-150行 | 复盘+**潜力股选股** |

**预测验证闭环**：
- 晚间选出潜力股 → 写入inheritance_latest.md
- 次日收盘复盘 → 逐条验证 → 计算命中率x/y=z%
- 命中率低 → 分析原因 → 改进选股逻辑

## 报告模板清单（2026-05-27更新）

| 模板 | 文件 | 主要改进 |
|------|------|---------|
| **早间速报** | cron prompt | 20-30行，只补充美股+隔夜 |
| **午间复盘** | `templates/midday_template.md` | 60-100行，精简版 |
| **收盘复盘** | `templates/review_template.md` | v3: 30秒速读+预测验证+规则系统+五级分类+继承项 |
| **晚间复盘** | cron prompt | 100-150行，含次日预测+潜力股选股 |

### 量化信号层内容

**早盘模板新增**：
- ML模型信号（LightGBM/XGBoost评分）
- 因子信号（IC值、等级、今日表现）
- 技术指标量化（RSI/MACD/布林带位置/ATR）
- 量化信号汇总（加权评分：ML30%+因子25%+技术20%+情绪15%+资金10%）
- 宏观数据层（全球市场+商品价格+宏观事件日历）

**午盘模板新增**：
- ML信号实时验证（信号准确度追踪）
- 因子表现追踪（IC变化、因子有效性）
- 技术指标变化（RSI/MACD/布林带位置变化）
- 量化信号汇总更新（早盘→午盘变化）

**收盘模板新增**：
- ML信号回测（准确率、平均收益）
- 因子表现回测（IC、多空收益、因子轮动信号）
- 技术指标验证（预测准确度）
- 量化信号综合评估（各维度准确度、改进建议）
- 明日预测新增ML信号和因子信号维度

### 使用说明

1. **早盘**：运行 `python3 pantalone_tools_hub.py --comprehensive --stock xxx` 获取量化信号
2. **午盘**：更新量化信号，验证早盘信号准确度
3. **收盘**：回测验证所有信号，统计准确率，生成改进建议

---

市场有风险，投资需谨慎! 以上仅作为教学案例，不作为投资建议!
