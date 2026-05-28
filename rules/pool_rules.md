# pool_rules.md — 观察池规则

## 观察股硬格式

```
代码 | 名称 | 池子 | 评级
1.观察理由
2.财报证据
3.长期逻辑
4.估值状态
5.技术位置
6.触发条件
7.失效条件
8.是否允许模拟盘
9.数据缺口
```

数据缺口>3项 → "仅观察，不进入模拟计划"

## 池子结构

| 池子 | 数量 | 定位 | 评级要求 |
|------|------|------|----------|
| A池 | 3-5只 | 长期价值 | A/B级 |
| B池 | 4-6只 | 价值-技术共振 | A/B/C级 |
| C池 | 3-5只 | 情绪样本 | C/D/E级 |
| D/E | 仅C池 | 纯题材票 | D/E级 |

## 模拟计划规则

以下任一条件成立则不生成模拟买入计划：
- 关键行情数据缺失
- 成交额缺失
- 涨停跌停缺失
- 个股价格缺失
- A/B池财报缺失
- 情绪温度估算且缺2项以上

→ "模拟盘：今日不触发，等待数据补全。"

## 默认观察池 v1.8.1（20只+，每次复盘动态更新）

**A池(长期价值)**：
- 600900 长江电力
- 600519 贵州茅台
- 000333 美的集团
- 600036 招商银行
- 600941 中国移动
- 601088 中国神华

**B池(价值-技术共振)**：
- 300124 汇川技术
- 002463 沪电股份
- 000063 中兴通讯
- 002475 立讯精密
- 300502 新易盛
- 601138 工业富联
- 300308 中际旭创
- 002334 英威腾
- 002281 光迅科技

**C池(情绪样本)**：
- 600396 华电辽能
- 002081 金螳螂
- 600726 华电能源
- 605006 山东玻纤
- 688008 澜起科技
- 300302 同有科技

## 观察股扩展规则

- 每次复盘前扫描市场，主动发现新候选，不固守默认池
- 通过涨停板、强势股池、成交额排名、换手率筛选新标的
- 新候选必须计算技术指标后再决定是否纳入
- B池新候选标准：RSI 40-70、非缩量新高、位置 30-85%、MACD多头
- C池新候选标准：连板股、题材龙头、换手>15%短线活跃股
- 超买+缩量+高位（RSI>75+量比<0.8+位置>90%）的新候选只放C池标注【赶顶信号】，不进B池

## 自动入池规则

| 条件 | 说明 |
|------|------|
| 新闻催化 | sentiment>=3 且与A股直接相关 |
| 排雷通过 | 5项排雷检查全部通过 |
| 技术达标 | RSI 40-70, 量比>1.0, 价格>MA20 |
| 板块匹配 | 映射到已知板块（半导体/AI/新能源/消费电子/汽车/农业/航空/金融/军工/医药） |
| 池子分配 | 基本面强→A池，技术共振→B池，情绪题材→C池 |

## 自动退池规则

| 条件 | 动作 | 时限 |
|------|------|------|
| 止损 | B池-5%, A池-8% | 立即 |
| 超时无触发 | C池>15天→退池, B池>30天→降级C | 每日检查 |
| 赶顶信号 | RSI>75+量比<0.8+位置>90% | 降级C |
| 基本面恶化 | ST/非标审计/质押>70% | 直接退池 |
| 板块退潮 | 连续3日资金净流出 | 标记观察 |
| 触发失效 | 失效条件达成 | 退池 |

## 新闻扫描器

**脚本**：`scripts/amadeus/amadeus_news_scanner.py`
**数据源**：东方财富(200条) + 财联社(20条) + 新浪(20条) + 同花顺(20条)
**功能**：自动采集→去重→情绪评分(-5~+5)→板块映射→个股提取→入池建议

```bash
# 全量扫描（输出JSON到缓存+stdout）
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py scan

# 只看重大利好/利空
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py hotspots
```

**输出缓存**：`~/.hermes/cache/amadeus/news_scan_YYYY-MM-DD_HHMM.json`

## 观察池管理器

**脚本**：`scripts/amadeus/amadeus_pool_manager.py`
**功能**：自动入池/退池/降级/止损/超时检测/赶顶检测/新闻整合

**自动执行命令**（推荐）：
```bash
# 一键自动执行：扫描退池+新闻入池+记录日志
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py auto
```

**日志文件**：`~/.hermes/cache/amadeus/pool_changes.log`（所有入池/退池操作自动记录）

```bash
# 查看池状态报告
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py report

# 扫描退池条件（仅扫描，不执行）
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py scan

# 执行scan的建议动作
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py apply

# 整合新闻入池（仅建议，不执行）
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py integrate-news

# 自动执行（scan退池+新闻入池+记录日志）← 推荐
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py auto

# 手动操作
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py add <代码> <池> "<理由>"
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py remove <代码> "<理由>"
```

## Cron调度

| 任务 | 时间 | 内容 |
|------|------|------|
| 新闻热点扫描 | 09:30/12:00/15:30 交易日 | 扫描重大利好/利空，推送到微信 |
| 观察池自动管理 | 16:00 交易日 | 退池检查+新闻入池+执行变更 |
| ETF池自动管理 | 16:05 交易日 | ETF退池检查+新闻入池+执行变更 |

## 注意事项

- 退池必须有明确理由，不能无故退池
- 新入池必须通过排雷检查
- 只推送重大利好/利空（sentiment>=4），一般新闻不推送

---

## ETF观察池管理器

**脚本**：`scripts/amadeus/amadeus_etf_pool_manager.py`
**功能**：ETF自动入池/退池/降级/止损/折溢价检查/流动性检查/18项风险扫描

**ETF类型与止损线**：

| ETF类型 | 止损线 | 入池级别 |
|---------|--------|----------|
| 宽基ETF | -6% | A池核心配置 |
| 红利/高股息 | -6% | A池核心配置 |
| 债券ETF | -3% | A池防守配置 |
| 黄金ETF | -10% | A池对冲工具 |
| 行业ETF | -8% | B池战术轮动 |
| 主题ETF | -8% | B池战术轮动 |
| QDII ETF | -10% | B/C池 |
| 商品ETF | -10% | B池 |
| 货币ETF | N/A | A池现金管理 |
| 风格ETF | -6% | A池核心配置 |

**执行命令**：
```bash
# 一键自动：扫描退池+新闻入池+日志
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_etf_pool_manager.py auto

# 查看ETF池状态
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_etf_pool_manager.py report

# 18项风险检查
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_etf_pool_manager.py risk <代码>

# 手动操作
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_etf_pool_manager.py add <代码> <池> "<理由>" [类型]
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_etf_pool_manager.py remove <代码> "<理由>"
```

**日志文件**：`~/.hermes/cache/amadeus/etf_pool_changes.log`
