"""
批量评估脚本

支持：
1. 从测试集批量评估
2. 生成对比报告
3. 统计分析
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluation import RAGEvaluator, AgentEvaluator, WorkflowEvaluator
from src.core.unified_agent import UnifiedAgent
from src.rag import load_index
from langchain_openai import ChatOpenAI
from src.config import Config
import json
import time
from typing import List, Dict, Any
import numpy as np


class BatchEvaluator:
    """批量评估器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
        self.vectorstore = load_index()
        self.agent = UnifiedAgent(llm=self.llm, vectorstore=self.vectorstore)
        
        self.rag_evaluator = RAGEvaluator(llm=self.llm)
        self.agent_evaluator = AgentEvaluator(llm=self.llm)
        self.workflow_evaluator = WorkflowEvaluator(llm=self.llm)
    
    def load_test_set(self, filepath: str) -> List[Dict[str, Any]]:
        """加载测试集"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_rag_batch(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量评估 RAG"""
        results = []
        
        print(f"\n开始批量评估 RAG，共 {len(test_cases)} 个测试用例\n")
        
        for i, case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] 评估: {case['query'][:50]}...")
            
            try:
                # 执行 RAG
                result = self.agent.run(case['query'], mode="rag")
                
                # 获取检索文档
                from src.agents.rag_agent import RAGAgent
                rag_agent = RAGAgent(llm=self.llm, vectorstore=self.vectorstore)
                docs = rag_agent.retrieve(case['query'])
                retrieved_docs = [doc.page_content for doc in docs]
                
                # 评估
                report = self.rag_evaluator.evaluate(
                    query=case['query'],
                    retrieved_docs=retrieved_docs,
                    generated_text=result,
                    reference_text=case.get('reference_answer')
                )
                
                results.append({
                    'case': case,
                    'result': result,
                    'report': report.to_dict()
                })
                
                print(f"  ✓ 完成，综合得分: {report.generation_metrics.overall_score:.1f}/10\n")
                
            except Exception as e:
                print(f"  ✗ 失败: {e}\n")
                results.append({
                    'case': case,
                    'error': str(e)
                })
        
        return results
    
    def evaluate_agent_batch(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量评估 Agent"""
        results = []
        
        print(f"\n开始批量评估 Agent，共 {len(test_cases)} 个测试用例\n")
        
        for i, case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] 评估: {case['task'][:50]}...")
            
            try:
                # 执行 Agent
                start_time = time.time()
                result = self.agent.run(case['task'], mode="simple")
                execution_time = time.time() - start_time
                
                # 评估
                report = self.agent_evaluator.evaluate(
                    task=case['task'],
                    selected_tools=case.get('expected_tools', ['retriever']),
                    reasoning_steps=["执行任务"],
                    final_answer=result,
                    execution_time=execution_time,
                    reference_answer=case.get('reference_answer')
                )
                
                results.append({
                    'case': case,
                    'result': result,
                    'report': report.to_dict()
                })
                
                print(f"  ✓ 完成，综合得分: {report.generation_metrics.overall_score:.1f}/10\n")
                
            except Exception as e:
                print(f"  ✗ 失败: {e}\n")
                results.append({
                    'case': case,
                    'error': str(e)
                })
        
        return results
    
    def generate_statistics(self, results: List[Dict[str, Any]], eval_type: str) -> Dict[str, Any]:
        """生成统计报告"""
        successful_results = [r for r in results if 'report' in r]
        
        if not successful_results:
            return {"error": "没有成功的评估结果"}
        
        stats = {
            "total_cases": len(results),
            "successful_cases": len(successful_results),
            "failed_cases": len(results) - len(successful_results),
            "success_rate": len(successful_results) / len(results) * 100
        }
        
        if eval_type == "rag":
            # RAG 统计
            gen_scores = [r['report']['generation_metrics']['overall_score'] for r in successful_results]
            ret_scores = [r['report']['retrieval_metrics']['relevance_score'] for r in successful_results]
            
            stats.update({
                "generation_metrics": {
                    "mean": np.mean(gen_scores),
                    "std": np.std(gen_scores),
                    "min": np.min(gen_scores),
                    "max": np.max(gen_scores)
                },
                "retrieval_metrics": {
                    "mean": np.mean(ret_scores),
                    "std": np.std(ret_scores),
                    "min": np.min(ret_scores),
                    "max": np.max(ret_scores)
                }
            })
        
        elif eval_type == "agent":
            # Agent 统计
            gen_scores = [r['report']['generation_metrics']['overall_score'] for r in successful_results]
            
            stats.update({
                "generation_metrics": {
                    "mean": np.mean(gen_scores),
                    "std": np.std(gen_scores),
                    "min": np.min(gen_scores),
                    "max": np.max(gen_scores)
                }
            })
        
        return stats
    
    def save_batch_results(self, results: List[Dict[str, Any]], stats: Dict[str, Any], eval_type: str):
        """保存批量评估结果"""
        output_dir = "data/evaluation_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = int(time.time())
        
        # 保存详细结果
        results_file = os.path.join(output_dir, f"batch_{eval_type}_{timestamp}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 保存统计报告
        stats_file = os.path.join(output_dir, f"batch_{eval_type}_stats_{timestamp}.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存:")
        print(f"  - 详细结果: {results_file}")
        print(f"  - 统计报告: {stats_file}")


def create_sample_test_set():
    """创建示例测试集"""
    rag_test_set = [
        {
            "query": "什么是 CLIP 模型？",
            "reference_answer": "CLIP 是一个多模态模型，可以理解图像和文本的关系"
        },
        {
            "query": "Transformer 的核心创新是什么？",
            "reference_answer": "Transformer 的核心创新是自注意力机制"
        },
        {
            "query": "深度学习在 NLP 中有哪些应用？",
            "reference_answer": "深度学习在 NLP 中的应用包括机器翻译、文本分类、问答系统等"
        }
    ]
    
    agent_test_set = [
        {
            "task": "检索并总结 Transformer 的核心特点",
            "expected_tools": ["retriever"],
            "reference_answer": "Transformer 使用自注意力机制，具有并行计算能力"
        },
        {
            "task": "分析深度学习的优势和局限性",
            "expected_tools": ["retriever"],
            "reference_answer": "深度学习优势在于强大的表示学习能力，局限性在于需要大量数据"
        }
    ]
    
    # 保存测试集
    os.makedirs("data/test_sets", exist_ok=True)
    
    with open("data/test_sets/rag_test_set.json", 'w', encoding='utf-8') as f:
        json.dump(rag_test_set, f, ensure_ascii=False, indent=2)
    
    with open("data/test_sets/agent_test_set.json", 'w', encoding='utf-8') as f:
        json.dump(agent_test_set, f, ensure_ascii=False, indent=2)
    
    print("示例测试集已创建:")
    print("  - data/test_sets/rag_test_set.json")
    print("  - data/test_sets/agent_test_set.json")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="批量评估脚本")
    parser.add_argument('--type', choices=['rag', 'agent'], required=True, help='评估类型')
    parser.add_argument('--test-set', help='测试集文件路径')
    parser.add_argument('--create-sample', action='store_true', help='创建示例测试集')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_test_set()
        return
    
    if not args.test_set:
        print("请指定测试集文件路径，或使用 --create-sample 创建示例测试集")
        return
    
    evaluator = BatchEvaluator()
    
    # 加载测试集
    test_cases = evaluator.load_test_set(args.test_set)
    
    # 批量评估
    if args.type == 'rag':
        results = evaluator.evaluate_rag_batch(test_cases)
    elif args.type == 'agent':
        results = evaluator.evaluate_agent_batch(test_cases)
    
    # 生成统计
    stats = evaluator.generate_statistics(results, args.type)
    
    # 输出统计
    print("\n" + "="*60)
    print("统计报告")
    print("="*60)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 保存结果
    evaluator.save_batch_results(results, stats, args.type)


if __name__ == "__main__":
    main()
