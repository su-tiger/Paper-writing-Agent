"""
RAG 系统评估器
"""

from typing import List, Dict, Any, Optional
import numpy as np
from langchain_openai import ChatOpenAI
import json
import re

from .base_evaluator import BaseEvaluator
from .metrics import RetrievalMetrics, GenerationMetrics, EvaluationReport
from ..config import Config


class RAGEvaluator(BaseEvaluator):
    """
    RAG 系统评估器
    
    评估维度：
    1. 检索质量：相关性、覆盖度
    2. 生成质量：流畅度、准确性、完整性
    """
    
    def __init__(self, llm=None):
        super().__init__(llm)
        if self.llm is None:
            self.llm = ChatOpenAI(
                model=Config.DEEPSEEK_MODEL,
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
    
    def evaluate_retrieval(
        self,
        query: str,
        retrieved_docs: List[str],
        ground_truth_docs: Optional[List[str]] = None
    ) -> RetrievalMetrics:
        """
        评估检索质量
        
        Args:
            query: 查询问题
            retrieved_docs: 检索到的文档列表
            ground_truth_docs: 真实相关文档列表（可选）
            
        Returns:
            检索质量指标
        """
        # 如果有真实标注，计算精确率和召回率
        if ground_truth_docs:
            retrieved_set = set(retrieved_docs)
            ground_truth_set = set(ground_truth_docs)
            
            tp = len(retrieved_set & ground_truth_set)
            precision = tp / len(retrieved_set) if retrieved_set else 0
            recall = tp / len(ground_truth_set) if ground_truth_set else 0
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        else:
            # 使用 LLM 评估相关性
            precision, recall, f1_score = self._llm_based_retrieval_eval(query, retrieved_docs)
        
        # 计算 MRR 和 NDCG（基于 LLM 评分）
        relevance_scores = self._get_relevance_scores(query, retrieved_docs)
        mrr = self._calculate_mrr(relevance_scores)
        ndcg = self._calculate_ndcg(relevance_scores)
        
        # 平均相关性得分
        relevance_score = np.mean(relevance_scores) if relevance_scores else 0.0
        
        return RetrievalMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            mrr=mrr,
            ndcg=ndcg,
            relevance_score=relevance_score
        )
    
    def _llm_based_retrieval_eval(self, query: str, retrieved_docs: List[str]) -> tuple:
        """使用 LLM 评估检索质量"""
        prompt = f"""
评估以下检索结果的质量。

查询问题：{query}

检索到的文档：
{self._format_docs(retrieved_docs)}

请评估：
1. 有多少文档与查询相关？
2. 估计可能遗漏了多少相关文档？

返回 JSON 格式：
{{
    "relevant_count": <相关文档数>,
    "total_retrieved": <检索总数>,
    "estimated_missing": <估计遗漏数>
}}
"""
        
        response = self.llm.invoke(prompt)
        try:
            result = json.loads(response.content)
            relevant = result.get('relevant_count', 0)
            total = result.get('total_retrieved', len(retrieved_docs))
            missing = result.get('estimated_missing', 0)
            
            precision = relevant / total if total > 0 else 0
            recall = relevant / (relevant + missing) if (relevant + missing) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            return precision, recall, f1
        except:
            # 默认值
            return 0.7, 0.6, 0.65
    
    def _get_relevance_scores(self, query: str, docs: List[str]) -> List[float]:
        """获取每个文档的相关性得分（1-10）"""
        scores = []
        for doc in docs:
            prompt = f"""
评估文档与查询的相关性（1-10分）。

查询：{query}
文档：{doc[:500]}...

只返回数字分数（1-10）。
"""
            try:
                response = self.llm.invoke(prompt)
                score = float(re.search(r'\d+', response.content).group())
                scores.append(min(max(score, 1), 10) / 10.0)  # 归一化到 0-1
            except:
                scores.append(0.5)  # 默认中等相关
        
        return scores
    
    def _calculate_mrr(self, relevance_scores: List[float]) -> float:
        """计算平均倒数排名 (MRR)"""
        for i, score in enumerate(relevance_scores):
            if score >= 0.7:  # 认为相关
                return 1.0 / (i + 1)
        return 0.0
    
    def _calculate_ndcg(self, relevance_scores: List[float], k: int = None) -> float:
        """计算归一化折损累积增益 (NDCG)"""
        if not relevance_scores:
            return 0.0
        
        k = k or len(relevance_scores)
        relevance_scores = relevance_scores[:k]
        
        # DCG
        dcg = sum(score / np.log2(i + 2) for i, score in enumerate(relevance_scores))
        
        # IDCG (理想情况)
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = sum(score / np.log2(i + 2) for i, score in enumerate(ideal_scores))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def evaluate_generation(
        self,
        query: str,
        generated_text: str,
        reference_text: Optional[str] = None,
        retrieved_docs: Optional[List[str]] = None
    ) -> GenerationMetrics:
        """
        评估生成质量
        
        Args:
            query: 查询问题
            generated_text: 生成的文本
            reference_text: 参考答案（可选）
            retrieved_docs: 检索到的文档（用于评估事实准确性）
            
        Returns:
            生成质量指标
        """
        prompt = f"""
你是一位专业的文本质量评估专家。请从以下维度评估生成文本的质量（每项 1-10 分）：

查询问题：{query}

生成文本：
{generated_text}

{f"参考答案：{reference_text}" if reference_text else ""}

{f"检索文档：{self._format_docs(retrieved_docs)}" if retrieved_docs else ""}

评估维度：
1. fluency（流畅度）：语言是否流畅自然
2. coherence（连贯性）：逻辑是否清晰连贯
3. relevance（相关性）：是否回答了问题
4. factuality（事实准确性）：内容是否准确可靠
5. completeness（完整性）：是否全面完整

返回 JSON 格式：
{{
    "fluency": <1-10>,
    "coherence": <1-10>,
    "relevance": <1-10>,
    "factuality": <1-10>,
    "completeness": <1-10>
}}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            # 解析 JSON
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                scores = json.loads(json_match.group())
            else:
                scores = json.loads(response.content)
            
            fluency = float(scores.get('fluency', 7))
            coherence = float(scores.get('coherence', 7))
            relevance = float(scores.get('relevance', 7))
            factuality = float(scores.get('factuality', 7))
            completeness = float(scores.get('completeness', 7))
            
        except Exception as e:
            print(f"[RAGEvaluator] 解析评分失败: {e}，使用默认值")
            fluency = coherence = relevance = factuality = completeness = 7.0
        
        # 计算综合得分（加权平均）
        overall_score = (
            fluency * 0.15 +
            coherence * 0.20 +
            relevance * 0.25 +
            factuality * 0.25 +
            completeness * 0.15
        )
        
        return GenerationMetrics(
            fluency=fluency,
            coherence=coherence,
            relevance=relevance,
            factuality=factuality,
            completeness=completeness,
            overall_score=overall_score
        )
    
    def evaluate(
        self,
        query: str,
        retrieved_docs: List[str],
        generated_text: str,
        reference_text: Optional[str] = None,
        ground_truth_docs: Optional[List[str]] = None
    ) -> EvaluationReport:
        """
        完整评估 RAG 系统
        
        Args:
            query: 查询问题
            retrieved_docs: 检索到的文档
            generated_text: 生成的文本
            reference_text: 参考答案（可选）
            ground_truth_docs: 真实相关文档（可选）
            
        Returns:
            完整评估报告
        """
        print("[RAGEvaluator] 开始评估...")
        
        # 评估检索质量
        print("[RAGEvaluator] 评估检索质量...")
        retrieval_metrics = self.evaluate_retrieval(
            query=query,
            retrieved_docs=retrieved_docs,
            ground_truth_docs=ground_truth_docs
        )
        
        # 评估生成质量
        print("[RAGEvaluator] 评估生成质量...")
        generation_metrics = self.evaluate_generation(
            query=query,
            generated_text=generated_text,
            reference_text=reference_text,
            retrieved_docs=retrieved_docs
        )
        
        # 生成报告
        report = EvaluationReport(
            task_type="RAG",
            task_description=query,
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
            input_data={
                "query": query,
                "retrieved_docs_count": len(retrieved_docs)
            },
            output_data={
                "generated_text": generated_text[:200] + "..."
            }
        )
        
        self.save_evaluation(report.to_dict())
        
        print("[RAGEvaluator] 评估完成！")
        return report
    
    def _format_docs(self, docs: List[str], max_length: int = 200) -> str:
        """格式化文档列表"""
        formatted = []
        for i, doc in enumerate(docs[:5]):  # 最多显示 5 个
            content = doc[:max_length] + "..." if len(doc) > max_length else doc
            formatted.append(f"[文档 {i+1}] {content}")
        return "\n".join(formatted)
