# 评估系统使用指南

## 概述

本项目提供了一个完整的评估系统，用于评估 RAG、Agent 和 Workflow 的性能和质量。

## 评估维度

### 1. RAG 系统评估

#### 检索质量指标
- **Precision（精确率）**: 检索结果中相关文档的比例
- **Recall（召回率）**: 相关文档被检索到的比例
- **F1 Score**: 精确率和召回率的调和平均
- **MRR（平均倒数排名）**: 第一个相关文档的排名倒数
- **NDCG（归一化折损累积增益）**: 考虑排序的检索质量
- **Relevance Score（相关性得分）**: 平均相关性评分

#### 生成质量指标
- **Fluency（流畅度）**: 语言是否流畅自然 (1-10)
- **Coherence（连贯性）**: 逻辑是否清晰连贯 (1-10)
- **Relevance（相关性）**: 是否回答了问题 (1-10)
- **Factuality（事实准确性）**: 内容是否准确可靠 (1-10)
- **Completeness（完整性）**: 是否全面完整 (1-10)
- **Overall Score（综合得分）**: 加权平均分 (1-10)

### 2. Agent 系统评估

#### 工具选择评估
- 工具选择的准确性
- 是否有遗漏的必要工具
- 是否有不必要的工具

#### 推理过程评估
- **Logic Score（逻辑得分）**: 推理逻辑是否清晰
- **Completeness Score（完整性得分）**: 推理是否完整
- **Efficiency Score（效率得分）**: 推理是否高效
- **Correctness Score（正确性得分）**: 推理是否正确

#### 答案质量评估
- 与 RAG 生成质量指标相同

### 3. Workflow 系统评估

#### 执行效率指标
- **Total Time（总时间）**: 工作流总执行时间
- **Node Times（节点时间）**: 各节点执行时间
- **Iterations（迭代次数）**: 实际迭代次数
- **Success（成功状态）**: 是否成功完成
- **Error Count（错误次数）**: 执行过程中的错误次数

#### 工作流设计评估
- **Logic Score（逻辑得分）**: 流程逻辑是否清晰
- **Efficiency Score（效率得分）**: 流程是否高效
- **Robustness Score（健壮性得分）**: 错误处理能力
- **Flexibility Score（灵活性得分）**: 流程灵活性

#### 最终输出质量
- 与 RAG 生成质量指标相同

## 使用方法

### 1. 单次评估

#### 评估 RAG 系统

```bash
python scripts/run_evaluation.py --type rag
```

#### 评估 Agent 系统

```bash
python scripts/run_evaluation.py --type agent
```

#### 评估 Workflow 系统

```bash
python scripts/run_evaluation.py --type workflow
```

#### 评估所有系统

```bash
python scripts/run_evaluation.py --type all
```

### 2. 批量评估

#### 创建测试集

```bash
python scripts/batch_evaluation.py --create-sample
```

这会在 `data/test_sets/` 目录下创建示例测试集：
- `rag_test_set.json`: RAG 测试集
- `agent_test_set.json`: Agent 测试集

#### 运行批量评估

```bash
# 批量评估 RAG
python scripts/batch_evaluation.py --type rag --test-set data/test_sets/rag_test_set.json

# 批量评估 Agent
python scripts/batch_evaluation.py --type agent --test-set data/test_sets/agent_test_set.json
```

### 3. 在代码中使用

#### 评估 RAG

```python
from src.evaluation import RAGEvaluator
from src.core.unified_agent import UnifiedAgent
from src.rag import load_index
from langchain_openai import ChatOpenAI
from src.config import Config

# 初始化
llm = ChatOpenAI(
    model=Config.DEEPSEEK_MODEL,
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.DEEPSEEK_BASE_URL
)
vectorstore = load_index()
agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
evaluator = RAGEvaluator(llm=llm)

# 执行查询
query = "什么是 CLIP 模型？"
result = agent.run(query, mode="rag")

# 获取检索文档
from src.agents.rag_agent import RAGAgent
rag_agent = RAGAgent(llm=llm, vectorstore=vectorstore)
docs = rag_agent.retrieve(query)
retrieved_docs = [doc.page_content for doc in docs]

# 评估
report = evaluator.evaluate(
    query=query,
    retrieved_docs=retrieved_docs,
    generated_text=result
)

# 查看报告
print(report.summary())
```

#### 评估 Agent

```python
from src.evaluation import AgentEvaluator
import time

evaluator = AgentEvaluator(llm=llm)

# 执行任务
task = "检索关于 Transformer 的信息并总结"
start_time = time.time()
result = agent.run(task, mode="simple")
execution_time = time.time() - start_time

# 评估
report = evaluator.evaluate(
    task=task,
    selected_tools=["retriever"],
    reasoning_steps=["分析任务", "选择工具", "执行检索", "生成总结"],
    final_answer=result,
    execution_time=execution_time
)

print(report.summary())
```

#### 评估 Workflow

```python
from src.evaluation import WorkflowEvaluator

evaluator = WorkflowEvaluator(llm=llm)

# 执行工作流
task = "深度学习在计算机视觉中的应用"
start_time = time.time()
result = agent.run(task, mode="workflow", max_iterations=2)
total_time = time.time() - start_time

# 评估
report = evaluator.evaluate(
    task=task,
    workflow_description="RAG + Agent 综述写作工作流",
    node_sequence=["retriever", "summarizer", "reviewer"],
    node_outputs={
        "retriever": "检索到 3 个文档",
        "summarizer": "生成综述",
        "reviewer": "审核通过"
    },
    final_output=result,
    total_time=total_time,
    node_times={"retriever": 2.5, "summarizer": 8.3, "reviewer": 3.2},
    iterations=1,
    max_iterations=2,
    success=True
)

print(report.summary())
```

## 测试集格式

### RAG 测试集

```json
[
  {
    "query": "什么是 CLIP 模型？",
    "reference_answer": "CLIP 是一个多模态模型...",
    "ground_truth_docs": ["doc1", "doc2"]  // 可选
  }
]
```

### Agent 测试集

```json
[
  {
    "task": "检索并总结 Transformer 的核心特点",
    "expected_tools": ["retriever"],
    "reference_answer": "Transformer 使用自注意力机制..."
  }
]
```

## 评估报告

评估报告会保存在 `data/evaluation_reports/` 目录下，包含：

1. **单次评估报告**: `{type}_evaluation_{timestamp}.json`
2. **批量评估结果**: `batch_{type}_{timestamp}.json`
3. **统计报告**: `batch_{type}_stats_{timestamp}.json`

### 报告结构

```json
{
  "task_type": "RAG",
  "task_description": "什么是 CLIP 模型？",
  "timestamp": "2024-01-01T12:00:00",
  "retrieval_metrics": {
    "precision": 0.85,
    "recall": 0.75,
    "f1_score": 0.80,
    "mrr": 0.90,
    "ndcg": 0.88,
    "relevance_score": 0.82
  },
  "generation_metrics": {
    "fluency": 8.5,
    "coherence": 8.0,
    "relevance": 9.0,
    "factuality": 8.5,
    "completeness": 8.0,
    "overall_score": 8.4
  },
  "comments": "评估备注"
}
```

## 自定义评估

### 添加自定义指标

```python
from src.evaluation.base_evaluator import BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    def evaluate(self, **kwargs):
        # 实现自定义评估逻辑
        pass
```

### 扩展现有评估器

```python
from src.evaluation import RAGEvaluator

class ExtendedRAGEvaluator(RAGEvaluator):
    def evaluate_custom_metric(self, query, result):
        # 添加自定义评估指标
        pass
```

## 最佳实践

1. **定期评估**: 在模型或系统更新后进行评估
2. **使用测试集**: 创建标准测试集以便对比不同版本
3. **多维度评估**: 同时关注检索质量和生成质量
4. **保存历史**: 保留评估历史以追踪性能变化
5. **人工审核**: 对于关键应用，结合人工审核

## 常见问题

### Q: 评估需要多长时间？

A: 单次评估通常需要 10-30 秒，批量评估取决于测试集大小。

### Q: 如何提高评估准确性？

A: 
- 提供参考答案和真实标注
- 使用更强的 LLM 进行评估
- 增加测试用例数量

### Q: 评估结果如何解读？

A:
- 8-10 分：优秀
- 6-8 分：良好
- 4-6 分：一般
- <4 分：需要改进

## 相关文档

- [架构文档](architecture.md)
- [RAG 快速入门](rag_quickstart.md)
- [工作流图解](workflow_diagram.md)
