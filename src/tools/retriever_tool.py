"""
FAISS 检索工具：从向量数据库中检索相关文档
"""

from .base_tool import BaseTool


class FAISSRetrieverTool(BaseTool):
    """基于 FAISS 的文档检索工具"""

    def __init__(self, vectorstore):
        """
        初始化检索工具
        
        Args:
            vectorstore: FAISS 向量存储实例
        """
        self.name = "faiss_retriever"
        self.description = "从知识库中检索相关论文或文档内容"
        self.vectorstore = vectorstore

    def run(self, query: str, method: str = "mmr", k: int = 3):
        """
        执行文档检索
        
        Args:
            query: 查询文本
            method: 检索方法，"mmr"（最大边际相关性）或 "similarity"（相似度）
            k: 返回的文档数量
            
        Returns:
            检索到的文档内容（拼接后的字符串）
        """
        # MMR 检索：在相关性和多样性之间取得平衡
        if method == "mmr":
            results = self.vectorstore.max_marginal_relevance_search(query, k=k)
        # 相似度检索：返回最相似的文档
        else:
            results = self.vectorstore.similarity_search(query, k=k)

        # 将多个文档内容拼接成一个字符串
        return "\n\n".join([doc.page_content for doc in results])
