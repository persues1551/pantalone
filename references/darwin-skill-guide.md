# Darwin Skill 2.0 使用指南

## 安装位置
`~/.hermes/skills/core/darwin-skill/`（2865⭐，MIT许可）

## 触发词
`达尔文` / `darwin` / `优化skill` / `skill评分` / `skill质量检查` / `帮我改改skill` / `skill怎么样` / `提升skill质量`

## 核心流程

### Phase 0: 初始化
1. 确认优化范围（全部skills或指定skills）
2. 创建git分支：`auto-optimize/YYYYMMDD-HHMM`
3. 初始化results.tsv

### Phase 0.5: 测试Prompt设计
为每个skill设计2-3个典型用户prompt，保存到skill目录/test-prompts.json

### Phase 1: 基线评估
- 维度1-7：主agent静态分析
- 维度8：spawn独立子agent实测（或dry_run）
- 维度9：检查反例与黑名单

### Phase 2: 优化循环（最多3轮）
1. 找最弱维度
2. 生成1个改进方案
3. 执行改进 + git commit
4. spawn独立子agent重评
5. 分数↑→保留，分数↓→git revert

### Phase 3: 汇总报告

## 9维度评分体系

| # | 维度 | 权重 | 说明 |
|---|------|------|------|
| 1 | Frontmatter质量 | 7% | name/description/触发词 |
| 2 | 工作流清晰度 | 12% | 步骤编号、I/O明确 |
| 3 | 失败模式编码 | 12% | "如果X失败→做Y"分支 |
| 4 | 检查点设计 | 6% | 🔴视觉标记 |
| 5 | 可执行具体性 | 17% | 禁止软化措辞 |
| 6 | 资源整合度 | 4% | 路径有效性 |
| 7 | 整体架构 | 12% | 无冗余、无AI腔 |
| 8 | 实测表现 | 23% | 跑测试prompt对比 |
| 9 | 反例与黑名单 | 6% | "不要做X"清单 |

## 关键规则
- 每轮只改一个维度
- 分数必须严格高于才保留（不靠四舍五入）
- 连续2轮Δ<2分→自动停止
- dim2/3/4是相关簇，修一个时观察另两个
- 必须spawn独立子agent评分，不能自评自改

## 与Hermes Agent兼容
- 原生SKILL.md格式，零依赖
- 需要git + 子agent spawning能力
- results.tsv位置：`~/.hermes/skills/core/darwin-skill/results.tsv`

## 实战经验（2026-05-28首次使用）
- Pantalone评分60.4→64.0（+3.6分）
- Round 1成功：添加集中式失败模式表（dim3: 5→8）
- Round 2失败：尝试去重不够彻底，judge评分反降，已回滚
- 教训：dim7整体架构需要"探索性重写"，不是微调能解决的
