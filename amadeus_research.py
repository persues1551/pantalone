#!/usr/bin/env python3
"""
Amadeus Research Agent — 受 AI Scientist-v2 启发的自动投研系统
核心流程：假设生成 → 证据收集 → 分析综合 → 集成评审 → 迭代改进

用法：
  python3 amadeus_research.py --topic "半导体板块投资机会"
  python3 amadeus_research.py --topic "英伟达财报对A股影响" --depth 3
  python3 amadeus_research.py --hypothesis "AI算力需求见顶" --review-rounds 2
"""

import json
import os
import sys
import time
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ═══════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════

CACHE_DIR = Path.home() / ".hermes" / "cache" / "amadeus" / "research"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SKILL_DIR = Path.home() / ".hermes" / "skills" / "investment" / "amadeus"
TEMPLATES_DIR = SKILL_DIR / "research_templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# 研究深度配置
DEPTH_CONFIG = {
    1: {"max_hypotheses": 3, "max_evidence": 5, "reviewers": 2, "reflections": 1},
    2: {"max_hypotheses": 5, "max_evidence": 10, "reviewers": 3, "reflections": 2},
    3: {"max_hypotheses": 8, "max_evidence": 15, "reviewers": 5, "reflections": 3},
}

# ═══════════════════════════════════════════════════════
# Prompt 模板
# ═══════════════════════════════════════════════════════

HYPOTHESIS_GENERATION_PROMPT = """你是一位资深A股投资研究员。基于以下研究主题，生成投资假设。

## 研究主题
{topic}

## 已有假设（避免重复）
{existing_hypotheses}

## 市场上下文
{market_context}

## 要求
生成一个有价值的投资假设，包含：
1. 核心论点（明确的多/空方向）
2. 逻辑链条（至少3步推理）
3. 需要验证的关键证据
4. 预期时间框架
5. 潜在风险

## 自评（1-10分）
- 新颖性：区别于市场共识的程度
- 可验证性：能否用数据验证
- 潜在收益：如果正确能赚多少

回复格式：
THOUGHT:
<你的思考过程>

HYPOTHESIS JSON:
```json
{{
  "name": "简短标识符（英文小写下划线）",
  "title": "假设标题",
  "direction": "long/short/neutral",
  "thesis": "核心论点（1-2句话）",
  "logic_chain": ["步骤1", "步骤2", "步骤3"],
  "evidence_needed": ["证据1", "证据2", "证据3"],
  "timeframe": "short/medium/long",
  "risk_factors": ["风险1", "风险2"],
  "self_scores": {{
    "novelty": 7,
    "verifiability": 8,
    "potential_return": 6
  }}
}}
```
"""

HYPOTHESIS_REFLECTION_PROMPT = """第 {current_round}/{num_reflections} 轮反思。

仔细审视你刚才生成的投资假设：
1. 逻辑链条是否有漏洞？
2. 是否忽略了反面证据？
3. 市场是否已经price in了这个逻辑？
4. 时间框架是否合理？
5. 风险评估是否充分？

改进假设，或如果已满意，在思考后写"I am done"。

回复格式同前。
"""

EVIDENCE_COLLECTION_PROMPT = """你是一位A股数据分析专家。为以下投资假设收集证据。

## 假设
{hypothesis}

## 需要验证的证据点
{evidence_needed}

## 可用数据源
- AKShare: A股行情、财务数据、板块资金流
- Tavily: 新闻搜索
- PubMed/ArXiv: 学术论文（如涉及医药/科技）

## 任务
对每个证据点，设计具体的数据收集方案：
1. 用什么API/数据源
2. 查什么指标
3. 怎么判断支持/反对假设

输出JSON格式：
```json
{{
  "evidence_plan": [
    {{
      "point": "证据点描述",
      "data_source": "akshare/tavily/pubmed",
      "query": "具体查询参数",
      "metric": "要计算的指标",
      "support_threshold": "支持假设的条件",
      "against_threshold": "反对假设的条件"
    }}
  ]
}}
```
"""

ANALYSIS_SYNTHESIS_PROMPT = """你是一位A股策略分析师。基于收集到的证据，综合分析投资假设。

## 假设
{hypothesis}

## 收集到的证据
{evidence_summary}

## 任务
1. 评估每条证据的可信度（1-10）
2. 判断证据是支持还是反对假设
3. 综合所有证据，给出结论
4. 提出具体的投资建议（标的、仓位、止损）

回复格式：
THOUGHT:
<分析过程>

ANALYSIS JSON:
```json
{{
  "evidence_evaluation": [
    {{
      "evidence": "证据描述",
      "credibility": 8,
      "supports_hypothesis": true,
      "weight": 0.3,
      "reasoning": "判断理由"
    }}
  ],
  "conclusion": "支持/反对/中性",
  "confidence": 0.75,
  "actionable": {{
    "recommendation": "买入/卖出/观望",
    "targets": [
      {{
        "ticker": "600519",
        "name": "贵州茅台",
        "direction": "long",
        "entry_price": 1800,
        "stop_loss": 1710,
        "take_profit": 2070,
        "position_pct": 15,
        "reasoning": "买入理由"
      }}
    ],
    "timeframe": "持有2-4周",
    "risk_reward_ratio": 2.5
  }},
  "key_risks": ["风险1", "风险2"],
  "monitoring_points": ["监控指标1", "监控指标2"]
}}
```
"""

REVIEWER_PROMPTS = {
    "bull": """你是一位乐观的成长型投资研究员。你倾向于看到机会，关注上行空间。
评审时重点关注：
- 假设的创新性和前瞻性
- 是否抓住了市场尚未充分定价的机会
- 上行空间是否足够大
但也要指出明显的问题。不要无脑看多。""",

    "bear": """你是一位谨慎的价值型投资研究员。你倾向于关注风险，寻找反面证据。
评审时重点关注：
- 逻辑链条的漏洞
- 被忽略的风险因素
- 市场是否已经price in
- 下行风险是否被低估
但也要承认好的机会。不要无脑看空。""",

    "quant": """你是一位量化投资研究员。你只相信数据，不接受主观判断。
评审时重点关注：
- 数据是否充分支持结论
- 统计显著性
- 回测结果的可靠性
- 是否存在过拟合
- 风险调整后收益（夏普比率）""",

    "macro": """你是一位宏观策略研究员。你从宏观角度审视所有投资假设。
评审时重点关注：
- 宏观环境是否支持
- 政策方向是否有利
- 资金流向是否配合
- 全球市场联动效应""",

    "contrarian": """你是一位逆向投资研究员。你喜欢挑战市场共识。
评审时重点关注：
- 这个假设是否太像市场共识？
- 如果所有人都这么想，谁来做对手盘？
- 有哪些被忽视的反面论据？
- 什么时候这个逻辑会失效？""",
}

REVIEW_PROMPT = """## 评审表格
请按照以下格式评审投资研究报告：

1. **摘要**：简述报告的核心观点和结论
2. **优势**：报告做得好的方面
3. **劣势**：报告需要改进的方面
4. **逻辑严密性**（1-4）：推理链条是否完整
5. **数据充分性**（1-4）：证据是否足够
6. **可操作性**（1-4）：建议是否具体可行
7. **风险管理**（1-4）：风险评估是否充分
8. **问题**：需要作者回答的问题
9. **改进建议**：具体的改进方向
10. **总体评分**（1-10）：整体质量评估
11. **投资建议评分**（1-10）：如果是实际投资决策，你会采纳这个建议吗？
12. **置信度**（1-5）：你对这个评审的自信程度
13. **决策**：Accept/Reject

回复格式：
THOUGHT:
<评审思考过程>

REVIEW JSON:
```json
{{
  "summary": "...",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "logic_score": 3,
  "data_score": 2,
  "actionability_score": 3,
  "risk_mgmt_score": 2,
  "questions": ["..."],
  "improvements": ["..."],
  "overall_score": 6,
  "investment_score": 5,
  "confidence": 4,
  "decision": "Accept"
}}
```

## 待评审报告
{report}
"""

META_REVIEW_PROMPT = """你是投研总监（Area Chair），负责综合多位研究员的评审意见。

## 评审意见汇总
{reviews_summary}

## 任务
1. 识别评审中的共识和分歧
2. 权衡不同角度的意见
3. 给出最终决策和改进建议

回复格式：
```json
{{
  "consensus_points": ["共识1", "共识2"],
  "divergence_points": [
    {{
      "topic": "分歧点",
      "bull_view": "多方观点",
      "bear_view": "空方观点",
      "your_judgment": "你的判断"
    }}
  ],
  "final_decision": "Accept/Revise/Reject",
  "revision_instructions": ["改进要求1", "改进要求2"],
  "final_score": 7,
  "confidence": 4
}}
```
"""

# ═══════════════════════════════════════════════════════
# 核心类
# ═══════════════════════════════════════════════════════

class ResearchHypothesis:
    """投资研究假设"""
    def __init__(self, data: dict):
        self.name = data.get("name", "unnamed")
        self.title = data.get("title", "")
        self.direction = data.get("direction", "neutral")
        self.thesis = data.get("thesis", "")
        self.logic_chain = data.get("logic_chain", [])
        self.evidence_needed = data.get("evidence_needed", [])
        self.timeframe = data.get("timeframe", "medium")
        self.risk_factors = data.get("risk_factors", [])
        self.self_scores = data.get("self_scores", {})
        self.evidence = []
        self.analysis = None
        self.reviews = []
        self.meta_review = None
        self.iteration = 0
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "direction": self.direction,
            "thesis": self.thesis,
            "logic_chain": self.logic_chain,
            "evidence_needed": self.evidence_needed,
            "timeframe": self.timeframe,
            "risk_factors": self.risk_factors,
            "self_scores": self.self_scores,
            "evidence": self.evidence,
            "analysis": self.analysis,
            "reviews": self.reviews,
            "meta_review": self.meta_review,
            "iteration": self.iteration,
            "created_at": self.created_at,
        }

    def summary(self):
        """简要摘要"""
        scores = self.self_scores
        score_str = f"新颖{scores.get('novelty', '?')}/可验{scores.get('verifiability', '?')}/收益{scores.get('potential_return', '?')}"
        direction_emoji = {"long": "📈", "short": "📉", "neutral": "↔️"}.get(self.direction, "❓")
        return f"{direction_emoji} [{self.name}] {self.title}\n   论点: {self.thesis}\n   自评: {score_str}"


class ResearchSession:
    """一次完整的研究会话"""
    def __init__(self, topic: str, depth: int = 2, review_rounds: int = 1):
        self.topic = topic
        self.depth = depth
        self.review_rounds = review_rounds
        self.config = DEPTH_CONFIG[depth]
        self.hypotheses: list[ResearchHypothesis] = []
        self.session_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        self.created_at = datetime.now().isoformat()
        self.status = "created"

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "depth": self.depth,
            "review_rounds": self.review_rounds,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "status": self.status,
            "created_at": self.created_at,
        }

    def save(self):
        """保存研究会话到缓存"""
        path = CACHE_DIR / f"session_{self.session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, session_id: str):
        """从缓存加载研究会话"""
        path = CACHE_DIR / f"session_{session_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = cls(data["topic"], data["depth"], data["review_rounds"])
        session.session_id = data["session_id"]
        session.status = data["status"]
        session.created_at = data["created_at"]
        for h_data in data.get("hypotheses", []):
            session.hypotheses.append(ResearchHypothesis(h_data))
        return session


# ═══════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════

def extract_json_from_response(text: str) -> dict | None:
    """从LLM回复中提取JSON"""
    import re
    # 尝试从 ```json ... ``` 块中提取
    json_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试找到第一个 { 到最后一个 }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    return None


def format_hypotheses_list(hypotheses: list[ResearchHypothesis]) -> str:
    """格式化已有假设列表"""
    if not hypotheses:
        return "（暂无）"
    return "\n".join(f"- [{h.name}] {h.thesis}" for h in hypotheses)


def format_evidence_summary(evidence: list[dict]) -> str:
    """格式化证据摘要"""
    if not evidence:
        return "（暂无证据）"
    lines = []
    for i, e in enumerate(evidence, 1):
        support = "✅支持" if e.get("supports") else "❌反对"
        lines.append(f"{i}. [{support}] {e.get('description', 'N/A')} (可信度: {e.get('credibility', '?')}/10)")
    return "\n".join(lines)


def format_reviews_summary(reviews: list[dict]) -> str:
    """格式化评审意见摘要"""
    if not reviews:
        return "（暂无评审）"
    lines = []
    for i, r in enumerate(reviews, 1):
        role = r.get("role", "unknown")
        score = r.get("overall_score", "?")
        decision = r.get("decision", "?")
        lines.append(f"### 评审{i} ({role}) - 评分: {score}/10 - 决策: {decision}")
        lines.append(f"优势: {', '.join(r.get('strengths', []))}")
        lines.append(f"劣势: {', '.join(r.get('weaknesses', []))}")
        if r.get("questions"):
            lines.append(f"问题: {', '.join(r['questions'])}")
        lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# 数据收集工具
# ═══════════════════════════════════════════════════════

def collect_market_context(topic: str) -> str:
    """收集市场上下文（供假设生成用）"""
    # 这里调用已有的数据采集工具
    context_parts = []

    # 读取最新情绪温度
    emotion_path = Path.home() / ".hermes" / "cache" / "amadeus" / "emotion.json"
    if emotion_path.exists():
        try:
            with open(emotion_path, "r") as f:
                emotion = json.load(f)
            context_parts.append(f"情绪温度: {emotion.get('score', 'N/A')}分 ({emotion.get('level', 'N/A')})")
        except:
            pass

    # 读取最新大盘数据
    market_path = Path.home() / ".hermes" / "cache" / "amadeus" / "daily_data.json"
    if market_path.exists():
        try:
            with open(market_path, "r") as f:
                market = json.load(f)
            context_parts.append(f"上证: {market.get('sh_index', 'N/A')} | 深证: {market.get('sz_index', 'N/A')} | 创业板: {market.get('cyb_index', 'N/A')}")
        except:
            pass

    # 读取观察池状态
    pool_path = Path.home() / ".hermes" / "cache" / "amadeus" / "pool_state.json"
    if pool_path.exists():
        try:
            with open(pool_path, "r") as f:
                pool = json.load(f)
            a_pool = pool.get("A_pool", [])
            context_parts.append(f"A池({len(a_pool)}只): {', '.join(a_pool[:6])}")
        except:
            pass

    if not context_parts:
        return "（市场数据暂不可用，请基于常识分析）"

    return "\n".join(context_parts)


def collect_evidence_for_hypothesis(hypothesis: ResearchHypothesis) -> list[dict]:
    """为假设收集证据（调用AKShare/Tavily等）"""
    evidence = []

    # 1. 调用AKShare获取相关板块/个股数据
    try:
        import akshare as ak
        for evidence_point in hypothesis.evidence_needed[:3]:
            # 尝试搜索相关个股
            if "板块" in evidence_point or "行业" in evidence_point:
                try:
                    df = ak.stock_board_industry_name_em()
                    # 简单匹配
                    relevant = df[df["板块名称"].str.contains(evidence_point[:2], na=False)]
                    if not relevant.empty:
                        evidence.append({
                            "description": f"板块数据: {evidence_point}",
                            "source": "akshare",
                            "supports": True,  # 需要更精细的判断
                            "credibility": 7,
                            "data": relevant.head(3).to_dict("records"),
                        })
                except Exception as e:
                    evidence.append({
                        "description": f"板块数据获取失败: {evidence_point}",
                        "source": "akshare",
                        "supports": None,
                        "credibility": 0,
                        "error": str(e),
                    })
    except ImportError:
        pass

    # 2. 调用Tavily搜索新闻
    tavily_script = Path.home() / ".hermes" / "scripts" / "tavily_search.py"
    if tavily_script.exists():
        for evidence_point in hypothesis.evidence_needed[:2]:
            try:
                import subprocess
                result = subprocess.run(
                    ["python3", str(tavily_script), evidence_point, "--topic", "news", "--days", "7", "--max-results", "3"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    news_data = json.loads(result.stdout) if result.stdout.strip().startswith('{') else {"raw": result.stdout[:500]}
                    evidence.append({
                        "description": f"新闻搜索: {evidence_point}",
                        "source": "tavily",
                        "supports": None,  # 需要LLM判断
                        "credibility": 6,
                        "data": news_data,
                    })
            except Exception as e:
                evidence.append({
                    "description": f"新闻搜索失败: {evidence_point}",
                    "source": "tavily",
                    "supports": None,
                    "credibility": 0,
                    "error": str(e),
                })

    # 3. 如果是医药相关，搜索PubMed
    med_keywords = ["医药", "生物", "临床", "药物", "医疗", "基因"]
    if any(kw in hypothesis.thesis for kw in med_keywords):
        for evidence_point in hypothesis.evidence_needed[:2]:
            try:
                import subprocess
                result = subprocess.run(
                    ["python3", "-c", f"""
import requests
r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={{"db": "pubmed", "term": "{evidence_point}", "retmax": 3, "retmode": "json"}})
print(r.text[:500])
"""],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    evidence.append({
                        "description": f"PubMed搜索: {evidence_point}",
                        "source": "pubmed",
                        "supports": None,
                        "credibility": 8,
                        "data": {"raw": result.stdout[:300]},
                    })
            except:
                pass

    return evidence


# ═══════════════════════════════════════════════════════
# 报告生成
# ═══════════════════════════════════════════════════════

def generate_report(session: ResearchSession) -> str:
    """生成最终研究报告"""
    report_lines = [
        f"# Amadeus 研究报告",
        f"",
        f"**主题**: {session.topic}",
        f"**深度**: L{session.depth} | **评审轮次**: {session.review_rounds}",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**会话ID**: {session.session_id}",
        f"",
        f"---",
        f"",
    ]

    for i, h in enumerate(session.hypotheses, 1):
        direction_emoji = {"long": "📈看多", "short": "📉看空", "neutral": "↔️中性"}.get(h.direction, "❓")
        report_lines.append(f"## 假设{i}: {h.title}")
        report_lines.append(f"")
        report_lines.append(f"**方向**: {direction_emoji}")
        report_lines.append(f"**核心论点**: {h.thesis}")
        report_lines.append(f"")
        report_lines.append(f"### 逻辑链条")
        for j, step in enumerate(h.logic_chain, 1):
            report_lines.append(f"{j}. {step}")
        report_lines.append(f"")

        if h.evidence:
            report_lines.append(f"### 证据汇总")
            report_lines.append(format_evidence_summary(h.evidence))
            report_lines.append(f"")

        if h.analysis:
            report_lines.append(f"### 分析结论")
            conclusion = h.analysis.get("conclusion", "N/A")
            confidence = h.analysis.get("confidence", "N/A")
            report_lines.append(f"- **结论**: {conclusion}")
            report_lines.append(f"- **置信度**: {confidence}")
            if h.analysis.get("actionable"):
                action = h.analysis["actionable"]
                report_lines.append(f"- **建议**: {action.get('recommendation', 'N/A')}")
                for target in action.get("targets", []):
                    report_lines.append(f"  - {target.get('name', '')}({target.get('ticker', '')}): "
                                       f"{target.get('direction', '')} @ {target.get('entry_price', 'N/A')}, "
                                       f"止损 {target.get('stop_loss', 'N/A')}, "
                                       f"目标 {target.get('take_profit', 'N/A')}")
            report_lines.append(f"")

        if h.reviews:
            report_lines.append(f"### 评审意见")
            report_lines.append(format_reviews_summary(h.reviews))
            report_lines.append(f"")

        if h.meta_review:
            report_lines.append(f"### 总监评审")
            mr = h.meta_review
            report_lines.append(f"- **最终决策**: {mr.get('final_decision', 'N/A')}")
            report_lines.append(f"- **最终评分**: {mr.get('final_score', 'N/A')}/10")
            if mr.get("consensus_points"):
                report_lines.append(f"- **共识**: {', '.join(mr['consensus_points'])}")
            if mr.get("revision_instructions"):
                report_lines.append(f"- **改进要求**:")
                for inst in mr["revision_instructions"]:
                    report_lines.append(f"  - {inst}")
            report_lines.append(f"")

        report_lines.append(f"---")
        report_lines.append(f"")

    # 风险提示
    report_lines.extend([
        f"",
        f"⚠️ **免责声明**: 以上仅为教学研究案例，不构成投资建议。",
        f"市场有风险，投资需谨慎！",
    ])

    return "\n".join(report_lines)


# ═══════════════════════════════════════════════════════
# 主流程（供 Hermes Agent 调用）
# ═══════════════════════════════════════════════════════

def create_session(topic: str, depth: int = 2, review_rounds: int = 1) -> ResearchSession:
    """创建研究会话"""
    session = ResearchSession(topic, depth, review_rounds)
    session.save()
    return session


def get_hypothesis_prompt(session: ResearchSession, existing: list[ResearchHypothesis] = None) -> str:
    """生成假设生成的prompt（供Agent调用）"""
    market_context = collect_market_context(session.topic)
    existing_str = format_hypotheses_list(existing or [])
    return HYPOTHESIS_GENERATION_PROMPT.format(
        topic=session.topic,
        existing_hypotheses=existing_str,
        market_context=market_context,
    )


def get_review_prompt(report_text: str) -> str:
    """生成评审prompt"""
    return REVIEW_PROMPT.format(report=report_text)


def get_meta_review_prompt(reviews: list[dict]) -> str:
    """生成总监评审prompt"""
    return META_REVIEW_PROMPT.format(reviews_summary=format_reviews_summary(reviews))


# ═══════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Amadeus Research Agent")
    parser.add_argument("--topic", type=str, help="研究主题")
    parser.add_argument("--depth", type=int, default=2, choices=[1, 2, 3], help="研究深度")
    parser.add_argument("--review-rounds", type=int, default=1, help="评审轮次")
    parser.add_argument("--session-id", type=str, help="加载已有会话")
    parser.add_argument("--list-sessions", action="store_true", help="列出所有会话")
    parser.add_argument("--report", type=str, help="生成报告（指定session_id）")

    args = parser.parse_args()

    if args.list_sessions:
        sessions = sorted(CACHE_DIR.glob("session_*.json"))
        if not sessions:
            print("暂无研究会话")
            return
        for s in sessions:
            with open(s, "r") as f:
                data = json.load(f)
            print(f"[{data['session_id']}] {data['topic']} ({data['status']}) - {data['created_at']}")
        return

    if args.report:
        session = ResearchSession.load(args.report)
        if not session:
            print(f"会话 {args.report} 不存在")
            return
        report = generate_report(session)
        report_path = CACHE_DIR / f"report_{args.report}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已生成: {report_path}")
        print(report)
        return

    if not args.topic:
        parser.print_help()
        return

    # 创建新会话
    session = create_session(args.topic, args.depth, args.review_rounds)
    print(f"✅ 研究会话已创建: {session.session_id}")
    print(f"   主题: {session.topic}")
    print(f"   深度: L{session.depth} ({session.config['max_hypotheses']}个假设, {session.config['reviewers']}位评审)")
    print()

    # 输出假设生成prompt
    prompt = get_hypothesis_prompt(session)
    print("=" * 60)
    print("📋 假设生成 Prompt（供Agent使用）:")
    print("=" * 60)
    print(prompt)
    print()
    print(f"💡 下一步: 使用 amadeus_research.py --session-id {session.session_id} 继续")


if __name__ == "__main__":
    main()
