"""
RAG Agent：结合检索增强生成的智能代理

核心功能：
1. 接收查询问题
2. 从向量数据库检索相关文档
3. 基于检索结果生成回答
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from ..rag import load_index
from ..config import Config
from .base_agent import BaseAgent


class RAGAgent(BaseAgent):
    """
    RAG Agent 实现
    
    工作流程：
    query → 向量检索 → 上下文构建 → LLM 生成答案
    """
    
    def __init__(self, llm=None, vectorstore=None, retrieval_k=None):
        """
        初始化 RAG Agent
        
        Args:
            llm: 大语言模型实例（可选）
            vectorstore: 向量存储实例（可选，默认加载已保存的索引）
            retrieval_k: 检索返回的文档数量（可选）
        """
        # 初始化 LLM
        self.llm = llm or ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
        
        # 初始化向量存储
        self.vectorstore = vectorstore or load_index()
        
        # 检索参数
        self.retrieval_k = retrieval_k or Config.RETRIEVAL_K
    
    def retrieve(self, query: str) -> list:
        """
        从向量数据库检索相关文档
        
        Args:
            query: 查询问题
            
        Returns:
            检索到的文档列表
        """
        print(f"[RAGAgent] 正在检索相关文档，query: {query[:50]}...")
        
        # 使用 MMR (最大边际相关性) 检索，避免结果过于相似
        docs = self.vectorstore.max_marginal_relevance_search(
            query,
            k=self.retrieval_k,
            fetch_k=self.retrieval_k * 2  # 先取更多候选，再筛选
        )
        
        print(f"[RAGAgent] 检索到 {len(docs)} 个相关文档片段")
        return docs
    
    def run(self, query: str, context: dict = None) -> str:
        """
        执行 RAG Agent 的完整流程
        
        Args:
            query: 用户查询问题
            context: 共享上下文（用于多 Agent 协作）
            
        Returns:
            基于检索结果生成的答案
        """
        context = context or {}
        
        # 1. 检索相关文档
        retrieved_docs = self.retrieve(query)
        
        # 2. 构建上下文
        doc_context = "\n\n".join([
            f"文档片段 {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # 保存到 context（供其他 Agent 使用）
        context["retrieved_docs"] = [doc.page_content for doc in retrieved_docs]
        
        # 3. 构建 prompt
        prompt = f"""
基于以下检索到的文档内容，回答用户的问题。

检索到的相关文档：
{doc_context}

用户问题：{query}

要求：
- 基于检索到的文档内容回答
- 如果文档中没有相关信息，请明确说明
- 回答要准确、清晰、有条理
"""
        
        # 4. 调用 LLM 生成答案
        print(f"[RAGAgent] 正在生成答案...")
        response = self.llm.invoke(prompt)
        
        # 保存结果到 context
        context["rag_result"] = response.content
        
        return response.content
