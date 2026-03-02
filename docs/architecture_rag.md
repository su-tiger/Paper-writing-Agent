# RAG + Agent 系统架构

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│  - 输入主题                                                  │
│  - 查看结果                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Scripts)                        │
│  - run_rag_writing.py: 运行工作流                           │
│  - build_index.py: 构建向量索引                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    工作流层 (Workflows)                      │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  RAG Writing Graph (rag_writing_graph.py)    │          │
│  │                                               │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │          │
│  │  │Retriever │→ │Summarizer│→ │ Reviewer │  │          │
│  │  └──────────┘  └──────────┘  └────┬─────┘  │          │
│  │                                    │         │          │
│  │                                    ▼         │          │
│  │                              ┌──────────┐   │          │
│  │                              │ Refiner  │   │          │
│  │                              └────┬─────┘   │          │
│  │                                   │         │          │
│  │                                   └─────────┘          │
│  └──────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Agent 层 (Agents)                        │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  RAG Agent (rag_agent.py)                    │          │
│  │  - retrieve(): 检索文档                       │          │
│  │  - run(): 完整 RAG 流程                       │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      RAG 层 (RAG)                            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Loader  │→ │ Splitter │→ │Embedding │→ │VectorStore│ │
│  │ (加载PDF) │  │ (文档切分)│  │ (向量化) │  │ (FAISS)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data)                           │
│  - PDF 文件 (data/pdf/)                                     │
│  - 向量索引 (data/faiss_index/)                             │
└─────────────────────────────────────────────────────────────┘
```

## 📦 模块详解

### 1. RAG 模块 (`src/rag/`)

负责文档的加载、处理和检索。

```
src/rag/
├── loader.py          # PDF 加载
│   └── load_pdf()     # 读取 PDF 文件
│
├── splitter.py        # 文档切分
│   └── split_documents()  # 将长文档切成小块
│
├── embedding.py       # 文本向量化
│   └── create_embeddings()  # 创建嵌入模型
│
└── vectorstore.py     # 向量存储
    ├── build_faiss_index()  # 构建索引
    ├── save_index()         # 保存索引
    └── load_index()         # 加载索引
```

**数据流：**
```
PDF 文件 → Loader → 文档对象 → Splitter → 文档块 
→ Embedding → 向量 → VectorStore → FAISS 索引
```

### 2. Agent 模块 (`src/agents/`)

封装了智能代理的能力。

```
src/agents/
├── base_agent.py      # Agent 基类
│   └── BaseAgent      # 定义 run() 接口
│
├── simple_agent.py    # 简单 Agent
│   └── SimpleAgent    # 基础实现
│
└── rag_agent.py       # ⭐ RAG Agent
    └── RAGAgent
        ├── retrieve()  # 检索文档
        └── run()       # 完整 RAG 流程
```

**RAG Agent 工作流：**
```
query → retrieve() → 检索文档 → 构建上下文 
→ LLM 生成 → 返回答案
```

### 3. 工作流模块 (`src/workflows/`)

使用 LangGraph 构建的多节点工作流。

```
src/workflows/
├── writing_graph.py       # 基础写作工作流
│   └── create_writing_graph()
│       ├── planner    # 生成大纲
│       ├── writerA    # 写作 A
│       ├── writerB    # 写作 B
│       └── reviewer   # 审核
│
└── rag_writing_graph.py   # ⭐ RAG 写作工作流
    └── create_rag_writing_graph()
        ├── retriever   # 检索文档
        ├── summarizer  # 生成综述
        ├── reviewer    # 审核质量
        └── refiner     # 优化综述
```

**RAG 工作流详细流程：**
```
[START]
   ↓
[Retriever]
   - 调用 RAG Agent 检索文档
   - 返回 3-5 个相关文档片段
   ↓
[Summarizer]
   - 接收检索到的文档
   - 构建 prompt（包含所有文档）
   - 调用 LLM 生成综述
   ↓
[Reviewer]
   - 评估综述质量（1-10 分）
   - 从多个维度评分：
     * 内容完整性 30%
     * 逻辑性 25%
     * 学术性 20%
     * 创新性 15%
     * 可读性 10%
   - 决策：
     * 评分 ≥ 8 → 通过 → END
     * 评分 < 8 → 需要优化 → Refiner
     * 达到最大次数 → END
   ↓
[Refiner]
   - 接收审核反馈
   - 根据反馈优化综述
   - 返回 Reviewer 重新审核
   ↓
(循环直到通过或达到最大次数)
   ↓
[END]
```

## 🔄 数据流转

### 1. 索引构建阶段

```
用户运行: python scripts/build_index.py
   ↓
读取 data/pdf/*.pdf
   ↓
Loader.load_pdf() → 文档对象
   ↓
Splitter.split_documents() → 文档块 (500 字/块)
   ↓
Embedding.create_embeddings() → 向量化
   ↓
VectorStore.build_faiss_index() → FAISS 索引
   ↓
保存到 data/faiss_index/
```

### 2. 综述生成阶段

```
用户运行: python scripts/run_rag_writing.py
   ↓
输入主题: "深度学习在 NLP 中的应用"
   ↓
创建工作流: create_rag_writing_graph()
   ↓
初始化状态:
{
  query: "深度学习在 NLP 中的应用",
  retrieved_docs: [],
  summary: "",
  iteration: 0
}
   ↓
[Retriever 节点]
   - 加载向量索引
   - 使用 MMR 检索相关文档
   - 更新状态: retrieved_docs = [doc1, doc2, doc3]
   ↓
[Summarizer 节点]
   - 构建 prompt（包含所有检索到的文档）
   - 调用 LLM 生成综述
   - 更新状态: summary = "生成的综述内容..."
   ↓
[Reviewer 节点]
   - 评估综述质量
   - 生成审核结果: {approved: false, score: 7, feedback: "..."}
   - 决策: score < 8 → 跳转到 Refiner
   ↓
[Refiner 节点]
   - 根据反馈优化综述
   - 更新状态: summary = "优化后的综述..."
   - 跳转回 Reviewer
   ↓
[Reviewer 节点] (第二次)
   - 再次评估
   - 结果: {approved: true, score: 9}
   - 决策: score ≥ 8 → 结束
   ↓
保存结果到 output_rag_summary.txt
```

## 🎯 关键技术点

### 1. MMR 检索算法

```python
# 在 RAGAgent.retrieve() 中使用
docs = self.vectorstore.max_marginal_relevance_search(
    query,
    k=3,        # 返回 3 个结果
    fetch_k=6   # 先从 6 个候选中选择
)
```

**为什么用 MMR？**
- 普通相似度检索可能返回 3 个几乎相同的文档
- MMR 在相关性和多样性之间平衡
- 确保检索结果覆盖更广的信息

### 2. 状态管理

```python
class RAGWritingState(TypedDict):
    query: str                    # 查询主题
    retrieved_docs: list[str]     # 检索到的文档
    summary: str                  # 当前综述
    review_feedback: str          # 审核反馈
    approved: bool                # 是否通过
    iteration: int                # 迭代次数
```

**状态在节点间传递：**
```
Retriever → 更新 retrieved_docs
   ↓
Summarizer → 读取 retrieved_docs，更新 summary
   ↓
Reviewer → 读取 summary，更新 review_feedback
   ↓
Refiner → 读取 review_feedback，更新 summary
```

### 3. 条件跳转 (Command)

```python
def reviewer(state):
    result = evaluate(state['summary'])
    
    if result.score >= 8:
        return Command(goto=END)  # 通过，结束
    elif state['iteration'] >= max_iterations:
        return Command(goto=END)  # 达到最大次数，结束
    else:
        return Command(goto="refiner")  # 需要优化
```

**Command 的作用：**
- 动态控制流程跳转
- 实现条件分支和循环
- 比静态边更灵活

### 4. 迭代控制

```python
# 防止无限循环
new_iteration = state['iteration'] + 1

if new_iteration >= max_iterations:
    return Command(goto=END)  # 强制结束
```

## 📊 性能优化

### 1. 向量检索优化

```python
# 使用 FAISS 的 IVF 索引（适合大规模数据）
from langchain_community.vectorstores import FAISS

# 构建索引时
vectorstore = FAISS.from_documents(
    documents,
    embeddings,
    # 可以添加索引参数优化性能
)
```

### 2. 批量处理

```python
# 批量生成多个综述
topics = ["主题1", "主题2", "主题3"]

for topic in topics:
    result = run_workflow(topic)
    save_result(topic, result)
```

### 3. 缓存机制

```python
# 使用 LangGraph 的 checkpointer
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# 支持断点恢复
config = {"configurable": {"thread_id": "session_1"}}
```

## 🔐 安全性考虑

### 1. API Key 管理

```python
# 使用环境变量
from dotenv import load_dotenv
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
```

### 2. 输入验证

```python
def validate_query(query: str) -> bool:
    if not query or len(query) < 5:
        return False
    if len(query) > 500:
        return False
    return True
```

### 3. 错误处理

```python
try:
    result = llm.invoke(prompt)
except Exception as e:
    logger.error(f"LLM 调用失败: {e}")
    return default_response
```

## 🚀 扩展方向

### 1. 支持更多文档格式

```python
# 添加 Word、Markdown 等格式支持
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader
)
```

### 2. 添加引用标注

```python
def summarizer_with_citations(state):
    context = "\n\n".join([
        f"[{i+1}] {doc}"
        for i, doc in enumerate(state['retrieved_docs'])
    ])
    
    prompt += "\n请在综述中用 [1], [2] 标注引用来源"
```

### 3. 支持多语言

```python
def summarizer(state):
    language = state.get('language', 'zh')
    
    if language == 'en':
        prompt = "Write a review in English..."
    else:
        prompt = "用中文写一篇综述..."
```

### 4. 添加人工审核

```python
def human_review(state):
    print(f"综述：\n{state['summary']}")
    feedback = input("请输入修改意见：")
    
    if not feedback:
        return Command(goto=END)
    else:
        return Command(
            update={"review_feedback": feedback},
            goto="refiner"
        )
```

## 📚 相关资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [FAISS 文档](https://github.com/facebookresearch/faiss)
- [LangChain 文档](https://python.langchain.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 🎓 学习建议

1. **理解 RAG 原理**：先检索，再生成
2. **掌握 LangGraph**：状态管理、节点、边、Command
3. **熟悉向量检索**：嵌入、相似度、MMR
4. **实践迭代优化**：审核 → 反馈 → 优化循环

这就是整个 RAG + Agent 系统的完整架构！🎉
