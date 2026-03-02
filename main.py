"""
主入口文件：提供统一的 CLI 接口
"""

import sys
import argparse
from scripts.build_index import main as build_index
from scripts.run_qa import main as run_qa
from scripts.run_writing import run_basic_workflow, run_interactive_workflow


def main():
    """主函数：解析命令行参数并执行相应功能"""
    parser = argparse.ArgumentParser(
        description="LangChain Tutorial - RAG 和 Agent 学习项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 构建索引
  python main.py build --pdf data/pdf/CLIP.pdf
  
  # 运行问答（单次）
  python main.py qa --query "What is CLIP?"
  
  # 运行问答（交互模式）
  python main.py qa --interactive
  
  # 运行写作工作流
  python main.py write --topic "人工智能的利弊"
  
  # 运行写作工作流（交互模式）
  python main.py write --topic "人工智能的利弊" --interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 构建索引命令
    build_parser = subparsers.add_parser('build', help='构建 FAISS 向量索引')
    build_parser.add_argument('--pdf', type=str, help='PDF 文件路径')
    
    # 问答命令
    qa_parser = subparsers.add_parser('qa', help='运行 RAG 问答系统')
    qa_parser.add_argument('--query', type=str, help='查询问题')
    qa_parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    
    # 写作命令
    write_parser = subparsers.add_parser('write', help='运行写作工作流')
    write_parser.add_argument('--topic', type=str, default='人工智能的利弊', help='写作主题')
    write_parser.add_argument('--max-iterations', type=int, default=3, help='最大迭代次数')
    write_parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return
    
    # 执行相应命令
    try:
        if args.command == 'build':
            build_index(args.pdf)
        
        elif args.command == 'qa':
            run_qa(args.query, args.interactive)
        
        elif args.command == 'write':
            if args.interactive:
                run_interactive_workflow(args.topic, args.max_iterations)
            else:
                run_basic_workflow(args.topic, args.max_iterations)
    
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
