# A股机构研报 Subagent

> **数据源**: 东财研报中心 `reportapi.eastmoney.com/report/list`（免 key，大陆直连已验证）
> **脚本**: `scripts/institutional_reports.py`（Pantalone 自带，无第三方依赖）

## 执行方式

通过 `delegate_task` 调用，或在研究流程中直接运行脚本：

```bash
python3 scripts/institutional_reports.py 600519 --days 180
python3 scripts/institutional_reports.py 600519 --days 180 --json
python3 scripts/institutional_reports.py 300750 --download /tmp/reports
python3 scripts/institutional_reports.py --market --limit 20
```

脚本输出结构化摘要：研报列表、评级分布、评级分歧、评级变化、EPS 预测区间、近 30 天覆盖缺口提示；`--json` 输出机器可读版本。

## 职责

1. 采集个股近 N 天（默认 180）的券商研报列表；
2. 标准化评级口径（买入/增持/持有/中性/减持/卖出/回避/区间操作），保留原始评级字段；
3. 统计评级分布、检测**评级分歧**（同时存在买入/增持与持有及以下）；
4. 提取评级变化（`lastRatingName → emRatingName`）并展示最近变化；
5. 汇总今年/明年 EPS 预测区间（不取平均掩盖分歧）；
6. 检测近 30 天覆盖缺口（标注“无近期机构覆盖”）；
7. 可选：下载研报 PDF（`--download DIR`，前 3 份）。

## 数据源要点

- `code` 必须为**裸6位代码**（如 `600519`）；`sh600519`/`SH600519`/`1.600519` 均返回空（2026-08-13 实测）；
- 字段：`title`/`orgSName`/`publishDate`/`emRatingName`/`sRatingName`/`lastRatingName`/`predictThisYearEps`/`predictNextYearEps`/`predictThisYearPe`/`predictNextYearPe`/`infoCode`；
- PDF 模板：`https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf`（实测返回 `application/pdf`）；
- 限流：脚本内置 1s 串行间隔；批量 >5 只时建议逐只调用或调整 `_MIN_INTERVAL`。

## 输出格式（摘要段，嵌入研究报告中）

```markdown
### 机构研报（近180天）
- 研报数：7
- 覆盖券商：国信证券, 山西证券, 西南证券, 交银国际证券, 群益证券, 东吴证券, 国金证券
- 评级分布：{'买入': 5, '增持': 2}
- 评级分歧：否
- 今年EPS预测区间：19.65 ~ 22.138
- 明年EPS预测区间：23.77 ~ 27.185
```

## 使用规则（红线）

1. 研报是**参考证据**，优先级低于：招股书 > 定期报告 > 官网 > 研报 > API；
2. 展示评级**分歧**（如中邮“买入” vs 群益“持有”），不得取平均或只报最乐观评级；
3. 引用必须注明券商、日期与评级，不得匿名“有机构看好”；
4. 评级变化（`lastRatingName → emRatingName`）比绝对评级更有信息量，优先展示；
5. 近 30 天无研报覆盖时，研究报告中标注“无近期机构覆盖”；
6. 单份研报目标价/EPS 不构成交易指令，操作建议需结合 OCIFQ、风控与合规审查。
