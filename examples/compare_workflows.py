"""
对比两种写作工作流

1. 基础写作工作流 (writing_graph.py)
   - 纯 LLM 生成，不依赖外部知识
   - 适合创意写作、观点文章
   
2. RAG 写作工作流 (rag_writing_graph.py)
   - 基于检索到的文档生成
   - 适合学术综述、技术报告
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def demo_basic_writing():
    """演示基础写作工作流"""
    print("="*70)
    print("📝 基础写作工作流演示")
    print("="*70)
    print()
    
    from src.workflows.writing_graph import create_writing_graph
    from langgraph.checkpoint.memory import MemorySaver
    
    # 创建工作流
    graph = create_writing_graph(max_iterations=2)
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    
    # 初始状态
    initial_state = {
        "topic": "人工智能对未来教育的影响",
        "outline": "",
        "draft": [],
        "feedback": "",
        "approved": False,
        "revision_type": None,
        "iteration": 0,
        "max_iterations": 2
    }
    
    print("主题：人工智能对未来教育的影响")
    print("特点：纯 LLM 生成，不依赖外部文档")
    print()
    print("流程：Planner → Writer A/B → Reviewer → (可能) Refine")
    print()
    
    # 运行（这里只是演示，不实际执行）
    print("✓ 工作流已准备就绪")
    print()


def demo_rag_writing():
    """演示 RAG 写作工作流"""
    print("="*70)
    print("📚 RAG 写作工作流演示")
    print("="*70)
    print()
    
    print("主题：深度学习在自然语言处理中的应用")
    print("特点：基于检索到的论文文档生成综述")
    print()
    print("流程：Retriever → Summarizer → Reviewer → (可能) Refiner")
    print()
    print("关键区别：")
    print("  1. 第一步是检索相关文档（不是生成大纲）")
    print("  2. 基于真实文档内容写作（不是凭空生成）")
    print("  3. 适合需要引用事实的学术写作")
    print()
    print("✓ 工作流已准备就绪")
    print()


def compare_workflows():
    """对比两种工作流"""
    print("="*70)
    print("🔍 两种工作流对比")
    print("="*70)
    print()
    
    comparison = """
┌─────────────────┬──────────────────────┬──────────────────────┐
│   特性          │   基础写作工作流      │   RAG 写作工作流      │
├─────────────────┼──────────────────────┼──────────────────────┤
│ 数据来源        │ LLM 内部知识         │ 外部文档检索         │
│ 适用场景        │ 创意写作、观点文章    │ 学术综述、技术报告    │
│ 准确性          │ 可能有幻觉           │ 基于真实文档         │
│ 时效性          │ 受训练数据限制        │ 可使用最新文档       │
│ 引用能力        │ 无法引用来源         │ 可标注文档来源       │
│ 第一步          │ Planner (生成大纲)   │ Retriever (检索文档) │
│ 核心节点        │ Writer              │ Summarizer          │
│ 依赖            │ 仅需 LLM            │ 需要向量数据库       │
└─────────────────┴──────────────────────┴──────────────────────┘

使用建议：
✓ 写观点文章、创意内容 → 使用基础写作工作流
✓ 写学术综述、技术报告 → 使用 RAG 写作工作流
✓ 需要引用具体来源 → 使用 RAG 写作工作流
✓ 追求创意和多样性 → 使用基础写作工作流
"""
    print(comparison)


def main():
    """主函数"""
    print("\n")
    print("🎯 写作工作流对比演示")
    print("\n")
    
    # 演示基础写作
    demo_basic_writing()
    
    # 演示 RAG 写作
    demo_rag_writing()
    
    # 对比分析
    compare_workflows()
    
    print("="*70)
    print("💡 提示")
    print("="*70)
    print()
    print("运行基础写作：python scripts/run_writing.py")
    print("运行 RAG 写作：python scripts/run_rag_writing.py")
    print()


if __name__ == "__main__":
    main()
