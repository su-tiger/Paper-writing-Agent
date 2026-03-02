"""
预定义的协作模式
"""

# 模式 1：研究 + 写作
RESEARCH_WRITE = [
    ("rag", {"k": 5}),      # RAG 检索 5 个文档
    ("workflow", {})         # Workflow 生成综述
]

# 模式 2：检索 + 分析 + 总结
RETRIEVE_ANALYZE_SUMMARIZE = [
    ("rag", {}),            # RAG 检索
    ("simple", {}),         # Simple 分析
    ("workflow", {})        # Workflow 总结
]

# 模式 3：多轮检索
MULTI_RETRIEVE = [
    ("rag", {"query": "深度学习"}),
    ("rag", {"query": "神经网络"}),
    ("simple", {})          # 综合分析
]

# 模式 4：审核循环
WRITE_REVIEW_LOOP = [
    ("workflow", {}),       # 生成初稿
    ("simple", {}),         # 审核
    ("workflow", {}),       # 根据反馈修改
]
