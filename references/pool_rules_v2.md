# pool_rules.md — 观察池规则 v2.0

## ⚠️ 核心原则（2026-06-08 重构）

**观察池是"逻辑实验场"，不是"热点收藏夹"。**

```
选股逻辑假设 → 入池观察 → 验证结果 → 修正逻辑 → 复利积累
```

**铁律：无逻辑不入池。** 入池必须填写：假设、催化剂、成功标准、失败标准、验证时间。

详见：`references/pool_philosophy.md`（完整哲学与规则）
管理脚本：`scripts/amadeus/pool_manager_v2.py`
验证日志：`cache/amadeus/pool_verify_log.json`

## 观察股硬格式（v2.0 更新）

```
代码 | 名称 | 池子 | 逻辑类型
1.逻辑假设（为什么选它？预期什么？）
2.催化剂（什么会驱动上涨？）
3.成功标准（什么算逻辑兑现？）
4.失败标准（什么算逻辑证伪？）
5.验证时间（什么时候验证？）
6.置信度（0-1）
7.财报证据
8.估值状态
9.技术位置
10.数据缺口
```

数据缺口>3项 → "仅观察，不进入模拟计划"

## 池子结构（v2.0 更新）

| 池子 | 定义 | 入池条件 | 止损线 |
|------|------|----------|--------|
| **A池** | 逻辑已验证的核心持仓 | 逻辑兑现+趋势良好 | -10% |
| **B池** | 逻辑进行中的观察池 | 有明确逻辑假设 | -5% |
| **C池** | 新逻辑的试验池 | 新入池，待观察 | -3% |
| **退池** | 逻辑证伪或止损触发 | 自动/手动退池 | - |

### 池子流动规则

```
新入池 → C池（观察期）→ B池（跟踪期）→ A池（核心持仓）
                                          ↓ 逻辑证伪/止损
                                        退池
```

## 逻辑类型与验证周期

| 逻辑类型 | 说明 | 验证周期 |
|----------|------|----------|
| **业绩驱动** | 预期财报超预期 | 1-3个月 |
| **行业周期** | 行业景气度上行 | 2-6个月 |
| **政策催化** | 政策利好落地 | 1-2个月 |
| **技术突破** | 新技术/新产品放量 | 2-4个月 |
| **估值修复** | 低估+催化剂 | 1-2个月 |
| **事件驱动** | 并购/重组/订单 | 事件落地后 |

## 入池模板

```json
{
  "code": "300502",
  "name": "新易盛",
  "pool": "B",
  "entry_date": "2026-06-08",
  "entry_price": 85.5,
  "logic": {
    "type": "业绩驱动",
    "hypothesis": "1.6T光模块放量，Q2营收有望超预期",
    "catalyst": "AI算力需求持续，海外大厂扩产",
    "success_criteria": "Q2营收增速>30%，毛利率>35%",
    "failure_criteria": "营收增速<10%，或订单取消",
    "verify_date": "2026-08-15",
    "confidence": 0.7
  },
  "source": "OCIFQ选股",
  "status": "观察"
}
```

## 验证规则

### 验证结果分类

| 结果 | 定义 | 处理 |
|------|------|------|
| ✅ **逻辑兑现** | 成功标准达成 | 升级到A/B池，记录成功模式 |
| ⏳ **逻辑进行中** | 还没到验证时间 | 继续观察 |
| ⚠️ **逻辑偏移** | 部分达成，部分偏离 | 分析原因，调整预期 |
| ❌ **逻辑证伪** | 失败标准达成 | 退池，记录失败原因 |
| 🔄 **逻辑修正** | 新信息改变假设 | 更新逻辑，重置验证时间 |

### 验证模板

```json
{
  "code": "300502",
  "verify_date": "2026-08-15",
  "result": "逻辑兑现",
  "evidence": "Q2营收+45%，毛利率38%，超预期",
  "lesson": "AI算力需求确实带动光模块放量，逻辑成立",
  "action": "升级B池，继续持有"
}
```

## 复盘规则

### 周复盘（每周五收盘后）

1. **检查观察池**：哪些股票到了验证时间？
2. **验证逻辑**：成功/失败/偏移？
3. **记录教训**：为什么对？为什么错？
4. **更新规则**：是否需要调整选股逻辑？

### 月复盘（每月最后一个交易日）

1. **统计胜率**：本月验证了多少？成功多少？
2. **分析模式**：哪些逻辑类型胜率高？
3. **优化体系**：调整入池标准、验证周期
4. **清理池子**：长期未验证的股票强制验证或退池

## 与OCIFQ的关系

OCIFQ是**选股工具**，观察池是**验证工具**。

```
OCIFQ选股 → 逻辑假设 → 观察池验证 → 修正OCIFQ权重
```

## 模拟计划规则

以下任一条件成立则不生成模拟买入计划：
- 关键行情数据缺失
- 成交额缺失
- 涨停跌停缺失
- 个股价格缺失
- A/B池财报缺失
- 情绪温度估算且缺2项以上

→ "模拟盘：今日不触发，等待数据补全。"

## 自动退池规则

| 条件 | 动作 | 时限 |
|------|------|------|
| 止损 | B池-5%, A池-8% | 立即 |
| 超时无触发 | C池>15天→退池, B池>30天→降级C | 每日检查 |
| 赶顶信号 | RSI>75+量比<0.8+位置>90% | 降级C |
| 基本面恶化 | ST/非标审计/质押>70% | 直接退池 |
| 逻辑证伪 | 失败标准达成 | 退池 |

## 新闻扫描器

**脚本**：`scripts/amadeus/amadeus_news_scanner.py`
**数据源**：东方财富(200条) + 财联社(20条) + 新浪(20条) + 同花顺(20条)
**功能**：自动采集→去重→情绪评分(-5~+5)→板块映射→个股提取→入池建议

**⚠️ 已知问题**：脚本频繁超时（财联社API不稳定），降级策略见pitfall #84。

```bash
# 全量扫描（输出JSON到缓存+stdout）
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py scan

# 只看重大利好/利空
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_news_scanner.py hotspots
```

**输出缓存**：`~/.hermes/cache/amadeus/news_scan_YYYY-MM-DD_HHMM.json`

## 观察池管理器

### v2.0 管理器（推荐）

**脚本**：`scripts/amadeus/pool_manager_v2.py`
**功能**：逻辑验证驱动的入池/退池/验证检查

```bash
# 查看状态
python3 ~/.hermes/scripts/amadeus/pool_manager_v2.py status

# 检查待验证股票
python3 ~/.hermes/scripts/amadeus/pool_manager_v2.py verify

# 入池（带逻辑假设）
python3 ~/.hermes/scripts/amadeus/pool_manager_v2.py add CODE NAME POOL TYPE HYPOTHESIS CATALYST SUCCESS FAIL DAYS CONFIDENCE

# 退池
python3 ~/.hermes/scripts/amadeus/pool_manager_v2.py remove CODE REASON
```

### v1.0 管理器（兼容保留）

**脚本**：`scripts/amadeus/amadeus_pool_manager.py`
**功能**：自动入池/退池/降级/止损/超时检测/赶顶检测/新闻整合

```bash
# 一键自动执行：扫描退池+新闻入池+记录日志
/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py auto
```

## 纪律

1. **无逻辑不入池**：没有明确假设的股票不入池
2. **有验证必记录**：每次验证都要写结果和教训
3. **止损是铁律**：跌破止损线无条件退池，不找借口
4. **复盘是必须**：每周必须复盘，不能跳过
5. **规则可进化**：根据验证结果持续优化规则

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