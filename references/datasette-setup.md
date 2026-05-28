# Datasette Agent 集成到 Pantalone 数据管线

## 安装状态

- Datasette 0.65.2 + sqlite-utils 3.39（安装到 ~/.hermes/hermes-agent/venv）
- 安装命令：`~/.hermes/hermes-agent/venv/bin/python -m pip install datasette sqlite-utils`

## 示例数据库

路径：`~/.hermes/cache/amadeus/data/pantalone_demo.db`
- 表 `stocks`：10条A股记录（code/name/sector/pe_ratio/market_cap/revenue_yoy）
- 包含：贵州茅台、五粮液、宁德时代、比亚迪、招商银行、中国平安、格力电器、海康威视、中芯国际、东方财富

## 启动命令

```bash
~/.hermes/hermes-agent/venv/bin/datasette ~/.hermes/cache/amadeus/data/pantalone_demo.db --cors --host 0.0.0.0 --port 8001
```

## JSON API 示例

```bash
# 全表数据
curl http://localhost:8001/pantalone_demo/stocks.json?_shape=array

# 按字段筛选
curl "http://localhost:8001/pantalone_demo/stocks.json?sector=白酒&_shape=array"

# 自定义SQL
curl "http://localhost:8001/pantalone_demo.json?sql=SELECT+code,name,pe_ratio+FROM+stocks+WHERE+pe_ratio>30"

# 聚合统计
curl "http://localhost:8001/pantalone_demo.json?sql=SELECT+sector,COUNT(*)+as+count,AVG(pe_ratio)+as+avg_pe+FROM+stocks+GROUP+BY+sector"
```

## 集成方案

1. 将API端点封装为Agent tool，支持自然语言→SQL→JSON
2. 用sqlite-utils导入CSV/JSON数据
3. 生产化需加：认证（datasette-auth-tokens）、CORS、systemd服务

## 响应性能

10条数据亚毫秒级响应（<5ms）。百万级SQLite + FTS5仍可维持<100ms。
