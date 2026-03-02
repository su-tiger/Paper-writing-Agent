"""
文档加载器：从 PDF 文件中提取文本内容
"""

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(path: str):
    """
    加载 PDF 文档
    
    Args:
        path: PDF 文件路径
        
    Returns:
        文档列表，每个文档对应 PDF 的一页
    """
    loader = PyPDFLoader(path)
    documents = loader.load()
    return documents
