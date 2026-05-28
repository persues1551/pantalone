# review_log.md — 复盘日志

## 预测记录格式

**脚本**：`scripts/amadeus/amadeus_predictions.py`

### 保存预测

```bash
python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py save '{
  "date": "2026-05-13",
  "predictions": [
    {
      "dimension": "指数方向",
      "prediction": "上证4200-4250，偏震荡",
      "verification": "收盘是否在区间内"
    },
    {
      "dimension": "资金主线",
      "prediction": "半导体/AI延续",
      "verification": "次日净流入TOP3包含半导体"
    }
  ]
}'
```

### 验证预测

```bash
python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py verify
```

### 查看统计

```bash
python3 ~/.hermes/scripts/amadeus/amadeus_predictions.py stats
```

## 验证结果记录

| 预测 | 验证标准 | 实际结果 | ✅/❌ | 偏差原因 |
|------|----------|----------|-------|----------|
| 指数区间xxx-xxx | 收盘在区间内 | 实际收盘xxx | ✅/❌ | 归因 |
| 资金主线xxx延续 | TOP3包含xxx | 实际TOP3: xxx | ✅/❌ | 归因 |
| xxx连板 | 收盘涨停 | 实际收x% | ✅/❌ | 归因 |

## 教训记录格式

```bash
python3 ~/.hermes/scripts/amadeus/amadeus_context.py add_lesson "教训内容"
```

### 教训分类

| 类型 | 说明 | 示例 |
|------|------|------|
| 数据教训 | 数据采集/处理错误 | "连板数据存疑时不能用于情绪温度计算" |
| 判断教训 | 分析判断错误 | "高开>5%的票不能追，即使板块强势" |
| 执行教训 | 操作执行错误 | "止损-5%必须执行，不能因为'感觉还能涨'而犹豫" |
| 系统教训 | 系统/工具问题 | "东方财富API断连时降级到新浪" |

## 投研上下文持久化

**脚本**：`scripts/amadeus/amadeus_context.py`

### 上下文字段说明

| 字段 | 用途 | 更新时机 |
|------|------|----------|
| market_stance | 当前市场立场（偏多/偏空/震荡） | 每次复盘更新 |
| prediction_streak | 预测准确率连击 | 每次验证预测后 |
| recent_predictions | 最近10条预测记录 | 每次写入预测时 |
| sector_trends | 板块趋势跟踪 | 复盘发现主线变化时 |
| stock_notes | 个股分析笔记 | 分析新标的或更新结论时 |
| lessons_learned | 教训（最近20条） | 发现错误/优化时 |
| pending_todos | 待办事项 | 发现可改进项时 |

### 更新命令

```bash
# 更新市场立场
python3 ~/.hermes/scripts/amadeus/amadeus_context.py set_stance <偏多/偏空/震荡> "<理由>"

# 记录预测
python3 ~/.hermes/scripts/amadeus/amadeus_context.py add_prediction '{"dimension":"指数方向","prediction":"...","result":"correct/incorrect","actual":"..."}'

# 记录教训
python3 ~/.hermes/scripts/amadeus/amadeus_context.py add_lesson "教训内容"

# 更新板块趋势
python3 ~/.hermes/scripts/amadeus/amadeus_context.py sector_trend "板块名" '{"status":"主线确认","consecutive_days":5}'

# 更新个股笔记
python3 ~/.hermes/scripts/amadeus/amadeus_context.py stock_note "600900" '{"pool":"A","note":"...","status":"观察"}'
```

### 数据维护

- 每周日自动清理>30天的旧数据（`prune`命令）
- 上下文文件：`~/.hermes/cache/amadeus/session_context.json`
- 不参与分析计算，仅提供历史参考

## 连续错误标记规则

- 某维度连续3次错误 → 自动标记【该维度判断逻辑待调整】
- 写入复盘「八、失败点」
- 必须在下次复盘中修正该维度的判断逻辑

---

## 实际复盘记录

### 2026-05-14 审计修复记录

**修复项目**：
1. 模拟盘集成：创建amadeus_sim_integrate.py，集成到cron报告流程
2. 观察池价格：修复盘前时段价格显示（昨收价替代current=0）
3. 预测验证：重写match_dimension函数，新增板块数据采集，准确率0%→100%
4. 涨停池截取：head(20)→head(50)，覆盖更多涨停股
5. 观察池数据：更新14只股票的entry_price

**预测验证结果**（2026-05-14）：
- 指数方向：OK（上证收4242.57，区间4220-4280）
- 资金主线：OK（半导体材料涨1.29%）
- 最强方向：OK（工业富联涨停）
- 最弱方向：OK（证券Ⅱ跌0.01%）
- 风险点：OK（涨停113只）
- 准确率：100% (5/5)

**教训**：
- amadeus_data.py的head(20)限制导致涨停股数据不完整
- 验证函数必须适配实际数据结构，不能假设扁平字段
- 盘前时段API返回current=0，需用prev_close替代

### 2026-05-13 初始记录

**市场概况**：
- 上证：4242.57（+0.67%）
- 涨停：163只，跌停：7只
- 情绪温度：升温（60%机会）
- 主线：半导体/AI算力、消费电子

**观察池建立**：
- A池：长江电力（水电龙头，高股息防御）
- B池：歌尔/三花/紫光国微/中信/立讯/工业富联/澜起/光迅/新易盛
- C池：蓝思/北大荒/东航/国航
- 总计：14只
