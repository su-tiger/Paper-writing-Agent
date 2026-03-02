# RAG + Agent 综述写作系统教程

## 📚 核心概念

### 什么是 RAG？
RAG (Retrieval-Augmented Generation) = 检索增强生成
- 先从知识库检索相关信息
- 再基于检索结果生成答案
- 解决 LLM 知识过时、幻觉等问题

### 什么是 Agent？
Agent = 智能代理，能够自主决策和执行任务的 AI 系统
- 可以调用工具（如检索、计算等）
- 可以多步推理和规划
- 可以根据反馈调整策略

## 🎯 我们的目标

构建一个：**可检索论文 + 自动写综述的 Agent 系统**

完整流程：
```
用户输入主题 
    ↓
[Retriever] 从向量数据库检索相关论文
    ↓
[Summarizer] 基于检索结果生成综述
    ↓
[Reviewer] 审核综述质量
    ↓
质量不够？→ [Refiner] 优化综述 → 返回 Reviewer
    ↓
质量满意 → 输出最终综述
```

## 🏗️ 系统架构

### 1. RAG Agent (`src/agents/rag_agent.py`)

这是一个封装了 RAG 能力的 Agent：

```python
class RAGAgent:
    def retrieve(self, query):
        """从向量数据库检索相关文档"""
        # 使用 MMR 算法，避免检索结果过于相似
        docs = self.vectorstore.max_marginal_relevance_search(query, k=3)
        return docs
    
    def run(self, query):
        """完整的 RAG 流程"""
        # 1. 检索
        docs = self.retrieve(query)
        # 2. 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])
        # 3. 生成答案
        answer = self.llm.invoke(f"基于：{context}\n回答：{query}")
        return answer
```

**关键点：**
- `max_marginal_relevance_search`：MMR 算法，平衡相关性和多样性
- `fetch_k=k*2`：先取更多候选，再筛选出最优的

### 2. RAG 写作工作流 (`src/workflows/rag_writing_graph.py`)

使用 LangGraph 构建的多节点工作流：

#### 节点 1：Retriever（检索器）
```python
def retriever(state):
    """检索相关论文"""
    docs = rag_agent.retrieve(state['query'])
    return {"retrieved_docs": [doc.page_content for doc in docs]}
```

**作用：** 从向量数据库找到与主题相关的论文片段

#### 节点 2：Summarizer（总结器）
```python
def summarizer(state):
    """生成综述"""
    context = "\n\n".join(state['retrieved_docs'])
    prompt = f"基于以下文档，写一篇关于 {state['query']} 的综述：\n{context}"
    summary = llm.invoke(prompt)
    return {"summary": summary.content}
```

**作用：** 将多个文档片段整合成一篇连贯的综述

#### 节点 3：Reviewer（审核器）
```python
def reviewer(state):
    """审核综述质量"""
    prompt = f"评审以下综述，返回 JSON：{state['summary']}"
    result = llm.invoke(prompt)
    
    # 解析审核结果
    review = json.loads(result.content)
    
    # 决策：通过 or 需要优化？
    if review['approved'] or review['score'] >= 8:
        return Command(goto=END)  # 结束
    else:
        return Command(goto="refiner")  # 继续优化
```

**作用：** 
- 评估综述质量（内容、逻辑、学术性等）
- 决定是否需要优化
- 使用 `Command` 控制流程跳转

#### 节点 4：Refiner（优化器）
```python
def refiner(state):
    """根据反馈优化综述"""
    prompt = f"""
    当前综述：{state['summary']}
    审核反馈：{state['review_feedback']}
    请优化综述。
    """
    refined = llm.invoke(prompt)
    
    # 返回 reviewer 重新审核
    return Command(
        update={"summary": refined.content},
        goto="reviewer"
    )
```

**作用：** 根据审核意见改进综述，形成优化循环

### 3. 工作流图结构

```python
graph = StateGraph(RAGWritingState)

# 添加节点
graph.add_node("retriever", retriever)
graph.add_node("summarizer", summarizer)
graph.add_node("reviewer", reviewer)
graph.add_node("refiner", refiner)

# 设置流程
graph.set_entry_point("retriever")
graph.add_edge("retriever", "summarizer")
graph.add_edge("summarizer", "reviewer")
# reviewer → refiner → reviewer 的循环由 Command 控制
```

**流程图：**
```
[START]
   ↓
[Retriever] ← 检索相关论文
   ↓
[Summarizer] ← 生成初步综述
   ↓
[Reviewer] ← 审核质量
   ↓
   ├─ 通过 → [END]
   └─ 不通过 → [Refiner] ← 优化综述
                   ↓
              返回 [Reviewer]
```

## 🔑 关键技术点

### 1. 状态管理
```python
class RAGWritingState(TypedDict):
    query: str                    # 查询主题
    retrieved_docs: list[str]     # 检索到的文档
    summary: str                  # 当前综述
    review_feedback: str          # 审核反馈
    approved: bool                # 是否通过
    iteration: int                # 迭代次数
```

**为什么需要状态？**
- 在多个节点之间传递数据
- 记录工作流的执行历史
- 支持断点恢复

### 2. Command 控制流程
```python
# 条件跳转
if approved:
    return Command(goto=END)
else:
    return Command(goto="refiner")

# 更新状态并跳转
return Command(
    update={"summary": new_summary},
    goto="reviewer"
)
```

**Command 的作用：**
- 动态控制节点跳转
- 实现条件分支和循环
- 比静态边更灵活

### 3. 迭代控制
```python
new_iteration = state['iteration'] + 1

if new_iteration >= max_iterations:
    return Command(goto=END)  # 防止无限循环
```

**为什么需要？**
- 避免无限优化循环
- 控制成本和时间
- 保证流程一定会结束

### 4. MMR 检索算法
```python
docs = vectorstore.max_marginal_relevance_search(
    query,
    k=3,           # 返回 3 个结果
    fetch_k=6      # 先取 6 个候选
)
```

**MMR vs 普通相似度检索：**
- 普通检索：可能返回 3 个几乎相同的文档
- MMR：在相关性和多样性之间平衡，返回更丰富的信息

## 🚀 使用方法

### 步骤 1：准备数据
```bash
# 构建向量索引（如果还没有）
python scripts/build_index.py
```

### 步骤 2：运行综述写作
```bash
python scripts/run_rag_writing.py
```

### 步骤 3：查看结果
- 终端会显示完整的执行过程
- 最终综述保存在 `output_rag_summary.txt`

## 💡 进阶优化建议

### 1. 改进检索质量
```python
# 使用重排序模型
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

compressor = CohereRerank()
retriever = ContextualCompressionRetriever(
    base_retriever=vectorstore.as_retriever(),
    base_compressor=compressor
)
```

### 2. 添加引用功能
```python
def summarizer(state):
    # 在综述中标注引用来源
    for i, doc in enumerate(state['retrieved_docs']):
        context += f"[{i+1}] {doc.page_content}\n"
    
    prompt = f"写综述时，用 [1], [2] 等标注引用来源"
```

### 3. 支持多种写作风格
```python
def summarizer(state):
    style = state.get('style', 'academic')  # academic, popular, technical
    prompt = f"用{style}风格写综述..."
```

### 4. 添加人工审核节点
```python
def human_review(state):
    """人工审核节点"""
    print(f"当前综述：\n{state['summary']}")
    feedback = input("请输入修改意见（直接回车表示通过）：")
    
    if not feedback:
        return Command(goto=END)
    else:
        return Command(
            update={"review_feedback": feedback},
            goto="refiner"
        )
```

## 🎓 学习要点总结

1. **RAG 的本质**：检索 + 生成，让 LLM 基于事实回答
2. **Agent 的价值**：自主决策、多步推理、工具调用
3. **LangGraph 的优势**：可视化工作流、状态管理、条件跳转
4. **迭代优化**：通过 reviewer → refiner 循环提升质量
5. **工程实践**：错误处理、迭代限制、结果保存

## 📖 相关资源

- LangGraph 文档：https://langchain-ai.github.io/langgraph/
- FAISS 向量检索：https://github.com/facebookresearch/faiss
- MMR 算法论文：Maximal Marginal Relevance (Carbonell & Goldstein, 1998)
