"""
嵌入模型：使用 HuggingFace 的 BGE 模型生成文本嵌入
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from ..config import Config


def create_embeddings(model_name=None, device=None):
    """
    创建文本嵌入模型实例
    
    Args:
        model_name: 模型名称（默认使用配置）
        device: 运行设备 cpu 或 cuda（默认使用配置）
        
    Returns:
        HuggingFaceEmbeddings 实例，用于将文本转换为向量
    """
    model_name = model_name or Config.EMBEDDING_MODEL
    device = device or Config.EMBEDDING_DEVICE
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True}
    )
