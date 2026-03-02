from abc import ABC, abstractmethod
from typing import Any
import asyncio


class BaseTool(ABC):
    """工具抽象基类"""
    
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """同步执行（保持向后兼容）"""
        pass
    
    async def arun(self, **kwargs) -> Any:
        """
        异步执行（新增）
        
        默认实现：在线程池中运行同步方法
        子类可以重写以提供真正的异步实现
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.run(**kwargs))
