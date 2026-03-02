"""
运行 RAG 综述写作工作流

使用方法：
python scripts/run_rag_writing.py

功能：
1. 从向量数据库检索相关论文
2. 自动生成学术综述
3. 多轮审核和优化
4. 输出最终结果
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflows.rag_writing_graph import create_rag_writing_graph
from langgraph.checkpoint.memory import MemorySaver


def main():
    """主函数：运行 RAG 综述写作工作流"""
    
    print("="*70)
    print("🚀 RAG + Agent 综述写作系统")
    print("="*70)
    print()
    
    # 用户输入查询主题
    query = input("请输入您想要撰写综述的主题：").strip()
    
    if not query:
        query = "深度学习在自然语言处理中的应用"
        print(f"使用默认主题：{query}")
    
    print()
    print("="*70)
    print("开始工作流...")
    print("="*70)
    print()
    
    # 创建工作流图
    graph = create_rag_writing_graph(max_iterations=3)
    
    # 添加检查点支持（用于断点恢复）
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    
    # 初始化状态
    initial_state = {
        "query": query,
        "retrieved_docs": [],
        "summary": "",
        "review_feedback": "",
        "refined_summary": "",
        "approved": False,
        "iteration": 0,
        "max_iterations": 3
    }
    
    # 运行工作流
    config = {"configurable": {"thread_id": "rag_writing_demo"}}
    
    try:
        final_state = None
        for state in app.stream(initial_state, config):
            final_state = state
        
        # 提取最终状态
        if final_state:
            # 获取最后一个节点的状态
            last_node = list(final_state.keys())[0]
            result = final_state[last_node]
            
            print()
            print("="*70)
            print("✅ 工作流执行完成！")
            print("="*70)
            print()
            
            # 输出结果
            print("📊 执行统计：")
            print(f"  - 迭代次数: {result.get('iteration', 0)}")
            print(f"  - 是否通过审核: {'✓ 是' if result.get('approved', False) else '✗ 否'}")
            print(f"  - 检索文档数: {len(result.get('retrieved_docs', []))}")
            print()
            
            print("="*70)
            print("📝 最终综述：")
            print("="*70)
            final_summary = result.get('refined_summary') or result.get('summary', '')
            print(final_summary)
            print()
            
            if result.get('review_feedback'):
                print("="*70)
                print("💬 最终审核反馈：")
                print("="*70)
                print(result['review_feedback'])
                print()
            
            # 保存结果到文件
            output_file = "output_rag_summary.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"查询主题：{query}\n")
                f.write(f"{'='*70}\n\n")
                f.write(f"最终综述：\n{final_summary}\n\n")
                f.write(f"{'='*70}\n")
                f.write(f"审核反馈：\n{result.get('review_feedback', '无')}\n")
            
            print(f"✓ 结果已保存到：{output_file}")
            
    except Exception as e:
        print(f"\n❌ 执行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
