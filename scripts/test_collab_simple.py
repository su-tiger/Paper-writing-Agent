# -*- coding: utf-8 -*-
"""
测试多 Agent 协作功能（简化版）
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import UnifiedAgent
from src.rag import load_index, create_embeddings
from langchain_openai import ChatOpenAI
from src.config import Config


def main():
    print("="*70)
    print("测试多 Agent 协作")
    print("="*70)
    
    # 初始化
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    try:
        vectorstore = load_index()
        print("[OK] 向量索引加载成功")
    except:
        vectorstore = None
        print("[WARN] 向量索引未加载")
    
    agent = UnifiedAgent(llm, vectorstore, enable_logging=False)
    print("[OK] Agent 创建成功\n")
    
    # 测试：RAG + Simple 协作
    print("测试: RAG -> Simple 协作")
    print("-"*70)
    
    for event in agent.collaborate(
        "什么是深度学习？",
        agents=[
            ("rag", {}),
            ("simple", {})
        ]
    ):
        if event.type == "node_start":
            print(f"[{event.data['node_name']}] 开始...")
        elif event.type == "node_end":
            print(f"[{event.data['node_name']}] 完成")
        elif event.type == "llm_token":
            print(event.data['token'], end="", flush=True)
        elif event.type == "end":
            print(f"\n\n最终结果长度: {len(event.data['result'])} 字符")
    
    print("\n" + "="*70)
    print("测试完成!")


if __name__ == "__main__":
    main()
