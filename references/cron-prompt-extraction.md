# Cron Prompt 提取方法

## 问题

`~/.hermes/cron/jobs.json` 中的 prompt 字段包含 unicode 转义序列（`\uXXXX`），且整个文件不是标准JSON（可能是JSONL或含注释），直接 `json.loads` 会失败。

常见错误：
- `json.decoder.JSONDecodeError: Expecting property name` — 文件非标准JSON
- `UnicodeDecodeError: 'unicodeescape' codec can't decode` — 截断的unicode转义
- `json.decoder.JSONDecodeError: Extra data` — 嵌套引号导致边界错误

## 正确方法

写 Python 脚本到文件，逐字符扫描找字符串边界：

```python
import json

with open('/home/ubuntu/.hermes/cron/jobs.json', 'rb') as f:
    content = f.read().decode('utf-8')

def get_prompt(job_id):
    idx = content.find(job_id)
    if idx == -1:
        return None
    prompt_idx = content.find('"prompt":', idx)
    if prompt_idx == -1:
        return None
    val_start = content.index('"', prompt_idx + 9) + 1
    i = val_start
    escaped = False
    while i < len(content):
        c = content[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if c == '\\':
            escaped = True
            i += 1
            continue
        if c == '"':
            break
        i += 1
    raw = content[val_start:i]
    return json.loads('"' + raw + '"')

# 用法
prompt = get_prompt("88a86c07c5dc")
print(prompt)
```

## 为什么不能用简单方法

1. `json.load(f)` — 文件可能不是合法JSON（多对象、注释等）
2. `grep + 切片` — prompt内含换行和引号，切片边界不可靠
3. `content[start:end].encode().decode('unicode_escape')` — 遇到不完整转义序列会崩溃
4. 正则表达式 — 无法正确处理嵌套转义

## 替代方案

用 `hermes cron edit <job_id>` 交互式编辑（需PTY），但不适合脚本化批量操作。

## 更新 Cron Prompt 的流程

1. 提取当前 prompt（用上述脚本）
2. 修改 prompt 内容
3. 用 `cronjob(action='update', job_id=..., prompt=新prompt)` 更新
4. 验证更新生效（再提取一次对比）
