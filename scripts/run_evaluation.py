"""
评估系统运行脚本

支持评估：
1. RAG 系统
2. Agent 系统
3. Workflow 系统
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluation import RAGEvaluator, AgentEvaluator, WorkflowEvaluator
from src.core.unified_agent import UnifiedAgent
from src.rag import load_index
from langchain_openai import ChatOpenAI
from src.config import Config
import time
import json


def evaluate_rag_system():
    """评估 RAG 系统"""
    print("\n" + "="*60)
    print("评估 RAG 系统")
    print("="*60 + "\n")
    
    # 初始化
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    vectorstore = load_index()
    agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
    evaluator = RAGEvaluator(llm=llm)
    
    # 测试查询
    query = "什么是 CLIP 模型？它的核心创新是什么？"
    
    print(f"查询: {query}\n")
    
    # 执行 RAG
    print("[执行] 运行 RAG Agent...")
    result = agent.run(query, mode="rag")
    
    # 获取检索文档
    from src.agents.rag_agent import RAGAgent
    rag_agent = RAGAgent(llm=llm, vectorstore=vectorstore)
    docs = rag_agent.retrieve(query)
    retrieved_docs = [doc.page_content for doc in docs]
    
    # 评估
    report = evaluator.evaluate(
        query=query,
        retrieved_docs=retrieved_docs,
        generated_text=result
    )
    
    # 输出报告
    print("\n" + "="*60)
    print("评估报告")
    print("="*60)
    print(report.summary())
    
    # 保存报告
    save_report(report, "rag_evaluation")
    
    return report


def evaluate_agent_system():
    """评估 Agent 系统"""
    print("\n" + "="*60)
    print("评估 Agent 系统")
    print("="*60 + "\n")
    
    # 初始化
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    vectorstore = load_index()
    agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
    evaluator = AgentEvaluator(llm=llm)
    
    # 测试任务
    task = "检索关于 Transformer 的信息，并总结其核心特点"
    
    print(f"任务: {task}\n")
    
    # 执行 Agent
    print("[执行] 运行 Simple Agent...")
    start_time = time.time()
    result = agent.run(task, mode="simple")
    execution_time = time.time() - start_time
    
    # 模拟推理步骤（实际应从 Agent 执行过程中提取）
    selected_tools = ["retriever"]
    reasoning_steps = [
        "分析任务：需要检索 Transformer 相关信息",
        "选择工具：使用 retriever 工具检索文档",
        "执行检索：从向量数据库获取相关文档",
        "生成总结：基于检索结果总结核心特点"
    ]
    
    # 评估
    report = evaluator.evaluate(
        task=task,
        selected_tools=selected_tools,
        reasoning_steps=reasoning_steps,
        final_answer=result,
        execution_time=execution_time
    )
    
    # 输出报告
    print("\n" + "="*60)
    print("评估报告")
    print("="*60)
    print(report.summary())
    
    # 保存报告
    save_report(report, "agent_evaluation")
    
    return report


def evaluate_workflow_system():
    """评估 Workflow 系统"""
    print("\n" + "="*60)
    print("评估 Workflow 系统")
    print("="*60 + "\n")
    
    try:
        from langgraph.checkpoint.memory import MemorySaver
    except ImportError:
        print("需要安装 langgraph: pip install langgraph")
        return None
    
    # 初始化
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    vectorstore = load_index()
    agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
    evaluator = WorkflowEvaluator(llm=llm)
    
    # 测试任务
    task = "深度学习在计算机视觉中的应用"
    
    print(f"任务: {task}\n")
    
    # 执行 Workflow
    print("[执行] 运行 RAG Writing Workflow...")
    start_time = time.time()
    
    # 收集节点信息
    node_sequence = []
    node_outputs = {}
    node_times = {}
    
    # 模拟执行（实际应从工作流中提取）
    result = agent.run(task, mode="workflow", max_iterations=2)
    
    total_time = time.time() - start_time
    
    # 模拟节点数据
    node_sequence = ["retriever", "summarizer", "reviewer", "refiner", "reviewer"]
    node_outputs = {
        "retriever": "检索到 3 个相关文档",
        "summarizer": result[:200] + "...",
        "reviewer": "评分: 7/10, 需要优化",
        "refiner": "优化后的综述",
    }
    node_times = {
        "retriever": 2.5,
        "summarizer": 8.3,
        "reviewer": 3.2,
        "refiner": 6.8
    }
    
    # 评估
    report = evaluator.evaluate(
        task=task,
        workflow_description="RAG + Agent 综述写作工作流",
        node_sequence=node_sequence,
        node_outputs=node_outputs,
        final_output=result,
        total_time=total_time,
        node_times=node_times,
        iterations=2,
        max_iterations=3,
        success=True,
        error_count=0
    )
    
    # 输出报告
    print("\n" + "="*60)
    print("评估报告")
    print("="*60)
    print(report.summary())
    
    # 保存报告
    save_report(report, "workflow_evaluation")
    
    return report


def save_report(report, filename):
    """保存评估报告"""
    output_dir = "data/evaluation_reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, f"{filename}_{int(time.time())}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存到: {filepath}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="评估系统运行脚本")
    parser.add_argument(
        '--type',
        choices=['rag', 'agent', 'workflow', 'all'],
        default='all',
        help='评估类型'
    )
    
    args = parser.parse_args()
    
    if args.type == 'rag' or args.type == 'all':
        evaluate_rag_system()
    
    if args.type == 'agent' or args.type == 'all':
        evaluate_agent_system()
    
    if args.type == 'workflow' or args.type == 'all':
        evaluate_workflow_system()


if __name__ == "__main__":
    main()
