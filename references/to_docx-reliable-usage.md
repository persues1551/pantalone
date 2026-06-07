# to_docx.py 可靠调用方法（2026-06-04验证）

## 问题

`cat file.md | python3 to_docx.py "title" output.docx` 在 execute_code / cron 非交互环境中**可能静默失败**：无输出、无文件生成、无报错。根因未明，可能与 stdin 重定向在非 PTY 环境中的行为有关。

## 推荐方法：直接 Python import

```python
import sys, os
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts/amadeus'))
from to_docx import md_to_docx

with open('report.md', 'r') as f:
    content = f.read()

result_path = md_to_docx(content, '晚间复盘+次日预测 2026-06-04', 'output.docx')
print(f"Generated: {result_path}")
```

在 execute_code 中使用：

```python
from hermes_tools import terminal

r = terminal("""python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts/amadeus'))
from to_docx import md_to_docx
with open('report.md') as f: content = f.read()
print(md_to_docx(content, '标题', 'output.docx'))
" 2>&1""")
print(r["output"])

# 必须验证文件生成
r2 = terminal("ls -la output.docx")
print(r2["output"])
```

## 函数签名

```python
def md_to_docx(md_text: str, title: str, output_path: str = None, auto_humanize: bool = True) -> str:
    """将 Markdown 文本转为 .docx，返回文件路径"""
```

- `md_text`：Markdown 内容（字符串）
- `title`：文档标题
- `output_path`：输出路径（可选，默认生成到 `~/.hermes/cache/amadeus/reports/`）
- `auto_humanize`：是否自动 humanizer（默认 True）
- 返回：生成的 .docx 文件路径

## 注意事项

1. to_docx.py 内建 humanizer，不需要先手动 humanize
2. 但 SKILL.md 流程中要求摘要文本单独 humanize（`humanize_auto.py --inplace`）
3. 调用后**必须 ls -la 验证**文件大小 > 0
4. 函数内部自动创建输出目录（`os.makedirs`）
