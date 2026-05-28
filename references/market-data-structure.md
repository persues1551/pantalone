# amadeus_data.py 输出结构 & 预测验证字段映射

## market_data JSON 结构

```json
{
  "collected_at": "2026-05-14T09:01:48",
  "market": {
    "date": "2026-05-14",
    "source": "新浪财经",
    "total": 5514,
    "up": 3215,        // ⚠️ 盘前为0！
    "down": 2133,      // ⚠️ 盘前为0！
    "flat": 166,
    "total_amount": 3.2637,  // 万亿
    "limit_up": 163,   // ⚠️ 这个字段盘前也可能为0
    "limit_down": 7,
    "breadth": 60.12
  },
  "indices": {
    "sh000001": {"name": "上证综指", "open": 4192.315, "close": 4242.572, "high": 4245.068, "low": 4192.315},
    "sz399001": {"name": "深证成指", "open": 15713.542, "close": 16089.749, "high": 16100.456, "low": 15713.542},
    "sz399006": {"name": "创业板指", "open": 3900.737, "close": 4038.333, "high": 4041.989, "low": 3893.803}
  },
  "pools": {
    "limit_up_count": 113,
    "limit_up_stocks": [
      {"代码": "001259", "名称": "利仁科技", "涨跌幅": 10.01},
      {"代码": "002777", "名称": "久远银海", "涨跌幅": 10.02}
    ],
    "limit_down_count": 2,
    "limit_down_stocks": [...],
    "break_board_count": 5,
    "break_rate": 4.2,
    "break_stocks": [...]
  },
  "lianban": [...],  // 连板数据
  "margin": {...},   // 融资融券
  "north": {...}     // 北向资金
}
```

## sectors 板块数据结构（2026-05-14 新增）

```json
{
  "sectors": {
    "total_count": 496,
    "top10": [
      {"板块名称": "氨纶", "涨跌幅": 5.04, "上涨家数": 1, "下跌家数": 0, "领涨股票": "华峰化学"},
      ...
    ],
    "bottom10": [
      {"板块名称": "教育", "涨跌幅": -2.15, "上涨家数": 0, "下跌家数": 8, "领涨股票": "中公教育"},
      ...
    ],
    "key_sectors": [
      {"name": "半导体材料", "change_pct": 1.29, "up_count": 11, "down_count": 18, "leader": "晶合集成"},
      {"name": "白酒Ⅱ", "change_pct": 0.73, "up_count": 15, "down_count": 3, "leader": "贵州茅台"},
      ...
    ]
  }
}
```

**验证逻辑**（2026-05-14修复后）：
- 资金主线：`sectors.key_sectors` 中目标板块 `change_pct > 0` 即可（不要求 up_count > down_count）
- 最弱方向：`sectors.key_sectors` 中目标板块 `change_pct < 0` 且 `down_count > up_count`
- 数据源：`ak.stock_board_industry_name_em()`（东方财富行业板块）

## match_dimension 字段提取路径

| 维度 | 提取路径 | 注意事项 |
|------|---------|---------|
| 指数方向 | `indices.sh000001.close` | 盘前有值（昨收） |
| 资金主线 | `sectors.key_sectors[].change_pct` | **2026-05-14改用板块涨跌幅** |
| 最强方向 | `pools.limit_up_stocks[].代码/名称` | 按股票名匹配 |
| 最弱方向 | `sectors.key_sectors[].change_pct` | **2026-05-14改用板块跌幅+下跌家数** |
| 风险点 | `pools.limit_up_count` | 对比阈值 |

## 板块关键词映射

涨停股名称不含大板块名，需映射：

```python
sector_keywords = {
    "半导体": ["半导体", "芯片", "存储", "封装", "晶圆", "封测", "EDA", "SOC"],
    "消费电子": ["电子", "VR", "MR", "苹果", "手机", "面板", "光学"],
    "电力": ["电力", "电网", "能源", "风电", "光伏", "核电"],
    "证券": ["证券", "券商"],
    "白酒": ["白酒", "酒"],
    "AI": ["AI", "人工智能", "算力", "数据中心"],
}
```

## 盘前数据陷阱

`amadeus_data.py` 在盘前（9:30前）运行时：
- `market.up/down` = 0（新浪API盘前返回全0）
- `indices.*.close` = 昨日收盘价（正常）
- `pools.limit_up_count` = 昨日数据（从cache读取）

验证逻辑必须处理这种情况：当 up=0 && down=0 时，用 pools 数据降级判断。
