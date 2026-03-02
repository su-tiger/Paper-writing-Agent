"""
文档切分器：将长文档切分成小块以便向量化和检索
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import Config


def split_documents(documents, chunk_size=None, chunk_overlap=None):
    """
    将文档切分成小块（chunks）
    
    Args:
        documents: 文档列表
        chunk_size: 每个块的最大字符数（默认使用配置）
        chunk_overlap: 相邻块之间的重叠字符数（默认使用配置）
        
    Returns:
        切分后的文档块列表
    """
    chunk_size = chunk_size or Config.CHUNK_SIZE
    chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)
    return chunks
