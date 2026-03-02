"""
智能路由器：根据任务类型自动选择最佳执行模式

支持的模式：
- simple: ReAct 模式（适合简单问答）
- rag: RAG 模式（适合知识库问答）
- workflow: 工作流模式（适合复杂任务）
- auto: 自动选择（默认）
"""

from typing import Literal
from langchain_openai import ChatOpenAI
import json
import re


TaskMode = Literal["simple", "rag", "workflow", "auto"]


class TaskRouter:
    """任务路由器：智能判断任务类型并选择最佳执行模式"""
    
    def __init__(self, llm=None):
        """
        初始化路由器
        
        Args:
            llm: 大语言模型实例（用于智能判断）
        """
        self.llm = llm
    
    def route(self, task: str, mode: TaskMode = "auto") -> TaskMode:
        """
        路由任务到最佳执行模式
        
        Args:
            task: 用户任务描述
            mode: 指定模式（如果是 auto 则自动判断）
            
        Returns:
            最佳执行模式
        """
        # 如果用户指定了模式，直接返回
        if mode != "auto":
            return mode
        
        # 自动判断模式
        return self._auto_route(task)
    
    def _auto_route(self, task: str) -> TaskMode:
        """
        自动判断任务类型
        
        Args:
            task: 用户任务描述
            
        Returns:
            推荐的执行模式
        """
        # 规则 1: 关键词匹配（快速判断）
        task_lower = task.lower()
        
        # 工作流模式的关键词
        workflow_keywords = [
            "写", "生成", "创作", "综述", "报告", "文章",
            "write", "generate", "create", "review", "report"
        ]
        
        # RAG 模式的关键词
        rag_keywords = [
            "什么是", "介绍", "解释", "原理", "如何",
            "what", "explain", "how", "principle"
        ]
        
        # 检查工作流关键词
        if any(keyword in task_lower for keyword in workflow_keywords):
            return "workflow"
        
        # 检查 RAG 关键词
        if any(keyword in task_lower for keyword in rag_keywords):
            return "rag"
        
        # 规则 2: 任务长度判断
        if len(task) > 100:
            # 长任务通常需要工作流
            return "workflow"
        
        # 规则 3: 使用 LLM 判断（如果有）
        if self.llm:
            return self._llm_route(task)
        
        # 默认使用 RAG 模式（最通用）
        return "rag"
    
    def _llm_route(self, task: str) -> TaskMode:
        """
        使用 LLM 智能判断任务类型
        
        Args:
            task: 用户任务描述
            
        Returns:
            推荐的执行模式
        """
        prompt = f"""
你是一个任务分类专家。请判断以下任务最适合哪种执行模式。

任务：{task}

可选模式：
1. simple: 简单问答，不需要检索（如"你好"、"今天天气"）
2. rag: 知识库问答，需要检索文档（如"什么是深度学习？"）
3. workflow: 复杂任务，需要多步骤协作（如"写一篇综述"、"生成报告"）

请只返回模式名称（simple/rag/workflow），不要有其他内容。
"""
        
        try:
            response = self.llm.invoke(prompt)
            mode = response.content.strip().lower()
            
            # 验证返回的模式
            if mode in ["simple", "rag", "workflow"]:
                return mode
            else:
                # 如果返回无效，使用默认
                return "rag"
        except Exception as e:
            print(f"[Router] LLM 判断失败: {e}，使用默认模式")
            return "rag"
    
    def explain_route(self, task: str, mode: TaskMode) -> str:
        """
        解释为什么选择这个模式
        
        Args:
            task: 用户任务
            mode: 选择的模式
            
        Returns:
            解释文本
        """
        explanations = {
            "simple": "这是一个简单的问答任务，使用 ReAct 模式（推理+行动）",
            "rag": "这是一个知识库问答任务，使用 RAG 模式（检索增强生成）",
            "workflow": "这是一个复杂任务，使用工作流模式（多节点协作）"
        }
        
        return explanations.get(mode, "未知模式")
