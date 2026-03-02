"""
测试统一事件流系统
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import UnifiedAgent, StreamEvent
from src.rag import load_index, create_embeddings
from langchain_openai import ChatOpenAI
from src.config import Config


def test_event_stream():
    """测试事件流"""
    print("="*70)
    print("🚀 测试统一事件流系统")
    print("="*70)
    print()
    
    # 初始化
    print("初始化...")
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    try:
        embeddings = create_embeddings()
        vectorstore = load_index()
        print("✓ 向量索引加载成功")
    except:
        vectorstore = None
        print("⚠ 向量索引未加载")
    
    agent = UnifiedAgent(llm, vectorstore, enable_logging=False)
    print("✓ Agent 创建成功")
    print()
    
    # 测试 1: 查看所有事件
    print("="*70)
    print("测试 1: RAG 模式 - 查看所有事件")
    print("="*70)
    task = "什么是深度学习？"
    print(f"任务: {task}\n")
    
    for event in agent.stream(task, mode="rag"):
        print(f"[{event.type}]", end=" ")
        
        if event.type == "route":
            print(f"路由到 {event.data['selected_mode']} 模式")
        elif event.type == "start":
            print(f"开始执行")
        elif event.type == "tool_start":
            print(f"调用工具: {event.data['tool_name']}")
        elif event.type == "tool_end":
            print(f"工具完成: {event.data['tool_output']}")
        elif event.type == "llm_start":
            print(f"LLM 开始生成\n回答: ", end="", flush=True)
        elif event.type == "llm_token":
            # 不显示标签，直接输出 token
            print(event.data['token'], end="", flush=True)
        elif event.type == "llm_end":
            print(f"\n[llm_end] LLM 生成完成")
        elif event.type == "end":
            print(f"[end] 执行结束")
        elif event.type == "error":
            print(f"错误: {event.data['error_message']}")
    
    print("\n")
    
    # 测试 2: 只显示 token
    print("="*70)
    print("测试 2: 只显示 LLM token（类似 ChatGPT）")
    print("="*70)
    task = "什么是机器学习？"
    print(f"任务: {task}\n")
    print("回答: ", end="", flush=True)
    
    for event in agent.stream(task, mode="rag"):
        if event.type == "llm_token":
            print(event.data['token'], end="", flush=True)
    
    print("\n")
    
    # 测试 3: 使用 run() 方法（非流式）
    print("="*70)
    print("测试 3: 使用 run() 方法（本质是 list(stream())[-1]）")
    print("="*70)
    task = "什么是神经网络？"
    print(f"任务: {task}\n")
    
    result = agent.run(task, mode="rag")
    print(f"结果: {result}")
    print()
    
    # 测试 4: Simple 模式事件
    print("="*70)
    print("测试 4: Simple 模式 - 查看工具调用事件")
    print("="*70)
    task = "你好"
    print(f"任务: {task}\n")
    
    for event in agent.stream(task, mode="simple"):
        if event.type in ["route", "start", "tool_start", "tool_end", "end"]:
            print(f"[{event.type}] {event.data}")
        elif event.type == "llm_token":
            print(event.data['token'], end="", flush=True)
    
    print("\n")


if __name__ == "__main__":
    test_event_stream()
