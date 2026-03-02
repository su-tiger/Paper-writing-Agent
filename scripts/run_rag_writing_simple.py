"""
简化版 RAG 综述写作脚本（不依赖 LangGraph）

功能：
1. 从向量数据库检索相关论文
2. 生成学术综述
3. 简单的质量评估
4. 保存结果

注意：这是简化版，不包含多轮迭代优化
如果需要完整功能，请安装 langgraph 并使用 run_rag_writing.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.rag import load_index, create_embeddings
from langchain_openai import ChatOpenAI
import json
import re


def retrieve_documents(vectorstore, query, k=3):
    """检索相关文档"""
    print(f"\n{'='*70}")
    print(f"[1/4] 检索相关文档")
    print(f"{'='*70}")
    print(f"查询主题: {query}")
    print(f"检索数量: {k}")
    
    docs = vectorstore.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=k*2
    )
    
    print(f"✓ 成功检索到 {len(docs)} 个相关文档片段")
    
    # 显示文档预览
    for i, doc in enumerate(docs):
        print(f"\n文档 {i+1} 预览:")
        print(f"{doc.page_content[:150]}...")
    
    return docs


def generate_summary(llm, query, docs):
    """生成综述"""
    print(f"\n{'='*70}")
    print(f"[2/4] 生成综述")
    print(f"{'='*70}")
    
    # 构建上下文
    context = "\n\n".join([
        f"【文档 {i+1}】\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ])
    
    prompt = f"""
你是一位专业的学术综述写作专家。请基于以下检索到的文档内容，撰写一篇关于"{query}"的学术综述。

检索到的相关文档：
{context}

要求：
1. 综合分析所有文档的核心观点
2. 逻辑清晰，结构合理
3. 突出重点和创新点
4. 使用学术化的语言
5. 字数控制在 500-800 字

请直接输出综述内容，不要添加额外的说明。
"""
    
    print("正在生成综述...")
    response = llm.invoke(prompt)
    summary = response.content.strip()
    
    print(f"✓ 综述生成完成 (长度: {len(summary)} 字符)")
    
    return summary


def review_summary(llm, query, summary):
    """评审综述质量"""
    print(f"\n{'='*70}")
    print(f"[3/4] 评审综述质量")
    print(f"{'='*70}")
    
    prompt = f"""
你是一位严格的学术审稿人。请评审以下综述的质量，并按照 JSON 格式返回评审结果。

原始查询主题：{query}

综述内容：
{summary}

评审标准：
1. 内容完整性：是否全面覆盖主题 (30%)
2. 逻辑性：论述是否清晰连贯 (25%)
3. 学术性：语言是否专业规范 (20%)
4. 创新性：是否有独到见解 (15%)
5. 可读性：是否易于理解 (10%)

请严格按照以下 JSON 格式返回：
{{
    "score": 1-10,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": ["建议1", "建议2"],
    "overall": "总体评价"
}}

评分标准：
- 8-10分：优秀
- 6-7分：良好
- 4-5分：一般
- 1-3分：需要改进
"""
    
    print("正在评审...")
    response = llm.invoke(prompt)
    response_text = response.content.strip()
    
    # 解析 JSON 响应
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # 尝试提取 JSON 部分
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "score": 7,
                "strengths": ["内容完整"],
                "weaknesses": ["需要进一步优化"],
                "suggestions": ["建议增加更多细节"],
                "overall": "质量良好"
            }
    
    print(f"\n评审结果：")
    print(f"  评分: {result.get('score', 'N/A')}/10")
    print(f"  总体评价: {result.get('overall', 'N/A')}")
    
    if result.get('strengths'):
        print(f"\n  优点:")
        for s in result['strengths']:
            print(f"    - {s}")
    
    if result.get('weaknesses'):
        print(f"\n  不足:")
        for w in result['weaknesses']:
            print(f"    - {w}")
    
    if result.get('suggestions'):
        print(f"\n  改进建议:")
        for s in result['suggestions']:
            print(f"    - {s}")
    
    return result


def save_result(query, summary, review, output_file="output_rag_summary_simple.txt"):
    """保存结果"""
    print(f"\n{'='*70}")
    print(f"[4/4] 保存结果")
    print(f"{'='*70}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"查询主题：{query}\n")
        f.write(f"{'='*70}\n\n")
        
        f.write(f"综述内容：\n")
        f.write(f"{summary}\n\n")
        
        f.write(f"{'='*70}\n")
        f.write(f"评审结果：\n")
        f.write(f"  评分: {review.get('score', 'N/A')}/10\n")
        f.write(f"  总体评价: {review.get('overall', 'N/A')}\n\n")
        
        if review.get('strengths'):
            f.write(f"  优点:\n")
            for s in review['strengths']:
                f.write(f"    - {s}\n")
            f.write("\n")
        
        if review.get('weaknesses'):
            f.write(f"  不足:\n")
            for w in review['weaknesses']:
                f.write(f"    - {w}\n")
            f.write("\n")
        
        if review.get('suggestions'):
            f.write(f"  改进建议:\n")
            for s in review['suggestions']:
                f.write(f"    - {s}\n")
    
    print(f"✓ 结果已保存到: {output_file}")


def main():
    """主函数"""
    print("="*70)
    print("🚀 RAG 综述写作系统（简化版）")
    print("="*70)
    print()
    print("注意：这是简化版，不包含多轮迭代优化")
    print("如需完整功能，请安装 langgraph 并使用 run_rag_writing.py")
    print()
    
    # 用户输入查询主题
    query = input("请输入您想要撰写综述的主题：").strip()
    
    if not query:
        query = "深度学习在自然语言处理中的应用"
        print(f"使用默认主题：{query}")
    
    try:
        # 1. 加载向量索引
        print(f"\n{'='*70}")
        print(f"[0/4] 初始化")
        print(f"{'='*70}")
        print("正在加载向量索引...")
        
        embeddings = create_embeddings()
        vectorstore = load_index()
        
        print("正在初始化 LLM...")
        llm = ChatOpenAI(
            model=Config.DEEPSEEK_MODEL,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
        
        print("✓ 初始化完成")
        
        # 2. 检索文档
        docs = retrieve_documents(vectorstore, query, k=Config.RETRIEVAL_K)
        
        # 3. 生成综述
        summary = generate_summary(llm, query, docs)
        
        # 4. 评审质量
        review = review_summary(llm, query, summary)
        
        # 5. 保存结果
        save_result(query, summary, review)
        
        # 显示最终结果
        print(f"\n{'='*70}")
        print(f"✅ 完成！")
        print(f"{'='*70}")
        print()
        print(f"📝 最终综述：")
        print(f"{'='*70}")
        print(summary)
        print()
        
        print(f"💡 提示：")
        print(f"  - 结果已保存到 output_rag_summary_simple.txt")
        print(f"  - 如需多轮优化，请安装 langgraph: pip install langgraph")
        print(f"  - 然后运行: python scripts/run_rag_writing.py")
        
    except Exception as e:
        print(f"\n❌ 执行出错：{e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 可能的原因：")
        print(f"  1. 向量索引未构建：运行 python scripts/build_index.py")
        print(f"  2. API Key 配置错误：检查 src/config.py")
        print(f"  3. 网络连接问题：检查网络连接")


if __name__ == "__main__":
    main()
