"""
统一 Agent：融合 SimpleAgent、RAGAgent、LangGraph 三大框架

核心特性：
1. 智能路由：自动选择最佳执行模式
2. 统一接口：一个 run() 方法处理所有任务
3. 事件流系统：所有输出都通过 StreamEvent
4. 灵活扩展：易于添加新模式和新工具
"""

from typing import Optional, Any, Generator
from langchain_openai import ChatOpenAI
import json
import re

from .router import TaskRouter, TaskMode
from .stream_event import StreamEvent
from ..agents.simple_agent import SimpleAgent
from ..agents.rag_agent import RAGAgent
from ..tools.tool_registry import ToolRegistry
from ..tools.retriever_tool import FAISSRetrieverTool
from ..config import Config







class UnifiedAgent:
    """
    统一 Agent：系统级的智能代理
    
    使用示例：
        agent = UnifiedAgent(llm, vectorstore)
        
        # 自动模式
        result = agent.run("什么是深度学习？")
        
        # 指定模式
        result = agent.run("写一篇综述", mode="workflow")
    """
    
    def __init__(
        self,
        llm=None,
        vectorstore=None,
        tool_registry=None,
        enable_logging=True
    ):
        """
        初始化统一 Agent
        
        Args:
            llm: 大语言模型实例
            vectorstore: 向量存储实例
            tool_registry: 工具注册表（可选）
            enable_logging: 是否启用日志
        """
        # 初始化 LLM
        self.llm = llm or ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
        
        # 初始化向量存储
        self.vectorstore = vectorstore
        
        # 初始化工具注册表
        self.tool_registry = tool_registry or self._init_tool_registry()
        
        # 初始化路由器
        self.router = TaskRouter(llm=self.llm)
        
        # 初始化各个子 Agent
        self._init_sub_agents()
        
        # 日志开关
        self.enable_logging = enable_logging
    
    def _init_tool_registry(self) -> ToolRegistry:
        """初始化工具注册表"""
        registry = ToolRegistry()
        
        # 注册检索工具
        if self.vectorstore:
            retriever_tool = FAISSRetrieverTool(self.vectorstore)
            registry.register(retriever_tool)
        
        return registry
    
    def _init_sub_agents(self):
        """初始化各个子 Agent"""
        # SimpleAgent（ReAct 模式）
        self.simple_agent = SimpleAgent(
            llm=self.llm,
            registry=self.tool_registry
        )
        
        # RAGAgent（RAG 模式）
        if self.vectorstore:
            self.rag_agent = RAGAgent(
                llm=self.llm,
                vectorstore=self.vectorstore
            )
        else:
            self.rag_agent = None
        
        # WorkflowAgent（工作流模式）
        # 注意：需要时才创建，避免依赖 langgraph
        self.workflow_agent = None
    def collaborate(
        self,
        task: str,
        agents: list,  # [("rag", {}), ("simple", {})]
        **kwargs
    ) -> Generator[StreamEvent, None, None]:
        """
        多 Agent 协作执行
        
        Args:
            task: 任务
            agents: Agent 列表 [(mode, config), ...]
            
        Example:
            # RAG 检索 → Simple 分析
            agent.collaborate(
                "分析深度学习",
                agents=[
                    ("rag", {}),      # 先用 RAG 检索
                    ("simple", {})    # 再用 Simple 分析
                ]
            )
        """
        context = {"task": task}
        
        # 按顺序执行每个 Agent
        for mode, config in agents:
            yield StreamEvent.node_start(
                node_name=mode,
                state=context
            )
            
            # 执行 Agent（传入 context）
            if mode == "rag":
                result = self._run_rag_with_context(task, context, **config)
            elif mode == "simple":
                result = self._run_simple_with_context(task, context, **config)
            elif mode == "workflow":
                result = self._run_workflow_with_context(task, context, **config)
            
            context[f"{mode}_result"] = result
            
            yield StreamEvent.node_end(
                node_name=mode,
                state=context
            )
        
        # 返回最终结果
        final_result = context.get(f"{agents[-1][0]}_result", "")
        yield StreamEvent.end(result=final_result, mode="collaborate")
    def _run_rag_with_context(self, task, context, **kwargs):
        """RAG 模式（带 context）"""
        # 调用 RAGAgent，传入 context
        return self.rag_agent.run(task, context=context)

    def _run_simple_with_context(self, task, context, **kwargs):
        """Simple 模式（带 context）"""
        # 调用 SimpleAgent，传入 context
        return self.simple_agent.run(task, context=context)

    def _run_workflow_with_context(self, task, context, **kwargs):
        """Workflow 模式（带 context）"""
        # 延迟导入
        try:
            from ..workflows.rag_writing_graph import create_rag_writing_graph
            from langgraph.checkpoint.memory import MemorySaver
        except ImportError:
            return "工作流模式需要安装 langgraph: pip install langgraph"
        
        # 创建工作流
        graph = create_rag_writing_graph(
            llm=self.llm,
            rag_agent=self.rag_agent,
            max_iterations=kwargs.get('max_iterations', 3)
        )
        
        # 编译工作流
        memory = MemorySaver()
        app = graph.compile(checkpointer=memory)
        
        # 初始化状态（可以从 context 读取初始数据）
        initial_state = {
            "query": task,
            "retrieved_docs": context.get("retrieved_docs", []),
            "summary": "",
            "review_feedback": "",
            "refined_summary": "",
            "approved": False,
            "iteration": 0,
            "max_iterations": kwargs.get('max_iterations', 3)
        }
        
        # 运行工作流
        config = {"configurable": {"thread_id": "unified_agent"}}
        
        final_state = None
        for state in app.stream(initial_state, config):
            final_state = state
        
        # 提取结果
        if final_state:
            last_node = list(final_state.keys())[0]
            result = final_state[last_node]
            final_result = result.get('refined_summary') or result.get('summary', '')
            
            # 保存到 context
            context["workflow_result"] = final_result
            
            return final_result
        
        return "工作流执行失败"
        graph.set_entry_point("retriever")
        
        # 添加边：定义节点之间的流转关系
        graph.add_edge("retriever", "summarizer")
        graph.add_edge("summarizer", "reviewer")
        # reviewer 和 refiner 的流转由 Command 控制，不需要显式添加边
        
        return graph
    
    def research_and_write(self, task: str):
        """研究 + 写作模式"""
        from .collaboration_patterns import RESEARCH_WRITE
        return self.collaborate(task, RESEARCH_WRITE)

    def deep_analysis(self, task: str):
        """深度分析模式"""
        from .collaboration_patterns import RETRIEVE_ANALYZE_SUMMARIZE
        return self.collaborate(task, RETRIEVE_ANALYZE_SUMMARIZE)

    def run(
        self,
        task: str,
        mode: TaskMode = "auto",
        **kwargs
    ) -> Any:
        """
        执行任务（非流式，返回最终结果）
        
        本质上调用 list(self.stream())[-1]
        
        Args:
            task: 用户任务描述
            mode: 执行模式（auto/simple/rag/workflow）
            **kwargs: 额外参数
            
        Returns:
            最终结果
        """
        # 收集所有事件
        events = list(self.stream(task, mode, **kwargs))
        
        # 返回最后一个事件的结果
        if events:
            last_event = events[-1]
            if last_event.type == "end":
                return last_event.data.get("result", "")
        
        return ""
    
    def stream(
        self,
        task: str,
        mode: TaskMode = "auto",
        **kwargs
    ) -> Generator[StreamEvent, None, None]:
        """
        流式执行任务（统一入口）
        
        所有模式都通过 StreamEvent 输出事件
        
        Args:
            task: 用户任务描述
            mode: 执行模式（auto/simple/rag/workflow）
            **kwargs: 额外参数
            
        Yields:
            StreamEvent 事件
        """
        try:
            # 1. 路由：选择最佳执行模式
            selected_mode = self.router.route(task, mode)
            
            # 2. 发送路由事件
            yield StreamEvent.route(
                task=task,
                selected_mode=selected_mode,
                reason=self.router.explain_route(task, selected_mode)
            )
            
            # 3. 发送开始事件
            yield StreamEvent.start(mode=selected_mode, task=task)
            
            # 4. 执行：根据模式调用相应的流式方法
            if selected_mode == "simple":
                yield from self._stream_simple(task, **kwargs)
            elif selected_mode == "rag":
                yield from self._stream_rag(task, **kwargs)
            elif selected_mode == "workflow":
                yield from self._stream_workflow(task, **kwargs)
            else:
                raise ValueError(f"未知模式: {selected_mode}")
            
        except Exception as e:
            # 发送错误事件
            yield StreamEvent.error(
                error_message=str(e),
                error_type=type(e).__name__
            )
    
    def _stream_simple(self, task: str, **kwargs) -> Generator[StreamEvent, None, None]:
        """
        Simple 模式流式执行（事件化）
        
        Args:
            task: 用户任务
            **kwargs: 额外参数
            
        Yields:
            StreamEvent 事件
        """
        # 1. LLM 决策（检查是否需要并发）
        yield StreamEvent.llm_start(prompt=f"决策任务: {task}")

        # 收集流式决策内容
        decision_text = ""
        for token in self.simple_agent.decide_parallel_stream(task):
            decision_text += token
            yield StreamEvent.llm_token(token=token)  # 实时输出决策过程

        yield StreamEvent.llm_end(content=decision_text)

        
        # 2. 解析决策
        try:
            decision = json.loads(decision_text)
        except:
            json_match = re.search(r'\{[\s\S]*\}', decision_text)
            if json_match:
                decision = json.loads(json_match.group())
            else:
                # JSON 解析失败
                yield StreamEvent.error(
                    error_message="决策 JSON 解析失败",
                    error_type="JSONDecodeError"
                )
                return
        
        tools_to_call = decision.get("tools", [])
        
        # 3. 如果不需要工具
        if not tools_to_call or tools_to_call[0].get("action") == "final":
            yield StreamEvent.end(
                result=tools_to_call[0].get("answer", ""),
                mode="simple"
            )
            return
        
        # 4. 准备工具调用（带参数验证）
        tools_and_inputs = []
        for tool_spec in tools_to_call:
            tool_name = tool_spec.get("action")
            tool_input = tool_spec.get("action_input")
            
            # 参数验证
            if not tool_input or len(str(tool_input).strip()) < 2:
                yield StreamEvent.error(
                    error_message=f"工具 {tool_name} 参数不完整或为空",
                    error_type="InvalidToolInput"
                )
                continue
            
            tool = self.simple_agent.registry.get(tool_name)
            if tool:
                tools_and_inputs.append((tool, {"query": tool_input}))
                yield StreamEvent.tool_start(
                    tool_name=tool_name,
                    tool_input=tool_input
                )
            else:
                yield StreamEvent.error(
                    error_message=f"工具 {tool_name} 不存在",
                    error_type="ToolNotFound"
                )
        
        # 如果没有有效的工具调用
        if not tools_and_inputs:
            yield StreamEvent.end(
                result="没有可执行的工具",
                mode="simple"
            )
            return
        
        # 5. 执行工具（并发或串行）
        import asyncio
        from ..tools.tool_executor import ToolExecutor
        
        if decision.get("parallel", False) and len(tools_and_inputs) > 1:
            # 并发执行
            results = asyncio.run(ToolExecutor.execute_parallel(tools_and_inputs))
        else:
            # 串行执行
            results = asyncio.run(ToolExecutor.execute_sequential(tools_and_inputs))
        
        # 6. 发送工具结束事件
        observations = []
        for result in results:
            yield StreamEvent.tool_end(
                tool_name=result["tool"],
                tool_output=result["result"] if not result["error"] else f"错误: {result['error']}"
            )
            
            if result["error"]:
                observations.append(f"[{result['tool']}] 错误: {result['error']}")
            else:
                observations.append(f"[{result['tool']}] {result['result']}")
        
        observation_text = "\n\n".join(observations)
        
        # 7. 生成最终答案（流式）
        final_prompt = f"""
用户问题: {task}

工具调用结果:
{observation_text}

请基于以上信息给出完整、准确的回答。
"""
        
        yield StreamEvent.llm_start(prompt=final_prompt)
        
        full_content = ""
        for chunk in self.llm.stream(final_prompt):
            if chunk.content:
                full_content += chunk.content
                yield StreamEvent.llm_token(token=chunk.content)
        
        yield StreamEvent.llm_end(content=full_content)
        yield StreamEvent.end(result=full_content, mode="simple")
    
    def _stream_rag(self, task: str, **kwargs) -> Generator[StreamEvent, None, None]:
        """
        RAG 模式流式执行（事件化）
        
        Args:
            task: 用户任务
            **kwargs: 额外参数
            
        Yields:
            StreamEvent 事件
        """
        if not self.rag_agent:
            yield StreamEvent.error(
                error_message="RAGAgent 未初始化，请提供 vectorstore",
                error_type="InitializationError"
            )
            return
        
        # 1. 检索文档（作为工具调用）
        yield StreamEvent.tool_start(
            tool_name="retriever",
            tool_input=task
        )
        
        docs = self.rag_agent.retrieve(task)
        
        doc_contents = [doc.page_content for doc in docs]
        
        yield StreamEvent.tool_end(
            tool_name="retriever",
            tool_output=f"检索到 {len(docs)} 个文档"
        )
        
        # 2. 构建上下文
        context = "\n\n".join([
            f"文档片段 {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ])
        
        # 3. 构建 prompt
        prompt = f"""
基于以下检索到的文档内容，回答用户的问题。

检索到的相关文档：
{context}

用户问题：{task}

要求：
- 基于检索到的文档内容回答
- 如果文档中没有相关信息，请明确说明
- 回答要准确、清晰、有条理
"""
        
        # 4. 流式生成答案
        yield StreamEvent.llm_start(prompt=prompt)
        
        full_content = ""
        for chunk in self.llm.stream(prompt):
            if chunk.content:
                full_content += chunk.content
                yield StreamEvent.llm_token(token=chunk.content)
        
        yield StreamEvent.llm_end(content=full_content)
        yield StreamEvent.end(result=full_content, mode="rag")
    
    def _stream_workflow(self, task: str, **kwargs) -> Generator[StreamEvent, None, None]:
        """
        Workflow 模式流式执行（事件化）
        
        Args:
            task: 用户任务
            **kwargs: 额外参数
            
        Yields:
            StreamEvent 事件
        """
        # 延迟导入
        try:
            from ..workflows.rag_writing_graph import create_rag_writing_graph
            from langgraph.checkpoint.memory import MemorySaver
        except ImportError:
            yield StreamEvent.error(
                error_message="工作流模式需要安装 langgraph: pip install langgraph",
                error_type="ImportError"
            )
            return
        
        # 创建工作流
        graph = create_rag_writing_graph(
            llm=self.llm,
            rag_agent=self.rag_agent,
            max_iterations=kwargs.get('max_iterations', 3)
        )
        
        # 编译工作流
        memory = MemorySaver()
        app = graph.compile(checkpointer=memory)
        
        # 初始化状态
        initial_state = {
            "query": task,
            "retrieved_docs": [],
            "summary": "",
            "review_feedback": "",
            "refined_summary": "",
            "approved": False,
            "iteration": 0,
            "max_iterations": kwargs.get('max_iterations', 3)
        }
        
        # 运行工作流（逐节点事件化）
        config = {"configurable": {"thread_id": "unified_agent"}}
        
        final_result = ""
        for state in app.stream(initial_state, config):
            node_name = list(state.keys())[0]
            node_state = state[node_name]
            
            # 发送节点开始事件
            yield StreamEvent.node_start(
                node_name=node_name,
                state=node_state
            )
            
            # 发送节点结束事件（包含生成的内容）
            yield StreamEvent.node_end(
                node_name=node_name,
                state=node_state
            )
            
            # 如果有新生成的内容，作为 token 输出
            if node_name == "summarizer" and node_state.get('summary'):
                final_result = node_state['summary']
                yield StreamEvent.llm_token(token=f"\n[生成综述]\n{node_state['summary']}\n")
            elif node_name == "reviewer" and node_state.get('review_feedback'):
                yield StreamEvent.llm_token(token=f"\n[审核反馈]\n{node_state['review_feedback']}\n")
            elif node_name == "refiner" and node_state.get('summary'):
                final_result = node_state['summary']
                yield StreamEvent.llm_token(token=f"\n[优化综述]\n{node_state['summary']}\n")
        
        # 发送结束事件
        yield StreamEvent.end(
            result=final_result or "工作流执行失败",
            mode="workflow"
        )
    
    def add_tool(self, tool):
        """
        添加新工具
        
        Args:
            tool: 工具实例（继承自 BaseTool）
        """
        self.tool_registry.register(tool)
    
    def list_tools(self):
        """列出所有可用工具"""
        return self.tool_registry.list_tools()
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "tools_count": len(self.tool_registry.list_tools()),
            "has_rag": self.rag_agent is not None,
            "has_workflow": self.workflow_agent is not None,
            "llm_model": Config.DEEPSEEK_MODEL
        }

    def research_and_write(self, task: str):
        """研究 + 写作模式（快捷方法）"""
        from .collaboration_patterns import RESEARCH_WRITE
        return self.collaborate(task, RESEARCH_WRITE)
    
    def deep_analysis(self, task: str):
        """深度分析模式（快捷方法）"""
        from .collaboration_patterns import RETRIEVE_ANALYZE_SUMMARIZE
        return self.collaborate(task, RETRIEVE_ANALYZE_SUMMARIZE)
