# Weixin 限流修复记录

## 日期
2026-05-13

## 问题链

1. **午盘报告太长** → 分成5-10个chunk
2. **chunk间隔1.5秒太短** → 触发iLink API限流（ret=-2）
3. **限流重试时** → aiohttp超时上下文出错："Timeout context manager should be used inside a task"

## 根因分析

1. 限流耗尽重试次数 → 抛出 RuntimeError
2. base.py 的 `_send_with_retry` 捕获后重试整个 send()
3. 重试期间触发了 reconnect（"restored 1 context token"）
4. reconnect 重建了 `_send_session`，但新 session 的 aiohttp timeout 上下文不在正确的 task 中
5. → "Timeout context manager should be used inside a task"

## 修复方案

### 代码修改

#### 1. 新增 `_reconnect_send_session()` 方法

```python
async def _reconnect_send_session(self) -> None:
    """Recreate the send session after a fatal aiohttp state error."""
    if self._send_session and not self._send_session.closed:
        try:
            await self._send_session.close()
        except Exception:
            pass
    self._send_session = aiohttp.ClientSession(
        trust_env=True, connector=_make_ssl_connector()
    )
    logger.info("[%s] Recreated send session for %s", self.name, _safe_id(self._account_id))
```

#### 2. 在 `_send_text_chunk` 中检测 timeout context 错误

```python
# 在 except 块中添加
if "Timeout context manager" in str(exc) and not session_reconnected:
    logger.warning(
        "[%s] send session corrupted for %s; reconnecting",
        self.name, _safe_id(chat_id),
    )
    await self._reconnect_send_session()
    session_reconnected = True
    continue  # retry immediately with fresh session
```

#### 3. caption 发送改用 `_send_text_chunk`

```python
# 旧代码
await _send_message(
    self._send_session,
    base_url=self._base_url,
    token=self._token,
    to=chat_id,
    text=self.format_message(caption),
    context_token=context_token,
    client_id=last_message_id,
)

# 新代码
await self._send_text_chunk(
    chat_id=chat_id,
    chunk=self.format_message(caption),
    context_token=context_token,
    client_id=last_message_id,
)
```

### 配置修改

```yaml
# config.yaml
platforms:
  weixin:
    send_chunk_delay_seconds: 5.0   # 原3.0
    send_chunk_retries: 6           # 原5
    send_chunk_retry_delay_seconds: 3.0  # 原2.0
```

## 补充修复（2026-05-13 16:27）

### 问题

Word 文档发送时也出现 "Timeout context manager should be used inside a task" 错误。

### 根因

`_send_file` 函数没有 session 重建逻辑，当 session 损坏时无法自动恢复。

### 修复方案

在 `_send_file` 中添加与 `_send_text_chunk` 相同的 session 重建逻辑：

```python
async def _send_file(self, chat_id: str, path: str, caption: str, force_file_attachment: bool = False) -> str:
    last_error: Optional[Exception] = None
    session_reconnected = False
    for attempt in range(self._send_chunk_retries + 1):
        try:
            # ... 原有逻辑 ...
            return last_message_id
        except Exception as exc:
            last_error = exc
            # 检测 timeout context 错误
            if "Timeout context manager" in str(exc) and not session_reconnected:
                logger.warning("[%s] send session corrupted for %s; reconnecting (file)", self.name, _safe_id(chat_id))
                await self._reconnect_send_session()
                session_reconnected = True
                continue  # 立即重试
            # ... 其他重试逻辑 ...
```

### 验证结果

```
✅ Word 文档发送成功
✅ 盘前早报、午间复盘、收盘复盘均成功推送
```

## to_docx.py 表格处理修复（2026-05-13 16:54）

### 问题

转换 Markdown 到 Word 时，如果表格列数不一致，会报 `IndexError: tuple index out of range`。

### 根因

`to_docx.py` 假设所有表格行的列数相同，但实际报告中不同表格可能有不同列数。

### 修复方案

在创建新表格前检查列数是否匹配：

```python
# 旧代码
if not hasattr(md_to_docx, '_table'):
    md_to_docx._table = doc.add_table(rows=1, cols=len(cells))

# 新代码
if not hasattr(md_to_docx, '_table') or len(md_to_docx._table.columns) != len(cells):
    # 如果列数不匹配或没有表格，创建新表格
    if hasattr(md_to_docx, '_table'):
        del md_to_docx._table
    md_to_docx._table = doc.add_table(rows=1, cols=len(cells))
```

### 验证结果

```
✅ 支持不同列数的表格
✅ 盘前早报、午间复盘、收盘复盘均成功转换
```

## 相关文件

- `gateway/platforms/weixin.py` - 主要修改文件（session 重建逻辑）
- `config.yaml` - 配置修改（chunk 间隔、重试次数）
- `gateway/platforms/base.py` - 重试逻辑（未修改，但触发了问题）
- `scripts/amadeus/to_docx.py` - 表格处理修复

## 经验教训

1. **aiohttp session 状态损坏** - 限流风暴后 session 可能进入不可恢复状态
2. **timeout context 错误** - 是 aiohttp 内部检查，表示 session 不在正确的 async task 中
3. **重建 session** - 遇到此错误时，重建 session 是最可靠的修复方式
4. **caption 发送** - 之前裸调 `_send_message` 无重试，现在统一用 `_send_text_chunk`
5. **文件发送** - `_send_file` 也需要 session 重建逻辑，不能只修 `_send_text_chunk`
6. **表格列数** - Markdown 转 Word 时，不同表格可能有不同列数，需要动态处理
