# 🚀 LangChain RAG & Agent 实战项目

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://github.com/langchain-ai/langchain)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 一个功能完整的 LangChain + LangGraph 实战项目，包含 RAG（检索增强生成）问答系统、多 Agent 协作工作流、以及完整的评估体系。

[English](README_EN.md) | 简体中文

## ✨ 核心特性

- 📚 **RAG 知识库问答**：基于 PDF 文档的智能问答系统
- 🤖 **多 Agent 协作**：Planner → Writer → Reviewer 工作流
- 📝 **RAG + Agent 综述写作**：自动检索论文并生成学术综述
- 📊 **完整评估体系**：支持 RAG、Agent、Workflow 全方位评估
- 🔄 **流式输出**：支持实时流式响应和事件监听
- 🛠️ **并行工具调用**：高效的多工具并行执行
- 🎯 **模块化设计**：清晰的架构，易于扩展和维护

## 📸 效果展示

```bash
# RAG 问答示例
$ python scripts/run_qa.py --query "What is CLIP?"

🤖 正在思考...
📚 检索到 3 个相关文档
✨ 生成回答...

CLIP (Contrastive Language-Image Pre-training) is a neural network 
trained on a variety of (image, text) pairs...
```

## 🚀 快速开始

### 一键安装（推荐）

**Windows:**
```bash
install.bat
```

**Mac/Linux:**
```bash
chmod +x install.sh
./install.sh
```

### 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/su-tiger/langchain-rag-agent.git
cd langchain-rag-agent

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY
```

### 运行示例

```bash
# 1. 构建向量索引
python scripts/build_index.py --pdf data/pdf/your_paper.pdf

# 2. 运行问答系统
python scripts/run_qa.py --interactive

# 3. 运行 RAG 写作
python scripts/run_rag_writing_simple.py
```

📖 **详细教程**：[快速开始指南](QUICKSTART_CN.md)

## 项目结构

```
LangChain-tutorial/
├── src/                      # 源代码
│   ├── agents/              # Agent 模块
│   ├── rag/                 # RAG 模块
│   ├── tools/               # 工具模块
│   ├── workflows/           # 工作流模块
│   └── config.py            # 配置管理
│
├── scripts/                 # 可执行脚本
│   ├── build_index.py      # 构建向量索引
│   ├── run_qa.py           # 运行问答系统
│   └── run_writing.py      # 运行写作工作流
│
├── data/                    # 数据目录
│   ├── pdf/                # PDF 文档
│   └── faiss_index/        # 向量索引
│
├── requirements.txt         # 依赖列表
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 功能特性

### 1. RAG 知识库问答系统
- 从 PDF 文档中提取知识
- 使用 FAISS 向量数据库存储文档嵌入
- 通过 Agent 架构实现智能检索和回答
- 支持 MMR（最大边际相关性）和相似度检索

### 2. LangGraph 多 Agent 写作工作流
- Planner（规划）→ Writer（写作）→ Reviewer（审核）循环流程
- 支持多个 Writer 并行工作（学术风格 vs 批判性分析）
- 具备断点恢复和人工介入能力
- 可根据审核反馈自动修改大纲或正文

### 3. ⭐ RAG + Agent 综述写作系统（新增）
- **自动检索论文 + 生成学术综述**
- 完整流程：query → RAG检索 → summary总结 → reviewer审核 → refine优化
- 基于真实文档，避免 LLM 幻觉
- 自动迭代优化，直到质量满意
- 适合学术综述、技术报告、文献综述

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 准备数据

将 PDF 文档放入 `data/pdf/` 目录。

### 4. 构建向量索引

```bash
python scripts/build_index.py --pdf data/pdf/CLIP.pdf
```

### 5. 运行问答系统

单次查询：
```bash
python scripts/run_qa.py --query "What is CLIP?"
```

交互模式：
```bash
python scripts/run_qa.py --interactive
```

### 6. 运行写作工作流

基本模式：
```bash
python scripts/run_writing.py --topic "人工智能的利弊"
```

交互模式（支持人工介入）：
```bash
python scripts/run_writing.py --topic "人工智能的利弊" --interactive
```

### 7. ⭐ 运行 RAG 综述写作（新增）

**方案 1：简化版（推荐，立即可用）**

```bash
python scripts/run_rag_writing_simple.py
```

不需要安装 langgraph，立即可用！

**方案 2：完整版（需要安装 langgraph）**

```bash
# 安装 langgraph
pip install langgraph

# 运行完整版
python scripts/run_rag_writing.py
```

输入主题，例如：
- "深度学习在自然语言处理中的应用"
- "Transformer 模型的发展历程"
- "强化学习的最新进展"

系统会自动：
1. 从论文库检索相关内容
2. 生成学术综述
3. 审核质量并评分
4. （完整版）根据反馈优化
5. 输出最终结果

**详细教程**：
- 📚 [完整教程](docs/rag_agent_tutorial.md)
- 🚀 [快速入门](docs/rag_quickstart.md)
- 📊 [流程图](docs/workflow_diagram.md)
- 🏗️ [架构文档](docs/architecture_rag.md)
- 📖 [中文使用指南](使用指南.md)
- 🎉 [最终总结](最终总结.md)

### 8. ⭐ 评估系统（新增）

**完整的评估体系，支持 RAG、Agent、Workflow 全方位评估**

单次评估：
```bash
# 评估 RAG 系统
python scripts/run_evaluation.py --type rag

# 评估 Agent 系统
python scripts/run_evaluation.py --type agent

# 评估 Workflow 系统
python scripts/run_evaluation.py --type workflow

# 评估所有系统
python scripts/run_evaluation.py --type all
```

批量评估：
```bash
# 创建示例测试集
python scripts/batch_evaluation.py --create-sample

# 批量评估 RAG
python scripts/batch_evaluation.py --type rag --test-set data/test_sets/rag_test_set.json

# 批量评估 Agent
python scripts/batch_evaluation.py --type agent --test-set data/test_sets/agent_test_set.json
```

**评估维度**：
- **RAG**: 检索质量（精确率、召回率、F1、MRR、NDCG）+ 生成质量（流畅度、连贯性、相关性、准确性、完整性）
- **Agent**: 工具选择准确性 + 推理过程合理性 + 答案质量
- **Workflow**: 执行效率 + 节点质量 + 流程设计 + 最终输出质量

**详细文档**：
- 📊 [评估系统指南](docs/evaluation_guide.md)

## 技术栈

- **LangChain**: 文档处理、向量存储、检索
- **LangGraph**: 工作流编排
- **FAISS**: 向量数据库
- **HuggingFace Embeddings**: 文本嵌入模型（BGE）
- **DeepSeek API**: 大语言模型
- **Evaluation System**: 完整的评估体系

## 项目亮点

1. **模块化设计**: 清晰的模块划分，易于扩展和维护
2. **配置管理**: 统一的配置管理，支持环境变量
3. **工具抽象**: 基于抽象基类的工具系统，易于添加新工具
4. **工作流编排**: 使用 LangGraph 实现复杂的多 Agent 协作
5. **断点恢复**: 支持工作流的断点恢复和状态管理
6. **人工介入**: 支持在关键节点进行人工审核和修改

## 开发指南

### 添加新的工具

1. 在 `src/tools/` 创建新文件
2. 继承 `BaseTool` 类
3. 实现 `run` 方法
4. 在 `src/tools/__init__.py` 中导出

### 添加新的 Agent

1. 在 `src/agents/` 创建新文件
2. 继承 `BaseAgent` 类
3. 实现 `run` 方法
4. 在 `src/agents/__init__.py` 中导出

### 修改配置

编辑 `src/config.py` 或使用环境变量。

## 📂 项目结构说明

```
src/
├── agents/              # Agent 实现（BaseAgent, SimpleAgent, RAGAgent）
├── rag/                 # RAG 模块（文档加载、切分、嵌入、检索）
├── tools/               # 工具系统（BaseTool, ToolExecutor, ToolRegistry）
├── workflows/           # LangGraph 工作流（写作流程、RAG 写作流程）
├── core/                # 核心模块（路由、统一 Agent、协作模式、流式事件）
└── evaluation/          # 评估系统（指标计算、评估器）
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 待办事项

- [ ] 添加更多嵌入模型支持（OpenAI、本地模型等）
- [ ] 支持更多向量数据库（Chroma、Pinecone 等）
- [ ] 添加 Web UI 界面
- [ ] 支持多语言文档处理
- [ ] 添加更多评估指标
- [ ] 性能优化和缓存机制

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 灵活的工作流编排工具
- [FAISS](https://github.com/facebookresearch/faiss) - 高效的向量检索库
- [DeepSeek](https://www.deepseek.com/) - 优秀的大语言模型

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/su-tiger/AgentFlow/issues)
- 发送邮件至：1477075086@qq.com

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐️
