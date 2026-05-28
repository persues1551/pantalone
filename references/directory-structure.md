# Amadeus 项目目录结构

> 2026-05-12 整理后生效。新文件严格按此结构存放。

```
~/.hermes/
├── skills/investment/amadeus/    # Amadeus 技能定义
│   ├── SKILL.md                  # 核心技能文件
│   └── references/               # 参考文档（数据源、结构等）
├── scripts/amadeus/              # 数据采集脚本（8个）
│   ├── amadeus_data.py           # 市场总貌、指数、涨跌停
│   ├── amadeus_global.py         # 外围市场（美股、A50、港股）
│   ├── amadeus_indicators.py     # 技术指标（MA/MACD/RSI）
│   ├── amadeus_financials.py     # 个股财报
│   ├── amadeus_news.py           # 财联社电报
│   ├── amadeus_simulator.py      # SQLite 模拟盘引擎
│   └── amadeus_collect_all.sh    # 一键全采集
├── cache/amadeus/                # 缓存数据
│   ├── market_YYYY-MM-DD.json    # 市场总貌缓存
│   ├── global_YYYY-MM-DD.json    # 外围市场缓存
│   ├── sector_flow_YYYY-MM-DD.json # 板块资金流
│   ├── indicators_*.json         # 技术指标缓存
│   └── financials_*.json         # 财报缓存
├── config/jobs.json              # Cron 推送任务定义
├── data/                         # 持久数据（新建）
│   ├── state.db                  # Hermes 状态数据库
│   └── response_store.db         # 响应存储
└── logs/                         # 日志文件
```

## 关键兼容 symlink

以下 symlink 保证旧路径仍然有效：

| Symlink | → 目标 |
|---------|--------|
| `scripts/amadeus_data.py` | `scripts/amadeus/amadeus_data.py` |
| `cache/images/` | 原 `image_cache/` |
| `cache/audio/` | 原 `audio_cache/` |

## 新文件规则

- 新采集脚本 → `scripts/amadeus/`
- 新缓存数据 → `cache/amadeus/`
- 新参考文档 → `skills/investment/amadeus/references/`
- 数据库文件 → `data/`
- 禁止在 `~/.hermes/` 根目录裸放新文件
