# Auto Pool Management Pattern (2026-05-14)

## Problem
`pool_manager.py` had `scan` (detect) and `apply` (execute) as separate commands. News integration (`integrate-news`) only returned suggestions, never auto-executed. Result: pool changes were suggested but never applied.

## Solution: `auto` Command
Single command that chains: scan退池 → integrate-news入池 → apply → log to file.

```bash
python3 amadeus_pool_manager.py auto
```

### Execution Flow
1. `scan_pool()` — detect exit/downgrade conditions (止损/超时/赶顶)
2. `apply_actions()` — execute scan results, update session_context.json
3. `integrate_news()` — read latest news_scan_*.json, find sentiment≥3 stocks
4. Auto-apply news suggestions — add to context with pool/entry_date/reason
5. Write all changes to `~/.hermes/cache/amadeus/pool_changes.log`

### Log Format
```
[2026-05-14 15:34] 入池: 002031 巨轮智能 → B池 (机器人概念逆势拉升)
[2026-05-14 15:34] 退池: 002475 立讯精密 (亏损-5.9%超过退池止损线-5%)
[2026-05-14 15:34] 排雷失败: 688234 天岳先进 (无法获取行情数据)
```

### Integration
`collect_all.sh` calls `pool_manager.py auto` as step 6 (after screening, before market filter).

## User Intent Mapping

- **"执行退池"** → run `auto` (not just `scan`+`apply`). User expects both退池 AND入池 in one step. If you only do scan+apply, user will follow up with "入池也执行". Always use `auto` unless user explicitly says "只扫描不执行".
- **"自己判断一下精简吧"** → autonomous pool slimming (see below)

## Autonomous Pool Slimming (2026-05-18)

When pool gets bloated (B pool >15 stocks), proactively slim down without asking:

### Step-by-Step
1. Run `report` to see full pool state
2. Categorize stocks by theme/sector (e.g., 半导体, 白酒, 农业, 机器人)
3. For each theme: keep 1-2 with strongest logic (龙头, 浮盈最好, 基本面最硬)
4. Remove散票 (weak/no-core-thesis stocks)
5. Upgrade C→B for stocks with strong fundamentals (浮盈>10%, 核心标的)
6. Target: B pool 6-10 stocks, each with clear theme + trigger + exit condition

### Removal Priority (remove first → last)
1. Invalid codes (no data)
2. Redundant within theme (6只白酒→留龙头1只)
3. Scattered concept plays (同一概念6只→留最正宗1-2只)
4. Weak fundamentals + no catalyst
5. Duplicated across pools (A池已有→B池去掉)

### Batch Removal Pattern
Use `execute_code` with terminal calls. **⚠️ 50 tool call limit per execute_code invocation.** For >50 removals, split into multiple execute_code calls. Pattern:

```python
from hermes_tools import terminal
for code, reason in remove_list:
    r = terminal(f'/usr/bin/python3 ~/.hermes/scripts/amadeus/amadeus_pool_manager.py remove {code} "{reason}"')
```

For C→B upgrades (no CLI command), modify `session_context.json` directly:
```python
from hermes_tools import read_file, write_file
import json
ctx = json.loads(terminal('cat ~/.hermes/cache/amadeus/session_context.json')['output'])
notes = ctx['stock_notes']
notes[code]['pool'] = 'B'
write_file(path, json.dumps(ctx, ensure_ascii=False, indent=2))
```

## Pitfalls
1. **Price source mismatch**: pool_manager uses Sina API prices, which may differ from 腾讯 API used by sim_integrate. Can cause false退池 triggers.
2. **News入池 flood**: Strong热点 can generate 10+ 入池 at once (e.g., 碳化硅概念 → 8只). Consider adding deduplication or priority filtering.
3. **退池 vs 模拟盘持仓 conflict**: A stock can be退池'd by pool_manager while still held in simulator. These are independent systems — pool退池 doesn't auto-sell in simulator.
4. **execute_code 50-call limit**: Batch removal of >50 stocks requires splitting across multiple execute_code invocations. Count removals first.
5. **ETF not supported**: pool_manager.py only manages `stock_notes`. ETF pool requires separate `etf_notes` field and dedicated manager (not yet built).
