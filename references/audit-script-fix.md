# API审计脚本修复记录

## 修复日期
2026-05-24

## 问题
`audit_api_relays.sh` 硬编码了未使用的端点（api.anthropic.com、openrouter.ai、api.openai.com），实际使用的是小米MiMo中转和DeepSeek直连。

## 根因
```bash
# 旧代码：硬编码
case "$provider_name" in
    "anthropic") echo "https://api.anthropic.com/v1" ;;  # ❌ 我们不用这个
    "openrouter") echo "https://openrouter.ai/api/v1" ;;  # ❌ 没配key
    "openai") echo "https://api.openai.com/v1" ;;         # ❌ 没配key
esac
```

## 实际端点
- 主provider: `https://token-plan-sgp.xiaomimimo.com/v1`（小米MiMo中转）
- ANTHROPIC_BASE_URL: `https://token-plan-sgp.xiaomimimo.com/anthropic`
- DeepSeek: `https://api.deepseek.com/v1`

## 修复方案
改为从 `~/.hermes/config.yaml` 读取实际端点：

```bash
case "$provider_name" in
    "mimo")
        base_url=$(grep -A10 'custom:mimo' "$HERMES_CONFIG" | grep 'base_url' | head -1 | awk '{print $2}')
        api_key=$(grep -A10 'custom:mimo' "$HERMES_CONFIG" | grep 'api_key' | head -1 | awk '{print $2}')
        ;;
    "deepseek")
        base_url=$(grep -A10 'deepseek:' "$HERMES_CONFIG" | grep 'base_url' | head -1 | awk '{print $2}')
        api_key=$(grep -A10 'deepseek:' "$HERMES_CONFIG" | grep 'api_key' | head -1 | awk '{print $2}')
        ;;
esac
```

## 修复后测试结果
| Provider | 风险级别 | 关键发现 |
|----------|----------|----------|
| MiMo（小米中转） | 🔴 HIGH | tool-call包替换3/4被重写、隐藏prompt注入243tok |
| DeepSeek（直连） | 🟢 LOW | 无明确漏洞 |

## 文件位置
- 脚本：`~/.hermes/scripts/audit/audit_api_relays.sh`
- Cron job：`24644399a1f1`（每周日03:00执行）

## 教训
1. **审计脚本必须审计实际端点**：从配置文件读取，不能硬编码"常见"端点
2. **修改后必须立即测试**：改完脚本→立即运行→确认结果→汇报主人
