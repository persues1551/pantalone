# Amadeus 合规审计摘要 (2026-05-14)

## 审计结论：基本合规，2×P0 + 4×P1 + 6×P2 + 4×P3

## P0 严重风险

### P0-01：API密钥明文暴露
- **文件**：`~/.hermes/config.yaml`
- **问题**：DeepSeek/MiMo API Key 明文存储
- **修复**：chmod 600 或改用环境变量引用

### P0-02：权限规则冲突
- **文件A**：`workflow.md "系统迭代原则"` → "规则缺陷/脚本bug → 直接修复，不提问不请示"
- **文件B**：`SOUL.md §15.2` → "修改规则文件" 列为必须确认
- **冲突**：workflow.md 说可以直接改 rules/，SOUL.md 说必须确认
- **建议**：以 SOUL.md 为准。workflow.md 应区分"bug修复"（可直接）和"规则变更"（需确认）

## P1 高风险

### P1-01：模型路由冲突
- **router.md**："盘前/午盘/收盘报告 → mimo-v2.5-pro"
- **SOUL.md §14.4.2**："A股完整报告 → L3 → DeepSeek"
- **建议**：统一。日常报告可用小米（成本考虑），深度分析用DeepSeek

### P1-02：workflow.md cron配置过时
- **workflow.md**："盘前早报 | `0 9 * * 1-5`" / "4个cron job"
- **实际**：盘前已改08:30 / 共16个cron任务
- **修复**：更新workflow.md定时推送配置表

### P1-03：cron自动推送未走确认
- **SOUL.md §15.2**："推送外部消息"需确认
- **实际**：cron每天自动推微信，无逐次确认
- **建议**：在SOUL.md补充"cron配置的自动推送视为预授权"

### P1-04：workflow.md迭代原则与SOUL.md矛盾
- 同P0-02，但聚焦于"观察池规则变更"场景
- workflow.md说可直接改pool_rules.md，SOUL.md说需确认

## P2 中风险

| 编号 | 问题 | 状态 |
|------|------|------|
| P2-01 | logs/三文件只有模板无实际记录 | 未修复 |
| P2-02 | 11个Subagent未实际实现（只有概念） | 未修复 |
| P2-03 | Risk Agent否决权未实现 | 未修复 |
| P2-04 | 模拟盘空库 | ✅ 已修复 |
| P2-05 | 观察池价格N/A | ✅ 已修复 |
| P2-06 | 预测验证0% | ✅ 已修复 |
| P2-07 | workflow.md遗留§5.4引用 | ✅ 已修复（→§15.4） |
| P2-08 | risk_rules.md遗留§18.4引用 | ✅ 已修复（移除引用，直接写入） |

## P3 低风险

| 编号 | 问题 |
|------|------|
| P3-01 | hermes-persona.md缺失 |
| P3-02 | router.md与workflow.md内容重复 |
| P3-03 | SOUL.md §14 Subagent描述过详（~500行） |
| P3-04 | knowledge_base.md引用表不完整 |

## 规则冲突清单

| 冲突点 | 文件A | 文件B | 建议保留 |
|--------|-------|-------|----------|
| 盘前报告模型 | router.md | SOUL.md §14.4.2 | SOUL.md（或明确例外） |
| 规则修改权限 | workflow.md | SOUL.md §15.2 | SOUL.md |
| cron推送确认 | cron配置 | SOUL.md §15.2 | 补充例外 |
| 情绪温度缺数据 | data_rules.md | trading_rules.md | data_rules.md |

## 修复优先级

1. **立即**：config.yaml 权限保护
2. **优先**：workflow.md 迭代原则与 SOUL.md 对齐
3. **优先**：router.md 模型路由表更新
4. **排期**：日志文件填充 / Subagent实现决策
