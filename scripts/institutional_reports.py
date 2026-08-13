#!/usr/bin/env python3
"""A股机构研报采集与结构化分析（东财研报中心）。

数据源：https://reportapi.eastmoney.com/report/list （免 key，大陆直连）
实测要点（2026-08-13）：
- code 必须用裸代码（如 600519）；sh600519/SH600519/1.600519 均返回空
- 字段：title/orgSName/publishDate/emRatingName/sRatingName/lastRatingName/
  predictThisYearEps/predictNextYearEps/predictThisYearPe/predictNextYearPe/infoCode
- PDF：https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf（application/pdf，可用）

用法：
  python3 institutional_reports.py 600519                # 个股研报摘要
  python3 institutional_reports.py 600519 300750        # 多股
  python3 institutional_reports.py 600519 --days 90     # 近90天
  python3 institutional_reports.py 600519 --download .  # 并下载PDF
  python3 institutional_reports.py --market --limit 20  # 全市场最新
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
REPORT_API = "https://reportapi.eastmoney.com/report/list"
PDF_TPL = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"
_MIN_INTERVAL = 1.0  # 东财限流：串行最小间隔
_last_call: List[float] = [0.0]

# 东财评级 → 标准口径（保留原值用于展示）
RATING_ORDER = ["买入", "增持", "持有", "中性", "减持", "卖出", "回避", "区间操作"]
_RATING_SYNONYMS = {
    "买进": "买入",
    "强烈推荐": "买入",
    "推荐": "买入",
    "优于大市": "增持",
    "跑赢行业": "增持",
    "outperform": "增持",
    "买入(buy)": "买入",
    "买入(Buy)": "买入",
    "买进(Buy)": "买入",
    "增持(outperform)": "增持",
    "持有(hold)": "持有",
    "区间操作(tranding buy)": "区间操作",
    "区间操作(Tranding Buy)": "区间操作",
}


def _throttle() -> None:
    wait = _MIN_INTERVAL - (time.monotonic() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.monotonic()


def _get(url: str, timeout: int = 30) -> Dict[str, Any]:
    _throttle()
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def fetch_reports(
    code: Optional[str] = "*",
    days: int = 180,
    page_size: int = 100,
    max_pages: int = 5,
    qtype: str = "0",
) -> List[Dict[str, Any]]:
    """拉取研报列表。code 为裸代码或 '*'（全市场）。返回原始记录。"""
    if code is None:
        code = "*"
    code = str(code).strip()
    if code not in ("*", "") and not re.fullmatch(r"\d{6}", code):
        raise ValueError(
            f"code 必须为裸6位代码或 '*'，收到 {code!r}（sh600519 等形式返回空）"
        )
    end = _dt.date.today()
    begin = end - _dt.timedelta(days=days)
    all_records: List[Dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*",
            "pageSize": str(page_size),
            "industry": "*",
            "rating": "*",
            "ratingChange": "*",
            "beginTime": begin.strftime("%Y-%m-%d"),
            "endTime": end.strftime("%Y-%m-%d"),
            "pageNo": str(page),
            "qType": qtype,
            "code": code,
        }
        url = REPORT_API + "?" + urllib.parse.urlencode(params)
        payload = _get(url)
        rows = payload.get("data") or []
        if not rows:
            break
        all_records.extend(rows)
        total_page = int(payload.get("TotalPage") or 1)
        if page >= total_page:
            break
    return all_records


def _norm_rating(raw: Any) -> str:
    if not raw:
        return ""
    text = str(raw).strip()
    if not text:
        return ""
    lower = text.lower()
    for syn, std in _RATING_SYNONYMS.items():
        if syn.lower() == lower:
            return std
    if text in RATING_ORDER:
        return text
    return text


def _as_float(value: Any) -> Optional[float]:
    if value in (None, "", "None"):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _date_only(value: Any) -> str:
    text = str(value or "")
    return text[:10]


def normalize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """清洗记录：标准化评级、数值化 EPS/PE、日期截断、按日期倒序。"""
    out = []
    for row in records:
        rating = _norm_rating(row.get("emRatingName"))
        last_rating = _norm_rating(row.get("lastRatingName"))
        out.append({
            "title": str(row.get("title") or "").strip(),
            "org": str(row.get("orgSName") or "").strip(),
            "date": _date_only(row.get("publishDate")),
            "rating": rating,
            "raw_rating": str(row.get("sRatingName") or "").strip(),
            "rating_change": (
                f"{last_rating}→{rating}"
                if last_rating and rating and last_rating != rating
                else ""
            ),
            "eps_this_year": _as_float(row.get("predictThisYearEps")),
            "eps_next_year": _as_float(row.get("predictNextYearEps")),
            "pe_this_year": _as_float(row.get("predictThisYearPe")),
            "pe_next_year": _as_float(row.get("predictNextYearPe")),
            "info_code": str(row.get("infoCode") or ""),
        })
    out.sort(key=lambda r: r["date"], reverse=True)
    return out


def rating_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """评级分布、分歧检测、评级变化统计。"""
    ratings = [r["rating"] for r in records if r["rating"]]
    rating_counts = dict(Counter(ratings))
    changes = [r for r in records if r["rating_change"]]
    distinct = set(ratings)
    eps_this = [r["eps_this_year"] for r in records if r["eps_this_year"] is not None]
    eps_next = [r["eps_next_year"] for r in records if r["eps_next_year"] is not None]
    return {
        "total": len(records),
        "orgs": sorted({r["org"] for r in records if r["org"]}),
        "rating_counts": rating_counts,
        "rating_disagreement": (
            len(distinct) >= 2
            and ({"买入", "增持"} & distinct)
            and bool({"持有", "中性", "减持", "卖出", "回避", "区间操作"} & distinct)
        ),
        "distinct_ratings": sorted(distinct),
        "rating_changes": changes,
        "eps_this_year_range": [min(eps_this), max(eps_this)] if eps_this else None,
        "eps_next_year_range": [min(eps_next), max(eps_next)] if eps_next else None,
    }


def coverage_gap(records: List[Dict[str, Any]], days: int = 30) -> bool:
    """近 days 天内无研报覆盖 → True（用于报告标注'无近期机构覆盖'）。"""
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).isoformat()
    return not any(r["date"] >= cutoff for r in records)


def download_pdf(record: Dict[str, Any], target_dir: str | Path = ".") -> Optional[str]:
    """下载单份研报 PDF，返回保存路径；失败返回 None。"""
    info_code = record.get("info_code") or record.get("infoCode") or ""
    if not info_code:
        return None
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    date = record.get("date", "")
    org = record.get("org", "unknown")
    title = re.sub(r'[\\/:*?"<>|]', "_", record.get("title", ""))[:80]
    dest = target / f"{date}_{org}_{title}.pdf"
    if dest.exists():
        return str(dest)
    url = PDF_TPL.format(info_code=urllib.parse.quote(info_code))
    _throttle()
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if len(data) < 1024 or not data.lstrip().startswith(b"%PDF"):
            return None
        dest.write_bytes(data)
        return str(dest)
    except Exception:
        return None


def summarize(
    code: Optional[str] = "*",
    days: int = 180,
    download_dir: Optional[str] = None,
    max_pages: int = 5,
) -> Dict[str, Any]:
    """单代码/全市场研报结构化摘要。"""
    records = fetch_reports(code=code, days=days, max_pages=max_pages)
    normalized = normalize_records(records)
    summary = rating_summary(normalized)
    downloaded: List[str] = []
    if download_dir and normalized:
        for record in normalized[:3]:
            path = download_pdf(record, download_dir)
            if path:
                downloaded.append(path)
    result: Dict[str, Any] = {
        "code": code,
        "window_days": days,
        "as_of": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": normalized,
        "summary": summary,
        "no_recent_coverage": coverage_gap(normalized),
        "downloads": downloaded,
    }
    return result


def _render_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    code = result["code"]
    header = "全市场最新研报" if code == "*" else f"个股 {code} 机构研报"
    lines.append(f"# {header}（近{result['window_days']}天，as_of {result['as_of']}）")
    summary = result["summary"]
    if summary["total"] == 0:
        lines.append("")
        lines.append("无研报数据。")
        return "\n".join(lines)
    lines.append("")
    lines.append(f"- 研报数：{summary['total']}")
    lines.append(f"- 覆盖券商：{', '.join(summary['orgs'])}")
    lines.append(f"- 评级分布：{summary['rating_counts']}")
    lines.append(f"- 评级分歧：{'是' if summary['rating_disagreement'] else '否'}")
    # 全市场模式跨股票合并 EPS 区间没有意义（不同标的量纲不同），只个股模式输出
    if code != "*" and summary["eps_this_year_range"]:
        lo, hi = summary["eps_this_year_range"]
        lines.append(f"- 今年EPS预测区间：{lo:g} ~ {hi:g}")
    if code != "*" and summary["eps_next_year_range"]:
        lo, hi = summary["eps_next_year_range"]
        lines.append(f"- 明年EPS预测区间：{lo:g} ~ {hi:g}")
    if summary["rating_changes"]:
        lines.append("- 评级变化：")
        for change in summary["rating_changes"][:5]:
            lines.append(
                f"  - {change['date']} {change['org']}：{change['rating_change']}"
            )
    if result["no_recent_coverage"]:
        lines.append("- ⚠️ 近30天无研报覆盖。")
    lines.append("")
    lines.append("| 日期 | 券商 | 评级 | 今年EPS | 明年EPS | 今年PE | 明年PE | 标题 |")
    lines.append("|------|------|------|--------|--------|--------|--------|------|")
    for r in result["records"]:
        lines.append(
            f"| {r['date']} | {r['org']} | {r['rating']} | "
            f"{r['eps_this_year'] if r['eps_this_year'] is not None else ''} | "
            f"{r['eps_next_year'] if r['eps_next_year'] is not None else ''} | "
            f"{r['pe_this_year'] if r['pe_this_year'] is not None else ''} | "
            f"{r['pe_next_year'] if r['pe_next_year'] is not None else ''} | "
            f"{r['title']} |"
        )
    if result["downloads"]:
        lines.append("")
        lines.append("已下载PDF：")
        for path in result["downloads"]:
            lines.append(f"- {path}")
    lines.append("")
    lines.append("> 研报为参考证据，不构成交易指令；引用需注明券商与日期。")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="A股机构研报采集与结构化分析")
    parser.add_argument("codes", nargs="*", help="裸6位代码，可多个；缺省为全市场")
    parser.add_argument("--days", type=int, default=180, help="回溯窗口（天）")
    parser.add_argument("--market", action="store_true", help="全市场最新研报")
    parser.add_argument("--limit", type=int, default=20, help="全市场模式 pageSize")
    parser.add_argument("--download", metavar="DIR", help="下载前N份研报PDF")
    parser.add_argument("--json", action="store_true", help="输出JSON")
    args = parser.parse_args(argv)

    if args.market or not args.codes:
        codes: List[str] = ["*"]
    else:
        codes = args.codes

    if args.market:
        # 全市场模式只取最新一页，避免大窗口翻页
        records = fetch_reports(code="*", days=args.days, page_size=args.limit, max_pages=1)
        normalized = normalize_records(records)
        result = {
            "code": "*",
            "window_days": args.days,
            "as_of": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "records": normalized,
            "summary": rating_summary(normalized),
            "no_recent_coverage": False,
            "downloads": [],
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(_render_text(result))
        return 0

    all_results: List[Dict[str, Any]] = []
    for code in codes:
        try:
            result = summarize(
                code=code,
                days=args.days,
                download_dir=args.download,
            )
            all_results.append(result)
        except Exception as exc:  # noqa: BLE001 — CLI 层统一报错
            all_results.append({
                "code": code,
                "error": f"{type(exc).__name__}: {exc}",
            })
    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
    else:
        for result in all_results:
            if "error" in result:
                print(f"# {result['code']} 查询失败：{result['error']}")
            else:
                print(_render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
