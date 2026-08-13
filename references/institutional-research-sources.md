# 机构研报采集与使用流程（2026-08-13 实测）

> 数据源可用性全部经真实探针验证（2026-08-13），含中国大陆网络环境。
> 研报有利益冲突（券商与标的常有投行业务关系），**只作为参考证据，不单独决定建仓动作**。

## 一、A股机构研报（东财研报中心，免 key，已验证 HTTP 200）

### 1. 全市场最新研报

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
curl -sS -H "User-Agent: $UA" -H 'Referer: https://data.eastmoney.com/' \
  'https://reportapi.eastmoney.com/report/list?industryCode=*&pageSize=20&beginTime=2026-08-01&endTime=2026-08-13&pageNo=1&qType=0&code=*'
```

### 2. 个股研报（code 用**裸代码**，如 `600519`；`sh600519`/`SH600519`/`1.600519` 均返回空）

```bash
curl -sS -H "User-Agent: $UA" -H 'Referer: https://data.eastmoney.com/' \
  'https://reportapi.eastmoney.com/report/list?industryCode=*&pageSize=20&beginTime=2026-06-01&endTime=2026-08-13&pageNo=1&qType=0&code=600519'
```

### 3. 可用字段（实测存在）

| 字段 | 含义 | 实测值 |
|------|------|--------|
| `title` | 研报标题 | 需求根基稳固，市场化定价持续兑现 |
| `orgSName` | 券商 | 中邮证券 |
| `publishDate` | 发布日期 | 2026-08-12 00:00:00.000 |
| `emRatingName` | 东财评级（买入/增持/中性/减持/卖出） | 买入 |
| `sRatingName` / `lastRatingName` | 卖方评级 / 上次评级 | 买入 |
| `predictThisYearEps` / `predictNextYearEps` | 今年/明年 EPS 预测 | 69.76 |
| `predictThisYearPe` / `predictNextYearPe` | 今年/明年 PE 预测 | 19.42 / 18.71（中邮证券 600519） |

### 4. 使用规则

1. 多份研报并存时**展示评级分歧**（如中邮买入 vs 群益持有），不取平均掩盖分歧；
2. 目标价/EPS 预测须标注券商与日期，不得混用不同报告的数字；
3. 研报评级变化（`lastRatingName` → `emRatingName`）比绝对评级更有信息量；
4. 近 30 天无研报覆盖的个股，在研究报告中标注"无近期机构覆盖"。

## 二、美股机构观点（实测可用）

### 1. StockAnalysis.com（免费，可解析，已验证 HTTP 200）

```bash
curl -sS -H "User-Agent: $UA" 'https://stockanalysis.com/stocks/nvda/forecast/'
```

- 页面含 `Analyst Consensus`（如 "Strong Buy"）、平均目标价（如 $302.83）、一年预期涨跌幅；
- 含 `ratingBuy/ratingHold/ratingSell/ratingStrongSell` 计数；
- 解析：用 `re` 抓 consensus 段，或 BeautifulSoup 抓 forecast 表格；
- 注意：这是**聚合观点**，不含具体券商名，深度分析仍需财报原文。

### 2. SEC EDGAR（事实源，已验证 HTTP 200，10 次/秒限流）

```bash
curl -sS -H "User-Agent: research <your-email>" \
  'https://data.sec.gov/submissions/CIK0001045810.json'   # NVDA 的 CIK 需先查
```

- 10-K/10-Q/8-K 用 XBRL 提取；CIK 查询：`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=NVIDIA&type=10-K`（⚠️ 必须用公司全名或 CIK——用 ticker 如 NVDA 会返回 "No matching companies." 静默空结果）
- EDGAR 是**事实源**，不是观点源：用于验证研报数字，不用于获取目标价。

### 3. yfinance 大陆网络限制（2026-08-13 实测）

| 接口 | 状态 | 说明 |
|------|------|------|
| `fc.yahoo.com`（cookie/crumb） | ❌ TLS 被干扰 | yfinance 的 `info`/`financials`/`download` 均依赖它，大陆不可用 |
| `query1.finance.yahoo.com/v8/finance/chart/` | ✅ HTTP 200 | K线/历史行情可直接 curl，无需 cookie |
| yfinance 1.5.x | ❌ 强制 curl_cffi | macOS 上 TLS 报 `OPENSSL_internal: invalid library` |
| yfinance 0.2.54 | ⚠️ 部分可用 | 换 requests 后端，但 fc.yahoo.com 仍被干扰，`info` 不可用 |

**结论**：美股 K线用 `query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range=1mo&interval=1d`（curl 直接可用）；财务和评级用 SEC EDGAR + StockAnalysis.com。**不要依赖 yfinance 的 info/财务接口**。

## 三、研报使用红线

1. 研报是参考证据，优先级低于：招股书 > 定期报告 > 官网 > 研报 > API（记忆中的数据采集层次不变）；
2. 单份研报的目标价不构成交易指令；操作建议必须结合 OCIFQ、风控与合规审查；
3. 引用研报必须注明券商、日期和评级，不得匿名引用"有机构看好"；
4. 港股研报暂未验证（东财 `qType=1` 实测返回的是行业研报而非个股港股研报；辉立/致富等渠道未验证），需要时先探针再使用。

## 三-bis、自动化脚本（Pantalone 自带）

`scripts/institutional_reports.py` 封装上述 A 股研报接口，输出结构化摘要：

```bash
python3 scripts/institutional_reports.py 600519 --days 180          # 个股摘要
python3 scripts/institutional_reports.py 600519 --json              # JSON 输出
python3 scripts/institutional_reports.py 300750 --download /tmp/reports  # 下载PDF
python3 scripts/institutional_reports.py --market --limit 20        # 全市场最新
```

输出包含：评级分布、评级分歧检测、评级变化（`lastRatingName → emRatingName`）、
今年/明年 EPS 预测区间、近 30 天覆盖缺口提示。代码必须为裸6位代码；脚本内置 1s
东财限流。使用规则与上述红线一致（展示分歧、注明券商日期、不单独构成交易指令）。

## 四、验证记录（2026-08-13）

| 探针 | 结果 |
|------|------|
| 东财研报列表 API（code=*） | HTTP 200，返回东吴/中邮/华金 3 条真实研报 |
| 东财个股研报 API（code=600519） | HTTP 200，返回中邮"买入"+EPS 69.76、群益"持有"+EPS 71.98 |
| stockanalysis.com/stocks/nvda/forecast/ | HTTP 200，consensus "Strong Buy"，目标价 $302.83 |
| SEC EDGAR submissions API | HTTP 200 |
| yfinance 1.5.2（curl_cffi） | TLS 错误，不可用 |
| yfinance 0.2.54（requests） | fc.yahoo.com 被干扰，info 不可用 |
| query1.finance.yahoo.com chart API | HTTP 200（curl 直连） |
