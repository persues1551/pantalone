# JSON Cache File Structures

Cron jobs and scripts frequently read these cache files. The structures are non-obvious — field names, nesting, and types differ from what you might assume. This reference prevents wasted trial-and-error.

## market_YYYY-MM-DD.json

Path: `~/.hermes/cache/amadeus/market_YYYY-MM-DD.json`

```json
{
  "collected_at": "2026-05-28T...",
  "market": {
    "date": "2026-05-28",
    "source": "新浪财经",
    "total": 5523,        // total stocks
    "up": 3017,           // NOT "up_count"
    "down": 2365,         // NOT "down_count"
    "flat": 141,
    "total_amount": 2.9868, // 万亿
    "limit_up": 152,      // market-wide limit up count
    "limit_down": 13,
    "breadth": 56.06      // percentage
  },
  "indices": {
    "sh000001": {"name": "上证综指", "open": 4080.304, "close": 4098.636, "high": 4110.782, "low": 4055.828, "t_minus_2_close": 4093.727},
    "sz399001": {"name": "深证成指", ...},
    "sz399006": {"name": "创业板指", ...}
  },
  // ⚠️ No "change" field — compute from close vs t_minus_2_close
  "pools": {
    "limit_up_count": 102,
    "limit_up_stocks": [{"代码": "600726", "名称": "华电能源", "涨跌幅": 10.04}, ...],
    "limit_down_count": 8,
    "limit_down_stocks": [...],
    "break_board_count": 21,
    "break_rate": 17.1
  },
  "lianban": [{"代码": "002552", "名称": "宝鼎科技", "board_count": 10, "total_days": 16}, ...],
  "north": {"date": "20260528", "net_flow": 38.35, "hgt": 17.53, "sgt": 20.82, "source": "tushare"},
  "sector_flow": {
    "top_inflow": [{"板块": "通信设备", "涨跌幅": 3.04, "净流入": 148.3, "上涨家数": 77, "下跌家数": 13, "领涨股": "联特科技"}, ...],
    "top_outflow": [{"板块": "证券", "涨跌幅": -1.94, "净流入": -46.79}, ...],
    "key_flow": [{"name": "半导体", "net_inflow": 111.05, "change_pct": 2.24}, ...],
    "total_count": 90,
    "source": "ths"
  }
}
```

### Pitfalls
- `sector_flow` is a **dict** with `top_inflow`/`top_outflow`/`key_flow` keys, NOT a list
- Index change must be computed: `(close - t_minus_2_close) / t_minus_2_close * 100`
- `north.net_flow` is the key, not `north.total`
- `market.up` not `market.up_count`
- **`market.limit_up` vs `pools.limit_up_count`可能不同**（2026-06-05发现）：`market.limit_up`是新浪返回的所有收盘涨停股（如107只），`pools.limit_up_count`是从连板/首板统计的（如66只）。情绪温度脚本用的是pools数据，但市场总貌用的是market数据。报告中引用涨停数时需注明来源
- **指数数据在`d['indices']`下**，不在`d['market']`下。market只含总貌（up/down/flat/total_amount/limit_up等）
- **⚠️ indices可能过期（2026-06-08发现）**：amadeus_data.py采集的indices可能显示前一日收盘价，而market breadth是实时的。验证方法：比较两个日期文件的`indices.sh000001.close`，如果完全相同则indices未更新。修复：用腾讯API `qt.gtimg.cn` 直接获取真实收盘价

### Verifying Stale Indices

If `indices.sh000001.close` in today's file equals yesterday's file, the indices are stale. Get real values:

```python
# Write to /tmp/get_index.py then run via terminal()
import urllib.request
for code, name in [('sh000001','上证'), ('sz399001','深成'), ('sz399006','创业板')]:
    url = f'http://qt.gtimg.cn/q={code}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    parts = resp.read().decode('gbk', errors='replace').split('~')
    # parts[3]=current, parts[4]=prev_close, parts[31]=change, parts[32]=pct
    print(f'{name}: {parts[3]} ({parts[32]}%)')
```

**Stock code prefixes**: 600xxx/601xxx/688xxx → `sh`, 000xxx/002xxx/300xxx/301xxx → `sz`

## pool_state.json

Path: `~/.hermes/cache/amadeus/pool_state.json`

```json
{
  "updated": "2026-05-26T18:03:38",
  "data_source": "OCIFQ+ML全市场扫描",
  "summary": {"total": 12, "a_pool": 0, "b_pool": 10, "c_pool": 2, "recently_removed": 0, "warnings": 0},
  "pools": {
    "A池": {"description": "长期价值·核心持仓", "stocks": []},
    "B池": {
      "description": "趋势跟踪·中期持仓",
      "stocks": {
        "002185": {"code": "002185", "name": "", "pnl_pct": 0, "price": 17.0, "status": "观察"},
        "300502": {"code": "300502", "name": "", "pnl_pct": 0, "price": 659.0, "status": "观察"}
      }
    },
    "C池": {"description": "事件驱动·短期持仓", "stocks": {"301538": {...}, "601991": {...}}}
  }
}
```

### Pitfalls
- `pools["B池"]["stocks"]` is a **dict keyed by stock code**, NOT a list
- Access: `pools["B池"]["stocks"]["002185"]` not `pools["B池"]["stocks"][0]`
- Pool names are Chinese: "A池", "B池", "C池"
- `name` field may be empty string — use code for display
- `pnl_pct` may be 0 if not updated recently

## emotion_YYYY-MM-DD.json

Path: `~/.hermes/cache/amadeus/emotion_YYYY-MM-DD.json`

**⚠️ 结构已变更（2026-06-05验证）**：输出不再包含`dimensions`字典，改为扁平化结构。

```json
{
  "score": 58,
  "level": "升温",
  "components": {
    "涨停跌停比": {"score": 8.1, "max": 25, "detail": "57涨/35跌 比值1.6"},
    "市场宽度": {"score": 11.9, "max": 25, "detail": "涨停57只(代理)"},
    "连板高度": {"score": 20, "max": 20, "detail": "最高10板"},
    "炸板率": {"score": 3, "max": 15, "detail": "跌停35只(代理)"},
    "成交额变化": {"score": 15, "max": 15, "detail": "成交额28229亿"}
  },
  "missing": [],
  "weights_used": 100,
  "weights_total": 100,
  "data_completeness": "100/100",
  "data_freshness": "fresh"
}
```

### Pitfalls
- **`components`是dict（2026-06-08验证）**：每个维度有`score`/`max`/`detail`三个字段，不是简单列表。旧文档说"各维度分数详情只在控制台输出中"已不准确
- **`level`字段是中文**："退潮"/"升温"/"过热"等
- **`score`是总分**（满分100），直接使用即可
- **情绪温度可能与实际体感严重脱节**（2026-06-08实例）：score=58"升温"但实际涨跌比898:4591(16%上涨)。原因：市场宽度因子用`pools.limit_up_count`(57只连板统计)而非`market.limit_up`(80只全市场涨停)。当跌停>涨停时，连板高度(10板)和成交额(2.8万亿)仍给高分，拉高总分

## global_YYYY-MM-DD.json

Path: `~/.hermes/cache/amadeus/global_YYYY-MM-DD.json`

```json
{
  "collected_at": "2026-05-28T...",
  "dji": {"close": 50644.28, "pct": 0.0, "source": "akshare_sina"},
  "nasdaq": {"close": 26674.73, "pct": 0.0, "source": "akshare_sina"},
  "spx": null,     // may be null if collection failed
  "a50": null,
  "hsi": {"close": 25328.23, "pct": 0.0, "source": "akshare_sina"},
  "usdcny": null
}
```

### Pitfalls
- `pct` may be 0.0 even when market moved (AKShare Sina returns stale data)
- Multiple fields may be `null` — always check before accessing

## decision_log.json

Path: `~/.hermes/cache/amadeus/decision_log.json`

**⚠️ 实际结构（2026-06-05验证）与旧文档不同**。顶层keys=`version/created/entries/stats`。

```json
{
  "version": "1.0",
  "created": "2026-05-30",
  "entries": [
    {
      "id": "20260605-01",
      "date": "2026-06-06",
      "type": "大盘方向",
      "prediction": "震荡偏弱（55%），4030-4070区间",
      "confidence": 0.55,
      "status": "pending",
      "source": "evening_review"
    }
  ],
  "stats": {
    "total_predictions": 58,
    "verified": 39,
    "hits": 27,
    "misses": 12
  }
}
```

### Pitfalls
- **entries是扁平结构**：每条entry直接含`type`/`prediction`/`confidence`/`status`，不是嵌套在`predictions`数组中
- **stats字段**：`verified`+`hits`+`misses`（非`total_hits`/`hit_rate`/`by_type`）
- **无`rolling_window`/`rolling_hit_rate`/`by_type`字段**：这些在旧文档中存在但实际JSON没有
- **id格式**：YYYYMMDD-NN（NN从01递增，同日多条）
- **status**：`pending` → `verified` → `miss`/`hit`
- **写入时机**：晚间复盘写入预判，收盘复盘验证+写入新预判
- **读取方式**：用`terminal("cat file")`或`execute_code`中的`open()`，不要用`read_file`（带行号前缀）

## Safe JSON Reading Pattern

**Never** use `cat file.json | python3 -c "..."` — security scan blocks pipe-to-interpreter.

**Always** use `execute_code`:
```python
import json
with open('/path/to/file.json') as f:
    d = json.load(f)
# then access d['market']['up'] etc.
```

## ⚠️ Read Before You Code (2026-06-08)

**铁律**：写任何解析JSON缓存文件的代码前，必须先读本文件确认结构。

反面案例：写代码假设`pools["B池"]["stocks"]`是list并用`stocks[:3]`切片，实际是dict keyed by stock code，触发`TypeError: unhashable type: 'slice'`。

正确做法：
```python
stocks = pools["B池"]["stocks"]  # dict, not list
for code, info in list(stocks.items())[:3]:
    print(code, info.get("name", ""))
```
