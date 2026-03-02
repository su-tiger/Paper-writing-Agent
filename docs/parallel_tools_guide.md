# 并发工具调用指南

## 概述

系统现在支持并发执行多个工具，可以显著提升性能。

## 核心组件

### 1. BaseTool 异步支持

所有工具现在支持异步执行：

```python
class BaseTool(ABC):
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """同步执行（保持向后兼容）"""
        pass
    
    async def arun(self, **kwargs) -> Any:
        """异步执行（默认在线程池中运行 run()）"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.run(**kwargs))
```

### 2. ToolExecutor 并发执行器

提供并发和串行两种执行模式：

```python
from src.tools.tool_executor import ToolExecutor

# 并发执行
results = await ToolExecutor.execute_parallel([
    (retriever_tool, {"query": "深度学习"}),
    (calculator_tool, {"expression": "1+1"}),
])

# 串行执行（用于对比）
results = await ToolExecutor.execute_sequential([...])
```

### 3. SimpleAgent 智能并发

SimpleAgent 会自动判断是否需要并发：

```python
agent = SimpleAgent(llm, registry)

# 自动检测并发需求
result = agent.run("搜索深度学习并计算 1+1")

# 如果 LLM 判断需要多个工具，会自动并发执行
```

## 使用示例

### 示例 1: 基础并发执行

```python
import asyncio
from src.tools.tool_executor import ToolExecutor
from src.tools.retriever_tool import FAISSRetrieverTool

# 准备工具和输入
tools_and_inputs = [
    (retriever_tool, {"query": "深度学习"}),
    (retriever_tool, {"query": "机器学习"}),
]

# 并发执行
results = asyncio.run(ToolExecutor.execute_parallel(tools_and_inputs))

# 处理结果
for result in results:
    if result["error"]:
        print(f"错误: {result['error']}")
    else:
        print(f"结果: {result['result']}")
```

### 示例 2: UnifiedAgent 自动并发

```python
from src.core.unified_agent import UnifiedAgent

agent = UnifiedAgent(vectorstore=vectorstore)

# Agent 会自动判断是否需要并发
for event in agent.stream("搜索深度学习和机器学习的区别"):
    if event.type == "tool_start":
        print(f"调用工具: {event.data['tool_name']}")
    elif event.type == "end":
        print(f"结果: {event.data['result']}")
```

### 示例 3: 自定义异步工具

如果你的工具本身支持异步，可以重写 `arun()` 方法：

```python
class AsyncAPITool(BaseTool):
    name = "async_api"
    description = "异步 API 调用"
    
    def run(self, query: str):
        # 同步版本（向后兼容）
        return requests.get(f"https://api.example.com?q={query}").text
    
    async def arun(self, query: str):
        # 真正的异步实现
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com?q={query}") as resp:
                return await resp.text()
```

## 性能对比

假设每个工具调用需要 2 秒：

- **串行执行**: 2 个工具 = 4 秒
- **并发执行**: 2 个工具 = 2 秒（提升 50%）

## 错误处理

并发执行时，单个工具的错误不会影响其他工具：

```python
results = await ToolExecutor.execute_parallel([
    (tool1, {"query": "正常查询"}),
    (tool2, {"query": "会出错的查询"}),
])

# 结果格式
[
    {"tool": "tool1", "result": "...", "error": None},
    {"tool": "tool2", "result": None, "error": "错误信息"},
]
```

## 测试

运行测试脚本：

```bash
python scripts/test_parallel_tools.py
```

## 注意事项

1. **LLM 决策**: SimpleAgent 依赖 LLM 判断是否需要并发，可能不总是准确
2. **线程安全**: 确保你的工具是线程安全的
3. **资源限制**: 并发数量受系统资源限制
4. **向后兼容**: 所有现有代码无需修改即可工作

## 未来改进

- [ ] 支持限制最大并发数
- [ ] 支持工具依赖关系（DAG 执行）
- [ ] 支持超时控制
- [ ] 支持重试机制
