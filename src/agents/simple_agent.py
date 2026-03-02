"""
简单 Agent 实现：基于 ReAct 模式的智能问答 Agent
流程：决策 → 工具调用 → 生成答案
"""

from .base_agent import BaseAgent
import json
import re
import asyncio
from ..tools.tool_executor import ToolExecutor

class SimpleAgent(BaseAgent):
    """简单 Agent 实现，支持工具调用和推理"""

    def __init__(self, llm, registry):
        """
        初始化 Agent
        
        Args:
            llm: 大语言模型实例
            registry: 工具注册表，包含可用的工具
        """
        self.llm = llm
        self.registry = registry
        self.last_decision = None  # 记录最后一次决策（用于 rollback）
        self.last_result = None    # 记录最后一次结果

    def decide(self, query: str):
        """
        决策阶段：让 LLM 判断是否需要使用工具
        
        Args:
            query: 用户查询
            
        Returns:
            LLM 的决策结果（JSON 格式字符串）
        """
        # 构建工具描述列表
        tool_descriptions = "\n".join(
            [f"{t.name}: {t.description}" for t in self.registry.list_tools()]
        )

        # 构建决策提示词
        prompt = f"""
你是一个智能助手。
用户问题: {query}

可用工具:
{tool_descriptions}

如果需要使用工具，请输出JSON格式:
{{
  "action": "tool_name",
  "action_input": "具体输入"
}}

如果不需要工具，请输出:
{{
  "action": "final",
  "answer": "你的回答"
}}
"""

        response = self.llm.invoke(prompt)
        return response.content
    def decide_parallel(self, query: str):
        """
        决策阶段：判断是否需要并发调用多个工具
        
        Returns:
            {
                "parallel": True/False,
                "tools": [
                    {"action": "tool1", "action_input": "..."},
                    {"action": "tool2", "action_input": "..."}
                ]
            }
        """
        tool_descriptions = "\n".join(
            [f"{t.name}: {t.description}" for t in self.registry.list_tools()]
        )

        prompt = f"""
你是一个智能助手。判断是否需要并发调用多个工具。

用户问题: {query}

可用工具:
{tool_descriptions}

如果需要并发调用多个工具，请输出JSON:
{{
  "parallel": true,
  "tools": [
    {{"action": "tool1", "action_input": "input1"}},
    {{"action": "tool2", "action_input": "input2"}}
  ]
}}

如果只需要一个工具或不需要工具，请输出JSON:
{{
  "parallel": false,
  "tools": [
    {{"action": "tool_name", "action_input": "..."}}
  ]
}}

或者不需要工具:
{{
  "parallel": false,
  "tools": [
    {{"action": "final", "answer": "你的回答"}}
  ]
}}
"""
        
        response = self.llm.invoke(prompt)
        return response.content

    async def run_async(self, query: str, context: dict = None):
        """
        异步执行（支持并发工具调用）
        
        Args:
            query: 用户查询
            context: 共享上下文
            
        Returns:
            最终答案
        """
        context = context or {}
        
        # 1. 决策
        decision_text = self.decide_parallel(query)
        
        # 2. 解析决策
        try:
            decision = json.loads(decision_text)
        except:
            json_match = re.search(r'\{[\s\S]*\}', decision_text)
            decision = json.loads(json_match.group())
        
        # 3. 检查是否需要工具
        tools_to_call = decision.get("tools", [])
        
        if not tools_to_call or tools_to_call[0].get("action") == "final":
            return tools_to_call[0].get("answer", "")
        
        # 4. 准备工具调用
        tools_and_inputs = []
        for tool_spec in tools_to_call:
            tool_name = tool_spec["action"]
            tool_input = tool_spec["action_input"]
            
            tool = self.registry.get(tool_name)
            if tool:
                tools_and_inputs.append((tool, {"query": tool_input}))
        
        # 5. 执行工具（并发或串行）
        if decision.get("parallel", False) and len(tools_and_inputs) > 1:
            # 并发执行
            results = await ToolExecutor.execute_parallel(tools_and_inputs)
        else:
            # 串行执行
            results = await ToolExecutor.execute_sequential(tools_and_inputs)
        
        # 6. 整合结果
        observations = []
        for result in results:
            if result["error"]:
                observations.append(f"[{result['tool']}] 错误: {result['error']}")
            else:
                observations.append(f"[{result['tool']}] {result['result']}")
        
        observation_text = "\n\n".join(observations)
        
        # 7. 生成最终答案
        final_prompt = f"""
用户问题: {query}

工具调用结果:
{observation_text}

请基于以上信息给出完整、准确的回答。
"""
        
        final_response = self.llm.invoke(final_prompt)
        context["simple_result"] = final_response.content
        
        return final_response.content

    def decide_stream(self, query: str):
        """
        流式决策：让用户看到 LLM 的思考过程
        
        Yields:
            决策内容的 token 流
        """
        tool_descriptions = "\n".join(
            [f"{t.name}: {t.description}" for t in self.registry.list_tools()]
        )

        prompt = f"""
你是一个智能助手。
用户问题: {query}

可用工具:
{tool_descriptions}

如果需要使用工具，请输出JSON格式:
{{
  "action": "tool_name",
  "action_input": "具体输入"
}}

如果不需要工具，请输出:
{{
  "action": "final",
  "answer": "你的回答"
}}
"""
        
        # 使用 stream() 而不是 invoke()
        for chunk in self.llm.stream(prompt):
            if chunk.content:
                yield chunk.content

    def decide_parallel_stream(self, query: str):
        """
        流式决策（并发版本）
        
        Yields:
            决策内容的 token 流
        """
        tool_descriptions = "\n".join(
            [f"{t.name}: {t.description}" for t in self.registry.list_tools()]
        )

        prompt = f"""
你是一个智能助手。判断是否需要并发调用多个工具。

重要规则：
1. 只在明确需要时使用工具（如检索知识、计算、搜索等）
2. 简单问候、闲聊、常识问题请直接回答，不要使用工具
3. 确保工具参数完整且有意义（至少3个字符）
4. 如果不确定是否需要工具，优先直接回答

用户问题: {query}

可用工具:
{tool_descriptions}

如果需要并发调用多个工具，请输出JSON:
{{
  "parallel": true,
  "tools": [
    {{"action": "tool1", "action_input": "input1"}},
    {{"action": "tool2", "action_input": "input2"}}
  ]
}}

如果只需要一个工具或不需要工具，请输出JSON:
{{
  "parallel": false,
  "tools": [
    {{"action": "tool_name", "action_input": "..."}}
  ]
}}

或者不需要工具:
{{
  "parallel": false,
  "tools": [
    {{"action": "final", "answer": "你的回答"}}
  ]
}}
"""
        
        for chunk in self.llm.stream(prompt):
            if chunk.content:
                yield chunk.content

    def run(self, query: str, context: dict = None):
        """
        同步执行（保持向后兼容）
        
        如果需要并发，会自动使用 asyncio.run()
        
        Args:
            query: 用户查询
            context: 共享上下文（用于多 Agent 协作）
            
        Returns:
            最终答案
        """
        context = context or {}
        
        # 检查是否需要并发
        decision_text = self.decide_parallel(query)
        
        try:
            decision = json.loads(decision_text)
        except:
            json_match = re.search(r'\{[\s\S]*\}', decision_text)
            if json_match:
                decision = json.loads(json_match.group())
            else:
                # JSON 解析失败，返回错误
                return "决策解析失败，请重试"
        
        # 保存决策（用于 rollback）
        self.last_decision = decision
        
        # 如果需要并发，使用异步版本
        if decision.get("parallel", False) and len(decision.get("tools", [])) > 1:
            result = asyncio.run(self.run_async(query, context))
            self.last_result = result
            return result
        
        # 否则使用原来的同步逻辑
        # 步骤1：检查 context 中是否已有检索结果
        if "retrieved_docs" in context:
            # 使用已有的检索结果
            observation = context["retrieved_docs"]
        else:
            # 步骤2：决策是否需要工具
            decision_text = self.decide(query)

            # 步骤3：解析 LLM 返回的 JSON 决策
            try:
                decision = json.loads(decision_text)
            except:
                # 如果直接解析失败，尝试提取 JSON 片段
                json_match = re.search(r'\{[\s\S]*\}', decision_text)
                decision = json.loads(json_match.group())

            # 步骤4：如果不需要工具，直接返回答案
            if decision["action"] == "final":
                answer = decision["answer"]
                context["simple_result"] = answer
                return answer

            # 步骤5：获取工具并执行
            tool_name = decision["action"]
            tool_input = decision["action_input"]

            tool = self.registry.get(tool_name)

            if tool is None:
                return f"Tool {tool_name} not found."

            # 调用工具获取检索结果
            observation = tool.run(query=tool_input)
            
            # 保存到 context
            context["retrieved_docs"] = observation

        # 步骤6：基于检索结果生成最终答案
        final_prompt = f"""
用户问题:
{query}

检索到的信息:
{observation}

请基于以上信息给出完整、准确的回答。
"""
        
        final_response = self.llm.invoke(final_prompt)
        
        # 保存结果到 context
        context["simple_result"] = final_response.content
        self.last_result = final_response.content
        
        return final_response.content
    
    def rollback(self):
        """
        回退到上一次决策
        
        Returns:
            上一次的决策和结果
        """
        return {
            "decision": self.last_decision,
            "result": self.last_result
        }
        
