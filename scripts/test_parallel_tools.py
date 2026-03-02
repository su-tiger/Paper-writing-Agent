"""
测试并发工具调用功能

演示：
1. 单工具调用（串行）
2. 多工具并发调用
3. 性能对比
"""

import sys
import os
import time
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.unified_agent import UnifiedAgent
from src.rag import load_index
from src.tools.base_tool import BaseTool
from src.tools.tool_executor import ToolExecutor


# 创建模拟工具（带延迟，方便观察并发效果）
class SlowSearchTool(BaseTool):
    """模拟慢速搜索工具"""
    name = "slow_search"
    description = "搜索信息（模拟网络延迟）"
    
    def run(self, query: str):
        time.sleep(2)  # 模拟 2 秒延迟
        return f"搜索结果: {query} 的相关信息"


class SlowCalculatorTool(BaseTool):
    """模拟慢速计算工具"""
    name = "slow_calculator"
    description = "执行计算（模拟复杂计算）"
    
    def run(self, expression: str):
        time.sleep(2)  # 模拟 2 秒延迟
        try:
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        except:
            return f"计算错误: {expression}"


def test_sequential_vs_parallel():
    """测试串行 vs 并行执行"""
    print("=" * 60)
    print("测试 1: 串行 vs 并行执行对比")
    print("=" * 60)
    
    # 创建工具
    search_tool = SlowSearchTool()
    calc_tool = SlowCalculatorTool()
    
    tools_and_inputs = [
        (search_tool, {"query": "深度学习"}),
        (calc_tool, {"expression": "100 + 200"}),
    ]
    
    # 测试串行执行
    print("\n[串行执行]")
    start = time.time()
    results = asyncio.run(ToolExecutor.execute_sequential(tools_and_inputs))
    elapsed = time.time() - start
    
    print(f"耗时: {elapsed:.2f} 秒")
    for result in results:
        print(f"  - {result['tool']}: {result['result']}")
    
    # 测试并行执行
    print("\n[并行执行]")
    start = time.time()
    results = asyncio.run(ToolExecutor.execute_parallel(tools_and_inputs))
    elapsed = time.time() - start
    
    print(f"耗时: {elapsed:.2f} 秒")
    for result in results:
        print(f"  - {result['tool']}: {result['result']}")
    
    print("\n✅ 并行执行应该快约 2 倍（2 秒 vs 4 秒）")


def test_with_unified_agent():
    """测试 UnifiedAgent 的并发功能"""
    print("\n" + "=" * 60)
    print("测试 2: UnifiedAgent 并发工具调用")
    print("=" * 60)
    
    # 初始化 Agent
    vectorstore = load_index()
    agent = UnifiedAgent(vectorstore=vectorstore)
    
    # 添加测试工具
    agent.add_tool(SlowSearchTool())
    agent.add_tool(SlowCalculatorTool())
    
    # 测试查询（需要调用多个工具）
    query = "搜索深度学习的信息，并计算 50 + 50"
    
    print(f"\n查询: {query}")
    print("\n[执行中...]")
    
    start = time.time()
    
    # 使用流式输出
    for event in agent.stream(query, mode="simple"):
        if event.type == "tool_start":
            print(f"  🔧 调用工具: {event.data['tool_name']}")
        elif event.type == "tool_end":
            print(f"  ✅ 工具完成: {event.data['tool_name']}")
        elif event.type == "end":
            elapsed = time.time() - start
            print(f"\n耗时: {elapsed:.2f} 秒")
            print(f"\n最终答案:\n{event.data['result']}")
    
    print("\n💡 提示: 如果 LLM 决策使用并发，两个工具应该同时执行（约 2 秒）")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 3: 并发执行中的错误处理")
    print("=" * 60)
    
    class ErrorTool(BaseTool):
        name = "error_tool"
        description = "会出错的工具"
        
        def run(self, **kwargs):
            raise ValueError("模拟工具错误")
    
    search_tool = SlowSearchTool()
    error_tool = ErrorTool()
    
    tools_and_inputs = [
        (search_tool, {"query": "测试"}),
        (error_tool, {}),
    ]
    
    print("\n[并行执行（包含错误）]")
    results = asyncio.run(ToolExecutor.execute_parallel(tools_and_inputs))
    
    for result in results:
        if result["error"]:
            print(f"  ❌ {result['tool']}: {result['error']}")
        else:
            print(f"  ✅ {result['tool']}: {result['result']}")
    
    print("\n✅ 一个工具出错不影响其他工具执行")


if __name__ == "__main__":
    print("\n🚀 并发工具调用测试\n")
    
    # 运行测试
    test_sequential_vs_parallel()
    test_with_unified_agent()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
