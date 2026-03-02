"""
Agent 模块测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import BaseTool, ToolRegistry


class MockTool(BaseTool):
    """模拟工具用于测试"""
    
    def __init__(self):
        self.name = "mock_tool"
        self.description = "这是一个模拟工具"
    
    def run(self, **kwargs):
        return "Mock result"


def test_tool_registry():
    """测试工具注册表"""
    registry = ToolRegistry()
    
    # 注册工具
    tool = MockTool()
    registry.register(tool)
    
    # 获取工具
    retrieved_tool = registry.get("mock_tool")
    assert retrieved_tool is not None
    assert retrieved_tool.name == "mock_tool"
    
    # 列出工具
    tools = registry.list_tools()
    assert len(tools) == 1
    
    print("✓ 工具注册表测试通过")


if __name__ == "__main__":
    print("运行 Agent 模块测试...\n")
    
    print("测试 1: 工具注册表")
    test_tool_registry()
    
    print("\n所有测试通过！")
