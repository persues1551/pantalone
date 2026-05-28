# Humanizer篡改事实数据问题（2026-05-27发现）

## 两套Humanizer系统（2026-05-28梳理）

| 系统 | 路径 | 类型 | 用途 |
|------|------|------|------|
| humanize_auto.py | `scripts/amadeus/humanize_auto.py` | 规则引擎（5/22安装） | to_docx.py内建调用，处理docx报告 |
| humanizer-zh SKILL.md | `skills/writing/humanizer-zh/SKILL.md` | 参考规则库（5/28安装） | 深度润色参考，基于op7418/Humanizer-zh(8424⭐) |

**关系**：humanize_auto.py是执行引擎，SKILL.md是参考规则。to_docx.py自动调用humanize_auto.py。

## 问题描述

`humanize_auto.py --inplace` 不仅修改写作风格，还会**篡改报告中的事实数据**：

### 实际案例（2026-05-27晚间复盘）

| 原始数据 | humanizer篡改为 | 差异 |
|---------|---------------|------|
| 数据等级：C（70%） | 数据：B级 | 等级错误 |
| 北向+40.75亿 | 北向净流入39.47亿 | 数值错误 |
| 000539粤电力A | 600578京能电力 | 完全换了一只股票 |
| 002129 TCL中环 | 002475立讯精密 | 完全换了一只股票 |
| 3只潜力股 | 5只候选标的 | 数量改变 |

## 根因分析

humanizer-zh 的"去AI痕迹"算法会：
1. 替换它认为"不自然"的具体数字
2. 替换它认为"不常见"的股票名称
3. 重写段落结构导致事实丢失

## 修复方案

**方案A（推荐）：只对摘要文本humanize，不对完整报告humanize**
- 完整报告直接转docx（to_docx.py内建humanizer已足够安全）
- 摘要文本（<500字）用humanize_auto.py处理
- 处理后必须人工/LLM校验关键数据

**方案B：humanize后强制校验**
- humanize完成后，用read_file读取结果
- 与原始数据交叉比对：指数点位、涨跌幅、板块资金流、个股代码、数据等级
- 发现篡改立即回滚

**方案C：禁用 --inplace，使用diff模式**
- `humanize_auto.py file.md`（不加--inplace）输出到stdout
- 手动比对后再决定是否采用

## 铁律

**humanizer处理后的报告必须校验以下字段是否被篡改**：
1. 指数点位和涨跌幅
2. 板块资金流数值
3. 个股代码和名称
4. 数据质量等级
5. 潜力股列表
6. 北向资金数值

**如果发现篡改，立即回滚到humanize前的版本。**
