# Sina Finance 实时新闻采集方法

> 验证于 2026-05-13，作为 web_search 不可用时的 Level 2 降级方案

## 方法1：首页关键词抓取（最可靠）

```bash
curl -sL 'https://finance.sina.com.cn/' -H 'User-Agent: Mozilla/5.0' 2>/dev/null \
  | grep -oP 'href="[^"]*"[^>]*>[^<]*关键词[^<]*' \
  | sed 's/href="//;s/"[^>]*>/ | /' | head -20
```

优点：首页实时更新，含标题+链接，结构化好。

## 方法2：逐篇抓正文

```bash
curl -sL '<文章URL>' -H 'User-Agent: Mozilla/5.0' -H 'Referer: https://finance.sina.com.cn' 2>/dev/null \
  | python3 -c "
import sys, re
html = sys.stdin.read()
blocks = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
for b in blocks:
    text = re.sub(r'<[^>]+>', '', b).strip()
    if len(text) > 20: print(text)
" | head -50
```

必须带 Referer header，否则可能返回空内容。

## 方法3：7x24快讯流

```bash
curl -sL 'https://finance.sina.com.cn/7x24/' -H 'User-Agent: Mozilla/5.0' 2>/dev/null \
  | grep -i '关键词' | python3 -c "
import sys, re
for line in sys.stdin:
    text = re.sub(r'<[^>]+>', '', line).strip()
    if len(text) > 20: print(text[:200])
" | head -20
```

## 注意事项
- Baidu News 需要验证码，curl 不可用
- Sina Search 搜索页已下线（返回404）
- 新浪文章页 &lt;p&gt; 标签提取最稳定
