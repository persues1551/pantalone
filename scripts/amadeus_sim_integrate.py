#!/usr/bin/python3
"""
Amadeus 模拟盘集成脚本 v1.0
用于读取模拟盘状态。daily_update/record 会写入状态，必须获得用户逐次明确授权。

用法：
  python3 amadeus_sim_integrate.py status      # 获取当前状态（JSON）
  python3 amadeus_sim_integrate.py daily_update --authorized # 授权后更新今日盈亏
  python3 amadeus_sim_integrate.py record <json> --authorized # 授权后记录交易
"""
import sqlite3
import json
import sys
import os
from datetime import datetime, date
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
DB_PATH = HERMES_HOME / "cache" / "amadeus" / "simulator.db"
INIT_CAPITAL = 200000.0
POOL_STOP_LOSS = {"A+": 0.10, "A": 0.10, "B": 0.05, "C": 0.03}


def calculate_stop_loss(price, pool):
    """Calculate the authoritative A+/A/B/C pool stop price."""
    if pool not in POOL_STOP_LOSS:
        raise ValueError(f"未知股票池: {pool}")
    return round(price * (1 - POOL_STOP_LOSS[pool]), 2)


def write_authorized(args):
    """Require an explicit flag for every state-writing CLI invocation."""
    return "--authorized" in args

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_status():
    """获取模拟盘完整状态"""
    conn = get_conn()
    cur = conn.execute("SELECT * FROM positions WHERE status='holding'")
    positions = [dict(row) for row in cur.fetchall()]
    cur = conn.execute("SELECT * FROM positions WHERE status='closed'")
    closed = [dict(row) for row in cur.fetchall()]
    cur = conn.execute("SELECT * FROM trades ORDER BY date DESC LIMIT 20")
    trades = [dict(row) for row in cur.fetchall()]
    cur = conn.execute("SELECT * FROM daily_pnl ORDER BY date DESC LIMIT 10")
    daily_pnl = [dict(row) for row in cur.fetchall()]
    total_pnl = sum(p.get('pnl', 0) or 0 for p in closed)
    total_value = INIT_CAPITAL + total_pnl
    conn.close()
    return {
        "initial_capital": INIT_CAPITAL,
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl / INIT_CAPITAL * 100, 2),
        "positions_count": len(positions),
        "positions": positions,
        "closed_count": len(closed),
        "closed_trades": closed,
        "recent_trades": trades,
        "daily_pnl": daily_pnl
    }

def daily_update(authorized=False):
    """更新今日盈亏（需要提供当前价格）"""
    if not authorized:
        return {"error": "explicit_authorization_required"}
    conn = get_conn()
    today = str(date.today())
    cur = conn.execute("SELECT * FROM daily_pnl WHERE date=?", (today,))
    if cur.fetchone():
        conn.close()
        return {"status": "already_recorded", "date": today}
    cur = conn.execute("SELECT * FROM positions WHERE status='holding'")
    positions = [dict(row) for row in cur.fetchall()]
    positions_value = sum(p.get('buy_price', 0) * p.get('shares', 0) for p in positions)
    cur = conn.execute("SELECT SUM(pnl) as total_pnl FROM positions WHERE status='closed'")
    closed_pnl = cur.fetchone()['total_pnl'] or 0
    cash = INIT_CAPITAL + closed_pnl - positions_value
    total_value = cash + positions_value
    cur = conn.execute("SELECT total_value FROM daily_pnl ORDER BY date DESC LIMIT 1")
    prev = cur.fetchone()
    prev_value = prev['total_value'] if prev else INIT_CAPITAL
    pnl_day = total_value - prev_value
    cur = conn.execute("SELECT MAX(total_value) as peak FROM daily_pnl")
    peak = cur.fetchone()['peak'] or INIT_CAPITAL
    peak = max(peak, total_value)
    drawdown = (peak - total_value) / peak * 100 if peak > 0 else 0
    conn.execute("""
        INSERT INTO daily_pnl (date, total_value, cash, positions_value, pnl_day, pnl_total, drawdown)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (today, round(total_value, 2), round(cash, 2), round(positions_value, 2),
          round(pnl_day, 2), round(closed_pnl, 2), round(drawdown, 2)))
    conn.commit()
    conn.close()
    return {
        "status": "recorded", "date": today,
        "total_value": round(total_value, 2), "cash": round(cash, 2),
        "positions_value": round(positions_value, 2), "pnl_day": round(pnl_day, 2),
        "pnl_total": round(closed_pnl, 2), "drawdown": round(drawdown, 2)
    }

def record_trade(trade_json, authorized=False):
    """记录交易"""
    if not authorized:
        return {"error": "explicit_authorization_required"}
    try:
        trade = json.loads(trade_json)
    except json.JSONDecodeError as e:
        return {"error": f"JSON解析失败: {e}"}
    conn = get_conn()
    today = str(date.today())
    action = trade.get('action', 'buy')
    code = trade.get('code', '')
    name = trade.get('name', '')
    pool = trade.get('pool', 'C')
    price = trade.get('price', 0)
    shares = trade.get('shares', 0)
    reason = trade.get('reason', '模拟交易')
    if action == 'buy':
        try:
            stop_loss = calculate_stop_loss(price, pool)
        except ValueError as exc:
            conn.close()
            return {"error": str(exc)}
        conn.execute("""
            INSERT INTO positions (code, name, pool, buy_date, buy_price, shares, stop_loss, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'holding')
        """, (code, name, pool, today, price, shares, stop_loss))
        conn.execute("""
            INSERT INTO trades (code, action, price, shares, amount, date, reason)
            VALUES (?, 'buy', ?, ?, ?, ?, ?)
        """, (code, price, shares, round(price * shares, 2), today, reason))
    elif action == 'sell':
        position_id = trade.get('position_id')
        if not position_id:
            conn.close()
            return {"error": "平仓需要提供position_id"}
        cur = conn.execute("SELECT * FROM positions WHERE id=? AND status='holding'", (position_id,))
        pos = cur.fetchone()
        if not pos:
            conn.close()
            return {"error": f"持仓ID {position_id} 不存在或已平仓"}
        pos = dict(pos)
        pnl = round((price - pos['buy_price']) * pos['shares'], 2)
        pnl_pct = round((price - pos['buy_price']) / pos['buy_price'] * 100, 2)
        conn.execute("""
            UPDATE positions SET status='closed', close_date=?, close_price=?, pnl=?, pnl_pct=?, notes=?
            WHERE id=?
        """, (today, price, pnl, pnl_pct, reason, position_id))
        conn.execute("""
            INSERT INTO trades (code, action, price, shares, amount, date, reason)
            VALUES (?, 'sell', ?, ?, ?, ?, ?)
        """, (code, price, pos['shares'], round(price * pos['shares'], 2), today, reason))
    conn.commit()
    conn.close()
    return {"status": "recorded", "action": action, "code": code, "price": price, "shares": shares}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 amadeus_sim_integrate.py [status|daily_update|record <json>]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "status":
        print(json.dumps(get_status(), ensure_ascii=False, indent=2))
    elif cmd == "daily_update":
        if not write_authorized(sys.argv[1:]):
            print("拒绝写入：daily_update 需要用户逐次明确授权并传入 --authorized")
            sys.exit(2)
        print(json.dumps(daily_update(authorized=True), ensure_ascii=False, indent=2))
    elif cmd == "record":
        if len(sys.argv) < 3:
            print("用法: python3 amadeus_sim_integrate.py record '<json>' --authorized")
            sys.exit(1)
        if not write_authorized(sys.argv[1:]):
            print("拒绝写入：record 需要用户逐次明确授权并传入 --authorized")
            sys.exit(2)
        print(json.dumps(record_trade(sys.argv[2], authorized=True), ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
