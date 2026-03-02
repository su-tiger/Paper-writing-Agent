# 项目架构文档

## 整体架构

本项目采用模块化设计，主要分为以下几个模块：

### 1. RAG 模块 (`src/rag/`)

负责文档处理和向量检索：

- `loader.py`: PDF 文档加载
- `splitter.py`: 文档切分
- `embedding.py`: 文本嵌入
- `vectorstore.py`: 向量存储管理

**工作流程：**
```
PDF 文档 → 加载 → 切分 → 嵌入 → FAISS 索引 → 检索
```

### 2. Agent 模块 (`src/agents/`)

实现智能代理：

- `base_agent.py`: Agent 抽象基类
- `simple_agent.py`: 基于 ReAct 模式的简单 Agent

**工作流程：**
```
用户查询 → 决策（是否使用工具）→ 工具调用 → 生成答案
```

### 3. 工具模块 (`src/tools/`)

提供 Agent 使用的工具：

- `base_tool.py`: 工具抽象基类
- `retriever_tool.py`: FAISS 检索工具
- `tool_registry.py`: 工具注册表

### 4. 工作流模块 (`src/workflows/`)

基于 LangGraph 的复杂工作流：

- `writing_graph.py`: 多 Agent 写作工作流

**工作流程：**
```
Planner → Dispatch → [WriterA, WriterB] → Reviewer
    ↑                                          ↓
    └──────────────── 反馈循环 ─────────────────┘
```

### 5. 配置模块 (`src/config.py`)

统一的配置管理，支持环境变量。

## 设计模式

### 1. 抽象基类模式

- `BaseAgent`: 所有 Agent 的基类
- `BaseTool`: 所有工具的基类

**优点：**
- 统一接口
- 易于扩展
- 类型安全

### 2. 注册表模式

`ToolRegistry` 管理所有工具：

```python
registry = ToolRegistry()
registry.register(tool)
tool = registry.get("tool_name")
```

**优点：**
- 动态管理工具
- 解耦工具和 Agent
- 易于测试

### 3. 工厂模式

`create_embeddings()` 和 `create_writing_graph()` 使用工厂模式：

```python
embeddings = create_embeddings()
graph = create_writing_graph()
```

**优点：**
- 封装创建逻辑
- 统一配置管理
- 易于测试和替换

## 数据流

### RAG 问答系统

```
用户查询
    ↓
SimpleAgent.run()
    ↓
decide() - 判断是否需要工具
    ↓
FAISSRetrieverTool.run() - 检索相关文档
    ↓
LLM 生成答案
    ↓
返回结果
```

### 写作工作流

```
初始状态
    ↓
Planner - 生成大纲
    ↓
Dispatch - 分发任务
    ↓
[WriterA, WriterB] - 并行写作
    ↓
Reviewer - 审核
    ↓
判断：通过？需要修改大纲？需要修改正文？
    ↓
循环或结束
```

## 扩展指南

### 添加新的检索方法

1. 在 `src/rag/vectorstore.py` 添加新函数
2. 在 `FAISSRetrieverTool` 中添加新方法选项

### 添加新的 Agent

1. 创建新文件继承 `BaseAgent`
2. 实现 `run` 方法
3. 在 `__init__.py` 中导出

### 添加新的工作流节点

1. 在 `writing_graph.py` 中定义新节点函数
2. 在 `create_writing_graph()` 中添加节点和边

## 性能优化

### 1. 向量索引优化

- 使用 FAISS 的 IVF 索引提高检索速度
- 调整 `chunk_size` 和 `chunk_overlap` 参数

### 2. 并行处理

- 多个 Writer 并行工作
- 批量处理文档

### 3. 缓存机制

- 缓存嵌入结果
- 缓存 LLM 响应（开发环境）

## 安全考虑

1. **API Key 管理**: 使用环境变量，不要硬编码
2. **输入验证**: 验证用户输入，防止注入攻击
3. **反序列化安全**: FAISS 加载时注意安全风险
4. **错误处理**: 完善的异常处理机制

## 测试策略

1. **单元测试**: 测试各个模块的核心功能
2. **集成测试**: 测试模块间的协作
3. **端到端测试**: 测试完整的工作流

## 未来改进

1. 支持更多文档格式（Word, Markdown 等）
2. 添加更多检索策略（混合检索、重排序等）
3. 支持流式输出
4. 添加 Web UI
5. 支持多语言
