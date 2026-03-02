"""
向量存储：构建和管理 FAISS 向量索引
"""

from langchain_community.vectorstores import FAISS
from .embedding import create_embeddings
from ..config import Config


def build_faiss_index(chunks, embeddings=None):
    """
    构建 FAISS 向量索引
    
    Args:
        chunks: 文档块列表（已切分的文档）
        embeddings: 嵌入模型实例（可选）
        
    Returns:
        FAISS 向量存储实例
    """
    if embeddings is None:
        embeddings = create_embeddings()
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def save_index(vectorstore, path=None):
    """
    保存 FAISS 索引到本地
    
    Args:
        vectorstore: FAISS 向量存储实例
        path: 保存路径（默认使用配置）
    """
    path = path or Config.INDEX_DIR
    vectorstore.save_local(path)


def load_index(path=None, embeddings=None):
    """
    从本地加载已保存的 FAISS 索引
    
    Args:
        path: 索引文件保存路径（默认使用配置）
        embeddings: 嵌入模型实例（可选）
        
    Returns:
        FAISS 向量存储实例
    """
    path = path or Config.INDEX_DIR
    
    if embeddings is None:
        embeddings = create_embeddings()
    
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )
