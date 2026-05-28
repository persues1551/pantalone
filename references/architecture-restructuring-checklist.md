# 架构重构查漏补缺流程

## 适用场景

当对 amadeus 模块化架构进行重大变更（拆分/合并/新增模块）后，执行此流程确保无遗漏。

## 步骤

### 1. 统计文件完整性

```bash
# 列出所有 .md 文件
find ~/.hermes/skills/investment/amadeus -name "*.md" | wc -l

# 按目录统计
for dir in rules templates eval logs advanced references; do
  echo "$dir: $(find ~/.hermes/skills/investment/amadeus/$dir -name '*.md' 2>/dev/null | wc -l)"
done
```

### 2. 检查 references 引用完整性

读取 `advanced/knowledge_base.md` 中的「外部参考文件」表格，对比 `references/` 目录实际文件：

```bash
# 实际文件
ls ~/.hermes/skills/investment/amadeus/references/*.md | xargs -I{} basename {}

# 对比 knowledge_base.md 中的引用
grep "references/" ~/.hermes/skills/investment/amadeus/advanced/knowledge_base.md
```

未被引用的文件 → 补充到 knowledge_base.md 引用表。

### 3. 检查模板中关键章节

每个模板必须包含：
- [ ] 模拟盘部分（交易计划/台账）
- [ ] 风险声明
- [ ] 数据来源说明

### 4. 检查规则一致性

- rules/ 下各文件不重复定义同一规则
- 散落在错误文件中的规则归位
- 新增规则写入正确的模块

### 5. 更新 knowledge_base.md

新增的 references 文件必须补充到引用表，格式：
```
| 文件描述 | `references/filename.md` | 内容摘要 |
```

### 6. 动态测试用例验证（2026-05-14 新增）

拆分后不仅要检查文件完整性，还要设计动态测试用例验证路由和Subagent是否正确：

**标准测试集**（10个用例，覆盖L0-L4）：
1. L0 解释概念 → 小米、不需要Risk
2. L1 润色邮件 → 小米、不需要Risk
3. L3 A股早报 → DeepSeek、Risk必须执行
4. L4 修改SOUL.md → DeepSeek、Ops/Code/Risk、必须确认
5. L4 Gateway中断 → DeepSeek、第一步只读检查
6. 财报缺失超3项 → Financial不得评级、Risk否决模拟盘
7. K线截图 → Vision Agent、标注明确可见/疑似/无法确认
8. 科研论文框架 → DeepSeek、不得编造文献
9. Cron修改 → L4、必须确认
10. 多资产分析 → DeepSeek、Macro Agent、不得说无风险

**详细模板**：`references/post-refactoring-audit-template.md`

### 7. 检查遗留 § 引用（2026-05-14 发现的坑）

拆分后最常见的问题是旧的 § 号引用失效：
```bash
grep -rn "SOUL.md §" <dir>/{router,workflow,rules/*,subagents/*}.md
```
对每个引用验证目标§是否在新SOUL.md中存在。不存在则改为新§号或直接写入内容。

## 历史案例

### 2026-05-13 v2.4 重构

- 800行 SKILL.md → 32个文件，10个目录
- 发现遗漏：5个 references 文件未被 knowledge_base.md 引用
- 发现遗漏：模拟盘规则未强制写入所有报告格式
- 修复：补充引用 + workflow.md 写入强制规则
