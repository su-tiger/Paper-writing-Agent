"""
运行写作工作流脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflows import create_writing_graph
from langgraph.checkpoint.memory import MemorySaver


def run_basic_workflow(topic: str, max_iterations: int = 3):
    """
    运行基本写作工作流（无人工介入）
    
    Args:
        topic: 写作主题
        max_iterations: 最大迭代次数
    """
    print(f"正在创建写作工作流...")
    graph = create_writing_graph(max_iterations=max_iterations)
    
    # 创建内存检查点
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    
    # 配置会话 ID
    config = {"configurable": {"thread_id": f"writing_{topic[:20]}"}}
    
    print(f"\n开始写作，主题: {topic}")
    print(f"最大迭代次数: {max_iterations}\n")
    print("=" * 80)
    
    # 执行工作流
    result = app.invoke({
        "topic": topic,
        "outline": "",
        "draft": [],
        "feedback": "",
        "approved": False,
        "revision_type": None,
        "iteration": 0,
        "max_iterations": max_iterations
    }, config=config)
    
    print("\n" + "=" * 80)
    print("\n===== 最终结果 =====\n")
    print(f"主题: {result['topic']}")
    print(f"\n大纲:\n{result['outline']}")
    print(f"\n文章:\n{result['draft'][0] if result['draft'] else '无'}")
    print(f"\n审核状态: {'通过' if result['approved'] else '未通过'}")
    print(f"迭代次数: {result['iteration']}")


def run_interactive_workflow(topic: str, max_iterations: int = 3):
    """
    运行交互式写作工作流（支持人工介入）
    
    Args:
        topic: 写作主题
        max_iterations: 最大迭代次数
    """
    print(f"正在创建写作工作流...")
    graph = create_writing_graph(max_iterations=max_iterations)
    
    # 创建内存检查点，在 reviewer 节点前暂停
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory, interrupt_before=["reviewer"])
    
    # 配置会话 ID
    config = {"configurable": {"thread_id": f"interactive_{topic[:20]}"}}
    
    print(f"\n开始写作，主题: {topic}")
    print(f"最大迭代次数: {max_iterations}")
    print("模式: 交互式（在审核前暂停）\n")
    print("=" * 80)
    
    # 步骤 1：启动工作流
    print("\n[系统] 正在生成大纲和文章...")
    app.invoke({
        "topic": topic,
        "iteration": 0,
        "max_iterations": max_iterations,
        "draft": []
    }, config)
    
    # 程序会在 reviewer 节点前自动暂停
    snapshot = app.get_state(config)
    print(f"\n[系统] 当前暂停节点: {snapshot.next}")
    print(f"\n[系统] 待审核内容预览:")
    print("-" * 80)
    for i, draft in enumerate(snapshot.values['draft'], 1):
        print(f"\n草稿 {i}:\n{draft[:500]}...")
    print("-" * 80)
    
    # 步骤 2：人工审核
    input("\n按下回车键继续进入审核流程...")
    user_feedback = input("\n[人工介入] 是否要修改草稿？(直接回车跳过，或输入修改意见): ")
    
    if user_feedback:
        new_draft = snapshot.values['draft'].copy()
        new_draft.append(f"\n[人工补充]: {user_feedback}")
        app.update_state(config, {"draft": new_draft}, as_node="writerA")
        print("\n[系统] 状态已更新")
    
    # 步骤 3：恢复执行
    print("\n[系统] 继续执行审核流程...")
    result = app.invoke(None, config)
    
    print("\n" + "=" * 80)
    print("\n===== 最终结果 =====\n")
    print(f"主题: {result['topic']}")
    print(f"\n审核状态: {'通过' if result['approved'] else '未通过'}")
    print(f"迭代次数: {result['iteration']}")
    if result.get('feedback'):
        print(f"\n反馈: {result['feedback']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行写作工作流")
    parser.add_argument(
        "--topic",
        type=str,
        help="写作主题",
        default="人工智能的利弊"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="最大迭代次数",
        default=3
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="交互模式（支持人工介入）"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_workflow(args.topic, args.max_iterations)
    else:
        run_basic_workflow(args.topic, args.max_iterations)
