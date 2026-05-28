#!/usr/bin/env python3
"""Amadeus Token 消耗审计脚本

从 Hermes session JSON 文件提取实际 API token 消耗。
计算每轮会话的累积上下文效应，估算推理 token 开销。

用法:
  python3 token_audit.py                     # 审计今天所有 session
  python3 token_audit.py 2026-05-12          # 审计指定日期
  python3 token_audit.py --cron-only         # 只看 cron 推送
  python3 token_audit.py --top 5             # Top N 消耗会话
"""

import json, glob, os, sys
from datetime import date

SESSIONS_DIR = os.path.expanduser("~/.hermes/sessions")

def token_estimate_chinese(chars):
    """中英文混合 token 估算。中文约 1.3 tok/字，JSON 约 0.4 tok/字。"""
    return int(chars * 0.6)

def token_estimate_json(chars):
    return int(chars * 0.3)

def audit_session(filepath):
    """返回单 session 的 token 分解"""
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception:
        return None

    msgs = data.get("messages", [])
    sp = data.get("system_prompt", "")
    tools = json.dumps(data.get("tools", []))

    sp_tok = token_estimate_chinese(len(sp))
    tools_tok = token_estimate_json(len(tools))
    num_tools = len(data.get("tools", []))

    # 模拟真实 API 调用：每轮累积上下文
    api_input = 0
    api_output = 0
    running_chars = 0
    turns = 0

    for m in msgs:
        role = m.get("role", "?")
        c = m.get("content", "")
        if isinstance(c, list):
            c = json.dumps(c)
        running_chars += len(c)

        if role == "user":
            turns += 1
            api_input += sp_tok + tools_tok + token_estimate_chinese(running_chars)
        elif role == "assistant" and len(c) > 50:
            api_output += token_estimate_chinese(len(c))

    # 估算推理 token（reasoning_effort: medium ≈ 5x output）
    reasoning_est = int(api_output * 5) if api_output > 0 else 0

    return {
        "file": os.path.basename(filepath),
        "turns": turns,
        "msgs": len(msgs),
        "tools": num_tools,
        "sp_tok": sp_tok,
        "tools_tok": tools_tok,
        "input_tok": api_input,
        "output_tok": api_output,
        "reasoning_est": reasoning_est,
        "total_est": api_input + api_output + reasoning_est,
    }


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%Y%m%d")
    cron_only = "--cron-only" in sys.argv
    top_n = 10
    for i, a in enumerate(sys.argv):
        if a == "--top" and i + 1 < len(sys.argv):
            top_n = int(sys.argv[i + 1])

    pattern = f"{SESSIONS_DIR}/session_{target_date}*.json"
    if not cron_only:
        pattern_cron = f"{SESSIONS_DIR}/session_cron_*{target_date}*.json"
        files = glob.glob(pattern) + glob.glob(pattern_cron)
    else:
        files = glob.glob(f"{SESSIONS_DIR}/session_cron_*{target_date}*.json")

    files = sorted(set(files))

    results = []
    for f in files:
        r = audit_session(f)
        if r and r["turns"] > 0:
            results.append(r)

    results.sort(key=lambda x: -x["total_est"])

    # Header
    print(f"\n{'='*80}")
    print(f"  Amadeus Token 审计 — {target_date}")
    print(f"  Sessions: {len(results)} | DeepSeek v4-pro | reasoning_effort: medium")
    print(f"{'='*80}\n")

    # Summary
    total_in = sum(r["input_tok"] for r in results)
    total_out = sum(r["output_tok"] for r in results)
    total_reasoning = sum(r["reasoning_est"] for r in results)
    grand = total_in + total_out + total_reasoning

    pct_in = total_in * 100 // grand if grand else 0
    pct_out = total_out * 100 // grand if grand else 0
    pct_r = total_reasoning * 100 // grand if grand else 0

    print(f"      常规输入: {total_in:>12,}  tok ({pct_in}%)")
    print(f"      常规输出: {total_out:>12,}  tok ({pct_out}%)")
    print(f"      推理(估): {total_reasoning:>12,}  tok ({pct_r}%)")
    print(f"      {'─'*40}")
    print(f"      总计(估): {grand:>12,}  tok")
    print(f"      费用(估): ${grand/1e6*2:.2f} (input $2/M, output $8/M blended)\n")

    # Top sessions
    print(f"  TOP {min(top_n, len(results))} 消耗会话:")
    print(f"  {'Session':<48} {'Turns':>5} {'常规':>10} {'推理':>10} {'合计':>10}")
    print(f"  {'─'*83}")
    for r in results[:top_n]:
        reg = r["input_tok"] + r["output_tok"]
        print(f"  {r['file']:<48} {r['turns']:>5} {reg:>10,} {r['reasoning_est']:>10,} {r['total_est']:>10,}")

    print()


if __name__ == "__main__":
    main()
