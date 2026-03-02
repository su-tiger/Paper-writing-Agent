"""
测试流式输出
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.unified_agent import UnifiedAgent
from src.rag import load_index, create_embeddings
from langchain_openai import ChatOpenAI
from src.config import Config


def test_stream():
    """测试流式输出"""
    print("="*70)
    print("🚀 测试流式输出")
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
    
    # 测试 1: RAG 模式流式输出
    print("="*70)
    print("测试 1: RAG 模式流式输出")
    print("="*70)
    task = "什么是深度学习？"
    print(f"任务: {task}")
    print("\n回答: ", end="", flush=True)
    
    for chunk in agent.run(task, mode="rag", stream=True):
        print(chunk, end="", flush=True)
    
    print("\n")
    
    # 测试 2: Simple 模式流式输出
    print("="*70)
    print("测试 2: Simple 模式流式输出")
    print("="*70)
    task = "你好"
    print(f"任务: {task}")
    print("\n回答: ", end="", flush=True)
    
    for chunk in agent.run(task, mode="simple", stream=True):
        print(chunk, end="", flush=True)
    
    print("\n")
    
    # 测试 3: 普通输出（对比）
    print("="*70)
    print("测试 3: 普通输出（对比）")
    print("="*70)
    task = "什么是机器学习？"
    print(f"任务: {task}")
    
    result = agent.run(task, mode="rag", stream=False)
    print(f"\n回答: {result}")
    print()


if __name__ == "__main__":
    test_stream()
