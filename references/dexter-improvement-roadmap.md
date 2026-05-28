# Dexter & Dexter-A 改进路线图（2026-05-13研究）

## Dexter（virattt/dexter）
- GitHub: 25,486 Stars | TypeScript + Bun + LangChain
- 定位：终端金融研究Agent（美股为主）

### 值得借鉴的设计

| 设计 | 价值 | 实施难度 | 状态 |
|------|------|----------|------|
| SOUL.md（灵魂文档） | 给Agent价值观，不只是规则 | 1小时 | 待实施 |
| Scratchpad（草稿本） | 记录每步工具调用决策，可审计 | 2天 | 待实施 |
| 大结果持久化 | 工具结果存盘防爆context | 简单 | 已有基础 |
| Skills checklist格式 | 执行流程更可控 | 批量改造 | 待实施 |
| 三级搜索降级 | Exa→Perplexity→Tavily | 配置调整 | 待实施 |

### SOUL.md核心内容（可直接复用）
```
## 投资哲学（巴菲特+芒格）
- Price is what you pay, value is what you get
- Invert, always invert（逆向思维）
- Circle of competence（能力圈）
- Margin of safety（安全边际）
- 诚实优于舒适，实质优于表演
```

### 三层上下文管理
```
Microcompact    每轮触发，工具结果>8条或token>80K
  ↓             保留最近4条，其余替换为占位符
Memory Flush    写盘到.dexter/目录
  ↓
Full Compaction LLM总结压缩
  ↓
Truncation      保留最近N轮，其余丢弃
```

## Dexter-A（abrclano/dexter-A）
- fork自Dexter，dev分支71个文件改动
- 定位：Dexter的A股中国适配版

### 新增模块

#### 东方财富妙想API（5个工具）
- `eastmoney_mx_data` — A股结构化数据
- `eastmoney_mx_search` — 研报/新闻/公告搜索
- `eastmoney_mx_select_stock` — 自然语言选股
- `eastmoney_mx_selfselect` — 自选股管理
- `eastmoney_mx_stock_simulator` — 股票模拟器
- 配置：`MX_APIKEY` in .env
- API: `https://mkapi2.dfcfs.com/finskillshub`

#### Tushare Pro API（20+个工具）
- 行情：daily/daily_basic/stk_week_month_adj
- 财务：income/balancesheet/cashflow/fina_indicator
- 市场：moneyflow_hsgt(北向)/margin(两融)/block_trade(大宗)/limit_list(涨跌停)
- 事件：forecast(业绩预告)/express(业绩快报)
- 配置：`TUSHARE_TOKEN`（需2000积分）

#### A股分析技能（6步）
1. 识别分析对象与意图
2. 数据采集（多源验证）
3. 排雷检查（退市/质押/商誉/审计）
4. 估值分析
5. 技术面分析
6. 综合研判与输出

### 对Amadeus的优先改进
1. **东方财富妙想API接入** — 比AKShare更稳定，自带研报搜索（需API key）
2. **Tushare Pro接入** — 2000积分解锁完整财务数据（需token）
3. **A股排雷检查** — 系统化检查退市风险/质押/商誉（1天可做）
