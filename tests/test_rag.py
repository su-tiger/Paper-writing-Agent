"""
RAG 模块测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag import create_embeddings, split_documents
from langchain.schema import Document


def test_create_embeddings():
    """测试嵌入模型创建"""
    embeddings = create_embeddings()
    assert embeddings is not None
    
    # 测试嵌入生成
    text = "This is a test sentence."
    embedding = embeddings.embed_query(text)
    assert len(embedding) > 0
    print(f"✓ 嵌入维度: {len(embedding)}")


def test_split_documents():
    """测试文档切分"""
    # 创建测试文档
    test_doc = Document(
        page_content="This is a test document. " * 100,
        metadata={"source": "test"}
    )
    
    chunks = split_documents([test_doc], chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    print(f"✓ 切分后块数: {len(chunks)}")


if __name__ == "__main__":
    print("运行 RAG 模块测试...\n")
    
    print("测试 1: 嵌入模型创建")
    test_create_embeddings()
    
    print("\n测试 2: 文档切分")
    test_split_documents()
    
    print("\n所有测试通过！")
