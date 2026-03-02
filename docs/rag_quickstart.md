# RAG + Agent 快速入门

## 🎯 5 分钟上手

### 第 1 步：准备向量数据库

如果你还没有构建向量索引，先运行：

```bash
python scripts/build_index.py
```

这会将 `data/pdf/` 目录下的 PDF 文件转换为向量索引。

### 第 2 步：运行 RAG 写作

```bash
python scripts/run_rag_writing.py
```

输入你想写综述的主题，例如：
- "深度学习在自然语言处理中的应用"
- "Transformer 模型的发展历程"
- "强化学习的最新进展"

### 第 3 步：查看结果

结果会保存在 `output_rag_summary.txt` 文件中。

## 📖 核心流程解析

```
用户输入：深度学习在 NLP 中的应用
    ↓
[Retriever] 从向量数据库检索相关论文片段
    ↓ 
    检索到 3 个相关文档：
    - 文档1: BERT 模型介绍...
    - 文档2: GPT 系列模型...
    - 文档3: Transformer 架构...
    ↓
[Summarizer] 基于这 3 个文档生成综述
    ↓
    生成初步综述（500-800字）
    ↓
[Reviewer] 审核综述质量
    ↓
    评分：7/10
    反馈：逻辑性不够，建议补充模型对比
    ↓
[Refiner] 根据反馈优化综述
    ↓
    优化后的综述
    ↓
[Reviewer] 再次审核
    ↓
    评分：9/10 ✓ 通过！
    ↓
输出最终综述
```

## 🔧 自定义配置

### 修改检索数量

编辑 `src/config.py`：

```python
RETRIEVAL_K = 5  # 默认是 3，改为 5 会检索更多文档
```

### 修改最大迭代次数

编辑 `src/config.py`：

```python
MAX_ITERATIONS = 5  # 默认是 3，允许更多轮优化
```

### 使用不同的 LLM

编辑 `src/config.py`：

```python
DEEPSEEK_MODEL = "deepseek-chat"  # 或其他模型
```

## 💡 常见问题

### Q1: 为什么检索不到相关文档？

**A:** 检查以下几点：
1. 确保已运行 `build_index.py` 构建索引
2. 确保 `data/pdf/` 目录下有 PDF 文件
3. 尝试换一个更具体的查询主题

### Q2: 生成的综述质量不高？

**A:** 可以尝试：
1. 增加检索文档数量（`RETRIEVAL_K`）
2. 增加最大迭代次数（`MAX_ITERATIONS`）
3. 使用更强大的 LLM 模型
4. 确保向量数据库中的文档质量

### Q3: 如何添加更多论文？

**A:** 
1. 将 PDF 文件放到 `data/pdf/` 目录
2. 重新运行 `python scripts/build_index.py`
3. 新的论文会被加入向量数据库

### Q4: 能否保存中间结果？

**A:** 可以！工作流使用了 `MemorySaver`，支持断点恢复。
你可以在代码中添加：

```python
# 保存检查点
config = {"configurable": {"thread_id": "my_session"}}

# 恢复执行
app.stream(initial_state, config)
```

## 🚀 进阶使用

### 1. 批量生成综述

```python
topics = [
    "深度学习在 NLP 中的应用",
    "计算机视觉的最新进展",
    "强化学习在游戏中的应用"
]

for topic in topics:
    # 运行工作流
    result = run_rag_writing(topic)
    # 保存结果
    save_result(topic, result)
```

### 2. 自定义审核标准

修改 `src/workflows/rag_writing_graph.py` 中的 `reviewer` 函数：

```python
评审标准：
1. 内容完整性：是否全面覆盖主题 (30%)
2. 逻辑性：论述是否清晰连贯 (25%)
3. 学术性：语言是否专业规范 (20%)
4. 创新性：是否有独到见解 (15%)
5. 可读性：是否易于理解 (10%)
```

### 3. 添加引用标注

在 `summarizer` 中添加引用功能：

```python
context = "\n\n".join([
    f"[{i+1}] {doc}"
    for i, doc in enumerate(state['retrieved_docs'])
])

prompt += "\n请在综述中用 [1], [2] 等标注引用来源"
```

## 📚 相关文档

- [完整教程](./rag_agent_tutorial.md) - 深入理解原理
- [工作流对比](../examples/compare_workflows.py) - 对比不同工作流
- [架构文档](./architecture.md) - 系统架构说明

## 🎓 学习路径

1. ✅ 运行基础示例，理解整体流程
2. 📖 阅读 [完整教程](./rag_agent_tutorial.md)，理解每个节点的作用
3. 🔧 修改配置参数，观察效果变化
4. 💻 自定义节点逻辑，实现特定需求
5. 🚀 扩展到其他应用场景

祝学习愉快！🎉
