import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.unified_agent import UnifiedAgent
from src.rag import load_index

def test_stream_decision():
    """测试流式决策"""
    print("=" * 60)
    print("测试流式决策")
    print("=" * 60)
    
    vectorstore = load_index()
    agent = UnifiedAgent(vectorstore=vectorstore)
    
    query = "什么是深度学习？"
    
    print(f"\n查询: {query}\n")
    print("[Agent 思考过程]")
    
    for event in agent.stream(query, mode="simple"):
        if event.type == "llm_start":
            print(f"\n🤔 开始思考...")
        elif event.type == "llm_token":
            # 实时输出决策过程
            print(event.data["token"], end="", flush=True)
        elif event.type == "llm_end":
            print("\n✅ 决策完成")
        elif event.type == "tool_start":
            print(f"\n🔧 调用工具: {event.data['tool_name']}")
        elif event.type == "tool_end":
            print(f"✅ 工具完成")
        elif event.type == "end":
            print(f"\n最终答案:\n{event.data['result']}")

if __name__ == "__main__":
    test_stream_decision()
