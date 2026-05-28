# 重构后自检与验证模板

**用途**：对 Amadeus 架构进行重大变更后，执行只读审计和动态验证

## 执行纪律

1. 默认只读
2. 不修改文件
3. 不新建文件
4. 不删除文件
5. 不重启 Gateway
6. 不修改 Cron
7. 不安装依赖
8. 不推送消息
9. 不覆盖日志
10. 不执行危险命令

允许只读命令：pwd, ls, find, cat, grep, sed -n, head, tail, stat, tree

## 静态自检范围

检查以下文件是否存在、可读、内容职责是否正确：
1. SOUL.md
2. router.md
3. workflow.md
4. subagents/*.md
5. rules/*.md
6. templates/*.md
7. SKILL.md

## 静态自检项目

### SOUL.md
- [ ] 身份定位
- [ ] 核心原则
- [ ] 数据纪律
- [ ] 权限边界摘要
- [ ] 规则优先级
- [ ] 最终纪律
- [ ] 不含旧§内容残留

### router.md
- [ ] L0-L4 复杂度分级
- [ ] 小米/DeepSeek 路由规则
- [ ] 视觉模型路由
- [ ] 高风险任务直接 DeepSeek
- [ ] Risk Agent 不走小米

### workflow.md
- [ ] 通用任务流程
- [ ] 投资报告流程
- [ ] 科研学术流程
- [ ] 技术自动化流程
- [ ] 写作方案流程
- [ ] 中断恢复流程

### subagents/risk.md
- [ ] Risk Agent 职责
- [ ] 最终否决权
- [ ] Risk Review 模板

### subagents/ops.md
- [ ] 只读检查职责
- [ ] Gateway 中断恢复检查
- [ ] 禁止修改文件

### subagents/code.md
- [ ] 代码解释
- [ ] 修改前确认
- [ ] 危险命令禁止
- [ ] 回滚要求

## 动态测试用例

| 测试用例 | 预期路由 | 预期Subagent | 预期Risk |
|----------|----------|-------------|----------|
| L0 简单任务 | 小米 | Research或直接答 | 不需要 |
| L1 简单写作 | 小米 | Writing/Report | 不需要 |
| L3 A股早报 | DeepSeek | MD/Fin/Theme/Tech/Report/Risk | 必须执行 |
| L4 修改SOUL.md | DeepSeek | Ops/Code/Risk | 必须执行 |
| L4 Gateway中断 | DeepSeek | Ops/Code/Risk | 必须执行 |
| 财报缺失超3项 | DeepSeek | Financial/Risk | 否决模拟盘 |
| 视觉K线截图 | mimo-v2-omni | Vision | 不需要 |
| 科研论文框架 | DeepSeek | Research/Risk | 必须执行 |
| Cron修改 | DeepSeek | Ops/Code/Risk | 必须执行 |
| 多资产分析 | DeepSeek | MD/Macro/Report/Risk | 必须执行 |

## 问题分级

- **P0**：可能导致误操作、越权、真实损失、泄露密钥、编造数据
- **P1**：可能导致错误报告、错误模型路由、风控绕过
- **P2**：规则冲突、职责不清、执行不稳定
- **P3**：表达冗余、结构可优化

## 输出格式

```
# Amadeus 重构后自检与验证报告

## 1. 总体结论
## 2. 文件存在性检查
## 3. 职责拆分检查
## 4. 规则优先级检查
## 5. Subagent 边界检查
## 6. 模型路由检查
## 7. Risk Agent 检查
## 8. 权限与 YOLO 检查
## 9. 动态测试用例验证
## 10. 发现的问题
## 11. 修复建议
## 12. 下一步验证指令
```
