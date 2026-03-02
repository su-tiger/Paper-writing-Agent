"""
Agent 基类：定义所有 Agent 的通用接口
"""

from abc import ABC, abstractmethod



# 新代码
class BaseAgent(ABC):
    @abstractmethod
    def run(self, query: str, context: dict = None):
        """
        执行 Agent
        
        Args:
            query: 查询
            context: 共享上下文（用于多 Agent 协作）
        """
        pass

