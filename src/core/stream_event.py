"""
统一流式事件系统

所有模式（Simple、RAG、Workflow）都通过 StreamEvent 输出事件
"""

from typing import Any, Dict, Literal
from dataclasses import dataclass


EventType = Literal[
    "start",           # 开始执行
    "route",           # 路由决策
    "tool_start",      # 工具调用开始
    "tool_end",        # 工具调用结束
    "llm_start",       # LLM 调用开始
    "llm_token",       # LLM token 输出
    "llm_end",         # LLM 调用结束
    "node_start",      # 工作流节点开始
    "node_end",        # 工作流节点结束
    "error",           # 错误
    "end",             # 执行结束
    "collaborate_start",   # 协作开始
    "collaborate_end",     # 协作结束
    "agent_handoff" ,       # Agent 交接
    "parallel_start",      # 并发开始
    "parallel_end",        # 并发结束
    "tool_parallel"     # 工具并发执行
]


@dataclass
class StreamEvent:
    """
    统一流式事件
    
    所有模式的输出都通过这个事件类型
    
    Attributes:
        type: 事件类型
        data: 事件数据
    """
    type: EventType
    data: Dict[str, Any]
    
    def __repr__(self):
        return f"StreamEvent(type='{self.type}', data={self.data})"
    
    @classmethod
    def start(cls, mode: str, task: str):
        """开始执行事件"""
        return cls(
            type="start",
            data={"mode": mode, "task": task}
        )
    
    @classmethod
    def route(cls, task: str, selected_mode: str, reason: str):
        """路由决策事件"""
        return cls(
            type="route",
            data={
                "task": task,
                "selected_mode": selected_mode,
                "reason": reason
            }
        )
    
    @classmethod
    def tool_start(cls, tool_name: str, tool_input: Any):
        """工具调用开始事件"""
        return cls(
            type="tool_start",
            data={
                "tool_name": tool_name,
                "tool_input": tool_input
            }
        )
    
    @classmethod
    def tool_end(cls, tool_name: str, tool_output: Any):
        """工具调用结束事件"""
        return cls(
            type="tool_end",
            data={
                "tool_name": tool_name,
                "tool_output": tool_output
            }
        )
    
    @classmethod
    def llm_start(cls, prompt: str):
        """LLM 调用开始事件"""
        return cls(
            type="llm_start",
            data={"prompt": prompt}
        )
    
    @classmethod
    def llm_token(cls, token: str):
        """LLM token 输出事件"""
        return cls(
            type="llm_token",
            data={"token": token}
        )
    
    @classmethod
    def llm_end(cls, content: str):
        """LLM 调用结束事件"""
        return cls(
            type="llm_end",
            data={"content": content}
        )
    
    @classmethod
    def node_start(cls, node_name: str, state: Dict[str, Any]):
        """工作流节点开始事件"""
        return cls(
            type="node_start",
            data={
                "node_name": node_name,
                "state": state
            }
        )
    
    @classmethod
    def node_end(cls, node_name: str, state: Dict[str, Any]):
        """工作流节点结束事件"""
        return cls(
            type="node_end",
            data={
                "node_name": node_name,
                "state": state
            }
        )
    
    @classmethod
    def error(cls, error_message: str, error_type: str = "unknown"):
        """错误事件"""
        return cls(
            type="error",
            data={
                "error_message": error_message,
                "error_type": error_type
            }
        )
    
    @classmethod
    def end(cls, result: Any, mode: str):
        """执行结束事件"""
        return cls(
            type="end",
            data={
                "result": result,
                "mode": mode
            }
        )
    @classmethod
    def agent_handoff(cls, from_agent: str, to_agent: str, context: dict):
        """Agent 交接事件"""
        return cls(
            type="agent_handoff",
            data={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context_keys": list(context.keys())
            }
        )
    @classmethod
    def parallel_start(cls, tool_count: int):
        """并发开始事件"""
        return cls(
            type="parallel_start",
            data={"tool_count": tool_count}
        )

    @classmethod
    def parallel_end(cls, results: list):
        """并发结束事件"""
        return cls(
            type="parallel_end",
            data={"results": results}
        )
