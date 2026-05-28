# 向量搜索模块部署记录

## 部署日期
2026-05-24

## 组件
| 组件 | 版本 | 用途 |
|------|------|------|
| chromadb | 1.5.9 | 向量数据库（本地持久化） |
| sentence-transformers | 5.5.1 | 嵌入模型框架 |
| torch | 2.12.0+cpu | PyTorch CPU版本 |
| 嵌入模型 | paraphrase-multilingual-MiniLM-L12-v2 | 多语言嵌入（支持中文） |

## 安装位置
- 向量数据库：`~/.hermes/cache/vector_db/`
- 搜索模块：`~/.hermes/scripts/vector_search.py`
- 安装环境：`~/.hermes/hermes-agent/venv/`

## 性能指标
- 索引速度：34.7条/秒（CPU）
- 向量维度：384
- 当前索引量：4040条（2026-05-24）

## 用法
```bash
# 增量索引（只处理新消息）
python3 ~/.hermes/scripts/vector_search.py index --limit 100

# 语义搜索
python3 ~/.hermes/scripts/vector_search.py search "清除聊天记录"

# 统计
python3 ~/.hermes/scripts/vector_search.py stats
```

## 与FTS5的区别
| 维度 | FTS5（当前） | 向量搜索（新增） |
|------|-------------|-----------------|
| 搜索方式 | 关键词匹配 | 语义相似度 |
| "重置对话"搜"清除聊天记录" | ❌ 找不到 | ✅ 相似度0.56 |
| 速度 | 毫秒级 | 秒级（含嵌入计算） |
| 存储 | SQLite内嵌 | ChromaDB独立 |

## 集成状态：✅ 已完成（2026-05-24）

已集成到 `session_search_tool.py`，FTS5关键词搜索后自动执行向量语义搜索，两路召回合并去重。

**修改文件**：`~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/tools/session_search_tool.py`
- 添加了 `import os`
- 在FTS5搜索后添加向量搜索逻辑（~30行代码）
- 向量结果格式：`{session_id, content, role, timestamp, source: "vector_search", similarity}`

**测试验证**：
```
搜索: "清除聊天记录"
1. [vector] (相似度: 0.59) 关于"重置对话"的讨论 ✅ 语义匹配成功
2. [vector] (相似度: 0.55) 关于会话连贯性的讨论
3. [vector] (相似度: 0.53) 关于长会话的问题
```

**用法**：
- session_search现在自动使用混合搜索，无需额外配置
- 如需禁用向量搜索：修改代码中 `use_vector=False`（默认True）
- 新消息索引：`python3 ~/.hermes/scripts/vector_search.py index --limit 100`

## Pitfalls
1. **HuggingFace认证**：text2vec-chinese需要HF token，改用sentence-transformers的multilingual模型
2. **全量索引慢**：14000+条消息全量索引>5分钟，必须用增量索引
3. **模型加载慢**：首次加载~3秒，后续调用复用实例
4. **向量搜索超时**：首次搜索含模型加载+ChromaDB初始化，可能>10秒。后续搜索<100ms
5. **内存占用**：torch+sentence-transformers加载后约占用300MB内存，懒加载模式下不使用时不占用
