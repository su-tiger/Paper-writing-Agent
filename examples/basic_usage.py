"""
基本使用示例
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
from src.rag import load_pdf, split_documents, build_faiss_index, save_index, load_index
from src.tools import FAISSRetrieverTool, ToolRegistry
from src.agents import SimpleAgent
from src.config import Config


def example_build_index():
    """示例：构建向量索引"""
    print("=" * 80)
    print("示例 1: 构建向量索引")
    print("=" * 80)
    
    # 加载 PDF
    pdf_path = os.path.join(Config.PDF_DIR, "CLIP.pdf")
    print(f"\n1. 加载 PDF: {pdf_path}")
    docs = load_pdf(pdf_path)
    print(f"   ✓ 共 {len(docs)} 页")
    
    # 切分文档
    print("\n2. 切分文档")
    chunks = split_documents(docs)
    print(f"   ✓ 共 {len(chunks)} 个文档块")
    
    # 构建索引
    print("\n3. 构建 FAISS 索引")
    vectorstore = build_faiss_index(chunks)
    print("   ✓ 索引构建完成")
    
    # 保存索引
    print("\n4. 保存索引")
    save_index(vectorstore)
    print(f"   ✓ 已保存到: {Config.INDEX_DIR}")


def example_rag_qa():
    """示例：RAG 问答"""
    print("\n" + "=" * 80)
    print("示例 2: RAG 问答")
    print("=" * 80)
    
    # 初始化 LLM
    print("\n1. 初始化 LLM")
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    print("   ✓ LLM 初始化完成")
    
    # 加载索引
    print("\n2. 加载向量索引")
    vectorstore = load_index()
    print("   ✓ 索引加载完成")
    
    # 创建工具和 Agent
    print("\n3. 创建 Agent")
    retriever_tool = FAISSRetrieverTool(vectorstore)
    registry = ToolRegistry()
    registry.register(retriever_tool)
    agent = SimpleAgent(llm, registry)
    print("   ✓ Agent 创建完成")
    
    # 执行查询
    print("\n4. 执行查询")
    query = "What is CLIP?"
    print(f"   问题: {query}")
    result = agent.run(query)
    print(f"\n   回答: {result}")


def example_direct_retrieval():
    """示例：直接检索（不使用 Agent）"""
    print("\n" + "=" * 80)
    print("示例 3: 直接检索")
    print("=" * 80)
    
    # 加载索引
    print("\n1. 加载向量索引")
    vectorstore = load_index()
    print("   ✓ 索引加载完成")
    
    # 执行检索
    query = "What is the core idea of CLIP?"
    print(f"\n2. 查询: {query}")
    
    # 相似度检索
    print("\n   方法 1: 相似度检索")
    results = vectorstore.similarity_search(query, k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n   结果 {i}:")
        print(f"   {doc.page_content[:200]}...")
    
    # MMR 检索
    print("\n   方法 2: MMR 检索（多样性）")
    results = vectorstore.max_marginal_relevance_search(query, k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n   结果 {i}:")
        print(f"   {doc.page_content[:200]}...")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LangChain Tutorial - 基本使用示例")
    print("=" * 80)
    
    # 检查是否存在索引
    if not os.path.exists(Config.INDEX_DIR):
        print("\n未找到向量索引，开始构建...")
        example_build_index()
    else:
        print(f"\n✓ 找到现有索引: {Config.INDEX_DIR}")
    
    # 运行示例
    example_direct_retrieval()
    example_rag_qa()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)
