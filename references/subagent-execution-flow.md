# Subagent 执行流程 v3.4（并行 delegate_task 架构）

## 关键发现（2026-05-15）

**根因**：cron任务缺少`delegation`工具集 → delegate_task静默不可用 → subagent永不执行。
**修复**：所有Amadeus cron任务（4主+3备份+AIHOT）已加`delegation`。

## 新架构：4步并行流程

```
┌─────────────────┐
│ 1. 加载上下文     │  amadeus_context.py + sim_integrate.py + data.py
├─────────────────┤
│ 2. 并行采集       │  delegate_task(tasks=[5个subagent]) 并行执行
│  ├─ market_data  │  情绪+资金流+大盘信号
│  ├─ technical    │  MA/RSI/MACD/布林带
│  ├─ macro        │  外围+宏观环境
│  ├─ theme        │  新闻+题材+轮动
│  └─ risk         │  选股+排雷
├─────────────────┤
│ 3. 生成报告       │  综合5个subagent结果 + 上下文 → 按模板生成
├─────────────────┤
│ 4. 独立审查       │  delegate_task → review subagent（不可自己审）
│  ├─ score≥70     │  → 通过，发送
│  ├─ score<70     │  → 修改后重审（最多1轮）
│  └─ 仍不通过      │  → 标注⚠️后发送
└─────────────────┘
```

## delegate_task 调用模板

```python
delegate_task(tasks=[
    {"goal": "你是市场数据采集专家。\n1. 运行 amadeus_emotion.py\n2. 运行 amadeus_sector_flow.py\n3. 运行 amadeus_market_filter.py\n返回结构化数据摘要。", "toolsets": ["terminal"]},
    {"goal": "你是技术分析专家。\n1. 运行 amadeus_realtime.py\n2. 分析MA/RSI/MACD/布林带\n返回技术面评分。", "toolsets": ["terminal"]},
    {"goal": "你是宏观分析师。\n1. 运行 amadeus_external.py\n2. 分析宏观环境\n返回宏观面评分。", "toolsets": ["terminal", "web"]},
    {"goal": "你是题材分析师。\n1. 运行 amadeus_news_scanner.py scan\n2. 分析题材+轮动\n返回题材面评分。", "toolsets": ["terminal", "web"]},
    {"goal": "你是风控审查员。\n1. 运行 amadeus_screening.py\n2. 排雷扫描\n返回风控结论。", "toolsets": ["terminal"]}
])
```

## 旧架构（v3.2，已废弃）

旧架构是串行执行7个subagent角色提示词，无delegate_task调用。主Agent自己跑所有脚本，自己审查自己。

## 自我审查反模式

**问题**：Agent默认会自己审查自己的报告（读文件→说"看起来不错"→发送）。
**修复**：prompt必须写"不可自己审查，不可跳过"，且delegation工具集必须可用。

## 数据来源要求

| Agent | 必须标注 | 缺失处理 |
|-------|----------|----------|
| market_data | 日期、口径（盘中/收盘）、来源 | 标注"数据缺失" |
| macro | 外围数据时间、汇率方向 | 标注"来源不明" |
| theme | 来源（政策/产业/消息/资金）、成交容量 | 无成交不算主线 |
| technical | 触发条件、失效条件、支撑/压力位 | 无失效条件不完整 |
| risk | 通过/警告/不通过 | 必须执行 |

## 模拟盘集成

每个投资报告必须调用：
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py status
python3 ~/.hermes/scripts/amadeus/amadeus_sim_integrate.py daily_update  # 收盘后
```

## 上下文持久化

每个报告开头加载：
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_context.py summary
```

每个报告结束更新：
```bash
python3 ~/.hermes/scripts/amadeus/amadeus_context.py set_stance <偏多/偏空/震荡> "<理由>"
python3 ~/.hermes/scripts/amadeus/amadeus_context.py add_prediction '{"dimension":"...","prediction":"...","confidence":0.X}'
python3 ~/.hermes/scripts/amadeus/amadeus_context.py sector_trend "板块名" '{"status":"...","consecutive_days":N}'
```
