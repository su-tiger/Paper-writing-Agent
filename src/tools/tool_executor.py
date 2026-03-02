"""
并发工具执行器

支持：
1. 并发执行多个工具
2. 收集所有结果
3. 错误处理
"""

import asyncio
from typing import List, Dict, Any, Tuple


class ToolExecutor:
    """工具并发执行器"""
    
    @staticmethod
    async def execute_parallel(
        tools_and_inputs: List[Tuple[Any, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        并发执行多个工具
        
        Args:
            tools_and_inputs: [(tool, input_kwargs), ...]
            
        Returns:
            [
                {"tool": tool_name, "result": ..., "error": None},
                {"tool": tool_name, "result": None, "error": "..."},
                ...
            ]
        
        Example:
            results = await ToolExecutor.execute_parallel([
                (retriever_tool, {"query": "深度学习"}),
                (calculator_tool, {"expression": "1+1"}),
            ])
        """
        tasks = []
        tool_names = []
        
        for tool, input_kwargs in tools_and_inputs:
            tasks.append(tool.arun(**input_kwargs))
            tool_names.append(tool.name)
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 格式化结果
        formatted_results = []
        for tool_name, result in zip(tool_names, results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "tool": tool_name,
                    "result": None,
                    "error": str(result)
                })
            else:
                formatted_results.append({
                    "tool": tool_name,
                    "result": result,
                    "error": None
                })
        
        return formatted_results
    
    @staticmethod
    async def execute_sequential(
        tools_and_inputs: List[Tuple[Any, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        串行执行多个工具（用于对比）
        
        Args:
            tools_and_inputs: [(tool, input_kwargs), ...]
            
        Returns:
            同 execute_parallel
        """
        results = []
        
        for tool, input_kwargs in tools_and_inputs:
            try:
                result = await tool.arun(**input_kwargs)
                results.append({
                    "tool": tool.name,
                    "result": result,
                    "error": None
                })
            except Exception as e:
                results.append({
                    "tool": tool.name,
                    "result": None,
                    "error": str(e)
                })
        
        return results
