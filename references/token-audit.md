# Token 消耗审计报告 — 2026-05-12

## 账单概览

| 指标 | 数值 |
|------|------|
| 平台账单（含推理） | **~5,000 万 token/天** |
| 常规输入 token | 1,162 万 |
| 常规输出 token | 11 万 |
| 推理 token（隐性） | ~3,800 万（平台账单 - 常规估算） |
| 会话数 | 25 个 |
| DeepSeek 余额 | 80.57 CNY |

## 消耗分布

### Top 3 会话（占总消耗 62%）

| 会话 | 轮次 | 常规输入 token | 说明 |
|------|------|---------------|------|
| 0901 微信聊天 | 44 轮 | 308 万 | 最长会话 |
| 1239 QQ 聊天 | 41 轮 | 229 万 | |
| 1227 QQ 聊天 | 36 轮 | 181 万 | |

### 单会话组成（6 个 cron session 平均）

| 组成部分 | Token | 占比 |
|----------|-------|------|
| System Prompt（persona + memory） | ~800 | 2% |
| Amadeus SKILL.md | ~7,000 | 17% |
| 工具定义（29 个） | ~11,400 | **27%** |
| 消息体（含 tool call/result） | ~23,000 | 54% |
| **总计** | **~42,000** | 100% |

## 推理 Token 分析

`reasoning_effort: medium` 使模型每输出 1 token 前做 3-8x 内部推理。

**推理 token 的特征**：
- 不出现在 session JSON 中
- 不出现在 agent.log 中
- 只在 DeepSeek 平台账单可见
- API 响应中 `usage.completion_tokens_details.reasoning_tokens` 可查（Hermes 未记录）

**估算**：
- 常规输出 11 万 token × 5（平均推理倍率）= 55 万推理 token
- 但平台账单显示 ~5,000 万，说明推理倍率远高于 5x
- 可能原因：工具调用循环中每步都触发推理、长上下文推理成本更高

## 优化措施（已实施）

| 措施 | 省 token/天 | 状态 |
|------|-----------|------|
| Cron 工具裁剪 29→4 | ~6 万 | ✅ 已实施 |
| DeepSeek Context Caching | 自动 | ✅ 默认启用（10% 价格命中） |
| Hermes Context Compression | 自动 | ✅ 默认启用（50% 阈值触发） |

## 被拒绝的优化

| 方案 | 原因 |
|------|------|
| v2.0 输出压缩规则 | "也没省多少"，且主人偏好完整分析 |
| 推理深度分层（low/medium） | "不用降低推理深度"，质量优先 |

## 关键发现

1. **输出压缩是伪需求**：输出仅占总消耗 <1%
2. **推理 token 是隐形杀手**：占账单 70%+，session 日志完全看不到
3. **上下文累积是最大输入消耗**：44 轮会话单轮上下文膨胀到 10 万 token
4. **工具定义是固定开销**：29 个工具 ~11,400 tok/轮，裁剪到 4 个仅 ~1,500 tok
5. **DeepSeek KV Cache 已自动生效**：精确前缀匹配，命中仅 10% 价格
6. **Hermes Context Compression 已自动生效**：50% 阈值，辅助模型总结中部轮次

## 审计工具

```bash
python3 ~/.hermes/skills/investment/amadeus/scripts/token_audit.py            # 今天
python3 ~/.hermes/skills/investment/amadeus/scripts/token_audit.py 2026-05-12 # 指定日期
python3 ~/.hermes/skills/investment/amadeus/scripts/token_audit.py --cron-only
```
