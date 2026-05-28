# SOUL.md 拆分重构模式

**日期**：2026-05-14
**目的**：将臃肿的 SOUL.md 拆分为模块化架构

## 拆分原则

SOUL.md 只保留最高原则（我是谁/信什么/不能做什么），其他内容外移到专用文件。

## 拆分前后对比

| 文件 | 拆分前 | 拆分后 | 变化 |
|------|--------|--------|------|
| SOUL.md | 1372行 | 559行 | -59% |
| router.md | 95行 | 262行 | +176% |
| workflow.md | 185行 | 362行 | +96% |
| subagents/ | 不存在 | 13文件 | 新建 |
| rules/ | 5文件 | 9文件 | +4新建 |

## 文件职责

```
SOUL.md (559行) ← 最高原则：身份/核心原则/权限/边界
  ├── router.md (262行) ← 任务路由：类型识别/复杂度分级/模型分工
  ├── workflow.md (362行) ← 执行流程：核心流程/汇总规则/审批规则
  ├── subagents/ (13文件) ← 权限边界
  ├── rules/ (9文件) ← 领域规则
  └── templates/ (3文件) ← 输出格式
```

## 拆分步骤

1. 分析 SOUL.md 章节结构（grep -n "^## " SOUL.md）
2. 识别保留章节 vs 移出章节
3. 创建 subagents/ 目录，写入13个文件
4. 重写 SOUL.md（只保留保留章节）
5. 扩充 router.md（加入任务路由/模型分工）
6. 扩充 workflow.md（加入执行流程/汇总规则）
7. 新建 rules/ 文件（research/writing/tech/learning）
8. 合并 rules/ 文件（data/trading/risk 追加内容）

## 自检清单

- [ ] SOUL.md 是否只保留最高原则
- [ ] router.md 是否包含 L0-L4 复杂度分级
- [ ] workflow.md 是否包含执行顺序/汇总规则
- [ ] subagents/*.md 是否有"可以做/不能做/输出格式"
- [ ] Risk Agent 是否拥有最终否决权
- [ ] 所有§引用是否有效
- [ ] 遗留引用是否已清理

## 回滚方式

```bash
cp SOUL.md.bak.20260514 SOUL.md
rm -rf subagents/
rm rules/{research,writing,tech,learning}_rules.md
```

## 动态验证设计

10个测试用例，验证路由和Subagent是否正确：
- L0 简单任务 → 小米，不需要Risk
- L1 简单写作 → 小米，不需要Risk
- L3 A股早报 → DeepSeek，Risk必须执行
- L4 修改SOUL.md → DeepSeek，必须确认
- L4 Gateway中断 → DeepSeek，第一步只读
- 财报缺失超3项 → 不得评级
- 视觉K线截图 → mimo-v2-omni，标注可信度
- 科研论文框架 → DeepSeek，不得编造文献
- Cron修改 → DeepSeek，必须确认
- 多资产分析 → DeepSeek，不得说无风险
