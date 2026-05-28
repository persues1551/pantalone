# Amadeus 审计报告摘要（2026-05-14）

## 三个结构性缺陷

1. **规则写了但没执行（Execution Gap）**：模拟盘规则迭代v1→v2→v3，数据库零条记录。Subagent 11个Agent全是markdown文件。以文档替代实现。
2. **数据采集有但数据使用断裂（Data Pipeline Gap）**：RSI/MACD不写入JSON，板块资金流完全不采，排雷检查无脚本。
3. **文档体系自我膨胀（Documentation Inflation）**：3000+行markdown vs 不到2000行Python。

## 审计后创建/修改的文件

### 新建脚本
- `amadeus_screening.py` — 排雷扫描（ST/质押/商誉/审计/现金流）
- `amadeus_valuation.py` — 估值模型（PE-Band+分位数）
- `amadeus_market_filter.py` — 大盘环境四级过滤器（v2.0：涨停>80直接主升浪）
- `amadeus_buy_scorer.py` — 买入信号评分系统（满分100）

### 修改的脚本
- `amadeus_collect_all.sh` — 修复废弃引用+嵌入排雷/过滤/daily_update
- `amadeus_sim_integrate.py` — v2.0：实时价格+单票检查(max(25%,1手))+部分平仓
- `amadeus_indicators.py` — v2.0：RSI/MACD入JSON+WATCHLIST同步+禁止买入检查

### 修改的规则文件
- `rules/data_rules.md` — 涨停阈值区分板块+TODO清除
- `rules/risk_rules.md` — 买入规则+三层清仓(+12%/+20%/+30%)
- `workflow.md` — 金额统一+模拟盘步骤嵌入
- `templates/morning_template.md` — 金额统一+评分门槛
- `router.md` — 模型路由统一(mimo主力)+视觉路由修正
- `SKILL.md` — v3.1.0+description更新+模拟盘集成方法

### 新建/重写的Subagent文件
- `subagents/review.md` — 审查复盘型Subagent规则v3.2（397行）
- `subagents/protocol.md` — 降级为角色提示词模板库
- `subagents/checklist.md` — 降级为报告自检清单

## 防复发机制（12项全部有效）

1. cron自动调用daily_update
2. 实时价格获取（腾讯API）
3. 单票max(25%,1手)上限拦截
4. 总暴露70%上限拦截
5. 禁止买入条件自动检查（RSI>75/缩量/位置>90%）
6. WATCHLIST与pool_rules.md同步
7. 涨停阈值板块区分规则
8. cron报告强制调用sim status+daily_update
9. L3/L4任务强制审查流程（review.md v3.2）
10. collect_all.sh全流程（排雷+过滤+daily_update）
11. 模型路由统一（mimo主力/DeepSeek子agent）
12. Subagent降级为角色提示词模板库
