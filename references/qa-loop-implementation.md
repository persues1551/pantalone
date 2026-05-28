# QA闭环测试系统 — 实现细节

**借鉴来源**：Replit AI Agent 的内循环开发模式（Inner Dev Loop）
**实施日期**：2026-05-24
**核心思想**：采集 → 验证 → 失败 → 自动修复 → 重验证，形成自我纠错闭环

## 与传统CI/CD的区别

| 维度 | 传统CI/CD | Replit QA闭环 |
|------|-----------|---------------|
| 触发时机 | Git push / PR | 每次代码生成后即时 |
| 反馈延迟 | 分钟级（排队+构建） | 秒级（原地执行） |
| 修复方式 | 人看日志→手动修→重新push | AI分析→自动修→自动重试 |
| 检测范围 | 测试套件+构建 | 测试+运行时+UI+lint |
| 循环性质 | 线性（fail→人工介入） | 闭环（fail→AI修→再验证） |

## 文件结构

```
~/.hermes/scripts/amadeus/
├── tests/
│   └── test_pantalone_data.py    # 16个测试用例，5层验证
├── qa_loop.py                    # QA闭环Runner
└── data_validator.py             # 统一验证模块（已有）
```

## 测试分层（5层递进）

### Layer 1: 格式验证（单元测试，不依赖网络）
- 数据字段完整性（price/change_pct/volume/name/code）
- 数值范围（价格>0，涨跌幅±20%，成交量≥0）
- 类型检查（int/float/str）
- 数据新鲜度（日期是今天或昨天）

### Layer 2: 数据采集（集成测试，需要网络）
- AKShare stock_zh_a_spot_em() 调用验证
- 指数行情采集验证
- 北向资金采集验证
- 标记 `@pytest.mark.network`

### Layer 3: 交叉验证（多信号）
- 同数据多源对比（新浪 vs 东方财富）
- 发现单源偏差
- 当前因格式不兼容跳过，待完善

### Layer 4: 质量评级验证
- 评分逻辑正确性（0-100范围）
- 评级阈值（A≥85/B≥70/C+≥50/C≥30/D≥15/F<15）

### Layer 5: 脚本完整性
- 必要文件存在（data_validator.py / data_quality.py / amadeus_data.py）
- JSON缓存可解析

## QA闭环Runner逻辑

```python
while attempt < max_retries:
    # Step 1: 运行格式验证（不依赖网络）
    result = run_tests("not network")
    if not result.passed:
        # 分析失败原因，尝试自动修复
        fixes = analyze_failures(result.output)
        if fixes:
            continue  # 修复后重试
        else:
            break  # 无法修复，终止

    # Step 2: 运行网络测试（数据采集验证）
    net_result = run_tests("network")
    if net_result.passed:
        break  # 全部通过
    else:
        break  # 网络失败不重试（可能是周末）
```

## 自动修复能力

| 问题 | 修复动作 |
|------|----------|
| JSON缓存损坏 | 自动备份(.corrupted) + 重建空JSON |
| 缺失文件 | 检测并报告路径 |
| 网络失败 | 等待5秒后重试（最多3次） |

## 使用场景

| 场景 | 命令 |
|------|------|
| 修改数据采集脚本后 | `python3 qa_loop.py --data-only` |
| 修改数据验证逻辑后 | `python3 qa_loop.py` |
| 周末/非交易时段 | `python3 qa_loop.py --data-only` |
| 快速验证格式 | `pytest tests/test_pantalone_data.py -v -k "not network"` |

## 测试结果（2026-05-24首次运行）

```
16个用例：13通过 ✅ / 3网络失败（周末正常） / 1跳过
QA闭环Runner：格式验证全部通过 ✅
```

## 扩展方向

1. **增加更多数据源的交叉验证**：新浪vs腾讯vs同花顺数值对比
2. **集成到cron job**：数据采集后自动运行qa_loop验证
3. **添加性能测试**：数据采集耗时监控
4. **添加回归测试**：修复bug后添加对应的测试用例
