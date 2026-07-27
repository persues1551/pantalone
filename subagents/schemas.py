"""Optional Pydantic contracts for validating Pantalone subagent data.

Hermes ``delegate_task`` returns text by default. Callers may explicitly parse
that output into these models and use the ``render_*`` helpers; defining the
schemas alone does not wire structured output into the runtime.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ============================================================================
# Shared enums — used across multiple subagents
# ============================================================================


class SentimentBias(str, Enum):
    """Sentiment direction for market data, macro, and capital-flow analysis."""

    BULLISH = "偏多"
    MILDLY_BULLISH = "中性偏多"
    NEUTRAL = "中性"
    MILDLY_BEARISH = "中性偏空"
    BEARISH = "偏空"


class DataQuality(str, Enum):
    """Data freshness and completeness grade."""

    A = "A"  # All sources returned live data
    B = "B"  # Most sources returned data, minor gaps
    C = "C"  # Some sources failed, significant gaps
    D = "D"  # Most sources failed, treat with caution


class ReviewVerdict(str, Enum):
    """Review outcome — mirrors TradingAgents' 5-tier rating pattern."""

    PASS = "通过"
    CONDITIONAL = "有条件通过"
    REVISE = "退回修改"
    REJECT = "否决"


class ETFGrade(str, Enum):
    """ETF quality rating: A=core, B=usable, C=watch, D=avoid, E=reject."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class ETFType(str, Enum):
    """ETF classification categories."""

    BROAD = "宽基"
    SECTOR = "行业"
    THEME = "主题"
    STYLE = "风格"
    BOND = "债券"
    COMMODITY = "商品"
    QDII = "QDII"
    MONEY = "货币"
    REITS = "REITs"


class TradeAction(str, Enum):
    """3-tier transaction direction (mirrors TradingAgents' TraderAction)."""

    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"


class IssueSeverity(str, Enum):
    """Issue severity for review results."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class RiskFlag(str, Enum):
    """Risk screening flags."""

    UNKNOWN = "unknown"
    PASS = "pass"
    WARN = "warn"
    VETO = "veto"  # 一票否决


class MacroBias(str, Enum):
    """Macro environment directional bias."""

    BULLISH = "偏多"
    MILDLY_BULLISH = "中性偏多"
    NEUTRAL = "中性"
    MILDLY_BEARISH = "中性偏空"
    BEARISH = "偏空"


# ============================================================================
# Market Data
# ============================================================================


class EmotionComponents(BaseModel):
    """Breakdown of sentiment temperature components."""

    retail: Optional[float] = Field(default=None, description="散户情绪分")
    institution: Optional[float] = Field(default=None, description="机构情绪分")
    breadth: Optional[float] = Field(default=None, description="涨跌比情绪分")


class EmotionReport(BaseModel):
    """Aggregate market emotion / temperature reading."""

    score: float = Field(ge=0.0, le=100.0, description="情绪温度 0-100")
    level: str = Field(description="情绪等级：恐慌/偏弱/中性/偏强/亢奋")
    components: EmotionComponents = Field(default_factory=EmotionComponents)


class SectorFlowReport(BaseModel):
    """Sector capital flow summary."""

    top_inflow: List[Dict[str, object]] = Field(
        default_factory=list,
        description="资金流入TOP板块，每项含 name/change_pct/net_flow_wan",
    )
    top_outflow: List[Dict[str, object]] = Field(
        default_factory=list,
        description="资金流出TOP板块，每项含 name/change_pct/net_flow_wan",
    )


class MarketFilterReport(BaseModel):
    """Broad market signal summary."""

    level: str = Field(description="大盘定性：震荡偏强/震荡/震荡偏弱/趋势向上/趋势向下")
    position_pct: float = Field(ge=0.0, le=100.0, description="建议仓位百分比")


class NorthboundReport(BaseModel):
    """Northbound (北向) capital flow snapshot."""

    hgt_yi: Optional[float] = Field(default=None, description="沪股通净额（亿元）")
    sgt_yi: Optional[float] = Field(default=None, description="深股通净额（亿元）")
    total_yi: Optional[float] = Field(default=None, description="北向合计净额（亿元）")
    bias: str = Field(default="数据缺失", description="净流入/净流出/持平/数据缺失")
    intraday_signal: Optional[str] = Field(default=None, description="盘中分钟流信号")


class MarketDataReport(BaseModel):
    """Structured market-data output consumed by downstream analysts.

    Sentiment, sector flow, market filter, and northbound capital are gathered
    by a single market_data subagent and passed as context to technical, macro,
    and theme analysts.
    """

    emotion: EmotionReport = Field(description="市场情绪温度")
    sector_flow: SectorFlowReport = Field(description="板块资金流")
    market_filter: MarketFilterReport = Field(description="大盘仓位信号")
    northbound: NorthboundReport = Field(description="北向资金")
    data_quality: DataQuality = Field(default=DataQuality.D, description="数据质量评级；未提供时为D")
    errors: List[str] = Field(default_factory=list, description="采集错误列表")


def render_market_data_report(report: MarketDataReport) -> str:
    """Render MarketDataReport to markdown for report stitching."""
    northbound_total = (
        "N/A" if report.northbound.total_yi is None else str(report.northbound.total_yi)
    )
    return "\n".join([
        "## 市场数据",
        "",
        f"**情绪温度**: {report.emotion.score:.0f}/100 ({report.emotion.level})",
        f"**大盘信号**: {report.market_filter.level} (建议仓位 {report.market_filter.position_pct:.0f}%)",
        f"**北向资金**: {northbound_total}亿 ({report.northbound.bias})",
        f"**数据质量**: {report.data_quality.value}",
        "",
        "### 板块资金流",
        f"流入TOP: {', '.join(item.get('name', '?') for item in report.sector_flow.top_inflow[:3])}" if report.sector_flow.top_inflow else "无数据",
        f"流出TOP: {', '.join(item.get('name', '?') for item in report.sector_flow.top_outflow[:3])}" if report.sector_flow.top_outflow else "无数据",
    ])


# ============================================================================
# Technical Analysis
# ============================================================================


class StockTechnical(BaseModel):
    """Per-stock technical indicators snapshot."""

    price: Optional[float] = Field(default=None, description="最新价格")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅(%)")
    MA5: Optional[float] = Field(default=None, description="5日均线")
    MA10: Optional[float] = Field(default=None, description="10日均线")
    MA20: Optional[float] = Field(default=None, description="20日均线")
    RSI14: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="RSI(14)")
    rsi_status: Optional[str] = Field(default=None, description="超买/中性/超卖")
    macd_signal: Optional[str] = Field(default=None, description="多头/空头/金叉/死叉")
    BB_upper: Optional[float] = Field(default=None, description="布林带上轨")
    BB_lower: Optional[float] = Field(default=None, description="布林带下轨")
    vol_ratio: Optional[float] = Field(default=None, description="成交量比(相对5日均量)")
    ma_trend: Optional[str] = Field(default=None, description="均线趋势：多头/空头/粘合")
    support_20d: Optional[float] = Field(default=None, description="20日均线支撑")
    resistance_20d: Optional[float] = Field(default=None, description="20日均线压力")
    buy_blocked: List[str] = Field(default_factory=list, description="阻止买入的信号")
    source: str = Field(default="", description="实际成功使用的数据来源；未采集时为空")


class TechnicalSummary(BaseModel):
    """Aggregate technical analysis summary."""

    bullish_count: int = Field(default=0, description="多头信号标的数")
    bearish_count: int = Field(default=0, description="空头信号标的数")
    neutral_count: int = Field(default=0, description="中性信号标的数")


class TechnicalAnalysisReport(BaseModel):
    """Structured technical analysis for a batch of stocks."""

    stocks: Dict[str, StockTechnical] = Field(
        description="标的代码→技术指标映射"
    )
    summary: TechnicalSummary = Field(default_factory=TechnicalSummary)
    errors: List[str] = Field(default_factory=list, description="采集/计算错误")
    data_sources: List[str] = Field(default_factory=list, description="实际成功使用的数据脚本")


def render_technical_report(report: TechnicalAnalysisReport) -> str:
    """Render TechnicalAnalysisReport to markdown."""
    lines = ["## 技术分析", ""]
    for code, stock in report.stocks.items():
        lines.append(f"### {code} (¥{stock.price})")
        lines.append(f"- MA趋势: {stock.ma_trend} | RSI: {stock.RSI14} | MACD: {stock.macd_signal}")
        lines.append(f"- 支撑: ¥{stock.support_20d} | 压力: ¥{stock.resistance_20d}")
        if stock.buy_blocked:
            lines.append(f"- ⚠️ 买入受阻: {', '.join(stock.buy_blocked)}")
        lines.append("")
    lines.append(f"**汇总**: 多头 {report.summary.bullish_count} / 空头 {report.summary.bearish_count} / 中性 {report.summary.neutral_count}")
    return "\n".join(lines)


# ============================================================================
# Financial / Fundamental Analysis
# ============================================================================


class Valuation(BaseModel):
    """Valuation metrics."""

    pe_ttm: Optional[float] = Field(default=None, description="市盈率TTM")
    pb: Optional[float] = Field(default=None, description="市净率")
    peg: Optional[float] = Field(default=None, description="PEG")


class DividendInfo(BaseModel):
    """Dividend history summary."""

    consecutive_years: int = Field(default=0, description="连续分红年数")
    recent_yields: List[float] = Field(default_factory=list, description="近3年股息率")
    trend: str = Field(default="", description="逐年提高/下降/稳定")


class FinancialReport(BaseModel):
    """Structured financial analysis for a single stock."""

    financial_score: float = Field(
        ge=0.0, le=100.0, description="财务面评分 0-100"
    )
    revenue_trend: str = Field(description="连续N季营收趋势描述")
    profit_trend: str = Field(description="连续N季利润趋势描述")
    roe: Optional[float] = Field(default=None, description="ROE(%)")
    gross_margin: Optional[float] = Field(default=None, description="毛利率(%)")
    cashflow_quality: str = Field(description="现金流质量描述（经营现金流/净利润比）")
    valuation: Valuation = Field(default_factory=Valuation)
    dividend: DividendInfo = Field(default_factory=DividendInfo)
    peer_comparison: str = Field(description="与同行业对比描述")
    key_risks: List[str] = Field(default_factory=list, description="关键风险点")


def render_financial_report(report: FinancialReport) -> str:
    """Render FinancialReport to markdown."""
    return "\n".join([
        "## 财报分析",
        "",
        f"**财务面评分**: {report.financial_score:.0f}/100",
        f"**营收趋势**: {report.revenue_trend}",
        f"**利润趋势**: {report.profit_trend}",
        f"**ROE**: {report.roe}% | **毛利率**: {report.gross_margin}%",
        f"**现金流**: {report.cashflow_quality}",
        f"**估值**: PE={report.valuation.pe_ttm}, PB={report.valuation.pb}, PEG={report.valuation.peg}",
        f"**分红**: 连续{report.dividend.consecutive_years}年 ({report.dividend.trend})",
        f"**行业对比**: {report.peer_comparison}",
        "",
        f"**风险**: {'; '.join(report.key_risks) if report.key_risks else '无明显风险'}",
    ])


# ============================================================================
# Theme / Sector Analysis
# ============================================================================


class HotReason(BaseModel):
    """A single stock's hot-topic reasons from 同花顺."""

    code: str = Field(description="股票代码")
    name: str = Field(description="股票名称")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅(%)")
    reasons: List[str] = Field(default_factory=list, description="题材标签")


class ThemeHeat(BaseModel):
    """Theme heat map summary."""

    top_themes: List[Dict[str, object]] = Field(
        default_factory=list,
        description="TOP题材 [{\"name\": \"X\", \"count\": N}]",
    )
    new_themes: List[str] = Field(default_factory=list, description="新出现题材")
    fading_themes: List[str] = Field(default_factory=list, description="退潮题材")


class IndustryRankItem(BaseModel):
    """A single industry's rank data."""

    name: str = Field(description="行业名称")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅(%)")


class IndustryRanking(BaseModel):
    """Industry performance rankings."""

    top3: List[IndustryRankItem] = Field(default_factory=list)
    bottom3: List[IndustryRankItem] = Field(default_factory=list)


class ThemeAnalysisReport(BaseModel):
    """Structured theme/sector analysis."""

    hot_reasons: List[HotReason] = Field(
        default_factory=list, description="同花顺热点归因标的列表"
    )
    theme_heat: ThemeHeat = Field(default_factory=ThemeHeat)
    industry_ranking: IndustryRanking = Field(default_factory=IndustryRanking)
    rotation_signal: str = Field(default="", description="板块轮动信号描述")
    theme_score: float = Field(ge=0.0, le=100.0, description="题材面评分")
    theme_bias: str = Field(description="题材热度：偏多/中性偏多/中性/中性偏空/偏空")
    key_signals: List[str] = Field(default_factory=list, description="关键信号")
    errors: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)


def render_theme_report(report: ThemeAnalysisReport) -> str:
    """Render ThemeAnalysisReport to markdown."""
    top_names = [t.get("name", "?") for t in report.theme_heat.top_themes[:5]]
    return "\n".join([
        "## 题材分析",
        "",
        f"**题材面评分**: {report.theme_score:.0f}/100 ({report.theme_bias})",
        f"**热点题材**: {', '.join(top_names)}" if top_names else "无热点",
        f"**新题材**: {', '.join(report.theme_heat.new_themes)}" if report.theme_heat.new_themes else "",
        f"**退潮**: {', '.join(report.theme_heat.fading_themes)}" if report.theme_heat.fading_themes else "",
        f"**轮动信号**: {report.rotation_signal}",
    ])


# ============================================================================
# Macro Analysis
# ============================================================================


class MarketIndex(BaseModel):
    """A single market index snapshot."""

    close: Optional[float] = Field(default=None, description="收盘价")
    pct: Optional[float] = Field(default=None, description="涨跌幅(%)")
    source: str = Field(default="", description="实际成功使用的数据源；未采集时为空")


class GlobalMarkets(BaseModel):
    """Key global index readings."""

    dji: MarketIndex = Field(default_factory=MarketIndex, description="道琼斯")
    nasdaq: MarketIndex = Field(default_factory=MarketIndex, description="纳斯达克")
    spx: MarketIndex = Field(default_factory=MarketIndex, description="标普500")
    a50: MarketIndex = Field(default_factory=MarketIndex, description="富时A50")
    hsi: MarketIndex = Field(default_factory=MarketIndex, description="恒生指数")
    usdcny: Optional[float] = Field(default=None, description="美元/人民币汇率")


class MacroAnalysisDetail(BaseModel):
    """Detailed macro environment assessment."""

    monetary_policy: str = Field(default="数据缺失", description="货币政策方向描述（基于公开数据）")
    fiscal_policy: str = Field(default="数据缺失", description="财政政策描述")
    overseas_impact: str = Field(default="数据缺失", description="海外环境对A股影响")
    data_freshness: str = Field(default="数据缺失", description="今日数据/昨日数据/数据缺失")


class MacroAnalysisReport(BaseModel):
    """Structured macro analysis."""

    global_markets: GlobalMarkets = Field(default_factory=GlobalMarkets)
    macro_analysis: MacroAnalysisDetail = Field(default_factory=MacroAnalysisDetail)
    macro_score: float = Field(ge=0.0, le=100.0, description="宏观面评分")
    macro_bias: str = Field(description="宏观方向: 偏多/中性偏多/中性/中性偏空/偏空")
    errors: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)


def render_macro_report(report: MacroAnalysisReport) -> str:
    """Render MacroAnalysisReport to markdown."""
    def render_index(label: str, index: MarketIndex) -> str:
        if index.close is None:
            return ""
        pct = "N/A" if index.pct is None else f"{index.pct:+.1f}%"
        return f"{label}: {index.close} ({pct})"

    return "\n".join([
        "## 宏观分析",
        "",
        f"**宏观面评分**: {report.macro_score:.0f}/100 ({report.macro_bias})",
        f"**货币政策**: {report.macro_analysis.monetary_policy}",
        f"**财政政策**: {report.macro_analysis.fiscal_policy}",
        f"**海外影响**: {report.macro_analysis.overseas_impact}",
        f"**数据时效**: {report.macro_analysis.data_freshness}",
        "",
        "### 全球市场",
        render_index("DJI", report.global_markets.dji),
        render_index("NASDAQ", report.global_markets.nasdaq),
        f"USD/CNY: {report.global_markets.usdcny}" if report.global_markets.usdcny is not None else "",
    ])


# ============================================================================
# Risk Screening
# ============================================================================


class ScreeningResult(BaseModel):
    """Per-stock risk screening flags."""

    st_risk: RiskFlag = Field(default=RiskFlag.UNKNOWN)
    pledge_risk: RiskFlag = Field(default=RiskFlag.UNKNOWN)
    goodwill_risk: RiskFlag = Field(default=RiskFlag.UNKNOWN)
    audit_risk: RiskFlag = Field(default=RiskFlag.UNKNOWN)
    cashflow_risk: RiskFlag = Field(default=RiskFlag.UNKNOWN)


class ChipAnalysis(BaseModel):
    """Per-stock chip/position analysis."""

    holder_trend: str = Field(default="", description="股东户数变化趋势")
    lockup_risk: str = Field(default="", description="限售解禁风险")
    block_trade_signal: str = Field(default="", description="大宗交易信号")


class RiskVerdict(BaseModel):
    """Per-stock overall risk verdict."""

    overall: RiskFlag = Field(default=RiskFlag.UNKNOWN)
    issues: List[str] = Field(default_factory=list, description="风险问题列表")
    chip_warnings: List[str] = Field(default_factory=list, description="筹码风险警告")


class RiskScreeningReport(BaseModel):
    """Structured risk screening for a batch of stocks."""

    screening: Dict[str, ScreeningResult] = Field(
        default_factory=dict, description="标的代码→排雷结果"
    )
    chip_analysis: Dict[str, ChipAnalysis] = Field(
        default_factory=dict, description="标的代码→筹码分析"
    )
    risk_verdicts: Dict[str, RiskVerdict] = Field(
        default_factory=dict, description="标的代码→风险结论"
    )
    risk_score: float = Field(ge=0.0, le=100.0, description="综合风控评分")
    risk_bias: str = Field(description="风险偏向")
    critical_alerts: List[str] = Field(default_factory=list, description="严重警报")
    errors: List[str] = Field(default_factory=list)


def render_risk_report(report: RiskScreeningReport) -> str:
    """Render RiskScreeningReport to markdown."""
    lines = ["## 风控审查", "", f"**风控评分**: {report.risk_score:.0f}/100 ({report.risk_bias})"]
    if report.critical_alerts:
        lines.append(f"**🚨 严重警报**: {'; '.join(report.critical_alerts)}")
    for code, verdict in report.risk_verdicts.items():
        lines.append(f"- **{code}**: {verdict.overall.value}")
        if verdict.issues:
            lines.append(f"  - 风险: {'; '.join(verdict.issues)}")
    return "\n".join(lines)


# ============================================================================
# Capital Flow / Institutional Flow
# ============================================================================


class DragonTigerPoolStock(BaseModel):
    """Per-pool-stock dragon tiger board data."""

    records: int = Field(default=0, description="上榜次数")
    institution_net: Optional[float] = Field(default=None, description="机构净买入(万元)")
    top_buy_seats: List[str] = Field(default_factory=list, description="TOP买入席位")


class DragonTiger(BaseModel):
    """Full dragon tiger board summary."""

    market_summary: Dict[str, object] = Field(default_factory=dict, description="全市场龙虎榜概况")
    pool_stocks: Dict[str, DragonTigerPoolStock] = Field(
        default_factory=dict, description="观察池标的龙虎榜详情"
    )


class MarginInfo(BaseModel):
    """Margin trading data for a single stock."""

    latest_date: str = Field(default="", description="最新数据日期")
    rzye_yi: Optional[float] = Field(default=None, description="融资余额(亿元)")
    trend: str = Field(default="", description="增加/下降/稳定")
    days_of_change: int = Field(default=0, description="连续变化天数")


class CapitalFlowReport(BaseModel):
    """Structured capital-flow / institutional-flow analysis."""

    dragon_tiger: DragonTiger = Field(default_factory=DragonTiger)
    margin: Dict[str, MarginInfo] = Field(default_factory=dict, description="融资融券数据")
    block_trades: Dict[str, Dict[str, object]] = Field(
        default_factory=dict, description="大宗交易"
    )
    northbound: NorthboundReport = Field(default_factory=NorthboundReport)
    capital_score: float = Field(ge=0.0, le=100.0, description="资金面评分")
    capital_bias: str = Field(description="资金面偏向: 偏多/中性偏多/中性/中性偏空/偏空")
    key_signals: List[str] = Field(default_factory=list, description="关键信号")
    errors: List[str] = Field(default_factory=list)


def render_capital_report(report: CapitalFlowReport) -> str:
    """Render CapitalFlowReport to markdown."""
    northbound_total = (
        "N/A" if report.northbound.total_yi is None else str(report.northbound.total_yi)
    )
    return "\n".join([
        "## 资金面",
        "",
        f"**资金面评分**: {report.capital_score:.0f}/100 ({report.capital_bias})",
        f"**北向资金**: {northbound_total}亿 ({report.northbound.bias})",
        "",
        "**关键信号**:",
    ] + [f"- {s}" for s in report.key_signals])


# ============================================================================
# Research Coverage
# ============================================================================


class ConsensusEPS(BaseModel):
    """Analyst consensus EPS estimates."""

    current_year: Optional[float] = Field(default=None, description="当年一致预期EPS")
    next_year: Optional[float] = Field(default=None, description="次年一致预期EPS")


class RecentReport(BaseModel):
    """A single analyst research report."""

    date: str = Field(description="报告日期")
    org: str = Field(description="机构名称")
    title: str = Field(description="报告标题")
    rating: Optional[str] = Field(default=None, description="评级")


class Announcement(BaseModel):
    """A single company announcement."""

    date: str = Field(description="公告日期")
    title: str = Field(description="公告标题")


class ResearchCoverageReport(BaseModel):
    """Structured research coverage / sell-side analysis."""

    coverage: Dict[str, object] = Field(
        default_factory=dict,
        description="覆盖情况: total_reports, recent_30d, institutions, consensus_rating, consensus_eps",
    )
    recent_reports: List[RecentReport] = Field(default_factory=list)
    announcements: List[Announcement] = Field(default_factory=list)
    research_score: float = Field(ge=0.0, le=100.0, description="研究面评分")
    key_finding: str = Field(description="核心发现")
    errors: List[str] = Field(default_factory=list)


def render_research_report(report: ResearchCoverageReport) -> str:
    """Render ResearchCoverageReport to markdown."""
    insts = report.coverage.get("institutions", [])
    return "\n".join([
        "## 研报覆盖",
        "",
        f"**研究面评分**: {report.research_score:.0f}/100",
        f"**覆盖机构**: {', '.join(insts) if isinstance(insts, list) else str(insts)}",
        f"**核心发现**: {report.key_finding}",
        f"**近期报告**: {len(report.recent_reports)}篇",
        f"**近期公告**: {len(report.announcements)}条",
    ])


# ============================================================================
# Review
# ============================================================================


class ReviewIssue(BaseModel):
    """A single issue found during review."""

    type: str = Field(description="问题类型: data/logic/risk/transport")
    severity: IssueSeverity = Field(description="严重程度")
    description: str = Field(description="问题描述")
    fix: str = Field(description="修复建议")


class ReviewResult(BaseModel):
    """Structured review output — mirrors review.md JSON format."""

    passed: bool = Field(description="是否通过")
    issues: List[ReviewIssue] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=100.0, description="审查评分")
    summary: str = Field(description="一句话结论")

    @model_validator(mode="after")
    def enforce_pass_invariants(self) -> "ReviewResult":
        has_blocking = any(
            issue.severity in {IssueSeverity.CRITICAL, IssueSeverity.MAJOR}
            for issue in self.issues
        )
        if self.passed and (self.score < 70 or has_blocking):
            raise ValueError("passed requires score >= 70 and no critical or major issues")
        return self


def render_review_result(result: ReviewResult) -> str:
    """Render ReviewResult to markdown."""
    lines = [
        "【Review Result】",
        f"结论: {'✅ 通过' if result.passed else '❌ 未通过'} (评分: {result.score:.0f}/100)",
        f"摘要: {result.summary}",
    ]
    if result.issues:
        lines.append("")
        lines.append("**问题**:")
        for i, iss in enumerate(result.issues):
            lines.append(f"{i+1}. [{iss.severity.value}] {iss.type}: {iss.description} → {iss.fix}")
    return "\n".join(lines)


# ============================================================================
# ETF Review
# ============================================================================


class ETFReviewResult(BaseModel):
    """Structured ETF review output."""

    passed: bool = Field(description="是否通过")
    etf_type: str = Field(description="识别的ETF类型")
    tracking_index_clear: bool = Field(default=False, description="跟踪指数是否清楚")
    underlying_clear: bool = Field(default=False, description="底层资产是否清楚")
    liquidity_adequate: bool = Field(default=False, description="流动性是否足够")
    premium_checked: bool = Field(default=False, description="折溢价是否检查")
    tracking_error_checked: bool = Field(default=False, description="跟踪误差是否检查")
    role_clear: bool = Field(default=False, description="组合角色是否明确")
    issues: List[ReviewIssue] = Field(default_factory=list)
    main_risks: List[str] = Field(default_factory=list, description="主要风险")
    conclusion: ReviewVerdict = Field(default=ReviewVerdict.PASS, description="审查结论")
    must_fix: List[str] = Field(default_factory=list, description="必须修正项")
    need_risk_agent: bool = Field(default=False, description="是否需要Risk Agent")

    @model_validator(mode="after")
    def enforce_pass_invariants(self) -> "ETFReviewResult":
        has_blocking = any(
            issue.severity in {IssueSeverity.CRITICAL, IssueSeverity.MAJOR}
            for issue in self.issues
        )
        if self.passed and (
            self.conclusion != ReviewVerdict.PASS or has_blocking or self.must_fix
        ):
            raise ValueError("passed requires PASS conclusion, no critical or major issues, and no must-fix items")
        return self


def render_etf_review_result(result: ETFReviewResult) -> str:
    """Render ETFReviewResult to markdown."""
    checks = [
        f"跟踪指数: {'✅' if result.tracking_index_clear else '❌'}",
        f"底层资产: {'✅' if result.underlying_clear else '❌'}",
        f"流动性: {'✅' if result.liquidity_adequate else '❌'}",
        f"折溢价: {'✅' if result.premium_checked else '❌'}",
        f"跟踪误差: {'✅' if result.tracking_error_checked else '❌'}",
        f"组合角色: {'✅' if result.role_clear else '❌'}",
    ]
    lines = [
        "【ETF Review】",
        f"ETF类型: {result.etf_type}",
        " | ".join(checks),
        f"结论: {result.conclusion.value}",
    ]
    if result.issues:
        lines.append(f"问题: {len(result.issues)}项")
    if result.must_fix:
        lines.append(f"必须修正: {'; '.join(result.must_fix)}")
    return "\n".join(lines)


# ============================================================================
# US Market subagent models (v5.2)
# ============================================================================


class IndexData(BaseModel):
    """Single index data point."""
    price: float
    five_day_return: float = Field(alias="5d_return")
    one_month_return: float = Field(alias="1m_return")
    three_month_return: float = Field(alias="3m_return")
    fifty_two_week_high_drawdown: float = Field(alias="52w_high_drawdown")
    above_50ma: bool
    above_200ma: bool
    volatility_60d: float


class SectorRotation(BaseModel):
    """Sector rotation classification."""
    trending_high: list[str] = Field(default_factory=list)
    pullback_opportunity: list[str] = Field(default_factory=list)
    weakening: list[str] = Field(default_factory=list)
    neutral: list[str] = Field(default_factory=list)


LEVERAGED_ETF_CONTRACTS = {
    # ticker: (direction, target leverage, exact stop loss %, max hold days)
    "TQQQ": ("long", 3.0, -5.0, 5),
    "UPRO": ("long", 3.0, -5.0, 5),
    "SPXL": ("long", 3.0, -5.0, 5),
    "SOXL": ("long", 3.0, -5.0, 5),
    "TECL": ("long", 3.0, -5.0, 5),
    "UDOW": ("long", 3.0, -5.0, 5),
    "SQQQ": ("inverse", 3.0, -5.0, 3),
    "SPXU": ("inverse", 3.0, -5.0, 3),
    "SOXS": ("inverse", 3.0, -5.0, 3),
    "TECS": ("inverse", 3.0, -5.0, 3),
    "SDOW": ("inverse", 3.0, -5.0, 3),
    "QLD": ("long", 2.0, -4.0, 8),
    "SSO": ("long", 2.0, -4.0, 8),
    "QID": ("inverse", 2.0, -4.0, 8),
    "SDS": ("inverse", 2.0, -4.0, 8),
}


class LeveragedETFPosition(BaseModel):
    """A bounded leveraged/inverse ETF tactical position."""

    ticker: str
    leverage: float = Field(gt=0, le=3)
    position_pct: float = Field(gt=0, le=12)
    stop_loss: float = Field(lt=0, ge=-8)
    max_hold_days: int = Field(gt=0, le=8)

    @model_validator(mode="after")
    def enforce_product_contract(self) -> "LeveragedETFPosition":
        ticker = self.ticker.upper()
        contract = LEVERAGED_ETF_CONTRACTS.get(ticker)
        if contract is None:
            raise ValueError("unsupported leveraged ETF ticker")
        _, expected_leverage, exact_stop_loss, max_hold = contract
        if self.leverage != expected_leverage:
            raise ValueError(f"{ticker} must use its {expected_leverage:g}x target leverage")
        if self.stop_loss != exact_stop_loss:
            raise ValueError(f"{ticker} stop_loss must equal {exact_stop_loss:g} percent")
        if self.max_hold_days > max_hold:
            raise ValueError(f"{ticker} max_hold_days must be <= {max_hold}")
        self.ticker = ticker
        return self


class LeveragedETFSignal(BaseModel):
    """Tactical signal that must allow the fail-closed avoid outcome."""

    direction: str = Field(default="avoid", pattern="^(long|inverse|avoid)$")
    inputs_complete: bool = False
    trend_confirmed: bool = False
    momentum_confirmed: bool = False
    liquidity_confirmed: bool = False
    volatility_confirmed: bool = False
    vix_value: Optional[float] = Field(default=None, ge=0)
    vix_level: str = "unknown"
    recommended: list[LeveragedETFPosition] = Field(default_factory=list)
    not_recommended: list[str] = Field(default_factory=list)
    rationale: str = ""

    @model_validator(mode="after")
    def enforce_avoid_and_exposure(self) -> "LeveragedETFSignal":
        if self.direction == "avoid" and self.recommended:
            raise ValueError("avoid direction cannot recommend leveraged positions")
        if self.direction != "avoid" and not self.recommended:
            raise ValueError("directional leveraged signal requires at least one supported product")
        confirmations = (
            self.inputs_complete,
            self.trend_confirmed,
            self.momentum_confirmed,
            self.liquidity_confirmed,
            self.volatility_confirmed,
        )
        if self.direction != "avoid" and not all(confirmations):
            raise ValueError("directional leveraged signal requires complete confirmed inputs")
        if self.direction != "avoid":
            if self.vix_value is None:
                raise ValueError("directional leveraged signal requires a current VIX value")
            vix_value = self.vix_value
            if vix_value > 30:
                raise ValueError("VIX above 30 requires avoid direction")
            if self.direction == "long" and vix_value >= 25:
                raise ValueError("long leveraged signal requires VIX below 25")
            if self.direction == "inverse" and not 25 <= vix_value <= 30:
                raise ValueError("inverse leveraged signal requires VIX between 25 and 30")
        tickers = {item.ticker for item in self.recommended}
        if tickers:
            expected_direction = {LEVERAGED_ETF_CONTRACTS[ticker][0] for ticker in tickers}
            if expected_direction != {self.direction}:
                raise ValueError("recommended products must match signal direction")
        exposure = sum(item.position_pct * item.leverage / 100 for item in self.recommended)
        if exposure > 0.5:
            raise ValueError("recommended leveraged notional exposure must be <= 0.5")
        return self


class USMarketDataReport(BaseModel):
    """US market data collection result."""
    indices: dict[str, IndexData]
    vix: dict[str, Any] = Field(default_factory=dict)
    dxy: dict[str, Any] = Field(default_factory=dict)
    tnx: dict[str, Any] = Field(default_factory=dict)
    sector_rotation: SectorRotation = Field(default_factory=SectorRotation)
    market_regime: str = "neutral"  # risk_on / risk_off / neutral
    position_advice: str = ""
    leveraged_signal: LeveragedETFSignal = Field(default_factory=LeveragedETFSignal)
    data_quality: DataQuality = DataQuality.B
    data_date: str = ""
    errors: list[str] = Field(default_factory=list)


class ValuationMetrics(BaseModel):
    """US stock valuation."""
    forward_pe: Optional[float] = None
    trailing_pe: Optional[float] = None
    ev_ebitda: Optional[float] = None
    peg: Optional[float] = None
    fcf_yield: Optional[float] = None


class GrowthMetrics(BaseModel):
    """Revenue/earnings/FCF growth and beat streak."""
    revenue_yoy: str = ""
    eps_yoy: str = ""
    fcf_yoy: str = ""
    revenue_beat_streak: int = 0
    eps_beat_streak: int = 0


class ProfitabilityMetrics(BaseModel):
    """Profitability ratios."""
    roe: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None


class BalanceSheetMetrics(BaseModel):
    """Key balance sheet strength indicators."""
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    cash_to_debt: Optional[float] = None
    goodwill_to_assets: Optional[float] = None


class PeerComparison(BaseModel):
    """Single peer comparison row."""
    ticker: str
    forward_pe: Optional[float] = None
    gross_margin: Optional[float] = None
    revenue_yoy: str = ""


class OCIQFResult(BaseModel):
    """OCIFQ five-dimension result for US stocks."""
    oligopoly: str = ""
    catalyst: str = ""
    industry_moat: str = ""
    financial_blast: str = ""
    quarterly_continuity: str = ""


class USFinancialReport(BaseModel):
    """US stock financial analysis report."""
    ticker: str
    company_name: str = ""
    currency: str = "USD"
    financial_score: int = Field(default=0, ge=0, le=100)
    valuation: ValuationMetrics = Field(default_factory=ValuationMetrics)
    growth: GrowthMetrics = Field(default_factory=GrowthMetrics)
    profitability: ProfitabilityMetrics = Field(default_factory=ProfitabilityMetrics)
    balance_sheet: BalanceSheetMetrics = Field(default_factory=BalanceSheetMetrics)
    peer_comparison: list[PeerComparison] = Field(default_factory=list)
    ocifq: OCIQFResult = Field(default_factory=OCIQFResult)
    accounting_notes: str = ""
    data_sources: list[str] = Field(default_factory=list)
    data_quality: DataQuality = DataQuality.B
    errors: list[str] = Field(default_factory=list)


class RiskCheckResult(BaseModel):
    """Single risk check result."""
    status: str = Field(pattern="^(pass|warn|fail|unknown)$")
    detail: str = ""


class USRiskReport(BaseModel):
    """US stock risk screening report."""
    ticker: str
    overall_risk: str = Field(default="medium", pattern="^(low|medium|high|critical|unknown)$")
    risk_score: int = Field(default=50, ge=0, le=100)  # higher = safer
    checks: dict[str, RiskCheckResult] = Field(default_factory=dict)
    critical_alerts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    risk_bias: str = ""
    data_sources: list[str] = Field(default_factory=list)
    data_quality: DataQuality = DataQuality.B
    errors: list[str] = Field(default_factory=list)
