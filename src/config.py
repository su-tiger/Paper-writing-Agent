"""
配置管理模块
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """项目配置类"""
    
    # LLM 配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 嵌入模型配置
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")  # cpu 或 cuda
    
    # 文档处理配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # 检索配置
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "3"))
    RETRIEVAL_METHOD = os.getenv("RETRIEVAL_METHOD", "mmr")  # mmr 或 similarity
    
    # 路径配置
    DATA_DIR = os.getenv("DATA_DIR", "data")
    PDF_DIR = os.path.join(DATA_DIR, "pdf")
    INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")
    
    # 工作流配置
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
    
    # 评估配置
    EVALUATION_OUTPUT_DIR = os.getenv("EVALUATION_OUTPUT_DIR", "data/evaluation_reports")
    ENABLE_AUTO_EVALUATION = os.getenv("ENABLE_AUTO_EVALUATION", "false").lower() == "true"
