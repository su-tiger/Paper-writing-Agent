"""
运行 RAG 问答系统脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
from src.tools import FAISSRetrieverTool, ToolRegistry
from src.agents import SimpleAgent
from src.rag import load_index
from src.config import Config


def main(query: str = None, interactive: bool = False):
    """
    运行 RAG 问答系统
    
    Args:
        query: 查询问题（如果为 None 且 interactive=False，使用默认问题）
        interactive: 是否进入交互模式
    """
    print("正在初始化 RAG 问答系统...")
    
    # 初始化 LLM
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    # 加载向量索引
    print(f"正在加载向量索引: {Config.INDEX_DIR}")
    vectorstore = load_index()
    print("✓ 索引加载完成")
    
    # 创建检索工具
    retriever_tool = FAISSRetrieverTool(vectorstore)
    
    # 创建工具注册表
    registry = ToolRegistry()
    registry.register(retriever_tool)
    
    # 创建 Agent
    agent = SimpleAgent(llm, registry)
    print("✓ Agent 初始化完成\n")
    
    # 交互模式
    if interactive:
        print("进入交互模式（输入 'quit' 或 'exit' 退出）\n")
        while True:
            user_query = input("请输入问题: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not user_query:
                continue
            
            print("\n正在思考...\n")
            result = agent.run(user_query)
            print(f"回答: {result}\n")
            print("-" * 80 + "\n")
    
    # 单次查询模式
    else:
        if query is None:
            query = "What is CLIP?"
        
        print(f"问题: {query}\n")
        print("正在思考...\n")
        result = agent.run(query)
        print(f"回答: {result}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行 RAG 问答系统")
    parser.add_argument(
        "--query",
        type=str,
        help="查询问题",
        default=None
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="进入交互模式"
    )
    
    args = parser.parse_args()
    main(args.query, args.interactive)
