"""
运行统一 Agent 系统

使用方法：
python scripts/run_unified_agent.py

功能：
1. 自动路由到最佳执行模式
2. 支持简单问答、RAG 问答、复杂工作流
3. 统一的接口和体验
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.unified_agent import UnifiedAgent
from src.rag import load_index, create_embeddings
from langchain_openai import ChatOpenAI
from src.config import Config


def main():
    """主函数"""
    print("="*70)
    print("🚀 统一 Agent 系统")
    print("="*70)
    print()
    print("这是一个融合了三大框架的统一系统：")
    print("  - SimpleAgent (ReAct 模式)")
    print("  - RAGAgent (RAG 模式)")
    print("  - LangGraph (工作流模式)")
    print()
    print("系统会自动选择最佳执行模式！")
    print()
    print("="*70)
    print()
    
    # 初始化
    print("[1/3] 初始化 LLM...")
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    print("✓ LLM 初始化完成")
    
    print("\n[2/3] 加载向量索引...")
    try:
        embeddings = create_embeddings()
        vectorstore = load_index()
        print("✓ 向量索引加载完成")
    except Exception as e:
        print(f"⚠ 向量索引加载失败: {e}")
        print("提示：运行 python scripts/build_index.py 构建索引")
        vectorstore = None
    
    print("\n[3/3] 创建统一 Agent...")
    agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
    print("✓ 统一 Agent 创建完成")
    
    # 显示统计信息
    stats = agent.get_stats()
    print(f"\n系统信息：")
    print(f"  - 可用工具数: {stats['tools_count']}")
    print(f"  - RAG 支持: {'✓' if stats['has_rag'] else '✗'}")
    print(f"  - LLM 模型: {stats['llm_model']}")
    
    print("\n" + "="*70)
    print("开始交互（输入 'quit' 退出）")
    print("="*70)
    print()
    
    # 交互循环
    while True:
        try:
            # 获取用户输入
            task = input("\n请输入任务：").strip()
            
            if not task:
                continue
            
            if task.lower() in ['quit', 'exit', 'q']:
                print("\n再见！👋")
                break
            
            # 执行任务（使用事件流）
            print("\n" + "="*70)
            print("📝 执行结果：")
            print("="*70)
            
            # 只显示 LLM token 和关键事件
            for event in agent.stream(task, mode="auto"):
                if event.type == "route":
                    print(f"[路由] {event.data['selected_mode']} 模式")
                elif event.type == "tool_start":
                    print(f"[工具] 调用 {event.data['tool_name']}...")
                elif event.type == "llm_token":
                    print(event.data['token'], end="", flush=True)
                elif event.type == "error":
                    print(f"\n[错误] {event.data['error_message']}")
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！👋")
            break
        except Exception as e:
            print(f"\n❌ 执行出错：{e}")
            import traceback
            traceback.print_exc()


def demo_mode():
    """演示模式：展示不同类型的任务"""
    print("="*70)
    print("🎯 统一 Agent 系统 - 演示模式")
    print("="*70)
    print()
    
    # 初始化
    print("正在初始化...")
    llm = ChatOpenAI(
        model=Config.DEEPSEEK_MODEL,
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    
    try:
        embeddings = create_embeddings()
        vectorstore = load_index()
    except:
        vectorstore = None
    
    agent = UnifiedAgent(llm=llm, vectorstore=vectorstore)
    
    # 测试任务
    test_tasks = [
        ("你好", "simple"),
        ("什么是深度学习？", "rag"),
        ("写一篇关于深度学习的综述", "workflow")
    ]
    
    for i, (task, expected_mode) in enumerate(test_tasks, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_tasks)}")
        print(f"{'='*70}")
        print(f"任务: {task}")
        print(f"预期模式: {expected_mode}")
        print("\n结果: ", end="", flush=True)
        
        try:
            # 使用流式输出
            for chunk in agent.run(task, mode="auto", stream=True):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n错误: {e}")
        
        print()


if __name__ == "__main__":
    import sys
    
    # 检查是否是演示模式
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        main()
