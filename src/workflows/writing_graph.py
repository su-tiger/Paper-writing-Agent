"""
LangGraph 多 Agent 写作工作流

功能：
1. Planner 生成文章大纲
2. 多个 Writer 并行写作（不同风格）
3. Reviewer 审核并决定是否需要修改
4. 支持断点恢复和人工介入

注意：这是基础的写作工作流（不带 RAG）
如果需要"检索论文 + 写综述"功能，请使用：
    src/workflows/rag_writing_graph.py
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Annotated
from operator import add
import json
import re
from pydantic import BaseModel, ValidationError
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

from ..config import Config


# =============================
# 数据模型定义
# =============================

class ReviewResult(BaseModel):
    """审核结果模型"""
    approved: bool  # 是否通过审核
    revision_type: str  # 修改类型："draft"（修改正文）| "outline"（修改大纲）| "none"（无需修改）
    feedback: str  # 审核反馈意见


class WritingState(TypedDict):
    """写作工作流的状态定义"""
    topic: str  # 写作主题
    outline: str  # 文章大纲
    draft: Annotated[list[str], add]  # 文章草稿列表（支持多个 Writer 并行写作）
    feedback: str  # 审核反馈
    approved: bool  # 是否通过审核
    revision_type: Optional[str]  # 修改类型
    iteration: int  # 当前迭代次数
    max_iterations: int  # 最大迭代次数


def create_writing_graph(llm=None, max_iterations=None):
    """
    创建写作工作流图
    
    Args:
        llm: 大语言模型实例（可选，默认使用配置创建）
        max_iterations: 最大迭代次数（可选，默认使用配置）
        
    Returns:
        编译后的工作流图
    """
    # 初始化 LLM
    if llm is None:
        llm = ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
    
    max_iterations = max_iterations or Config.MAX_ITERATIONS
    
    # =============================
    # 节点函数定义
    # =============================
    
    def planner(state: WritingState):
        """规划节点：根据主题生成文章大纲"""
        print(f"[Planner] iteration={state['iteration']}")

        prompt = f"""
请为以下主题生成一个清晰、结构合理的文章大纲：

主题：{state['topic']}
"""
        response = llm.invoke(prompt)

        return {
            "outline": response.content,
            "feedback": "",
        }

    def writerA(state: WritingState):
        """写作节点 A：学术风格写作"""
        print(f"[WriterA] iteration={state['iteration']}")

        feedback_text = state.get("feedback", "")

        prompt = f"""
根据以下大纲写一篇完整文章(偏学术风格)：

大纲：
{state['outline']}

如有修改意见，请根据以下意见优化：
{feedback_text}

要求：
- 逻辑清晰
- 结构合理
- 内容充实
"""
        response = llm.invoke(prompt)

        return {
            "draft": [response.content]
        }

    def writerB(state: WritingState):
        """写作节点 B：批判性分析风格写作"""
        print(f"[WriterB] iteration={state['iteration']}")

        feedback_text = state.get("feedback", "")

        prompt = f"""
根据以下大纲写一篇完整文章(偏批判性分析)：

大纲：
{state['outline']}

如有修改意见，请根据以下意见优化：
{feedback_text}

要求：
- 逻辑清晰
- 结构合理
- 内容充实
"""
        response = llm.invoke(prompt)

        return {
            "draft": [response.content]
        }

    def reviewer(state: WritingState):
        """审核节点：评审文章质量并决定下一步操作"""
        print(f"[Reviewer] iteration={state['iteration']}")

        # 合并草稿
        draft_text = "\n\n".join(state["draft"])
        
        prompt = f"""
请评审下面的文章，并严格按照以下JSON格式返回评审结果：
{{
    "approved": true/false,
    "revision_type": "draft" | "outline" | "none",
    "feedback": "具体的评审意见"
}}

评审标准：
- 如果结构有问题 → revision_type="outline"
- 如果表达或论证问题 → revision_type="draft"
- 如果已经很好 → approved=true 且 revision_type="none"

文章：
{draft_text}
"""
        response = llm.invoke(prompt)
        response_text = response.content.strip()

        # 解析 JSON 响应
        try:
            result_dict = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result_dict = json.loads(json_match.group())
            else:
                result_dict = {
                    "approved": False,
                    "revision_type": "draft",
                    "feedback": "评审结果解析失败，默认需要修改正文"
                }

        # 验证并转换为 ReviewResult 对象
        try:
            result: ReviewResult = ReviewResult(**result_dict)
        except ValidationError as e:
            print(f"[Reviewer] 评审结果验证失败: {e}")
            result = ReviewResult(
                approved=False,
                revision_type="draft",
                feedback=f"评审结果格式错误: {e}"
            )
        
        new_iteration = state["iteration"] + 1

        # 判断是否达到最大迭代次数
        if new_iteration >= state["max_iterations"]:
            return Command(
                update={
                    "approved": result.approved,
                    "revision_type": result.revision_type,
                    "feedback": result.feedback,
                    "iteration": new_iteration
                },
                goto=END
            )

        # 如果审核通过，结束工作流
        if result.approved:
            return Command(
                update={
                    "approved": True,
                    "iteration": new_iteration
                },
                goto=END
            )

        # 如果需要修改大纲，跳转到 planner 节点
        if result.revision_type == "outline":
            return Command(
                update={
                    "feedback": result.feedback,
                    "iteration": new_iteration
                },
                goto="planner"
            )

        # 如果需要修改正文，跳转到 dispatch_draft 节点
        return Command(
            update={
                "approved": result.approved,
                "revision_type": result.revision_type,
                "feedback": result.feedback,
                "iteration": new_iteration
            },
            goto="dispatch_draft"
        )

    def dispatch_draft(state: WritingState):
        """分发节点：用于将流程分发到多个 Writer 节点"""
        return {}

    # =============================
    # 构建工作流图
    # =============================
    
    graph = StateGraph(WritingState)

    # 添加节点
    graph.add_node("planner", planner)
    graph.add_node("writerA", writerA)
    graph.add_node("writerB", writerB)
    graph.add_node("reviewer", reviewer)
    graph.add_node("dispatch_draft", dispatch_draft)

    # 设置入口点
    graph.set_entry_point("planner")

    # 添加边
    graph.add_edge("planner", "dispatch_draft")
    graph.add_edge("dispatch_draft", "writerA")
    graph.add_edge("dispatch_draft", "writerB")
    graph.add_edge(["writerA", "writerB"], "reviewer")

    return graph
