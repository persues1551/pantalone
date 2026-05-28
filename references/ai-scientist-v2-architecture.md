# AI Scientist-v2 架构分析

> 来源：SakanaAI/AI-Scientist (GitHub, Apache 2.0) | 2026-05-14

## 核心发现

博客声称有"tree_search.py"实现MCTS，实际**不存在**。真实架构是线性流水线+反思循环。

## 实际架构

```
launch_scientist.py
├── generate_ideas.py — 创意生成+反思循环(5轮)
├── perform_experiments.py — Aider代码迭代(4轮×5运行)
├── perform_writeup.py — LaTeX论文生成
└── perform_review.py — 集成评审(5个独立评审→Area Chair综合)
    └── llm.py — 统一LLM客户端(OpenAI/Anthropic/DeepSeek/Gemini)
```

## 关键细节

- **评审集成**: 5个独立评审→meta-reviewer(Area Chair)综合→Accept/Reject
- **评审字段**: Summary/Strengths/Weaknesses/Originality/Quality/Clarity/Significance(1-4)/Overall(1-10)
- **Few-shot**: 3篇真实ICLR论文评审作示例
- **文献查新**: Semantic Scholar API，最多10轮迭代
- **成本**: $10-180/篇（取决于模型和GPU）

## 社区反馈

正面: 论文结构完整(~70%可运行)、审稿具体、教育价值高
负面: 无真正创新、公式微妙错误、写稿Agent"欺骗"审稿Agent

## Amadeus适配

已创建amadeus_research.py，评审1种→5种(Bull/Bear/Quant/Macro/Contrarian)，数据源Aider→AKShare/Tavily/PubMed，输出论文→投资建议。
