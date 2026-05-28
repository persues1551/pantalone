# Pantalone Research Agent — 自动投研系统

> 受 AI Scientist-v2 (Sakana AI) 启发，适配A股投研场景

## 概述

Pantalone Research Agent 是一个自动化投研系统，核心流程：

```
假设生成 → 证据收集 → 分析综合 → 集成评审 → 迭代改进
   ↑                                              |
   └──────────────── 反馈循环 ────────────────────┘
```

与 AI Scientist-v2 的对应关系：
| AI Scientist-v2 | Pantalone Research Agent |
|---|---|
| idea_generation.py | 假设生成（投资假设而非学术idea） |
| perform_experiments.py | 证据收集（AKShare/Tavily/PubMed） |
| perform_writeup.py | 分析综合（策略报告而非学术论文） |
| perform_review.py | 集成评审（5角色而非NeurIPS评审） |
| LaTeX模板 | Markdown报告模板 |

## 关键改进（相比AI Scientist-v2原版）

### 1. 评审角色多样化
原版只有一种评审prompt（正面/负面两种风格），我们设计了5种投资研究角色：
- 🐂 **Bull** — 成长型，关注上行空间
- 🐻 **Bear** — 价值型，关注下行风险
- 📊 **Quant** — 量化型，只信数据
- 🌍 **Macro** — 宏观型，关注政策和资金
- 🔄 **Contrarian** — 逆向型，挑战共识

### 2. 真正的证据收集
原版用Aider跑ML实验，我们用真实金融数据：
- AKShare: A股行情、财务、板块资金流
- Tavily: 实时新闻搜索
- PubMed: 医药相关论文
- amadeus_emotion.py: 情绪温度
- amadeus_market_filter.py: 大盘过滤器

### 3. 可操作的输出
原版输出学术论文，我们输出：
- 具体标的（代码、名称）
- 入场价位、止损、目标价
- 仓位比例
- 持有时间框架
- 监控指标

## 使用方式

### 方式1：Hermes Agent 对话式
```
主人: 研究一下半导体板块的投资机会
Agent: [自动创建研究会话 → 生成假设 → 收集证据 → 评审 → 输出报告]
```

### 方式2：Cron自动执行
```bash
# 每周五收盘后自动研究一个热门话题
0 15 * * 5 python3 amadeus_research.py --topic "本周热门板块" --depth 2
```

### 方式3：CLI手动触发
```bash
python3 amadeus_research.py --topic "英伟达财报对A股影响" --depth 3
python3 amadeus_research.py --list-sessions
python3 amadeus_research.py --report <session_id>
```

## 评审流程详解

### 单轮评审
```
报告 → [Bull评审, Bear评审, Quant评审, Macro评审, Contrarian评审] → Area Chair综合 → 决策
```

### 多轮迭代（review_rounds > 1）
```
报告v1 → 评审 → 修改意见 → 报告v2 → 评审 → ... → 最终报告
```

### Area Chair（投研总监）职责
1. 识别评审共识和分歧
2. 权衡不同角度意见
3. 给出最终决策：Accept / Revise / Reject
4. 如Revise，列出具体改进要求

## 文件结构

```
amadeus/
├── amadeus_research.py          # 核心引擎
├── subagents/
│   └── research_agent.md        # 本文件（说明文档）
├── research_templates/          # 研究模板
│   ├── sector_analysis.md       # 板块分析模板
│   ├── earnings_analysis.md     # 财报分析模板
│   └── macro_analysis.md        # 宏观分析模板
└── ~/.hermes/cache/amadeus/research/
    ├── session_<id>.json        # 研究会话数据
    └── report_<id>.md           # 生成的报告
```

## 与现有Pantalone组件的集成

| 组件 | 集成方式 |
|---|---|
| amadeus_emotion.py | 提供情绪温度上下文 |
| amadeus_market_filter.py | 提供大盘过滤信号 |
| amadeus_buy_scorer.py | 对研究发现的标的评分 |
| amadeus_valuation.py | 提供估值数据 |
| amadeus_screening.py | 排雷扫描 |
| pool_manager.py | 自动入池/退池建议 |
| amadeus_sim_integrate.py | 模拟盘验证 |

## 模型路由

| 阶段 | 推荐模型 | 原因 |
|---|---|---|
| 假设生成 | DeepSeek V4 Pro | 需要创造力和推理 |
| 证据收集 | mimo-v2.5-pro | 工具调用为主 |
| 分析综合 | DeepSeek V4 Pro | 复杂推理 |
| 评审（Bull/Bear） | mimo-v2.5-pro | 角色扮演不需要最强模型 |
| 评审（Quant） | DeepSeek V4 Pro | 需要数据推理能力 |
| Area Chair | DeepSeek V4 Pro | 综合决策需要强推理 |

## 成本估算

| 深度 | 假设数 | 评审人数 | 预估Token | 预估时间 |
|---|---|---|---|---|
| L1 | 3 | 2 | ~50K | 2-3分钟 |
| L2 | 5 | 3 | ~120K | 5-8分钟 |
| L3 | 8 | 5 | ~250K | 10-15分钟 |

## TODO

- [ ] 研究模板（板块/财报/宏观）
- [ ] 与模拟盘联动（研究→模拟→复盘闭环）
- [ ] 研究历史索引（避免重复研究）
- [ ] 自动选题（基于市场热点自动选研究主题）
- [ ] 树搜索实现（并行探索多条假设路径）
