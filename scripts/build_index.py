"""
构建 FAISS 向量索引脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag import load_pdf, split_documents, build_faiss_index, save_index
from src.config import Config


def main(pdf_path: str = None):
    """
    构建 FAISS 索引
    
    Args:
        pdf_path: PDF 文件路径（默认使用 CLIP.pdf）
    """
    # 默认 PDF 路径
    if pdf_path is None:
        pdf_path = os.path.join(Config.PDF_DIR, "CLIP.pdf")
    
    print(f"正在加载 PDF: {pdf_path}")
    
    # 步骤1：加载 PDF 文档
    docs = load_pdf(pdf_path)
    print(f"✓ 加载完成，共 {len(docs)} 页")
    
    # 步骤2：将文档切分成小块
    chunks = split_documents(docs)
    print(f"✓ 切分完成，共 {len(chunks)} 个文档块")
    
    # 步骤3：构建 FAISS 向量索引
    print("正在构建向量索引...")
    vectorstore = build_faiss_index(chunks)
    print("✓ 索引构建完成")
    
    # 步骤4：保存索引到本地
    save_index(vectorstore)
    print(f"✓ 索引已保存到: {Config.INDEX_DIR}")
    
    print("\n索引构建成功！")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="构建 FAISS 向量索引")
    parser.add_argument(
        "--pdf",
        type=str,
        help="PDF 文件路径",
        default=None
    )
    
    args = parser.parse_args()
    main(args.pdf)
